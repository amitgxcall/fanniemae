import json
import re
from typing import Dict, List, Set
import hashlib
from collections import Counter

def normalize_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1\2', text)
    
    return text

def create_hash(record: Dict) -> str:
    content = json.dumps(record, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

def clean_record(record: Dict) -> Dict:
    cleaned = {}
    
    for key, value in record.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        
        if isinstance(value, str):
            cleaned_value = normalize_text(value)
            if cleaned_value:
                cleaned[key] = cleaned_value
        elif isinstance(value, (int, float, bool)):
            cleaned[key] = value
        elif isinstance(value, list):
            cleaned_list = [normalize_text(item) if isinstance(item, str) else item 
                          for item in value if item]
            if cleaned_list:
                cleaned[key] = cleaned_list
        elif isinstance(value, dict):
            cleaned_dict = clean_record(value)
            if cleaned_dict:
                cleaned[key] = cleaned_dict
        else:
            cleaned[key] = value
    
    return cleaned

def process_dataset(input_file: str, output_file: str):
    print(f"Processing {input_file}...")
    
    records = []
    seen_hashes = set()
    duplicates = 0
    invalid_records = 0
    empty_records = 0
    
    stats = {
        'total_records': 0,
        'valid_records': 0,
        'duplicates': 0,
        'invalid_json': 0,
        'empty_after_cleaning': 0,
        'missing_instruction': 0,
        'missing_output': 0,
        'field_counts': Counter()
    }
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total_records'] += 1
            
            if line_num % 5000 == 0:
                print(f"Processed {line_num} records...")
            
            try:
                record = json.loads(line.strip())
            except json.JSONDecodeError:
                stats['invalid_json'] += 1
                print(f"Invalid JSON at line {line_num}")
                continue
            
            cleaned = clean_record(record)
            
            if not cleaned:
                stats['empty_after_cleaning'] += 1
                continue
            
            if 'instruction' not in cleaned:
                stats['missing_instruction'] += 1
                continue
            
            if 'output' not in cleaned and 'response' not in cleaned:
                stats['missing_output'] += 1
                continue
            
            if 'response' in cleaned and 'output' not in cleaned:
                cleaned['output'] = cleaned.pop('response')
            
            if 'input' in cleaned and not cleaned['input']:
                del cleaned['input']
            
            if 'context' in cleaned and not cleaned['context']:
                del cleaned['context']
            
            record_hash = create_hash(cleaned)
            if record_hash in seen_hashes:
                stats['duplicates'] += 1
                continue
            
            seen_hashes.add(record_hash)
            records.append(cleaned)
            stats['valid_records'] += 1
            
            for field in cleaned.keys():
                stats['field_counts'][field] += 1
    
    records.sort(key=lambda x: (len(x.get('instruction', '')), x.get('instruction', '')))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print("\n=== Dataset Cleaning Summary ===")
    print(f"Total records processed: {stats['total_records']}")
    print(f"Valid records after cleaning: {stats['valid_records']}")
    print(f"Duplicates removed: {stats['duplicates']}")
    print(f"Invalid JSON records: {stats['invalid_json']}")
    print(f"Empty after cleaning: {stats['empty_after_cleaning']}")
    print(f"Missing instruction field: {stats['missing_instruction']}")
    print(f"Missing output/response field: {stats['missing_output']}")
    print(f"\nField distribution:")
    for field, count in stats['field_counts'].most_common():
        print(f"  {field}: {count} records")
    print(f"\nCleaned dataset saved to: {output_file}")
    
    return stats

def validate_cleaned_dataset(file_path: str):
    print(f"\nValidating {file_path}...")
    
    valid = True
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                
                if 'instruction' not in record:
                    issues.append(f"Line {line_num}: Missing 'instruction' field")
                    valid = False
                
                if 'output' not in record:
                    issues.append(f"Line {line_num}: Missing 'output' field")
                    valid = False
                
                if 'instruction' in record and not record['instruction'].strip():
                    issues.append(f"Line {line_num}: Empty instruction")
                    valid = False
                
                if 'output' in record and not record['output'].strip():
                    issues.append(f"Line {line_num}: Empty output")
                    valid = False
                    
            except json.JSONDecodeError:
                issues.append(f"Line {line_num}: Invalid JSON")
                valid = False
    
    if valid:
        print("✓ Dataset validation passed!")
    else:
        print("✗ Dataset validation failed:")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    
    return valid

if __name__ == "__main__":
    input_file = "fannie_mae_ultimate_merged_dataset.jsonl"
    output_file = "fannie_mae_cleaned_llm_ready.jsonl"
    
    stats = process_dataset(input_file, output_file)
    validate_cleaned_dataset(output_file)