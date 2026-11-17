"""
AI Virtual Try-On Package (CatVTON + SegFormer)
Author: Nutz Virtual Fitting Team
Version: 2.0.0
"""

import sys
import os

# Ensure project root is in path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Expose core components
try:
    from main import app
except ImportError:
    app = None

try:
    from src.preprocessing.classifier import classify_garment
except ImportError:
    classify_garment = None

__all__ = ["app", "classify_garment"]

