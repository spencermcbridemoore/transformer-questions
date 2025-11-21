"""
Model library: Base and SFT/Instruct model pairs.

This module contains a dictionary mapping base models to their
supervised fine-tuned (SFT) / Instruct versions.
"""

MODEL_PAIRS = {
    # Qwen 2.5 models
    "Qwen/Qwen2.5-0.5B": "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B": "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-3B": "Qwen/Qwen2.5-3B-Instruct",
    "Qwen/Qwen2.5-7B": "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-14B": "Qwen/Qwen2.5-14B-Instruct",
    "Qwen/Qwen2.5-32B": "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-72B": "Qwen/Qwen2.5-72B-Instruct",
    
    # Qwen 2.5 Math models
    "Qwen/Qwen2.5-Math-1.5B": "Qwen/Qwen2.5-Math-1.5B-Instruct",
    "Qwen/Qwen2.5-Math-7B": "Qwen/Qwen2.5-Math-7B-Instruct",
    "Qwen/Qwen2.5-Math-72B": "Qwen/Qwen2.5-Math-72B-Instruct",
    
    # Llama 3.1 models
    "meta-llama/Llama-3.1-8B": "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Llama-3.1-70B": "meta-llama/Llama-3.1-70B-Instruct",
    "meta-llama/Llama-3.1-405B": "meta-llama/Llama-3.1-405B-Instruct",
    
    # DeepSeek models
    "deepseek-ai/DeepSeek-V3-Base": "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-V3.1-Base": "deepseek-ai/DeepSeek-V3.1",
    
    # NVIDIA models
    "nvidia/Mistral-NeMo-12B-Base": "nvidia/Mistral-NeMo-12B-Instruct",
    "nvidia/Mistral-NeMo-Minitron-8B-Base": "nvidia/Mistral-NeMo-Minitron-8B-Instruct",
    "nvidia/Nemotron-4-340B-Base": "nvidia/Nemotron-4-340B-Instruct",
}


def get_base_models():
    """Get list of all base models."""
    return list(MODEL_PAIRS.keys())


def get_instruct_models():
    """Get list of all instruct/SFT models."""
    return list(MODEL_PAIRS.values())


def get_instruct_model(base_model: str) -> str:
    """Get the instruct version of a base model."""
    return MODEL_PAIRS.get(base_model)


def get_base_model(instruct_model: str) -> str:
    """Get the base version of an instruct model."""
    for base, instruct in MODEL_PAIRS.items():
        if instruct == instruct_model:
            return base
    return None


def get_model_pair(base_model: str) -> tuple:
    """Get (base_model, instruct_model) pair."""
    if base_model in MODEL_PAIRS:
        return (base_model, MODEL_PAIRS[base_model])
    return None


def filter_by_size(max_size: str = None, min_size: str = None):
    """
    Filter models by size.
    
    Args:
        max_size: Maximum model size (e.g., "7B", "14B")
        min_size: Minimum model size (e.g., "1.5B", "3B")
    
    Returns:
        Dictionary of filtered model pairs
    """
    def extract_size(model_name: str) -> float:
        """Extract numeric size from model name."""
        import re
        # Look for patterns like "0.5B", "1.5B", "7B", "72B", "340B", "405B"
        match = re.search(r'(\d+\.?\d*)[Bb]', model_name)
        if match:
            return float(match.group(1))
        return 0.0
    
    filtered = {}
    for base, instruct in MODEL_PAIRS.items():
        size = extract_size(base)
        
        if max_size:
            max_val = extract_size(max_size)
            if size > max_val:
                continue
        
        if min_size:
            min_val = extract_size(min_size)
            if size < min_val:
                continue
        
        filtered[base] = instruct
    
    return filtered


def filter_by_family(family: str):
    """
    Filter models by family (Qwen, Llama, DeepSeek, nvidia).
    
    Args:
        family: Model family name (case-insensitive)
    
    Returns:
        Dictionary of filtered model pairs
    """
    family_lower = family.lower()
    filtered = {}
    
    for base, instruct in MODEL_PAIRS.items():
        if family_lower in base.lower():
            filtered[base] = instruct
    
    return filtered


def get_model_info(model_name: str) -> dict:
    """
    Get information about a model.
    
    Returns:
        Dictionary with model information
    """
    info = {
        'name': model_name,
        'is_base': model_name in MODEL_PAIRS,
        'is_instruct': model_name in MODEL_PAIRS.values(),
    }
    
    if info['is_base']:
        info['instruct_version'] = MODEL_PAIRS[model_name]
        info['type'] = 'base'
    elif info['is_instruct']:
        info['base_version'] = get_base_model(model_name)
        info['type'] = 'instruct'
    else:
        info['type'] = 'unknown'
    
    # Extract size
    import re
    size_match = re.search(r'(\d+\.?\d*)[Bb]', model_name)
    if size_match:
        info['size'] = float(size_match.group(1))
        info['size_str'] = size_match.group(0)
    else:
        info['size'] = None
        info['size_str'] = None
    
    # Extract family
    if 'qwen' in model_name.lower():
        info['family'] = 'Qwen'
    elif 'llama' in model_name.lower():
        info['family'] = 'Llama'
    elif 'deepseek' in model_name.lower():
        info['family'] = 'DeepSeek'
    elif 'nvidia' in model_name.lower() or 'nemo' in model_name.lower() or 'nemotron' in model_name.lower():
        info['family'] = 'NVIDIA'
    else:
        info['family'] = 'Unknown'
    
    return info

