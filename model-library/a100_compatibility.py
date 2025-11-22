#!/usr/bin/env python3
"""Analyze which models can run fast on A100 GPUs."""
from models import MODEL_PAIRS, get_model_info, filter_by_size

# A100 GPU specifications
A100_40GB = {
    'memory_gb': 40,
    'description': 'A100 40GB - Can handle models up to ~20-24B with quantization',
    'fast_models_max': 14,  # Models 14B and below run very fast
    'medium_models_max': 32,  # Models up to 32B work but may need quantization
}

A100_80GB = {
    'memory_gb': 80,
    'description': 'A100 80GB - Can handle models up to ~70B with quantization',
    'fast_models_max': 32,  # Models 32B and below run very fast
    'medium_models_max': 72,  # Models up to 72B work but may need quantization
}

def analyze_model_for_a100(model_name: str, a100_type='40GB'):
    """
    Analyze if a model can run fast on A100.
    
    Returns:
        dict with compatibility info
    """
    info = get_model_info(model_name)
    if not info['size']:
        # Models without size in name (like DeepSeek V3) - need manual check
        return {
            'model': model_name,
            'size': 'Unknown',
            'fast_on_40gb': 'Unknown',
            'fast_on_80gb': 'Unknown',
            'notes': 'Size not in model name - check HuggingFace for actual size'
        }
    
    size = info['size']
    a100_spec = A100_40GB if a100_type == '40GB' else A100_80GB
    
    # Rough estimates for fast inference
    # Fast = can run at full precision or with minimal quantization
    # Medium = needs quantization but still usable
    # Slow = needs significant optimization or won't fit
    
    fast_40gb = size <= A100_40GB['fast_models_max']
    medium_40gb = size <= A100_40GB['medium_models_max'] and size > A100_40GB['fast_models_max']
    
    fast_80gb = size <= A100_80GB['fast_models_max']
    medium_80gb = size <= A100_80GB['medium_models_max'] and size > A100_80GB['fast_models_max']
    
    result = {
        'model': model_name,
        'size': f"{info['size_str']} ({size}B parameters)",
        'family': info['family'],
        'fast_on_40gb': fast_40gb,
        'medium_on_40gb': medium_40gb,
        'fast_on_80gb': fast_80gb,
        'medium_on_80gb': medium_80gb,
    }
    
    if size > 72:
        result['notes'] = 'Very large - may need model parallelism or significant quantization'
    elif size > 32:
        result['notes'] = 'Large - will need quantization on 40GB, may work on 80GB'
    elif size > 14:
        result['notes'] = 'Medium - may benefit from quantization on 40GB'
    else:
        result['notes'] = 'Small - should run very fast'
    
    return result

if __name__ == '__main__':
    print("=" * 80)
    print("A100 GPU Compatibility Analysis")
    print("=" * 80)
    
    print("\nA100 40GB Specifications:")
    print(f"  Memory: {A100_40GB['memory_gb']}GB")
    print(f"  Fast models: Up to {A100_40GB['fast_models_max']}B parameters")
    print(f"  Medium models: Up to {A100_40GB['medium_models_max']}B parameters (with quantization)")
    
    print("\nA100 80GB Specifications:")
    print(f"  Memory: {A100_80GB['memory_gb']}GB")
    print(f"  Fast models: Up to {A100_80GB['fast_models_max']}B parameters")
    print(f"  Medium models: Up to {A100_80GB['medium_models_max']}B parameters (with quantization)")
    
    print("\n" + "=" * 80)
    print("Model Compatibility Analysis")
    print("=" * 80)
    
    # Analyze all models
    results = []
    for base_model in MODEL_PAIRS.keys():
        result_40 = analyze_model_for_a100(base_model, '40GB')
        result_80 = analyze_model_for_a100(base_model, '80GB')
        results.append((result_40, result_80))
    
    # Fast models on 40GB A100
    print("\n[FAST on A100 40GB] - Models that will run very fast:")
    print("-" * 80)
    fast_40gb = [r for r, _ in results if r.get('fast_on_40gb') == True]
    for r in fast_40gb:
        print(f"  {r['model']:50s} {r['size']:15s} ({r['family']})")
    
    # Fast models on 80GB A100
    print("\n[FAST on A100 80GB] - Models that will run very fast:")
    print("-" * 80)
    fast_80gb = [r for r, _ in results if r.get('fast_on_80gb') == True]
    for r in fast_80gb:
        print(f"  {r['model']:50s} {r['size']:15s} ({r['family']})")
    
    # Medium models (work but slower)
    print("\n[MEDIUM on A100 40GB] - Models that work but may need quantization:")
    print("-" * 80)
    medium_40gb = [r for r, _ in results if r.get('medium_on_40gb') == True]
    if medium_40gb:
        for r in medium_40gb:
            print(f"  {r['model']:50s} {r['size']:15s} ({r['family']})")
    else:
        print("  None")
    
    # Large models
    print("\n[LARGE] - Models that need significant optimization:")
    print("-" * 80)
    large = []
    for r, _ in results:
        if r.get('size') and r['size'] != 'Unknown':
            try:
                size_val = float(r['size'].split()[0].replace('B', ''))
                if size_val > 32:
                    large.append(r)
            except (ValueError, IndexError):
                pass
    for r in large:
        print(f"  {r['model']:50s} {r['size']:15s} ({r['family']}) - {r.get('notes', '')}")
    
    # Unknown size models
    print("\n[UNKNOWN SIZE] - Check HuggingFace for actual model size:")
    print("-" * 80)
    unknown = [r for r, _ in results if r.get('size') == 'Unknown']
    for r in unknown:
        print(f"  {r['model']:50s} {r.get('notes', '')}")

