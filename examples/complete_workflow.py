#!/usr/bin/env python3
"""
Complete Workflow Example - End-to-end demonstration of the tutorial

This example shows the complete workflow from:
1. Setting up the environment
2. Creating a basic agent
3. Adding tool calling
4. Integrating MCP servers
5. Building a production-ready agent

This serves as a comprehensive demonstration of everything learned in the tutorial.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        "openai",
        "anthropic", 
        "requests",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - Configured")
        else:
            print(f"❌ {var} - Not configured")
            missing_vars.append(var)
    
    # Summary
    if not missing_packages and not missing_vars:
        print("\n🎉 Environment setup complete!")
        return True
    else:
        print(f"\n⚠️  Issues found:")
        if missing_packages:
            print(f"  - Missing packages: {missing_packages}")
        if missing_vars:
            print(f"  - Missing environment variables: {missing_vars}")
        return False

def demonstrate_basic_agent():
    """Demonstrate a basic AI agent"""
    print("\n🤖 Basic AI Agent Demonstration")
    print("=" * 50)
    
    try:
        from examples.simple_test_agent import SimpleTestAgent
        
        agent = SimpleTestAgent()
        
        # Test basic conversation
        test_messages = [
            "Hello! How are you?",
            "What can you help me with?",
            "Explain what an AI agent is in simple terms"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"Test {i}: {message}")
            response = agent.chat(message)
            print(f"Response: {response}\n")
        
        print("✅ Basic agent demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Basic agent demonstration failed: {e}")
        return False

def demonstrate_tool_calling():
    """Demonstrate tool calling capabilities"""
    print("\n🔧 Tool Calling Demonstration")
    print("=" * 50)
    
    try:
        from agents.basic.tool_calling_agent import ToolCallingAgent
        
        agent = ToolCallingAgent()
        
        # Test tool calling
        test_cases = [
            "What is 15 * 23 + 7?",
            "What time is it right now?",
            "Can you echo back 'Hello, World!'?",
            "Calculate (10 + 5) * 2 and tell me the current time"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case}")
            response = agent.chat(test_case)
            print(f"Response: {response}\n")
        
        print("✅ Tool calling demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Tool calling demonstration failed: {e}")
        return False

async def demonstrate_mcp_integration():
    """Demonstrate MCP server integration"""
    print("\n🔗 MCP Integration Demonstration")
    print("=" * 50)
    
    try:
        from agents.advanced.mcp_integrated_agent import MCPIntegratedAgent
        
        agent = MCPIntegratedAgent()
        
        # Show available services
        services = agent.list_available_services()
        print(f"Available services: {services}")
        
        # Test MCP integration
        test_cases = [
            "Send a message to the #general channel saying 'Hello from MCP agent!'",
            "What channels are available in Slack?",
            "Send an email to john@example.com with subject 'Meeting Reminder'",
            "Search for repositories related to 'machine learning'"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case}")
            response = await agent.chat(test_case)
            print(f"Response: {response}")
        
        print("\n✅ MCP integration demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration demonstration failed: {e}")
        return False

def demonstrate_custom_tools():
    """Demonstrate creating custom tools"""
    print("\n🛠️  Custom Tools Demonstration")
    print("=" * 50)
    
    try:
        from agents.basic.tool_calling_agent import ToolCallingAgent, Tool
        
        agent = ToolCallingAgent()
        
        # Create a custom weather tool
        def get_weather(location: str) -> str:
            """Get weather information for a location (mock)"""
            weather_data = {
                "New York": "72°F, Partly cloudy",
                "London": "65°F, Rainy",
                "Tokyo": "78°F, Sunny",
                "Sydney": "82°F, Clear"
            }
            return weather_data.get(location, f"Weather data not available for {location}")
        
        weather_tool = Tool(
            name="get_weather",
            description="Get current weather for a location",
            function=get_weather,
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        )
        
        # Register the custom tool
        agent.register_custom_tool(weather_tool)
        
        # Test the custom tool
        test_cases = [
            "What's the weather like in New York?",
            "How's the weather in Tokyo?",
            "Tell me about the weather in London and calculate 15 * 3"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case}")
            response = agent.chat(test_case)
            print(f"Response: {response}\n")
        
        print("✅ Custom tools demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Custom tools demonstration failed: {e}")
        return False

def demonstrate_error_handling():
    """Demonstrate error handling and validation"""
    print("\n⚠️  Error Handling Demonstration")
    print("=" * 50)
    
    try:
        from agents.basic.tool_calling_agent import ToolCallingAgent
        
        agent = ToolCallingAgent()
        
        # Test error cases
        error_test_cases = [
            "Calculate 2 + 2 / 0",  # Division by zero
            "Calculate invalid_expression",  # Invalid expression
            "What's the weather like?",  # No location specified
            "Send a message without specifying channel"  # Missing parameters
        ]
        
        for i, test_case in enumerate(error_test_cases, 1):
            print(f"Test {i}: {test_case}")
            response = agent.chat(test_case)
            print(f"Response: {response}\n")
        
        print("✅ Error handling demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling demonstration failed: {e}")
        return False

def demonstrate_conversation_management():
    """Demonstrate conversation management"""
    print("\n💬 Conversation Management Demonstration")
    print("=" * 50)
    
    try:
        from agents.basic.tool_calling_agent import ToolCallingAgent
        
        agent = ToolCallingAgent()
        
        # Simulate a conversation
        conversation = [
            "Hello! My name is Alice.",
            "What's the current time?",
            "Can you remember my name?",
            "Calculate 10 * 5 for me.",
            "What was the result of that calculation?",
            "Reset our conversation.",
            "Do you remember my name now?"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"Turn {i}: {message}")
            response = agent.chat(message)
            print(f"Agent: {response}")
            
            # Show conversation summary
            summary = agent.get_conversation_summary()
            print(f"📊 Messages: {summary['message_count']}, Tool calls: {summary['tool_calls']}\n")
        
        print("✅ Conversation management demonstration complete!")
        return True
        
    except Exception as e:
        print(f"❌ Conversation management demonstration failed: {e}")
        return False

async def run_complete_workflow():
    """Run the complete workflow demonstration"""
    print("🚀 Complete AI Agent Workflow Demonstration")
    print("=" * 60)
    print("This demonstration shows the complete journey from basic agent to")
    print("production-ready AI assistant with MCP integration.\n")
    
    # Step 1: Environment Check
    if not check_environment():
        print("\n❌ Environment setup incomplete. Please fix the issues above.")
        return
    
    # Step 2: Basic Agent
    if not demonstrate_basic_agent():
        print("\n❌ Basic agent demonstration failed.")
        return
    
    # Step 3: Tool Calling
    if not demonstrate_tool_calling():
        print("\n❌ Tool calling demonstration failed.")
        return
    
    # Step 4: Custom Tools
    if not demonstrate_custom_tools():
        print("\n❌ Custom tools demonstration failed.")
        return
    
    # Step 5: Error Handling
    if not demonstrate_error_handling():
        print("\n❌ Error handling demonstration failed.")
        return
    
    # Step 6: Conversation Management
    if not demonstrate_conversation_management():
        print("\n❌ Conversation management demonstration failed.")
        return
    
    # Step 7: MCP Integration
    if not await demonstrate_mcp_integration():
        print("\n❌ MCP integration demonstration failed.")
        return
    
    # Final summary
    print("\n🎉 Complete Workflow Demonstration Successful!")
    print("=" * 60)
    print("You have successfully demonstrated:")
    print("✅ Environment setup and configuration")
    print("✅ Basic AI agent functionality")
    print("✅ Tool calling capabilities")
    print("✅ Custom tool creation")
    print("✅ Error handling and validation")
    print("✅ Conversation management")
    print("✅ MCP server integration")
    print("\nYou are now ready to build production AI agents!")

def main():
    """Main function"""
    print("🤖 AI Agent Tutorial - Complete Workflow")
    print("=" * 60)
    
    print("This script demonstrates the complete workflow from the tutorial.")
    print("It will run through all the major concepts and show how they work together.\n")
    
    print("Choose an option:")
    print("1. Run complete workflow demonstration")
    print("2. Check environment setup only")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(run_complete_workflow())
        elif choice == "2":
            check_environment()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 