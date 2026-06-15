"""
Library MCP Server.
An independent Model Context Protocol server that exposes the campus
library catalog as tools the AI can call. Run on its own with:
    python servers/library_server.py
It speaks MCP over stdio, so the host (agent.py) launches it as a subprocess.
"""
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).parent.parent / "data" / "books.json"

mcp = FastMCP("library")


@mcp.tool()
def search_book(title: str) -> dict:
    """Search the campus library catalog for a book by full or partial title.
    Returns availability, number of copies, author, and shelf location."""
    books = json.loads(DATA.read_text())
    for b in books:
        if title.lower() in b["title"].lower():
            return b
    return {"error": f"No book matching '{title}' was found in the catalog."}


@mcp.tool()
def list_books() -> list:
    """List every book in the campus library catalog with its availability."""
    return json.loads(DATA.read_text())


if __name__ == "__main__":
    mcp.run()  # defaults to stdio transport
