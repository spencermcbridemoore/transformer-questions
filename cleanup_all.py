#!/usr/bin/env python3
"""Cleanup all active instances."""
from vastai import VastAI
import os
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

print("Checking for active instances...")
instances = client.show_instances()
instance_list = instances if isinstance(instances, list) else instances.get('instances', [])

print(f"Found {len(instance_list)} instances")

for inst in instance_list:
    if isinstance(inst, dict):
        inst_id = inst.get('id')
        status = inst.get('status', inst.get('state', 'unknown'))
        print(f"\nDestroying instance {inst_id} (status: {status})...")
        try:
            client.destroy_instance(id=inst_id)
            print(f"[OK] Instance {inst_id} destroyed")
        except Exception as e:
            print(f"[ERROR] Failed to destroy {inst_id}: {e}")

print("\n[OK] Cleanup complete")

