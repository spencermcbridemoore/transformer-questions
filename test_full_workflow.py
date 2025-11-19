#!/usr/bin/env python3
"""Complete end-to-end test of Vast.ai A100 workflow."""
from vastai import VastAI
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

print("=" * 70)
print("Vast.ai A100 Complete Workflow Test")
print("=" * 70)
print("[WARNING] This will launch a real instance and incur costs (~$0.20-0.30)")
print()

# Initialize tracking
instance_id = None
instance_start_time = None
selected_price = None

def cleanup():
    """Cleanup function for error handling."""
    if instance_id:
        print("\n[CLEANUP] Attempting to destroy instance...")
        try:
            client.destroy_instance(id=instance_id)
            print(f"[OK] Instance {instance_id} destroyed")
        except Exception as e:
            print(f"[ERROR] Failed to destroy: {e}")
            print("[WARNING] Please manually destroy instance at https://console.vast.ai/instances/")

try:
    # Step 1: Search for A100 instances
    print("[1/6] Searching for A100 instances under $2.00/hr...")
    offers = client.search_offers(query='gpu_name:A100', order='score', limit=50)
    
    if isinstance(offers, list):
        offers_list = offers
    elif isinstance(offers, dict):
        offers_list = offers.get('offers', [])
    else:
        offers_list = []
    
    # Filter for A100s under $2.00/hr (availability may vary)
    a100_offers = []
    for o in offers_list:
        if isinstance(o, dict):
            gpu_name = o.get('gpu_name', '')
            price = o.get('dph_total', o.get('dph', o.get('price', 999)))
            if 'A100' in gpu_name.upper() and price < 2.0:
                a100_offers.append(o)
    
    if not a100_offers:
        raise ValueError("No A100 instances found under $2.00/hr")
    
    a100_offers.sort(key=lambda x: x.get('dph_total', x.get('dph', 999)))
    selected_offer = a100_offers[0]
    selected_price = selected_offer.get('dph_total', selected_offer.get('dph', 0))
    selected_id = selected_offer.get('id')
    
    print(f"[OK] Selected: {selected_offer.get('gpu_name')} @ ${selected_price:.2f}/hr (ID: {selected_id})")
    print(f"     Estimated 10-minute cost: ${(selected_price / 60) * 10:.4f}")
    
    # Step 2: Launch instance
    print("\n[2/6] Launching instance...")
    print("[WARNING] Billing starts now!")
    
    instance_start_time = time.time()
    
    instance = client.create_instance(
        id=selected_id,
        image='pytorch/pytorch:latest',
        disk=10,
    )
    
    # create_instance returns {'success': True, 'new_contract': <instance_id>}
    if isinstance(instance, dict):
        instance_id = instance.get('new_contract') or instance.get('id')
    else:
        instance_id = instance
    
    if not instance_id:
        raise ValueError("Failed to get instance ID from create_instance response")
    
    print(f"[OK] Instance created: {instance_id}")
    
    # Step 3: Wait for instance to be ready
    print("\n[3/6] Waiting for instance to be ready...")
    max_wait = 300  # 5 minutes
    poll_interval = 10
    instance_info = None
    
    for attempt in range(max_wait // poll_interval):
        try:
            instances = client.show_instances()
            instance_list = instances if isinstance(instances, list) else instances.get('instances', [])
            
            for inst in instance_list:
                if isinstance(inst, dict) and str(inst.get('id')) == str(instance_id):
                    status = inst.get('status', inst.get('state', inst.get('actual_status', 'unknown')))
                    ip = inst.get('public_ipaddr', inst.get('ip'))
                    
                    # Print more details occasionally
                    if attempt % 3 == 0:
                        print(f"  Attempt {attempt + 1}: Status = {status}, IP = {ip}")
                    
                    # Consider instance ready if it has an IP address (even if status is 'unknown')
                    if ip and ip != 'None' and ip.strip():
                        instance_info = inst
                        print(f"[OK] Instance is ready! Status: {status}, IP: {ip}")
                        break
                    elif status in ['running', 'ready', 'online', 'active']:
                        instance_info = inst
                        print(f"[OK] Instance is ready! Status: {status}")
                        break
                    elif status in ['error', 'failed', 'terminated']:
                        raise Exception(f"Instance failed with status: {status}")
            
            if instance_info:
                break
            
            time.sleep(poll_interval)
        except Exception as e:
            if 'failed' in str(e).lower() or 'error' in str(e).lower():
                raise
            print(f"[WARNING] Error checking status: {e}")
            time.sleep(poll_interval)
    
    if not instance_info:
        raise TimeoutError(f"Instance {instance_id} did not become ready within {max_wait} seconds")
    
    # Extract connection info
    ssh_host = instance_info.get('public_ipaddr', instance_info.get('ip'))
    ssh_port = instance_info.get('ssh_port', 22)
    ssh_user = instance_info.get('ssh_username', 'root')
    
    print(f"[OK] Instance ready!")
    print(f"     IP: {ssh_host}")
    print(f"     SSH: {ssh_user}@{ssh_host}:{ssh_port}")
    
    # Step 4: Check instance info
    print("\n[4/6] Instance information:")
    print(f"     GPU: {instance_info.get('gpu_name', 'Unknown')}")
    print(f"     Price: ${selected_price:.2f}/hr")
    
    # Calculate current cost
    runtime_seconds = time.time() - instance_start_time
    runtime_minutes = runtime_seconds / 60
    current_cost = (runtime_minutes / 60) * selected_price
    print(f"     Runtime so far: {runtime_minutes:.1f} minutes")
    print(f"     Cost so far: ${current_cost:.4f}")
    
    # Step 5: Model testing (simulated - SSH would require keys)
    print("\n[5/6] Model testing (simulated)...")
    print("[INFO] Actual model testing requires SSH connection setup")
    print("[INFO] Code for model testing is provided in notebook")
    print("[INFO] For this test, we'll skip to cleanup to minimize costs")
    
    # Step 6: Cleanup
    print("\n[6/6] Cleaning up instance...")
    
    final_runtime = time.time() - instance_start_time
    final_minutes = final_runtime / 60
    final_cost = (final_minutes / 60) * selected_price
    
    print(f"     Total runtime: {final_minutes:.1f} minutes ({final_runtime:.0f} seconds)")
    print(f"     Total cost: ${final_cost:.4f}")
    
    try:
        result = client.destroy_instance(id=instance_id)
        print(f"[OK] Instance {instance_id} destroyed")
    except Exception as e:
        print(f"[ERROR] Failed to destroy: {e}")
        raise
    
    # Verify destruction
    print("\n[VERIFY] Verifying instance termination...")
    time.sleep(5)
    
    instances = client.show_instances()
    instance_list = instances if isinstance(instances, list) else instances.get('instances', [])
    found = any(str(inst.get('id')) == str(instance_id) for inst in instance_list if isinstance(inst, dict))
    
    if not found:
        print("[OK] Instance verified as destroyed")
    else:
        print("[WARNING] Instance still appears in list - please verify manually!")
    
    print("\n" + "=" * 70)
    print("[OK] Test completed successfully!")
    print(f"Total runtime: {final_minutes:.1f} minutes")
    print(f"Total cost: ~${final_cost:.4f}")
    print("=" * 70)
    
except KeyboardInterrupt:
    print("\n[INTERRUPTED] User interrupted test")
    cleanup()
    raise
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    cleanup()
    raise

