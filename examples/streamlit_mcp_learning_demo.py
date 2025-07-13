#!/usr/bin/env python3
"""
Streamlit MCP Learning Demo for College Students

This application teaches Model Context Protocol (MCP) servers using Google Maps
functionality. It's designed for students who know Python and Streamlit.

What you'll learn:
1. What MCP servers are and why they're useful
2. How to create a mock MCP server
3. How to call MCP tools from a Streamlit app
4. How to integrate external APIs (Google Maps) into AI agents

Author: AI Teaching Assistant
Target Audience: College students learning Python and Streamlit
"""

from logging import config
import os
from dotenv import load_dotenv
import streamlit as st
import asyncio
import json
import math
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Import the server classes
from google_apis_mcp_server import GoogleAPIServer, GoogleAPIConfig

# Page configuration
st.set_page_config(
    page_title="MCP Server Learning Demo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .code-block {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

class MockGoogleMapsMCPServer:
    """
    Mock Google Maps MCP Server
    
    This is a simplified version of what a real Google Maps MCP server would look like.
    In a real application, this would connect to Google's APIs.
    
    Key Concepts:
    - MCP servers provide tools that AI agents can call
    - Each tool has a name, description, and parameters
    - Tools return structured data that agents can understand
    """
    
    def __init__(self):
        self.name = "google-maps"
        self.tools = self._define_tools()
        
        # Mock data for demonstration
        self.mock_locations = {
            "New York, NY": {"lat": 40.7128, "lng": -74.0060},
            "London, UK": {"lat": 51.5074, "lng": -0.1278},
            "Tokyo, Japan": {"lat": 35.6762, "lng": 139.6503},
            "Sydney, Australia": {"lat": -33.8688, "lng": 151.2093},
            "Paris, France": {"lat": 48.8566, "lng": 2.3522},
            "San Francisco, CA": {"lat": 37.7749, "lng": -122.4194},
            "Berlin, Germany": {"lat": 52.5200, "lng": 13.4050},
            "Mumbai, India": {"lat": 19.0760, "lng": 72.8777},
            "Rio de Janeiro, Brazil": {"lat": -22.9068, "lng": -43.1729},
            "Cape Town, South Africa": {"lat": -33.9249, "lng": 18.4241},
        }
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """
        Define the tools this MCP server provides
        
        Each tool has:
        - name: What the tool is called
        - description: What the tool does
        - parameters: What data the tool needs (like function parameters)
        """
        return [
            {
                "name": "geocode_address",
                "description": "Convert an address to coordinates (latitude and longitude)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The address to convert to coordinates"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "reverse_geocode",
                "description": "Convert coordinates to an address (reverse geocoding)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude coordinate"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude coordinate"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "calculate_distance",
                "description": "Calculate distance between two locations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat1": {"type": "number", "description": "Latitude of first location"},
                        "lng1": {"type": "number", "description": "Longitude of first location"},
                        "lat2": {"type": "number", "description": "Latitude of second location"},
                        "lng2": {"type": "number", "description": "Longitude of second location"},
                        "unit": {
                            "type": "string",
                            "description": "Distance unit",
                            "enum": ["km", "miles"]
                        }
                    },
                    "required": ["lat1", "lng1", "lat2", "lng2", "unit"]
                }
            },
            {
                "name": "find_nearby_places",
                "description": "Find places near a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number", "description": "Latitude coordinate"},
                        "longitude": {"type": "number", "description": "Longitude coordinate"},
                        "radius": {"type": "number", "description": "Search radius in meters"},
                        "place_type": {
                            "type": "string",
                            "description": "Type of places to search for",
                            "enum": ["restaurant", "hotel", "gas_station", "hospital", "school"]
                        }
                    },
                    "required": ["latitude", "longitude", "radius", "place_type"]
                }
            }
        ]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return all available tools"""
        return self.tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments
        
        This is where the actual work happens. In a real MCP server,
        this would call Google's APIs or other external services.
        """
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        try:
            if name == "geocode_address":
                return self._geocode_address(arguments.get("address", ""))
            elif name == "reverse_geocode":
                return self._reverse_geocode(
                    arguments.get("latitude", 0),
                    arguments.get("longitude", 0)
                )
            elif name == "calculate_distance":
                return self._calculate_distance(
                    arguments.get("lat1", 0),
                    arguments.get("lng1", 0),
                    arguments.get("lat2", 0),
                    arguments.get("lng2", 0),
                    arguments.get("unit", "km")
                )
            elif name == "find_nearby_places":
                return self._find_nearby_places(
                    arguments.get("latitude", 0),
                    arguments.get("longitude", 0),
                    arguments.get("radius", 1000),
                    arguments.get("place_type", "restaurant")
                )
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": f"Error executing {name}: {str(e)}"}
    
    def _geocode_address(self, address: str) -> Dict[str, Any]:
        """Convert address to coordinates"""
        # Check if we have mock data for this address
        if address in self.mock_locations:
            coords = self.mock_locations[address]
            return {
                "success": True,
                "address": address,
                "latitude": coords["lat"],
                "longitude": coords["lng"],
                "formatted_address": address
            }
        
        # For unknown addresses, generate mock coordinates
        lat = random.uniform(-90, 90)
        lng = random.uniform(-180, 180)
        
        return {
            "success": True,
            "address": address,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "formatted_address": f"{address} (Mock Location)"
        }
    
    def _reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Convert coordinates to address"""
        # Find the closest mock location
        closest_location = None
        min_distance = float('inf')
        
        for address, coords in self.mock_locations.items():
            distance = ((lat - coords["lat"])**2 + (lng - coords["lng"])**2)**0.5
            if distance < min_distance:
                min_distance = distance
                closest_location = address
        
        if closest_location and min_distance < 1.0:
            return {
                "success": True,
                "latitude": lat,
                "longitude": lng,
                "address": closest_location,
                "formatted_address": closest_location
            }
        else:
            return {
                "success": True,
                "latitude": lat,
                "longitude": lng,
                "address": f"Unknown Location ({lat:.6f}, {lng:.6f})",
                "formatted_address": f"Unknown Location ({lat:.6f}, {lng:.6f})"
            }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float, unit: str) -> Dict[str, Any]:
        """Calculate distance using Haversine formula"""
        R = 6371 if unit == "km" else 3959  # Earth's radius
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return {
            "success": True,
            "distance": round(distance, 2),
            "unit": unit,
            "point1": {"latitude": lat1, "longitude": lng1},
            "point2": {"latitude": lat2, "longitude": lng2}
        }
    
    def _find_nearby_places(self, lat: float, lng: float, radius: float, place_type: str) -> Dict[str, Any]:
        """Find places near a location"""
        places = []
        num_places = random.randint(3, 8)
        
        for i in range(num_places):
            offset_lat = random.uniform(-radius/111000, radius/111000)
            offset_lng = random.uniform(-radius/111000, radius/111000)
            
            place_lat = lat + offset_lat
            place_lng = lng + offset_lng
            
            places.append({
                "name": f"Mock {place_type.title()} {i+1}",
                "latitude": round(place_lat, 6),
                "longitude": round(place_lng, 6),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "distance": round(random.uniform(100, radius), 0)
            })
        
        places.sort(key=lambda x: x["distance"])
        
        return {
            "success": True,
            "places": places,
            "center": {"latitude": lat, "longitude": lng},
            "radius": radius,
            "place_type": place_type
        }

class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self):
        # api_key = os.getenv("GOOGLE_API_KEY")
        # # Create configuration
        # config = GoogleAPIConfig(
        #     api_key=api_key,
        # )
        # # Create server instance
        # self.server = GoogleAPIServer(config)
        # 
        # print("✅ Server initialized successfully")
        # print(f"🔑 API Key: {api_key[:10]}...")
        # print(f"🔐 OAuth2: {'Enabled' if config.client_id else 'Disabled'}")

        self.server = MockGoogleMapsMCPServer()
        
    
    def list_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool["name"] for tool in self.server.list_tools()]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server"""
        return await self.server.call_tool(name, arguments)

