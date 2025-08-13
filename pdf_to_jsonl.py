#!/usr/bin/env python3
import json
import re
from typing import List, Dict, Tuple
import PyPDF2
import argparse
from pathlib import Path
import sys

class PDFToJSONLConverter:
    def __init__(self):
        """
        Initialize the converter for extracting instruction-output pairs from PDFs.
        """
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                print(f"PDF has {num_pages} pages")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise
            
        return text
    
    def extract_text_from_pdf_limited(self, pdf_path: str, max_pages: int) -> str:
        """
        Extract text content from limited pages of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            max_pages: Maximum number of pages to extract
            
        Returns:
            Extracted text as a string
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                pages_to_read = min(max_pages, total_pages)
                
                print(f"PDF has {total_pages} pages, reading first {pages_to_read}")
                
                for page_num in range(pages_to_read):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise
            
        return text
    
    def extract_qa_pairs_heuristic(self, text: str) -> List[Dict[str, str]]:
        """
        Extract question-answer pairs using heuristic pattern matching.
        
        Args:
            text: The text to process
            
        Returns:
            List of dictionaries with 'instruction' and 'output' keys
        """
        qa_pairs = []
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'--- Page \d+ ---', '\n[PAGE_BREAK]\n', text)
        
        # Pattern 1: Q&A format (Q: ... A: ...)
        qa_pattern = r'(?:Q:|Question:)\s*([^?]+\??)\s*(?:A:|Answer:)\s*([^Q]+?)(?=(?:Q:|Question:)|$|\[PAGE_BREAK\])'
        matches = re.findall(qa_pattern, text, re.IGNORECASE | re.DOTALL)
        for q, a in matches:
            q = q.strip()
            a = a.strip()
            if len(q) > 10 and len(a) > 10:
                qa_pairs.append({
                    "instruction": q,
                    "output": a
                })
        
        # Pattern 2: Numbered questions (1. Question? Answer...)
        numbered_pattern = r'(\d+\.\s*[^?]+\?)\s*([^0-9]+?)(?=\d+\.|$|\[PAGE_BREAK\])'
        matches = re.findall(numbered_pattern, text, re.DOTALL)
        for q, a in matches:
            q = re.sub(r'^\d+\.\s*', '', q).strip()
            a = a.strip()
            if len(q) > 10 and len(a) > 10 and not a.startswith('?'):
                qa_pairs.append({
                    "instruction": q,
                    "output": a
                })
        
        # Pattern 3: How to / What is patterns
        howto_pattern = r'((?:How to|How do|How can|What is|What are|Why|When|Where)[^.?]+[.?])\s*([^.]+\.)'
        matches = re.findall(howto_pattern, text, re.IGNORECASE)
        for q, a in matches:
            q = q.strip()
            a = a.strip()
            if len(q) > 10 and len(a) > 20:
                qa_pairs.append({
                    "instruction": q,
                    "output": a
                })
        
        # Pattern 4: Section headers followed by content
        section_pattern = r'\n([A-Z][A-Za-z\s]+(?:Guidelines|Instructions|Steps|Process|Procedure|Overview|Introduction|Description))\n+([^A-Z\n]+(?:\n[^A-Z\n]+)*)'
        matches = re.findall(section_pattern, text)
        for header, content in matches:
            header = header.strip()
            content = ' '.join(content.split()[:100])  # Limit to first 100 words
            if len(header) > 5 and len(content) > 30:
                qa_pairs.append({
                    "instruction": f"Explain {header.lower()}",
                    "output": content.strip()
                })
        
        # Pattern 5: Definitions (Term: definition or Term - definition)
        definition_pattern = r'([A-Z][A-Za-z\s]+)(?::|–|-)\s*([A-Z][^.]+\.)'
        matches = re.findall(definition_pattern, text)
        for term, definition in matches:
            term = term.strip()
            definition = definition.strip()
            if len(term) < 50 and len(definition) > 20:
                qa_pairs.append({
                    "instruction": f"What is {term.lower()}?",
                    "output": definition
                })
        
        # Pattern 6: Step-by-step instructions
        step_pattern = r'Step\s+(\d+)[:\s]+([^S]+?)(?=Step\s+\d+|$|\[PAGE_BREAK\])'
        matches = re.findall(step_pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            steps = []
            for step_num, step_content in matches:
                step_content = step_content.strip()
                if len(step_content) > 10:
                    steps.append(f"Step {step_num}: {step_content}")
            
            if steps:
                qa_pairs.append({
                    "instruction": "What are the steps in this process?",
                    "output": "\n".join(steps)
                })
        
        # Pattern 7: FAQ style (question ending with ? followed by answer)
        faq_pattern = r'([^.?]+\?)\s*([^?]+?[.])\s*(?=[^.?]+\?|$|\[PAGE_BREAK\])'
        matches = re.findall(faq_pattern, text, re.DOTALL)
        for q, a in matches:
            q = q.strip()
            a = a.strip()
            # Avoid duplicate from other patterns and ensure quality
            if len(q) > 15 and len(a) > 20 and not any(qa['instruction'] == q for qa in qa_pairs):
                qa_pairs.append({
                    "instruction": q,
                    "output": a
                })
        
        # Remove duplicates
        seen = set()
        unique_pairs = []
        for pair in qa_pairs:
            pair_tuple = (pair['instruction'][:50], pair['output'][:50])
            if pair_tuple not in seen:
                seen.add(pair_tuple)
                unique_pairs.append(pair)
        
        return unique_pairs
    
    def extract_contextual_pairs(self, text: str) -> List[Dict[str, str]]:
        """
        Extract instruction-output pairs based on document structure and context.
        
        Args:
            text: The text to process
            
        Returns:
            List of dictionaries with 'instruction' and 'output' keys
        """
        qa_pairs = []
        
        # Split by pages
        pages = text.split('--- Page')
        
        for page in pages:
            if not page.strip():
                continue
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in page.split('\n\n') if p.strip() and len(p.strip()) > 50]
            
            # Create pairs from consecutive paragraphs that seem related
            for i in range(len(paragraphs) - 1):
                para1 = paragraphs[i]
                para2 = paragraphs[i + 1]
                
                # If first paragraph looks like a heading or question
                if (len(para1) < 200 and 
                    (para1.endswith('?') or 
                     para1.endswith(':') or
                     re.match(r'^[A-Z][A-Za-z\s]+$', para1) or
                     any(word in para1.lower() for word in ['how', 'what', 'why', 'when', 'where', 'guide', 'overview']))):
                    
                    qa_pairs.append({
                        "instruction": para1 if para1.endswith('?') else f"Explain about {para1.lower().rstrip(':')}",
                        "output": para2
                    })
            
            # Look for lists after headers
            list_pattern = r'([A-Za-z\s]+:)\s*\n([•\-\*\d]+[.\)]\s+.+(?:\n[•\-\*\d]+[.\)]\s+.+)*)'
            matches = re.findall(list_pattern, page, re.MULTILINE)
            for header, list_content in matches:
                if len(header) < 100 and len(list_content) > 30:
                    qa_pairs.append({
                        "instruction": f"List the items for {header.rstrip(':')}",
                        "output": list_content.strip()
                    })
        
        return qa_pairs
    
    def convert_to_jsonl(self, pdf_path: str, output_path: str = None, max_pages: int = None) -> str:
        """
        Convert a PDF file to JSONL format with instruction-output pairs.
        
        Args:
            pdf_path: Path to the input PDF file
            output_path: Path for the output JSONL file (optional)
            max_pages: Maximum number of pages to process (None for all)
            
        Returns:
            Path to the created JSONL file
        """
        # Extract text from PDF with page limit
        print(f"\nExtracting text from {pdf_path}...")
        
        if max_pages:
            print(f"Processing first {max_pages} pages only...")
            text = self.extract_text_from_pdf_limited(pdf_path, max_pages)
        else:
            text = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            print("Warning: No text extracted from PDF")
            return None
        
        print(f"Extracted {len(text)} characters of text")
        
        # Extract Q&A pairs using multiple methods
        print("\nExtracting instruction-output pairs...")
        
        # Method 1: Heuristic patterns
        print("  Applying pattern matching...")
        heuristic_pairs = self.extract_qa_pairs_heuristic(text)
        print(f"  Found {len(heuristic_pairs)} pairs from patterns")
        
        # Method 2: Contextual extraction
        print("  Analyzing document structure...")
        contextual_pairs = self.extract_contextual_pairs(text)
        print(f"  Found {len(contextual_pairs)} pairs from structure")
        
        # Combine all pairs
        all_pairs = heuristic_pairs + contextual_pairs
        
        # Remove duplicates while preserving order
        seen = set()
        qa_pairs = []
        for pair in all_pairs:
            # Clean whitespace
            pair['instruction'] = ' '.join(pair['instruction'].split())
            pair['output'] = ' '.join(pair['output'].split())
            
            # Create a signature for deduplication
            sig = (pair['instruction'][:100].lower(), pair['output'][:100].lower())
            if sig not in seen and len(pair['instruction']) > 10 and len(pair['output']) > 20:
                seen.add(sig)
                qa_pairs.append(pair)
        
        print(f"\n✓ Total unique pairs: {len(qa_pairs)}")
        
        if not qa_pairs:
            print("Warning: No instruction-output pairs could be extracted")
            print("The PDF might not contain Q&A formatted content.")
            return None
        
        # Sort by instruction length for better organization
        qa_pairs.sort(key=lambda x: len(x['instruction']))
        
        # Determine output path
        if output_path is None:
            pdf_path_obj = Path(pdf_path)
            output_path = pdf_path_obj.with_suffix('.jsonl')
        
        # Write to JSONL file
        print(f"\nWriting to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for pair in qa_pairs:
                json_line = json.dumps(pair, ensure_ascii=False)
                f.write(json_line + '\n')
        
        print(f"✓ Successfully created {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(
        description='Convert PDF to JSONL format with instruction-output pairs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script extracts instruction-output pairs from PDFs using pattern matching.
It looks for:
  - Q&A formatted content
  - How-to instructions
  - Definitions and explanations
  - Step-by-step procedures
  - Section headers with content
  - FAQ-style questions and answers

Examples:
  python pdf_to_jsonl.py document.pdf
  python pdf_to_jsonl.py document.pdf -o training_data.jsonl
        """
    )
    parser.add_argument('pdf_file', help='Path to the PDF file to convert')
    parser.add_argument('-o', '--output', help='Output JSONL file path (default: same name as PDF with .jsonl extension)')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to process (useful for large PDFs)')
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not Path(args.pdf_file).exists():
        print(f"Error: PDF file '{args.pdf_file}' not found")
        sys.exit(1)
    
    # Create converter
    converter = PDFToJSONLConverter()
    
    # Convert PDF to JSONL
    try:
        output_file = converter.convert_to_jsonl(args.pdf_file, args.output, args.max_pages)
        if output_file:
            print(f"\n{'='*60}")
            print(f"Conversion complete!")
            print(f"Output file: {output_file}")
            print(f"{'='*60}")
            
            # Show statistics and sample
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\nStatistics:")
                print(f"  Total pairs: {len(lines)}")
                
                if lines:
                    # Calculate average lengths
                    total_inst_len = 0
                    total_out_len = 0
                    min_inst = float('inf')
                    max_inst = 0
                    min_out = float('inf')
                    max_out = 0
                    
                    for line in lines:
                        data = json.loads(line)
                        inst_len = len(data['instruction'])
                        out_len = len(data['output'])
                        
                        total_inst_len += inst_len
                        total_out_len += out_len
                        
                        min_inst = min(min_inst, inst_len)
                        max_inst = max(max_inst, inst_len)
                        min_out = min(min_out, out_len)
                        max_out = max(max_out, out_len)
                    
                    print(f"  Instruction length: {min_inst}-{max_inst} chars (avg: {total_inst_len // len(lines)})")
                    print(f"  Output length: {min_out}-{max_out} chars (avg: {total_out_len // len(lines)})")
                    
                    # Show samples
                    print(f"\nSample entries (first 5):")
                    print("-" * 60)
                    for i, line in enumerate(lines[:5]):
                        data = json.loads(line)
                        print(f"\n[Entry {i+1}]")
                        inst = data['instruction']
                        out = data['output']
                        
                        # Show instruction
                        if len(inst) > 120:
                            print(f"Q: {inst[:120]}...")
                        else:
                            print(f"Q: {inst}")
                        
                        # Show output (first 150 chars)
                        if len(out) > 150:
                            print(f"A: {out[:150]}...")
                        else:
                            print(f"A: {out}")
                    
                    print(f"\n{'='*60}")
                    print(f"Use this JSONL file for fine-tuning language models.")
                    print(f"Each line contains: {{\"instruction\": \"...\", \"output\": \"...\"}}")
                    
    except Exception as e:
        print(f"\nError during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()