# """
# Cafeteria MCP Server.
# Independent MCP server exposing the mess/cafeteria menu as tools.
# Run standalone with: python servers/menu_server.py
# """
# import json
# from pathlib import Path
# from mcp.server.fastmcp import FastMCP

# DATA = Path(__file__).parent.parent / "data" / "menu.json"

# mcp = FastMCP("cafeteria")


# @mcp.tool()
# def get_todays_menu() -> dict:
#     """Return today's lunch and dinner in the campus cafeteria."""
#     m = json.loads(DATA.read_text())
#     return {"date": m["today"], "lunch": m["today_lunch"], "dinner": m["today_dinner"]}


# @mcp.tool()
# def get_menu_for_day(day: str) -> dict:
#     """Return lunch and dinner for a given weekday (e.g. 'Monday')."""
#     m = json.loads(DATA.read_text())
#     day = day.capitalize()
#     if day in m["week"]:
#         return {"day": day, **m["week"][day]}
#     return {"error": f"No menu found for '{day}'. Use a weekday like Monday."}


# if __name__ == "__main__":
#     mcp.run()

"""
Cafeteria MCP Server.

Independent MCP server exposing the mess/cafeteria menu as tools.

Run standalone with:
    python servers/menu_server.py
"""

import json
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).parent.parent / "data" / "menu.json"

mcp = FastMCP("cafeteria")


# @mcp.tool()
# def get_todays_menu() -> dict:
#     """
#     Return today's breakfast, lunch, and dinner based on the current weekday.
#     """
#     menu = json.loads(DATA.read_text())

#     today = datetime.now().strftime("%A")

#     if today not in menu:
#         return {"error": f"No menu available for {today}"}

#     return {
#         "day": today,
#         "breakfast": menu[today]["breakfast"],
#         "lunch": menu[today]["lunch"],
#         "dinner": menu[today]["dinner"],
#     }


# @mcp.tool()
# def get_menu_for_day(day: str) -> dict:
#     """
#     Return breakfast, lunch, and dinner for a specified weekday.
#     Example: Monday, Tuesday, Wednesday...
#     """
#     menu = json.loads(DATA.read_text())

#     day = day.strip().capitalize()

#     if day not in menu:
#         return {
#             "error": f"No menu found for '{day}'. Use a weekday like Monday."
#         }

#     return {
#         "day": day,
#         "breakfast": menu[day]["breakfast"],
#         "lunch": menu[day]["lunch"],
#         "dinner": menu[day]["dinner"],
#     }
from datetime import datetime, timedelta

@mcp.tool()
def get_menu_for_day(day: str) -> dict:
    """
    Return breakfast, lunch and dinner for a given day.

    Examples:
    - Monday
    - Tuesday
    - today
    - tomorrow
    """

    menu = json.loads(DATA.read_text())

    day = day.strip().lower()

    if day == "today":
        day = datetime.now().strftime("%A")

    elif day == "tomorrow":
        day = (datetime.now() + timedelta(days=1)).strftime("%A")

    else:
        day = day.capitalize()

    if day not in menu:
        return {
            "error": f"No menu found for '{day}'."
        }

    return {
        "day": day,
        "breakfast": menu[day]["breakfast"],
        "lunch": menu[day]["lunch"],
        "dinner": menu[day]["dinner"],
    }

if __name__ == "__main__":
    mcp.run()