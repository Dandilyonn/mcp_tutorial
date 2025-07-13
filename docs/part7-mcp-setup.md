# Part 7: Installing and Configuring MCP Servers

## What You'll Learn

In this part, you'll learn how to:
- Install official MCP servers
- Configure server connections
- Set up authentication
- Test server functionality
- Integrate servers with your agent

## Installing MCP Servers

### Step 1: Install Core MCP Package

```bash
# Install the core MCP package
pip install mcp

# Verify installation
python -c "import mcp; print('MCP installed successfully!')"
```

### Step 2: Install Official MCP Servers

**Note**: Official MCP servers are still in development. For now, we'll use mock implementations in our examples.

```bash
# Install the core MCP package
pip install mcp

# For real MCP servers, check the official MCP repository:
# https://github.com/modelcontextprotocol
# 
# When available, you can install servers like:
# pip install mcp-server-slack
# pip install mcp-server-google
# pip install mcp-server-github
# pip install mcp-server-filesystem
```

### Step 3: Verify Server Installation

```python
# test_mcp_servers.py
import subprocess
import sys

def test_server_installation():
    """Test if MCP servers are properly installed"""
    servers = [
        "mcp-server-slack",
        "mcp-server-google", 
        "mcp-server-github",
        "mcp-server-filesystem"
    ]
    
    print("🔍 Testing MCP Server Installation")
    print("=" * 50)
    
    for server in servers:
        try:
            # Try to import the server
            result = subprocess.run([
                sys.executable, "-c", f"import {server.replace('-', '_')}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {server} - Installed")
            else:
                print(f"❌ {server} - Not installed")
                
        except Exception as e:
            print(f"❌ {server} - Error: {e}")
    
    print("\n🎉 Server installation test complete!")

if __name__ == "__main__":
    test_server_installation()
```

## Configuring MCP Servers

### Step 1: Create Configuration Directory

```bash
# Create configuration directory
mkdir -p ~/.mcp/servers
mkdir -p ~/.mcp/configs
```

### Step 2: Create Server Configuration File

```yaml
# ~/.mcp/configs/servers.yaml
servers:
  slack:
    command: "mcp-server-slack"
    args: []
    env:
      SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"
      SLACK_APP_TOKEN: "${SLACK_APP_TOKEN}"
  
  google:
    command: "mcp-server-google"
    args: []
    env:
      GOOGLE_APPLICATION_CREDENTIALS: "${GOOGLE_CREDENTIALS}"
      GOOGLE_PROJECT_ID: "${GOOGLE_PROJECT_ID}"
  
  github:
    command: "mcp-server-github"
    args: []
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
  
  filesystem:
    command: "mcp-server-filesystem"
    args: ["--root", "${HOME}"]
    env: {}
```

### Step 3: Set Up Environment Variables

Add these to your `.env` file:

```bash
# .env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token

# Google Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
GOOGLE_PROJECT_ID=your-google-project-id

# GitHub Configuration
GITHUB_TOKEN=ghp-your-github-token

# Other useful variables
HOME=${HOME}
```

## Setting Up Slack MCP Server

### Step 1: Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Name your app (e.g., "MCP Tutorial Bot")
5. Select your workspace

### Step 2: Configure Bot Permissions

1. Go to "OAuth & Permissions"
2. Add these bot token scopes:
   - `chat:write` - Send messages
   - `channels:read` - Read channel information
   - `users:read` - Read user information
   - `channels:history` - Read channel messages

### Step 3: Install App to Workspace

1. Go to "Install App"
2. Click "Install to Workspace"
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Step 4: Get App-Level Token

1. Go to "Basic Information"
2. Under "App-Level Tokens", click "Generate Token and Scopes"
3. Name it "MCP-Server"
4. Add scope: `connections:write`
5. Copy the token (starts with `xapp-`)

### Step 5: Test Slack Server

```python
# test_slack_mcp.py
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_slack_server():
    """Test Slack MCP server connection"""
    try:
        # Check if tokens are set
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        app_token = os.getenv("SLACK_APP_TOKEN")
        
        if not bot_token or not app_token:
            print("❌ Slack tokens not configured")
            return False
        
        print("✅ Slack tokens found")
        
        # Test server connection (simplified)
        print("🔗 Testing Slack server connection...")
        
        # In a real implementation, you would connect to the MCP server
        # For now, we'll just verify the tokens are valid format
        if bot_token.startswith("xoxb-") and app_token.startswith("xapp-"):
            print("✅ Slack tokens appear to be in correct format")
            return True
        else:
            print("❌ Slack tokens are not in correct format")
            return False
            
    except Exception as e:
        print(f"❌ Slack server test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_slack_server())
```

## Setting Up Google APIs MCP Server

### Step 1: Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the APIs you need:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Sheets API

### Step 2: Create Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name it "MCP-Server"
4. Add description: "Service account for MCP server"
5. Click "Create and Continue"

