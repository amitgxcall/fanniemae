#!/usr/bin/env python3
import json
import re
import hashlib
from typing import List, Dict, Set, Tuple
import os
from collections import defaultdict
import unicodedata
from difflib import SequenceMatcher

class FannieDatasetNormalizer:
    """Comprehensive dataset normalizer with semantic deduplication and enrichment."""
    
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
        
        # Stop words for similarity calculation
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'what', 'when', 'where',
            'who', 'why', 'how', 'can', 'could', 'would', 'should', 'may', 'might'
        ])
        
    def normalize_text(self, text: str) -> str:
        """Apply comprehensive text normalization."""
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
        text = text.replace('Ã©', 'e').replace('Ã¡', 'a').replace('Ã±', 'n')
        
        # Standardize punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)  # Add single space after punctuation
        text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces
        
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
        """Expand known abbreviations for consistency."""
        text_lower = text.lower()
        
        for abbr, expansion in self.abbreviations.items():
            # Case-insensitive replacement with word boundaries
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # Normalize for comparison
        text1_normalized = self.normalize_text(text1).lower()
        text2_normalized = self.normalize_text(text2).lower()
        
        # Remove stop words for better similarity matching
        words1 = set(word for word in text1_normalized.split() if word not in self.stop_words)
        words2 = set(word for word in text2_normalized.split() if word not in self.stop_words)
        
        # If either is empty after stop word removal, use original
        if not words1 or not words2:
            return SequenceMatcher(None, text1_normalized, text2_normalized).ratio()
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        jaccard = len(intersection) / len(union)
        
        # Also use sequence matcher for order-aware similarity
        sequence_sim = SequenceMatcher(None, text1_normalized, text2_normalized).ratio()
        
        # Weighted average
        return 0.6 * jaccard + 0.4 * sequence_sim
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count (approximation for GPT-style tokenization)."""
        # Rough estimate: ~4 characters per token on average
        # More sophisticated: count words and punctuation
        words = text.split()
        punctuation = len(re.findall(r'[.,!?;:()]', text))
        
        # Estimate: words + extra for subword tokens + punctuation
        estimated_tokens = len(words) + (len(words) // 3) + punctuation
        return estimated_tokens
    
    def calculate_complexity_score(self, text: str) -> str:
        """Calculate text complexity (simple, moderate, complex)."""
        # Factors: sentence length, word length, technical terms
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Count technical terms (simplified)
        technical_terms = sum(1 for w in words if len(w) > 10 or '-' in w)
        technical_ratio = technical_terms / max(len(words), 1)
        
        # Scoring
        if avg_sentence_length < 15 and avg_word_length < 6 and technical_ratio < 0.1:
            return "simple"
        elif avg_sentence_length > 25 or avg_word_length > 7 or technical_ratio > 0.2:
            return "complex"
        else:
            return "moderate"
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for metadata."""
        # Simple keyword extraction based on importance patterns
        key_terms = []
        
        # Extract capitalized terms (likely proper nouns/important terms)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        key_terms.extend(capitalized[:5])  # Limit to top 5
        
        # Extract terms in quotes
        quoted = re.findall(r'"([^"]+)"', text)
        key_terms.extend(quoted[:3])
        
        # Extract acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        key_terms.extend(acronyms[:3])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)
        
        return unique_terms[:10]  # Max 10 key terms
    
    def deduplicate_semantically(self, entries: List[Dict], threshold: float = 0.85) -> List[Dict]:
        """Remove semantic duplicates based on similarity threshold."""
        print(f"🔍 Performing semantic deduplication (threshold: {threshold})...")
        
        deduplicated = []
        seen_entries = []
        duplicates_removed = 0
        
        for i, entry in enumerate(entries):
            if i % 5000 == 0:
                print(f"  Processing entry {i}/{len(entries)}...")
            
            is_duplicate = False
            
            # Create signature for quick comparison
            inst_normalized = self.normalize_text(entry['instruction']).lower()
            resp_normalized = self.normalize_text(entry['response']).lower()[:200]  # First 200 chars
            
            # Check against seen entries
            for seen in seen_entries:
                # Quick check with instruction similarity
                inst_sim = self.calculate_text_similarity(
                    entry['instruction'], 
                    seen['instruction']
                )
                
                if inst_sim > threshold:
                    # If instructions are very similar, check responses
                    resp_sim = self.calculate_text_similarity(
                        entry['response'][:500],  # Compare first 500 chars for efficiency
                        seen['response'][:500]
                    )
                    
                    if resp_sim > threshold * 0.9:  # Slightly lower threshold for responses
                        is_duplicate = True
                        duplicates_removed += 1
                        break
            
            if not is_duplicate:
                deduplicated.append(entry)
                seen_entries.append(entry)
                
                # Keep seen_entries list manageable
                if len(seen_entries) > 1000:
                    seen_entries = seen_entries[-500:]  # Keep recent 500
        
        print(f"  ✅ Removed {duplicates_removed} semantic duplicates")
        return deduplicated
    
    def enrich_metadata(self, entry: Dict) -> Dict:
        """Add rich metadata to each entry."""
        enriched = entry.copy()
        
        # Add token counts
        enriched['metadata'] = {
            'instruction_tokens': self.estimate_token_count(entry['instruction']),
            'response_tokens': self.estimate_token_count(entry['response']),
            'total_tokens': self.estimate_token_count(entry['instruction']) + self.estimate_token_count(entry['response']),
            
            # Add length metrics
            'instruction_length': len(entry['instruction']),
            'response_length': len(entry['response']),
            
            # Add complexity scores
            'instruction_complexity': self.calculate_complexity_score(entry['instruction']),
            'response_complexity': self.calculate_complexity_score(entry['response']),
            
            # Extract key terms
            'key_terms': self.extract_key_terms(entry['instruction'] + ' ' + entry['response']),
            
            # Question type classification
            'question_type': self.classify_question_type(entry['instruction']),
            
            # Response type
            'response_type': self.classify_response_type(entry['response']),
            
            # Quality score (based on length and completeness)
            'quality_score': self.calculate_quality_score(entry)
        }
        
        return enriched
    
    def classify_question_type(self, instruction: str) -> str:
        """Classify the type of question/instruction."""
        inst_lower = instruction.lower()
        
        if inst_lower.startswith(('what is', 'what are', 'what does')):
            return 'definition'
        elif inst_lower.startswith(('how to', 'how do', 'how can')):
            return 'procedural'
        elif inst_lower.startswith(('why', 'explain why')):
            return 'explanatory'
        elif inst_lower.startswith(('when', 'what time')):
            return 'temporal'
        elif inst_lower.startswith(('who', 'whom')):
            return 'identity'
        elif inst_lower.startswith(('define', 'definition')):
            return 'definition'
        elif inst_lower.startswith(('compare', 'difference', 'contrast')):
            return 'comparison'
        elif inst_lower.startswith(('list', 'enumerate', 'what are all')):
            return 'enumeration'
        elif 'calculate' in inst_lower or 'compute' in inst_lower:
            return 'calculation'
        else:
            return 'general'
    
    def classify_response_type(self, response: str) -> str:
        """Classify the type of response."""
        resp_lower = response.lower()
        
        if 'definition:' in resp_lower or resp_lower.startswith('a ') or resp_lower.startswith('an '):
            return 'definition'
        elif any(marker in resp_lower for marker in ['step 1', '1.', 'first,', 'second,', 'finally']):
            return 'step_by_step'
        elif 'for example' in resp_lower or 'such as' in resp_lower:
            return 'example_based'
        elif len(response) < 100:
            return 'brief'
        elif len(response) > 500:
            return 'detailed'
        elif '•' in response or '- ' in response:
            return 'list'
        else:
            return 'standard'
    
    def calculate_quality_score(self, entry: Dict) -> float:
        """Calculate quality score for the entry (0-1)."""
        score = 0.0
        
        # Length factors
        inst_len = len(entry['instruction'])
        resp_len = len(entry['response'])
        
        # Good instruction length (not too short, not too long)
        if 10 <= inst_len <= 200:
            score += 0.2
        elif inst_len < 10:
            score += 0.05
        else:
            score += 0.1
        
        # Good response length
        if 50 <= resp_len <= 1000:
            score += 0.3
        elif resp_len < 50:
            score += 0.1
        else:
            score += 0.2
        
        # Has proper ending punctuation
        if entry['response'].strip().endswith(('.', '!', '?')):
            score += 0.1
        
        # Has context
        if 'context' in entry and entry['context']:
            score += 0.1
        
        # Response completeness (doesn't end abruptly)
        if not entry['response'].endswith('...'):
            score += 0.1
        
        # Instruction clarity (starts with clear indicator)
        inst_starters = ['what', 'how', 'why', 'when', 'who', 'define', 'explain', 'describe']
        if any(entry['instruction'].lower().startswith(s) for s in inst_starters):
            score += 0.2
        
        return min(score, 1.0)
    
    def standardize_context_labels(self, context: str) -> str:
        """Standardize context labels to consistent format."""
        return self.context_standardization.get(context, 'general')
    
    def process_dataset(self, input_file: str, output_file: str) -> Dict:
        """Process the entire dataset with all normalizations."""
        print("🚀 STARTING COMPREHENSIVE DATASET NORMALIZATION")
        print("=" * 60)
        
        stats = {
            'total_entries': 0,
            'processed_entries': 0,
            'semantic_duplicates': 0,
            'quality_filtered': 0,
            'context_distribution': defaultdict(int),
            'question_types': defaultdict(int),
            'quality_scores': []
        }
        
        # Read all entries
        print("📖 Reading dataset...")
        entries = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    stats['total_entries'] += 1
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        print(f"  Loaded {len(entries)} entries")
        
        # Step 1: Text normalization
        print("\n📝 Normalizing text...")
        for i, entry in enumerate(entries):
            if i % 5000 == 0:
                print(f"  Processing {i}/{len(entries)}...")
            
            entry['instruction'] = self.normalize_text(entry['instruction'])
            entry['response'] = self.normalize_text(entry['response'])
            entry['instruction'] = self.expand_abbreviations(entry['instruction'])
            entry['response'] = self.expand_abbreviations(entry['response'])
        
        # Step 2: Semantic deduplication
        entries = self.deduplicate_semantically(entries, threshold=0.85)
        stats['semantic_duplicates'] = stats['total_entries'] - len(entries)
        
        # Step 3: Context standardization and metadata enrichment
        print("\n🏷️ Standardizing labels and enriching metadata...")
        enriched_entries = []
        
        for i, entry in enumerate(entries):
            if i % 5000 == 0:
                print(f"  Processing {i}/{len(entries)}...")
            
            # Standardize context
            if 'context' in entry:
                entry['context'] = self.standardize_context_labels(entry['context'])
                stats['context_distribution'][entry['context']] += 1
            
            # Enrich with metadata
            enriched_entry = self.enrich_metadata(entry)
            
            # Track statistics
            stats['question_types'][enriched_entry['metadata']['question_type']] += 1
            stats['quality_scores'].append(enriched_entry['metadata']['quality_score'])
            
            # Quality filtering (keep only good quality entries)
            if enriched_entry['metadata']['quality_score'] >= 0.3:
                enriched_entries.append(enriched_entry)
            else:
                stats['quality_filtered'] += 1
        
        stats['processed_entries'] = len(enriched_entries)
        
        # Step 4: Sort by quality score (best first)
        print("\n📊 Sorting by quality...")
        enriched_entries.sort(key=lambda x: x['metadata']['quality_score'], reverse=True)
        
        # Step 5: Save normalized dataset
        print(f"\n💾 Saving normalized dataset to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in enriched_entries:
                # Create clean version without metadata for training
                clean_entry = {
                    'instruction': entry['instruction'],
                    'context': entry.get('context', 'general'),
                    'response': entry['response']
                }
                f.write(json.dumps(clean_entry, ensure_ascii=False) + '\n')
        
        # Also save version with metadata
        metadata_file = output_file.replace('.jsonl', '_with_metadata.jsonl')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            for entry in enriched_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"  Also saved metadata version: {metadata_file}")
        
        return stats

