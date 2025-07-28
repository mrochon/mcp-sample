#!/usr/bin/env python3
"""
Start the MCP HTTP server
"""
import uvicorn
from server import app

if __name__ == "__main__":
    print("Starting MCP HTTP server on http://localhost:8000")
    print("MCP endpoint will be available at: http://localhost:8000/mcp")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
