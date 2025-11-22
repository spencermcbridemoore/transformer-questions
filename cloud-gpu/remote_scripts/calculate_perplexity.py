#!/usr/bin/env python3
"""
Calculate perplexity for a model on a dataset.

This script can be customized for specific perplexity evaluation tasks.
"""
import sys
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

def calculate_perplexity(model_name: str, dataset_name: str = "wikitext", dataset_config: str = "wikitext-2-raw-v1", split: str = "test", max_samples: int = 1000):
    """
    Calculate perplexity for a model on a dataset.
    
    Args:
        model_name: HuggingFace model name
        dataset_name: Dataset name from HuggingFace datasets
        dataset_config: Dataset configuration
        split: Dataset split to use
        max_samples: Maximum number of samples to evaluate
    """
    print(f"Calculating perplexity for {model_name}")
    print("=" * 60)
    
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    
    if torch.cuda.is_available():
        device = "cuda"
        print(f"  [OK] Model loaded on GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print(f"  [OK] Model loaded on CPU")
    
    model.eval()
    
    # Load dataset
    print(f"\nLoading dataset: {dataset_name}/{dataset_config}")
    try:
        dataset = load_dataset(dataset_name, dataset_config, split=split)
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
        print(f"  [OK] Loaded {len(dataset)} samples")
    except Exception as e:
        print(f"  [ERROR] Failed to load dataset: {e}")
        return None
    
    # Calculate perplexity
    print("\nCalculating perplexity...")
    total_loss = 0.0
    total_tokens = 0
    
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    batch_size = 4
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i:i+batch_size]
        texts = [item.get('text', item.get('content', '')) for item in batch]
        
        # Tokenize
        encodings = tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        if device == "cuda":
            encodings = {k: v.to(device) for k, v in encodings.items()}
        
        # Calculate loss
        with torch.no_grad():
            outputs = model(**encodings, labels=encodings['input_ids'])
            loss = outputs.loss
        
        # Accumulate
        batch_tokens = encodings['input_ids'].numel()
        total_loss += loss.item() * batch_tokens
        total_tokens += batch_tokens
        
        if (i // batch_size + 1) % 10 == 0:
            print(f"  Processed {i + len(batch)}/{len(dataset)} samples...")
    
    # Calculate final perplexity
    avg_loss = total_loss / total_tokens if total_tokens > 0 else float('inf')
    perplexity = np.exp(avg_loss)
    
    print("\n" + "=" * 60)
    print(f"Results:")
    print(f"  Average loss: {avg_loss:.4f}")
    print(f"  Perplexity: {perplexity:.4f}")
    print(f"  Total tokens: {total_tokens:,}")
    print("=" * 60)
    
    return perplexity

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python calculate_perplexity.py <model_name> [dataset_name] [max_samples]")
        print("  Example: python calculate_perplexity.py gpt2 wikitext 1000")
        sys.exit(1)
    
    model_name = sys.argv[1]
    dataset_name = sys.argv[2] if len(sys.argv) > 2 else "wikitext"
    max_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    perplexity = calculate_perplexity(model_name, max_samples=max_samples)
    if perplexity is None:
        sys.exit(1)

