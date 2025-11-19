#!/usr/bin/env python3
"""Quick test of Vast.ai search to find cheap A100 instances."""
from vastai import VastAI
import os
from dotenv import load_dotenv

load_dotenv()
client = VastAI(api_key=os.getenv('VAST_API_KEY'))

print("Searching for A100 instances under $1/hr...")
offers = client.search_offers(query='gpu_name:A100', order='score', limit=50)

# Process offers
if isinstance(offers, list):
    offers_list = offers
elif isinstance(offers, dict):
    offers_list = offers.get('offers', [])
else:
    offers_list = []

print(f"Total offers: {len(offers_list)}")

# Filter by price and GPU type - must actually be A100
cheap = []
for o in offers_list:
    if isinstance(o, dict):
        price = o.get('dph_total', o.get('dph', 999))
        gpu_name = o.get('gpu_name', '')
        # Must actually contain A100 in the name
        if price < 1.0 and 'A100' in gpu_name.upper():
            cheap.append(o)

print(f"Found {len(cheap)} actual A100 instances under $1/hr\n")

if cheap:
    cheap.sort(key=lambda x: x.get('dph_total', x.get('dph', 999)))
    print("Cheapest A100 instances:")
    for i, o in enumerate(cheap[:10], 1):
        price = o.get('dph_total', o.get('dph', 0))
        gpu = o.get('gpu_name', 'Unknown')
        offer_id = o.get('id', 'N/A')
        print(f"{i}. ${price:.2f}/hr - {gpu} (ID: {offer_id})")
    
    if cheap:
        cheapest = cheap[0]
        price = cheapest.get('dph_total', cheapest.get('dph', 0))
        print(f"\nCheapest A100: ${price:.2f}/hr")
        print(f"Running for 10 minutes would cost: ${(price / 60) * 10:.4f}")
        print(f"Safe to test if < $1 total!")
else:
    print("No A100 instances found under $1/hr")
    print("\nShowing all A100 instances regardless of price:")
    a100_all = [o for o in offers_list if isinstance(o, dict) and 'A100' in o.get('gpu_name', '').upper()]
    if a100_all:
        a100_all.sort(key=lambda x: x.get('dph_total', x.get('dph', 999)))
        for i, o in enumerate(a100_all[:5], 1):
            price = o.get('dph_total', o.get('dph', 0))
            gpu = o.get('gpu_name', 'Unknown')
            print(f"{i}. ${price:.2f}/hr - {gpu}")
