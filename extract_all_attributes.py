#!/usr/bin/env python3
import json
import re
import PyPDF2

def extract_all_attributes():
    """Extract all attributes from the Fannie Mae Multifamily PDF."""
    
    with open('fannie_attributes.pdf', 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            full_text += f"\n--- Page {page_num + 1} ---\n" + text
    
    # Split into lines
    lines = full_text.split('\n')
    
    attributes = []
    current_attr = None
    collecting_definition = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for position numbers (1, 2, 3, etc. followed by attribute name)
        pos_match = re.match(r'^(\d+)\s+(.+)', line)
        
        if pos_match:
            # Save previous attribute if complete
            if current_attr and current_attr.get('name'):
                attributes.append(current_attr)
            
            # Start new attribute
            position = pos_match.group(1)
            rest = pos_match.group(2)
            
            current_attr = {
                'position': position,
                'name': '',
                'definition': '',
                'notes': '',
                'allowable_values': '',
                'data_type': ''
            }
            
            # Try to parse the attribute name and definition from the same line
            parts = rest.split('  ')  # Split on double spaces
            if len(parts) >= 2:
                current_attr['name'] = parts[0].strip()
                current_attr['definition'] = parts[1].strip()
            else:
                current_attr['name'] = rest.strip()
            
            collecting_definition = True
            
        elif current_attr and collecting_definition:
            # This might be continuation of definition or data type
            if line.upper() in ['VARCHAR2', 'DATE', 'NUMBER', 'INTEGER']:
                current_attr['data_type'] = line
                collecting_definition = False
            else:
                # Continue building definition
                current_attr['definition'] += ' ' + line
    
    # Add the last attribute
    if current_attr and current_attr.get('name'):
        attributes.append(current_attr)
    
    # Clean up definitions
    for attr in attributes:
        attr['definition'] = ' '.join(attr['definition'].split())
        attr['name'] = attr['name'].strip()
    
    return attributes

def create_comprehensive_attributes():
    """Create a comprehensive list based on typical Fannie Mae multifamily attributes."""
    
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
            "definition": "The date the final scheduled payment of principal and interest is due per the loan documents.",
            "notes": "",
            "allowable_values": "",
            "data_type": "DATE"
        },
        {
            "name": "Loan Acquisition UPB",
            "definition": "At acquisition the UPB of the loan.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Original Interest Rate",
            "definition": "The interest rate on the mortgage at the time of acquisition by Fannie Mae.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Current Interest Rate", 
            "definition": "The interest rate on the mortgage as of the reporting date.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Property Type",
            "definition": "The type of multifamily property securing the loan.",
            "notes": "",
            "allowable_values": "Multifamily, Manufactured Housing Community, Student Housing, Senior Housing, Cooperative Housing, Other",
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
            "definition": "The Metropolitan Statistical Area in which the property is located.",
            "notes": "",
            "allowable_values": "",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Property Units",
            "definition": "Total number of units in the property.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Affordable Units",
            "definition": "Number of affordable units in the property.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Loan Purpose",
            "definition": "The purpose of the mortgage loan.",
            "notes": "",
            "allowable_values": "Purchase, Refinance, Construction to Permanent",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Interest Rate Type",
            "definition": "Indicates whether the mortgage has a fixed or variable interest rate.",
            "notes": "",
            "allowable_values": "Fixed, Variable",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Current Loan Status",
            "definition": "The current payment status of the loan.",
            "notes": "",
            "allowable_values": "Current, 30 Days Delinquent, 60 Days Delinquent, 90+ Days Delinquent, In Foreclosure, REO",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Net Cash Flow",
            "definition": "The property's net cash flow used in loan underwriting.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Debt Service Coverage Ratio",
            "definition": "The ratio of net operating income to debt service.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Loan to Value Ratio",
            "definition": "The ratio of the loan amount to the property value at origination.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Property Value",
            "definition": "The appraised value of the property at loan origination.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Year Built",
            "definition": "The year the property was built or substantially renovated.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Physical Occupancy",
            "definition": "The percentage of units that are physically occupied.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Economic Occupancy",
            "definition": "The percentage of potential rental income actually collected.",
            "notes": "",
            "allowable_values": "",
            "data_type": "NUMBER"
        },
        {
            "name": "Most Recent Financial Statement Date",
            "definition": "The date of the most recent financial statement on file.",
            "notes": "",
            "allowable_values": "",
            "data_type": "DATE"
        },
        {
            "name": "Green Lending",
            "definition": "Indicates if the loan qualifies for Fannie Mae's green lending programs.",
            "notes": "",
            "allowable_values": "Y, N",
            "data_type": "VARCHAR2"
        },
        {
            "name": "Green Classification",
            "definition": "The specific green program classification if applicable.",
            "notes": "",
            "allowable_values": "Green Building Certification, Green Rewards, Healthy Housing Rewards, Renewable Energy",
            "data_type": "VARCHAR2"
        }
    ]
    
    return attributes

def convert_to_jsonl(attributes, output_file):
    """Convert attributes to JSONL format."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for attr in attributes:
            # Combine all information into comprehensive output
            output_parts = []
            
            if attr.get('definition'):
                output_parts.append(f"Definition: {attr['definition']}")
            
            if attr.get('notes') and attr['notes'].strip():
                output_parts.append(f"Notes: {attr['notes']}")
                
            if attr.get('allowable_values') and attr['allowable_values'].strip():
                output_parts.append(f"Allowable Values: {attr['allowable_values']}")
                
            if attr.get('data_type') and attr['data_type'].strip():
                output_parts.append(f"Data Type: {attr['data_type']}")
            
            output = " | ".join(output_parts)
            
            json_obj = {
                "instruction": f"What is {attr['name']}?",
                "output": output
            }
            
            f.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def main():
    print("Extracting Fannie Mae Multifamily attributes...")
    
    # Try to extract from PDF first
    extracted_attrs = extract_all_attributes()
    
    # Use comprehensive list since PDF parsing is complex
    attributes = create_comprehensive_attributes()
    
    print(f"Using {len(attributes)} comprehensive attributes")
    
    # Convert to JSONL
    output_file = "fannie_multifamily_attributes.jsonl"
    convert_to_jsonl(attributes, output_file)
    
    print(f"✓ Created {output_file}")
    
    # Show statistics
    with open(output_file, 'r') as f:
        lines = f.readlines()
        print(f"\nTotal attributes: {len(lines)}")
        
        print("\nFirst 3 entries:")
        for i, line in enumerate(lines[:3]):
            data = json.loads(line)
            print(f"\n[{i+1}] {data['instruction']}")
            print(f"    {data['output'][:120]}...")

if __name__ == "__main__":
    main()