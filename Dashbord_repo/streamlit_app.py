"""
Entry point for Streamlit Cloud deployment.
This file allows Streamlit Cloud to find and run the app from the repository root.
"""
import sys
import os

# Add Dashboard-JS to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Dashboard-JS"))

# Import and run the app
from app import *
