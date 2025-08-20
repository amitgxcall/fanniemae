#!/usr/bin/env python3
import json
import re
import hashlib
from typing import List, Dict, Set, Tuple
import os
from collections import defaultdict
import unicodedata

class FannieDatasetNormalizerFast:
    """Optimized dataset normalizer with faster processing."""
    
    def __init__(self):
        # Standardized context mapping
        self.context_standardization = {
            "Mortgage Terminology and Definitions": "terminology",
            "Property and Real Estate": "property",
            "Government Programs and Regulations": "government",
            "Fannie Mae Products and Programs": "fannie_products",
            "Loan Origination and Underwriting": "origination",
            "Multifamily and Commercial": "multifamily",
            "Data Dictionary and Attributes": "data_dictionary",
            "Financial Terms and Calculations": "financial",
            "Secondary Market and Securities": "securities",
            "Technology and Digital Services": "technology",
            "General Mortgage Knowledge": "general"
        }
        
        # Common abbreviations for expansion
        self.abbreviations = {
            "mtg": "mortgage",
            "prop": "property", 
            "pmt": "payment",
            "int": "interest",
            "prin": "principal",
            "refi": "refinance",
            "ltv": "loan-to-value",
            "dti": "debt-to-income",
            "arm": "adjustable rate mortgage",
            "apr": "annual percentage rate",
            "pmi": "private mortgage insurance",
            "hoa": "homeowners association",
            "reo": "real estate owned",
            "mbs": "mortgage-backed securities",
            "gse": "government-sponsored enterprise"
        }
    
    def normalize_text(self, text: str) -> str:
        """Apply text normalization."""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove control characters
        text = ''.join(char for char in text if not unicodedata.category(char).startswith('C'))
        
        # Standardize whitespace
        text = ' '.join(text.split())
        
        # Fix common encoding issues
        text = text.replace('â€™', "'").replace('â€"', '-').replace('â€œ', '"').replace('â€', '"')
        
        # Standardize punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Standardize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Remove trailing/leading whitespace
        text = text.strip()
        
        # Ensure sentence ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand known abbreviations."""
        for abbr, expansion in self.abbreviations.items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        return text
    
    def fast_deduplicate(self, entries: List[Dict]) -> List[Dict]:
        """Fast deduplication using hashes."""
        print(f"🔍 Performing fast deduplication...")
        
        seen_hashes = set()
        deduplicated = []
        duplicates_removed = 0
        
        for entry in entries:
            # Create normalized signature
            inst_norm = self.normalize_text(entry['instruction']).lower()[:100]
            resp_norm = self.normalize_text(entry['response']).lower()[:100]
            
            # Create hash
            signature = hashlib.md5(f"{inst_norm}|{resp_norm}".encode()).hexdigest()
            
            if signature not in seen_hashes:
                seen_hashes.add(signature)
                deduplicated.append(entry)
            else:
                duplicates_removed += 1
        
        print(f"  ✅ Removed {duplicates_removed} duplicates")
        return deduplicated
    
    def estimate_token_count(self, text: str) -> int:
        """Fast token count estimation."""
        # Simple estimation: words + punctuation
        words = len(text.split())
        punctuation = text.count('.') + text.count(',') + text.count('!') + text.count('?')
        return words + (words // 3) + punctuation
    
    def calculate_complexity_score(self, text: str) -> str:
        """Fast complexity calculation."""
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        if avg_word_length < 5 and len(words) < 20:
            return "simple"
        elif avg_word_length > 7 or len(words) > 50:
            return "complex"
        else:
            return "moderate"
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Fast key term extraction."""
        key_terms = []
        
        # Extract capitalized terms
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        key_terms.extend(capitalized[:3])
        
        # Extract acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        key_terms.extend(acronyms[:2])
        
        return list(set(key_terms))[:5]
    
    def classify_question_type(self, instruction: str) -> str:
        """Fast question type classification."""
        inst_lower = instruction.lower()
        
        if inst_lower.startswith(('what is', 'what are', 'define')):
            return 'definition'
        elif inst_lower.startswith(('how', 'why', 'when', 'who')):
            return 'explanatory'
        elif 'compare' in inst_lower or 'difference' in inst_lower:
            return 'comparison'
        else:
            return 'general'
    
    def calculate_quality_score(self, entry: Dict) -> float:
        """Fast quality score calculation."""
        score = 0.5  # Base score
        
        inst_len = len(entry['instruction'])
        resp_len = len(entry['response'])
        
        # Length bonuses
        if 10 <= inst_len <= 200:
            score += 0.2
        if 50 <= resp_len <= 1000:
            score += 0.3
        
        return min(score, 1.0)
    
    def enrich_metadata_fast(self, entry: Dict) -> Dict:
        """Fast metadata enrichment."""
        enriched = entry.copy()
        
        enriched['metadata'] = {
            'instruction_tokens': self.estimate_token_count(entry['instruction']),
            'response_tokens': self.estimate_token_count(entry['response']),
            'instruction_complexity': self.calculate_complexity_score(entry['instruction']),
            'response_complexity': self.calculate_complexity_score(entry['response']),
            'key_terms': self.extract_key_terms(entry['instruction']),
            'question_type': self.classify_question_type(entry['instruction']),
            'quality_score': self.calculate_quality_score(entry)
        }
        
        return enriched
    
    def standardize_context_labels(self, context: str) -> str:
        """Standardize context labels."""
        return self.context_standardization.get(context, 'general')
    
    def process_dataset(self, input_file: str, output_file: str, batch_size: int = 1000) -> Dict:
        """Process dataset in batches for better performance."""
        print("🚀 STARTING FAST DATASET NORMALIZATION")
        print("=" * 60)
        
        stats = {
            'total_entries': 0,
            'processed_entries': 0,
            'duplicates_removed': 0,
            'quality_filtered': 0,
            'context_distribution': defaultdict(int),
            'question_types': defaultdict(int)
        }
        
        # Process in batches for memory efficiency
        all_entries = []
        batch = []
        
        print("📖 Reading and normalizing dataset...")
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 5000 == 0:
                    print(f"  Processing line {line_num}...")
                
                try:
                    entry = json.loads(line.strip())
                    stats['total_entries'] += 1
                    
                    # Normalize text
                    entry['instruction'] = self.normalize_text(entry['instruction'])
                    entry['response'] = self.normalize_text(entry['response'])
                    entry['instruction'] = self.expand_abbreviations(entry['instruction'])
                    entry['response'] = self.expand_abbreviations(entry['response'])
                    
                    batch.append(entry)
                    
                    # Process batch
                    if len(batch) >= batch_size:
                        all_entries.extend(batch)
                        batch = []
                        
                except json.JSONDecodeError:
                    continue
        
        # Add remaining batch
        if batch:
            all_entries.extend(batch)
        
        print(f"  Loaded {len(all_entries)} entries")
        
        # Fast deduplication
        all_entries = self.fast_deduplicate(all_entries)
        stats['duplicates_removed'] = stats['total_entries'] - len(all_entries)
        
        # Process entries
        print("\n🏷️ Enriching metadata and standardizing...")
        processed_entries = []
        
        for i, entry in enumerate(all_entries):
            if i % 5000 == 0:
                print(f"  Processing {i}/{len(all_entries)}...")
            
            # Standardize context
            if 'context' in entry:
                entry['context'] = self.standardize_context_labels(entry['context'])
                stats['context_distribution'][entry['context']] += 1
            else:
                entry['context'] = 'general'
                stats['context_distribution']['general'] += 1
            
            # Fast metadata enrichment
            enriched = self.enrich_metadata_fast(entry)
            
            # Track statistics
            stats['question_types'][enriched['metadata']['question_type']] += 1
            
            # Quality filtering
            if enriched['metadata']['quality_score'] >= 0.3:
                processed_entries.append(enriched)
            else:
                stats['quality_filtered'] += 1
        
        stats['processed_entries'] = len(processed_entries)
        
        # Sort by quality
        print("\n📊 Sorting by quality...")
        processed_entries.sort(key=lambda x: x['metadata']['quality_score'], reverse=True)
        
        # Save normalized dataset
        print(f"\n💾 Saving normalized dataset...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in processed_entries:
                clean_entry = {
                    'instruction': entry['instruction'],
                    'context': entry.get('context', 'general'),
                    'response': entry['response']
                }
                f.write(json.dumps(clean_entry, ensure_ascii=False) + '\n')
        
        # Save metadata version
        metadata_file = output_file.replace('.jsonl', '_with_metadata.jsonl')
        print(f"💾 Saving metadata version...")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            for entry in processed_entries[:1000]:  # Save first 1000 with metadata as sample
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        return stats

def print_report(stats: Dict):
    """Print normalization report."""
    print("\n" + "=" * 60)
    print("📊 NORMALIZATION REPORT")
    print("=" * 60)
    
    print(f"\n📈 Processing Statistics:")
    print(f"  • Original entries: {stats['total_entries']:,}")
    print(f"  • Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"  • Quality filtered: {stats['quality_filtered']:,}")
    print(f"  • Final entries: {stats['processed_entries']:,}")
    
    print(f"\n🏷️ Context Distribution:")
    total = stats['processed_entries']
    for context, count in sorted(stats['context_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"  • {context}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n❓ Question Types:")
    for qtype, count in sorted(stats['question_types'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"  • {qtype}: {count:,} ({percentage:.1f}%)")

def main():
    input_file = "fannie_mae_ultimate_with_context.jsonl"
    output_file = "fannie_mae_normalized_final.jsonl"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    normalizer = FannieDatasetNormalizerFast()
    stats = normalizer.process_dataset(input_file, output_file)
    
    print_report(stats)
    
    print("\n" + "=" * 60)
    print("✅ NORMALIZATION COMPLETE!")
    print(f"📄 Output: {output_file}")
    print(f"📄 Metadata sample: {output_file.replace('.jsonl', '_with_metadata.jsonl')}")
    print(f"📊 Final entries: {stats['processed_entries']:,}")
    print("🎯 Dataset normalized and ready for training!")

if __name__ == "__main__":
    main()