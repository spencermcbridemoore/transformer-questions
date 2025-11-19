"""Tests for Vast.ai API functionality."""
import pytest
from conftest import (
    vast_api_key,
    vast_client,
    has_vastai_sdk,
    load_vast_api_key,
    skip_if_no_vastai_sdk,
    skip_if_no_api_key,
    skip_if_no_vastai_api,
    vastai_api_available
)


def test_vast_api_key_loaded():
    """Test that API key can be loaded from environment."""
    api_key = load_vast_api_key()
    if api_key is None:
        pytest.skip("VAST_API_KEY not set - skipping test")
    
    assert api_key is not None
    assert len(api_key) > 0
    assert api_key != 'your_vast_api_key_here'
    print(f"API key loaded (length: {len(api_key)})")


@skip_if_no_vastai_sdk
def test_vastai_sdk_imported():
    """Test that vastai-sdk can be imported."""
    import vastai
    assert vastai is not None
    from vastai import VastAI
    assert VastAI is not None


@skip_if_no_vastai_api
def test_vast_client_initialization(vast_api_key):
    """Test that VastAI client can be initialized with API key."""
    from vastai import VastAI
    client = VastAI(api_key=vast_api_key)
    assert client is not None
    assert hasattr(client, 'show_user')
    assert hasattr(client, 'search_offers')


@skip_if_no_vastai_api
def test_vast_account_info(vast_client):
    """Test fetching account/user information from Vast.ai API."""
    user_info = vast_client.show_user()
    assert user_info is not None
    
    if isinstance(user_info, dict):
        # Check for expected fields
        assert 'id' in user_info or 'username' in user_info or 'email' in user_info
        if 'id' in user_info:
            print(f"Account ID: {user_info['id']}")
        if 'username' in user_info:
            print(f"Username: {user_info['username']}")
        if 'email' in user_info:
            print(f"Email: {user_info['email']}")
    else:
        # API might return list or other format
        assert user_info is not None


@skip_if_no_vastai_api
def test_vast_search_offers(vast_client):
    """Test searching for available GPU instances."""
    offers = vast_client.search_offers(
        query="gpu_name:RTX",
        order="score",
        limit=3
    )
    
    # Offers might be list, dict, or None
    assert offers is not None
    
    if isinstance(offers, list):
        print(f"Found {len(offers)} instance(s)")
        if len(offers) > 0:
            for i, offer in enumerate(offers[:3], 1):
                if isinstance(offer, dict):
                    gpu_name = offer.get('gpu_name', 'Unknown')
                    price = offer.get('dph_total', 0)
                    print(f"{i}. {gpu_name} - ${price:.2f}/hr")
    elif isinstance(offers, dict):
        # API might return dict with 'offers' key
        assert 'offers' in offers or len(offers) > 0


@skip_if_no_vastai_api
def test_vast_search_offers_with_filters(vast_client):
    """Test searching for instances with specific filters."""
    # Test searching for H100 GPUs
    offers = vast_client.search_offers(
        query="gpu_name:H100",
        order="score",
        limit=5
    )
    
    assert offers is not None
    # Test passes regardless of results - just verifying API works


@skip_if_no_vastai_api
def test_vast_api_key_length(vast_api_key):
    """Test that API key has expected format."""
    # Vast.ai API keys are typically 64 characters
    assert len(vast_api_key) >= 32, "API key seems too short"
    assert len(vast_api_key) <= 128, "API key seems too long"
    print(f"API key length: {len(vast_api_key)} (expected ~64)")


def test_vastai_availability_check():
    """Test availability checking functions (runs on all systems)."""
    # This test always runs, just checks detection logic
    has_sdk = has_vastai_sdk()
    has_key = load_vast_api_key() is not None
    api_available = vastai_api_available()
    
    print(f"vastai-sdk installed: {has_sdk}")
    print(f"API key available: {has_key}")
    print(f"API available: {api_available}")
    
    # Test passes regardless of availability
    assert isinstance(has_sdk, bool)
    assert isinstance(has_key, bool)
    assert isinstance(api_available, bool)

