"""
CLI Entrypoint for AI Virtual Try-On Package
Enables running: python -m try_on
"""

import uvicorn
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if __name__ == "__main__":
    print("Starting Nutz 2D Virtual Try-On Studio on http://localhost:8000 ...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

