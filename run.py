#!/usr/bin/env python3
"""
Run script for the Business Idea Validator Streamlit app.
This script provides a convenient way to start the Streamlit app.
"""

import os
import subprocess
import sys

def main():
    """Run the Streamlit app."""
    print("Starting Business Idea Validator Streamlit app...")
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("Streamlit is installed.")
    except ImportError:
        print("Streamlit is not installed. Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
    
    # Run the Streamlit app
    print("Launching the app...")
    subprocess.call(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
