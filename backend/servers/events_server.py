"""
Events MCP Server.
Independent MCP server exposing campus club/fest events as tools.
Run standalone with: python servers/events_server.py
"""
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).parent.parent / "data" / "events.json"

mcp = FastMCP("events")


@mcp.tool()
def get_events() -> list:
    """Return all upcoming campus events with name, date, time, venue, and club."""
    return json.loads(DATA.read_text())


@mcp.tool()
def find_events_by_club(club: str) -> list:
    """Return upcoming events organised by a specific club or society."""
    events = json.loads(DATA.read_text())
    return [e for e in events if club.lower() in e["club"].lower()]


if __name__ == "__main__":
    mcp.run()
