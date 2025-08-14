#!/usr/bin/env python3
import json
from typing import List, Dict, Set
import os

def merge_specific_jsonl_files(files_to_merge: List[str], output_file: str) -> Dict:
    """
    Merge specific JSONL files with deduplication.
    
    Args:
        files_to_merge: List of file paths to merge
        output_file: Output file path
        
    Returns:
        Dictionary with merge statistics
    """
    
    print("🔄 MERGING SPECIFIC JSONL FILES")
    print("=" * 60)
    
    all_entries = []
    seen_signatures = set()
    stats = {
        'total_files': len(files_to_merge),
        'file_stats': {},
        'total_raw_entries': 0,
        'unique_entries': 0,
        'duplicates_removed': 0
    }
    
    for file_path in files_to_merge:
        print(f"\n📂 Processing: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ File not found: {file_path}")
            continue
        
        file_entries = 0
        file_unique = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        file_entries += 1
                        
                        # Validate required fields
                        if 'instruction' not in data or 'output' not in data:
                            print(f"   ⚠️  Line {line_num}: Missing required fields")
                            continue
                        
                        # Clean up text
                        instruction = ' '.join(data['instruction'].split())
                        output = ' '.join(data['output'].split())
                        
                        # Skip if too short
                        if len(instruction) < 5 or len(output) < 10:
                            continue
                        
                        # Create signature for deduplication (using first 150 chars)
                        signature = (instruction.lower()[:150], output.lower()[:150])
                        
                        if signature not in seen_signatures:
                            seen_signatures.add(signature)
                            all_entries.append({
                                'instruction': instruction,
                                'output': output,
                                'source_file': os.path.basename(file_path)
                            })
                            file_unique += 1
                    
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  Line {line_num}: JSON error - {e}")
                        continue
                    except Exception as e:
                        print(f"   ⚠️  Line {line_num}: Error - {e}")
                        continue
        
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            continue
        
        # Store file statistics
        stats['file_stats'][file_path] = {
            'raw_entries': file_entries,
            'unique_entries': file_unique,
            'file_size': os.path.getsize(file_path)
        }
        
        stats['total_raw_entries'] += file_entries
        print(f"   📊 Raw entries: {file_entries}")
        print(f"   ✅ Unique entries: {file_unique}")
        print(f"   📁 File size: {os.path.getsize(file_path):,} bytes")
    
    stats['unique_entries'] = len(all_entries)
    stats['duplicates_removed'] = stats['total_raw_entries'] - stats['unique_entries']
    
    # Sort entries by instruction length for consistency
    all_entries.sort(key=lambda x: len(x['instruction']))
    
    # Save merged file
    print(f"\n💾 SAVING MERGED FILE: {output_file}")
    print("=" * 60)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            # Remove source_file before saving
            clean_entry = {
                'instruction': entry['instruction'],
                'output': entry['output']
            }
            f.write(json.dumps(clean_entry, ensure_ascii=False) + '\n')
    
    # Calculate output file size
    output_size = os.path.getsize(output_file)
    stats['output_size'] = output_size
    
    print(f"✅ Merge complete!")
    print(f"📊 Total unique entries: {stats['unique_entries']:,}")
    print(f"📁 Output file size: {output_size:,} bytes ({output_size/1024/1024:.1f} MB)")
    
    return stats, all_entries

def print_merge_statistics(stats: Dict, entries: List[Dict]):
    """Print detailed merge statistics."""
    
    print(f"\n📊 DETAILED MERGE STATISTICS")
    print("=" * 60)
    
    print(f"📂 Files processed: {stats['total_files']}")
    print(f"📄 Total raw entries: {stats['total_raw_entries']:,}")
    print(f"✅ Unique entries: {stats['unique_entries']:,}")
    print(f"🗑️  Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"💾 Output file size: {stats['output_size']:,} bytes ({stats['output_size']/1024/1024:.1f} MB)")
    
    print(f"\n📋 Per-file breakdown:")
    for file_path, file_stats in stats['file_stats'].items():
        filename = os.path.basename(file_path)
        print(f"  📄 {filename}")
        print(f"      Raw: {file_stats['raw_entries']:,} entries")
        print(f"      Unique: {file_stats['unique_entries']:,} entries")
        print(f"      Size: {file_stats['file_size']:,} bytes")
    
    # Analyze by source
    print(f"\n🔍 Source file distribution in final dataset:")
    source_counts = {}
    for entry in entries:
        source = entry.get('source_file', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(entries)) * 100
        print(f"  📄 {source}: {count:,} entries ({percentage:.1f}%)")
    
    # Content analysis
    print(f"\n📏 Content length analysis:")
    inst_lengths = [len(entry['instruction']) for entry in entries]
    out_lengths = [len(entry['output']) for entry in entries]
    
    print(f"  Instructions: {min(inst_lengths)}-{max(inst_lengths)} chars (avg: {sum(inst_lengths)//len(inst_lengths)})")
    print(f"  Outputs: {min(out_lengths)}-{max(out_lengths)} chars (avg: {sum(out_lengths)//len(out_lengths)})")

def show_samples(entries: List[Dict], num_samples: int = 5):
    """Show sample entries from the merged dataset."""
    
    print(f"\n📋 SAMPLE ENTRIES FROM MERGED DATASET")
    print("=" * 60)
    
    # Show samples from beginning, middle, and end
    indices = [0, len(entries)//4, len(entries)//2, 3*len(entries)//4, len(entries)-1]
    
    for i, idx in enumerate(indices[:num_samples]):
        entry = entries[idx]
        print(f"\n[Sample {i+1} - Position {idx+1}/{len(entries)}]")
        print(f"Source: {entry.get('source_file', 'unknown')}")
        print(f"Q: {entry['instruction']}")
        print(f"A: {entry['output'][:120]}{'...' if len(entry['output']) > 120 else ''}")

def main():
    # Files to merge
    files_to_merge = [
        "final_1.jsonl",
        "fannie_mae_complete_dataset_20k.jsonl", 
        "fannie_mae_sample_1k.jsonl",
        "output/fannie_mae_simple_18445.jsonl"  # Largest output file
    ]
    
    output_file = "fannie_mae_ultimate_merged_dataset.jsonl"
    
    print("🎯 MERGING SPECIFIC FANNIE MAE JSONL FILES")
    print("=" * 60)
    print("Files to merge:")
    for file_path in files_to_merge:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path} (not found)")
    
    # Perform merge
    stats, entries = merge_specific_jsonl_files(files_to_merge, output_file)
    
    # Print detailed statistics
    print_merge_statistics(stats, entries)
    
    # Show samples
    show_samples(entries)
    
    print(f"\n🎉 MERGE COMPLETE!")
    print("=" * 60)
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total entries: {stats['unique_entries']:,}")
    print(f"💾 File size: {stats['output_size']/1024/1024:.1f} MB")
    print(f"🎯 Ready for training!")

if __name__ == "__main__":
    main()