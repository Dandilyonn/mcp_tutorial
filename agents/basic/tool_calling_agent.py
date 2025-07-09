#!/usr/bin/env python3
"""
Tool Calling Agent - A basic AI agent with tool calling capabilities

This agent demonstrates:
- Tool definition and registration
- Dynamic tool calling based on user requests
- Error handling and validation
- Conversation management

This serves as a foundation for more advanced agents.
"""

import os
import json
import sys
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
except ImportError:
    print("❌ OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

class Tool:
    """Represents a tool that the agent can call"""
    
    def __init__(self, name: str, description: str, function: Callable, 
                 parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def call(self, arguments: Dict[str, Any]) -> Any:
        """Execute the tool with given arguments"""
        try:
            return self.function(**arguments)
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

class ToolRegistry:
    """Manages available tools for the agent"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI format"""
        return [tool.to_openai_format() for tool in self.tools.values()]

class ToolCallingAgent:
    """An AI agent that can call tools based on user requests"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the agent"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.tool_registry = ToolRegistry()
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register some basic tools for demonstration"""
        
        # Calculator tool
        def calculate(expression: str) -> str:
            """Safely evaluate mathematical expressions"""
            try:
                # Only allow basic math operations for safety
                allowed_chars = set("0123456789+-*/(). ")
                if not all(c in allowed_chars for c in expression):
                    return "Error: Invalid characters in expression"
                
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        calculator_tool = Tool(
            name="calculate",
            description="Perform mathematical calculations",
            function=calculate,
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 2 * 3')"
                    }
                },
                "required": ["expression"]
            }
        )
        self.tool_registry.register_tool(calculator_tool)
        
        # Current time tool
        def get_current_time() -> str:
            """Get the current date and time"""
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        time_tool = Tool(
            name="get_current_time",
            description="Get the current date and time",
            function=get_current_time,
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        self.tool_registry.register_tool(time_tool)
        
        # Echo tool (for testing)
        def echo(message: str) -> str:
            """Echo back the input message"""
            return f"Echo: {message}"
        
        echo_tool = Tool(
            name="echo",
            description="Echo back the input message (for testing)",
            function=echo,
            parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        )
        self.tool_registry.register_tool(echo_tool)
    
    def add_to_history(self, role: str, content: str, tool_calls: Optional[List] = None):
        """Add a message to conversation history"""
        message = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.conversation_history.append(message)
        
        # Keep only last 20 messages to avoid token limits
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def chat(self, message: str) -> str:
        """Process a user message and return a response"""
        try:
            # Add user message to history
            self.add_to_history("user", message)
            
            # Prepare messages for API call
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant with access to various tools. 
                    When a user asks for something that requires a tool, use the appropriate tool.
                    Always explain what you're doing and provide helpful responses."""
                }
            ] + self.conversation_history
            
            # Get available tools
            tools = self.tool_registry.get_openai_tools()
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=300,
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
                    tool = self.tool_registry.get_tool(tool_name)
                    
                    if tool:
                        # Parse arguments
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Execute tool
                        result = tool.call(arguments)
                        tool_results.append(result)
                        
                        # Add tool result to history
                        self.add_to_history(
                            "tool",
                            str(result),
                            [{"id": tool_call.id, "type": "tool_call"}]
                        )
                    else:
                        error_msg = f"Tool '{tool_name}' not found"
                        tool_results.append(error_msg)
                        self.add_to_history(
                            "tool",
                            error_msg,
                            [{"id": tool_call.id, "type": "tool_call"}]
                        )
                
                # Generate final response with tool results
                final_messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Use the tool results to provide a comprehensive response to the user."
                    }
                ] + self.conversation_history
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=final_messages,
                    max_tokens=300,
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
    
    def register_custom_tool(self, tool: Tool):
        """Register a custom tool"""
        self.tool_registry.register_tool(tool)
        print(f"✅ Tool '{tool.name}' registered successfully")
    
    def list_available_tools(self) -> List[str]:
        """List all available tools"""
        return [tool.name for tool in self.tool_registry.list_tools()]
    
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
            "available_tools": self.list_available_tools(),
            "model": self.model
        }

def demo_tool_calling():
    """Demonstrate tool calling capabilities"""
    print("🔧 Tool Calling Demonstration")
    print("=" * 50)
    
    try:
        agent = ToolCallingAgent()
        
        # Show available tools
        print(f"Available tools: {agent.list_available_tools()}\n")
        
        # Test cases
        test_cases = [
            "What is 15 * 23 + 7?",
            "What time is it right now?",
            "Can you echo back 'Hello, World!'?",
            "Calculate (10 + 5) * 2 and tell me the current time",
            "Just say hello without using any tools"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case}")
            print(f"User: {test_case}")
            response = agent.chat(test_case)
            print(f"Agent: {response}\n")
        
        # Show conversation summary
        summary = agent.get_conversation_summary()
        print(f"📊 Conversation Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def interactive_session():
    """Start an interactive session with tool calling"""
    print("💬 Interactive Tool Calling Session")
    print("Type 'quit' to exit, 'reset' to clear history, 'tools' to list tools, 'summary' for info\n")
    
    try:
        agent = ToolCallingAgent()
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                continue
            elif user_input.lower() == 'tools':
                tools = agent.list_available_tools()
                print(f"🔧 Available tools: {tools}")
                continue
            elif user_input.lower() == 'summary':
                summary = agent.get_conversation_summary()
                print(f"📊 Summary: {summary}")
                continue
            elif not user_input:
                continue
            
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")
            
    except KeyboardInterrupt:
        print("\n👋 Session interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Session error: {e}")

def main():
    """Main function"""
    print("🤖 Tool Calling Agent")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to the .env file")
        return
    
    print("Choose an option:")
    print("1. Run tool calling demonstration")
    print("2. Start interactive session")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_tool_calling()
        elif choice == "2":
            interactive_session()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 