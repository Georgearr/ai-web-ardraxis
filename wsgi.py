import os
import sys

cwd = os.path.dirname(os.path.abspath(__file__))
if cwd not in sys.path:
    sys.path.insert(0, cwd)

backend_dir = os.path.join(cwd, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app

if __name__ == "__main__":
    app.run()
