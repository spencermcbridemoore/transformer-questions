#!/usr/bin/env python3
"""Quick test of multi-GPU search functionality."""
import sys
from pathlib import Path

# Add lib directory to path
lib_path = Path('cloud-gpu/lib')
sys.path.insert(0, str(lib_path))

from dotenv import load_dotenv
load_dotenv()

from vast_manager import VastManager

print("=" * 60)
print("Testing Multi-GPU Search (A100 or H100 under $3/hour)")
print("=" * 60)

manager = VastManager()

try:
    # Test the new multi-GPU search
    offers = manager.search_instances(
        gpu_types=['A100', 'H100'],
        max_price_per_hour=3.0,
        limit=20
    )
    
    print(f"\n[OK] Found {len(offers)} offers")
    print("\nTop 5 cheapest offers:")
    for i, offer in enumerate(offers[:5], 1):
        gpu = offer.get('gpu_name', 'Unknown')
        price = offer.get('dph_total', offer.get('dph', offer.get('price', 0)))
        print(f"  {i}. {gpu} - ${price:.2f}/hour")
    
    # Check if we got both types
    gpu_names = [o.get('gpu_name', '') for o in offers]
    has_a100 = any('A100' in gpu.upper() for gpu in gpu_names)
    has_h100 = any('H100' in gpu.upper() for gpu in gpu_names)
    
    print(f"\n[INFO] GPU types found:")
    print(f"  A100: {'Yes' if has_a100 else 'No'}")
    print(f"  H100: {'Yes' if has_h100 else 'No'}")
    
    if offers:
        selected = manager.select_cheapest(offers)
        print(f"\n[OK] Cheapest offer selected successfully!")
        print(f"  GPU: {selected.get('gpu_name')}")
        print(f"  Price: ${selected.get('dph_total', selected.get('dph', 0)):.2f}/hour")
    
except ValueError as e:
    if "No A100 instances found" in str(e) or "No H100 instances found" in str(e):
        print(f"\n[SKIP] No A100 or H100 instances available under $3/hour")
        print(f"  This is expected if none are available right now")
    else:
        raise

print("\n" + "=" * 60)
print("[OK] Multi-GPU search test completed")

