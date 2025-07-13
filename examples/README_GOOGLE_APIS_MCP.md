# 🌐 Google APIs MCP Server

A comprehensive Model Context Protocol (MCP) server that provides access to multiple Google APIs. This server demonstrates how to integrate real Google services with MCP for AI agent access.

## 🚀 Features

### Supported Google APIs
- **📍 Google Maps API** - Geocoding, Places, Directions
- **📅 Google Calendar API** - List calendars, events, create events
- **📁 Google Drive API** - List files, get file information
- **📊 Google Sheets API** - Read and write spreadsheet data
- **🌍 Google Translate API** - Text translation
- **👁️ Google Vision API** - Image analysis (labels, text, faces, landmarks)

### Production Features
- **🔐 OAuth2 Authentication** - Secure access to user-specific APIs
- **⚡ Rate Limiting** - Prevents API quota exhaustion
- **💾 Caching** - Reduces API calls and improves performance
- **🛡️ Error Handling** - Comprehensive error management
- **🔄 Async Operations** - Non-blocking API calls
- **📝 Structured Responses** - Consistent JSON output format

## 📋 Prerequisites

### Required Knowledge
- ✅ Basic Python programming
- ✅ Understanding of APIs and HTTP requests
- ✅ Familiarity with OAuth2 (for user-specific APIs)

### Google Cloud Setup
1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Required APIs**
   - Google Maps JavaScript API
   - Google Calendar API
   - Google Drive API
   - Google Sheets API
   - Google Translate API
   - Google Vision API

3. **Create API Credentials**
   - API Key (for Maps, Translate, Vision)
   - OAuth2 Client ID (for Calendar, Drive, Sheets)

## 🔧 Installation

### 1. Install Dependencies

```bash
# Core dependencies
pip install googlemaps google-auth-oauthlib google-auth-httplib2 google-api-python-client

# MCP dependencies
pip install mcp

# Additional utilities
pip install requests python-dotenv
```

### 2. Set Up Environment Variables

Create a `.env` file in the examples directory:

```bash
# Required for all APIs
GOOGLE_API_KEY=your_google_api_key_here

# Required for user-specific APIs (Calendar, Drive, Sheets)
GOOGLE_CLIENT_ID=your_oauth2_client_id
GOOGLE_CLIENT_SECRET=your_oauth2_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080
```

### 3. Get Google API Credentials

#### API Key Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "API Key"
4. Copy the API key to your `.env` file

#### OAuth2 Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "OAuth 2.0 Client IDs"
4. Choose "Desktop application"
5. Download the JSON file and extract client ID and secret
6. Add to your `.env` file

## 🎯 Quick Start

### 1. Run the Server

```bash
cd examples
python google_apis_mcp_server.py
```

### 2. Test Basic Functionality

The server will start and be ready to accept MCP tool calls. You can test it with a simple client:

```python
import asyncio
from google_apis_mcp_server import GoogleAPIServer, GoogleAPIConfig

async def test_server():
    config = GoogleAPIConfig(api_key="your_api_key")
    server = GoogleAPIServer(config)
    
    # Test geocoding
    result = await server.call_tool("geocode_address", {
        "address": "New York, NY"
    })
    print(result)

asyncio.run(test_server())
```

## 🛠️ Available Tools

### 📍 Google Maps Tools

#### 1. Geocode Address
Convert addresses to coordinates.

```python
await server.call_tool("geocode_address", {
    "address": "1600 Amphitheatre Parkway, Mountain View, CA",
    "components": {
        "country": "US"
    }
})
```

**Response:**
```json
{
    "success": true,
    "address": "1600 Amphitheatre Parkway, Mountain View, CA",
    "results": [
        {
            "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
            "latitude": 37.422131,
            "longitude": -122.084801,
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
            "types": ["street_address"]
        }
    ]
}
```

#### 2. Reverse Geocode
Convert coordinates to addresses.

```python
await server.call_tool("reverse_geocode", {
    "latitude": 37.422131,
    "longitude": -122.084801,
    "result_type": ["street_address"]
})
```

