#!/usr/bin/env python3
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
                formatted += f"### Human: {content}\n"
            elif role == 'assistant':
                formatted += f"### Assistant: {content}\n"
        
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
