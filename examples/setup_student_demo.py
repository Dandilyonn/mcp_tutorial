#!/usr/bin/env python3
"""
Setup Script for Streamlit MCP Learning Demo

This script helps college students quickly set up and run the MCP learning demo.
It checks dependencies, installs missing packages, and provides clear instructions.

Usage:
    python setup_student_demo.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: pip is not available")
        return False

def install_package(package_name, version=None):
    """Install a Python package"""
    package_spec = f"{package_name}>={version}" if version else package_name
    
    try:
        print(f"📦 Installing {package_spec}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", package_spec
        ], check=True, capture_output=True)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def setup_demo():
    """Main setup function"""
    print("🌍 Streamlit MCP Learning Demo Setup")
    print("=" * 50)
    print("This script will help you set up the MCP learning demo.")
    print()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        return False
    
    # Required packages
    required_packages = [
        ("streamlit", "1.28.0"),
        ("python-dotenv", "1.0.0"),
    ]
    
    print("\n📋 Checking required packages...")
    
    # Check and install packages
    for package, version in required_packages:
        if check_package(package.replace("-", "_")):
            print(f"✅ {package} is already installed")
        else:
            if not install_package(package, version):
                return False
    
    print("\n🎉 Setup completed successfully!")
    return True

def show_instructions():
    """Show instructions for running the demo"""
    print("\n" + "=" * 50)
    print("🚀 READY TO RUN THE DEMO!")
    print("=" * 50)
    
    print("""
To start the MCP learning demo:

1. Open a terminal/command prompt
2. Navigate to the examples directory:
   cd examples

3. Run the Streamlit app:
   streamlit run streamlit_mcp_learning_demo.py

4. Open your web browser to the URL shown in the terminal
   (usually http://localhost:8501)

5. Start learning about MCP servers! 🌍

Troubleshooting:
- If you get a "command not found" error, try:
  python -m streamlit run streamlit_mcp_learning_demo.py
  
- If the port is busy, try:
  streamlit run streamlit_mcp_learning_demo.py --server.port 8502

Need help? Check the README_STREAMLIT_LEARNING.md file for detailed instructions.
""")

def main():
    """Main function"""
    try:
        if setup_demo():
            show_instructions()
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            print("💡 Try running: pip install streamlit python-dotenv")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 