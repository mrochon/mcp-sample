
import requests

response = requests.get("http://127.0.0.1:8000/mcp", headers={"Accept": "text/event-stream"})
print(response.status_code)
print(response.text)
