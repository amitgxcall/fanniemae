#!/usr/bin/env python3
"""
Script to help fix KeyError: 'dialog' issues in LLaMA fine-tuning scripts.
Provides code examples for handling different JSONL formats.
"""

def show_data_loading_fixes():
    """Show how to fix data loading for different JSONL formats."""
    
    print("🔧 DATA LOADING FIXES FOR LLAMA FINE-TUNING")
    print("=" * 60)
    
    print("""
## OPTION 1: Fix your existing script to handle instruction-output format

### Original problematic code:
```python
# This causes KeyError: 'dialog'
dialog = data['dialog']
```

### Fixed code for instruction-output format:
```python
def load_instruction_output_data(file_path):
    conversations = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            
            # Convert instruction-output to dialog format
            conversation = {
                "dialog": [
                    {"role": "user", "content": data['instruction']},
                    {"role": "assistant", "content": data['output']}
                ]
            }
            conversations.append(conversation)
    
    return conversations
```

## OPTION 2: Flexible data loader that handles multiple formats

```python
def load_flexible_jsonl(file_path):
    conversations = []
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Handle different formats
                if 'dialog' in data:
                    # Already in dialog format
                    conversation = data
                elif 'instruction' in data and 'output' in data:
                    # Convert instruction-output to dialog
                    conversation = {
                        "dialog": [
                            {"role": "user", "content": data['instruction']},
                            {"role": "assistant", "content": data['output']}
                        ]
                    }
                elif 'conversations' in data:
                    # Vicuna/ShareGPT format
                    dialog = []
                    for conv in data['conversations']:
                        if conv['from'] == 'human':
                            dialog.append({"role": "user", "content": conv['value']})
                        elif conv['from'] == 'gpt':
                            dialog.append({"role": "assistant", "content": conv['value']})
                    conversation = {"dialog": dialog}
                elif 'messages' in data:
                    # Chat format
                    conversation = {"dialog": data['messages']}
                else:
                    print(f"Warning: Unknown format in line {line_num}")
                    continue
                
                conversations.append(conversation)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    return conversations
```

## OPTION 3: Simple format detector and converter

```python
def detect_and_convert_format(data):
    '''Detect JSONL format and convert to standard dialog format'''
    
    if 'dialog' in data:
        return data['dialog']
    elif 'instruction' in data and 'output' in data:
        return [
            {"role": "user", "content": data['instruction']},
            {"role": "assistant", "content": data['output']}
        ]
    elif 'conversations' in data:
        dialog = []
        for conv in data['conversations']:
            role = "user" if conv['from'] == 'human' else "assistant"
            dialog.append({"role": role, "content": conv['value']})
        return dialog
    elif 'messages' in data:
        return data['messages']
    else:
        raise ValueError(f"Unknown format: {list(data.keys())}")

# Usage in your fine-tuning script:
def load_data(file_path):
    conversations = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            dialog = detect_and_convert_format(data)
            conversations.append({"dialog": dialog})
    return conversations
```
""")

def create_sample_finetuning_script():
    """Create a sample fine-tuning script that handles the format correctly."""
    
    script_content = '''#!/usr/bin/env python3
"""
Sample LLaMA fine-tuning script that handles instruction-output JSONL format.
This fixes the KeyError: 'dialog' issue.
"""

import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from typing import List, Dict

class FannieMaeDataset(Dataset):
    """Dataset class that handles instruction-output format."""
    
    def __init__(self, jsonl_file: str, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.conversations = self.load_conversations(jsonl_file)
    
    def load_conversations(self, jsonl_file: str) -> List[Dict]:
        """Load and convert JSONL to dialog format."""
        conversations = []
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    
                    # Handle different formats
                    if 'dialog' in data:
                        # Already in dialog format
                        dialog = data['dialog']
                    elif 'instruction' in data and 'output' in data:
                        # Convert instruction-output to dialog format
                        dialog = [
                            {"role": "user", "content": data['instruction']},
                            {"role": "assistant", "content": data['output']}
                        ]
                    else:
                        print(f"Warning: Unknown format in line {line_num}")
                        continue
                    
                    conversations.append({"dialog": dialog})
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
        
        print(f"Loaded {len(conversations)} conversations from {jsonl_file}")
        return conversations
    
    def __len__(self):
        return len(self.conversations)
    
    def __getitem__(self, idx):
        conversation = self.conversations[idx]
        
        # Format the conversation for training
        formatted_text = self.format_conversation(conversation['dialog'])
        
        # Tokenize
        encoding = self.tokenizer(
            formatted_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }
    
    def format_conversation(self, dialog: List[Dict]) -> str:
        """Format dialog for LLaMA training."""
        formatted = ""
        
        for turn in dialog:
            role = turn['role']
            content = turn['content']
            
            if role == 'user':
                formatted += f"### Human: {content}\\n"
            elif role == 'assistant':
                formatted += f"### Assistant: {content}\\n"
        
        return formatted

def main():
    # Configuration
    model_name = "meta-llama/Llama-2-7b-hf"  # or your preferred model
    jsonl_file = "fannie_mae_master_knowledge_base.jsonl"  # Your original file
    output_dir = "./fannie_mae_finetuned_model"
    
    # Load tokenizer and model
    print("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Create dataset
    print("Creating dataset...")
    dataset = FannieMaeDataset(jsonl_file, tokenizer)
    
    # Split dataset (80% train, 20% eval)
    train_size = int(0.8 * len(dataset))
    eval_size = len(dataset) - train_size
    train_dataset, eval_dataset = torch.utils.data.random_split(
        dataset, [train_size, eval_size]
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=500,
        save_steps=1000,
        load_best_model_at_end=True,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )
    
    # Start training
    print("Starting training...")
    trainer.train()
    
    # Save the model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
'''
    
    with open('fixed_llama_finetuning.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created fixed_llama_finetuning.py")

def main():
    show_data_loading_fixes()
    
    print("\n" + "="*60)
    print("🎯 SOLUTIONS SUMMARY")
    print("="*60)
    print("""
You have 3 options to fix the KeyError: 'dialog' issue:

1. 📄 USE CONVERTED FILES:
   - Use: fannie_mae_llama_dialog.jsonl (already has 'dialog' key)
   - No code changes needed in your script

2. 🔧 FIX YOUR EXISTING SCRIPT:
   - Modify data loading to handle 'instruction'/'output' format
   - See code examples above

3. 💾 USE THE SAMPLE SCRIPT:
   - Use the generated fixed_llama_finetuning.py
   - Handles multiple formats automatically

RECOMMENDED: Use option 1 with fannie_mae_llama_dialog.jsonl
""")
    
    create_sample_finetuning_script()
    
    print(f"\n📋 FILES CREATED:")
    print(f"  ✅ fannie_mae_llama_dialog.jsonl (LLaMA format)")
    print(f"  ✅ fannie_mae_alpaca_format.jsonl (Alpaca format)")
    print(f"  ✅ fannie_mae_vicuna_format.jsonl (Vicuna format)")
    print(f"  ✅ fannie_mae_chat_format.jsonl (Chat format)")
    print(f"  ✅ fixed_llama_finetuning.py (Sample script)")

if __name__ == "__main__":
    main()