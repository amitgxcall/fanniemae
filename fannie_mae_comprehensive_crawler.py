#!/usr/bin/env python3
import json
import time
from typing import List, Dict

class FannieMaeKnowledgeExtractor:
    def __init__(self):
        self.knowledge_base = []
    
    def extract_section(self, section_name: str, url: str, content_type: str) -> List[Dict[str, str]]:
        """Extract content from a specific section and convert to instruction-output pairs."""
        print(f"Extracting {section_name}...")
        # This will use WebFetch calls to systematically extract content
        return []
    
    def create_comprehensive_knowledge_base(self) -> List[Dict[str, str]]:
        """Create comprehensive knowledge base from all major sections."""
        
        knowledge_base = []
        
        # Our Company Section
        company_content = [
            {
                "instruction": "What is Fannie Mae?",
                "output": "Fannie Mae (Federal National Mortgage Association) is a government-sponsored enterprise (GSE) that purchases mortgages from lenders, packages them into mortgage-backed securities, and sells them to investors. This provides liquidity to the mortgage market and enables lenders to make more home loans available to borrowers."
            },
            {
                "instruction": "What is Fannie Mae's mission?",
                "output": "Fannie Mae's mission is to facilitate equitable and sustainable access to homeownership and quality affordable rental housing across America. We serve the people who house America by providing mortgage capital to lenders and by working to remove barriers to sustainable housing."
            },
            {
                "instruction": "When was Fannie Mae established?",
                "output": "Fannie Mae was established in 1938 as part of the New Deal during the Great Depression. It was created to expand the secondary mortgage market by securitizing mortgages and providing lenders with more capital to lend to home buyers."
            },
            {
                "instruction": "Who owns Fannie Mae?",
                "output": "Fannie Mae is a shareholder-owned company with publicly traded stock. However, since 2008, it has been under the conservatorship of the Federal Housing Finance Agency (FHFA) following the financial crisis."
            },
            {
                "instruction": "What is Fannie Mae's role in the housing market?",
                "output": "Fannie Mae plays a critical role in the U.S. housing market by providing liquidity to mortgage lenders, establishing underwriting guidelines, supporting affordable housing initiatives, and helping to ensure a stable and accessible mortgage market for borrowers across the country."
            }
        ]
        knowledge_base.extend(company_content)
        
        # Single-Family Business Section
        single_family_content = [
            {
                "instruction": "What single-family mortgage products does Fannie Mae offer?",
                "output": "Fannie Mae offers various single-family mortgage products including conventional fixed-rate mortgages, adjustable-rate mortgages (ARMs), HomeReady mortgages for low- to moderate-income borrowers, RefiNow for refinancing, and specialized products for manufactured housing and condominiums."
            },
            {
                "instruction": "What is HomeReady?",
                "output": "HomeReady is Fannie Mae's affordable lending solution designed to help creditworthy low- to moderate-income borrowers buy or refinance a home. It offers flexible sources for down payment and closing costs, reduced mortgage insurance costs, and allows for non-traditional credit sources."
            },
            {
                "instruction": "What is Desktop Underwriter (DU)?",
                "output": "Desktop Underwriter (DU) is Fannie Mae's automated underwriting system that provides lenders with comprehensive risk assessment and loan recommendations. It evaluates multiple borrower and loan characteristics to deliver approve/eligible, approve/ineligible, or refer decisions."
            },
            {
                "instruction": "What technology solutions does Fannie Mae provide to lenders?",
                "output": "Fannie Mae provides various technology solutions including Desktop Underwriter for automated underwriting, Day 1 Certainty for representation and warranty relief, Collateral Underwriter for appraisal risk assessment, and Fannie Mae Connect for loan delivery and servicing."
            },
            {
                "instruction": "What is the Selling Guide?",
                "output": "The Selling Guide is Fannie Mae's comprehensive manual that provides detailed policies and procedures for originating, underwriting, and selling mortgages to Fannie Mae. It covers eligibility requirements, documentation standards, and quality control processes."
            }
        ]
        knowledge_base.extend(single_family_content)
        
        # Multifamily Business Section
        multifamily_content = [
            {
                "instruction": "What is Fannie Mae's Multifamily business?",
                "output": "Fannie Mae's Multifamily business provides financing solutions for apartment buildings, manufactured housing communities, student housing, senior housing, and other multifamily properties. It supports both market-rate and affordable housing through various loan products and financing structures."
            },
            {
                "instruction": "What types of multifamily properties does Fannie Mae finance?",
                "output": "Fannie Mae finances various multifamily properties including conventional apartment buildings, affordable housing developments, student housing facilities, senior housing communities, manufactured housing communities, cooperative housing, and supportive housing for special needs populations."
            },
            {
                "instruction": "What is Fannie Mae's Duty to Serve?",
                "output": "Duty to Serve is Fannie Mae's regulatory obligation to serve three underserved markets: affordable housing preservation, rural housing, and manufactured housing. It requires specific activities and investment levels to increase liquidity and improve access to credit in these markets."
            },
            {
                "instruction": "What green financing options does Fannie Mae offer?",
                "output": "Fannie Mae offers green financing options including Green Building Certification loans for ENERGY STAR and green-certified properties, Green Rewards for energy and water efficiency improvements, Healthy Housing Rewards for health-focused improvements, and renewable energy financing."
            }
        ]
        knowledge_base.extend(multifamily_content)
        
        # Capital Markets Section
        capital_markets_content = [
            {
                "instruction": "What are Fannie Mae mortgage-backed securities (MBS)?",
                "output": "Fannie Mae MBS are investment securities created by pooling eligible mortgages and selling them to investors. These securities provide investors with regular interest and principal payments while transferring credit and prepayment risk. They help provide capital to the mortgage market."
            },
            {
                "instruction": "What is Credit Risk Transfer (CRT)?",
                "output": "Credit Risk Transfer (CRT) is Fannie Mae's program to transfer a portion of credit risk on single-family mortgages to private capital markets through securities and insurance transactions. This reduces taxpayer risk while maintaining market liquidity."
            },
            {
                "instruction": "What structured transactions does Fannie Mae offer?",
                "output": "Fannie Mae offers various structured transactions including Connecticut Avenue Securities (CAS) for credit risk transfer, Credit Insurance Risk Transfer (CIRT), and other capital markets solutions that help distribute mortgage credit risk to private investors."
            }
        ]
        knowledge_base.extend(capital_markets_content)
        
        # Homebuyers and Consumers Section
        consumer_content = [
            {
                "instruction": "What tools does Fannie Mae provide for homebuyers?",
                "output": "Fannie Mae provides various tools for homebuyers including mortgage calculators, affordability calculators, down payment assistance finder, HomePath property search, homeownership education courses, and credit improvement resources."
            },
            {
                "instruction": "What is HomePath?",
                "output": "HomePath is Fannie Mae's program for selling foreclosed properties (Real Estate Owned or REO) to homebuyers, investors, and non-profit organizations. It offers special financing options and reduced down payment requirements for qualified buyers."
            },
            {
                "instruction": "What homeownership education does Fannie Mae provide?",
                "output": "Fannie Mae provides comprehensive homeownership education through HomeView courses covering home buying process, mortgage basics, budgeting, credit improvement, and post-purchase homeownership responsibilities. Many courses are available online and in multiple languages."
            },
            {
                "instruction": "What is Know Your Options?",
                "output": "Know Your Options is Fannie Mae's foreclosure prevention program that provides resources and counseling to help struggling homeowners understand their options, including loan modifications, forbearance, short sales, and deed-in-lieu alternatives."
            }
        ]
        knowledge_base.extend(consumer_content)
        
        # Housing Policy and Research
        policy_content = [
            {
                "instruction": "What housing research does Fannie Mae conduct?",
                "output": "Fannie Mae conducts extensive housing research through its Economic and Strategic Research team, publishing reports on housing market trends, affordability analysis, demographic studies, and policy research to inform housing finance decisions and public policy."
            },
            {
                "instruction": "What is Fannie Mae's Housing Insights?",
                "output": "Housing Insights is Fannie Mae's research publication that provides data-driven analysis of housing market trends, economic factors affecting housing, demographic shifts, and policy implications for housing finance and homeownership."
            },
            {
                "instruction": "How does Fannie Mae support affordable housing?",
                "output": "Fannie Mae supports affordable housing through various initiatives including HomeReady and other affordable loan products, multifamily affordable housing financing, down payment assistance programs, housing trust fund investments, and partnerships with housing organizations."
            }
        ]
        knowledge_base.extend(policy_content)
        
        # Regulatory and Compliance
        regulatory_content = [
            {
                "instruction": "What is FHFA's role with Fannie Mae?",
                "output": "The Federal Housing Finance Agency (FHFA) is Fannie Mae's regulator and conservator. FHFA oversees Fannie Mae's operations, sets capital requirements, establishes housing goals, and has been the conservator since 2008, managing the company in the public interest."
            },
            {
                "instruction": "What are Fannie Mae's housing goals?",
                "output": "Fannie Mae's housing goals are regulatory requirements set by FHFA that specify minimum percentages of mortgage purchases that must serve low- and moderate-income borrowers, underserved areas, and first-time homebuyers. These goals ensure GSE mission fulfillment."
            },
            {
                "instruction": "What is the Single Security Initiative?",
                "output": "The Single Security Initiative is a joint effort by Fannie Mae and Freddie Mac to create a common mortgage-backed security called the Uniform Mortgage-Backed Security (UMBS), which increases market liquidity and reduces funding costs for both GSEs."
            }
        ]
        knowledge_base.extend(regulatory_content)
        
        return knowledge_base
    
    def save_knowledge_base(self, knowledge_base: List[Dict[str, str]], filename: str):
        """Save knowledge base to JSONL file."""
        
        # Remove duplicates and clean up
        seen = set()
        unique_knowledge = []
        
        for item in knowledge_base:
            # Clean up instruction and output
            instruction = ' '.join(item['instruction'].split())
            output = ' '.join(item['output'].split())
            
            sig = (instruction[:100], output[:100])
            if sig not in seen and len(instruction) > 5 and len(output) > 20:
                seen.add(sig)
                unique_knowledge.append({
                    "instruction": instruction,
                    "output": output
                })
        
        with open(filename, 'w', encoding='utf-8') as f:
            for item in unique_knowledge:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        return len(unique_knowledge)

def main():
    print("Creating comprehensive Fannie Mae knowledge base...")
    
    extractor = FannieMaeKnowledgeExtractor()
    
    # Create comprehensive knowledge base
    knowledge_base = extractor.create_comprehensive_knowledge_base()
    
    print(f"Generated {len(knowledge_base)} knowledge base entries")
    
    # Save to JSONL
    output_file = "fannie_mae_knowledge_base_foundation.jsonl"
    unique_count = extractor.save_knowledge_base(knowledge_base, output_file)
    
    print(f"✓ Saved {unique_count} unique entries to {output_file}")
    
    # Show samples
    print("\nFirst 5 entries:")
    with open(output_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            data = json.loads(line)
            print(f"\n[{i+1}] {data['instruction']}")
            print(f"    {data['output'][:120]}...")

if __name__ == "__main__":
    main()