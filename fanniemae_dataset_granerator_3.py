#!/usr/bin/env python3
"""
Simple Fannie Mae Dataset Generator
"""
import json
import random
import os

# Load mortgage terms
with open("config/mortgage_terms.json", "r") as f:
    mortgage_terms = json.load(f)

# Load templates
with open("config/question_templates.json", "r") as f:
    question_templates = json.load(f)

with open("config/modifier_templates.json", "r") as f:
    modifier_templates = json.load(f)

# Define output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Generate dataset
dataset = []
target_count = 100000

# Simple definition questions
for term, definition in mortgage_terms:
    for template in question_templates:
        dataset.append({
            "instruction": template.format(term=term),
            "output": definition
        })

# Questions with modifiers
for term, definition in mortgage_terms:
    for template in question_templates:
        for modifier in modifier_templates:
            dataset.append({
                "instruction": template.format(term=f"{term} {modifier}"),
                "output": definition
            })

# Shuffle and limit the dataset
random.shuffle(dataset)
dataset = dataset[:target_count]

# Save the dataset
output_file = os.path.join(output_dir, f"fannie_mae_simple_{len(dataset)}.jsonl")
with open(output_file, "w") as f:
    for entry in dataset:
        f.write(json.dumps(entry) + "\n")

print(f"Generated {len(dataset)} entries in {output_file}")