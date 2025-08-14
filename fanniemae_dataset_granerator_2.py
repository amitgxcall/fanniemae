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
        self.mortgage_industry_terms = self.config["mortgage_industry_terms"]
        
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
                config[key] = self._get_embedded_config()[key]
        
        return config
    
    def _get_embedded_config(self) -> Dict[str, Any]:
        """Return embedded configuration if external config files are not available"""
        # This is a simplified version - in a real implementation, you would include all the 
        # category definitions, templates, and terms here
        return {
            "categories": {
                "company_info": "Fannie Mae company information and business operations",
                "single_family": "Fannie Mae single-family mortgage lending and homeownership",
                # ... rest of categories
            },
            "question_templates": [
                "What is {term}?",
                "Define {term}.",
                # ... rest of question templates
            ],
            "complex_question_templates": [
                "How does {term1} differ from {term2}?",
                "What are the requirements for {term}?",
                # ... rest of complex question templates
            ],
            "modifier_templates": [
                "in the context of Fannie Mae",
                "according to Fannie Mae guidelines",
                # ... rest of modifier templates
            ],
            "scenario_templates": [
                "I'm a lender working with a borrower who has a 650 credit score. How would {term} affect their loan application?",
                # ... rest of scenario templates
            ],
            "mortgage_industry_terms": [
                ["Fannie Mae", "Fannie Mae (Federal National Mortgage Association) is a government-sponsored enterprise that purchases mortgages from lenders, packages them into mortgage-backed securities, and sells them to investors, providing liquidity to the mortgage market."],
                # ... rest of mortgage industry terms
            ],
            "response_templates": {
                "requirements": {
                    "underwriting": [
                        "1. Borrower qualification criteria including credit score minimums (typically 620 or higher), debt-to-income ratios (generally not exceeding 45%), and employment verification.",
                        # ... more templates
                    ],
                    # ... templates for other categories
                },
                # ... templates for other response types
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
        
        # Return the category with the highest score
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def generate_dataset(self, target_count: int) -> None:
        """Generate a dataset with the specified number of entries"""
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
        
        while len(self.dataset) < (len(self.dataset) + count) and attempts < max_attempts and generated < count:
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
        term1_entry = random.choice(all_terms)
        term2_entry = random.choice(all_terms)
        while term1_entry == term2_entry:
            term2_entry = random.choice(all_terms)
        
        term1, def1 = term1_entry
        term2, def2 = term2_entry
        
        # Find comparison templates
        templates = [t for t in self.complex_question_templates if "{term1}" in t and "{term2}" in t]
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
        comparison += "Key differences:\n"
        
        # Generate differences based on definitions
        def1_sentences = def1.split('. ')
        def2_sentences = def2.split('. ')
        
        if len(def1_sentences) > 0 and len(def2_sentences) > 0:
            comparison += f"1. Purpose: {term1} primarily relates to {def1_sentences[0].lower()}, while {term2} focuses on {def2_sentences[0].lower()}\n"
        
        comparison += f"2. Application: {term1} is typically used in {random.choice(['loan origination', 'underwriting', 'servicing', 'secondary market', 'regulatory compliance'])}, whereas {term2} is more commonly associated with {random.choice(['risk assessment', 'loan pricing', 'investor reporting', 'portfolio management', 'loss mitigation'])}\n"
        
        comparison += f"3. Stakeholders: {term1} primarily affects {random.choice(['lenders', 'borrowers', 'investors', 'servicers', 'regulators'])}, while {term2} is more relevant to {random.choice(['lenders', 'borrowers', 'investors', 'servicers', 'regulators'])}\n"
        
        # Add relationship between terms
        if category1 == category2:
            comparison += f"\nBoth {term1} and {term2} are related to {self.categories[category1].lower()}, but they serve different functions within this domain."
        else:
            comparison += f"\nWhile {term1} falls under the domain of {self.categories[category1].lower()}, {term2} is more closely associated with {self.categories[category2].lower()}."
        
        return comparison
    
    def _generate_requirements(self, term: str, definition: str) -> str:
        """Generate requirements for a term using templates"""
        category = self._determine_category(definition)
        template_key = next((k for k in self.config["response_templates"]["requirements"] if k in category), "default")
        
        templates = self.config["response_templates"]["requirements"][template_key]
        
        requirements = f"The requirements for {term} in Fannie Mae mortgage lending include:\n\n"
        
        # Select 4-6 requirement templates
        num_requirements = random.randint(4, 6)
        selected_templates = random.sample(templates, min(num_requirements, len(templates)))
        
        for i, template in enumerate(selected_templates, 1):
            requirements += f"{i}. {template}\n\n"
        
        requirements += f"These requirements ensure that {term} is implemented properly and consistently across the mortgage finance system, maintaining Fannie Mae's standards for quality, compliance, and risk management."
        
        return requirements
    
    # Similar implementation for other generator methods using templates
    # _generate_process, _generate_benefits, etc.
    
    def _generate_scenario_response(self, term: str, definition: str, scenario: str) -> str:
        """Generate a response to a scenario-based question"""
        category = self._determine_category(definition)
        template_key = next((k for k in self.config["response_templates"]["scenario"] if k in category), "default")
        
        response = f"When addressing {term} in this scenario, consider the following key points:\n\n"
        response += f"**Understanding {term}**:\n{definition}\n\n"
        
        # Analyze the scenario to determine the appropriate response structure
        if "lender" in scenario.lower() or "loan officer" in scenario.lower():
            templates = self.config["response_templates"]["scenario"]["lender"]
        elif "training" in scenario.lower() or "presentation" in scenario.lower():
            templates = self.config["response_templates"]["scenario"]["training"]
        elif "impact" in scenario.lower() or "affect" in scenario.lower():
            templates = self.config["response_templates"]["scenario"]["impact"]
        else:
            templates = self.config["response_templates"]["scenario"]["default"]
        
        # Select 3-4 templates for the response
        num_points = random.randint(3, 4)
        selected_templates = random.sample(templates, min(num_points, len(templates)))
        
        response += "**Key Considerations for This Scenario**:\n"
        for i, template in enumerate(selected_templates, 1):
            response += f"{i}. {template.format(term=term)}\n\n"
        
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