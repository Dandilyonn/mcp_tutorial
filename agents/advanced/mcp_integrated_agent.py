#!/usr/bin/env python3
"""
MCP Integrated Agent - Advanced AI agent with MCP server integration

This agent demonstrates:
- Integration with multiple MCP servers
- Real-world tool calling scenarios
- Error handling and fallback strategies
- Conversation management with external tools
- Practical use cases for AI agents

This is a comprehensive example showing how to build production-ready agents.
"""

import os
import json
import asyncio
import sys
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
except ImportError:
    print("❌ OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

# Note: In a real implementation, you would import actual MCP libraries
# For this tutorial, we'll create mock MCP servers to demonstrate the concept

class MockMCPServer:
    """Mock MCP server for demonstration purposes"""
    
    def __init__(self, name: str, tools: List[Dict[str, Any]]):
        self.name = name
        self.tools = tools
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return available tools"""
        return self.tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock tool execution"""
        # Simulate async operation
        await asyncio.sleep(0.1)
        
        # Find the tool
        tool = next((t for t in self.tools if t["name"] == name), None)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        
        # Mock responses based on tool name
        if name == "send_message":
            return {
                "success": True,
                "message": f"Message sent to {arguments.get('channel', 'unknown')}",
                "content": arguments.get("message", "")
            }
        elif name == "get_channels":
            return {
                "channels": [
                    {"id": "C123", "name": "general"},
                    {"id": "C456", "name": "random"},
                    {"id": "C789", "name": "announcements"}
                ]
            }
        elif name == "send_email":
            return {
                "success": True,
                "message": f"Email sent to {arguments.get('to', 'unknown')}",
                "subject": arguments.get("subject", "")
            }
        elif name == "create_calendar_event":
            return {
                "success": True,
                "event_id": "event_123",
                "title": arguments.get("title", "New Event"),
                "start_time": arguments.get("start_time", "")
            }
        elif name == "search_repositories":
            return {
                "repositories": [
                    {"name": "mcp-tutorial", "description": "AI Agent Tutorial"},
                    {"name": "awesome-mcp", "description": "MCP Resources"}
                ]
            }
        else:
            return {"error": f"Mock tool '{name}' not implemented"}

class MCPIntegratedAgent:
    """Advanced AI agent with MCP server integration"""
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize the agent with MCP servers"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
        self.mcp_servers: Dict[str, MockMCPServer] = {}
        
        # Initialize MCP servers
        self._initialize_mcp_servers()
    
    def _initialize_mcp_servers(self):
        """Initialize mock MCP servers"""
        
        # Slack MCP Server
        slack_tools = [
            {
                "name": "send_message",
                "description": "Send a message to a Slack channel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "description": "Channel name or ID"},
                        "message": {"type": "string", "description": "Message content"}
                    },
                    "required": ["channel", "message"]
                }
            },
            {
                "name": "get_channels",
                "description": "List all available Slack channels",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        self.mcp_servers["slack"] = MockMCPServer("slack", slack_tools)
        
        # Google MCP Server
        google_tools = [
            {
                "name": "send_email",
                "description": "Send an email via Gmail",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "create_calendar_event",
                "description": "Create a Google Calendar event",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Event title"},
                        "start_time": {"type": "string", "description": "Event start time (ISO format)"},
                        "end_time": {"type": "string", "description": "Event end time (ISO format)"},
                        "description": {"type": "string", "description": "Event description"}
                    },
                    "required": ["title", "start_time"]
                }
            }
        ]
        self.mcp_servers["google"] = MockMCPServer("google", google_tools)
        
        # GitHub MCP Server
        github_tools = [
            {
                "name": "search_repositories",
                "description": "Search GitHub repositories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "language": {"type": "string", "description": "Programming language filter"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_issue",
                "description": "Create a GitHub issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository": {"type": "string", "description": "Repository name (owner/repo)"},
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue description"}
                    },
                    "required": ["repository", "title"]
                }
            }
        ]
        self.mcp_servers["github"] = MockMCPServer("github", github_tools)
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all MCP servers"""
        all_tools = []
        for server_name, server in self.mcp_servers.items():
            for tool in server.list_tools():
                # Add server prefix to tool name to avoid conflicts
                tool_copy = tool.copy()
                tool_copy["name"] = f"{server_name}_{tool['name']}"
                tool_copy["description"] = f"[{server_name.upper()}] {tool['description']}"
                all_tools.append(tool_copy)
        return all_tools
    
    def add_to_history(self, role: str, content: str, tool_calls: Optional[List] = None):
        """Add a message to conversation history"""
        message = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.conversation_history.append(message)
        
        # Keep only last 30 messages to avoid token limits
        if len(self.conversation_history) > 30:
            self.conversation_history = self.conversation_history[-30:]
    
    async def chat(self, message: str) -> str:
        """Process a user message and return a response"""
        try:
            # Add user message to history
            self.add_to_history("user", message)
            
            # Prepare messages for API call
            messages = [
                {
                    "role": "system",
                    "content": """You are an advanced AI assistant with access to multiple external services through MCP servers.

