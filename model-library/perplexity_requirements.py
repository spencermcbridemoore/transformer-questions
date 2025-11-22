#!/usr/bin/env python3
"""
Analyze computational demands for running PyTorch perplexity evaluation.

Perplexity calculation requires:
1. Loading model in PyTorch
2. Running inference on evaluation dataset
3. Calculating log probabilities
4. Aggregating results
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import MODEL_PAIRS, get_model_info

def estimate_memory_requirements(model_name: str, batch_size: int = 8, seq_length: int = 512):
    """
    Estimate memory requirements for perplexity evaluation.
    
    Memory needed = Model weights + Activations + KV cache + Batch data
    
    Rough estimates:
    - Model weights: ~4 bytes per parameter (FP32) or ~2 bytes (FP16/BF16)
    - Activations: batch_size * seq_length * hidden_size * num_layers * 2 bytes
    - KV cache: batch_size * seq_length * hidden_size * num_layers * 2 * 2 bytes
    - Batch data: batch_size * seq_length * 4 bytes (tokens)
    """
    info = get_model_info(model_name)
    
    if not info['size']:
        return {
            'model': model_name,
            'size': 'Unknown',
            'note': 'Cannot estimate - check HuggingFace for model size'
        }
    
    size_b = info['size']  # Billions of parameters
    
    # Memory estimates (in GB)
    # Using FP16/BF16 (common for inference)
    model_memory_fp16 = size_b * 2  # 2 bytes per parameter
    model_memory_fp32 = size_b * 4  # 4 bytes per parameter
    
    # Activation memory (rough estimate)
    # More realistic: hidden_size and layers scale with model size
    # Typical: 7B model has ~4096 hidden_size, 32 layers
    # Rough scaling: hidden_size ~= 1000 * sqrt(size_b), layers ~= 8 * sqrt(size_b)
    hidden_size_approx = int(1000 * (size_b ** 0.5))
    num_layers_approx = max(12, int(8 * (size_b ** 0.5)))
    
    # Activation memory per forward pass (in GB)
    # activations = batch * seq * hidden * layers * 2 bytes (FP16)
    activation_memory = (batch_size * seq_length * hidden_size_approx * num_layers_approx * 2) / 1e9
    
    # KV cache memory (for attention) - typically 2x activations
    kv_cache_memory = activation_memory * 2
    
    # Batch data memory
    batch_data_memory = (batch_size * seq_length * 4) / 1e9
    
    # Total memory estimates
    total_fp16 = model_memory_fp16 + activation_memory + kv_cache_memory + batch_data_memory + 2  # +2GB overhead
    total_fp32 = model_memory_fp32 + activation_memory + kv_cache_memory + batch_data_memory + 2
    
    return {
        'model': model_name,
        'size': f"{info['size_str']} ({size_b}B params)",
        'family': info['family'],
        'batch_size': batch_size,
        'seq_length': seq_length,
        'model_memory_fp16_gb': round(model_memory_fp16, 2),
        'model_memory_fp32_gb': round(model_memory_fp32, 2),
        'activation_memory_gb': round(activation_memory, 2),
        'kv_cache_memory_gb': round(kv_cache_memory, 2),
        'total_fp16_gb': round(total_fp16, 2),
        'total_fp32_gb': round(total_fp32, 2),
        'fits_a100_40gb_fp16': total_fp16 <= 40,
        'fits_a100_80gb_fp16': total_fp16 <= 80,
        'fits_a100_40gb_fp32': total_fp32 <= 40,
        'fits_a100_80gb_fp32': total_fp32 <= 80,
    }

def estimate_compute_time(model_name: str, dataset_size: int = 1000, batch_size: int = 8, seq_length: int = 512):
    """
    Estimate compute time for perplexity evaluation.
    
    Rough estimates based on typical inference speeds:
    - Small models (0.5-3B): ~50-100 tokens/sec on A100
    - Medium models (7-14B): ~20-50 tokens/sec on A100
    - Large models (32B+): ~5-20 tokens/sec on A100
    """
    info = get_model_info(model_name)
    
    if not info['size']:
        return {
            'model': model_name,
            'note': 'Cannot estimate - check HuggingFace for model size'
        }
    
    size_b = info['size']
    
    # Rough tokens/sec estimates for A100
    if size_b <= 1:
        tokens_per_sec = 100
    elif size_b <= 3:
        tokens_per_sec = 80
    elif size_b <= 7:
        tokens_per_sec = 50
    elif size_b <= 14:
        tokens_per_sec = 30
    elif size_b <= 32:
        tokens_per_sec = 15
    else:
        tokens_per_sec = 5
    
    # Total tokens to process
    total_tokens = dataset_size * seq_length
    
    # Time estimates
    total_seconds = total_tokens / (tokens_per_sec * batch_size)
    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    
    return {
        'model': model_name,
        'size': f"{info['size_str']} ({size_b}B params)",
        'dataset_size': dataset_size,
        'batch_size': batch_size,
        'seq_length': seq_length,
        'total_tokens': total_tokens,
        'estimated_tokens_per_sec': tokens_per_sec,
        'estimated_time_seconds': round(total_seconds, 1),
        'estimated_time_minutes': round(total_minutes, 1),
        'estimated_time_hours': round(total_hours, 2),
    }

if __name__ == '__main__':
    print("=" * 90)
    print("PyTorch Perplexity Evaluation Requirements")
    print("=" * 90)
    
    print("\nPerplexity evaluation requires:")
    print("  1. Model loaded in GPU memory")
    print("  2. Running inference on evaluation dataset")
    print("  3. Calculating log probabilities for each token")
    print("  4. Aggregating results across dataset")
    print("\nMemory requirements are HIGHER than simple inference due to:")
    print("  - Need to store activations for loss calculation")
    print("  - Batch processing requires KV cache")
    print("  - Dataset batches in memory")
    
    print("\n" + "=" * 90)
    print("Memory Requirements (FP16/BF16 precision)")
    print("=" * 90)
    print(f"{'Model':<50} {'Size':<15} {'Model':<8} {'Total':<8} {'A100-40':<10} {'A100-80':<10}")
    print("-" * 90)
    
    # Analyze models that would run fast
    fast_models = [
        "Qwen/Qwen2.5-0.5B",
        "Qwen/Qwen2.5-1.5B",
        "Qwen/Qwen2.5-3B",
        "Qwen/Qwen2.5-7B",
        "Qwen/Qwen2.5-14B",
        "Qwen/Qwen2.5-32B",
        "meta-llama/Llama-3.1-8B",
        "nvidia/Mistral-NeMo-12B-Base",
    ]
    
    for model in fast_models:
        mem = estimate_memory_requirements(model, batch_size=8, seq_length=512)
        if 'note' not in mem:
            fits_40 = "Yes" if mem['fits_a100_40gb_fp16'] else "No"
            fits_80 = "Yes" if mem['fits_a100_80gb_fp16'] else "Yes"
            print(f"{mem['model']:<50} {mem['size']:<15} {mem['model_memory_fp16_gb']:>6.1f}GB {mem['total_fp16_gb']:>6.1f}GB {fits_40:<10} {fits_80:<10}")
    
    print("\n" + "=" * 90)
    print("Compute Time Estimates (1000 samples, batch_size=8, seq_length=512)")
    print("=" * 90)
    print(f"{'Model':<50} {'Size':<15} {'Time (min)':<12} {'Time (hr)':<10} {'Tokens/sec':<12}")
    print("-" * 90)
    
    for model in fast_models:
        time_est = estimate_compute_time(model, dataset_size=1000, batch_size=8, seq_length=512)
        if 'note' not in time_est:
            print(f"{time_est['model']:<50} {time_est['size']:<15} {time_est['estimated_time_minutes']:>10.1f} {time_est['estimated_time_hours']:>8.2f} {time_est['estimated_tokens_per_sec']:>10.0f}")
    
    print("\n" + "=" * 90)
    print("Key Requirements Summary")
    print("=" * 90)
    print("\n1. GPU Memory:")
    print("   - A100 40GB: Can handle models up to ~14B with FP16")
    print("   - A100 80GB: Can handle models up to ~32B with FP16")
    print("   - Use FP16/BF16 for memory efficiency (2x less than FP32)")
    print("   - Batch size affects memory: smaller batch = less memory needed")
    
    print("\n2. Compute Time:")
    print("   - Small models (0.5-3B): ~1-5 minutes for 1000 samples")
    print("   - Medium models (7-14B): ~5-15 minutes for 1000 samples")
    print("   - Large models (32B): ~30-60 minutes for 1000 samples")
    print("   - Larger datasets scale linearly")
    
    print("\n3. Software Requirements:")
    print("   - PyTorch with CUDA support")
    print("   - transformers library")
    print("   - accelerate (optional, for memory optimization)")
    print("   - datasets library (for evaluation datasets)")
    
    print("\n4. Dataset Considerations:")
    print("   - Common datasets: WikiText-2, C4, PTB")
    print("   - Dataset size affects total compute time")
    print("   - Need to tokenize dataset (can be done offline)")
    
    print("\n5. Memory Optimization Tips:")
    print("   - Use FP16/BF16 instead of FP32")
    print("   - Reduce batch_size if OOM errors occur")
    print("   - Use gradient_checkpointing if training")
    print("   - Use torch.compile() for faster inference (PyTorch 2.0+)")
    print("   - Consider using accelerate library for memory management")

