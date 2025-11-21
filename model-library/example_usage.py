#!/usr/bin/env python3
"""Example usage of the model library."""
from models import (
    MODEL_PAIRS,
    get_base_models,
    get_instruct_model,
    filter_by_size,
    filter_by_family,
    get_model_info,
)

print("=" * 70)
print("Model Library Examples")
print("=" * 70)

# Show all model pairs
print(f"\nTotal model pairs: {len(MODEL_PAIRS)}")
print("\nAll model pairs:")
for base, instruct in MODEL_PAIRS.items():
    print(f"  {base}")
    print(f"    -> {instruct}")

# Filter by size
print("\n" + "=" * 70)
print("Models 7B and smaller:")
small_models = filter_by_size(max_size="7B")
for base, instruct in small_models.items():
    info = get_model_info(base)
    print(f"  {base} ({info['size_str']}) - {info['family']}")

# Filter by family
print("\n" + "=" * 70)
print("Qwen models:")
qwen_models = filter_by_family("Qwen")
for base, instruct in qwen_models.items():
    info = get_model_info(base)
    print(f"  {base} ({info['size_str']})")

# Get model info
print("\n" + "=" * 70)
print("Model information example:")
info = get_model_info("Qwen/Qwen2.5-7B")
for key, value in info.items():
    print(f"  {key}: {value}")

# Get instruct version
print("\n" + "=" * 70)
print("Getting instruct versions:")
test_models = ["Qwen/Qwen2.5-7B", "meta-llama/Llama-3.1-8B"]
for base in test_models:
    instruct = get_instruct_model(base)
    print(f"  {base}")
    print(f"    -> {instruct}")

