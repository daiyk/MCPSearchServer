from typing import Any
import json
import os
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
SEARCH_AGENT = "docs/1.0"
SERPER_ENDPOINT = "https://google.serper.dev/search"

mcp = FastMCP("search") # initialize the FastMCP server

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
                SERPER_ENDPOINT,
                headers=headers,
                json=payload  # httpx will handle JSON serialization automatically
            )
            response.raise_for_status()  # Raises an error for 4xx/5xx responses
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
async def extract_search_result(link: str):
    """
    Extracts the text from the search result link.
    """
    # visit the link and get the content
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
               link,
               timeout=30,  # Set a timeout for the request
            )
            response.raise_for_status()  # Raises an error for 4xx/5xx responses
            if response.status_code == 200:
                soap = BeautifulSoup(response.text, "html.parser")
                # Extract the text from the soup
                return soap.get_text()
            else:
                print(f"Error Extract the search results: {response.status_code}")
                return None
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")
            return None

@mcp.tool()
async def search_tool(query: str) -> str:
    """
    Search Google with a give query string using the Serper API.
    Args:
        query (str): The search query.
    Returns:
        str: The search results in JSON format.
    """
    result = await search_google(query)
    if len(result["organic"])>0:
        searchResult = result["organic"]
        # Extract the first two results
        searchResult = searchResult[:2]
        # extract the text from the search result
        searchResult = extract_search_result(searchResult)
        print(json.dumps(searchResult, indent=2))
        return searchResult
    else:
        return "No results found."

if __name__ == "__main__":
    mcp.run(transport="stdio")
