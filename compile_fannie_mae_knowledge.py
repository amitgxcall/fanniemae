#!/usr/bin/env python3
import json
from typing import List, Dict

def create_comprehensive_fannie_mae_knowledge_base() -> List[Dict[str, str]]:
    """Compile comprehensive Fannie Mae knowledge base from all extracted content."""
    
    knowledge_base = []
    
    # Company Information (Updated from About Us)
    company_info = [
        {
            "instruction": "What is Fannie Mae's founding history?",
            "output": "Fannie Mae was founded nearly 90 years ago (circa 1935) and created by Congress to provide reliable, affordable mortgage credit nationwide. It plays an essential role in U.S. economic stability, with the housing market representing 15-18% of U.S. GDP."
        },
        {
            "instruction": "What is Fannie Mae's current financial scale?",
            "output": "As of the first half of 2025, Fannie Mae provided $178 billion in funding to the U.S. housing market, assisted 668,000 households, and has total assets of $4.3 trillion."
        },
        {
            "instruction": "How does Fannie Mae's business model work?",
            "output": "Fannie Mae purchases mortgages from lenders, bundles them into mortgage-backed securities, and sells securities to investors. This enables a continuous lending cycle that provides liquidity to the mortgage market."
        },
        {
            "instruction": "What key innovations has Fannie Mae created?",
            "output": "Fannie Mae's key innovations include standardizing the 30-year fixed-rate mortgage, creating the HomeReady mortgage program allowing 3% down payments, developing technology to simplify the mortgage process, and creating tools to reach more creditworthy borrowers."
        }
    ]
    knowledge_base.extend(company_info)
    
    # Careers and Workplace
    careers_info = [
        {
            "instruction": "What career opportunities does Fannie Mae offer?",
            "output": "Fannie Mae offers roles across Corporate Teams, Data & Analytics, Digital & Technology, Mortgage & Customer Solutions, and Risk Management. The company helps expand access to affordable housing across the country."
        },
        {
            "instruction": "What workplace recognitions has Fannie Mae received?",
            "output": "Fannie Mae has been recognized as Glassdoor Best Places to Work (#36 large company), Great Place to Work Certified, Washington Post Top Workplaces (#1 Largest Companies), and ranked #34 in Vault Top 100 Internships."
        },
        {
            "instruction": "What benefits does Fannie Mae provide employees?",
            "output": "Fannie Mae provides comprehensive benefits packages, professional development opportunities, internship and early career programs, and is committed to being an equal opportunity employer with reasonable accommodations."
        }
    ]
    knowledge_base.extend(careers_info)
    
    # Research and Market Insights
    research_info = [
        {
            "instruction": "What research does Fannie Mae publish regularly?",
            "output": "Fannie Mae publishes the monthly National Housing Survey with the Home Purchase Sentiment Index (HPSI), Economic & Housing Outlook reports, and maintains the Home Price Index. The Economic & Strategic Research (ESR) Group conducts comprehensive housing market analysis."
        },
        {
            "instruction": "What are Fannie Mae's current mortgage rate forecasts?",
            "output": "According to the July 24, 2025 Economic & Housing Outlook, Fannie Mae forecasts mortgage rates of 6.4% by end of 2025 and 6.0% by end of 2026, representing downward revisions from previous projections."
        },
        {
            "instruction": "What are current home price trends according to Fannie Mae?",
            "output": "Single-family home prices increased 4.1% from Q2 2024 to Q2 2025, showing slower growth compared to the previous quarter's 5.0% year-over-year pace, indicating a moderating price growth trend."
        },
        {
            "instruction": "What emerging research areas is Fannie Mae exploring?",
            "output": "Fannie Mae is exploring variable and gig income's potential to expand homeownership access, analyzing consumer attitudes toward new housing development, and examining advanced risk management strategies in mortgage lending."
        }
    ]
    knowledge_base.extend(research_info)
    
    # Single-Family Business (Detailed)
    single_family_detailed = [
        {
            "instruction": "What is RefiNow?",
            "output": "RefiNow is Fannie Mae's refinance option with expanded eligibility designed to help borrowers refinance to lower interest rates, particularly targeting borrowers who may not qualify for traditional refinance programs."
        },
        {
            "instruction": "What is HomeReady mortgage?",
            "output": "HomeReady is Fannie Mae's low down payment mortgage allowing 3% down payment with flexible income options. It's designed for creditworthy low- to moderate-income borrowers and includes reduced mortgage insurance costs and acceptance of non-traditional credit sources."
        },
        {
            "instruction": "What is HomeStyle Renovation financing?",
            "output": "HomeStyle Renovation is Fannie Mae's financing solution that allows borrowers to include home improvement costs in their mortgage, enabling them to purchase or refinance a home and finance renovation costs with a single loan."
        },
        {
            "instruction": "What is MH Advantage?",
            "output": "MH Advantage provides affordable manufactured home financing with conventional loan benefits for eligible manufactured homes that meet specific construction and site requirements, offering better terms than traditional manufactured home loans."
        },
        {
            "instruction": "What is HomeStyle Energy?",
            "output": "HomeStyle Energy is a mortgage product that allows borrowers to finance energy-efficient improvements and utility-reducing home upgrades as part of their mortgage, supporting both environmental goals and long-term cost savings."
        },
        {
            "instruction": "What technology solutions does Fannie Mae provide to lenders?",
            "output": "Fannie Mae provides Desktop Underwriter (DU) for automated underwriting, Servicing Marketplace to connect lenders and servicing buyers, Fannie Mae Connect for data and analytics, Income Calculator, and Closing Costs Calculator."
        },
        {
            "instruction": "What is the Appraiser Development Initiative?",
            "output": "The Appraiser Development Initiative, launched in 2018, is Fannie Mae's program to address appraiser shortages and diversity in the appraisal industry by supporting appraiser education, training, and career development."
        }
    ]
    knowledge_base.extend(single_family_detailed)
    
    # Multifamily Business (Detailed)
    multifamily_detailed = [
        {
            "instruction": "What is Fannie Mae's market position in multifamily lending?",
            "output": "Fannie Mae is the largest guarantor of multifamily mortgages in the U.S., backing approximately 20% of multifamily loans with a book of business exceeding $500 billion, serving diverse markets from conventional to specialty projects."
        },
        {
            "instruction": "What is workforce housing in multifamily lending?",
            "output": "Workforce housing refers to apartments affordable to tenants earning up to 120% of area median income. Over 90% of Fannie Mae's financed apartments are classified as workforce housing, targeting middle-income workers."
        },
        {
            "instruction": "What is the DUS platform?",
            "output": "The Delegated Underwriting and Servicing (DUS) platform is Fannie Mae's multifamily lending system where approved lenders handle underwriting and servicing while typically retaining one-third of the loan risk, emphasizing technology, risk management, and data standards."
        },
        {
            "instruction": "What is Fannie Mae's green financing approach in multifamily?",
            "output": "Fannie Mae pioneers green financing solutions incorporating energy and water efficiency concepts, supporting preservation, rehabilitation, and new construction of rental housing with environmental benefits and cost savings."
        },
        {
            "instruction": "What was Fannie Mae's Q1 2025 multifamily performance?",
            "output": "In Q1 2025, Fannie Mae financed over 93,000 rental units, demonstrating continued strong activity in supporting affordable and workforce housing across the country."
        }
    ]
    knowledge_base.extend(multifamily_detailed)
    
    # Consumer Resources and Tools
    consumer_resources = [
        {
            "instruction": "What is HomeView homebuyer education?",
            "output": "HomeView is Fannie Mae's free online homebuyer education course covering detailed homebuying process steps, available in English and Spanish. Completing the course may help borrowers qualify for home buying assistance programs."
        },
        {
            "instruction": "What calculators and tools does Fannie Mae provide consumers?",
            "output": "Fannie Mae provides mortgage calculators, down payment assistance search tool, mortgage affordability calculator, loan lookup tool, income calculator, and closing costs calculator through yourhome.fanniemae.com and related platforms."
        },
        {
            "instruction": "What renter resources does Fannie Mae offer?",
            "output": "Fannie Mae offers renter resources including rental process guidance, renter rights information, the 'Make Your Rent Count' program to help build credit through rent payments, and credit basics education."
        },
        {
            "instruction": "What financial assistance programs does Fannie Mae provide?",
            "output": "Fannie Mae provides help for financial uncertainty, disaster recovery assistance, connections to housing counselors, forbearance options, and various homeownership assistance programs."
        },
        {
            "instruction": "What educational content does Fannie Mae offer homeowners?",
            "output": "Fannie Mae offers educational content on credit score improvement, understanding mortgage statements, homeownership preparation, severe weather home preparation, and comprehensive housing journey support."
        }
    ]
    knowledge_base.extend(consumer_resources)
    
    # Recent News and Developments
    recent_developments = [
        {
            "instruction": "What recent portfolio management activities has Fannie Mae announced?",
            "output": "Fannie Mae announced the sale of reperforming loans in August 2025 and completed its twenty-seventh non-performing loan sale transaction as part of active mortgage portfolio management."
        },
        {
            "instruction": "What current research initiatives is Fannie Mae pursuing?",
            "output": "Fannie Mae is currently researching leveraging variable and gig income to expand homeownership, analyzing consumer attitudes toward new housing development, and developing methods to assess mortgage credit risk safely."
        },
        {
            "instruction": "How is Fannie Mae addressing housing access challenges?",
            "output": "Fannie Mae is focusing on income flexibility for mortgage approvals, researching risk management techniques, studying consumer perspectives on housing density and zoning, and expanding access to credit for underserved populations."
        }
    ]
    knowledge_base.extend(recent_developments)
    
    # Additional Comprehensive Content
    additional_content = [
        {
            "instruction": "What is Fannie Mae's approach to sustainable housing?",
            "output": "Fannie Mae promotes sustainable housing through green financing options, energy-efficient mortgage products like HomeStyle Energy, multifamily green building certifications, and research into environmental benefits of energy-efficient housing."
        },
        {
            "instruction": "How does Fannie Mae support housing counselors?",
            "output": "Fannie Mae provides training and resources for housing counselors, connects consumers to certified housing counseling agencies, supports foreclosure prevention counseling, and offers specialized resources for disaster-affected areas."
        },
        {
            "instruction": "What is Fannie Mae's role in mortgage servicing?",
            "output": "Fannie Mae establishes servicing guidelines through the Servicing Guide, operates a Servicing Marketplace to facilitate servicing transfers, provides technology solutions for servicers, and oversees servicing quality to protect borrower interests."
        },
        {
            "instruction": "How does Fannie Mae ensure loan quality?",
            "output": "Fannie Mae ensures loan quality through Desktop Underwriter automated risk assessment, Collateral Underwriter for appraisal risk, Day 1 Certainty program, quality control sampling, and comprehensive selling guide standards."
        },
        {
            "instruction": "What is Fannie Mae's approach to affordable housing preservation?",
            "output": "Fannie Mae supports affordable housing preservation through acquisition and rehabilitation financing, partnerships with affordable housing developers, tax credit equity investments, and specialized loan products for aging affordable housing properties."
        }
    ]
    knowledge_base.extend(additional_content)
    
    return knowledge_base

