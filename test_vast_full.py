#!/usr/bin/env python3
"""Test the full Vast.ai workflow with cheapest available A100."""
from vastai import VastAI
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

print("=" * 60)
print("Vast.ai A100 Instance Testing")
print("=" * 60)

# 1. Search for A100 instances
print("\n[1/6] Searching for A100 instances...")
offers = client.search_offers(query='gpu_name:A100', order='score', limit=50)

if isinstance(offers, list):
    offers_list = offers
elif isinstance(offers, dict):
    offers_list = offers.get('offers', [])
else:
    offers_list = []

# Filter for actual A100s
a100_offers = [o for o in offers_list if isinstance(o, dict) and 'A100' in o.get('gpu_name', '').upper()]

if not a100_offers:
    print(f"[DEBUG] Total offers: {len(offers_list)}")
    print(f"[DEBUG] Sample GPU names: {[o.get('gpu_name') for o in offers_list[:5] if isinstance(o, dict)]}")
    raise ValueError("No A100 instances found")

a100_offers.sort(key=lambda x: x.get('dph_total', x.get('dph', 999)))

if not a100_offers:
    print("[ERROR] No A100 instances found")
    exit(1)

selected_offer = a100_offers[0]
selected_price = selected_offer.get('dph_total', selected_offer.get('dph', 0))
selected_id = selected_offer.get('id')

print(f"[OK] Selected: {selected_offer.get('gpu_name')} @ ${selected_price:.2f}/hr (ID: {selected_id})")
print(f"  Estimated cost for 10 minutes: ${(selected_price / 60) * 10:.4f}")

# 2. Launch instance
print("\n[2/6] Launching instance...")
print("[WARNING] This will start billing!")

try:
    # create_instance takes offer ID as keyword argument 'id'
    instance = client.create_instance(
        id=selected_id,  # offer ID
        image='pytorch/pytorch:latest',
        disk=10,
    )
    
    instance_id = instance.get('id') if isinstance(instance, dict) else instance
    start_time = time.time()
    
    print(f"[OK] Instance launched: {instance_id}")
except Exception as e:
    print(f"[ERROR] Failed to launch instance: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)

# 3. Wait for instance
print("\n[3/6] Waiting for instance to be ready...")
max_wait = 300  # 5 minutes
poll_interval = 10
instance_info = None

for _ in range(max_wait // poll_interval):
    try:
        instances = client.show_instances()
        instance_list = instances if isinstance(instances, list) else instances.get('instances', [])
        
        for inst in instance_list:
            if isinstance(inst, dict) and str(inst.get('id')) == str(instance_id):
                status = inst.get('status', inst.get('state', 'unknown'))
                print(f"  Status: {status}")
                
                if status in ['running', 'ready', 'online']:
                    instance_info = inst
                    print("[OK] Instance is ready!")
                    break
                elif status in ['error', 'failed']:
                    raise Exception(f"Instance failed with status: {status}")
        
        if instance_info:
            break
        
        time.sleep(poll_interval)
    except Exception as e:
        print(f"[WARNING] Error checking status: {e}")
        time.sleep(poll_interval)

if not instance_info:
    print(f"[ERROR] Instance {instance_id} did not become ready")
    print(f"[CLEANUP] Attempting to destroy instance...")
    try:
        client.destroy_instance(instance_id)
        print("[OK] Instance destroyed")
    except:
        print("[ERROR] Could not destroy - please destroy manually!")
    exit(1)

# Get connection info
ssh_host = instance_info.get('public_ipaddr', instance_info.get('ip'))
ssh_port = instance_info.get('ssh_port', 22)
print(f"[OK] Instance ready!")
print(f"  IP: {ssh_host}")
print(f"  Port: {ssh_port}")

# 4. Quick model test (simulated - actual SSH would require keys)
print("\n[4/6] Model testing (simulated)...")
print("[INFO] Actual model testing would require SSH connection")
print("[INFO] Code for model testing is provided in notebook")
print("[INFO] Skipping to cleanup to minimize costs...")

# 5. Calculate cost
runtime_seconds = time.time() - start_time
runtime_minutes = runtime_seconds / 60
estimated_cost = (runtime_minutes / 60) * selected_price

print(f"\n[5/6] Runtime: {runtime_minutes:.1f} minutes ({runtime_seconds:.0f} seconds)")
print(f"  Estimated cost: ${estimated_cost:.4f}")

# 6. Cleanup
print("\n[6/6] Destroying instance...")
try:
    result = client.destroy_instance(instance_id)
    print(f"[OK] Instance {instance_id} destroyed")
except Exception as e:
    print(f"[ERROR] Failed to destroy: {e}")
    print("[WARNING] Please manually destroy instance at https://console.vast.ai/instances/")
    exit(1)

# Verify destruction
time.sleep(5)
instances = client.show_instances()
instance_list = instances if isinstance(instances, list) else instances.get('instances', [])
found = any(str(inst.get('id')) == str(instance_id) for inst in instance_list if isinstance(inst, dict))

if not found:
    print("[OK] Instance verified as destroyed")
else:
    print("[WARNING] Instance still appears in list - verify manually!")

print("\n" + "=" * 60)
print("Test completed successfully!")
print(f"Total runtime: {runtime_minutes:.1f} minutes")
print(f"Total cost: ~${estimated_cost:.4f}")
print("=" * 60)

