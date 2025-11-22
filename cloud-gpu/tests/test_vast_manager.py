"""Tests for VastManager module."""
import pytest
from vast_manager import VastManager


class TestVastManager:
    """Test VastManager class."""
    
    def test_init_with_api_key(self, vast_api_key):
        """Test VastManager initialization with API key."""
        manager = VastManager(api_key=vast_api_key)
        assert manager.client is not None
        assert manager.instance_id is None
        assert manager.instance_start_time is None
        assert manager.selected_offer is None
    
    def test_init_without_api_key(self):
        """Test VastManager initialization without API key (should fail)."""
        # Mock environment without API key
        import os
        old_key = os.environ.get('VAST_API_KEY')
        try:
            if 'VAST_API_KEY' in os.environ:
                del os.environ['VAST_API_KEY']
            with pytest.raises(ValueError, match="VAST_API_KEY not found"):
                VastManager()
        finally:
            if old_key:
                os.environ['VAST_API_KEY'] = old_key
    
    @pytest.mark.vast
    def test_search_instances(self, vast_api_key):
        """Test searching for instances."""
        manager = VastManager(api_key=vast_api_key)
        offers = manager.search_instances(
            gpu_type="A100",
            max_price_per_hour=2.0,
            limit=10
        )
        assert isinstance(offers, list)
        # May be empty, that's ok - just testing API works
    
    @pytest.mark.vast
    def test_select_cheapest(self, vast_api_key):
        """Test selecting cheapest offer."""
        manager = VastManager(api_key=vast_api_key)
        offers = manager.search_instances(
            gpu_type="A100",
            max_price_per_hour=2.0,
            limit=10
        )
        
        if not offers:
            pytest.skip("No offers available for testing")
        
        selected = manager.select_cheapest(offers)
        assert selected is not None
        assert isinstance(selected, dict)
        assert 'gpu_name' in selected or 'id' in selected
    
    def test_select_cheapest_empty_list(self, vast_api_key):
        """Test selecting cheapest from empty list (should fail)."""
        manager = VastManager(api_key=vast_api_key)
        with pytest.raises(ValueError, match="No offers provided"):
            manager.select_cheapest([])
    
    def test_get_connection_info(self, vast_api_key):
        """Test extracting connection information."""
        manager = VastManager(api_key=vast_api_key)
        
        # Mock instance info
        instance_info = {
            'id': 12345,
            'public_ipaddr': '192.168.1.100',
            'ssh_port': 22,
            'ssh_username': 'root'
        }
        
        conn_info = manager.get_connection_info(instance_info)
        assert conn_info['host'] == '192.168.1.100'
        assert conn_info['port'] == '22'
        assert conn_info['username'] == 'root'
    
    def test_calculate_cost(self, vast_api_key):
        """Test cost calculation."""
        manager = VastManager(api_key=vast_api_key)
        
        # No start time - should return None
        assert manager.calculate_cost() is None
        
        # Set start time
        import time
        manager.instance_start_time = time.time() - 3600  # 1 hour ago
        manager.selected_offer = {'dph_total': 1.5}
        
        cost = manager.calculate_cost()
        assert cost is not None
        assert cost > 0
        # Should be approximately $1.50 for 1 hour
        assert 1.4 <= cost <= 1.6

