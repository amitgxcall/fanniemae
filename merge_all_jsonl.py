#!/usr/bin/env python3
import json
import glob
from typing import List, Dict, Set

def merge_all_jsonl_files() -> List[Dict[str, str]]:
    """Merge all JSONL files into one comprehensive dataset."""
    
    # Find all JSONL files
    jsonl_files = glob.glob("*.jsonl")
    fannie_files = [f for f in jsonl_files if 'fannie' in f.lower() or 'selling' in f.lower()]
    
    print("Found JSONL files to merge:")
    for file in fannie_files:
        print(f"  - {file}")
    
    all_entries = []
    seen_signatures = set()
    
    for filename in fannie_files:
        print(f"\nProcessing {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file_entries = 0
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Validate required fields
                        if 'instruction' not in data or 'output' not in data:
                            print(f"    Warning: Missing required fields in line {line_num}")
                            continue
                        
                        # Clean up text
                        instruction = ' '.join(data['instruction'].split())
                        output = ' '.join(data['output'].split())
                        
                        # Skip if too short
                        if len(instruction) < 5 or len(output) < 10:
                            continue
                        
                        # Create signature for deduplication
                        signature = (instruction.lower()[:100], output.lower()[:100])
                        
                        if signature not in seen_signatures:
                            seen_signatures.add(signature)
                            all_entries.append({
                                'instruction': instruction,
                                'output': output,
                                'source_file': filename
                            })
                            file_entries += 1
                    
                    except json.JSONDecodeError as e:
                        print(f"    Error parsing JSON on line {line_num}: {e}")
                        continue
                
                print(f"    Added {file_entries} unique entries")
        
        except FileNotFoundError:
            print(f"    File not found: {filename}")
        except Exception as e:
            print(f"    Error processing {filename}: {e}")
    
    return all_entries

def save_merged_dataset(entries: List[Dict[str, str]], output_file: str):
    """Save merged dataset to file."""
    
    # Sort by instruction length for better organization
    entries.sort(key=lambda x: len(x['instruction']))
    
    # Remove source_file before saving
    clean_entries = []
    for entry in entries:
        clean_entries.append({
            'instruction': entry['instruction'],
            'output': entry['output']
        })
    
    # Save to JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in clean_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return len(clean_entries)

def analyze_dataset(entries: List[Dict[str, str]]):
    """Analyze the merged dataset."""
    
    print("\n" + "="*60)
    print("DATASET ANALYSIS")
    print("="*60)
    
    # Count by source file
    source_counts = {}
    for entry in entries:
        source = entry.get('source_file', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print(f"\nEntries by source file:")
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} entries")
    
    # Analyze instruction patterns
    instruction_patterns = {
        'what_is': 0,
        'how_to': 0,
        'what_are': 0,
        'requirements': 0,
        'other': 0
    }
    
    for entry in entries:
        instruction = entry['instruction'].lower()
        if instruction.startswith('what is'):
            instruction_patterns['what_is'] += 1
        elif instruction.startswith('what are'):
            instruction_patterns['what_are'] += 1
        elif 'how to' in instruction or 'how do' in instruction:
            instruction_patterns['how_to'] += 1
        elif 'requirement' in instruction or 'criteria' in instruction:
            instruction_patterns['requirements'] += 1
        else:
            instruction_patterns['other'] += 1
    
    print(f"\nInstruction patterns:")
    for pattern, count in instruction_patterns.items():
        percentage = (count / len(entries)) * 100
        print(f"  {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    # Length analysis
    inst_lengths = [len(entry['instruction']) for entry in entries]
    out_lengths = [len(entry['output']) for entry in entries]
    
    print(f"\nLength statistics:")
    print(f"  Instructions: {min(inst_lengths)}-{max(inst_lengths)} chars (avg: {sum(inst_lengths)//len(inst_lengths)})")
    print(f"  Outputs: {min(out_lengths)}-{max(out_lengths)} chars (avg: {sum(out_lengths)//len(out_lengths)})")
    
    return source_counts

def main():
    print("Merging all Fannie Mae JSONL files...")
    
    # Merge all files
    all_entries = merge_all_jsonl_files()
    
    if not all_entries:
        print("No entries found to merge!")
        return
    
    # Analyze dataset
    analyze_dataset(all_entries)
    
    # Save merged dataset
    output_file = "fannie_mae_master_knowledge_base.jsonl"
    unique_count = save_merged_dataset(all_entries, output_file)
    
    print(f"\n" + "="*60)
    print("MERGE COMPLETE")
    print("="*60)
    print(f"✓ Total unique entries: {unique_count}")
    print(f"✓ Output file: {output_file}")
    print(f"✓ File size: {round(sum(len(json.dumps(e)) for e in all_entries[:unique_count]) / 1024, 1)} KB")
    
    # Show samples
    print(f"\nFirst 3 entries:")
    print("-" * 40)
    for i in range(min(3, len(all_entries))):
        entry = all_entries[i]
        print(f"\n[{i+1}] {entry['instruction']}")
        print(f"    {entry['output'][:100]}...")
    
    print(f"\nLast 3 entries:")
    print("-" * 40)
    for i in range(max(0, len(all_entries)-3), len(all_entries)):
        entry = all_entries[i]
        print(f"\n[{i+1}] {entry['instruction']}")
        print(f"    {entry['output'][:100]}...")

if __name__ == "__main__":
    main()