import os
import sys

cwd = os.path.dirname(os.path.abspath(__file__))

# Ensure root directory is first in sys.path so root app.py is loaded, not backend/app.py
if cwd in sys.path:
    sys.path.remove(cwd)
sys.path.insert(0, cwd)

backend_dir = os.path.join(cwd, "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app import app as application
