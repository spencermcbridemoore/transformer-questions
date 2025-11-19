"""Pytest configuration and fixtures for Vast.ai API tests."""
import os
import pytest
from dotenv import load_dotenv


def load_vast_api_key():
    """Load VAST_API_KEY from environment or .env file."""
    load_dotenv()
    api_key = os.getenv('VAST_API_KEY')
    if not api_key or api_key == 'your_vast_api_key_here':
        return None
    return api_key


def has_vastai_sdk():
    """Check if vastai-sdk is installed."""
    try:
        import vastai
        return True
    except ImportError:
        return False


def vastai_api_available():
    """Check if Vast.ai API is available (SDK installed and API key present)."""
    return has_vastai_sdk() and load_vast_api_key() is not None


@pytest.fixture(scope="session")
def vast_api_key():
    """Fixture to get Vast.ai API key from environment."""
    api_key = load_vast_api_key()
    if not api_key:
        pytest.skip("VAST_API_KEY not set in environment or .env file")
    return api_key


@pytest.fixture(scope="session")
def vast_client(vast_api_key):
    """Fixture to create VastAI client."""
    if not has_vastai_sdk():
        pytest.skip("vastai-sdk not installed")
    
    from vastai import VastAI
    return VastAI(api_key=vast_api_key)


# Skip decorators for convenience
skip_if_no_vastai_sdk = pytest.mark.skipif(not has_vastai_sdk(), reason="vastai-sdk not installed")
skip_if_no_api_key = pytest.mark.skipif(load_vast_api_key() is None, reason="VAST_API_KEY not set")
skip_if_no_vastai_api = pytest.mark.skipif(not vastai_api_available(), reason="Vast.ai API not available")

