#!/usr/bin/env python3
"""Check instance status details."""
from vastai import VastAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

instances = client.show_instances()
instance_list = instances if isinstance(instances, list) else instances.get('instances', [])

print(f"Found {len(instance_list)} instances\n")

for inst in instance_list[:3]:
    if isinstance(inst, dict):
        print(f"Instance {inst.get('id')}:")
        print(f"  Keys: {list(inst.keys())[:10]}")
        print(f"  Status: {inst.get('status', 'N/A')}")
        print(f"  State: {inst.get('state', 'N/A')}")
        print(f"  Actual_status: {inst.get('actual_status', 'N/A')}")
        print(f"  GPU: {inst.get('gpu_name', 'N/A')}")
        print(f"  IP: {inst.get('public_ipaddr', inst.get('ip', 'N/A'))}")
        print()