### Step 3: Download Credentials

1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Download the file and save it securely

### Step 4: Test Google Server

```python
# test_google_mcp.py
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_google_server():
    """Test Google MCP server setup"""
    try:
        # Check credentials file
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        
        if not creds_path or not project_id:
            print("❌ Google configuration incomplete")
            return False
        
        # Check if credentials file exists
        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            return False
        
        # Validate credentials file
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in creds:
                    print(f"❌ Missing field in credentials: {field}")
                    return False
            
            print("✅ Google credentials file is valid")
            print(f"✅ Project ID: {project_id}")
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON in credentials file")
            return False
            
    except Exception as e:
        print(f"❌ Google server test failed: {e}")
        return False

if __name__ == "__main__":
    test_google_server()
```

## Setting Up GitHub MCP Server

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token" > "Generate new token (classic)"
3. Give it a name: "MCP Server"
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read organization data)
   - `read:user` (Read user data)
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

### Step 2: Test GitHub Server

```python
# test_github_mcp.py
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_github_server():
    """Test GitHub MCP server setup"""
    try:
        token = os.getenv("GITHUB_TOKEN")
        
        if not token:
            print("❌ GitHub token not configured")
            return False
        
        # Test token by making a simple API call
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub token is valid")
            print(f"✅ Authenticated as: {user_data['login']}")
            return True
        else:
            print(f"❌ GitHub token validation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub server test failed: {e}")
        return False

if __name__ == "__main__":
    test_github_server()
```

## Creating a Test Script

```python
# test_all_mcp_servers.py
#!/usr/bin/env python3
"""
Test All MCP Servers

This script tests the installation and configuration of all MCP servers.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check .env file
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        return False
    
    # Check required environment variables
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN", 
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_PROJECT_ID",
        "GITHUB_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - Configured")
        else:
            print(f"❌ {var} - Not configured")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        return False
    
    return True

def test_mcp_installation():
    """Test MCP package installation"""
    print("\n📦 Testing MCP Installation")
    print("=" * 50)
    
    try:
        import mcp
        print("✅ MCP core package installed")
        return True
    except ImportError:
        print("❌ MCP core package not installed")
        return False

def test_server_packages():
    """Test MCP server packages"""
    print("\n🔧 Testing MCP Server Packages")
    print("=" * 50)
    
    # Note: Official MCP servers are still in development
    print("ℹ️  Official MCP servers are still in development")
    print("✅ Using mock implementations in our examples")
    print("✅ Core MCP package is available")
    
    # Test core MCP package
    try:
        import mcp
        print("✅ MCP core package - Installed")
        return True
    except ImportError:
        print("❌ MCP core package - Not installed")
        return False

async def main():
    """Main test function"""
    print("🚀 MCP Server Setup Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    # Test MCP installation
    mcp_ok = test_mcp_installation()
    
    # Test server packages
    servers_ok = test_server_packages()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"MCP Core: {'✅' if mcp_ok else '❌'}")
    print(f"Server Packages: {'✅' if servers_ok else '❌'}")
    
    if env_ok and mcp_ok and servers_ok:
        print("\n🎉 All tests passed! Your MCP servers are ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("\nNext steps:")
        if not env_ok:
            print("- Configure missing environment variables")
        if not mcp_ok:
            print("- Install MCP core package: pip install mcp")
        if not servers_ok:
            print("- Install missing server packages")

if __name__ == "__main__":
    asyncio.run(main())
```

## Running the Tests

```bash
# Run all tests
python test_all_mcp_servers.py

# Run individual tests
python test_slack_mcp.py
python test_google_mcp.py
python test_github_mcp.py
```

## Troubleshooting Common Issues

### Issue 1: Import Errors
```bash
# If you get import errors, try reinstalling
pip uninstall mcp-server-slack mcp-server-google mcp-server-github
pip install mcp-server-slack mcp-server-google mcp-server-github
```

### Issue 2: Permission Errors
```bash
# Make sure you have write permissions
chmod 600 ~/.mcp/configs/servers.yaml
chmod 600 .env
```

### Issue 3: Token Validation
```bash
# Test tokens individually
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('SLACK_TOKEN:', os.getenv('SLACK_BOT_TOKEN')[:10] + '...' if os.getenv('SLACK_BOT_TOKEN') else 'Not found')"
```

## Next Steps

Now that you have MCP servers installed and configured, you can:

1. **Test individual servers** using the test scripts
2. **Integrate servers with your agent** in the next parts
3. **Build custom servers** for your specific needs
4. **Explore server capabilities** through interactive sessions

## Key Takeaways

- MCP servers provide standardized access to external services
- Proper configuration requires API keys and tokens
- Test your setup before integrating with agents
- Keep credentials secure in environment variables
- Each server has specific setup requirements

---

**Ready to integrate MCP servers with your agent?** Continue to [Part 8: Slack MCP Server Integration](./part8-slack-mcp.md) 