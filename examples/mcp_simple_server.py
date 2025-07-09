#!/usr/bin/env python3
"""
Simple MCP Server Example

This demonstrates a basic MCP server that provides:
- A simple calculator tool
- A time tool
- A file reading tool

This serves as a foundation for understanding MCP server implementation.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List

# Note: In a real implementation, you would import from mcp.server
# For this tutorial, we'll create a simplified version

class SimpleMCPServer:
    """A simple MCP server implementation"""
    
    def __init__(self):
        self.name = "simple-server"
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define the tools this server provides"""
        return [
            {
                "name": "calculate",
                "description": "Perform basic mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "get_time",
                "description": "Get the current date and time",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["filepath"]
                }
            }
        ]
    
    def list_tools(self) -> Dict[str, Any]:
        """Return list of available tools"""
        return {
            "tools": self.tools
        }
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        try:
            if name == "calculate":
                return self._calculate(arguments.get("expression", ""))
            elif name == "get_time":
                return self._get_time()
            elif name == "read_file":
                return self._read_file(arguments.get("filepath", ""))
            else:
                return {
                    "error": f"Unknown tool: {name}"
                }
        except Exception as e:
            return {
                "error": f"Error executing {name}: {str(e)}"
            }
    
    def _calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate mathematical expression"""
        try:
            # Only allow basic math operations for safety
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return {
                    "error": "Invalid characters in expression"
                }
            
            result = eval(expression)
            return {
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "error": f"Calculation error: {str(e)}"
            }
    
    def _get_time(self) -> Dict[str, Any]:
        """Get current time"""
        now = datetime.now()
        return {
            "datetime": now.isoformat(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": now.timestamp()
        }
    
    def _read_file(self, filepath: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            if not os.path.exists(filepath):
                return {
                    "error": f"File not found: {filepath}"
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "filepath": filepath,
                "size": len(content)
            }
        except Exception as e:
            return {
                "error": f"Error reading file: {str(e)}"
            }

class SimpleMCPClient:
    """A simple MCP client for testing"""
    
    def __init__(self, server: SimpleMCPServer):
        self.server = server
    
    def list_tools(self) -> List[str]:
        """Get list of available tools"""
        tools = self.server.list_tools()
        return [tool["name"] for tool in tools["tools"]]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server"""
        return self.server.call_tool(name, arguments)

def demo_server():
    """Demonstrate the MCP server functionality"""
    print("🔧 Simple MCP Server Demo")
    print("=" * 50)
    
    # Create server and client
    server = SimpleMCPServer()
    client = SimpleMCPClient(server)
    
    # Show available tools
    tools = client.list_tools()
    print(f"Available tools: {tools}\n")
    
    # Test cases
    test_cases = [
        ("calculate", {"expression": "2 + 2 * 3"}),
        ("get_time", {}),
        ("read_file", {"filepath": "README.md"}),
        ("calculate", {"expression": "(10 + 5) * 2"}),
        ("read_file", {"filepath": "nonexistent.txt"})
    ]
    
    for i, (tool_name, args) in enumerate(test_cases, 1):
        print(f"Test {i}: {tool_name}({args})")
        result = client.call_tool(tool_name, args)
        print(f"Result: {json.dumps(result, indent=2)}\n")

def interactive_server():
    """Interactive session with the MCP server"""
    print("💬 Interactive MCP Server Session")
    print("Type 'quit' to exit, 'tools' to list tools\n")
    
    server = SimpleMCPServer()
    client = SimpleMCPClient(server)
    
    while True:
        try:
            user_input = input("Enter tool name and arguments (e.g., 'calculate {\"expression\": \"2+2\"}'): ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'tools':
                tools = client.list_tools()
                print(f"🔧 Available tools: {tools}")
                continue
            elif not user_input:
                continue
            
            # Parse input (simple format: tool_name {"arg": "value"})
            try:
                if ' ' in user_input:
                    tool_name, args_str = user_input.split(' ', 1)
                    args = json.loads(args_str)
                else:
                    tool_name = user_input
                    args = {}
                
                result = client.call_tool(tool_name, args)
                print(f"Result: {json.dumps(result, indent=2)}\n")
                
            except json.JSONDecodeError:
                print("❌ Invalid JSON format for arguments")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        except KeyboardInterrupt:
            print("\n👋 Session interrupted. Goodbye!")
            break

def main():
    """Main function"""
    print("🤖 Simple MCP Server")
    print("=" * 50)
    
    print("Choose an option:")
    print("1. Run server demonstration")
    print("2. Start interactive session")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_server()
        elif choice == "2":
            interactive_server()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 