#!/bin/bash
set -e

# Fix permissions for the cache directory if running as root
if [ "$(id -u)" = "0" ]; then
    # Ensure cache directory exists and has correct permissions
    mkdir -p /app/.cache/fastembed
    chown -R appuser:appuser /app/.cache
    chmod -R 755 /app/.cache
    
    # Execute command as appuser
    exec gosu appuser "$@"
else
    # If not root, just run the command
    exec "$@"
fi