#### 3. Find Places
Search for places using Google Places API.

```python
await server.call_tool("find_places", {
    "query": "coffee shops",
    "location": {
        "latitude": 37.422131,
        "longitude": -122.084801
    },
    "radius": 1000,
    "type": "restaurant"
})
```

#### 4. Get Directions
Get directions between locations.

```python
await server.call_tool("get_directions", {
    "origin": "San Francisco, CA",
    "destination": "Mountain View, CA",
    "mode": "driving",
    "departure_time": "2024-01-15T09:00:00Z"
})
```

### 📅 Google Calendar Tools

#### 1. List Calendars
Get list of available calendars.

```python
await server.call_tool("list_calendars", {
    "show_hidden": false
})
```

#### 2. List Events
Get calendar events.

```python
await server.call_tool("list_events", {
    "calendar_id": "primary",
    "time_min": "2024-01-15T00:00:00Z",
    "time_max": "2024-01-16T00:00:00Z",
    "max_results": 10
})
```

#### 3. Create Event
Create a new calendar event.

```python
await server.call_tool("create_event", {
    "summary": "Team Meeting",
    "description": "Weekly team sync",
    "start_time": "2024-01-15T10:00:00Z",
    "end_time": "2024-01-15T11:00:00Z",
    "location": "Conference Room A"
})
```

### 📁 Google Drive Tools

#### 1. List Files
List files in Google Drive.

```python
await server.call_tool("list_files", {
    "query": "name contains 'report'",
    "page_size": 20
})
```

#### 2. Get File Info
Get information about a specific file.

```python
await server.call_tool("get_file_info", {
    "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
})
```

### 📊 Google Sheets Tools

#### 1. Read Sheet
Read data from Google Sheets.

```python
await server.call_tool("read_sheet", {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "range": "Sheet1!A1:D10"
})
```

#### 2. Write Sheet
Write data to Google Sheets.

```python
await server.call_tool("write_sheet", {
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "range": "Sheet1!A1",
    "values": [
        ["Name", "Age", "City"],
        ["John", "25", "New York"],
        ["Jane", "30", "San Francisco"]
    ]
})
```

### 🌍 Google Translate Tools

#### 1. Translate Text
Translate text between languages.

```python
await server.call_tool("translate_text", {
    "text": "Hello, world!",
    "target_language": "es",
    "source_language": "en"
})
```

### 👁️ Google Vision Tools

#### 1. Analyze Image
Analyze image content.

```python
await server.call_tool("analyze_image", {
    "image_url": "https://example.com/image.jpg",
    "features": ["LABEL_DETECTION", "TEXT_DETECTION", "FACE_DETECTION"]
})
```

## 🔐 Authentication

### API Key Authentication
Used for Maps, Translate, and Vision APIs. Simple and suitable for server-to-server communication.

### OAuth2 Authentication
Required for Calendar, Drive, and Sheets APIs. Provides access to user-specific data.

**First-time setup:**
1. Run the server with OAuth2 credentials
2. Browser will open for authentication
3. Grant permissions to your application
4. Credentials are saved to `token.json`

## ⚡ Performance Features

### Caching
- **Automatic caching** of API responses
- **Configurable TTL** (default: 1 hour)
- **Cache directory**: `.cache/`
- **Cache key**: MD5 hash of request parameters

### Rate Limiting
- **Default limit**: 10 requests per second
- **Automatic queuing** when limit reached
- **Configurable** per API service

### Error Handling
- **Graceful degradation** when APIs are unavailable
- **Detailed error messages** for debugging
- **Retry logic** for transient failures

## 🧪 Testing

### Unit Tests
```bash
# Run tests
python -m pytest tests/test_google_apis_mcp.py

# Run with coverage
python -m pytest --cov=google_apis_mcp_server tests/
```

### Integration Tests
```bash
# Test with real API calls
python tests/test_integration.py
```

## 📊 Monitoring

