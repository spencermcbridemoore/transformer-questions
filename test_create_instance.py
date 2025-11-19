#!/usr/bin/env python3
"""Debug create_instance response."""
from vastai import VastAI
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

# Find A100 offer
offers = client.search_offers(query='gpu_name:A100', order='score', limit=50)
offers_list = offers if isinstance(offers, list) else offers.get('offers', [])

print(f"Total offers: {len(offers_list)}")
print(f"Sample GPU names: {[o.get('gpu_name') for o in offers_list[:5] if isinstance(o, dict)]}")

# Filter for A100s
a100_offers = []
for o in offers_list:
    if isinstance(o, dict):
        gpu_name = o.get('gpu_name', '')
        price = o.get('dph_total', o.get('dph', 999))
        if 'A100' in gpu_name.upper():
            a100_offers.append(o)
            print(f"  A100 found: {gpu_name} @ ${price:.2f}/hr")

print(f"\nA100 offers found: {len(a100_offers)}")

if not a100_offers:
    print("No A100 offers found")
    exit(1)

a100_offers.sort(key=lambda x: x.get('dph_total', x.get('dph', 999)))
selected = a100_offers[0]
offer_id = selected.get('id')

print(f"\nSelected Offer:")
print(f"  Offer ID: {offer_id}")
print(f"  GPU: {selected.get('gpu_name')}")
print(f"  Price: ${selected.get('dph_total', selected.get('dph', 0)):.2f}/hr")

print("\nCreating instance...")
result = client.create_instance(id=offer_id, image='pytorch/pytorch:latest', disk=10)

print(f"\nResult type: {type(result)}")
print(f"Result: {result}")
if isinstance(result, dict):
    print(f"Result keys: {list(result.keys())}")
    print(f"Result['id']: {result.get('id')}")
elif result is None:
    print("Result is None - instance may have been created but no ID returned")
else:
    print(f"Result is not a dict: {type(result)}")

# Wait a moment, then check instances
print("\nWaiting 5 seconds...")
time.sleep(5)

print("\nChecking instances...")
instances = client.show_instances()
instance_list = instances if isinstance(instances, list) else instances.get('instances', [])

print(f"Found {len(instance_list)} instances")
new_instances = []
for inst in instance_list:
    if isinstance(inst, dict):
        inst_id = inst.get('id')
        status = inst.get('status', inst.get('state', 'unknown'))
        gpu = inst.get('gpu_name', 'Unknown')
        print(f"  Instance {inst_id}: {status} ({gpu})")
        
        # If we find a newly created one, that's probably ours
        if inst_id and status not in ['terminated', 'destroyed', 'stopped']:
            new_instances.append((inst_id, status))

if new_instances:
    print(f"\n[OK] Found {len(new_instances)} potentially active instance(s)")
    print(f"     Latest instance ID: {new_instances[0][0]}")
else:
    print("\n[WARNING] No active instances found")
