#!/usr/bin/env python3
"""
Fannie Mae Knowledge Dataset Generator
Creates 250,000 instruction-output pairs for training an LLM on Fannie Mae mortgage knowledge
"""

import json
import random
import os
import re
from typing import List, Dict, Tuple, Set, Any, Callable
from collections import defaultdict
import argparse
from datetime import datetime
from tqdm import tqdm

class FannieMaeDatasetGenerator:
    """Generate a comprehensive dataset of Fannie Mae knowledge instruction-output pairs"""
    
    def __init__(self, config_path: str = "config"):
        """Initialize the generator with configuration files"""
        self.dataset = []
        self.existing_instructions = set()
        
        # Load configurations from files
        self.config = self._load_config(config_path)
        self.categories = self.config["categories"]
        self.question_templates = self.config["question_templates"]
        self.complex_question_templates = self.config["complex_question_templates"]
        self.modifier_templates = self.config["modifier_templates"]
        self.scenario_templates = self.config["scenario_templates"]
        self.mortgage_industry_terms = self.config.get("mortgage_industry_terms", [])
        
        # Template functions for generating complex responses
        self.response_generators = {
            "requirements": self._generate_requirements,
            "process": self._generate_process,
            "benefits": self._generate_benefits,
            "eligibility": self._generate_eligibility,
            "calculation": self._generate_calculation,
            "factors": self._generate_factors,
            "use_cases": self._generate_use_cases,
            "features": self._generate_features,
            "documentation": self._generate_documentation,
            "impact": self._generate_impact,
            "comparison": self._generate_comparison,
            "scenario": self._generate_scenario_response
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load all configuration files from the config directory"""
        config = {}
        
        # Define config files to load
        config_files = {
            "categories": "categories.json",
            "question_templates": "question_templates.json",
            "complex_question_templates": "complex_question_templates.json",
            "modifier_templates": "modifier_templates.json",
            "scenario_templates": "scenario_templates.json",
            "mortgage_industry_terms": "mortgage_terms.json",
            "response_templates": "response_templates.json"
        }
        
        # Check if config directory exists, if not use embedded config
        if not os.path.exists(config_path):
            print(f"Config directory {config_path} not found. Using embedded configurations.")
            return self._get_embedded_config()
        
        # Load each config file
        for key, filename in config_files.items():
            file_path = os.path.join(config_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    config[key] = json.load(f)
            else:
                print(f"Warning: Config file {file_path} not found. Using embedded configuration for {key}.")
                config[key] = self._get_embedded_config().get(key, {})
        
        return config
    
    def _get_embedded_config(self) -> Dict[str, Any]:
        """Return embedded configuration if external config files are not available"""
        # This is a simplified version with minimal entries
        return {
            "categories": {
                "company_info": "Fannie Mae company information and business operations",
                "single_family": "Fannie Mae single-family mortgage lending and homeownership",
                "multifamily": "Fannie Mae multifamily lending and apartment financing",
                "capital_markets": "Fannie Mae mortgage-backed securities and capital markets",
                "underwriting": "Fannie Mae underwriting guidelines and loan eligibility"
            },
            "question_templates": [
                "What is {term}?",
                "Define {term}.",
                "Can you explain what {term} is?",
                "What does {term} mean?"
            ],
            "complex_question_templates": [
                "How does {term1} differ from {term2}?",
                "What are the requirements for {term}?",
                "What is the process for {term}?",
                "What are the benefits of {term}?"
            ],
            "modifier_templates": [
                "in the context of Fannie Mae",
                "according to Fannie Mae guidelines",
                "in mortgage lending",
                "in housing finance"
            ],
            "scenario_templates": [
                "I'm a lender working with a borrower who has a 650 credit score. How would {term} affect their loan application?",
                "As a homebuyer with 5% down payment, how does {term} impact my mortgage options?"
            ],
            "mortgage_industry_terms": [
                ["Fannie Mae", "Fannie Mae (Federal National Mortgage Association) is a government-sponsored enterprise that purchases mortgages from lenders, packages them into mortgage-backed securities, and sells them to investors, providing liquidity to the mortgage market."],
                ["Conventional Loan", "A conventional loan is a mortgage that is not guaranteed or insured by any government agency, typically requiring a minimum credit score of 620 and a down payment of at least 3% for first-time homebuyers."]
            ],
            "response_templates": {
                "requirements": {
                    "underwriting": [
                        "Borrower qualification criteria including credit score minimums (typically 620 or higher), debt-to-income ratios (generally not exceeding 45%), and employment verification.",
                        "Property eligibility requirements including acceptable property types, occupancy status, and condition standards."
                    ],
                    "default": [
                        "Adherence to Fannie Mae's published guidelines and requirements in the applicable Selling or Servicing Guide.",
                        "Proper documentation and record-keeping to demonstrate compliance with Fannie Mae standards."
                    ]
                },
                "process": {
                    "underwriting": [
                        "Application: The borrower submits a mortgage application with required documentation.",
                        "Initial Review: The lender reviews the application for completeness and basic eligibility."
                    ],
                    "default": [
                        "Assessment: Evaluate current processes and systems to determine how best to implement the specific mortgage function.",
                        "Planning: Develop a comprehensive plan including timeline, resource requirements, and success metrics."
                    ]
                },
                "scenario": {
                    "lender": [
                        "**Guideline Application**: {term} applies to this situation in the following way: For a borrower with specific circumstances, it affects their eligibility and pricing.",
                        "**Documentation Requirements**: Ensure you collect and verify all documentation required to properly evaluate {term}."
                    ],
                    "default": [
                        "**Application**: {term} applies to this situation in the following ways: It affects eligibility and qualification standards.",
                        "**Compliance and Guidelines**: When working with {term}, ensure adherence to Fannie Mae Selling Guide requirements."
                    ]
                }
            }
        }
    
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
        
        # Add pre-defined mortgage industry terms if we don't have many entries
        if len(self.dataset) < 300:
            self._add_predefined_terms()
    
    def _add_predefined_terms(self):
        """Add predefined mortgage industry terms to the dataset"""
        print("Adding predefined mortgage industry terms...")
        added_count = 0
        
        for term, definition in self.mortgage_industry_terms:
            instruction = f"What is {term}?"
            if instruction not in self.existing_instructions:
                self.dataset.append({
                    "instruction": instruction,
                    "output": definition
                })
                self.existing_instructions.add(instruction)
                added_count += 1
        
        print(f"Added {added_count} predefined terms")
    
    def extract_terms(self) -> Dict[str, List[Tuple[str, str]]]:
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
        
        # Add our predefined terms to the categories
        for term, definition in self.mortgage_industry_terms:
            category = self._determine_category(definition)
            if (term, definition) not in terms[category]:
                terms[category].append((term, definition))
        
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
        
        # Return the category with the highest score, or a default if no matches
        if not category_scores:
            return "default"
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def generate_dataset(self, target_count: int) -> None:
        """Generate a dataset with the specified number of entries"""
        print(f"Starting with {len(self.dataset)} entries")
        
        # Add some default terms if we don't have any
        if not self.mortgage_industry_terms and len(self.dataset) == 0:
            self.mortgage_industry_terms = [
                ["Fannie Mae", "Fannie Mae (Federal National Mortgage Association) is a government-sponsored enterprise that purchases mortgages from lenders, packages them into mortgage-backed securities, and sells them to investors, providing liquidity to the mortgage market."],
                ["Conventional Loan", "A conventional loan is a mortgage that is not guaranteed or insured by any government agency, typically requiring a minimum credit score of 620 and a down payment of at least 3% for first-time homebuyers."],
                ["Debt-to-Income Ratio", "Debt-to-Income (DTI) ratio is a financial measurement that compares a borrower's total monthly debt obligations to their gross monthly income, expressed as a percentage. Fannie Mae typically requires a DTI ratio of 45% or less for most conventional loans."],
                ["Loan-to-Value Ratio", "Loan-to-Value (LTV) ratio is the percentage of a property's value that is financed by a mortgage loan. A higher LTV ratio represents more risk to the lender. Fannie Mae typically requires mortgage insurance for loans with LTV ratios above 80%."],
                ["Desktop Underwriter", "Desktop Underwriter (DU) is Fannie Mae's automated underwriting system that evaluates mortgage loan applications against Fannie Mae's eligibility requirements. It provides a comprehensive credit risk assessment and determines the loan's eligibility for delivery to Fannie Mae."]
            ]
            self._add_predefined_terms()
        
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
        
        # Define generation distribution
        distribution = {
            "basic": 0.30,        # Basic definition questions
            "modified": 0.20,     # Questions with context modifiers
            "complex": 0.25,      # Complex questions about single terms
            "comparison": 0.10,   # Comparison questions between two terms
            "scenario": 0.15      # Scenario-based questions
        }
        
        generation_plan = {
            "basic": int(target_count * distribution["basic"]),
            "modified": int(target_count * distribution["modified"]),
            "complex": int(target_count * distribution["complex"]),
            "comparison": int(target_count * distribution["comparison"]),
            "scenario": int(target_count * distribution["scenario"])
        }
        
        # Ensure the total adds up to target_count
        total_planned = sum(generation_plan.values())
        if total_planned < target_count:
            generation_plan["basic"] += (target_count - total_planned)
        
        print("Generation plan:")
        for category, count in generation_plan.items():
            print(f"  {category}: {count} entries")
        
        # Generate each type of question
        with tqdm(total=target_count - len(self.dataset), desc="Generating dataset") as pbar:
            # Generate basic questions
            self._generate_entries("basic", generation_plan["basic"], all_terms, pbar)
            
            # Generate modified questions
            self._generate_entries("modified", generation_plan["modified"], all_terms, pbar)
            
            # Generate complex questions
            self._generate_entries("complex", generation_plan["complex"], all_terms, pbar)
            
            # Generate comparison questions
            self._generate_entries("comparison", generation_plan["comparison"], all_terms, pbar)
            
            # Generate scenario questions
            self._generate_entries("scenario", generation_plan["scenario"], all_terms, pbar)
        
        print(f"Final dataset size: {len(self.dataset)} entries")
        
        if len(self.dataset) < target_count:
            print(f"WARNING: Could only generate {len(self.dataset)} entries, which is less than the target of {target_count}")
    
    def _generate_entries(self, entry_type: str, count: int, all_terms: List[Tuple[str, str]], pbar) -> None:
        """Generate entries of a specific type"""
        max_attempts = count * 3  # Limit attempts to avoid infinite loop
        attempts = 0
        generated = 0
        
        while generated < count and attempts < max_attempts:
            attempts += 1
            
            if entry_type == "basic":
                success = self._generate_basic_entry(all_terms)
            elif entry_type == "modified":
                success = self._generate_modified_entry(all_terms)
            elif entry_type == "complex":
                success = self._generate_complex_entry(all_terms)
            elif entry_type == "comparison":
                success = self._generate_comparison_entry(all_terms)
            elif entry_type == "scenario":
                success = self._generate_scenario_entry(all_terms)
            else:
                success = False
            
            if success:
                generated += 1
                pbar.update(1)
    
    def _generate_basic_entry(self, all_terms: List[Tuple[str, str]]) -> bool:
        """Generate a basic question-answer entry"""
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
            return True
        return False
    
    def _generate_modified_entry(self, all_terms: List[Tuple[str, str]]) -> bool:
        """Generate a question with context modifiers"""
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
            return True
        return False
    
    def _generate_complex_entry(self, all_terms: List[Tuple[str, str]]) -> bool:
        """Generate a complex question about a single term"""
        term_entry = random.choice(all_terms)
        term, definition = term_entry
        
        # Filter templates to exclude comparison questions
        templates = [t for t in self.complex_question_templates if "{term1}" not in t and "{term2}" not in t]
        if not templates:
            return False
        
        template = random.choice(templates)
        
        instruction = template.format(term=term)
        
        # Determine which generator function to use based on the template
        generator_type = self._determine_generator_type(template)
        output = self.response_generators[generator_type](term, definition)
        
        if instruction not in self.existing_instructions:
            self.dataset.append({
                "instruction": instruction,
                "output": output
            })
            self.existing_instructions.add(instruction)
            return True
        return False
    
    def _generate_comparison_entry(self, all_terms: List[Tuple[str, str]]) -> bool:
        """Generate a comparison question between two terms"""
        if len(all_terms) < 2:
            return False
            
        term1_entry = random.choice(all_terms)
        term2_entry = random.choice(all_terms)
        attempts = 0
        while term1_entry == term2_entry and attempts < 10:
            term2_entry = random.choice(all_terms)
            attempts += 1
        
        if term1_entry == term2_entry:
            return False
        
        term1, def1 = term1_entry
        term2, def2 = term2_entry
        
        # Find comparison templates
        templates = [t for t in self.complex_question_templates if "{term1}" in t and "{term2}" in t]
        if not templates:
            return False
        
        template = random.choice(templates)
        
        instruction = template.format(term1=term1, term2=term2)
        output = self._generate_comparison(term1, def1, term2, def2)
        
        if instruction not in self.existing_instructions:
            self.dataset.append({
                "instruction": instruction,
                "output": output
            })
            self.existing_instructions.add(instruction)
            return True
        return False
    
    def _generate_scenario_entry(self, all_terms: List[Tuple[str, str]]) -> bool:
        """Generate a scenario-based question"""
        term_entry = random.choice(all_terms)
        term, definition = term_entry
        
        if not self.scenario_templates:
            return False
            
        template = random.choice(self.scenario_templates)
        instruction = template.format(term=term)
        
        output = self._generate_scenario_response(term, definition, instruction)
        
        if instruction not in self.existing_instructions:
            self.dataset.append({
                "instruction": instruction,
                "output": output
            })
            self.existing_instructions.add(instruction)
            return True
        return False
    
    def _determine_generator_type(self, template: str) -> str:
        """Determine which generator function to use based on the template"""
        template_lower = template.lower()
        
        if "requirements" in template_lower:
            return "requirements"
        elif "process" in template_lower:
            return "process"
        elif "benefits" in template_lower:
            return "benefits"
        elif "eligibility criteria" in template_lower:
            return "eligibility"
        elif "calculated" in template_lower:
            return "calculation"
        elif "factors" in template_lower:
            return "factors"
        elif "when would someone use" in template_lower:
            return "use_cases"
        elif "key features" in template_lower:
            return "features"
        elif "documentation" in template_lower:
            return "documentation"
        elif "impact" in template_lower:
            return "impact"
        else:
            return "scenario"  # Default to scenario response
    
    def _generate_requirements(self, term: str, definition: str) -> str:
        """Generate requirements for a term using templates"""
        category = self._determine_category(definition)
        response_templates = self.config.get("response_templates", {}).get("requirements", {})
        template_key = next((k for k in response_templates if k in category), "default")
        
        templates = response_templates.get(template_key, [])
        if not templates:
            templates = [
                "Adherence to Fannie Mae's published guidelines in the Selling Guide.",
                "Proper documentation to verify borrower eligibility and property condition.",
                "Compliance with all applicable federal, state, and local regulations.",
                "Integration with existing systems and processes to maintain data integrity."
            ]
        
        requirements = f"The requirements for {term} in Fannie Mae mortgage lending include:\n\n"
        
        # Select 4-6 requirement templates
        num_requirements = random.randint(4, 6)
        selected_templates = random.sample(templates, min(num_requirements, len(templates)))
        
        for i, template in enumerate(selected_templates, 1):
            requirements += f"{i}. {template}\n\n"
        
        requirements += f"These requirements ensure that {term} is implemented properly and consistently across the mortgage finance system, maintaining Fannie Mae's standards for quality, compliance, and risk management."
        
        return requirements
    
    def _generate_process(self, term: str, definition: str) -> str:
        """Generate process description for a term using templates"""
        category = self._determine_category(definition)
        response_templates = self.config.get("response_templates", {}).get("process", {})
        template_key = next((k for k in response_templates if k in category), "default")
        
        templates = response_templates.get(template_key, [])
        if not templates:
            templates = [
                "Assessment: Evaluate current processes and systems to determine implementation approach.",
                "Planning: Develop a comprehensive plan including timeline and resource requirements.",
                "Development: Create or modify necessary policies, procedures, and systems.",
                "Testing: Validate that the implementation meets all requirements and performs as expected."
            ]
        
        process = f"The process for {term} in Fannie Mae mortgage lending typically follows these steps:\n\n"
        
        # Select all available process steps
        selected_templates = templates[:min(8, len(templates))]
        
        for i, template in enumerate(selected_templates, 1):
            process += f"{i}. {template}\n\n"
        
        process += f"This process ensures that {term} is handled efficiently and in compliance with Fannie Mae guidelines and regulatory requirements."
        
        return process
    
    def _generate_benefits(self, term: str, definition: str) -> str:
        """Generate benefits for a term"""
        benefits = f"The benefits of {term} in Fannie Mae mortgage lending include:\n\n"
        
        # Generate 5-7 benefits
        num_benefits = random.randint(5, 7)
        
        benefit_templates = [
            f"Enhanced liquidity in the mortgage market, allowing lenders to extend more credit to qualified borrowers.",
            f"Standardization of mortgage practices, leading to greater efficiency and consistency.",
            f"Reduced risk for lenders through Fannie Mae's guarantee on qualifying loans.",
            f"Potentially lower interest rates for borrowers due to the secondary market efficiencies.",
            f"Increased access to homeownership for qualified borrowers.",
            f"Simplified loan processing through standardized guidelines and technology.",
            f"Greater stability in the housing finance system.",
            f"Support for affordable housing initiatives.",
            f"Flexibility for lenders in managing their mortgage portfolios.",
            f"Transparency in mortgage lending practices."
        ]
        
        selected_benefits = random.sample(benefit_templates, min(num_benefits, len(benefit_templates)))
        
        for i, benefit in enumerate(selected_benefits, 1):
            benefits += f"{i}. {benefit}\n\n"
        
        benefits += f"These benefits contribute to a more efficient, accessible, and stable housing finance system, which is a core part of Fannie Mae's mission."
        
        return benefits
    
    def _generate_eligibility(self, term: str, definition: str) -> str:
        """Generate eligibility criteria for a term"""
        eligibility = f"The eligibility criteria for {term} in Fannie Mae mortgage lending typically include:\n\n"
        
        # Generate 5-7 eligibility criteria
        num_criteria = random.randint(5, 7)
        
        criteria_templates = [
            f"Minimum credit score requirements, generally 620 or higher depending on the specific program.",
            f"Debt-to-income ratio limits, typically not exceeding 45% for most borrowers.",
            f"Loan-to-value ratio constraints based on property type, occupancy, and transaction type.",
            f"Property must meet Fannie Mae's property standards and appraisal requirements.",
            f"Borrower must have stable and documentable income sufficient to support the mortgage payment.",
            f"Property must be a residential dwelling that meets Fannie Mae's eligibility guidelines.",
            f"Loan amount must not exceed the current conforming loan limits set by FHFA.",
            f"Borrower must meet citizenship or eligible non-citizen status requirements.",
            f"Property must be located in the United States, its territories, or possessions.",
            f"Loan purpose must be eligible under Fannie Mae guidelines (purchase, refinance, etc.)."
        ]
        
        selected_criteria = random.sample(criteria_templates, min(num_criteria, len(criteria_templates)))
        
        for i, criterion in enumerate(selected_criteria, 1):
            eligibility += f"{i}. {criterion}\n\n"
        
        eligibility += f"These criteria help ensure that loans associated with {term} meet Fannie Mae's risk management standards and align with responsible lending practices."
        
        return eligibility
    
    def _generate_calculation(self, term: str, definition: str) -> str:
        """Generate calculation explanation for a term"""
        calculation = f"The calculation of {term} in Fannie Mae mortgage lending involves the following steps:\n\n"
        
        # Generate 4-6 calculation steps
        num_steps = random.randint(4, 6)
        
        calculation_templates = [
            f"Gathering all necessary data inputs from loan application, credit reports, and property documentation.",
            f"Applying the appropriate formula or algorithm as specified in Fannie Mae guidelines.",
            f"Adjusting for any risk factors that may impact the calculation.",
            f"Validating the results against established thresholds and benchmarks.",
            f"Documenting the calculation methodology and results for audit purposes.",
            f"Incorporating the calculation into the overall underwriting decision.",
            f"Reviewing for any exceptions or special circumstances that may require manual adjustment.",
            f"Ensuring compliance with all regulatory requirements related to the calculation."
        ]
        
        selected_steps = random.sample(calculation_templates, min(num_steps, len(calculation_templates)))
        
        for i, step in enumerate(selected_steps, 1):
            calculation += f"{i}. {step}\n\n"
        
        calculation += f"The accurate calculation of {term} is essential for proper risk assessment and compliance with Fannie Mae guidelines."
        
        return calculation
    
    def _generate_factors(self, term: str, definition: str) -> str:
        """Generate factors affecting a term"""
        factors = f"Several key factors affect {term} in Fannie Mae mortgage lending:\n\n"
        
        # Generate 5-7 factors
        num_factors = random.randint(5, 7)
        
        factor_templates = [
            f"Economic conditions, including interest rates, inflation, and employment trends.",
            f"Housing market dynamics, such as supply and demand, home price appreciation, and regional variations.",
            f"Regulatory environment and changes in laws affecting mortgage lending.",
            f"Borrower characteristics, including credit profile, income stability, and debt obligations.",
            f"Property characteristics, including type, location, condition, and value.",
            f"Loan characteristics, such as loan-to-value ratio, loan purpose, and loan term.",
            f"Fannie Mae policy changes and updates to underwriting guidelines.",
            f"Technological advancements in mortgage origination and servicing.",
            f"Secondary market conditions and investor appetite for mortgage-backed securities.",
            f"Risk management practices and models employed by lenders and Fannie Mae."
        ]
        
        selected_factors = random.sample(factor_templates, min(num_factors, len(factor_templates)))
        
        for i, factor in enumerate(selected_factors, 1):
            factors += f"{i}. {factor}\n\n"
        
        factors += f"Understanding these factors is crucial for effectively implementing and managing {term} within the Fannie Mae mortgage ecosystem."
        
        return factors
    
    def _generate_use_cases(self, term: str, definition: str) -> str:
        """Generate use cases for a term"""
        use_cases = f"Common scenarios when someone would use {term} in Fannie Mae mortgage lending include:\n\n"
        
        # Generate 4-6 use cases
        num_cases = random.randint(4, 6)
        
        case_templates = [
            f"When a lender is evaluating a borrower's eligibility for a conventional mortgage loan.",
            f"During the loan origination process to ensure compliance with Fannie Mae guidelines.",
            f"When assessing the risk profile of a potential mortgage transaction.",
            f"In the secondary market when packaging loans into mortgage-backed securities.",
            f"During loan servicing to manage borrower interactions and loan performance.",
            f"When implementing loss mitigation strategies for struggling borrowers.",
            f"During the development of new mortgage products aligned with Fannie Mae standards.",
            f"When analyzing portfolio performance and making strategic business decisions.",
            f"In regulatory reporting and compliance activities.",
            f"During training and education for mortgage professionals."
        ]
        
        selected_cases = random.sample(case_templates, min(num_cases, len(case_templates)))
        
        for i, case in enumerate(selected_cases, 1):
            use_cases += f"{i}. {case}\n\n"
        
        use_cases += f"{term} is an integral part of the mortgage lending process, providing structure and guidance for lenders operating within the Fannie Mae ecosystem."
        
        return use_cases
    
    def _generate_features(self, term: str, definition: str) -> str:
        """Generate key features for a term"""
        features = f"The key features of {term} in Fannie Mae mortgage lending include:\n\n"
        
        # Generate 5-7 features
        num_features = random.randint(5, 7)
        
        feature_templates = [
            f"Standardization across the mortgage industry to ensure consistency and efficiency.",
            f"Integration with Fannie Mae's automated underwriting systems for streamlined processing.",
            f"Regular updates to reflect changing market conditions and regulatory requirements.",
            f"Clear documentation in Fannie Mae's Selling and Servicing Guides.",
            f"Support through Fannie Mae's lender training and education resources.",
            f"Alignment with Fannie Mae's mission to promote affordable housing and sustainable homeownership.",
            f"Risk management controls to protect the interests of borrowers, lenders, and investors.",
            f"Technological enablement through Fannie Mae's suite of digital tools.",
            f"Flexibility to accommodate various borrower situations within defined parameters.",
            f"Transparency in implementation and application across the mortgage finance system."
        ]
        
        selected_features = random.sample(feature_templates, min(num_features, len(feature_templates)))
        
        for i, feature in enumerate(selected_features, 1):
            features += f"{i}. {feature}\n\n"
        
        features += f"These features make {term} an essential component of Fannie Mae's approach to maintaining a liquid, efficient, and responsible housing finance market."
        
        return features
    
    def _generate_documentation(self, term: str, definition: str) -> str:
        """Generate documentation requirements for a term"""
        documentation = f"The documentation required for {term} in Fannie Mae mortgage lending typically includes:\n\n"
        
        # Generate 5-7 documentation requirements
        num_docs = random.randint(5, 7)
        
        doc_templates = [
            f"Completed and signed loan application (Form 1003).",
            f"Credit reports and verification of credit history.",
            f"Income verification documents such as pay stubs, W-2s, tax returns, or employment verification.",
            f"Asset documentation including bank statements and verification of deposits.",
            f"Property appraisal or other valuation documentation.",
            f"Title report and property insurance information.",
            f"Verification of mortgage or rent payment history.",
            f"Purchase agreement for purchase transactions.",
            f"Explanation letters for credit events or unique circumstances.",
            f"Compliance documentation such as Truth in Lending disclosures and Loan Estimate."
        ]
        
        selected_docs = random.sample(doc_templates, min(num_docs, len(doc_templates)))
        
        for i, doc in enumerate(selected_docs, 1):
            documentation += f"{i}. {doc}\n\n"
        
        documentation += f"Proper documentation is essential for verifying compliance with Fannie Mae's requirements for {term} and ensuring loan quality."
        
        return documentation
    
    def _generate_impact(self, term: str, definition: str) -> str:
        """Generate impact assessment for a term"""
        impact = f"The impact of {term} on loan eligibility and mortgage processes includes:\n\n"
        
        # Generate 4-6 impact points
        num_points = random.randint(4, 6)
        
        impact_templates = [
            f"Determining whether a loan meets Fannie Mae's eligibility requirements for purchase or guarantee.",
            f"Influencing the interest rate and terms offered to borrowers based on risk assessment.",
            f"Affecting the documentation requirements and verification processes for loan approval.",
            f"Impacting the timeline for loan processing and closing.",
            f"Determining the need for mortgage insurance and other credit enhancements.",
            f"Influencing servicing practices and loss mitigation options if the loan becomes delinquent.",
            f"Affecting the marketability and pricing of loans in the secondary market.",
            f"Influencing the capital requirements and risk management strategies of lenders."
        ]
        
        selected_impacts = random.sample(impact_templates, min(num_points, len(impact_templates)))
        
        for i, impact_point in enumerate(selected_impacts, 1):
            impact += f"{i}. {impact_point}\n\n"
        
        impact += f"Understanding the impact of {term} helps lenders, borrowers, and other stakeholders navigate the mortgage process more effectively and make informed decisions."
        
        return impact
    
    def _generate_comparison(self, term1: str, def1: str, term2: str, def2: str) -> str:
        """Generate a comparison between two terms"""
        # Use template-based approach for comparisons
        category1 = self._determine_category(def1)
        category2 = self._determine_category(def2)
        
        comparison = f"{term1} and {term2} are both important concepts in mortgage finance, but they differ in several key ways.\n\n"
        
        # Add definition of first term
        comparison += f"{term1}: {def1}\n\n"
        
        # Add definition of second term
        comparison += f"{term2}: {def2}\n\n"
        
        # Add key differences
        comparison += "Key differences:\n\n"
        
        # Generate differences based on definitions
        def1_sentences = def1.split('. ')
        def2_sentences = def2.split('. ')
        
        if len(def1_sentences) > 0 and len(def2_sentences) > 0:
            comparison += f"1. Purpose: {term1} primarily relates to {def1_sentences[0].lower()}, while {term2} focuses on {def2_sentences[0].lower()}\n\n"
        
        comparison += f"2. Application: {term1} is typically used in {random.choice(['loan origination', 'underwriting', 'servicing', 'secondary market', 'regulatory compliance'])}, whereas {term2} is more commonly associated with {random.choice(['risk assessment', 'loan pricing', 'investor reporting', 'portfolio management', 'loss mitigation'])}\n\n"
        
        comparison += f"3. Stakeholders: {term1} primarily affects {random.choice(['lenders', 'borrowers', 'investors', 'servicers', 'regulators'])}, while {term2} is more relevant to {random.choice(['lenders', 'borrowers', 'investors', 'servicers', 'regulators'])}\n\n"
        
        # Add relationship between terms
        if category1 == category2:
            comparison += f"Both {term1} and {term2} are related to {self.categories.get(category1, 'mortgage finance')}, but they serve different functions within this domain."
        else:
            comparison += f"While {term1} falls under the domain of {self.categories.get(category1, 'mortgage finance')}, {term2} is more closely associated with {self.categories.get(category2, 'mortgage finance')}."
        
        return comparison
    
    def _generate_scenario_response(self, term: str, definition: str, scenario: str = None) -> str:
        """Generate a response to a scenario-based question"""
        category = self._determine_category(definition)
        response_templates = self.config.get("response_templates", {}).get("scenario", {})
        
        # Fix for the NoneType error - check if scenario is None before calling lower()
        if scenario is not None:
            template_key = next((k for k in response_templates if k in category or (k in scenario.lower())), "default")
        else:
            template_key = next((k for k in response_templates if k in category), "default")
        
        templates = response_templates.get(template_key, [])
        if not templates:
            templates = [
                "**Application**: {term} applies to this situation in the following ways: It affects eligibility and qualification standards.",
                "**Compliance and Guidelines**: When working with {term}, ensure adherence to Fannie Mae Selling Guide requirements.",
                "**Communication Strategy**: Effectively communicate about {term} by using clear language appropriate for your audience.",
                "**Next Steps**: To properly address {term} in this scenario, gather all relevant information and documentation.",
                "**Risk Mitigation**: Identify potential risks associated with {term} in this context and develop appropriate strategies."
            ]
        
        response = f"When addressing {term} in this scenario, consider the following key points:\n\n"
        response += f"**Understanding {term}**:\n{definition}\n\n"
        
        # Analyze the scenario to determine the appropriate response structure
        response_type = "default"
        if scenario is not None:
            if "lender" in scenario.lower() or "loan officer" in scenario.lower():
                response_type = "lender"
            elif "training" in scenario.lower() or "presentation" in scenario.lower():
                response_type = "training"
            elif "impact" in scenario.lower() or "affect" in scenario.lower():
                response_type = "impact"
        
        # Select 3-4 templates for the response
        num_points = random.randint(3, 4)
        available_templates = templates
        if len(available_templates) < num_points:
            # Add some generic templates if we don't have enough
            additional_templates = [
                "**Key Consideration**: When evaluating {term}, focus on how it aligns with Fannie Mae's current guidelines and requirements.",
                "**Practical Implementation**: Apply {term} by following established industry practices and Fannie Mae's documentation requirements.",
                "**Common Challenges**: Be aware that {term} may present challenges related to documentation, timing, or eligibility determinations.",
                "**Future Outlook**: Consider how recent trends and policy directions might affect {term} in the coming months."
            ]
            available_templates.extend(additional_templates)
        
        selected_templates = random.sample(available_templates, min(num_points, len(available_templates)))
        
        response += "**Key Considerations for This Scenario**:\n\n"
        for i, template in enumerate(selected_templates, 1):
            response += f"{template.format(term=term)}\n\n"
        
        response += f"By carefully considering these aspects of {term}, you'll be better equipped to address this situation effectively while ensuring compliance with Fannie Mae requirements and industry best practices."
        
        return response
    
    def save_dataset(self, output_dir: str, filename_prefix: str) -> None:
        """Save the dataset to JSONL files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the complete dataset
        complete_path = os.path.join(output_dir, f"{filename_prefix}_{len(self.dataset)}.jsonl")
        with open(complete_path, 'w', encoding='utf-8') as f:
            for entry in self.dataset:
                f.write(json.dumps(entry) + '\n')
        
        print(f"Saved complete dataset with {len(self.dataset)} entries to {complete_path}")
        
        # Save sample datasets of different sizes
        sample_sizes = [1000, 5000, 10000]
        for size in sample_sizes:
            if len(self.dataset) >= size:
                sample_path = os.path.join(output_dir, f"{filename_prefix}_sample_{size}.jsonl")
                with open(sample_path, 'w', encoding='utf-8') as f:
                    for entry in random.sample(self.dataset, size):
                        f.write(json.dumps(entry) + '\n')
                print(f"Saved sample dataset with {size} entries to {sample_path}")


def main():
    """Main function to run the dataset generator"""
    parser = argparse.ArgumentParser(description="Generate a Fannie Mae mortgage knowledge dataset")
    parser.add_argument("--count", type=int, default=250000, help="Number of instruction-output pairs to generate")
    parser.add_argument("--output", type=str, default="output", help="Output directory for dataset files")
    parser.add_argument("--prefix", type=str, default="fannie_mae", help="Prefix for output filenames")
    parser.add_argument("--config", type=str, default="config", help="Path to configuration directory")
    parser.add_argument("--input", type=str, nargs="*", default=[], help="Input JSONL files to load existing data")
    
    args = parser.parse_args()
    
    generator = FannieMaeDatasetGenerator(args.config)
    
    if args.input:
        generator.load_existing_data(args.input)
    
    generator.generate_dataset(args.count)
    generator.save_dataset(args.output, args.prefix)
    
    print("Dataset generation complete.")


if __name__ == "__main__":
    main()