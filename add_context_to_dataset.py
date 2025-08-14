#!/usr/bin/env python3
import json
import re
from typing import List, Dict, Set
import os

def determine_context(instruction: str, output: str) -> str:
    """
    Determine appropriate context based on instruction and output content.
    
    Args:
        instruction: The instruction/question text
        output: The response/answer text
        
    Returns:
        Context string describing the domain/category
    """
    
    # Convert to lowercase for analysis
    inst_lower = instruction.lower()
    out_lower = output.lower()
    combined = f"{inst_lower} {out_lower}"
    
    # Define context patterns and their keywords
    context_patterns = {
        "Mortgage Terminology and Definitions": [
            "define", "definition", "what is", "what are", "meaning of", "refer to",
            "mortgage", "loan", "interest rate", "payment", "principal", "refinance"
        ],
        
        "Fannie Mae Products and Programs": [
            "homeready", "refinow", "homestyle", "mh advantage", "homepath", 
            "desktop underwriter", "du", "collateral underwriter", "day 1 certainty",
            "fannie mae connect", "selling guide", "servicing marketplace"
        ],
        
        "Loan Origination and Underwriting": [
            "underwriting", "origination", "qualification", "approval", "credit score",
            "debt-to-income", "dti", "loan-to-value", "ltv", "down payment",
            "closing", "application", "urla", "1003"
        ],
        
        "Property and Real Estate": [
            "property", "real estate", "appraisal", "valuation", "deed", "title",
            "foreclosure", "reo", "condominium", "single-family", "multifamily",
            "manufactured housing", "units"
        ],
        
        "Financial Terms and Calculations": [
            "piti", "escrow", "points", "fees", "rate lock", "buydown", "amortization",
            "principal", "interest", "taxes", "insurance", "payment", "balance"
        ],
        
        "Government Programs and Regulations": [
            "fha", "va", "usda", "fhfa", "hud", "federal", "government", 
            "regulation", "compliance", "oversight", "guidelines", "requirements"
        ],
        
        "Multifamily and Commercial": [
            "multifamily", "commercial", "dus", "delegated underwriting", 
            "apartment", "rental", "investment property", "cap rate", "noi",
            "debt service coverage", "dscr"
        ],
        
        "Data Dictionary and Attributes": [
            "data type", "allowable values", "field", "attribute", "element",
            "number", "date", "text", "indicator", "flag", "code"
        ],
        
        "Secondary Market and Securities": [
            "mbs", "mortgage-backed securities", "umbs", "uniform mortgage-backed",
            "securitization", "tba", "secondary market", "pooling", "issuance"
        ],
        
        "Technology and Digital Services": [
            "digital", "technology", "online", "platform", "system", "software",
            "automated", "electronic", "api", "integration", "portal"
        ]
    }
    
    # Score each context based on keyword matches
    context_scores = {}
    
    for context, keywords in context_patterns.items():
        score = 0
        for keyword in keywords:
            # Count occurrences in instruction (weighted more)
            score += inst_lower.count(keyword) * 3
            # Count occurrences in output
            score += out_lower.count(keyword) * 2
        
        context_scores[context] = score
    
    # Find the highest scoring context
    if context_scores:
        best_context = max(context_scores.keys(), key=lambda k: context_scores[k])
        
        # If no keywords matched, use a default context based on instruction type
        if context_scores[best_context] == 0:
            if inst_lower.startswith(("define", "what is", "what are")):
                return "Mortgage Terminology and Definitions"
            elif "data type" in out_lower or "allowable values" in out_lower:
                return "Data Dictionary and Attributes"
            elif "fannie mae" in combined:
                return "Fannie Mae Products and Programs"
            else:
                return "General Mortgage Knowledge"
        
        return best_context
    
    return "General Mortgage Knowledge"

