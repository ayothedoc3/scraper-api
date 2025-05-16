#!/usr/bin/env python3
"""
Script to check if the required API keys are set in the environment.
This script helps users verify that their API keys are properly configured.
"""

import os
import sys
from pathlib import Path
import re

def check_env_file():
    """Check if .env file exists and contains the required API keys."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found.")
        return False, {}
    
    print("✅ .env file found.")
    
    # Read .env file
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Extract API keys
    scraper_api_key = re.search(r'SCRAPER_API_KEY\s*=\s*[\'"]?([^\'"]+)[\'"]?', env_content)
    openai_api_key = re.search(r'OPENAI_API_KEY\s*=\s*[\'"]?([^\'"]+)[\'"]?', env_content)
    
    api_keys = {}
    if scraper_api_key:
        api_keys['SCRAPER_API_KEY'] = scraper_api_key.group(1)
    if openai_api_key:
        api_keys['OPENAI_API_KEY'] = openai_api_key.group(1)
    
    return True, api_keys

def check_python_file():
    """Check if API keys are hardcoded in test_enhanced.py."""
    py_path = Path('test_enhanced.py')
    
    if not py_path.exists():
        print("❌ test_enhanced.py file not found.")
        return False, {}
    
    print("✅ test_enhanced.py file found.")
    
    # Read Python file
    with open(py_path, 'r') as f:
        py_content = f.read()
    
    # Extract API keys
    scraper_api_key = re.search(r'SCRAPER_API_KEY\s*=\s*[\'"]([^\'"]+)[\'"]', py_content)
    openai_api_key = re.search(r'OPENAI_API_KEY\s*=\s*[\'"]([^\'"]+)[\'"]', py_content)
    
    api_keys = {}
    if scraper_api_key:
        api_keys['SCRAPER_API_KEY'] = scraper_api_key.group(1)
    if openai_api_key:
        api_keys['OPENAI_API_KEY'] = openai_api_key.group(1)
    
    return True, api_keys

def check_env_variables():
    """Check if API keys are set as environment variables."""
    api_keys = {}
    
    scraper_api_key = os.environ.get('SCRAPER_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    
    if scraper_api_key:
        api_keys['SCRAPER_API_KEY'] = scraper_api_key
    if openai_api_key:
        api_keys['OPENAI_API_KEY'] = openai_api_key
    
    return api_keys

def main():
    """Check if the required API keys are set."""
    print("Checking API keys configuration...")
    
    # Check .env file
    env_exists, env_keys = check_env_file()
    
    # Check Python file
    py_exists, py_keys = check_python_file()
    
    # Check environment variables
    env_var_keys = check_env_variables()
    
    # Combine all keys (environment variables take precedence)
    all_keys = {**py_keys, **env_keys, **env_var_keys}
    
    # Check if all required keys are present
    missing_keys = []
    if 'SCRAPER_API_KEY' not in all_keys:
        missing_keys.append('SCRAPER_API_KEY')
    if 'OPENAI_API_KEY' not in all_keys:
        missing_keys.append('OPENAI_API_KEY')
    
    # Print results
    print("\nAPI Keys Status:")
    
    if 'SCRAPER_API_KEY' in all_keys:
        key = all_keys['SCRAPER_API_KEY']
        masked_key = key[:4] + '*' * (len(key) - 8) + key[-4:] if len(key) > 8 else '****'
        print(f"✅ SCRAPER_API_KEY: {masked_key}")
    else:
        print("❌ SCRAPER_API_KEY: Not found")
    
    if 'OPENAI_API_KEY' in all_keys:
        key = all_keys['OPENAI_API_KEY']
        masked_key = key[:4] + '*' * (len(key) - 8) + key[-4:] if len(key) > 8 else '****'
        print(f"✅ OPENAI_API_KEY: {masked_key}")
    else:
        print("❌ OPENAI_API_KEY: Not found")
    
    # Provide guidance if keys are missing
    if missing_keys:
        print("\n⚠️ Some API keys are missing. Please set them using one of these methods:")
        print("1. Create a .env file with the following content:")
        for key in missing_keys:
            print(f"   {key}=your_api_key_here")
        print("2. Set them as environment variables:")
        for key in missing_keys:
            if sys.platform.startswith('win'):
                print(f"   set {key}=your_api_key_here")
            else:
                print(f"   export {key}=your_api_key_here")
        print("3. Hardcode them in test_enhanced.py (not recommended for security reasons)")
        return False
    
    print("\n✅ All required API keys are configured.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
