#!/usr/bin/env python3
"""
Evaluate a HuggingFace model on remote instance.

This script downloads a model, tests tokenization and inference,
and reports results.
"""
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def evaluate_model(model_name: str, test_text: str = "Hello, how are you today?"):
    """
    Download and evaluate a model.
    
    Args:
        model_name: HuggingFace model name
        test_text: Text to use for testing
    """
    print(f"Evaluating model: {model_name}")
    print("=" * 60)
    
    # Load tokenizer
    print("Loading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f"  [OK] Tokenizer loaded (vocab size: {len(tokenizer)}")
    except Exception as e:
        print(f"  [ERROR] Failed to load tokenizer: {e}")
        return False
    
    # Load model
    print("Loading model...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        print(f"  [OK] Model loaded")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            device = "cuda"
            print(f"  [OK] Model on GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            print(f"  [WARNING] Using CPU")
    except Exception as e:
        print(f"  [ERROR] Failed to load model: {e}")
        return False
    
    # Test tokenization
    print(f"\nTesting tokenization...")
    print(f"  Input text: {test_text}")
    
    try:
        inputs = tokenizer(test_text, return_tensors="pt")
        if device == "cuda":
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        print(f"  [OK] Tokenized")
        print(f"  Token IDs: {inputs['input_ids'].tolist()}")
        
        # Decode back
        decoded = tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)
        print(f"  Decoded: {decoded}")
    except Exception as e:
        print(f"  [ERROR] Tokenization failed: {e}")
        return False
    
    # Test inference
    print(f"\nTesting inference...")
    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id if tokenizer.pad_token_id is None else tokenizer.pad_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"  [OK] Inference complete")
        print(f"  Generated: {generated_text}")
        print(f"  Output shape: {outputs.shape}")
    except Exception as e:
        print(f"  [ERROR] Inference failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[OK] Model evaluation complete!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluate_model.py <model_name> [test_text]")
        sys.exit(1)
    
    model_name = sys.argv[1]
    test_text = sys.argv[2] if len(sys.argv) > 2 else "Hello, how are you today?"
    
    success = evaluate_model(model_name, test_text)
    sys.exit(0 if success else 1)

