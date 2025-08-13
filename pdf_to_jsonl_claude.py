import json
import re
from typing import List, Dict, Any
import PyPDF2
from anthropic import Anthropic
import argparse
from pathlib import Path
import sys

class PDFToJSONLConverter:
    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the converter with Anthropic API credentials.
        
        Args:
            api_key: Anthropic API key (if None, will look for ANTHROPIC_API_KEY env var)
            model: The Claude model to use for extraction
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
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
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise
            
        return text
    
    def extract_qa_pairs_with_llm(self, text: str, chunk_size: int = 4000) -> List[Dict[str, str]]:
        """
        Use Claude to identify and extract question-answer pairs from text.
        
        Args:
            text: The text to process
            chunk_size: Size of text chunks to process at once
            
        Returns:
            List of dictionaries with 'instruction' and 'output' keys
        """
        qa_pairs = []
        
        # Split text into manageable chunks
        chunks = self._split_text_into_chunks(text, chunk_size)
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            
            prompt = """
            Analyze the following text and extract all question-answer pairs, instructions with their responses, 
            or any content that can be formatted as an instruction-output pair.
            
            For each pair found, format it as a JSON object with:
            - "instruction": The question, command, or instruction
            - "output": The answer, response, or result
            
            Return ONLY a valid JSON array of these objects. Do not include any explanation or markdown formatting.
            If no clear pairs are found, return an empty array [].
            
            Text to analyze:
            ---
            {text}
            ---
            
            Return only the JSON array:
            """.format(text=chunk)
            
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                result = response.content[0].text
                
                # Clean the response to ensure it's valid JSON
                result = result.strip()
                # Remove any markdown code blocks if present
                result = re.sub(r'^```json\s*', '', result)
                result = re.sub(r'^```\s*', '', result)
                result = re.sub(r'\s*```$', '', result)
                
                # Parse the JSON response
                try:
                    pairs = json.loads(result)
                    
                    # Ensure we have a list
                    if isinstance(pairs, list):
                        qa_pairs.extend(pairs)
                    else:
                        print(f"Warning: Unexpected response format in chunk {i+1}")
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from chunk {i+1}: {e}")
                    print(f"Response was: {result[:200]}...")
                    continue
                    
            except Exception as e:
                print(f"Error processing chunk {i+1} with Claude: {e}")
                continue
        
        return qa_pairs
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of approximately chunk_size characters.
        Tries to split at sentence boundaries when possible.
        
        Args:
            text: Text to split
            chunk_size: Approximate size of each chunk
            
        Returns:
            List of text chunks
        """
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def convert_to_jsonl(self, pdf_path: str, output_path: str = None) -> str:
        """
        Convert a PDF file to JSONL format with instruction-output pairs.
        
        Args:
            pdf_path: Path to the input PDF file
            output_path: Path for the output JSONL file (optional)
            
        Returns:
            Path to the created JSONL file
        """
        # Extract text from PDF
        print(f"Extracting text from {pdf_path}...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            print("Warning: No text extracted from PDF")
            return None
        
        print(f"Extracted {len(text)} characters of text")
        
        # Extract Q&A pairs using Claude
        print("Extracting instruction-output pairs using Claude...")
        qa_pairs = self.extract_qa_pairs_with_llm(text)
        
        print(f"Found {len(qa_pairs)} instruction-output pairs")
        
        # Determine output path
        if output_path is None:
            pdf_path_obj = Path(pdf_path)
            output_path = pdf_path_obj.with_suffix('.jsonl')
        
        # Write to JSONL file
        print(f"Writing to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for pair in qa_pairs:
                # Ensure each pair has the required fields
                if 'instruction' in pair and 'output' in pair:
                    json_line = json.dumps(pair, ensure_ascii=False)
                    f.write(json_line + '\n')
        
        print(f"Successfully created {output_path}")
        return output_path

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to JSONL format with instruction-output pairs using Claude')
    parser.add_argument('pdf_file', help='Path to the PDF file to convert')
    parser.add_argument('-o', '--output', help='Output JSONL file path (default: same name as PDF)')
    parser.add_argument('--api-key', help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
    parser.add_argument('--model', default='claude-3-5-sonnet-20241022', 
                       help='Claude model to use (default: claude-3-5-sonnet-20241022)')
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not Path(args.pdf_file).exists():
        print(f"Error: PDF file '{args.pdf_file}' not found")
        sys.exit(1)
    
    # Create converter
    try:
        converter = PDFToJSONLConverter(api_key=args.api_key, model=args.model)
    except Exception as e:
        print(f"Error initializing converter: {e}")
        print("Make sure you have set the ANTHROPIC_API_KEY environment variable or passed it with --api-key")
        sys.exit(1)
    
    # Convert PDF to JSONL
    try:
        output_file = converter.convert_to_jsonl(args.pdf_file, args.output)
        if output_file:
            print(f"\nConversion complete! Output saved to: {output_file}")
            
            # Show sample of the output
            print("\nSample of extracted data:")
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:3]):  # Show first 3 entries
                    data = json.loads(line)
                    print(f"\nEntry {i+1}:")
                    print(f"  Instruction: {data['instruction'][:100]}...")
                    print(f"  Output: {data['output'][:100]}...")
                    
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()