Available services:
- Slack: Send messages, manage channels
- Google: Send emails, manage calendar
- GitHub: Search repositories, create issues

When a user asks for something that requires external services, use the appropriate tools.
Always explain what you're doing and provide helpful responses.
If a tool call fails, try alternative approaches or explain the limitation."""
                }
            ] + self.conversation_history
            
            # Get available tools
            tools = self.get_all_tools()
            
            # Convert to OpenAI format
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call tools
            if response_message.tool_calls:
                # Add the assistant's message (with tool calls) to history
                self.add_to_history(
                    "assistant", 
                    response_message.content or "",
                    response_message.tool_calls
                )
                
                # Execute each tool call
                tool_results = []
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Parse server and tool name
                    if "_" in tool_name:
                        server_name, actual_tool_name = tool_name.split("_", 1)
                        server = self.mcp_servers.get(server_name)
                        
                        if server:
                            result = await server.call_tool(actual_tool_name, arguments)
                            tool_results.append(result)
                            
                            # Add tool result to history
                            self.add_to_history(
                                "tool",
                                json.dumps(result),
                                [{"id": tool_call.id, "type": "tool_call"}]
                            )
                        else:
                            error_msg = f"Server '{server_name}' not found"
                            tool_results.append({"error": error_msg})
                            self.add_to_history(
                                "tool",
                                error_msg,
                                [{"id": tool_call.id, "type": "tool_call"}]
                            )
                    else:
                        error_msg = f"Invalid tool name format: {tool_name}"
                        tool_results.append({"error": error_msg})
                        self.add_to_history(
                            "tool",
                            error_msg,
                            [{"id": tool_call.id, "type": "tool_call"}]
                        )
                
                # Generate final response with tool results
                final_messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Use the tool results to provide a comprehensive response to the user. If any tools failed, explain what happened and suggest alternatives."
                    }
                ] + self.conversation_history
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=final_messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                assistant_message = final_response.choices[0].message.content
                self.add_to_history("assistant", assistant_message)
                
                return assistant_message
            else:
                # No tool calls, just return the response
                assistant_message = response_message.content
                self.add_to_history("assistant", assistant_message)
                return assistant_message
                
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def list_available_services(self) -> List[str]:
        """List all available MCP services"""
        return list(self.mcp_servers.keys())
    
    def get_service_tools(self, service_name: str) -> List[str]:
        """Get tools available for a specific service"""
        server = self.mcp_servers.get(service_name)
        if server:
            return [tool["name"] for tool in server.list_tools()]
        return []
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get information about the current conversation"""
        tool_calls = sum(1 for msg in self.conversation_history if "tool_calls" in msg)
        return {
            "message_count": len(self.conversation_history),
            "tool_calls": tool_calls,
            "available_services": self.list_available_services(),
            "model": self.model
        }

async def demo_mcp_integration():
    """Demonstrate MCP integration capabilities"""
    print("🔧 MCP Integration Demonstration")
    print("=" * 50)
    
    try:
        agent = MCPIntegratedAgent()
        
        # Show available services
        services = agent.list_available_services()
        print(f"Available services: {services}\n")
        
        # Show tools for each service
        for service in services:
            tools = agent.get_service_tools(service)
            print(f"{service.upper()} tools: {tools}")
        print()
        
        # Test cases
        test_cases = [
            "Send a message to the #general channel saying 'Hello from MCP agent!'",
            "What channels are available in Slack?",
            "Send an email to john@example.com with subject 'Meeting Reminder' and body 'Don't forget our meeting tomorrow'",
            "Create a calendar event for tomorrow at 2 PM titled 'Team Standup'",
            "Search for repositories related to 'machine learning'",
            "Can you help me organize a team meeting? I need to send a Slack message and create a calendar event."
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case}")
            print(f"User: {test_case}")
            response = await agent.chat(test_case)
            print(f"Agent: {response}\n")
        
        # Show conversation summary
        summary = agent.get_conversation_summary()
        print(f"📊 Conversation Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def interactive_session():
    """Start an interactive session with MCP integration"""
    print("💬 Interactive MCP Integration Session")
    print("Type 'quit' to exit, 'reset' to clear history, 'services' to list services, 'summary' for info\n")
    
    try:
        agent = MCPIntegratedAgent()
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                continue
            elif user_input.lower() == 'services':
                services = agent.list_available_services()
                print(f"🔧 Available services: {services}")
                for service in services:
                    tools = agent.get_service_tools(service)
                    print(f"  {service}: {tools}")
                continue
            elif user_input.lower() == 'summary':
                summary = agent.get_conversation_summary()
                print(f"📊 Summary: {summary}")
                continue
            elif not user_input:
                continue
            
            response = await agent.chat(user_input)
            print(f"Agent: {response}\n")
            
    except KeyboardInterrupt:
        print("\n👋 Session interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Session error: {e}")

async def main():
    """Main function"""
    print("🤖 MCP Integrated Agent")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to the .env file")
        return
    
    print("Choose an option:")
    print("1. Run MCP integration demonstration")
    print("2. Start interactive session")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await demo_mcp_integration()
        elif choice == "2":
            await interactive_session()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main()) 