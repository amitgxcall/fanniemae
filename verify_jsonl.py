#!/usr/bin/env python3
import json
import sys
from typing import Dict, List, Tuple

def verify_jsonl_format(filename: str) -> Dict:
    """Verify JSONL format and return detailed analysis."""
    
    results = {
        'valid': True,
        'total_lines': 0,
        'valid_entries': 0,
        'invalid_entries': 0,
        'errors': [],
        'warnings': [],
        'sample_entries': [],
        'field_analysis': {
            'instruction_stats': {'min': float('inf'), 'max': 0, 'avg': 0, 'total': 0},
            'output_stats': {'min': float('inf'), 'max': 0, 'avg': 0, 'total': 0}
        }
    }
    
    print(f"🔍 Verifying JSONL format for: {filename}")
    print("=" * 60)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                results['total_lines'] = line_num
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    results['warnings'].append(f"Line {line_num}: Empty line")
                    continue
                
                try:
                    # Parse JSON
                    data = json.loads(line)
                    
                    # Validate structure
                    if not isinstance(data, dict):
                        results['errors'].append(f"Line {line_num}: Entry is not a dictionary")
                        results['invalid_entries'] += 1
                        continue
                    
                    # Check required fields
                    if 'instruction' not in data:
                        results['errors'].append(f"Line {line_num}: Missing 'instruction' field")
                        results['invalid_entries'] += 1
                        continue
                    
                    if 'output' not in data:
                        results['errors'].append(f"Line {line_num}: Missing 'output' field")
                        results['invalid_entries'] += 1
                        continue
                    
                    # Check field types
                    if not isinstance(data['instruction'], str):
                        results['errors'].append(f"Line {line_num}: 'instruction' must be a string")
                        results['invalid_entries'] += 1
                        continue
                    
                    if not isinstance(data['output'], str):
                        results['errors'].append(f"Line {line_num}: 'output' must be a string")
                        results['invalid_entries'] += 1
                        continue
                    
                    # Check for extra fields
                    expected_fields = {'instruction', 'output'}
                    extra_fields = set(data.keys()) - expected_fields
                    if extra_fields:
                        results['warnings'].append(f"Line {line_num}: Extra fields found: {extra_fields}")
                    
                    # Validate content quality
                    instruction = data['instruction'].strip()
                    output = data['output'].strip()
                    
                    if len(instruction) == 0:
                        results['warnings'].append(f"Line {line_num}: Empty instruction")
                    elif len(instruction) < 5:
                        results['warnings'].append(f"Line {line_num}: Very short instruction ({len(instruction)} chars)")
                    
                    if len(output) == 0:
                        results['warnings'].append(f"Line {line_num}: Empty output")
                    elif len(output) < 10:
                        results['warnings'].append(f"Line {line_num}: Very short output ({len(output)} chars)")
                    
                    # Update statistics
                    inst_len = len(instruction)
                    out_len = len(output)
                    
                    results['field_analysis']['instruction_stats']['min'] = min(
                        results['field_analysis']['instruction_stats']['min'], inst_len)
                    results['field_analysis']['instruction_stats']['max'] = max(
                        results['field_analysis']['instruction_stats']['max'], inst_len)
                    results['field_analysis']['instruction_stats']['total'] += inst_len
                    
                    results['field_analysis']['output_stats']['min'] = min(
                        results['field_analysis']['output_stats']['min'], out_len)
                    results['field_analysis']['output_stats']['max'] = max(
                        results['field_analysis']['output_stats']['max'], out_len)
                    results['field_analysis']['output_stats']['total'] += out_len
                    
                    # Store samples
                    if len(results['sample_entries']) < 5:
                        results['sample_entries'].append({
                            'line': line_num,
                            'instruction': instruction[:100] + ('...' if len(instruction) > 100 else ''),
                            'output': output[:100] + ('...' if len(output) > 100 else ''),
                            'inst_len': inst_len,
                            'out_len': out_len
                        })
                    
                    results['valid_entries'] += 1
                    
                except json.JSONDecodeError as e:
                    results['errors'].append(f"Line {line_num}: JSON decode error - {e}")
                    results['invalid_entries'] += 1
                    continue
                
                except Exception as e:
                    results['errors'].append(f"Line {line_num}: Unexpected error - {e}")
                    results['invalid_entries'] += 1
                    continue
    
    except FileNotFoundError:
        results['valid'] = False
        results['errors'].append(f"File not found: {filename}")
        return results
    
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"File reading error: {e}")
        return results
    
    # Calculate averages
    if results['valid_entries'] > 0:
        results['field_analysis']['instruction_stats']['avg'] = (
            results['field_analysis']['instruction_stats']['total'] / results['valid_entries'])
        results['field_analysis']['output_stats']['avg'] = (
            results['field_analysis']['output_stats']['total'] / results['valid_entries'])
    
    # Set overall validity
    results['valid'] = (results['invalid_entries'] == 0 and len(results['errors']) == 0)
    
    return results

