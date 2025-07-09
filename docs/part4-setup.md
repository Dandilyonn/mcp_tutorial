# Part 4: Setting Up Your Development Environment

## Prerequisites

Before we begin, make sure you have the following installed:

- **Python 3.8+** (we'll use Python 3.11 for this tutorial)
- **Git** for version control
- **A code editor** (VS Code, PyCharm, or your preferred editor)
- **Command line access** (Terminal on Mac/Linux, Command Prompt/PowerShell on Windows)

## Step 1: Clone the Tutorial Repository

```bash
# Clone this repository
git clone <your-repo-url>
cd mcp_tutorial

# Verify you're in the right directory
ls -la
```

You should see the project structure we created earlier.

## Step 2: Set Up Python Environment

### Option A: Using venv (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation
which python  # Should show path to venv
```

### Option B: Using conda

```bash
# Create a conda environment
conda create -n mcp_tutorial python=3.11

# Activate the environment
conda activate mcp_tutorial
```

## Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import openai, anthropic, mcp; print('All packages installed successfully!')"
```

## Step 4: Set Up API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add your API keys to the `.env` file:

```bash
# .env
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Slack API Keys (we'll set these up later)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token

# Google API Keys (we'll set these up later)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
GOOGLE_PROJECT_ID=your-google-project-id

# GitHub Token (we'll set these up later)
GITHUB_TOKEN=ghp-your-github-token
```

## Step 5: Verify Your Setup

Let's create a simple test script to verify everything is working:

```python
# test_setup.py
import os
from dotenv import load_dotenv
import openai
import anthropic

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API connection"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello! Just testing the connection."}],
            max_tokens=10
        )
        print("✅ OpenAI API connection successful!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_anthropic():
    """Test Anthropic API connection"""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello! Just testing the connection."}]
        )
        print("✅ Anthropic API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Anthropic API connection failed: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("🔍 Testing environment setup...")
    
    # Check Python version
    import sys
    print(f"Python version: {sys.version}")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        return False
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key and openai_key.startswith("sk-"):
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured or invalid")
    
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        print("✅ Anthropic API key configured")
    else:
        print("❌ Anthropic API key not configured or invalid")
    
    return True

if __name__ == "__main__":
    print("🚀 Testing MCP Tutorial Setup\n")
    
    env_ok = test_environment()
    if env_ok:
        openai_ok = test_openai()
        anthropic_ok = test_anthropic()
        
        if openai_ok and anthropic_ok:
            print("\n🎉 Setup complete! You're ready to start building agents.")
        else:
            print("\n⚠️  Some API connections failed. Check your API keys.")
    else:
        print("\n❌ Environment setup incomplete. Please check your configuration.")
```

Run the test:

```bash
python test_setup.py
```

## Step 6: Install MCP Servers

### Install Official MCP Servers

```bash
# Install MCP server packages
pip install mcp-server-slack
pip install mcp-server-google
pip install mcp-server-github
pip install mcp-server-filesystem
```

### Verify MCP Installation

```python
# test_mcp.py
import asyncio
from mcp.client import ClientSession, StdioServerParameters

async def test_mcp_connection():
    """Test basic MCP functionality"""
    try:
        # Test with a simple echo server
        server_params = StdioServerParameters(
            command="echo",
            args=["Hello MCP!"]
        )
        
        print("✅ MCP client library installed successfully!")
        return True
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
```

## Step 7: Set Up Development Tools

### Install Code Formatting Tools

```bash
# Install development tools
pip install black flake8 mypy

# Create configuration files
```

### Create `.black` configuration

```ini
# .black
[black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Create `.flake8` configuration

```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv,venv
```

## Step 8: Create Project Structure

Let's create the complete project structure:

```bash
# Create additional directories
mkdir -p examples/part1 examples/part2 examples/part3
mkdir -p agents/basic agents/advanced
mkdir -p configs/servers configs/agents
mkdir -p tests/unit tests/integration
mkdir -p docs/images

# Create initial files
touch examples/__init__.py
touch agents/__init__.py
touch tests/__init__.py
```

## Step 9: Set Up Version Control

```bash
# Initialize git repository (if not already done)
git init

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# API keys and credentials
credentials/
*.json
!requirements.json

# Test coverage
.coverage
htmlcov/

# MCP server data
.mcp/
EOF

# Add files to git
git add .
git commit -m "Initial setup: Project structure and dependencies"
```

## Step 10: Create a Simple Test Agent

Let's create a basic agent to test our setup:

```python
# examples/simple_test_agent.py
import os
from dotenv import load_dotenv
import openai
from typing import Dict, Any

class SimpleTestAgent:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def chat(self, message: str) -> str:
        """Simple chat function to test the agent"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    """Test the simple agent"""
    print("🤖 Testing Simple AI Agent\n")
    
    agent = SimpleTestAgent()
    
    # Test basic conversation
    test_messages = [
        "Hello! How are you?",
        "What can you help me with?",
        "Can you explain what an AI agent is?"
    ]
    
    for message in test_messages:
        print(f"User: {message}")
        response = agent.chat(message)
        print(f"Agent: {response}\n")
    
    print("✅ Simple agent test completed!")

if __name__ == "__main__":
    main()
```

## Step 11: Run Your First Test

```bash
# Test the simple agent
python examples/simple_test_agent.py
```

## Troubleshooting Common Issues

### Issue 1: Python Version
```bash
# Check Python version
python --version

# If you need to install Python 3.11
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Issue 2: API Key Problems
```bash
# Check if .env file is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_KEY:', os.getenv('OPENAI_API_KEY')[:10] + '...' if os.getenv('OPENAI_API_KEY') else 'Not found')"
```

### Issue 3: Package Installation Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Issue 4: Virtual Environment Issues
```bash
# Deactivate and recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Next Steps

Congratulations! Your development environment is now set up. You can:

1. **Test your setup** by running the test scripts
2. **Start building** with [Part 5: Creating Your First Agent](./part5-first-agent.md)
3. **Explore examples** in the `examples/` directory
4. **Customize your environment** based on your preferences

## Verification Checklist

- [ ] Python 3.8+ installed and working
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] API keys configured in `.env` file
- [ ] Basic agent test passes
- [ ] Git repository initialized
- [ ] Development tools installed (black, flake8)
- [ ] Project structure created

## Key Takeaways

- Always use virtual environments for Python projects
- Keep API keys secure in `.env` files
- Test your setup before proceeding
- Use version control from the start
- Install development tools for code quality

---

**Ready to build your first agent?** Continue to [Part 5: Creating Your First Agent](./part5-first-agent.md) 