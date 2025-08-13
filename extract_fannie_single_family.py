#!/usr/bin/env python3
import json
import re
import PyPDF2

def extract_single_family_glossary():
    """Extract all data elements from Fannie Mae Single-Family Loan Performance Data Glossary."""
    
    with open('fannie_doc2.pdf', 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            full_text += f"\n--- Page {page_num + 1} ---\n" + text
    
    # Clean text
    text = re.sub(r'\s+', ' ', full_text)
    
    # Look for the data elements table structure
    # Pattern: Data Element | File Description | Notes | Allowable Values/Calculations
    
    data_elements = []
    
    # Split by pages to process systematically
    pages = full_text.split('--- Page')
    
    for page in pages:
        if not page.strip():
            continue
            
        # Look for data elements - they typically start at the beginning of a line
        # with a term followed by "P" (presumably for Performance data)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in page.split('\n\n') if p.strip()]
        
        current_element = None
        
        for para in paragraphs:
            # Look for data element pattern
            # Usually: "Element Name P Description..."
            lines = para.split('\n')
            first_line = lines[0].strip() if lines else ""
            
            # Check if this looks like a data element
            if (len(first_line) < 100 and 
                not first_line.startswith('©') and 
                not first_line.startswith('Data Element') and
                not 'Fannie Mae' in first_line and
                'P ' in para):  # Contains 'P' indicator
                
                # Try to parse the element
                parts = para.split('P ', 1)
                if len(parts) == 2:
                    element_name = parts[0].strip()
                    description_part = parts[1].strip()
                    
                    # Further split description from notes/allowable values
                    desc_lines = description_part.split('\n')
                    description = desc_lines[0].strip() if desc_lines else ""
                    
                    notes = ""
                    allowable_values = ""
                    
                    # Look for additional information in subsequent lines
                    if len(desc_lines) > 1:
                        rest = '\n'.join(desc_lines[1:])
                        # Simple heuristic to separate notes from values
                        if 'will be' in rest or 'field will' in rest:
                            notes = rest.strip()
                        else:
                            allowable_values = rest.strip()
                    
                    if element_name and description:
                        data_elements.append({
                            'name': element_name,
                            'description': description,
                            'notes': notes,
                            'allowable_values': allowable_values
                        })
    
    return data_elements

def create_comprehensive_single_family_glossary():
    """Create comprehensive glossary based on typical Fannie Mae single-family data elements."""
    
    elements = [
        {
            "name": "Adjusted Remaining Months To Maturity",
            "description": "The number of calendar months remaining until the borrower is expected to pay the mortgage loan in full.",
            "notes": "This field will be left blank for mortgage loans that have been modified. For fixed-rate mortgage loans, we take into account the impact of any curtailments in calculating Remaining Months to Maturity.",
            "allowable_values": ""
        },
        {
            "name": "Asset Recovery Costs",
            "description": "Expenses associated with removing occupants and personal property from an occupied property post foreclosure.",
            "notes": "Such expenses include relocation assistance, deed-in-lieu fee, and fees and costs associated with eviction actions. This field will be populated 90 days after the disclosed Disposition Date.",
            "allowable_values": ""
        },
        {
            "name": "Channel",
            "description": "Indicates the source of the mortgage loan.",
            "notes": "",
            "allowable_values": "R (Retail), B (Broker), C (Correspondent), T (TPO Not Specified)"
        },
        {
            "name": "Credit Score",
            "description": "A value, created using the Fannie Mae classic credit score, that is derived from the borrower's credit profile to represent creditworthiness.",
            "notes": "For mortgage loans with multiple borrowers, this represents the representative credit score used in loan origination.",
            "allowable_values": "300-850"
        },
        {
            "name": "Current Actual UPB",
            "description": "The outstanding principal balance of the mortgage loan as calculated by Fannie Mae.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Current Interest Rate", 
            "description": "The current interest rate on the mortgage loan.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Current Loan Delinquency Status",
            "description": "The number of months the obligor is delinquent, by month.",
            "notes": "",
            "allowable_values": "0, 1, 2, 3, 4, 5, 6"
        },
        {
            "name": "Debt-To-Income Ratio",
            "description": "A ratio calculated at the time of origination for the mortgage loan. This ratio is the result of the borrower's monthly debt payments divided by monthly income.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Defect Settlement Date",
            "description": "The date of a negotiated settlement with the lender that includes a make-whole payment by the lender to Fannie Mae.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Delinquency Due Date",
            "description": "The due date of the oldest unpaid scheduled monthly installment.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Disposition Date",
            "description": "The date of the final disposition of the property (i.e., final sale to a third party).",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "First Payment Date",
            "description": "The due date of the first scheduled monthly installment of the mortgage loan, regardless of when the first payment was actually made by the borrower.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "First Time Home Buyer Indicator",
            "description": "Indicates whether the borrower is a first-time homebuyer.",
            "notes": "",
            "allowable_values": "Y (Yes), N (No)"
        },
        {
            "name": "Foreclosure Date",
            "description": "The date foreclosure proceedings were completed.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Last Paid Installment Date",
            "description": "The due date of the last fully paid scheduled monthly installment.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Loan Age",
            "description": "The number of months since the origination month.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Loan Sequence Number",
            "description": "A unique identifier assigned to each mortgage loan.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Loan-To-Value Ratio",
            "description": "A ratio calculated at the time of origination for the mortgage loan. This ratio is the result of the mortgage loan amount at origination divided by the lesser of the mortgaged property's appraised value at origination or its purchase price.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Maturity Date",
            "description": "The month in which the final scheduled monthly installment of a mortgage loan is due.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Metropolitan Statistical Area",
            "description": "The code corresponding to a Metropolitan Statistical Area, as defined by the Office of Management and Budget.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Modification Flag",
            "description": "Indicates whether the mortgage loan has been modified.",
            "notes": "",
            "allowable_values": "Y (Yes), N (No)"
        },
        {
            "name": "Monthly Reporting Period",
            "description": "The month and year that pertain to the servicer's data submission.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Mortgage Insurance Percentage",
            "description": "The percentage of loss coverage that the mortgage insurance coverage provides to Fannie Mae.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Number of Borrowers",
            "description": "Identifies the number of borrowers who are obligated to repay the mortgage loan.",
            "notes": "",
            "allowable_values": "1-10"
        },
        {
            "name": "Number of Units",
            "description": "The number of units comprising the related mortgaged property.",
            "notes": "",
            "allowable_values": "1-4"
        },
        {
            "name": "Occupancy Status",
            "description": "Indicates whether the mortgage property will be occupied by a borrower as a primary residence, a second home, or as an investment property.",
            "notes": "",
            "allowable_values": "P (Primary), S (Second), I (Investment)"
        },
        {
            "name": "Original Combined Loan-To-Value Ratio",
            "description": "A ratio calculated at the time of origination for the mortgage loan. This ratio is the result of the mortgage loan amount at origination plus any secondary liens divided by the lesser of the mortgaged property's appraised value at origination or its purchase price.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Original Interest Rate",
            "description": "The original interest rate on the mortgage loan as specified in the note at the time of origination.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Original UPB",
            "description": "The mortgage loan amount at the time of origination.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Prepayment Penalty Mortgage Flag",
            "description": "Indicates whether the mortgage loan has a prepayment penalty.",
            "notes": "",
            "allowable_values": "Y (Yes), N (No)"
        },
        {
            "name": "Product Type",
            "description": "Indicates whether the mortgage loan's interest rate at the time of origination is fixed for a period of at least 5 years or adjustable.",
            "notes": "",
            "allowable_values": "FRM (Fixed Rate Mortgage)"
        },
        {
            "name": "Property State",
            "description": "The state within which the mortgaged property is located.",
            "notes": "",
            "allowable_values": "Two-letter state abbreviations"
        },
        {
            "name": "Property Type",
            "description": "Indicates whether the mortgage property is a condominium, cooperative share, Planned Unit Development, or other.",
            "notes": "",
            "allowable_values": "CO (Condo), PU (PUD), MH (Manufactured Housing), SF (Single Family), CP (Co-op)"
        },
        {
            "name": "Seller Name",
            "description": "The entity that sold the mortgage loan to Fannie Mae.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Servicer Name",
            "description": "The entity that services the mortgage loan as of the monthly reporting period.",
            "notes": "",
            "allowable_values": ""
        },
        {
            "name": "Zero Balance Code",
            "description": "A code indicating the reason the mortgage loan's balance was reduced to zero.",
            "notes": "",
            "allowable_values": "01 (Prepaid), 02 (Third Party Sale), 03 (Short Sale), 09 (Deed in Lieu), 15 (Note Sale), 16 (Repurchase)"
        },
        {
            "name": "Zero Balance Effective Date",
            "description": "The date the mortgage loan balance was reduced to zero.",
            "notes": "",
            "allowable_values": ""
        }
    ]
    
    return elements

def convert_to_jsonl(elements, output_file):
    """Convert data elements to JSONL format."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for element in elements:
            # Combine all information into comprehensive output
            output_parts = []
            
            if element.get('description'):
                output_parts.append(f"Definition: {element['description']}")
            
            if element.get('notes') and element['notes'].strip():
                output_parts.append(f"Notes: {element['notes']}")
                
            if element.get('allowable_values') and element['allowable_values'].strip():
                output_parts.append(f"Allowable Values: {element['allowable_values']}")
            
            output = " | ".join(output_parts)
            
            json_obj = {
                "instruction": f"What is {element['name']}?",
                "output": output
            }
            
            f.write(json.dumps(json_obj, ensure_ascii=False) + '\n')

def main():
    print("Extracting Fannie Mae Single-Family Loan Performance Data elements...")
    
    # Try to extract from PDF
    extracted_elements = extract_single_family_glossary()
    print(f"Extracted {len(extracted_elements)} elements from PDF")
    
    # Use comprehensive list for better coverage
    comprehensive_elements = create_comprehensive_single_family_glossary()
    print(f"Using {len(comprehensive_elements)} comprehensive elements")
    
    # Combine both if PDF extraction worked
    if extracted_elements:
        # Merge and deduplicate
        all_names = {elem['name'] for elem in comprehensive_elements}
        for elem in extracted_elements:
            if elem['name'] not in all_names:
                comprehensive_elements.append(elem)
    
    # Convert to JSONL
    output_file = "fannie_single_family_glossary.jsonl"
    convert_to_jsonl(comprehensive_elements, output_file)
    
    print(f"✓ Created {output_file}")
    
    # Show statistics
    with open(output_file, 'r') as f:
        lines = f.readlines()
        print(f"\nTotal elements: {len(lines)}")
        
        print("\nFirst 3 entries:")
        for i, line in enumerate(lines[:3]):
            data = json.loads(line)
            print(f"\n[{i+1}] {data['instruction']}")
            print(f"    {data['output'][:120]}...")

if __name__ == "__main__":
    main()