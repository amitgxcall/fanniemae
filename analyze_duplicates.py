import json
from collections import Counter
import hashlib

def analyze_duplicates(file_path):
    print(f"Analyzing duplicates in {file_path}...")
    
    instructions = []
    outputs = []
    instruction_output_pairs = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line.strip())
            inst = record.get('instruction', '').lower().strip()
            out = record.get('output', '').lower().strip()
            
            instructions.append(inst)
            outputs.append(out)
            instruction_output_pairs.append((inst, out))
    
    instruction_counts = Counter(instructions)
    output_counts = Counter(outputs)
    pair_counts = Counter(instruction_output_pairs)
    
    duplicate_instructions = {k: v for k, v in instruction_counts.items() if v > 1}
    duplicate_outputs = {k: v for k, v in output_counts.items() if v > 1}
    duplicate_pairs = {k: v for k, v in pair_counts.items() if v > 1}
    
    print(f"\nTotal records: {len(instructions)}")
    print(f"Unique instructions: {len(set(instructions))}")
    print(f"Unique outputs: {len(set(outputs))}")
    print(f"Unique instruction-output pairs: {len(set(instruction_output_pairs))}")
    
    print(f"\nDuplicate instructions: {len(duplicate_instructions)}")
    print(f"Duplicate outputs: {len(duplicate_outputs)}")
    print(f"Duplicate instruction-output pairs: {len(duplicate_pairs)}")
    
    if duplicate_pairs:
        print("\nTop 5 duplicate instruction-output pairs:")
        for (inst, out), count in list(sorted(duplicate_pairs.items(), key=lambda x: x[1], reverse=True))[:5]:
            print(f"  Count: {count}")
            print(f"  Instruction: {inst[:100]}...")
            print(f"  Output: {out[:100]}...")
            print()
    
    return len(duplicate_pairs)

def remove_exact_duplicates(input_file, output_file):
    print(f"\nRemoving exact duplicates from {input_file}...")
    
    seen_pairs = set()
    unique_records = []
    duplicates_removed = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line.strip())
            
            pair_key = (
                record.get('instruction', '').lower().strip(),
                record.get('output', '').lower().strip()
            )
            
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                unique_records.append(record)
            else:
                duplicates_removed += 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in unique_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"Removed {duplicates_removed} duplicate records")
    print(f"Final dataset has {len(unique_records)} unique records")
    print(f"Saved to {output_file}")
    
    return len(unique_records)

if __name__ == "__main__":
    dup_count = analyze_duplicates("fannie_mae_cleaned_llm_ready.jsonl")
    
    if dup_count > 0:
        remove_exact_duplicates(
            "fannie_mae_cleaned_llm_ready.jsonl",
            "fannie_mae_cleaned_deduped.jsonl"
        )
        print("\n=== After Deduplication ===")
        analyze_duplicates("fannie_mae_cleaned_deduped.jsonl")
    else:
        print("\nNo duplicates found! Dataset is ready for LLM training.")