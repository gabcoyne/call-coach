"""
Launcher script for Horizon deployment.
This ensures the package is installed before importing the server.
"""
import subprocess
import sys
from pathlib import Path

# Install the package in editable mode if not already installed
try:
    import coaching_mcp
except ImportError:
    print("Installing coaching_mcp package...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
    print("Package installed successfully")

# Now import and expose the server
from coaching_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
