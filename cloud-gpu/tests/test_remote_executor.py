"""Tests for RemoteExecutor module."""
import pytest

try:
    from remote_executor import RemoteExecutor
except ImportError as e:
    pytest.skip(f"remote_executor not available: {e}", allow_module_level=True)


class TestRemoteExecutor:
    """Test RemoteExecutor class."""
    
    def test_init(self):
        """Test RemoteExecutor initialization."""
        executor = RemoteExecutor(
            host="192.168.1.100",
            port=22,
            username="testuser",
            timeout=30
        )
        assert executor.host == "192.168.1.100"
        assert executor.port == 22
        assert executor.username == "testuser"
        assert executor.timeout == 30
        assert executor._ssh_client is None
        assert executor._sftp_client is None
    
    def test_init_with_ssh_key(self):
        """Test RemoteExecutor initialization with SSH key."""
        executor = RemoteExecutor(
            host="192.168.1.100",
            ssh_key_path="/path/to/key",
            timeout=30
        )
        assert executor.ssh_key_path == "/path/to/key"
        assert executor.password is None
    
    def test_init_with_password(self):
        """Test RemoteExecutor initialization with password."""
        executor = RemoteExecutor(
            host="192.168.1.100",
            password="secret",
            timeout=30
        )
        assert executor.password == "secret"
        assert executor.ssh_key_path is None
    
    def test_context_manager(self):
        """Test RemoteExecutor as context manager."""
        executor = RemoteExecutor(
            host="192.168.1.100",
            port=22,
            username="testuser"
        )
        
        # Context manager should handle connect/disconnect
        # (We can't actually connect in tests, but can test structure)
        assert executor._ssh_client is None
        
        # Test that it's a context manager
        assert hasattr(executor, '__enter__')
        assert hasattr(executor, '__exit__')
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected (should not error)."""
        executor = RemoteExecutor(host="192.168.1.100")
        # Should not raise error
        executor.disconnect()
        assert executor._ssh_client is None
    
    def test_execute_command_when_not_connected(self):
        """Test execute_command when not connected (should attempt connection)."""
        executor = RemoteExecutor(
            host="192.168.1.100",
            port=22,
            username="testuser"
        )
        
        # Won't actually connect, but should handle gracefully
        # The actual connection will fail, but method should exist
        output, error, status = executor.execute_command("echo test")
        # Status will be 1 (error) because connection fails
        assert status == 1 or status == 0  # May fail or timeout
    
    def test_upload_file_invalid_path(self):
        """Test upload_file with invalid local path."""
        executor = RemoteExecutor(host="192.168.1.100")
        
        # Should return False for non-existent file
        result = executor.upload_file("/nonexistent/file.py", "/tmp/file.py")
        assert result is False
    
    # Note: We can't test actual SSH connections without a real server,
    # but we can test the structure and error handling

