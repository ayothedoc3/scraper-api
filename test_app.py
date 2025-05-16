#!/usr/bin/env python3
"""
Test script for the Business Idea Validator Streamlit app.
This script verifies that all required dependencies are installed and the app can be imported.
"""

import importlib
import sys

def test_dependencies():
    """Test that all required dependencies are installed."""
    required_modules = [
        "streamlit",
        "plotly",
        "pandas",
        "matplotlib",
        "numpy",
        "requests",
        "pydantic",
        "SimplerLLM"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module} is installed")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} is NOT installed")
    
    return missing_modules

def test_app_imports():
    """Test that the app can be imported."""
    try:
        # Only import the app, don't run it
        import app
        print("✓ App can be imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing app: {str(e)}")
        return False

def main():
    """Run the tests."""
    print("Testing Business Idea Validator Streamlit app setup...")
    print("\nChecking dependencies:")
    missing_modules = test_dependencies()
    
    if missing_modules:
        print(f"\nMissing dependencies: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("\nChecking app imports:")
    app_import_success = test_app_imports()
    
    if not app_import_success:
        print("\nThere was an error importing the app. Please check the error message above.")
        return False
    
    print("\nAll tests passed! The app should run correctly.")
    print("Run the app using: python run.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
