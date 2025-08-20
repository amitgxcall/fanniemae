#!/usr/bin/env python3
import json
import os

def update_context_to_field(input_file: str, output_file: str):
    """Update all context values to 'field' in the dataset."""
    
    print("🔄 UPDATING CONTEXT VALUES TO 'field'")
    print("=" * 60)
    
    updated_count = 0
    total_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                total_count += 1
                
                # Update context to 'field'
                data['context'] = 'field'
                updated_count += 1
                
                # Write updated entry
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
                # Progress indicator
                if updated_count % 5000 == 0:
                    print(f"  Processed {updated_count:,} entries...")
                    
            except json.JSONDecodeError as e:
                print(f"  ⚠️ Line {line_num}: JSON error - {e}")
                continue
    
    print(f"\n✅ Update complete!")
    print(f"📊 Total entries processed: {total_count:,}")
    print(f"📊 Context updated to 'field': {updated_count:,}")
    
    # Get file size
    output_size = os.path.getsize(output_file)
    print(f"📁 Output file size: {output_size:,} bytes ({output_size/1024/1024:.2f} MB)")
    
    return updated_count

def verify_context_values(file_path: str, sample_size: int = 10):
    """Verify that all context values are 'field'."""
    
    print(f"\n🔍 Verifying context values in {file_path}...")
    
    context_values = set()
    sample_entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line.strip())
                context_values.add(data.get('context', 'missing'))
                
                if len(sample_entries) < sample_size:
                    sample_entries.append(data)
                    
            except json.JSONDecodeError:
                continue
    
    print(f"  Unique context values found: {context_values}")
    
    if context_values == {'field'}:
        print("  ✅ All context values are 'field'")
    else:
        print(f"  ❌ Found other context values: {context_values}")
    
    # Show samples
    print(f"\n📋 Sample entries:")
    for i, entry in enumerate(sample_entries[:3], 1):
        print(f"\n  Sample {i}:")
        print(f"    Instruction: {entry['instruction'][:80]}...")
        print(f"    Context: {entry['context']}")
        print(f"    Response: {entry['response'][:80]}...")

def main():
    input_file = "fannie_mae_normalized_final.jsonl"
    output_file = "fannie_mae_normalized_final_field.jsonl"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Update context values
    count = update_context_to_field(input_file, output_file)
    
    # Verify the update
    verify_context_values(output_file)
    
    # Replace original file
    print(f"\n📝 Replacing original file with updated version...")
    os.rename(output_file, input_file)
    print(f"✅ File updated: {input_file}")
    
    print("\n" + "=" * 60)
    print("🎉 CONTEXT UPDATE COMPLETE!")
    print(f"📄 Updated file: {input_file}")
    print(f"📊 All {count:,} entries now have context='field'")

if __name__ == "__main__":
    main()