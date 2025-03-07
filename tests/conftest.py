# tests/conftest.py
import sys
import os

# Add the repository root to the PYTHONPATH
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)