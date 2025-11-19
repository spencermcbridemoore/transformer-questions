#!/usr/bin/env python3
"""Cleanup active instance."""
from vastai import VastAI
import os
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

instance_id = 28027776
print(f"Destroying instance {instance_id}...")

try:
    result = client.destroy_instance(id=instance_id)
    print(f"[OK] Instance {instance_id} destroyed")
    print(f"Result: {result}")
except Exception as e:
    print(f"[ERROR] Failed to destroy: {e}")
    import traceback
    traceback.print_exc()

