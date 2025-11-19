#!/bin/bash
# Bash script to create SSH tunnel for Jupyter
# Usage: bash tunnel.sh [host] [port]

set -e

HOST=${1:-"your-remote-host"}
PORT=${2:-8888}
REMOTE_PORT=${3:-8888}

if [ "$HOST" = "your-remote-host" ]; then
    echo "Usage: bash tunnel.sh <host> [local_port] [remote_port]"
    echo "Example: bash tunnel.sh my-gpu-server 8888 8888"
    exit 1
fi

echo "Creating SSH tunnel for Jupyter..."
echo "Host: $HOST"
echo "Local Port: $PORT -> Remote Port: $REMOTE_PORT"
echo ""
echo "Once connected, access Jupyter at: http://localhost:$PORT"
echo "Press Ctrl+C to close the tunnel"
echo ""

ssh -L ${PORT}:localhost:${REMOTE_PORT} -N $HOST

