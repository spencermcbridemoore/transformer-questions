#!/usr/bin/env python3
"""Check for active Vast.ai instances."""
from vastai import VastAI
import os
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

instances = client.show_instances()
inst_list = instances if isinstance(instances, list) else instances.get('instances', [])

print(f'Active instances: {len(inst_list)}')

if inst_list:
    for inst in inst_list:
        if isinstance(inst, dict):
            inst_id = inst.get('id')
            status = inst.get('status', inst.get('state', 'unknown'))
            print(f"  Instance {inst_id}: {status}")
            
            # If running, show cost info
            if status in ['running', 'ready', 'online']:
                price = inst.get('dph_total', inst.get('dph', 0))
                print(f"    Price: ${price:.2f}/hr")
                print(f"    ⚠️  This instance is running and incurring costs!")
else:
    print("No active instances")