def print_normalization_report(stats: Dict):
    """Print detailed normalization report."""
    print("\n" + "=" * 60)
    print("📊 NORMALIZATION REPORT")
    print("=" * 60)
    
    print(f"\n📈 Processing Statistics:")
    print(f"  • Original entries: {stats['total_entries']:,}")
    print(f"  • After deduplication: {stats['total_entries'] - stats['semantic_duplicates']:,}")
    print(f"  • After quality filtering: {stats['processed_entries']:,}")
    print(f"  • Semantic duplicates removed: {stats['semantic_duplicates']:,}")
    print(f"  • Low quality filtered: {stats['quality_filtered']:,}")
    
    print(f"\n🏷️ Context Distribution:")
    for context, count in sorted(stats['context_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['processed_entries']) * 100
        print(f"  • {context}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n❓ Question Type Distribution:")
    for qtype, count in sorted(stats['question_types'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['processed_entries']) * 100
        print(f"  • {qtype}: {count:,} ({percentage:.1f}%)")
    
    if stats['quality_scores']:
        avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
        print(f"\n⭐ Quality Metrics:")
        print(f"  • Average quality score: {avg_quality:.3f}")
        print(f"  • Min quality score: {min(stats['quality_scores']):.3f}")
        print(f"  • Max quality score: {max(stats['quality_scores']):.3f}")

def main():
    input_file = "fannie_mae_ultimate_with_context.jsonl"
    output_file = "fannie_mae_normalized_final.jsonl"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    normalizer = FannieDatasetNormalizer()
    stats = normalizer.process_dataset(input_file, output_file)
    
    print_normalization_report(stats)
    
    print("\n" + "=" * 60)
    print("✅ NORMALIZATION COMPLETE!")
    print(f"📄 Output file: {output_file}")
    print(f"📄 Metadata file: {output_file.replace('.jsonl', '_with_metadata.jsonl')}")
    print(f"📊 Final entries: {stats['processed_entries']:,}")
    print("🎯 Dataset is now normalized, deduplicated, and enriched!")

if __name__ == "__main__":
    main()