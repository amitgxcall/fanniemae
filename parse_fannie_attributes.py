#!/usr/bin/env python3
import json
import re
import PyPDF2
import sys

def extract_attributes_table(pdf_path):
    """Extract attribute definitions from Fannie Mae PDF table format."""
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        # Extract all text
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
    
    # Clean up text
    text = re.sub(r'\s+', ' ', full_text)
    
    # Find the main table section
    # Look for patterns like "Position Attribute Name Definition Notes Allowable Values Data Type"
    table_start = text.find("Position")
    if table_start == -1:
        table_start = text.find("Attribute Name")
    
    if table_start == -1:
        print("Could not find table start")
        return []
    
    table_text = text[table_start:]
    
    # Split into lines and process
    lines = table_text.split('\n')
    
    attributes = []
    current_attr = {}
    
    # Look for numbered entries (position numbers)
    position_pattern = r'^\d+\s+'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a position number
        if re.match(position_pattern, line):
            # Save previous attribute if exists
            if current_attr.get('name'):
                attributes.append(current_attr)
                current_attr = {}
            
            # Parse this line
            parts = re.split(r'\s{2,}', line)  # Split on multiple spaces
            if len(parts) >= 2:
                # Remove position number
                attr_name = re.sub(position_pattern, '', parts[0]).strip()
                current_attr['name'] = attr_name
                current_attr['definition'] = parts[1] if len(parts) > 1 else ""
                current_attr['notes'] = parts[2] if len(parts) > 2 else ""
                current_attr['allowable_values'] = parts[3] if len(parts) > 3 else ""
                current_attr['data_type'] = parts[4] if len(parts) > 4 else ""
    
    # Add the last attribute
    if current_attr.get('name'):
        attributes.append(current_attr)
    
    return attributes

def manual_extract_attributes():
    """Manually extracted attributes from the PDF based on the visible structure."""
    attributes = [
        {
            "name": "Loan Number",
            "definition": "A unique number assigned to each mortgage loan by Fannie Mae.",
            "notes": "",
            "allowable_values": "",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Acquisition Date", 
            "definition": "The date on which Fannie Mae acquired the loan. Some loans acquired prior to 2008 may have Acquisition Date before the Note Date.",
            "notes": "",
            "allowable_values": "",
            "data_type": "DATE"
        },
        {
            "name": "Note Date",
            "definition": "The date on which the mortgage note or deed of trust is executed.",
            "notes": "",
            "allowable_values": "",
            "data_type": "DATE"
        },
        {
            "name": "Maturity Date at Acquisition",
            "definition": "The date the final scheduled payment of principal and interest is due on the mortgage.",
            "notes": "",
            "allowable_values": "",
            "data_type": "DATE"
        },
        {
            "name": "Original Loan Amount",
            "definition": "The original principal balance of the mortgage at the time of acquisition by Fannie Mae.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Current Loan Amount",
            "definition": "The outstanding principal balance of the mortgage as of the reporting date.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Original Interest Rate",
            "definition": "The initial interest rate on the mortgage at the time of acquisition.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Current Interest Rate", 
            "definition": "The current interest rate on the mortgage as of the reporting date.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Property Type",
            "definition": "The type of multifamily property securing the loan.",
            "notes": "",
            "allowable_values": "Multifamily, Manufactured Housing Community, Student Housing, Senior Housing, Healthcare, Other",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Property State",
            "definition": "The state in which the property is located.",
            "notes": "",
            "allowable_values": "Two-letter state abbreviations",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Metro Area",
            "definition": "The Metropolitan Statistical Area (MSA) in which the property is located.",
            "notes": "",
            "allowable_values": "",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Units",
            "definition": "The total number of rental units in the property.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        }
    ]
    
    return attributes

def convert_to_jsonl(attributes, output_file):
    """Convert attributes to JSONL format with instruction-output pairs."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for attr in attributes:
            # Combine all information into output
            output_parts = []
            
            if attr['definition']:
                output_parts.append(f"Definition: {attr['definition']}")
            
            if attr['notes']:
                output_parts.append(f"Notes: {attr['notes']}")
                
            if attr['allowable_values']:
                output_parts.append(f"Allowable Values: {attr['allowable_values']}")
                
            if attr['data_type']:
                output_parts.append(f"Data Type: {attr['data_type']}")
            
            output = " | ".join(output_parts)
            
            json_obj = {
                "instruction": f"What is {attr['name']}?",
                "output": output
            }
            
            f.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def main():
    pdf_path = "fannie_attributes.pdf"
    output_path = "fannie_attributes.jsonl"
    
    print("Extracting attributes from Fannie Mae PDF...")
    
    # Try automatic extraction first
    attributes = extract_attributes_table(pdf_path)
    
    # If automatic fails, use manual extraction
    if len(attributes) < 5:
        print("Using manual extraction fallback...")
        attributes = manual_extract_attributes()
    
    print(f"Found {len(attributes)} attributes")
    
    # Convert to JSONL
    convert_to_jsonl(attributes, output_path)
    
    print(f"Created {output_path}")
    
    # Show samples
    print("\nFirst 3 entries:")
    with open(output_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            data = json.loads(line)
            print(f"\n[{i+1}]")
            print(f"Q: {data['instruction']}")
            print(f"A: {data['output'][:150]}...")

if __name__ == "__main__":
    main()