def merge_with_existing_knowledge():
    """Merge new comprehensive content with existing knowledge base files."""
    
    all_knowledge = []
    
    # Load existing files
    existing_files = [
        "fannie_glossary.jsonl",
        "fannie_multifamily_attributes.jsonl", 
        "fannie_single_family_glossary.jsonl",
        "fannie_selling_guide_complete.jsonl",
        "fannie_mae_knowledge_base_foundation.jsonl"
    ]
    
    for filename in existing_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        all_knowledge.append(data)
            print(f"Loaded content from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found, skipping...")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    # Add new comprehensive content
    new_content = create_comprehensive_fannie_mae_knowledge_base()
    all_knowledge.extend(new_content)
    
    return all_knowledge

def save_final_knowledge_base(knowledge_base: List[Dict[str, str]], filename: str):
    """Save final comprehensive knowledge base."""
    
    # Remove duplicates and clean up
    seen = set()
    unique_knowledge = []
    
    for item in knowledge_base:
        # Clean up instruction and output
        instruction = ' '.join(item['instruction'].split())
        output = ' '.join(item['output'].split())
        
        sig = (instruction.lower()[:100], output.lower()[:100])
        if sig not in seen and len(instruction) > 5 and len(output) > 20:
            seen.add(sig)
            unique_knowledge.append({
                "instruction": instruction,
                "output": output
            })
    
    # Sort by instruction length for better organization
    unique_knowledge.sort(key=lambda x: len(x['instruction']))
    
    with open(filename, 'w', encoding='utf-8') as f:
        for item in unique_knowledge:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    return len(unique_knowledge)