def show_introduction():
    """Show the introduction section"""
    st.markdown('<h1 class="main-header">🌍 MCP Server Learning Demo</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Welcome to MCP Server Learning! 🎓
    
    This demo will teach you about **Model Context Protocol (MCP) servers** using Google Maps functionality.
    If you know Python and Streamlit, you're ready to learn!
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**What is MCP?**\n\nMCP lets AI agents use external tools and data sources safely and efficiently.")
    
    with col2:
        st.success("**Why Learn MCP?**\n\nIt's the future of AI applications - connecting AI to real-world data and services.")
    
    with col3:
        st.warning("**What You'll Build**\n\nA mock Google Maps MCP server and a Streamlit app that uses it!")

def show_mcp_explanation():
    """Explain MCP concepts"""
    st.markdown('<h2 class="section-header">📚 Understanding MCP Servers</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### What is a Model Context Protocol (MCP) Server?
    
    Think of an MCP server as a **translator** between AI agents and external services. 
    It provides a standardized way for AI to:
    - Access external APIs (like Google Maps)
    - Read files and databases
    - Control applications
    - Get real-time data
    """)
    
    # Visual explanation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ```
        AI Agent → MCP Server → External Service
        (You)     (Translator)   (Google Maps)
        ```
        """)
    
    st.markdown("""
    ### Key Components of an MCP Server:
    
    1. **Tools**: Functions the server can perform (like geocoding an address)
    2. **Parameters**: Data each tool needs (like the address to geocode)
    3. **Responses**: Structured data the tool returns (like coordinates)
    
    ### Why Use MCP?
    
    - **Safety**: AI agents can only access what you allow
    - **Standardization**: Same interface for different services
    - **Efficiency**: Reusable tools across different AI applications
    """)

def show_server_implementation():
    """Show the MCP server implementation"""
    st.markdown('<h2 class="section-header">🔧 MCP Server Implementation</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Our Mock Google Maps MCP Server
    
    Below is the code for our mock MCP server. In a real application, 
    this would connect to Google's actual APIs.
    """)
    
    # Show the server class structure
    with st.expander("📖 View MCP Server Code", expanded=False):
        st.code("""
class MockGoogleMapsMCPServer:
    def __init__(self):
        self.name = "google-maps"
        self.tools = self._define_tools()
    
    def _define_tools(self):
        # Define what tools this server provides
        return [
            {
                "name": "geocode_address",
                "description": "Convert address to coordinates",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"}
                    },
                    "required": ["address"]
                }
            },
            # ... more tools
        ]
    
    async def call_tool(self, name, arguments):
        # Execute the requested tool
        if name == "geocode_address":
            return self._geocode_address(arguments["address"])
        # ... handle other tools
        """, language="python")
    
    st.markdown("""
    ### Key Concepts in the Code:
    
    - **Tool Definition**: Each tool has a name, description, and required parameters
    - **Async Execution**: Tools run asynchronously for better performance
    - **Error Handling**: Proper error responses for invalid requests
    - **Mock Data**: Realistic data for demonstration purposes
    """)

def show_tools_demo():
    """Demonstrate the available tools"""
    st.markdown('<h2 class="section-header">🛠️ Available MCP Tools</h2>', unsafe_allow_html=True)
    
    client = MCPClient()
    tools = client.list_tools()
    
    st.markdown(f"""
    Our Google Maps MCP server provides **{len(tools)} tools**:
    """)
    
    # Display tools in a nice format
    for i, tool_name in enumerate(tools, 1):
        with st.expander(f"🔧 {i}. {tool_name.replace('_', ' ').title()}", expanded=True):
            if tool_name == "geocode_address":
                st.markdown("**Purpose**: Convert an address to coordinates")
                st.markdown("**Example**: 'New York, NY' → (40.7128, -74.0060)")
                st.markdown("**Use Case**: Finding exact location of a place")
                
            elif tool_name == "reverse_geocode":
                st.markdown("**Purpose**: Convert coordinates to an address")
                st.markdown("**Example**: (40.7128, -74.0060) → 'New York, NY'")
                st.markdown("**Use Case**: Understanding what's at specific coordinates")
                
            elif tool_name == "calculate_distance":
                st.markdown("**Purpose**: Calculate distance between two locations")
                st.markdown("**Example**: NYC to London = 5,570 km")
                st.markdown("**Use Case**: Planning trips, logistics")
                
            elif tool_name == "find_nearby_places":
                st.markdown("**Purpose**: Find places near a location")
                st.markdown("**Example**: Restaurants within 2km of Times Square")
                st.markdown("**Use Case**: Local search, recommendations")

def show_interactive_demo():
    """Show interactive demo section"""
    st.markdown('<h2 class="section-header">🎮 Interactive Demo</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Now let's try out the MCP tools! Choose a tool below and see how it works.
    """)
    
    client = MCPClient()
    
    # Tool selection
    tool_options = {
        "geocode_address": "📍 Convert Address to Coordinates",
        "reverse_geocode": "🔄 Convert Coordinates to Address", 
        "calculate_distance": "📏 Calculate Distance Between Locations",
        "find_nearby_places": "🏪 Find Nearby Places"
    }
    
    selected_tool = st.selectbox(
        "Choose a tool to try:",
        options=list(tool_options.keys()),
        format_func=lambda x: tool_options[x]
    )
    
    st.markdown("---")
    
    # Handle different tools
    if selected_tool == "geocode_address":
        st.markdown("### 📍 Address to Coordinates")
        st.markdown("Enter an address to get its coordinates:")
        
        address = st.text_input("Address:", value="New York, NY")
        
        if st.button("🔍 Geocode Address"):
            with st.spinner("Converting address to coordinates..."):
                result = asyncio.run(client.call_tool("geocode_address", {"address": address}))
                
            if result.get("success"):
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Address**: {result['address']}")
                    st.info(f"**Latitude**: {result['latitude']}")
                with col2:
                    st.info(f"**Longitude**: {result['longitude']}")
                    st.info(f"**Formatted**: {result['formatted_address']}")
                
                # Show the API call
                st.markdown("**API Call Made**:")
                st.code(f"""
await client.call_tool("geocode_address", {{
    "address": "{address}"
}})
                """, language="python")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    elif selected_tool == "reverse_geocode":
        st.markdown("### 🔄 Coordinates to Address")
        st.markdown("Enter coordinates to get the address:")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude:", value=40.7128, format="%.6f")
        with col2:
            lng = st.number_input("Longitude:", value=-74.0060, format="%.6f")
        
        if st.button("🔄 Reverse Geocode"):
            with st.spinner("Converting coordinates to address..."):
                result = asyncio.run(client.call_tool("reverse_geocode", {
                    "latitude": lat,
                    "longitude": lng
                }))
                
            if result.get("success"):
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Coordinates**: ({lat}, {lng})")
                    st.info(f"**Address**: {result['address']}")
                with col2:
                    st.info(f"**Formatted**: {result['formatted_address']}")
                
                st.markdown("**API Call Made**:")
                st.code(f"""
await client.call_tool("reverse_geocode", {{
    "latitude": {lat},
    "longitude": {lng}
}})
                """, language="python")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    elif selected_tool == "calculate_distance":
        st.markdown("### 📏 Distance Calculator")
        st.markdown("Calculate distance between two locations:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Point 1:**")
            lat1 = st.number_input("Latitude 1:", value=40.7128, format="%.6f", key="lat1")
            lng1 = st.number_input("Longitude 1:", value=-74.0060, format="%.6f", key="lng1")
        with col2:
            st.markdown("**Point 2:**")
            lat2 = st.number_input("Latitude 2:", value=51.5074, format="%.6f", key="lat2")
            lng2 = st.number_input("Longitude 2:", value=-0.1278, format="%.6f", key="lng2")
        
        unit = st.selectbox("Distance unit:", ["km", "miles"])
        
        if st.button("📏 Calculate Distance"):
            with st.spinner("Calculating distance..."):
                result = asyncio.run(client.call_tool("calculate_distance", {
                    "lat1": lat1, "lng1": lng1,
                    "lat2": lat2, "lng2": lng2,
                    "unit": unit
                }))
                
            if result.get("success"):
                st.success(f"**Distance**: {result['distance']} {result['unit']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Point 1**: ({lat1}, {lng1})")
                with col2:
                    st.info(f"**Point 2**: ({lat2}, {lng2})")
                
                st.markdown("**API Call Made**:")
                st.code(f"""
await client.call_tool("calculate_distance", {{
    "lat1": {lat1}, "lng1": {lng1},
    "lat2": {lat2}, "lng2": {lng2},
    "unit": "{unit}"
}})
                """, language="python")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    elif selected_tool == "find_nearby_places":
        st.markdown("### 🏪 Nearby Places Search")
        st.markdown("Find places near a location:")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Center Latitude:", value=40.7128, format="%.6f", key="nearby_lat")
            lng = st.number_input("Center Longitude:", value=-74.0060, format="%.6f", key="nearby_lng")
        with col2:
            radius = st.number_input("Search Radius (meters):", value=2000, min_value=100, max_value=50000)
            place_type = st.selectbox("Place Type:", ["restaurant", "hotel", "gas_station", "hospital", "school"])
        
        if st.button("🏪 Find Nearby Places"):
            with st.spinner("Searching for nearby places..."):
                result = asyncio.run(client.call_tool("find_nearby_places", {
                    "latitude": lat,
                    "longitude": lng,
                    "radius": radius,
                    "place_type": place_type
                }))
                
            if result.get("success"):
                st.success(f"Found {len(result['places'])} {place_type}s within {radius}m")
                
                # Display places in a nice format
                for i, place in enumerate(result['places'], 1):
                    with st.expander(f"🏪 {i}. {place['name']}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Location**: ({place['latitude']}, {place['longitude']})")
                        with col2:
                            st.write(f"**Distance**: {place['distance']}m")
                        with col3:
                            st.write(f"**Rating**: ⭐ {place['rating']}")
                
                st.markdown("**API Call Made**:")
                st.code(f"""
await client.call_tool("find_nearby_places", {{
    "latitude": {lat},
    "longitude": {lng},
    "radius": {radius},
    "place_type": "{place_type}"
}})
                """, language="python")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

