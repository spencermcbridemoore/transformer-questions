"""Tests for ModelEvaluator module."""
import pytest
from model_evaluator import ModelEvaluator


class TestModelEvaluator:
    """Test ModelEvaluator utility class."""
    
    def test_format_instance_info(self):
        """Test formatting instance information."""
        instance_info = {
            'id': 12345,
            'gpu_name': 'A100',
            'public_ipaddr': '192.168.1.100',
            'ssh_port': 22,
            'ssh_username': 'root',
            'status': 'running'
        }
        
        formatted = ModelEvaluator.format_instance_info(instance_info)
        assert formatted['id'] == 12345
        assert formatted['gpu'] == 'A100'
        assert formatted['ip'] == '192.168.1.100'
        assert formatted['port'] == 22
        assert formatted['username'] == 'root'
        assert formatted['status'] == 'running'
    
    def test_format_instance_info_missing_fields(self):
        """Test formatting instance info with missing fields."""
        instance_info = {
            'id': 12345,
        }
        
        formatted = ModelEvaluator.format_instance_info(instance_info)
        assert formatted['id'] == 12345
        assert formatted['gpu'] == 'Unknown'
        assert formatted['ip'] is None
    
    def test_print_connection_info(self, capsys):
        """Test printing connection information."""
        connection_info = {
            'host': '192.168.1.100',
            'port': '22',
            'username': 'root'
        }
        
        ModelEvaluator.print_connection_info(connection_info)
        captured = capsys.readouterr()
        
        assert '192.168.1.100' in captured.out
        assert 'root' in captured.out
        assert '22' in captured.out
    
    def test_estimate_model_download_time(self):
        """Test model download time estimation."""
        # Small model (500MB)
        time_500mb = ModelEvaluator.estimate_model_download_time(0.5, bandwidth_mbps=100)
        assert time_500mb > 0
        assert time_500mb < 100  # Should be < 100 seconds for 500MB at 100 Mbps
        
        # Large model (10GB)
        time_10gb = ModelEvaluator.estimate_model_download_time(10.0, bandwidth_mbps=100)
        assert time_10gb > time_500mb  # Larger model should take longer
        
        # Different bandwidth
        time_slow = ModelEvaluator.estimate_model_download_time(1.0, bandwidth_mbps=10)
        time_fast = ModelEvaluator.estimate_model_download_time(1.0, bandwidth_mbps=100)
        assert time_slow > time_fast  # Slower connection should take longer