def main():
    print("Creating comprehensive Fannie Mae knowledge base...")
    
    # Merge all knowledge
    all_knowledge = merge_with_existing_knowledge()
    print(f"Total items collected: {len(all_knowledge)}")
    
    # Save final knowledge base
    output_file = "fannie_mae_complete_knowledge_base.jsonl"
    unique_count = save_final_knowledge_base(all_knowledge, output_file)
    
    print(f"✓ Saved {unique_count} unique entries to {output_file}")
    
    # Show statistics
    with open(output_file, 'r') as f:
        lines = f.readlines()
        
        # Count by category
        categories = {
            'definitions': 0,
            'requirements': 0,
            'procedures': 0,
            'products': 0,
            'general': 0
        }
        
        for line in lines:
            data = json.loads(line)
            instruction = data['instruction'].lower()
            
            if 'what is' in instruction or 'define' in instruction:
                categories['definitions'] += 1
            elif 'requirement' in instruction or 'criteria' in instruction:
                categories['requirements'] += 1
            elif 'how to' in instruction or 'procedure' in instruction:
                categories['procedures'] += 1
            elif any(product in instruction for product in ['homeready', 'refi', 'homestyl', 'du', 'mbs']):
                categories['products'] += 1
            else:
                categories['general'] += 1
    
    print(f"\nKnowledge Base Statistics:")
    print(f"  Total entries: {len(lines)}")
    print(f"  Definitions: {categories['definitions']}")
    print(f"  Requirements: {categories['requirements']}")
    print(f"  Procedures: {categories['procedures']}")
    print(f"  Products: {categories['products']}")
    print(f"  General: {categories['general']}")
    
    # Show samples
    print("\nFirst 5 entries:")
    for i, line in enumerate(lines[:5]):
        data = json.loads(line)
        print(f"\n[{i+1}] {data['instruction']}")
        print(f"    {data['output'][:120]}...")

if __name__ == "__main__":
    main()