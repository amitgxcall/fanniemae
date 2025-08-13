#!/usr/bin/env python3
import json
import re
from typing import List, Dict
import PyPDF2
import argparse
from pathlib import Path
import sys

class PDFToJSONLConverter:
    def __init__(self):
        pass
    
    def extract_text_from_pdf_range(self, pdf_path: str, start_page: int = 1, end_page: int = None) -> str:
        """Extract text from specific page range."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Adjust page numbers (1-indexed to 0-indexed)
                start_idx = max(0, start_page - 1)
                end_idx = min(total_pages, end_page) if end_page else total_pages
                
                print(f"PDF has {total_pages} pages")
                print(f"Processing pages {start_idx + 1} to {end_idx}")
                
                for page_num in range(start_idx, end_idx):
                    if (page_num - start_idx) % 10 == 0:
                        print(f"  Processing page {page_num + 1}/{end_idx}...")
                    
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise
            
        return text
    
    def extract_qa_pairs_smart(self, text: str) -> List[Dict[str, str]]:
        """Smart extraction of Q&A pairs from various formats."""
        qa_pairs = []
        
        # Split into sections
        sections = re.split(r'--- Page \d+ ---', text)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Skip table of contents pages (lots of page numbers and dots)
            if section.count('...') > 5 or re.findall(r'\d{3,4}\s*\.{2,}', section):
                continue
            
            # Extract various patterns
            
            # Pattern 1: Headers followed by paragraphs
            paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs):
                # Look for headers (short lines that might be titles)
                if len(para) < 150 and i < len(paragraphs) - 1:
                    next_para = paragraphs[i + 1]
                    if len(next_para) > 100:
                        # Check if it looks like a header
                        if (re.match(r'^[A-Z]', para) and 
                            not para.startswith('Published') and
                            not re.search(r'\d{2}/\d{2}/\d{4}', para)):
                            
                            instruction = para.rstrip('.:')
                            output = ' '.join(next_para.split()[:150])  # First 150 words
                            
                            if len(instruction) > 10 and len(output) > 50:
                                qa_pairs.append({
                                    "instruction": f"What is {instruction}?" if not instruction.endswith('?') else instruction,
                                    "output": output
                                })
            
            # Pattern 2: Bullet points and lists
            list_pattern = r'(?:^|\n)([A-Za-z][^:]+:)\s*\n((?:[•\-\*]\s*.+\n?)+)'
            matches = re.findall(list_pattern, section, re.MULTILINE)
            for header, items in matches:
                if len(header) < 100 and len(items) > 30:
                    qa_pairs.append({
                        "instruction": f"List the {header.rstrip(':')}",
                        "output": items.strip()
                    })
            
            # Pattern 3: Requirements or criteria sections
            req_pattern = r'((?:Requirements?|Criteria|Standards?|Guidelines?)[^:]*:)\s*([^.]+(?:\.[^.]+){1,3}\.)'
            matches = re.findall(req_pattern, section, re.IGNORECASE)
            for header, content in matches:
                if len(header) < 100 and len(content) > 50:
                    qa_pairs.append({
                        "instruction": f"What are the {header.rstrip(':')}?",
                        "output": content.strip()
                    })
            
            # Pattern 4: Process descriptions
            process_pattern = r'(The \w+ (?:process|procedure|method)[^.]*\.)\s*([^.]+(?:\.[^.]+){1,4}\.)'
            matches = re.findall(process_pattern, section, re.IGNORECASE)
            for intro, description in matches:
                if len(description) > 50:
                    qa_pairs.append({
                        "instruction": "Describe " + intro.lower(),
                        "output": description.strip()
                    })
        
        # Remove duplicates
        seen = set()
        unique_pairs = []
        for pair in qa_pairs:
            sig = (pair['instruction'][:50], pair['output'][:50])
            if sig not in seen:
                seen.add(sig)
                unique_pairs.append(pair)
        
        return unique_pairs
    
    def convert_to_jsonl(self, pdf_path: str, output_path: str = None, 
                         start_page: int = 1, end_page: int = None) -> str:
        """Convert PDF to JSONL format."""
        
        # Extract text
        print(f"\nExtracting text from {pdf_path}...")
        text = self.extract_text_from_pdf_range(pdf_path, start_page, end_page)
        
        if not text.strip():
            print("Warning: No text extracted")
            return None
        
        print(f"Extracted {len(text)} characters")
        
        # Extract Q&A pairs
        print("\nExtracting instruction-output pairs...")
        qa_pairs = self.extract_qa_pairs_smart(text)
        
        print(f"Found {len(qa_pairs)} instruction-output pairs")
        
        if not qa_pairs:
            print("No pairs found - PDF might not have suitable content")
            return None
        
        # Output path
        if output_path is None:
            pdf_path_obj = Path(pdf_path)
            output_path = pdf_path_obj.with_suffix('.jsonl')
        
        # Write JSONL
        print(f"\nWriting to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for pair in qa_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        
        print(f"✓ Created {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(
        description='Fast PDF to JSONL converter for instruction-output pairs'
    )
    parser.add_argument('pdf_file', help='PDF file path')
    parser.add_argument('-o', '--output', help='Output JSONL path')
    parser.add_argument('--start', type=int, default=1, help='Start page (default: 1)')
    parser.add_argument('--end', type=int, help='End page (default: all)')
    
    args = parser.parse_args()
    
    if not Path(args.pdf_file).exists():
        print(f"Error: {args.pdf_file} not found")
        sys.exit(1)
    
    converter = PDFToJSONLConverter()
    
    try:
        output = converter.convert_to_jsonl(
            args.pdf_file, args.output, args.start, args.end
        )
        
        if output:
            # Show sample
            with open(output, 'r') as f:
                lines = f.readlines()
                print(f"\nTotal pairs: {len(lines)}")
                print("\nFirst 3 examples:")
                for i, line in enumerate(lines[:3]):
                    data = json.loads(line)
                    print(f"\n[{i+1}]")
                    print(f"Q: {data['instruction'][:100]}...")
                    print(f"A: {data['output'][:150]}...")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()