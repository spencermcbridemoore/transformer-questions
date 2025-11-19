# JupyterLab configuration for remote access
# This config allows remote connections via SSH tunnel

c = get_config()

# Server settings
c.ServerApp.ip = '0.0.0.0'  # Listen on all interfaces
c.ServerApp.port = 8888
c.ServerApp.open_browser = False  # Don't try to open browser on remote
c.ServerApp.allow_origin = '*'  # Allow any origin (use with tunnel)
c.ServerApp.allow_root = False  # Security: don't allow root
c.ServerApp.token = ''  # Will generate token on startup
c.ServerApp.password = ''  # No password (use token instead)

# Allow Colab connection if needed
c.ServerApp.allow_origin_pat = 'https://.*\.colab\.research\.google\.com'

# Additional security settings
c.ServerApp.disable_check_xsrf = False  # Keep XSRF protection
c.ServerApp.terminals_enabled = True  # Enable terminal access

# Notebook settings
c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.open_browser = False

