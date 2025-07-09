#!/usr/bin/env python3
"""
Simple Test Agent - A basic AI agent to verify your setup

This example demonstrates a minimal AI agent that can:
- Connect to OpenAI's API
- Process user messages
- Generate responses

Run this to test your environment setup.
"""

import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
except ImportError:
    print("❌ OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

class SimpleTestAgent:
    """A simple AI agent for testing purposes"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the agent with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only last 10 messages to avoid token limits
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def chat(self, message: str) -> str:
        """Process a user message and return a response"""
        try:
            # Add user message to history
            self.add_to_history("user", message)
            
            # Prepare messages for API call
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Keep responses concise and friendly."
                }
            ] + self.conversation_history
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.add_to_history("assistant", assistant_message)
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"Error communicating with OpenAI: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get information about the current conversation"""
        return {
            "message_count": len(self.conversation_history),
            "model": self.model,
            "last_message": self.conversation_history[-1] if self.conversation_history else None
        }

def test_agent_functionality():
    """Test various agent functionalities"""
    print("🧪 Testing Agent Functionality\n")
    
    try:
        agent = SimpleTestAgent()
        
        # Test 1: Basic conversation
        print("Test 1: Basic conversation")
        response = agent.chat("Hello! How are you?")
        print(f"Response: {response}\n")
        
        # Test 2: Follow-up conversation
        print("Test 2: Follow-up conversation")
        response = agent.chat("What's your name?")
        print(f"Response: {response}\n")
        
        # Test 3: Conversation summary
        print("Test 3: Conversation summary")
        summary = agent.get_conversation_summary()
        print(f"Summary: {summary}\n")
        
        # Test 4: Reset conversation
        print("Test 4: Reset conversation")
        agent.reset_conversation()
        summary = agent.get_conversation_summary()
        print(f"Summary after reset: {summary}\n")
        
        print("✅ All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def interactive_chat():
    """Start an interactive chat session"""
    print("💬 Starting Interactive Chat Session")
    print("Type 'quit' to exit, 'reset' to clear history, 'summary' for conversation info\n")
    
    try:
        agent = SimpleTestAgent()
        
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                agent.reset_conversation()
                continue
            elif user_input.lower() == 'summary':
                summary = agent.get_conversation_summary()
                print(f"📊 Conversation Summary: {summary}")
                continue
            elif not user_input:
                continue
            
            # Get agent response
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")
            
    except KeyboardInterrupt:
        print("\n👋 Chat session interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Chat session error: {e}")

def main():
    """Main function to run the test agent"""
    print("🤖 Simple Test Agent")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to the .env file")
        return
    
    # Test functionality
    if not test_agent_functionality():
        print("❌ Agent functionality test failed")
        return
    
    print("🎉 Setup verification complete!")
    
    # Ask if user wants to start interactive chat
    try:
        choice = input("\nWould you like to start an interactive chat? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_chat()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 