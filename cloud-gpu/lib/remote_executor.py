"""
Remote execution utilities for SSH/SCP operations.

Handles file upload and command execution on remote instances.
"""
import os
import stat
from typing import Optional, Tuple, Dict
from pathlib import Path

try:
    import paramiko
except ImportError:
    raise ImportError("paramiko not installed. Install with: pip install paramiko")


class RemoteExecutor:
    """Handles remote execution via SSH and file transfer via SCP."""
    
    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        ssh_key_path: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize remote executor.
        
        Args:
            host: Remote host IP address
            port: SSH port (default: 22)
            username: SSH username (default: root)
            ssh_key_path: Path to SSH private key file
            password: SSH password (if not using key)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.username = username
        self.ssh_key_path = ssh_key_path
        self.password = password
        self.timeout = timeout
        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._sftp_client: Optional[paramiko.SFTPClient] = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try key-based authentication first
            if self.ssh_key_path and os.path.exists(self.ssh_key_path):
                self._ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.ssh_key_path,
                    timeout=self.timeout
                )
            elif self.password:
                self._ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout
                )
            else:
                # Try default key locations
                default_key_paths = [
                    os.path.expanduser("~/.ssh/id_rsa"),
                    os.path.expanduser("~/.ssh/id_ed25519"),
                ]
                
                for key_path in default_key_paths:
                    if os.path.exists(key_path):
                        try:
                            self._ssh_client.connect(
                                hostname=self.host,
                                port=self.port,
                                username=self.username,
                                key_filename=key_path,
                                timeout=self.timeout
                            )
                            break
                        except:
                            continue
                else:
                    raise Exception("No SSH key or password provided, and no default keys found")
            
            print(f"[OK] Connected to {self.username}@{self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"[ERROR] SSH connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH and SFTP connections."""
        if self._sftp_client:
            try:
                self._sftp_client.close()
            except:
                pass
            self._sftp_client = None
        
        if self._ssh_client:
            try:
                self._ssh_client.close()
            except:
                pass
            self._ssh_client = None
    
    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> Tuple[Optional[str], Optional[str], int]:
        """
        Execute a command on remote host.
        
        Args:
            command: Command to execute
            timeout: Command timeout (uses connection timeout if None)
            
        Returns:
            Tuple of (stdout, stderr, exit_status)
        """
        if not self._ssh_client:
            if not self.connect():
                return None, "Connection failed", 1
        
        try:
            timeout_val = timeout if timeout is not None else self.timeout
            stdin, stdout, stderr = self._ssh_client.exec_command(command, timeout=timeout_val)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            return output, error, exit_status
            
        except Exception as e:
            return None, str(e), 1
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        create_dirs: bool = True
    ) -> bool:
        """
        Upload a file to remote host via SCP.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
            create_dirs: Create remote directories if they don't exist
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(local_path):
            print(f"[ERROR] Local file not found: {local_path}")
            return False
        
        if not self._ssh_client:
            if not self.connect():
                return False
        
        try:
            # Create SFTP client if needed
            if not self._sftp_client:
                self._sftp_client = self._ssh_client.open_sftp()
            
            # Create remote directory if needed
            if create_dirs:
                remote_dir = os.path.dirname(remote_path)
                if remote_dir:
                    self._mkdir_p(remote_dir)
            
            # Upload file
            self._sftp_client.put(local_path, remote_path)
            print(f"[OK] Uploaded {local_path} -> {self.host}:{remote_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] File upload failed: {e}")
            return False
    
    def upload_directory(
        self,
        local_dir: str,
        remote_dir: str
    ) -> bool:
        """
        Upload a directory to remote host recursively.
        
        Args:
            local_dir: Local directory path
            remote_dir: Remote directory path
            
        Returns:
            True if successful, False otherwise
        """
        local_path = Path(local_dir)
        if not local_path.exists() or not local_path.is_dir():
            print(f"[ERROR] Local directory not found: {local_dir}")
            return False
        
        try:
            # Create remote directory
            self.execute_command(f"mkdir -p {remote_dir}")
            
            # Upload files
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    remote_path = os.path.join(remote_dir, str(relative_path).replace('\\', '/'))
                    if not self.upload_file(str(file_path), remote_path):
                        return False
            
            print(f"[OK] Uploaded directory {local_dir} -> {self.host}:{remote_dir}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Directory upload failed: {e}")
            return False
    
    def _mkdir_p(self, remote_dir: str):
        """Create remote directory and parents recursively."""
        parts = remote_dir.strip('/').split('/')
        current = ''
        for part in parts:
            if not part:
                continue
            current = os.path.join(current, part) if current else part
            # Try to create directory
            self.execute_command(f"mkdir -p /{current}" if not current.startswith('/') else f"mkdir -p {current}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

