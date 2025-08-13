#!/usr/bin/env python3
import json
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict

class SellingGuideCrawler:
    def __init__(self):
        self.base_url = "https://selling-guide.fanniemae.com"
        self.visited_urls = set()
        self.instruction_output_pairs = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_content_from_page(self, url: str) -> List[Dict[str, str]]:
        """Extract instruction-output pairs from a single page."""
        try:
            print(f"Processing: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            pairs = []
            
            # Remove navigation, headers, footers
            for element in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
                element.decompose()
            
            # Extract page title as context
            title_elem = soup.find('h1') or soup.find('title')
            page_title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract main content areas
            content_areas = (
                soup.find_all('div', class_=['content', 'main-content', 'article-content']) or
                soup.find_all('section') or
                soup.find_all('article') or
                [soup.find('main')] if soup.find('main') else [soup]
            )
            
            for content_area in content_areas:
                if not content_area:
                    continue
                    
                # Extract structured content
                pairs.extend(self._extract_definitions(content_area, page_title))
                pairs.extend(self._extract_requirements(content_area, page_title))
                pairs.extend(self._extract_procedures(content_area, page_title))
                pairs.extend(self._extract_qa_format(content_area, page_title))
                pairs.extend(self._extract_lists(content_area, page_title))
                pairs.extend(self._extract_headings_content(content_area, page_title))
            
            return pairs
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return []
    
    def _extract_definitions(self, content, context: str) -> List[Dict[str, str]]:
        """Extract definition-style content."""
        pairs = []
        
        # Look for definition patterns
        def_patterns = [
            r'([A-Z][^:]{3,50}):\s*([^.]+\.)',
            r'([A-Z][^-]{3,50})\s*[-–]\s*([^.]+\.)',
            r'The term "([^"]+)" means ([^.]+\.)',
        ]
        
        text = content.get_text()
        
        for pattern in def_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for term, definition in matches:
                if len(term) < 100 and len(definition) > 20:
                    pairs.append({
                        "instruction": f"What is {term.strip()}?",
                        "output": f"Definition: {definition.strip()}"
                    })
        
        return pairs
    
    def _extract_requirements(self, content, context: str) -> List[Dict[str, str]]:
        """Extract requirement-style content."""
        pairs = []
        
        # Find requirement sections
        req_headings = content.find_all(['h1', 'h2', 'h3', 'h4'], 
            string=re.compile(r'requirements?|must|shall|eligibility', re.IGNORECASE))
        
        for heading in req_headings:
            heading_text = heading.get_text(strip=True)
            next_content = ""
            
            # Get following content until next heading
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                next_content += sibling.get_text(strip=True) + " "
            
            if len(next_content) > 50:
                pairs.append({
                    "instruction": f"What are the {heading_text.lower()}?",
                    "output": next_content[:500].strip()
                })
        
        return pairs
    
    def _extract_procedures(self, content, context: str) -> List[Dict[str, str]]:
        """Extract procedure-style content."""
        pairs = []
        
        # Find procedure sections
        proc_headings = content.find_all(['h1', 'h2', 'h3', 'h4'], 
            string=re.compile(r'procedure|process|steps?|how to', re.IGNORECASE))
        
        for heading in proc_headings:
            heading_text = heading.get_text(strip=True)
            
            # Look for ordered lists or step-by-step content
            next_ol = heading.find_next_sibling('ol') or heading.find_next('ol')
            if next_ol:
                steps = []
                for li in next_ol.find_all('li'):
                    steps.append(li.get_text(strip=True))
                
                if steps:
                    pairs.append({
                        "instruction": f"What is the procedure for {heading_text.lower()}?",
                        "output": " | ".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
                    })
        
        return pairs
    
    def _extract_qa_format(self, content, context: str) -> List[Dict[str, str]]:
        """Extract Q&A format content."""
        pairs = []
        
        text = content.get_text()
        
        # Look for Q&A patterns
        qa_patterns = [
            r'(?:Q:|Question:)\s*([^?]+\?)\s*(?:A:|Answer:)\s*([^Q]+?)(?=(?:Q:|Question:)|$)',
            r'([^.?]+\?)\s*([A-Z][^?]+\.)'
        ]
        
        for pattern in qa_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for question, answer in matches:
                question = question.strip()
                answer = answer.strip()
                
                if len(question) > 10 and len(answer) > 20 and len(question) < 200:
                    pairs.append({
                        "instruction": question,
                        "output": answer
                    })
        
        return pairs
    
    def _extract_lists(self, content, context: str) -> List[Dict[str, str]]:
        """Extract list-based content."""
        pairs = []
        
        # Find lists with preceding headings
        for ul in content.find_all(['ul', 'ol']):
            prev_heading = None
            prev_sibling = ul.find_previous_sibling(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
            
            if prev_sibling and prev_sibling.name.startswith('h'):
                prev_heading = prev_sibling.get_text(strip=True)
            elif prev_sibling and len(prev_sibling.get_text(strip=True)) < 100:
                prev_heading = prev_sibling.get_text(strip=True)
            
            if prev_heading:
                items = []
                for li in ul.find_all('li'):
                    item_text = li.get_text(strip=True)
                    if item_text:
                        items.append(item_text)
                
                if items and len(items) <= 10:  # Reasonable list size
                    pairs.append({
                        "instruction": f"What are the {prev_heading.lower()}?",
                        "output": " | ".join([f"• {item}" for item in items])
                    })
        
        return pairs
    
    def _extract_headings_content(self, content, context: str) -> List[Dict[str, str]]:
        """Extract heading followed by content."""
        pairs = []
        
        headings = content.find_all(['h1', 'h2', 'h3', 'h4'])
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            
            if len(heading_text) > 100 or len(heading_text) < 10:
                continue
            
            # Get content until next heading
            following_content = ""
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                    
                sibling_text = sibling.get_text(strip=True)
                if sibling_text:
                    following_content += sibling_text + " "
                
                if len(following_content) > 300:  # Limit length
                    break
            
            if 50 < len(following_content) < 500:
                pairs.append({
                    "instruction": f"Explain {heading_text.lower()}",
                    "output": following_content.strip()
                })
        
        return pairs
    
    def crawl_key_sections(self) -> List[Dict[str, str]]:
        """Crawl key sections of the Selling Guide."""
        
        # Key URLs to crawl (starting with main sections)
        key_urls = [
            f"{self.base_url}/copyright-and-preface",
            f"{self.base_url}/part-a/approval-and-qualification",
            f"{self.base_url}/part-a/lender-contract", 
            f"{self.base_url}/part-b/loan-application-package",
            f"{self.base_url}/part-b/eligibility",
            f"{self.base_url}/part-b/underwriting-borrowers",
            f"{self.base_url}/part-b/underwriting-property",
            f"{self.base_url}/part-b/insurance",
            f"{self.base_url}/part-c/execution-options",
            f"{self.base_url}/part-d/lender-qc-process",
            f"{self.base_url}/part-e/selling-guide-resources"
        ]
        
        all_pairs = []
        
        for url in key_urls:
            if url not in self.visited_urls:
                pairs = self.extract_content_from_page(url)
                all_pairs.extend(pairs)
                self.visited_urls.add(url)
                
                # Rate limiting
                time.sleep(1)
        
        return all_pairs
    
    def save_to_jsonl(self, pairs: List[Dict[str, str]], filename: str):
        """Save pairs to JSONL file."""
        
        # Remove duplicates
        seen = set()
        unique_pairs = []
        
        for pair in pairs:
            sig = (pair['instruction'][:100], pair['output'][:100])
            if sig not in seen:
                seen.add(sig)
                unique_pairs.append(pair)
        
        with open(filename, 'w', encoding='utf-8') as f:
            for pair in unique_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        
        return len(unique_pairs)

def main():
    print("Starting Fannie Mae Selling Guide crawl...")
    
    crawler = SellingGuideCrawler()
    
    # Crawl key sections
    all_pairs = crawler.crawl_key_sections()
    
    print(f"\nExtracted {len(all_pairs)} total pairs")
    
    # Save to JSONL
    output_file = "fannie_selling_guide.jsonl"
    unique_count = crawler.save_to_jsonl(all_pairs, output_file)
    
    print(f"✓ Saved {unique_count} unique pairs to {output_file}")
    
    # Show samples
    print("\nFirst 3 entries:")
    with open(output_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            data = json.loads(line)
            print(f"\n[{i+1}] {data['instruction']}")
            print(f"    {data['output'][:120]}...")

if __name__ == "__main__":
    main()