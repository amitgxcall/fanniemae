#!/usr/bin/env python3
import json
from typing import List, Dict

def convert_to_instruction_context_response(input_file: str, output_file: str) -> int:
    """
    Convert instruction-output JSONL to instruction-context-response format.
    
    Args:
        input_file: Input JSONL with instruction/output format
        output_file: Output JSONL with instruction/context/response format
    
    Returns:
        Number of converted entries
    """
    
    converted_count = 0
    
    print(f"🔄 Converting {input_file} to instruction-context-response format...")
    print("=" * 60)
    
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
                
                original_instruction = data['instruction']
                original_output = data['output']
                
                # Create instruction-context-response format
                # Context will be "Fannie Mae mortgage lending knowledge base"
                # since all entries are from Fannie Mae domain
                converted_entry = {
                    "instruction": original_instruction,
                    "context": "Fannie Mae mortgage lending and housing finance knowledge base",
                    "response": original_output
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

def convert_with_dynamic_context(input_file: str, output_file: str) -> int:
    """
    Convert with more specific context based on the content type.
    
    Args:
        input_file: Input JSONL with instruction/output format
        output_file: Output JSONL with instruction/context/response format
    
    Returns:
        Number of converted entries
    """
    
    converted_count = 0
    
    print(f"🔄 Converting {input_file} with dynamic context...")
    print("=" * 60)
    
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
                
                # Determine context based on content
                context = determine_context(instruction, output)
                
                # Create instruction-context-response format
                converted_entry = {
                    "instruction": instruction,
                    "context": context,
                    "response": output
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

def determine_context(instruction: str, output: str) -> str:
    """Determine appropriate context based on instruction and output content."""
    
    instruction_lower = instruction.lower()
    output_lower = output.lower()
    
    # Multifamily-related context
    if any(term in instruction_lower or term in output_lower for term in 
           ['multifamily', 'apartment', 'rental', 'dus', 'affordable housing']):
        return "Fannie Mae multifamily lending and apartment financing"
    
    # Single-family mortgage context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['mortgage', 'homeready', 'desktop underwriter', 'du', 'loan']):
        return "Fannie Mae single-family mortgage lending and homeownership"
    
    # Technology/systems context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['desktop underwriter', 'technology', 'system', 'automated']):
        return "Fannie Mae technology solutions and automated systems"
    
    # Consumer/homebuyer context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['homebuyer', 'consumer', 'calculator', 'education', 'counselor']):
        return "Fannie Mae consumer resources and homebuyer education"
    
    # Capital markets context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['mbs', 'securities', 'credit risk transfer', 'crt', 'investor']):
        return "Fannie Mae capital markets and mortgage-backed securities"
    
    # Company/business context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['fannie mae', 'company', 'mission', 'business', 'fhfa']):
        return "Fannie Mae company information and business operations"
    
    # Regulatory/compliance context
    elif any(term in instruction_lower or term in output_lower for term in 
             ['regulation', 'compliance', 'requirement', 'guideline', 'policy']):
        return "Fannie Mae regulatory requirements and compliance guidelines"
    
    # Default context
    else:
        return "Fannie Mae mortgage lending and housing finance knowledge base"

def show_format_example():
    """Show example of the instruction-context-response format."""
    
    example = {
        "instruction": "What is HomeReady?",
        "context": "Fannie Mae single-family mortgage lending and homeownership",
        "response": "HomeReady is Fannie Mae's affordable lending solution designed to help creditworthy low- to moderate-income borrowers buy or refinance a home. It offers flexible sources for down payment and closing costs, reduced mortgage insurance costs, and allows for non-traditional credit sources."
    }
    
    print("📋 INSTRUCTION-CONTEXT-RESPONSE FORMAT EXAMPLE:")
    print("=" * 60)
    print(json.dumps(example, indent=2, ensure_ascii=False))

def main():
    print("🔄 JSONL FORMAT CONVERTER")
    print("Converting to instruction-context-response format")
    print("=" * 60)
    
    # Show format example
    show_format_example()
    
    input_file = "fannie_mae_master_knowledge_base.jsonl"
    
    # Create two versions
    conversions = [
        {
            "type": "simple",
            "output_file": "fannie_mae_instruction_context_response.jsonl",
            "description": "Simple context (generic Fannie Mae knowledge base)"
        },
        {
            "type": "dynamic", 
            "output_file": "fannie_mae_instruction_context_response_dynamic.jsonl",
            "description": "Dynamic context (specific to content type)"
        }
    ]
    
    print(f"\n🔄 CONVERTING: {input_file}")
    print("=" * 60)
    
    for conversion in conversions:
        try:
            if conversion["type"] == "simple":
                count = convert_to_instruction_context_response(
                    input_file, conversion["output_file"]
                )
            else:
                count = convert_with_dynamic_context(
                    input_file, conversion["output_file"]
                )
            
            print(f"✅ {conversion['type'].upper()}: {count} entries → {conversion['output_file']}")
            print(f"   {conversion['description']}")
            
        except Exception as e:
            print(f"❌ {conversion['type'].upper()}: Error - {e}")
    
    # Show samples of converted files
    print(f"\n📋 SAMPLE CONVERSIONS:")
    print("=" * 60)
    
    for conversion in conversions:
        try:
            print(f"\n🔹 {conversion['type'].upper()} FORMAT SAMPLE:")
            with open(conversion['output_file'], 'r') as f:
                sample = json.loads(f.readline())
                print(json.dumps(sample, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error reading {conversion['output_file']}: {e}")
    
    # Validation
    print(f"\n✅ VALIDATION:")
    print("=" * 60)
    
    for conversion in conversions:
        try:
            with open(conversion['output_file'], 'r') as f:
                line_count = 0
                valid_count = 0
                
                for line in f:
                    line_count += 1
                    try:
                        data = json.loads(line.strip())
                        if all(key in data for key in ['instruction', 'context', 'response']):
                            valid_count += 1
                    except:
                        continue
                
                print(f"📊 {conversion['output_file']}: {valid_count}/{line_count} valid entries")
                
        except Exception as e:
            print(f"Error validating {conversion['output_file']}: {e}")

if __name__ == "__main__":
    main()