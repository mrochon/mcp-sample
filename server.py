# server.py
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI


# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Add a weather tool (mock implementation)
@mcp.tool()
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    # Mock weather data
    weather_data = {
        "seattle": "Cloudy, 15°C",
        "new york": "Sunny, 22°C", 
        "london": "Rainy, 12°C",
        "tokyo": "Partly cloudy, 18°C"
    }
    location_lower = location.lower()
    if location_lower in weather_data:
        return f"Weather in {location}: {weather_data[location_lower]}"
    else:
        return f"Weather in {location}: Sunny, 20°C (mock data)"

# Add a text processing tool
@mcp.tool()
def count_words(text: str) -> int:
    """Count the number of words in text"""
    return len(text.split())

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Main execution block - this is required to run the server
if __name__ == "__main__":
    import uvicorn
    # Create the HTTP app that supports text/event-stream
    app = mcp.streamable_http_app()
    # Run the server on localhost:8000
    uvicorn.run(app, host="localhost", port=8000)
else:
    # For deployment, expose the app
    app = mcp.streamable_http_app()

