from typing import Any
import json
import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
USER_AGENT = "docs/1.0"
API_BASE  = "https://google.serper.dev/search"
def main():
    print("Hello from mcppythontestserver!")


async def search_google(query: str) -> list | None:
    api_key = os.getenv("SERPER_API_KEY")
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        "q": query
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                API_BASE,
                headers=headers,
                json=payload  # httpx will handle JSON serialization automatically
            )
            
            if response.status_code == 200:
                result = response.json()  # httpx can parse JSON directly
                print(response.text)
                return result
            else:
                print(f"Error: {response.status_code}")
                return None
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")
            return None

@mcp.tool()
async def search_tool(query: str) -> str:
    result = await search_google(query)
    if result:
        return json.dumps(result, indent=2)
    else:
        return "No results found."

if __name__ == "__main__":
    main()