def add_context_to_dataset(input_file: str, output_file: str) -> Dict:
    """
    Add context field to each entry in the JSONL dataset.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file with context
        
    Returns:
        Statistics about the conversion
    """
    
    print("🔄 ADDING CONTEXT TO FANNIE MAE DATASET")
    print("=" * 60)
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    stats = {
        'total_entries': 0,
        'processed_entries': 0,
        'context_distribution': {},
        'skipped_entries': 0
    }
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                stats['total_entries'] += 1
                
                # Validate required fields
                if 'instruction' not in data or 'output' not in data:
                    print(f"⚠️  Line {line_num}: Missing required fields")
                    stats['skipped_entries'] += 1
                    continue
                
                # Determine context
                context = determine_context(data['instruction'], data['output'])
                
                # Create new entry with context
                new_entry = {
                    'instruction': data['instruction'],
                    'context': context,
                    'response': data['output']  # Renamed from 'output' to 'response'
                }
                
                # Update context distribution
                stats['context_distribution'][context] = stats['context_distribution'].get(context, 0) + 1
                
                # Write to output file
                outfile.write(json.dumps(new_entry, ensure_ascii=False) + '\n')
                stats['processed_entries'] += 1
                
                # Progress indicator
                if stats['processed_entries'] % 5000 == 0:
                    print(f"📊 Processed {stats['processed_entries']:,} entries...")
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Line {line_num}: JSON error - {e}")
                stats['skipped_entries'] += 1
                continue
            except Exception as e:
                print(f"⚠️  Line {line_num}: Error - {e}")
                stats['skipped_entries'] += 1
                continue
    
    # Calculate output file size
    output_size = os.path.getsize(output_file)
    stats['output_size'] = output_size
    
    print(f"\n✅ Context addition complete!")
    print(f"📊 Total entries processed: {stats['processed_entries']:,}")
    print(f"📊 Entries skipped: {stats['skipped_entries']}")
    print(f"📁 Output file size: {output_size:,} bytes ({output_size/1024/1024:.1f} MB)")
    
    return stats

def print_context_statistics(stats: Dict):
    """Print detailed context distribution statistics."""
    
    print(f"\n📊 CONTEXT DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    total_entries = stats['processed_entries']
    
    print(f"📈 Context breakdown ({total_entries:,} total entries):")
    
    # Sort contexts by frequency
    sorted_contexts = sorted(
        stats['context_distribution'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for context, count in sorted_contexts:
        percentage = (count / total_entries) * 100
        print(f"  📋 {context}")
        print(f"      {count:,} entries ({percentage:.1f}%)")
    
    print(f"\n🔍 Context diversity: {len(stats['context_distribution'])} different contexts")

def show_context_samples(output_file: str, num_samples: int = 3):
    """Show sample entries with context from each major category."""
    
    print(f"\n📋 SAMPLE ENTRIES WITH CONTEXT")
    print("=" * 60)
    
    # Collect samples by context
    context_samples = {}
    
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                context = data['context']
                
                if context not in context_samples:
                    context_samples[context] = []
                
                if len(context_samples[context]) < num_samples:
                    context_samples[context].append(data)
                    
            except json.JSONDecodeError:
                continue
    
    # Show samples from each context
    for context, samples in context_samples.items():
        print(f"\n🏷️  {context}")
        print("-" * 50)
        
        for i, sample in enumerate(samples, 1):
            print(f"[Sample {i}]")
            print(f"Q: {sample['instruction']}")
            print(f"A: {sample['response'][:120]}{'...' if len(sample['response']) > 120 else ''}")
            if i < len(samples):
                print()

def main():
    input_file = "fannie_mae_ultimate_merged_dataset.jsonl"
    output_file = "fannie_mae_ultimate_with_context.jsonl"
    
    print("🎯 ADDING CONTEXT TO FANNIE MAE ULTIMATE DATASET")
    print("=" * 60)
    print(f"📥 Input: {input_file}")
    print(f"📤 Output: {output_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Add context to dataset
    stats = add_context_to_dataset(input_file, output_file)
    
    # Print detailed statistics
    print_context_statistics(stats)
    
    # Show sample entries
    show_context_samples(output_file)
    
    print(f"\n🎉 CONTEXT ADDITION COMPLETE!")
    print("=" * 60)
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total entries: {stats['processed_entries']:,}")
    print(f"💾 File size: {stats['output_size']/1024/1024:.1f} MB")
    print(f"🎯 Ready for LLM training with context!")

if __name__ == "__main__":
    main()