def print_verification_results(results: Dict):
    """Print formatted verification results."""
    
    print("\n📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    # Overall status
    status_icon = "✅" if results['valid'] else "❌"
    print(f"{status_icon} Overall Status: {'VALID' if results['valid'] else 'INVALID'}")
    
    # Basic statistics
    print(f"\n📈 Basic Statistics:")
    print(f"  Total lines: {results['total_lines']}")
    print(f"  Valid entries: {results['valid_entries']}")
    print(f"  Invalid entries: {results['invalid_entries']}")
    
    if results['total_lines'] > 0:
        success_rate = (results['valid_entries'] / results['total_lines']) * 100
        print(f"  Success rate: {success_rate:.1f}%")
    
    # Field statistics
    if results['valid_entries'] > 0:
        inst_stats = results['field_analysis']['instruction_stats']
        out_stats = results['field_analysis']['output_stats']
        
        print(f"\n📏 Field Length Statistics:")
        print(f"  Instructions: {inst_stats['min']}-{inst_stats['max']} chars (avg: {inst_stats['avg']:.1f})")
        print(f"  Outputs: {out_stats['min']}-{out_stats['max']} chars (avg: {out_stats['avg']:.1f})")
    
    # Errors
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"  • {error}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more errors")
    
    # Warnings
    if results['warnings']:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results['warnings'][:10]:  # Show first 10 warnings
            print(f"  • {warning}")
        if len(results['warnings']) > 10:
            print(f"  ... and {len(results['warnings']) - 10} more warnings")
    
    # Sample entries
    if results['sample_entries']:
        print(f"\n📋 Sample Entries:")
        for i, sample in enumerate(results['sample_entries']):
            print(f"\n  [{i+1}] Line {sample['line']} ({sample['inst_len']} + {sample['out_len']} chars)")
            print(f"      Q: {sample['instruction']}")
            print(f"      A: {sample['output']}")

def validate_specific_patterns(filename: str):
    """Validate specific JSONL patterns and content quality."""
    
    print(f"\n🔬 DETAILED CONTENT ANALYSIS")
    print("=" * 60)
    
    patterns = {
        'questions': 0,
        'definitions': 0,
        'procedures': 0,
        'duplicates': 0
    }
    
    seen_instructions = set()
    seen_outputs = set()
    duplicate_pairs = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    instruction = data.get('instruction', '').strip().lower()
                    output = data.get('output', '').strip().lower()
                    
                    # Pattern analysis
                    if instruction.startswith('what is') or instruction.startswith('what are'):
                        patterns['definitions'] += 1
                    elif '?' in instruction:
                        patterns['questions'] += 1
                    elif 'how to' in instruction or 'procedure' in instruction:
                        patterns['procedures'] += 1
                    
                    # Duplicate detection
                    inst_key = instruction[:100]
                    out_key = output[:100]
                    
                    if inst_key in seen_instructions:
                        patterns['duplicates'] += 1
                        duplicate_pairs.append(f"Line {line_num}: Duplicate instruction")
                    else:
                        seen_instructions.add(inst_key)
                    
                    if out_key in seen_outputs:
                        patterns['duplicates'] += 1
                        duplicate_pairs.append(f"Line {line_num}: Duplicate output")
                    else:
                        seen_outputs.add(out_key)
                
                except:
                    continue
    
    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        return
    
    print(f"📊 Content Patterns:")
    print(f"  Definitions (What is/are): {patterns['definitions']}")
    print(f"  Questions (contains ?): {patterns['questions']}")
    print(f"  Procedures (How to): {patterns['procedures']}")
    print(f"  Potential duplicates: {patterns['duplicates']}")
    
    if duplicate_pairs:
        print(f"\n⚠️  Potential Duplicates (first 5):")
        for dup in duplicate_pairs[:5]:
            print(f"  • {dup}")

def main():
    filename = "fannie_mae_master_knowledge_base.jsonl"
    
    print("🔍 JSONL FORMAT VERIFICATION")
    print("=" * 60)
    print(f"File: {filename}")
    
    # Run verification
    results = verify_jsonl_format(filename)
    
    # Print results
    print_verification_results(results)
    
    # Additional analysis
    if results['valid_entries'] > 0:
        validate_specific_patterns(filename)
    
    # Final summary
    print(f"\n🎯 FINAL VERDICT")
    print("=" * 60)
    if results['valid']:
        print("✅ File is VALID JSONL format and ready for use!")
        print("✅ All entries have required fields")
        print("✅ JSON syntax is correct")
        if len(results['warnings']) == 0:
            print("✅ No issues found")
        else:
            print(f"⚠️  {len(results['warnings'])} minor warnings (see above)")
    else:
        print("❌ File has ERRORS and needs fixing")
        print(f"❌ {results['invalid_entries']} invalid entries found")
        print("❌ Fix errors before using for training")

if __name__ == "__main__":
    main()