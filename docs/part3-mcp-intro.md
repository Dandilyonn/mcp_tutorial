# Part 3: MCP Server Introduction

## What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is an open standard that enables AI models and applications to connect to external data sources and tools through a standardized interface. Think of it as a "plug-and-play" system for AI capabilities.

## Why MCP Matters

### Before MCP
- Each AI application had to implement its own integrations
- Limited to what the application developer built
- No standardization across different tools
- Difficult to extend functionality

### With MCP
- Standardized way to connect AI to any service
- Plug-and-play tool integration
- Rich ecosystem of pre-built servers
- Easy to extend with custom servers

## MCP Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   MCP Client    │    │   MCP Server    │
│                 │◄──►│                 │◄──►│                 │
│ - LLM Model     │    │ - Protocol      │    │ - Tool Logic    │
│ - Reasoning     │    │ - Connection    │    │ - API Calls     │
│ - Response Gen  │    │ - Tool Registry │    │ - Data Sources  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### 1. **MCP Client**
- Connects to MCP servers
- Manages tool registry
- Handles communication protocol
- Integrates with AI models

### 2. **MCP Server**
- Implements specific functionality
- Exposes tools and resources
- Handles authentication
- Manages data sources

### 3. **Protocol**
- Standardized communication
- Tool definitions
- Resource management
- Error handling

## Popular MCP Servers

### 1. **Slack MCP Server**
- Send and receive messages
- Manage channels and users
- Handle notifications
- Integrate with workflows

### 2. **Google APIs MCP Server**
- Gmail integration
- Google Drive access
- Calendar management
- Google Sheets operations

### 3. **GitHub MCP Server**
- Repository management
- Issue tracking
- Code review
- CI/CD integration

### 4. **File System MCP Server**
- File operations
- Directory management
- Search capabilities
- Content reading/writing

## MCP vs Traditional Tool Calling

### Traditional Approach
```python
# Hard-coded API integration
class SlackTool:
    def __init__(self, token):
        self.client = SlackClient(token)
    
    def send_message(self, channel, message):
        return self.client.chat_postMessage(
            channel=channel,
            text=message
        )

# Agent needs to know about Slack specifically
agent.tools.append(SlackTool(slack_token))
```

### MCP Approach
```python
# Generic MCP client
mcp_client = MCPClient()

# Connect to any MCP server
mcp_client.connect("slack-server")
mcp_client.connect("google-server")
mcp_client.connect("github-server")

# Agent gets tools automatically
agent.tools = mcp_client.get_tools()
```

## Benefits of MCP

### 1. **Standardization**
- Consistent interface across all tools
- Predictable behavior
- Easier to learn and use

### 2. **Modularity**
- Add/remove capabilities easily
- Mix and match servers
- Independent development

### 3. **Security**
- Centralized authentication
- Permission management
- Audit trails

### 4. **Extensibility**
- Build custom servers
- Community contributions
- Rapid innovation

## MCP Server Categories

### 1. **Communication Servers**
- Slack, Discord, Teams
- Email (Gmail, Outlook)
- SMS and messaging
- Video conferencing

### 2. **Productivity Servers**
- Google Workspace
- Microsoft 365
- Notion, Airtable
- Project management tools

### 3. **Development Servers**
- GitHub, GitLab
- CI/CD platforms
- Cloud providers
- Development tools

### 4. **Data Servers**
- Databases
- File systems
- APIs and web services
- Analytics platforms

## Example: Slack MCP Server

Let's look at how a Slack MCP server works:

