# Model Library

A curated library of base and SFT/Instruct model pairs for transformer experiments.

## Models Included

### Qwen 2.5 Series
- 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B
- Math variants: 1.5B, 7B, 72B

### Llama 3.1 Series
- 8B, 70B, 405B

### DeepSeek Series
- V3-Base → V3
- V3.1-Base → V3.1

### NVIDIA Series
- Mistral-NeMo-12B
- Mistral-NeMo-Minitron-8B
- Nemotron-4-340B

## Usage

```python
from model_library.models import (
    MODEL_PAIRS,
    get_base_models,
    get_instruct_models,
    get_instruct_model,
    get_base_model,
    filter_by_size,
    filter_by_family,
    get_model_info
)

# Get all base models
base_models = get_base_models()

# Get instruct version of a base model
instruct = get_instruct_model("Qwen/Qwen2.5-7B")
# Returns: "Qwen/Qwen2.5-7B-Instruct"

# Filter by size
small_models = filter_by_size(max_size="7B")
# Returns models 7B and smaller

# Filter by family
qwen_models = filter_by_family("Qwen")

# Get model information
info = get_model_info("Qwen/Qwen2.5-7B")
# Returns: {
#   'name': 'Qwen/Qwen2.5-7B',
#   'is_base': True,
#   'is_instruct': False,
#   'instruct_version': 'Qwen/Qwen2.5-7B-Instruct',
#   'type': 'base',
#   'size': 7.0,
#   'size_str': '7B',
#   'family': 'Qwen'
# }
```

## Integration

This library can be used with:
- Vast.ai instance testing (see `cloud-gpu/examples/vast-ai-test.ipynb`)
- Model comparison experiments
- Fine-tuning workflows
- Inference testing

