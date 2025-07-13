#!/usr/bin/env python3
"""
Google APIs MCP Server

A comprehensive Model Context Protocol (MCP) server that provides access to various Google APIs:
- Google Maps API (Geocoding, Places, Directions)
- Google Calendar API
- Google Drive API
- Google Sheets API
- Google Translate API
- Google Vision API

This server demonstrates how to integrate real Google APIs with MCP for AI agent access.

Features:
- OAuth2 authentication
- Rate limiting and caching
- Comprehensive error handling
- Async operations
- Structured responses

Usage:
    python google_apis_mcp_server.py

Environment Variables Required:
    GOOGLE_API_KEY: Your Google API key
    GOOGLE_CLIENT_ID: OAuth2 client ID (for user-specific APIs)
    GOOGLE_CLIENT_SECRET: OAuth2 client secret
    GOOGLE_REDIRECT_URI: OAuth2 redirect URI
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import hashlib
import pickle

from dotenv import find_dotenv, load_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Google API imports
try:
    import googlemaps
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import requests
except ImportError as e:
    print(f"Missing Google API dependencies: {e}")
    print("Install with: pip install googlemaps google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    exit(1)

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
except ImportError as e:
    print(f"Missing MCP dependencies: {e}")
    print("Install with: pip install mcp")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GoogleAPIConfig:
    """Configuration for Google APIs"""
    api_key: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: List[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/cloud-vision'
            ]

class GoogleAPICache:
    """Simple cache for API responses"""
    
    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{self._get_cache_key(key)}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                    if time.time() - data['timestamp'] < self.ttl:
                        return data['value']
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value"""
        cache_path = self._get_cache_path(key)
        try:
            data = {
                'value': value,
                'timestamp': time.time()
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

class GoogleAPIRateLimiter:
    """Rate limiter for Google APIs"""
    
    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
        self.request_count = 0
        self.reset_time = time.time() + 1
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()
        
        # Reset counter if a second has passed
        if current_time >= self.reset_time:
            self.request_count = 0
            self.reset_time = current_time + 1
        
        # Check if we need to wait
        if self.request_count >= self.requests_per_second:
            wait_time = self.reset_time - current_time
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.reset_time = time.time() + 1
        
        self.request_count += 1

class GoogleAPIServer:
    """Main Google APIs MCP Server"""
    
    def __init__(self, config: GoogleAPIConfig):
        self.config = config
        self.cache = GoogleAPICache()
        self.rate_limiter = GoogleAPIRateLimiter()
        
        # Initialize Google Maps client
        self.gmaps = googlemaps.Client(key=config.api_key)
        
        # Initialize other API clients
        self.calendar_service = None
        self.drive_service = None
        self.sheets_service = None
        self.translate_service = None
        self.vision_service = None
        
        # OAuth2 credentials
        self.credentials = None
        
        # Initialize OAuth2 if credentials provided
        if config.client_id and config.client_secret:
            self._initialize_oauth2()
    
    def _initialize_oauth2(self):
        """Initialize OAuth2 authentication"""
        try:
            creds = None
            token_path = Path("token.json")
            
            # Load existing credentials
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), self.config.scopes)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        {
                            "installed": {
                                "client_id": self.config.client_id,
                                "client_secret": self.config.client_secret,
                                "redirect_uris": [self.config.redirect_uri or "http://localhost"],
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token"
                            }
                        },
                        self.config.scopes
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            
            # Initialize services
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            self.translate_service = build('translate', 'v2', credentials=creds)
            self.vision_service = build('vision', 'v1', credentials=creds)
            
            logger.info("OAuth2 authentication successful")
            
        except Exception as e:
            logger.error(f"OAuth2 initialization failed: {e}")
    
    def list_tools(self) -> ListToolsResult:
        """List all available tools"""
        tools = self._define_tools()
        return ListToolsResult(tools=tools)
    
    def _define_tools(self) -> List[Tool]:
        """Define all available tools"""
        return [
            # Google Maps Tools
            Tool(
                name="geocode_address",
                description="Convert an address to coordinates using Google Maps Geocoding API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The address to geocode"
                        },
                        "components": {
                            "type": "object",
                            "description": "Component filtering (optional)",
                            "properties": {
                                "country": {"type": "string"},
                                "postal_code": {"type": "string"},
                                "locality": {"type": "string"}
                            }
                        }
                    },
                    "required": ["address"]
                }
            ),
            
            Tool(
                name="reverse_geocode",
                description="Convert coordinates to an address using Google Maps Geocoding API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude coordinate"
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude coordinate"
                        },
                        "result_type": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of results to return"
                        }
                    },
                    "required": ["latitude", "longitude"]
                }
            ),
            
            Tool(
                name="find_places",
                description="Find places using Google Places API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text search query"
                        },
                        "location": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            }
                        },
                        "radius": {
                            "type": "number",
                            "description": "Search radius in meters"
                        },
                        "type": {
                            "type": "string",
                            "description": "Place type filter"
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            Tool(
                name="get_directions",
                description="Get directions between locations using Google Maps Directions API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Origin address or coordinates"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination address or coordinates"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["driving", "walking", "bicycling", "transit"],
                            "description": "Travel mode"
                        },
                        "departure_time": {
                            "type": "string",
                            "description": "Departure time (ISO format)"
                        }
                    },
                    "required": ["origin", "destination"]
                }
            ),
            
            # Google Calendar Tools
            Tool(
                name="list_calendars",
                description="List available Google Calendars",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "show_hidden": {
                            "type": "boolean",
                            "description": "Include hidden calendars"
                        }
                    }
                }
            ),
            
            Tool(
                name="list_events",
                description="List calendar events",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: primary)"
                        },
                        "time_min": {
                            "type": "string",
                            "description": "Start time (ISO format)"
                        },
                        "time_max": {
                            "type": "string",
                            "description": "End time (ISO format)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of events"
                        }
                    }
                }
            ),
            
            Tool(
                name="create_event",
                description="Create a new calendar event",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "calendar_id": {
                            "type": "string",
                            "description": "Calendar ID (default: primary)"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Event title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description"
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time (ISO format)"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time (ISO format)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location"
                        }
                    },
                    "required": ["summary", "start_time", "end_time"]
                }
            ),
            
            # Google Drive Tools
            Tool(
                name="list_files",
                description="List files in Google Drive",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of results per page"
                        }
                    }
                }
            ),
            
            Tool(
                name="get_file_info",
                description="Get information about a specific file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "Google Drive file ID"
                        }
                    },
                    "required": ["file_id"]
                }
            ),
            
            # Google Sheets Tools
            Tool(
                name="read_sheet",
                description="Read data from Google Sheets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "Spreadsheet ID"
                        },
                        "range": {
                            "type": "string",
                            "description": "Range (e.g., 'Sheet1!A1:D10')"
                        }
                    },
                    "required": ["spreadsheet_id", "range"]
                }
            ),
            
            Tool(
                name="write_sheet",
                description="Write data to Google Sheets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "Spreadsheet ID"
                        },
                        "range": {
                            "type": "string",
                            "description": "Range (e.g., 'Sheet1!A1')"
                        },
                        "values": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                            "description": "Data to write"
                        }
                    },
                    "required": ["spreadsheet_id", "range", "values"]
                }
            ),
            
            # Google Translate Tools
            Tool(
                name="translate_text",
                description="Translate text using Google Translate API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to translate"
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (e.g., 'es', 'fr')"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code (auto-detect if not specified)"
                        }
                    },
                    "required": ["text", "target_language"]
                }
            ),
            
            # Google Vision Tools
            Tool(
                name="analyze_image",
                description="Analyze image using Google Vision API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of image to analyze"
                        },
                        "features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["LABEL_DETECTION", "TEXT_DETECTION", "FACE_DETECTION", "LANDMARK_DETECTION"]
                            },
                            "description": "Analysis features to perform"
                        }
                    },
                    "required": ["image_url"]
                }
            )
        ]
    
    async def _geocode_address(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Geocode an address"""
        await self.rate_limiter.wait_if_needed()
        
        address = arguments["address"]
        components = arguments.get("components", {})
        
        cache_key = f"geocode:{address}:{json.dumps(components, sort_keys=True)}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = self.gmaps.geocode(address, components=components)
            
            if result:
                geocode_data = {
                    "success": True,
                    "address": address,
                    "results": []
                }
                
                for item in result:
                    geocode_data["results"].append({
                        "formatted_address": item["formatted_address"],
                        "latitude": item["geometry"]["location"]["lat"],
                        "longitude": item["geometry"]["location"]["lng"],
                        "place_id": item["place_id"],
                        "types": item["types"]
                    })
                
                self.cache.set(cache_key, geocode_data)
                return geocode_data
            else:
                return {
                    "success": False,
                    "error": "No results found",
                    "address": address
                }
                
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def _reverse_geocode(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse geocode coordinates"""
        await self.rate_limiter.wait_if_needed()
        
        lat = arguments["latitude"]
        lng = arguments["longitude"]
        result_type = arguments.get("result_type", [])
        
        cache_key = f"reverse_geocode:{lat}:{lng}:{json.dumps(result_type, sort_keys=True)}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = self.gmaps.reverse_geocode((lat, lng), result_type=result_type)
            
            if result:
                reverse_data = {
                    "success": True,
                    "coordinates": {"latitude": lat, "longitude": lng},
                    "results": []
                }
                
                for item in result:
                    reverse_data["results"].append({
                        "formatted_address": item["formatted_address"],
                        "place_id": item["place_id"],
                        "types": item["types"],
                        "address_components": item["address_components"]
                    })
                
                self.cache.set(cache_key, reverse_data)
                return reverse_data
            else:
                return {
                    "success": False,
                    "error": "No results found",
                    "coordinates": {"latitude": lat, "longitude": lng}
                }
                
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return {
                "success": False,
                "error": str(e),
                "coordinates": {"latitude": lat, "longitude": lng}
            }
    
    async def _find_places(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Find places using Places API"""
        await self.rate_limiter.wait_if_needed()
        
        query = arguments["query"]
        location = arguments.get("location")
        radius = arguments.get("radius", 5000)
        place_type = arguments.get("type")
        
        cache_key = f"places:{query}:{json.dumps(location or {}, sort_keys=True)}:{radius}:{place_type}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            if location:
                result = self.gmaps.places_nearby(
                    location=(location["latitude"], location["longitude"]),
                    radius=radius,
                    type=place_type,
                    keyword=query
                )
            else:
                result = self.gmaps.places(query, type=place_type)
            
            if result.get("results"):
                places_data = {
                    "success": True,
                    "query": query,
                    "places": []
                }
                
                for place in result["results"]:
                    places_data["places"].append({
                        "name": place["name"],
                        "place_id": place["place_id"],
                        "formatted_address": place.get("formatted_address"),
                        "latitude": place["geometry"]["location"]["lat"],
                        "longitude": place["geometry"]["location"]["lng"],
                        "rating": place.get("rating"),
                        "types": place["types"],
                        "photos": len(place.get("photos", []))
                    })
                
                self.cache.set(cache_key, places_data)
                return places_data
            else:
                return {
                    "success": False,
                    "error": "No places found",
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Places search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _get_directions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get directions between locations"""
        await self.rate_limiter.wait_if_needed()
        
        origin = arguments["origin"]
        destination = arguments["destination"]
        mode = arguments.get("mode", "driving")
        departure_time = arguments.get("departure_time")
        
        cache_key = f"directions:{origin}:{destination}:{mode}:{departure_time}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            directions_params = {
                "origin": origin,
                "destination": destination,
                "mode": mode
            }
            
            if departure_time:
                directions_params["departure_time"] = departure_time
            
            result = self.gmaps.directions(**directions_params)
            
            if result:
                route = result[0]
                directions_data = {
                    "success": True,
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "summary": route["summary"],
                    "distance": route["legs"][0]["distance"]["text"],
                    "duration": route["legs"][0]["duration"]["text"],
                    "steps": []
                }
                
                for step in route["legs"][0]["steps"]:
                    directions_data["steps"].append({
                        "instruction": step["html_instructions"],
                        "distance": step["distance"]["text"],
                        "duration": step["duration"]["text"]
                    })
                
                self.cache.set(cache_key, directions_data)
                return directions_data
            else:
                return {
                    "success": False,
                    "error": "No route found",
                    "origin": origin,
                    "destination": destination
                }
                
        except Exception as e:
            logger.error(f"Directions error: {e}")
            return {
                "success": False,
                "error": str(e),
                "origin": origin,
                "destination": destination
            }
    
    async def _list_calendars(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List Google Calendars"""
        if not self.calendar_service:
            return {"success": False, "error": "Calendar service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            show_hidden = arguments.get("show_hidden", False)
            
            calendars = self.calendar_service.calendarList().list(
                showHidden=show_hidden
            ).execute()
            
            calendar_list = []
            for calendar in calendars.get("items", []):
                calendar_list.append({
                    "id": calendar["id"],
                    "summary": calendar["summary"],
                    "description": calendar.get("description"),
                    "primary": calendar.get("primary", False),
                    "access_role": calendar["accessRole"]
                })
            
            return {
                "success": True,
                "calendars": calendar_list,
                "total": len(calendar_list)
            }
            
        except Exception as e:
            logger.error(f"Calendar list error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _list_events(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events"""
        if not self.calendar_service:
            return {"success": False, "error": "Calendar service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            calendar_id = arguments.get("calendar_id", "primary")
            time_min = arguments.get("time_min", datetime.now().isoformat() + "Z")
            time_max = arguments.get("time_max")
            max_results = arguments.get("max_results", 10)
            
            events_params = {
                "calendarId": calendar_id,
                "timeMin": time_min,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime"
            }
            
            if time_max:
                events_params["timeMax"] = time_max
            
            events_result = self.calendar_service.events().list(**events_params).execute()
            
            events = []
            for event in events_result.get("items", []):
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                
                events.append({
                    "id": event["id"],
                    "summary": event.get("summary", "No title"),
                    "description": event.get("description"),
                    "start": start,
                    "end": end,
                    "location": event.get("location"),
                    "attendees": len(event.get("attendees", []))
                })
            
            return {
                "success": True,
                "events": events,
                "total": len(events)
            }
            
        except Exception as e:
            logger.error(f"Events list error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_event(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event"""
        if not self.calendar_service:
            return {"success": False, "error": "Calendar service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            calendar_id = arguments.get("calendar_id", "primary")
            
            event = {
                "summary": arguments["summary"],
                "description": arguments.get("description"),
                "start": {
                    "dateTime": arguments["start_time"],
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": arguments["end_time"],
                    "timeZone": "UTC"
                }
            }
            
            if arguments.get("location"):
                event["location"] = arguments["location"]
            
            created_event = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event["id"],
                "summary": created_event["summary"],
                "start": created_event["start"]["dateTime"],
                "end": created_event["end"]["dateTime"]
            }
            
        except Exception as e:
            logger.error(f"Event creation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _list_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List Google Drive files"""
        if not self.drive_service:
            return {"success": False, "error": "Drive service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            query = arguments.get("query", "")
            page_size = arguments.get("page_size", 10)
            
            files_result = self.drive_service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            files = []
            for file in files_result.get("files", []):
                files.append({
                    "id": file["id"],
                    "name": file["name"],
                    "type": file["mimeType"],
                    "size": file.get("size"),
                    "modified": file["modifiedTime"]
                })
            
            return {
                "success": True,
                "files": files,
                "total": len(files)
            }
            
        except Exception as e:
            logger.error(f"Files list error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_file_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get Google Drive file information"""
        if not self.drive_service:
            return {"success": False, "error": "Drive service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            file_id = arguments["file_id"]
            
            file = self.drive_service.files().get(
                fileId=file_id,
                fields="id,name,mimeType,size,modifiedTime,createdTime,parents,webViewLink"
            ).execute()
            
            return {
                "success": True,
                "file": {
                    "id": file["id"],
                    "name": file["name"],
                    "type": file["mimeType"],
                    "size": file.get("size"),
                    "created": file["createdTime"],
                    "modified": file["modifiedTime"],
                    "web_link": file.get("webViewLink")
                }
            }
            
        except Exception as e:
            logger.error(f"File info error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _read_sheet(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Read Google Sheets data"""
        if not self.sheets_service:
            return {"success": False, "error": "Sheets service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get("values", [])
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "data": values,
                "rows": len(values),
                "columns": len(values[0]) if values else 0
            }
            
        except Exception as e:
            logger.error(f"Sheet read error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _write_sheet(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Write data to Google Sheets"""
        if not self.sheets_service:
            return {"success": False, "error": "Sheets service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            spreadsheet_id = arguments["spreadsheet_id"]
            range_name = arguments["range"]
            values = arguments["values"]
            
            body = {
                "values": values
            }
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "range": range_name,
                "updated_cells": result["updatedCells"],
                "updated_rows": result["updatedRows"],
                "updated_columns": result["updatedColumns"]
            }
            
        except Exception as e:
            logger.error(f"Sheet write error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _translate_text(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text using Google Translate API"""
        if not self.translate_service:
            return {"success": False, "error": "Translate service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            text = arguments["text"]
            target_language = arguments["target_language"]
            source_language = arguments.get("source_language")
            
            translate_params = {
                "q": text,
                "target": target_language
            }
            
            if source_language:
                translate_params["source"] = source_language
            
            result = self.translate_service.translations().list(**translate_params).execute()
            
            translations = result.get("translations", [])
            if translations:
                return {
                    "success": True,
                    "original_text": text,
                    "translated_text": translations[0]["translatedText"],
                    "source_language": translations[0].get("detectedSourceLanguage", source_language),
                    "target_language": target_language
                }
            else:
                return {
                    "success": False,
                    "error": "No translation available",
                    "text": text
                }
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image using Google Vision API"""
        if not self.vision_service:
            return {"success": False, "error": "Vision service not available"}
        
        await self.rate_limiter.wait_if_needed()
        
        try:
            image_url = arguments["image_url"]
            features = arguments.get("features", ["LABEL_DETECTION"])
            
            # Download image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Prepare request
            image = {"content": response.content}
            feature_objects = [{"type": feature} for feature in features]
            
            request = {
                "image": image,
                "features": feature_objects
            }
            
            result = self.vision_service.images().annotate(body=request).execute()
            
            analysis = {}
            
            # Process labels
            if "labelAnnotations" in result["responses"][0]:
                labels = []
                for label in result["responses"][0]["labelAnnotations"]:
                    labels.append({
                        "description": label["description"],
                        "confidence": label["score"]
                    })
                analysis["labels"] = labels
            
            # Process text
            if "textAnnotations" in result["responses"][0]:
                text_annotations = result["responses"][0]["textAnnotations"]
                if text_annotations:
                    analysis["text"] = text_annotations[0]["description"]
            
            # Process faces
            if "faceAnnotations" in result["responses"][0]:
                faces = []
                for face in result["responses"][0]["faceAnnotations"]:
                    faces.append({
                        "joy_likelihood": face["joyLikelihood"],
                        "sorrow_likelihood": face["sorrowLikelihood"],
                        "anger_likelihood": face["angerLikelihood"],
                        "surprise_likelihood": face["surpriseLikelihood"]
                    })
                analysis["faces"] = faces
            
            # Process landmarks
            if "landmarkAnnotations" in result["responses"][0]:
                landmarks = []
                for landmark in result["responses"][0]["landmarkAnnotations"]:
                    landmarks.append({
                        "description": landmark["description"],
                        "confidence": landmark["score"]
                    })
                analysis["landmarks"] = landmarks
            
            return {
                "success": True,
                "image_url": image_url,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by name"""
        try:
            if name == "geocode_address":
                return await self._geocode_address(arguments)
            elif name == "reverse_geocode":
                return await self._reverse_geocode(arguments)
            elif name == "find_places":
                return await self._find_places(arguments)
            elif name == "get_directions":
                return await self._get_directions(arguments)
            elif name == "list_calendars":
                return await self._list_calendars(arguments)
            elif name == "list_events":
                return await self._list_events(arguments)
            elif name == "create_event":
                return await self._create_event(arguments)
            elif name == "list_files":
                return await self._list_files(arguments)
            elif name == "get_file_info":
                return await self._get_file_info(arguments)
            elif name == "read_sheet":
                return await self._read_sheet(arguments)
            elif name == "write_sheet":
                return await self._write_sheet(arguments)
            elif name == "translate_text":
                return await self._translate_text(arguments)
            elif name == "analyze_image":
                return await self._analyze_image(arguments)
            else:
                return {"success": False, "error": f"Unknown tool: {name}"}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """Main function to run the MCP server"""
    
    # Load configuration from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Get your API key from: https://console.cloud.google.com/apis/credentials")
        return
    
    # Create configuration
    config = GoogleAPIConfig(
        api_key=api_key,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )
    
    # Create server instance
    server = GoogleAPIServer(config)
    
    # Create MCP server
    mcp_server = Server("google-apis")
    
    @mcp_server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        """Handle list tools request"""
        return server.list_tools()
    
    @mcp_server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool call request"""
        result = await server.call_tool(name, arguments)
        
        # Convert result to MCP format
        content = [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        return CallToolResult(
            content=content,
            isError=not result.get("success", False)
        )
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 