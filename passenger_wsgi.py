import os
import sys

# Add directory paths
cwd = os.path.dirname(os.path.abspath(__file__))
if cwd not in sys.path:
    sys.path.insert(0, cwd)

backend_dir = os.path.join(cwd, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import Flask app instance
from app import app as application