### Logging
The server provides comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Metrics
Track API usage and performance:

```python
# Access rate limiter stats
print(f"Requests per second: {server.rate_limiter.request_count}")

# Access cache stats
print(f"Cache hits: {server.cache.hit_count}")
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional (for user-specific APIs)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080

# Optional (for customization)
GOOGLE_CACHE_TTL=3600
GOOGLE_RATE_LIMIT=10
```

### Custom Configuration
```python
from google_apis_mcp_server import GoogleAPIConfig

config = GoogleAPIConfig(
    api_key="your_key",
    client_id="your_client_id",
    client_secret="your_client_secret",
    scopes=[
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/drive'
    ]
)
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "google_apis_mcp_server.py"]
```

### Environment Setup
```bash
# Production environment variables
export GOOGLE_API_KEY=your_production_key
export GOOGLE_CLIENT_ID=your_production_client_id
export GOOGLE_CLIENT_SECRET=your_production_client_secret
export GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth/callback
```

### Security Considerations
- **API Key Security**: Store keys securely, use environment variables
- **OAuth2 Security**: Use HTTPS in production, validate redirect URIs
- **Rate Limiting**: Monitor API usage to prevent quota exhaustion
- **Caching**: Consider using Redis for distributed caching

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: API key not valid
```
**Solution**: Verify API key in Google Cloud Console and enable required APIs.

#### 2. OAuth2 Authentication Issues
```
Error: OAuth2 authentication failed
```
**Solution**: Check client ID/secret and redirect URI configuration.

#### 3. Rate Limiting
```
Rate limit reached, waiting X seconds
```
**Solution**: This is normal behavior. Consider increasing rate limits or implementing caching.

#### 4. Missing Dependencies
```
ImportError: No module named 'googlemaps'
```
**Solution**: Install required packages: `pip install googlemaps google-auth-oauthlib`

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Examples

### Complete AI Agent Example
```python
import asyncio
from google_apis_mcp_server import GoogleAPIServer, GoogleAPIConfig

async def travel_assistant():
    config = GoogleAPIConfig(api_key="your_key")
    server = GoogleAPIServer(config)
    
    # 1. Geocode destination
    location = await server.call_tool("geocode_address", {
        "address": "Times Square, New York"
    })
    
    # 2. Find nearby restaurants
    restaurants = await server.call_tool("find_places", {
        "query": "restaurants",
        "location": {
            "latitude": location["results"][0]["latitude"],
            "longitude": location["results"][0]["longitude"]
        },
        "radius": 1000
    })
    
    # 3. Get directions
    directions = await server.call_tool("get_directions", {
        "origin": "JFK Airport",
        "destination": "Times Square, New York",
        "mode": "driving"
    })
    
    # 4. Create calendar event
    event = await server.call_tool("create_event", {
        "summary": "New York Trip",
        "description": f"Visit to Times Square. Found {len(restaurants['places'])} restaurants nearby.",
        "start_time": "2024-02-15T10:00:00Z",
        "end_time": "2024-02-15T18:00:00Z",
        "location": "Times Square, New York"
    })
    
    return {
        "location": location,
        "restaurants": restaurants,
        "directions": directions,
        "event": event
    }

# Run the assistant
result = asyncio.run(travel_assistant())
print(result)
```

## 🔗 Resources

### Official Documentation
- [Google Maps API](https://developers.google.com/maps)
- [Google Calendar API](https://developers.google.com/calendar)
- [Google Drive API](https://developers.google.com/drive)
- [Google Sheets API](https://developers.google.com/sheets)
- [Google Translate API](https://cloud.google.com/translate)
- [Google Vision API](https://cloud.google.com/vision)

### MCP Resources
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Official MCP Documentation](https://modelcontextprotocol.io/)

### Community
- [Google Cloud Community](https://cloud.google.com/community)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy coding with Google APIs! 🌐🚀**

*This MCP server demonstrates best practices for integrating real-world APIs with AI agents through the Model Context Protocol.* 