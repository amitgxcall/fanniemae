#!/usr/bin/env python3
import json
from typing import List, Dict

def convert_instruction_output_to_dialog(input_file: str, output_file: str, format_type: str = "llama") -> int:
    """
    Convert instruction-output JSONL to dialog format for LLaMA fine-tuning.
    
    Args:
        input_file: Input JSONL with instruction/output format
        output_file: Output JSONL with dialog format
        format_type: Type of dialog format ('llama', 'alpaca', 'vicuna', or 'custom')
    
    Returns:
        Number of converted entries
    """
    
    converted_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                
                # Validate input format
                if 'instruction' not in data or 'output' not in data:
                    print(f"Warning: Line {line_num} missing required fields")
                    continue
                
                instruction = data['instruction']
                output = data['output']
                
                # Convert to different dialog formats
                if format_type == "llama":
                    # LLaMA format: dialog with role-based conversation
                    converted_entry = {
                        "dialog": [
                            {"role": "user", "content": instruction},
                            {"role": "assistant", "content": output}
                        ]
                    }
                
                elif format_type == "alpaca":
                    # Alpaca format: instruction, input (optional), output
                    converted_entry = {
                        "instruction": instruction,
                        "input": "",
                        "output": output
                    }
                
                elif format_type == "vicuna":
                    # Vicuna conversation format
                    converted_entry = {
                        "conversations": [
                            {"from": "human", "value": instruction},
                            {"from": "gpt", "value": output}
                        ]
                    }
                
                elif format_type == "sharegpt":
                    # ShareGPT format
                    converted_entry = {
                        "conversations": [
                            {"from": "human", "value": instruction},
                            {"from": "gpt", "value": output}
                        ]
                    }
                
                elif format_type == "chat":
                    # Simple chat format
                    converted_entry = {
                        "messages": [
                            {"role": "user", "content": instruction},
                            {"role": "assistant", "content": output}
                        ]
                    }
                
                elif format_type == "dialog_simple":
                    # Simple dialog format
                    converted_entry = {
                        "dialog": f"User: {instruction}\nAssistant: {output}"
                    }
                
                else:  # custom format
                    converted_entry = {
                        "dialog": [
                            {"speaker": "user", "text": instruction},
                            {"speaker": "assistant", "text": output}
                        ]
                    }
                
                # Write converted entry
                outfile.write(json.dumps(converted_entry, ensure_ascii=False) + '\n')
                converted_count += 1
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"Error converting line {line_num}: {e}")
                continue
    
    return converted_count

def show_format_examples():
    """Show examples of different dialog formats."""
    
    sample_instruction = "What is a conventional loan?"
    sample_output = "A mortgage loan not insured or guaranteed by the federal government."
    
    formats = {
        "llama": {
            "dialog": [
                {"role": "user", "content": sample_instruction},
                {"role": "assistant", "content": sample_output}
            ]
        },
        "alpaca": {
            "instruction": sample_instruction,
            "input": "",
            "output": sample_output
        },
        "vicuna": {
            "conversations": [
                {"from": "human", "value": sample_instruction},
                {"from": "gpt", "value": sample_output}
            ]
        },
        "chat": {
            "messages": [
                {"role": "user", "content": sample_instruction},
                {"role": "assistant", "content": sample_output}
            ]
        },
        "dialog_simple": {
            "dialog": f"User: {sample_instruction}\nAssistant: {sample_output}"
        }
    }
    
    print("📋 AVAILABLE DIALOG FORMATS:")
    print("=" * 60)
    
    for format_name, example in formats.items():
        print(f"\n🔹 {format_name.upper()} FORMAT:")
        print(json.dumps(example, indent=2, ensure_ascii=False))

def main():
    print("🔄 JSONL FORMAT CONVERTER")
    print("=" * 60)
    print("Convert instruction-output format to dialog format for fine-tuning")
    
    # Show available formats
    show_format_examples()
    
    # Default conversion to LLaMA format
    input_file = "fannie_mae_master_knowledge_base.jsonl"
    
    # Create multiple formats
    formats_to_create = [
        ("llama", "fannie_mae_llama_dialog.jsonl"),
        ("alpaca", "fannie_mae_alpaca_format.jsonl"),
        ("vicuna", "fannie_mae_vicuna_format.jsonl"),
        ("chat", "fannie_mae_chat_format.jsonl"),
        ("dialog_simple", "fannie_mae_simple_dialog.jsonl")
    ]
    
    print(f"\n🔄 CONVERTING: {input_file}")
    print("=" * 60)
    
    for format_type, output_file in formats_to_create:
        try:
            count = convert_instruction_output_to_dialog(input_file, output_file, format_type)
            print(f"✅ {format_type.upper()}: {count} entries → {output_file}")
        except Exception as e:
            print(f"❌ {format_type.upper()}: Error - {e}")
    
    # Show samples of converted files
    print(f"\n📋 SAMPLE CONVERSIONS:")
    print("=" * 60)
    
    for format_type, output_file in formats_to_create[:2]:  # Show first 2 formats
        try:
            print(f"\n🔹 {format_type.upper()} FORMAT SAMPLE:")
            with open(output_file, 'r') as f:
                sample = json.loads(f.readline())
                print(json.dumps(sample, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error reading {output_file}: {e}")

if __name__ == "__main__":
    main()