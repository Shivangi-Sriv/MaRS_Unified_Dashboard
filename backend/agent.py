from dotenv import load_dotenv
load_dotenv()

"""
The MCP Host (a.k.a. the "router").

This connects to every independent MCP server, asks each one what tools it
offers, and gives those tool *descriptions* to Gemini. When Gemini decides to
call a tool, we route the call to the correct server over MCP, run it, feed the
result back, and let Gemini write the final answer.

We drive the tool-calling loop manually (instead of passing the live MCP
sessions straight into Gemini) because the SDK deep-copies its config, and a
live session can't be copied -> "cannot pickle '_asyncio.Future' object".
Doing the loop ourselves is version-proof and lets us report exactly which
servers handled each question.

"""
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

BASE = Path(__file__).parent
SERVERS = [
    "library_server.py",
    "events_server.py",
    "menu_server.py",
    "handbook_server.py",
]

MODEL = "gemini-2.5-flash"  # change if your key has access to a different model

client = genai.Client()  # reads GEMINI_API_KEY from the environment
today = datetime.now().strftime("%Y-%m-%d")

SYSTEM = (
    f"Today's date is {today}. "
    "You are the Campus Assistant for a college. "
    "Answer student questions about the library, cafeteria menu, campus events, and academic policies. "
    "Always use the available tools to fetch real data before answering. "
    "When users ask about today, tomorrow, dates, weekdays, or date ranges, "
    "use the tools and reason using today's date. "
    "Keep answers short, friendly, and concrete."
)


def _result_text(call_result) -> str:
    """Flatten an MCP tool result into plain text."""
    parts = []
    for block in call_result.content:
        parts.append(getattr(block, "text", str(block)))
    return "\n".join(parts)


async def ask(message: str) -> dict:
    """Run one question through the full MCP routing pipeline.

    Returns {"answer": str, "tools_used": [str, ...]}.
    """
    async with AsyncExitStack() as stack:
        # 1. Connect to every MCP server and collect its tools.
        tool_to_session = {}          # tool name -> the session that owns it
        declarations = []             # Gemini function declarations

        for fname in SERVERS:
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(BASE / "servers" / fname)],
            )
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            tools = (await session.list_tools()).tools
            for t in tools:
                tool_to_session[t.name] = session
                declarations.append(
                    types.FunctionDeclaration(
                        name=t.name,
                        description=t.description or "",
                        parameters_json_schema=t.inputSchema,
                    )
                )

        gemini_tools = [types.Tool(function_declarations=declarations)]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0,
            tools=gemini_tools,
            # We run the loop ourselves, so turn the SDK's auto-calling off.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        # 2. The conversation loop: ask -> run any tool calls -> ask again.
        contents = [types.Content(role="user", parts=[types.Part(text=message)])]
        tools_used = []
        for _ in range(5):
            try:
                response = await client.aio.models.generate_content(
                    model=MODEL,
                    contents=contents,
                    config=config
                )
            except Exception:
                return {
                    "answer": "AI service temporarily unavailable. Please try again later.",
                    "tools_used": tools_used,
                }

            calls = response.function_calls
            if not calls:
                return {"answer": response.text or "", "tools_used": tools_used}

            # Record the model's tool-call turn, then answer each call.
            contents.append(response.candidates[0].content)
            tool_parts = []
            for fc in calls:
                if fc.name not in tools_used:
                    tools_used.append(fc.name)
                session = tool_to_session.get(fc.name)
                if session is None:
                    output = f"Error: no server provides tool '{fc.name}'."
                else:
                    result = await session.call_tool(fc.name, dict(fc.args or {}))
                    output = _result_text(result)
                tool_parts.append(
                    types.Part.from_function_response(
                        name=fc.name, response={"result": output}
                    )
                )
            contents.append(types.Content(role="user", parts=tool_parts))

        return {"answer": "Sorry, that took too many steps.", "tools_used": tools_used}
