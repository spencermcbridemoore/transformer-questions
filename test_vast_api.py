#!/usr/bin/env python3
"""Test script for Vast.ai API connection."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key
api_key = os.getenv('VAST_API_KEY')

if not api_key or api_key == 'your_vast_api_key_here':
    print("[ERROR] API key not found or not set")
    exit(1)

print(f"[OK] API key found (length: {len(api_key)})")
print("Testing Vast.ai API connection...")

try:
    from vastai import VastAI
    
    # Initialize Vast client with API key
    # The SDK will use environment variable VAST_API_KEY if not passed
    client = VastAI(api_key=api_key)
    
    # Test API connection by getting user info
    print("Fetching account information...")
    user_info = client.show_user()
    
    print("[OK] API connection successful!")
    if isinstance(user_info, dict):
        print(f"Account ID: {user_info.get('id', 'N/A')}")
        print(f"Username: {user_info.get('username', 'N/A')}")
        print(f"Email: {user_info.get('email', 'N/A')}")
    else:
        print(f"User info: {user_info}")
    
    # Try to search for available instances
    print("\nSearching for available instances (RTX GPUs)...")
    offers = client.search_offers(
        query="gpu_name:RTX",
        order="score",
        limit=3
    )
    
    if offers and len(offers) > 0:
        print(f"[OK] Found {len(offers)} instance(s)")
        for i, offer in enumerate(offers[:3], 1):
            if isinstance(offer, dict):
                gpu_name = offer.get('gpu_name', 'Unknown')
                price = offer.get('dph_total', 0)
                cuda = offer.get('cuda_max_good', 'N/A')
                print(f"\n{i}. {gpu_name}")
                print(f"   Price: ${price:.2f}/hr")
                print(f"   CUDA: {cuda}")
            else:
                print(f"\n{i}. {offer}")
    else:
        print("No instances found (this is OK - API is working)")
        
except ImportError as e:
    print(f"[ERROR] vastai-sdk not properly installed: {e}")
    print("Try: pip install vastai-sdk")
except Exception as e:
    print(f"[ERROR] API connection failed: {e}")
    import traceback
    traceback.print_exc()
    print("\nCheck your API key at https://vast.ai/console/account")