### Server Definition
```python
# slack_mcp_server.py
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
)

class SlackMCPServer:
    def __init__(self):
        self.server = Server("slack")
        self.slack_client = None
        
        # Register tools
        self.server.list_tools(self.list_tools)
        self.server.call_tool(self.call_tool)
    
    def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        return ListToolsResult(
            tools=[
                Tool(
                    name="send_message",
                    description="Send a message to a Slack channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "message": {"type": "string"}
                        },
                        "required": ["channel", "message"]
                    }
                ),
                Tool(
                    name="get_channels",
                    description="List all available channels",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        )
    
    def call_tool(self, request: CallToolRequest) -> CallToolResult:
        if request.name == "send_message":
            # Parse arguments
            channel = request.arguments["channel"]
            message = request.arguments["message"]
            
            # Send message via Slack API
            result = self.slack_client.chat_postMessage(
                channel=channel,
                text=message
            )
            
            return CallToolResult(
                content=[{"type": "text", "text": f"Message sent to {channel}"}]
            )
        
        elif request.name == "get_channels":
            # Get channels from Slack API
            channels = self.slack_client.conversations_list()
            
            return CallToolResult(
                content=[{"type": "text", "text": str(channels)}]
            )
```

### Client Usage
```python
# agent_with_slack.py
from mcp.client import ClientSession, StdioServerParameters
import asyncio

async def main():
    # Connect to Slack MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["slack_mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        # Get available tools
        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools.tools]}")
        
        # Send a message
        result = await session.call_tool(
            "send_message",
            {"channel": "#general", "message": "Hello from MCP!"}
        )
        print(f"Result: {result.content}")

asyncio.run(main())
```

## MCP Server Configuration

### Environment Variables
```bash
# Slack configuration
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token

# Google configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GOOGLE_PROJECT_ID=your-project-id

# GitHub configuration
GITHUB_TOKEN=ghp-your-token
GITHUB_REPOSITORY=owner/repo
```

### Configuration Files
```yaml
# config/mcp_servers.yaml
servers:
  slack:
    command: "python"
    args: ["slack_mcp_server.py"]
    env:
      SLACK_BOT_TOKEN: "${SLACK_BOT_TOKEN}"
  
  google:
    command: "python"
    args: ["google_mcp_server.py"]
    env:
      GOOGLE_APPLICATION_CREDENTIALS: "${GOOGLE_CREDENTIALS}"
  
  github:
    command: "python"
    args: ["github_mcp_server.py"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

## Building Your Own MCP Server

### Step 1: Define Your Tools
```python
from mcp.server import Server
from mcp.types import Tool

class CustomMCPServer:
    def __init__(self):
        self.server = Server("custom")
        
        # Define your tools
        self.tools = [
            Tool(
                name="custom_action",
                description="Perform a custom action",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parameter": {"type": "string"}
                    },
                    "required": ["parameter"]
                }
            )
        ]
```

### Step 2: Implement Tool Logic
```python
    def call_tool(self, request: CallToolRequest) -> CallToolResult:
        if request.name == "custom_action":
            parameter = request.arguments["parameter"]
            
            # Your custom logic here
            result = self.perform_custom_action(parameter)
            
            return CallToolResult(
                content=[{"type": "text", "text": str(result)}]
            )
    
    def perform_custom_action(self, parameter: str):
        # Implement your custom functionality
        return f"Processed: {parameter}"
```

### Step 3: Run the Server
```python
if __name__ == "__main__":
    server = CustomMCPServer()
    stdio_server(server.server)
```

## Best Practices for MCP Servers

### 1. **Tool Design**
- Keep tools focused and single-purpose
- Provide clear descriptions
- Use proper parameter validation
- Handle errors gracefully

### 2. **Security**
- Implement proper authentication
- Validate all inputs
- Use environment variables for secrets
- Implement rate limiting

### 3. **Performance**
- Use async operations when possible
- Implement caching for expensive operations
- Handle timeouts appropriately
- Monitor resource usage

### 4. **Documentation**
- Document all tools clearly
- Provide usage examples
- Include error codes and messages
- Maintain changelog

## Next Steps

Now that you understand MCP servers, let's move on to [Part 4: Setting Up Your Development Environment](./part4-setup.md) where you'll learn how to set up everything you need to start building agents with MCP integration.

## Key Takeaways

- MCP provides a standardized way to connect AI to external tools
- MCP servers are modular and can be mixed and matched
- Popular servers include Slack, Google APIs, and GitHub
- MCP offers better security, extensibility, and standardization
- You can build custom MCP servers for specific needs

---

**Ready to set up your development environment?** Continue to [Part 4: Setting Up Your Development Environment](./part4-setup.md) 