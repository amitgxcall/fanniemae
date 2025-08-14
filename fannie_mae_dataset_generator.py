#!/usr/bin/env python3
"""
Fannie Mae Knowledge Dataset Generator
Creates 20,000 instruction-output pairs for training an LLM on Fannie Mae mortgage knowledge
"""

import json
import random
import os
from typing import List, Dict, Tuple, Set
import re
from collections import defaultdict

class FannieMaeDatasetGenerator:
    """Generate a comprehensive dataset of Fannie Mae knowledge instruction-output pairs"""
    
    def __init__(self):
        self.dataset = []
        self.existing_instructions = set()
        self.categories = {
            "company_info": "Fannie Mae company information and business operations",
            "single_family": "Fannie Mae single-family mortgage lending and homeownership",
            "multifamily": "Fannie Mae multifamily lending and apartment financing",
            "capital_markets": "Fannie Mae mortgage-backed securities and capital markets",
            "underwriting": "Fannie Mae underwriting guidelines and loan eligibility",
            "affordable_housing": "Fannie Mae affordable housing initiatives and programs",
            "technology": "Fannie Mae technology solutions and automated systems",
            "loan_products": "Fannie Mae loan products and special financing programs",
            "regulatory": "Fannie Mae regulatory requirements and compliance guidelines",
            "consumer": "Fannie Mae consumer resources and homebuyer education",
            "glossary": "Fannie Mae mortgage lending and housing finance knowledge base"
        }
        
        # Templates for generating variations
        self.question_templates = [
            "What is {term}?",
            "Define {term}.",
            "Can you explain what {term} is?",
            "What does {term} mean?",
            "What is the definition of {term}?",
            "What is meant by {term}?",
            "What is {term} in mortgage lending?",
            "Explain the concept of {term}.",
            "Please define {term}.",
            "How would you define {term}?"
        ]
        
        # Templates for more complex questions
        self.complex_question_templates = [
            "How does {term1} differ from {term2}?",
            "What are the requirements for {term}?",
            "What is the process for {term}?",
            "What are the benefits of {term}?",
            "What are the eligibility criteria for {term}?",
            "How is {term} calculated?",
            "What factors affect {term}?",
            "When would someone use {term}?",
            "What are the key features of {term}?",
            "What documentation is required for {term}?"
        ]
        
        # Modifier templates to create variations
        self.modifier_templates = [
            "in the context of Fannie Mae",
            "according to Fannie Mae guidelines",
            "in mortgage lending",
            "in housing finance",
            "for conventional loans",
            "for homebuyers",
            "in the secondary mortgage market",
            "for lenders",
            "in underwriting",
            "for loan qualification"
        ]
    
    def load_existing_data(self, jsonl_files: List[str]) -> None:
        """Load existing data from JSONL files"""
        for file in jsonl_files:
            if not os.path.exists(file):
                print(f"Warning: File {file} not found. Skipping.")
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Handle different formats
                        if 'instruction' in entry and 'output' in entry:
                            instruction = entry['instruction']
                            output = entry['output']
                        elif 'dialog' in entry:
                            # Handle dialog format
                            instruction = entry['dialog'][0]['content']
                            output = entry['dialog'][1]['content']
                        else:
                            # Skip entries with unknown format
                            continue
                        
                        # Check if the instruction is already in our dataset
                        if instruction not in self.existing_instructions:
                            self.dataset.append({
                                "instruction": instruction,
                                "output": output
                            })
                            self.existing_instructions.add(instruction)
                    except json.JSONDecodeError:
                        print(f"Warning: Invalid JSON in {file}. Skipping line.")
                    except Exception as e:
                        print(f"Error processing line in {file}: {e}")
        
        print(f"Loaded {len(self.dataset)} unique entries from existing files")
    
    def extract_terms(self) -> Dict[str, List[str]]:
        """Extract terms and their definitions from the dataset"""
        terms = defaultdict(list)
        extraction_patterns = [
            (r"^What is (.+?)\?$", 1),
            (r"^Define (.+?)\.$", 1),
            (r"^What does (.+?) mean\?$", 1),
            (r"^What is the definition of (.+?)\?$", 1),
            (r"^What is (.+?) in mortgage lending\?$", 1),
            (r"^Explain (.+?)\.$", 1)
        ]
        
        term_count = 0
        
        for entry in self.dataset:
            instruction = entry["instruction"]
            output = entry["output"]
            
            term = None
            
            # Try multiple patterns to extract terms
            for pattern, group in extraction_patterns:
                match = re.search(pattern, instruction)
                if match:
                    term = match.group(group).strip()
                    break
            
            # If no pattern matched but instruction starts with "What is", try simple extraction
            if term is None and instruction.startswith("What is ") and instruction.endswith("?"):
                term = instruction[8:-1].strip()
            
            # Process the extracted term
            if term and len(term.split()) <= 5:  # Only consider reasonably short terms
                category = self._determine_category(output)
                terms[category].append((term, output))
                term_count += 1
        
        print(f"Extracted {term_count} terms across {len(terms)} categories")
        
        # If we didn't extract enough terms, use all entries as potential terms
        if term_count < 100:
            print("Not enough terms extracted. Using all entries as potential terms.")
            for entry in self.dataset:
                instruction = entry["instruction"]
                output = entry["output"]
                
                # Try to extract a potential term from the instruction
                potential_term = instruction
                if instruction.endswith("?"):
                    potential_term = instruction[:-1]
                if instruction.startswith("What is "):
                    potential_term = instruction[8:]
                if len(potential_term.split()) <= 10:  # Allow longer "terms" in this fallback
                    category = self._determine_category(output)
                    terms[category].append((potential_term, output))
        
        return terms
    
    def _determine_category(self, text: str) -> str:
        """Determine the category of an entry based on its content"""
        category_scores = {}
        
        for category, keywords in self.categories.items():
            score = 0
            for word in keywords.lower().split():
                if word in text.lower():
                    score += 1
            category_scores[category] = score
        
        # Return the category with the highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def generate_variations(self, target_count: int = 20000) -> None:
        """Generate variations to reach the target count"""
        print(f"Starting with {len(self.dataset)} entries")
        
        # Extract terms and their definitions
        terms_by_category = self.extract_terms()
        all_terms = []
        for category, terms in terms_by_category.items():
            print(f"Category '{category}' has {len(terms)} terms")
            all_terms.extend(terms)
        
        if not all_terms:
            print("ERROR: No terms extracted. Cannot generate variations.")
            return
            
        print(f"Total extracted terms: {len(all_terms)}")
        
        # If we don't have enough terms, create some basic ones
        if len(all_terms) < 50:
            print("Not enough terms extracted. Creating basic terms...")
            basic_terms = [
                ("Mortgage", "A loan used to buy or refinance a home, where the property serves as collateral for the loan."),
                ("Fannie Mae", "A government-sponsored enterprise that purchases mortgages from lenders and packages them into mortgage-backed securities."),
                ("Loan-to-value ratio", "The ratio of a loan to the value of the property, expressed as a percentage."),
                ("Debt-to-income ratio", "A measure of a borrower's monthly debt payments compared to their gross monthly income."),
                ("Conventional loan", "A mortgage loan not insured or guaranteed by the federal government."),
                ("Underwriting", "The process a lender uses to determine if the risk of offering a mortgage to a particular borrower is acceptable."),
                ("Escrow", "An account held by the lender to pay property-related expenses like taxes and insurance."),
                ("Down payment", "The amount of money paid upfront to purchase a home, usually expressed as a percentage of the purchase price."),
                ("Credit score", "A numerical expression based on analysis of a person's credit files, representing creditworthiness."),
                ("Amortization", "The gradual repayment of a mortgage loan by installments with both principal and interest."),
                ("Private mortgage insurance", "Insurance that protects the lender if the borrower defaults on a loan with an LTV ratio above 80%."),
                ("HomeReady", "Fannie Mae's affordable lending solution designed for low- to moderate-income borrowers."),
                ("Closing costs", "Expenses over and above the price of the property that buyers and sellers incur to complete a transaction."),
                ("Appraisal", "A professional analysis used to estimate the value of the property."),
                ("Fixed-rate mortgage", "A mortgage with an interest rate that remains the same for the entire term of the loan.")
            ]
            
            for term, definition in basic_terms:
                category = "glossary"  # Default category
                if "Fannie Mae" in term or "Fannie Mae" in definition:
                    category = "company_info"
                all_terms.append((term, definition))
            
            print(f"Added {len(basic_terms)} basic terms. Total terms: {len(all_terms)}")
        
        # Generate basic variations using templates
        target_basic = int(target_count * 0.4)
        print(f"Generating {target_basic} basic variations...")
        variation_count = 0
        max_attempts = target_basic * 3  # Limit attempts to avoid infinite loop
        attempts = 0
        
        while len(self.dataset) < target_count * 0.4 and attempts < max_attempts:
            attempts += 1
            if attempts % 1000 == 0:
                print(f"Made {attempts} attempts, generated {variation_count} variations, dataset size: {len(self.dataset)}")
                
            term_entry = random.choice(all_terms)
            term, definition = term_entry
            
            template = random.choice(self.question_templates)
            instruction = template.format(term=term)
            
            if instruction not in self.existing_instructions:
                self.dataset.append({
                    "instruction": instruction,
                    "output": definition
                })
                self.existing_instructions.add(instruction)
                variation_count += 1
        
        print(f"Generated {variation_count} basic variations, now at {len(self.dataset)} entries ({attempts} attempts)")
        
        # Generate modified questions (with context)
        target_modified = int(target_count * 0.6)
        print(f"Generating modified questions to reach {target_modified} entries...")
        variation_count = 0
        max_attempts = (target_modified - len(self.dataset)) * 3
        attempts = 0
        
        while len(self.dataset) < target_count * 0.6 and attempts < max_attempts:
            attempts += 1
            if attempts % 1000 == 0:
                print(f"Made {attempts} attempts, generated {variation_count} variations, dataset size: {len(self.dataset)}")
                
            term_entry = random.choice(all_terms)
            term, definition = term_entry
            
            template = random.choice(self.question_templates)
            modifier = random.choice(self.modifier_templates)
            instruction = template.format(term=f"{term} {modifier}")
            
            if instruction not in self.existing_instructions:
                self.dataset.append({
                    "instruction": instruction,
                    "output": definition
                })
                self.existing_instructions.add(instruction)
                variation_count += 1
        
        print(f"Generated {variation_count} modified questions, now at {len(self.dataset)} entries")
        
        # Generate complex questions (comparisons, processes, etc.)
        target_complex = int(target_count * 0.8)
        print(f"Generating complex questions to reach {target_complex} entries...")
        variation_count = 0
        max_attempts = (target_complex - len(self.dataset)) * 3
        attempts = 0
        
        while len(self.dataset) < target_count * 0.8 and attempts < max_attempts:
            attempts += 1
            if attempts % 1000 == 0:
                print(f"Made {attempts} attempts, generated {variation_count} variations, dataset size: {len(self.dataset)}")
                
            template = random.choice(self.complex_question_templates)
            
            if "{term1}" in template and "{term2}" in template:
                # For comparison questions
                term1_entry = random.choice(all_terms)
                term2_entry = random.choice(all_terms)
                while term1_entry == term2_entry:
                    term2_entry = random.choice(all_terms)
                
                term1, def1 = term1_entry
                term2, def2 = term2_entry
                
                instruction = template.format(term1=term1, term2=term2)
                output = self._generate_comparison(term1, def1, term2, def2)
            else:
                # For other complex questions
                term_entry = random.choice(all_terms)
                term, definition = term_entry
                
                instruction = template.format(term=term)
                output = self._generate_complex_answer(template, term, definition)
            
            if instruction not in self.existing_instructions:
                self.dataset.append({
                    "instruction": instruction,
                    "output": output
                })
                self.existing_instructions.add(instruction)
                variation_count += 1
        
        print(f"Generated {variation_count} complex questions, now at {len(self.dataset)} entries")
        
        # Generate scenario-based questions
        target_final = target_count
        print(f"Generating scenario questions to reach {target_final} entries...")
        variation_count = 0
        max_attempts = (target_final - len(self.dataset)) * 3
        attempts = 0
        
        while len(self.dataset) < target_count and attempts < max_attempts:
            attempts += 1
            if attempts % 1000 == 0:
                print(f"Made {attempts} attempts, generated {variation_count} variations, dataset size: {len(self.dataset)}")
                
            term_entry = random.choice(all_terms)
            term, definition = term_entry
            
            instruction, output = self._generate_scenario_question(term, definition)
            
            if instruction not in self.existing_instructions:
                self.dataset.append({
                    "instruction": instruction,
                    "output": output
                })
                self.existing_instructions.add(instruction)
                variation_count += 1
        
        print(f"Generated {variation_count} scenario questions")
        print(f"Final dataset size: {len(self.dataset)} entries")
        
        if len(self.dataset) < target_count:
            print(f"WARNING: Could only generate {len(self.dataset)} entries, which is less than the target of {target_count}")
            print("Consider adding more source data or adjusting the extraction criteria.")
    
    def _generate_comparison(self, term1: str, def1: str, term2: str, def2: str) -> str:
        """Generate a comparison between two terms"""
        return f"{term1} refers to {def1.split('.')[0] if '.' in def1 else def1}\n\nIn contrast, {term2} refers to {def2.split('.')[0] if '.' in def2 else def2}\n\nThe key differences are related to their purpose and application in mortgage lending."
    
    def _generate_complex_answer(self, template: str, term: str, definition: str) -> str:
        """Generate a more complex answer based on the question template"""
        if "requirements" in template or "criteria" in template:
            return f"The requirements for {term} typically include proper documentation, lender verification, and compliance with Fannie Mae guidelines. {definition}"
        
        if "process" in template:
            return f"The process for {term} involves application submission, verification of information, underwriting approval, and final documentation. {definition}"
        
        if "benefits" in template:
            return f"The benefits of {term} include potential cost savings, streamlined processes, and expanded eligibility for borrowers. {definition}"
        
        if "calculated" in template:
            return f"{term} is calculated based on relevant financial data, including income, debt, and property value as applicable. {definition}"
        
        if "factors" in template:
            return f"Key factors affecting {term} include market conditions, borrower qualifications, property characteristics, and regulatory requirements. {definition}"
        
        if "use" in template:
            return f"{term} is typically used when borrowers need specific financing options or when lenders need to meet certain requirements. {definition}"
        
        if "features" in template:
            return f"The key features of {term} include specific eligibility criteria, documentation requirements, and potential benefits for qualified borrowers. {definition}"
        
        if "documentation" in template:
            return f"Documentation required for {term} typically includes income verification, asset statements, property information, and credit history. {definition}"
        
        # Default response
        return definition
    
    def _generate_scenario_question(self, term: str, definition: str) -> Tuple[str, str]:
        """Generate a scenario-based question and answer"""
        scenarios = [
            f"How would {term} affect a first-time homebuyer?",
            f"What happens if a borrower doesn't meet the requirements for {term}?",
            f"Can {term} be used with other Fannie Mae programs?",
            f"Is {term} available for investment properties?",
            f"How does {term} impact loan pricing?",
            f"What is the relationship between {term} and credit scores?",
            f"When should a lender consider {term} for a borrower?",
            f"What are common misconceptions about {term}?",
            f"How has {term} evolved in recent years?",
            f"What role does {term} play in the mortgage approval process?"
        ]
        
        instruction = random.choice(scenarios)
        
        # Generate contextual answer
        if "first-time homebuyer" in instruction:
            output = f"For first-time homebuyers, {term} can be particularly important because they often have unique financing needs. {definition}"
        elif "doesn't meet the requirements" in instruction:
            output = f"If a borrower doesn't meet the requirements for {term}, they may need to explore alternative financing options or work to improve their qualification factors. {definition}"
        elif "other Fannie Mae programs" in instruction:
            output = f"Yes, {term} can often be used in conjunction with other Fannie Mae programs, providing borrowers with flexible financing solutions. {definition}"
        elif "investment properties" in instruction:
            output = f"{term} may be available for investment properties, though typically with different requirements than for primary residences. {definition}"
        elif "loan pricing" in instruction:
            output = f"{term} can impact loan pricing through risk assessment, eligibility determination, and specific program requirements. {definition}"
        elif "credit scores" in instruction:
            output = f"{term} and credit scores are often related in the mortgage process, as credit worthiness is a key factor in loan eligibility and terms. {definition}"
        elif "lender consider" in instruction:
            output = f"Lenders should consider {term} when evaluating borrower eligibility, loan terms, and compliance with Fannie Mae guidelines. {definition}"
        elif "misconceptions" in instruction:
            output = f"Common misconceptions about {term} include misunderstandings about eligibility requirements, application processes, and available benefits. {definition}"
        elif "evolved" in instruction:
            output = f"{term} has evolved over time to adapt to changing market conditions, regulatory requirements, and borrower needs. {definition}"
        elif "role" in instruction:
            output = f"{term} plays an important role in the mortgage approval process by impacting eligibility, terms, and compliance requirements. {definition}"
        else:
            output = definition
        
        return instruction, output
    
    def save_dataset(self, output_file: str) -> None:
        """Save the dataset to a JSONL file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in self.dataset:
                f.write(json.dumps(entry) + '\n')
        
        print(f"Saved {len(self.dataset)} entries to {output_file}")

def main():
    """Main function to generate the dataset"""
    generator = FannieMaeDatasetGenerator()
    
    # List of input files
    input_files = [
        "fannie_attributes.jsonl",
        "fannie_mae_instruction_context_response_dynamic.jsonl",
        "fannie_mae_knowledge_base_foundation.jsonl",
        "fannie_mae_llama_dialog.jsonl",
        "fannie_mae_master_knowledge_base.jsonl",
        "fannie_multifamily_attributes.jsonl",
        "fannie_selling_guide.jsonl",
        "fannie_selling_guide_complete.jsonl",
        "fannie_selling_guide_comprehensive.jsonl",
        "fannie_single_family_glossary.jsonl",
        "final_1.jsonl"
    ]
    
    # Filter to only include files that exist
    existing_files = []
    for file in input_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            print(f"Warning: File {file} not found and will be skipped.")
    
    if not existing_files:
        print("Error: No input files found. Please check file paths.")
        return
    
    print(f"Found {len(existing_files)} input files.")
    
    # Load existing data
    generator.load_existing_data(existing_files)
    
    # Check if we have enough data to proceed
    if len(generator.dataset) < 10:
        print("Error: Not enough entries loaded. Please check your input files.")
        return
    
    # Create a small sample dataset (for testing)
    # Set target to a lower number for testing first
    target_count = 20000
    print(f"Generating variations to reach {target_count} entries...")
    
    # Generate variations to reach the target count
    generator.generate_variations(target_count=target_count)
    
    # Save the dataset
    output_file = "fannie_mae_complete_dataset_20k.jsonl"
    generator.save_dataset(output_file)
    
    # Create a small sample file as well (first 1000 entries)
    sample_file = "fannie_mae_sample_1k.jsonl"
    with open(sample_file, 'w', encoding='utf-8') as f:
        for entry in generator.dataset[:min(1000, len(generator.dataset))]:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Saved sample of {min(1000, len(generator.dataset))} entries to {sample_file}")

if __name__ == "__main__":
    main()