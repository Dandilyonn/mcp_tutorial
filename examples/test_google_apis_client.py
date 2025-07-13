#!/usr/bin/env python3
"""
Test Client for Google APIs MCP Server

This script demonstrates how to use the Google APIs MCP server
with various API calls and shows the responses.

Usage:
    python test_google_apis_client.py

Make sure to set up your environment variables first:
    GOOGLE_API_KEY=your_api_key
    GOOGLE_CLIENT_ID=your_client_id (optional)
    GOOGLE_CLIENT_SECRET=your_client_secret (optional)
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the server classes
from google_apis_mcp_server import GoogleAPIServer, GoogleAPIConfig

def print_result(tool_name: str, result: dict):
    """Pretty print tool results"""
    print(f"\n{'='*60}")
    print(f"🔧 Tool: {tool_name}")
    print(f"{'='*60}")
    
    if result.get("success"):
        print("✅ Success!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Error:")
        print(f"Error: {result.get('error', 'Unknown error')}")

async def test_maps_apis(server: GoogleAPIServer):
    """Test Google Maps APIs"""
    print("\n🌍 Testing Google Maps APIs...")
    
    # Test geocoding
    print("\n📍 Testing Geocoding...")
    result = await server.call_tool("geocode_address", {
        "address": "1600 Amphitheatre Parkway, Mountain View, CA"
    })
    print_result("geocode_address", result)
    
    if result.get("success") and result.get("results"):
        # Test reverse geocoding with the coordinates we just got
        coords = result["results"][0]
        print("\n🔄 Testing Reverse Geocoding...")
        reverse_result = await server.call_tool("reverse_geocode", {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"]
        })
        print_result("reverse_geocode", reverse_result)
    
    # Test places search
    print("\n🏪 Testing Places Search...")
    places_result = await server.call_tool("find_places", {
        "query": "coffee shops",
        "location": {
            "latitude": 37.422131,
            "longitude": -122.084801
        },
        "radius": 1000
    })
    print_result("find_places", places_result)
    
    # Test directions
    print("\n🗺️ Testing Directions...")
    directions_result = await server.call_tool("get_directions", {
        "origin": "San Francisco, CA",
        "destination": "Mountain View, CA",
        "mode": "driving"
    })
    print_result("get_directions", directions_result)

async def test_translate_apis(server: GoogleAPIServer):
    """Test Google Translate APIs"""
    print("\n🌍 Testing Google Translate APIs...")
    
    # Test translation
    print("\n🔄 Testing Translate Text...")
    translate_result = await server.call_tool("translate_text", {
        "text": "Hello, world! This is a test of the Google Translate API through MCP.",
        "target_language": "es",
        "source_language": "en"
    })
    print_result("translate_text", translate_result)
    
    # Test another language
    print("\n🔄 Testing Translate to French...")
    translate_fr_result = await server.call_tool("translate_text", {
        "text": "Hello, world! This is a test of the Google Translate API through MCP.",
        "target_language": "fr"
    })
    print_result("translate_text (French)", translate_fr_result)

async def test_complete_workflow(server: GoogleAPIServer):
    """Test a complete workflow combining multiple APIs"""
    print("\n🚀 Testing Complete Workflow...")
    
    # 1. Geocode a location
    print("\n1️⃣ Geocoding location...")
    location_result = await server.call_tool("geocode_address", {
        "address": "Times Square, New York"
    })
    
    if not location_result.get("success"):
        print("❌ Failed to geocode location")
        return
    
    coords = location_result["results"][0]
    print(f"✅ Found: {coords['formatted_address']}")
    
    # 2. Find nearby restaurants
    print("\n2️⃣ Finding nearby restaurants...")
    restaurants_result = await server.call_tool("find_places", {
        "query": "restaurants",
        "location": {
            "latitude": coords["latitude"],
            "longitude": coords["longitude"]
        },
        "radius": 1000
    })
    
    if not restaurants_result.get("success"):
        print("❌ Failed to find restaurants")
        return
    
    print(f"✅ Found {len(restaurants_result['places'])} restaurants")
    
    # 3. Get directions
    print("\n3️⃣ Getting directions...")
    directions_result = await server.call_tool("get_directions", {
        "origin": "JFK Airport",
        "destination": "Times Square, New York",
        "mode": "driving"
    })
    
    if not directions_result.get("success"):
        print("❌ Failed to get directions")
        return
    
    print(f"✅ Route: {directions_result['distance']} in {directions_result['duration']}")
    
    # 4. Translate summary
    print("\n4️⃣ Translating summary to Spanish...")
    summary = f"Visit to Times Square with {len(restaurants_result['places'])} restaurants nearby"
    translate_result = await server.call_tool("translate_text", {
        "text": summary,
        "target_language": "es"
    })
    
    if translate_result.get("success"):
        print(f"✅ Translation: {translate_result['translated_text']}")
    else:
        print("❌ Failed to translate")
    
    print("\n🎉 Complete workflow finished!")

async def main():
    """Main test function"""
    print("🌐 Google APIs MCP Server Test Client")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        return
    
    # Create configuration
    config = GoogleAPIConfig(
        api_key=api_key,
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
    
    # Create server instance
    server = GoogleAPIServer(config)
    
    print("✅ Server initialized successfully")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"🔐 OAuth2: {'Enabled' if config.client_id else 'Disabled'}")
    
    # Run tests
    try:
        # Test Maps APIs (always available with API key)
        await test_maps_apis(server)
        
        # Test Translate API (always available with API key)
        await test_translate_apis(server)
        
        # Test complete workflow
        await test_complete_workflow(server)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 