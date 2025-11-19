#!/usr/bin/env python3
"""Script to display GPU information."""
import subprocess
import sys


def get_gpu_info():
    """Get GPU information using nvidia-smi."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu', 
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        print("Error: Could not query GPU information")
        return []
    except FileNotFoundError:
        print("Error: nvidia-smi not found. Is NVIDIA driver installed?")
        return []
    except subprocess.TimeoutExpired:
        print("Error: nvidia-smi timed out")
        return []


def get_cuda_version():
    """Get CUDA version."""
    try:
        result = subprocess.run(
            ['nvcc', '--version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        # Extract version from output
        for line in result.stdout.split('\n'):
            if 'release' in line.lower():
                return line.strip()
        return "CUDA version unknown"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_pytorch_info():
    """Get PyTorch CUDA information."""
    try:
        import torch
        info = {
            'version': torch.__version__,
            'cuda_available': torch.cuda.is_available(),
        }
        
        if info['cuda_available']:
            info['cuda_version'] = torch.version.cuda
            info['device_count'] = torch.cuda.device_count()
            info['devices'] = []
            for i in range(info['device_count']):
                info['devices'].append({
                    'index': i,
                    'name': torch.cuda.get_device_name(i),
                    'capability': torch.cuda.get_device_capability(i)
                })
        return info
    except ImportError:
        return None


def main():
    """Main function."""
    print("=" * 60)
    print("GPU Information")
    print("=" * 60)
    print()
    
    # NVIDIA-SMI info
    print("NVIDIA-SMI Information:")
    print("-" * 60)
    gpu_lines = get_gpu_info()
    if gpu_lines:
        print(f"{'ID':<4} {'Name':<30} {'Mem Total':<12} {'Mem Used':<12} {'Mem Free':<12} {'Temp':<8} {'Util':<8}")
        print("-" * 60)
        for line in gpu_lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 7:
                print(f"{parts[0]:<4} {parts[1]:<30} {parts[2]:<12} {parts[3]:<12} {parts[4]:<12} {parts[5]:<8} {parts[6]:<8}")
    else:
        print("No GPU information available")
    print()
    
    # CUDA version
    print("CUDA Information:")
    print("-" * 60)
    cuda_version = get_cuda_version()
    if cuda_version:
        print(cuda_version)
    else:
        print("CUDA not found")
    print()
    
    # PyTorch info
    print("PyTorch Information:")
    print("-" * 60)
    pytorch_info = get_pytorch_info()
    if pytorch_info:
        print(f"PyTorch version: {pytorch_info['version']}")
        print(f"CUDA available: {pytorch_info['cuda_available']}")
        if pytorch_info['cuda_available']:
            print(f"CUDA version: {pytorch_info['cuda_version']}")
            print(f"Device count: {pytorch_info['device_count']}")
            for device in pytorch_info['devices']:
                print(f"  Device {device['index']}: {device['name']}")
                print(f"    Compute Capability: {device['capability'][0]}.{device['capability'][1]}")
    else:
        print("PyTorch not installed")
    print()
    
    print("=" * 60)


if __name__ == '__main__':
    main()

