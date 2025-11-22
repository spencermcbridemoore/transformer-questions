"""
Model evaluation utilities.

Helper functions for model evaluation, perplexity calculation, etc.
"""
from typing import Dict, Any, Optional, List


class ModelEvaluator:
    """Utilities for model evaluation."""
    
    @staticmethod
    def format_instance_info(instance_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format instance information for display.
        
        Args:
            instance_info: Instance info dictionary from Vast.ai
            
        Returns:
            Formatted dictionary with connection details
        """
        return {
            'id': instance_info.get('id'),
            'gpu': instance_info.get('gpu_name', 'Unknown'),
            'ip': instance_info.get('public_ipaddr', instance_info.get('ip')),
            'port': instance_info.get('ssh_port', 22),
            'username': instance_info.get('ssh_username', 'root'),
            'status': instance_info.get('status', instance_info.get('state', 'unknown')),
        }
    
    @staticmethod
    def print_connection_info(connection_info: Dict[str, str]):
        """Print connection information in a readable format."""
        print("[OK] Instance ready!")
        print(f"  IP: {connection_info['host']}")
        print(f"  SSH User: {connection_info['username']}")
        print(f"  SSH Port: {connection_info['port']}")
        print(f"\n  Connect with:")
        print(f"  ssh {connection_info['username']}@{connection_info['host']} -p {connection_info['port']}")
    
    @staticmethod
    def estimate_model_download_time(model_size_gb: float, bandwidth_mbps: float = 100) -> float:
        """
        Estimate model download time.
        
        Args:
            model_size_gb: Model size in GB
            bandwidth_mbps: Download bandwidth in Mbps (default: 100 Mbps)
            
        Returns:
            Estimated time in seconds
        """
        # Convert to bits
        size_bits = model_size_gb * 8 * 1024 * 1024 * 1024
        # Calculate time
        time_seconds = size_bits / (bandwidth_mbps * 1024 * 1024)
        return time_seconds