def show_ai_agent_example():
    """Show how AI agents would use MCP"""
    st.markdown('<h2 class="section-header">🤖 AI Agent Example</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### How AI Agents Use MCP Servers
    
    Imagine you're building an AI travel assistant. Here's how it would use our MCP server:
    """)
    
    # Example conversation
    st.markdown("""
    **User**: "I want to visit New York and find restaurants near Times Square"
    
    **AI Agent** (using MCP tools):
    """)
    
    st.code("""
# Step 1: Convert "Times Square" to coordinates
location = await mcp_client.call_tool("geocode_address", {
    "address": "Times Square, New York"
})

# Step 2: Find restaurants nearby
restaurants = await mcp_client.call_tool("find_nearby_places", {
    "latitude": location["latitude"],
    "longitude": location["longitude"],
    "radius": 1000,
    "place_type": "restaurant"
})

# Step 3: Format response for user
response = f"I found {len(restaurants['places'])} restaurants near Times Square..."
    """, language="python")
    
    st.markdown("""
    **AI Response**: "I found 5 restaurants near Times Square. The closest is Mock Restaurant 1, 
    just 150m away with a 4.2-star rating..."
    """)
    
    st.markdown("""
    ### Benefits for AI Development:
    
    - **Modular**: Each tool does one thing well
    - **Reusable**: Same tools work for different AI applications
    - **Safe**: AI can only access what you allow
    - **Scalable**: Easy to add new tools and services
    """)

def show_next_steps():
    """Show next steps for learning"""
    st.markdown('<h2 class="section-header">🚀 Next Steps in Your Learning</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### What You've Learned:
    
    ✅ How MCP servers work
    ✅ How to define tools and parameters
    ✅ How to call MCP tools from applications
    ✅ How AI agents use MCP for real-world tasks
    """)
    
    st.markdown("""
    ### What to Try Next:
    
    1. **Build Your Own MCP Server**
       - Create a server for a different API (weather, news, etc.)
       - Add more complex tools with multiple parameters
       - Implement real API calls instead of mock data
    
    2. **Integrate with Real AI Models**
       - Connect your MCP server to ChatGPT or other LLMs
       - Build a conversational AI that uses your tools
       - Create a multi-step workflow using multiple tools
    
    3. **Advanced Features**
       - Add authentication to your MCP server
       - Implement rate limiting and caching
       - Create tools that modify data (not just read it)
    
    4. **Real-World Applications**
       - Build a travel planning assistant
       - Create a local business finder
       - Develop a logistics optimization tool
    """)
    
    st.markdown("""
    ### Resources for Further Learning:
    
    - [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
    - [Official MCP Documentation](https://modelcontextprotocol.io/)
    - [Google Maps API Documentation](https://developers.google.com/maps)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    """)

def main():
    """Main application"""
    
    # Sidebar navigation
    st.sidebar.title("📚 Learning Navigation")

    page = st.sidebar.radio(
        "Choose a section:",
        [
            "🏠 Introduction",
            "📚 Understanding MCP",
            "🔧 Server Implementation", 
            "🛠️ Available Tools",
            "🎮 Interactive Demo",
            "🤖 AI Agent Example",
            "🚀 Next Steps"
        ]
    )
    
    # Display appropriate section
    if page == "🏠 Introduction":
        show_introduction()
    elif page == "📚 Understanding MCP":
        show_mcp_explanation()
    elif page == "🔧 Server Implementation":
        show_server_implementation()
    elif page == "🛠️ Available Tools":
        show_tools_demo()
    elif page == "🎮 Interactive Demo":
        show_interactive_demo()
    elif page == "🤖 AI Agent Example":
        show_ai_agent_example()
    elif page == "🚀 Next Steps":
        show_next_steps()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🌍 MCP Server Learning Demo | Built for College Students | 
        <a href='https://modelcontextprotocol.io/' target='_blank'>Learn More About MCP</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 