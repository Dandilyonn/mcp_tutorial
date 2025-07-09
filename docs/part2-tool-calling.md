# Part 2: Tool Calling Basics

## What is Tool Calling?

Tool calling is the mechanism that allows AI agents to execute specific functions or actions beyond just generating text. Instead of just responding with words, agents can:

- Make HTTP requests to APIs
- Execute database queries
- Send emails or messages
- Create or modify files
- Perform calculations
- Interact with external services

## How Tool Calling Works

### 1. **Tool Definition**
First, you define what tools your agent can use:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or coordinates"
                }
            },
            "required": ["location"]
        }
    }
]
```

### 2. **Agent Decision**
The agent analyzes the user's request and decides which tool to call:

```
User: "What's the weather like in New York?"
Agent: I need to call the get_weather tool with location="New York"
```

### 3. **Tool Execution**
The system executes the tool and gets the result:

```python
def get_weather(location):
    # Make API call to weather service
    response = weather_api.get_current(location)
    return {
        "temperature": "72°F",
        "condition": "Partly cloudy",
        "humidity": "65%"
    }
```

### 4. **Response Generation**
The agent uses the tool result to generate a helpful response:

```
Agent: "The weather in New York is currently 72°F and partly cloudy with 65% humidity."
```

## Tool Calling Patterns

### 1. **Single Tool Call**
Simple cases where one tool is sufficient:

```python
# User asks for weather
user_input = "What's the weather in London?"
# Agent calls weather tool
weather_data = get_weather("London")
# Agent responds with weather info
```

### 2. **Sequential Tool Calls**
Multiple tools called in order:

```python
# User asks for flight info and weather
user_input = "I'm flying to Tokyo tomorrow. What's the weather like there?"

# Step 1: Get flight info
flight_data = get_flight_info("Tokyo", "tomorrow")

# Step 2: Get weather for destination
weather_data = get_weather("Tokyo")

# Step 3: Combine and respond
response = f"Your flight to Tokyo is at {flight_data['time']}. The weather there will be {weather_data['condition']}."
```

### 3. **Conditional Tool Calls**
Tools called based on conditions:

```python
user_input = "Can you help me with my travel plans?"

if "weather" in user_input:
    weather_data = get_weather(location)
if "flights" in user_input:
    flight_data = get_flights(destination)
if "hotels" in user_input:
    hotel_data = get_hotels(location)
```

## Implementing Tool Calling

### Step 1: Define Your Tools

```python
from typing import Dict, Any
import requests

class WeatherTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location"""
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": location
        }
        response = requests.get(url, params=params)
        return response.json()

class CalculatorTool:
    def evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        try:
            # Use ast.literal_eval for safety
            import ast
            return ast.literal_eval(expression)
        except:
            raise ValueError("Invalid mathematical expression")
```

### Step 2: Create Tool Registry

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, tool: Any, description: str):
        """Register a tool with the agent"""
        self.tools[name] = {
            "tool": tool,
            "description": description
        }
    
    def get_tool(self, name: str):
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self):
        """List all available tools"""
        return list(self.tools.keys())
```

### Step 3: Build the Agent

```python
class SimpleAgent:
    def __init__(self, llm_client, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.tools = tool_registry
    
    def process_request(self, user_input: str) -> str:
        # Step 1: Analyze the request
        analysis = self.llm.analyze_request(user_input)
        
        # Step 2: Determine which tools to call
        tool_calls = self.llm.determine_tool_calls(analysis)
        
        # Step 3: Execute tools
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["tool"]
            parameters = tool_call["parameters"]
            
            tool = self.tools.get_tool(tool_name)
            if tool:
                result = tool["tool"](**parameters)
                results.append(result)
        
        # Step 4: Generate response
        response = self.llm.generate_response(user_input, results)
        return response
```

## Example: Building a Simple Calculator Agent

Let's build a complete example:

```python
# examples/simple_calculator_agent.py
import openai
from typing import Dict, Any

class CalculatorAgent:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform mathematical calculations",
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
                }
            }
        ]
    
    def calculate(self, expression: str) -> float:
        """Safely evaluate mathematical expressions"""
        try:
            # Only allow basic math operations for safety
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")
            
            result = eval(expression)
            return float(result)
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def chat(self, message: str) -> str:
        """Process a user message and return a response"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            tools=self.tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call a tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            
            if tool_call.function.name == "calculate":
                expression = tool_call.function.arguments
                # Parse the JSON arguments
                import json
                args = json.loads(expression)
                result = self.calculate(args["expression"])
                
                # Send the result back to the model
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": message},
                        {"role": "tool", "content": str(result), "tool_call_id": tool_call.id}
                    ]
                )
                
                return response.choices[0].message.content
        
        return message.content

# Usage example
if __name__ == "__main__":
    agent = CalculatorAgent("your-api-key-here")
    
    # Test the agent
    result = agent.chat("What is 15 * 23 + 7?")
    print(result)  # Should output something like "15 * 23 + 7 = 352"
```

## Best Practices for Tool Calling

### 1. **Tool Design**
- Keep tools focused and single-purpose
- Provide clear descriptions and parameter documentation
- Handle errors gracefully
- Validate inputs before processing

### 2. **Security**
- Never use `eval()` with untrusted input
- Validate all parameters
- Implement rate limiting for API calls
- Use environment variables for sensitive data

### 3. **Error Handling**
- Always handle tool execution errors
- Provide meaningful error messages
- Implement fallback strategies
- Log errors for debugging

### 4. **Performance**
- Cache frequently used results
- Implement timeouts for external calls
- Use async operations when possible
- Monitor tool execution times

## Common Tool Types

### 1. **Information Retrieval**
- Web search
- Database queries
- File reading
- API calls

### 2. **Data Processing**
- Calculations
- Data transformation
- Format conversion
- Validation

### 3. **Communication**
- Email sending
- Message posting
- Notification sending
- API webhooks

### 4. **File Operations**
- File creation
- File modification
- File deletion
- File upload/download

## Next Steps

Now that you understand tool calling basics, let's explore [Part 3: MCP Server Introduction](./part3-mcp-intro.md) to learn how Model Context Protocol servers can enhance your agent's capabilities.

## Key Takeaways

- Tool calling allows agents to execute actions beyond text generation
- Tools should be well-defined with clear parameters and descriptions
- Implement proper error handling and security measures
- Tool calling follows patterns: single, sequential, and conditional
- Always validate inputs and handle errors gracefully

---

**Ready to learn about MCP servers?** Continue to [Part 3: MCP Server Introduction](./part3-mcp-intro.md) 