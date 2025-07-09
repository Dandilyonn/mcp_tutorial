# Quick Start Guide - AI Agents with Tool Calling and MCP Servers

## 🚀 Get Started in 5 Minutes

This quick start guide will get you up and running with AI agents and tool calling in just a few minutes!

## Prerequisites

- Python 3.8+ installed
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp_tutorial

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Create a `.env` file in the project root:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## Step 3: Test Your Setup

```bash
# Run the simple test agent
python examples/simple_test_agent.py
```

You should see output like:
```
🤖 Simple Test Agent
==================================================
✅ OpenAI API connection successful!
✅ Anthropic API connection successful!
🎉 Setup verification complete!
```

## Step 4: Try Tool Calling

```bash
# Run the tool calling agent
python agents/basic/tool_calling_agent.py
```

Try these commands:
- "What is 15 * 23 + 7?"
- "What time is it right now?"
- "Can you echo back 'Hello, World!'?"

## Step 5: Explore MCP Integration

```bash
# Run the MCP integrated agent
python agents/advanced/mcp_integrated_agent.py
```

Try these commands:
- "Send a message to #general saying 'Hello from MCP agent!'"
- "What channels are available in Slack?"
- "Send an email to john@example.com with subject 'Meeting Reminder'"

## 🎯 What You Can Do Now

### Basic Agent
```python
from examples.simple_test_agent import SimpleTestAgent

agent = SimpleTestAgent()
response = agent.chat("Hello! How are you?")
print(response)
```

### Tool Calling Agent
```python
from agents.basic.tool_calling_agent import ToolCallingAgent

agent = ToolCallingAgent()
response = agent.chat("What is 2 + 2 * 3?")
print(response)  # Will use the calculator tool
```

### MCP Integrated Agent
```python
from agents.advanced.mcp_integrated_agent import MCPIntegratedAgent

agent = MCPIntegratedAgent()
response = await agent.chat("Send a Slack message to #general")
print(response)  # Will use Slack MCP server
```

## 🔧 Customize Your Agent

### Add Custom Tools
```python
from agents.basic.tool_calling_agent import ToolCallingAgent, Tool

def my_custom_function(parameter: str) -> str:
    return f"Processed: {parameter}"

custom_tool = Tool(
    name="my_tool",
    description="My custom tool",
    function=my_custom_function,
    parameters={
        "type": "object",
        "properties": {
            "parameter": {"type": "string"}
        },
        "required": ["parameter"]
    }
)

agent = ToolCallingAgent()
agent.register_custom_tool(custom_tool)
```

### Create Your Own MCP Server
```python
# See examples/mcp_simple_server.py for a complete example
class MyMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "my_action",
                "description": "Perform my custom action",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            }
        ]
```

## 📚 Next Steps

1. **Read the Full Tutorial**: Start with [Part 1: Foundations](./docs/part1-foundations.md)
2. **Set Up Real APIs**: Configure Slack, Google, and GitHub integrations
3. **Build Your Own Agent**: Create agents for your specific use cases
4. **Join the Community**: Share your implementations and learn from others

## 🆘 Need Help?

- **Environment Issues**: Check [Part 4: Setup](./docs/part4-setup.md)
- **API Problems**: Verify your API keys and permissions
- **Tool Calling**: Review [Part 2: Tool Calling](./docs/part2-tool-calling.md)
- **MCP Integration**: See [Part 7: MCP Setup](./docs/part7-mcp-setup.md)

## 🎉 You're Ready!

You now have a working AI agent with tool calling capabilities! Explore the examples, modify the code, and start building your own agents.

**Happy coding! 🚀** 