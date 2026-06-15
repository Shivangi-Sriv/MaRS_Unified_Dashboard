# Campus Intelligence Dashboard

A unified campus web dashboard with an embedded AI assistant. Instead of one
giant scraped database, each campus data source runs as its **own independent
MCP (Model Context Protocol) server**. The AI reads a student's natural-language
question, decides which server(s) to query, calls them live over MCP, and
answers from the real results.

## Why this design

The library, cafeteria, events, and academic handbook each live behind their
own MCP server. They share nothing. The backend acts as the **MCP host**: it
connects to all four servers and hands their tools to the language model, which
routes each question to whichever server(s) it needs. There is no central
database — every answer is assembled live.

## Architecture

```
                 Next.js dashboard (chat + live cards)
                              |  HTTP
                              v
                 FastAPI backend  (main.py)
                              |
                 MCP host / router (agent.py)
                              |
          Gemini decides which tool(s) to call
            |            |            |            |
       Library      Events      Cafeteria    Academics    <- 4 independent
       MCP server   MCP server  MCP server   MCP server      MCP servers
       (stdio)      (stdio)     (stdio)      (stdio)
            |            |            |            |
        books.json  events.json  menu.json   handbook.txt
```

Each server is launched as a subprocess and speaks MCP over stdio. The model's
tool calls are executed over the protocol and the results are fed back to it
automatically by the Gemini SDK's MCP integration.

## Tech stack

| Layer        | Technology                                  |
|--------------|---------------------------------------------|
| Frontend     | Next.js (App Router, TypeScript)            |
| Backend/Host | FastAPI (Python)                            |
| MCP servers  | Python `mcp` SDK (FastMCP)                  |
| AI           | Gemini (`google-genai`) with MCP tool-calling |

## Features

- Four independent MCP servers (library, events, cafeteria, academics).
- AI assistant that routes natural-language queries to the right server(s).
- Multi-server queries in one question (e.g. menu + events together).
- Retrieval over the student handbook for policy questions.
- "Routed to" badges in the UI that show which server handled each answer.
- Live dashboard cards fed directly from each data source.

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free Gemini API key: https://aistudio.google.com/apikey

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# set your key (mac/linux):
export GEMINI_API_KEY="your_key_here"
# windows powershell:
# $env:GEMINI_API_KEY="your_key_here"

uvicorn main:app --reload --port 8000
```

The backend starts the MCP servers automatically when a question comes in —
you do **not** run them by hand. To sanity-check the API:
`curl http://localhost:8000/menu`

### 2. Frontend

```bash
cd frontend
npx create-next-app@latest .    # TypeScript: Yes, App Router: Yes
# then overwrite app/page.tsx, app/layout.tsx, app/globals.css with the
# files from this repo (already included here).
npm run dev
```

Open http://localhost:3000.

## How it works (the important file)

`backend/agent.py` is the host. It opens an MCP client session to every server,
passes those sessions to Gemini as `tools`, and the SDK handles the
decide → call → feed-back → answer loop. It also reports which tools were
called so the UI can show the routing.

## Adding a new campus data source

1. Drop a data file in `backend/data/`.
2. Copy one of the files in `backend/servers/` and expose its tools with
   `@mcp.tool()`.
3. Add the filename to the `SERVERS` list in `backend/agent.py`.

That's it — the AI discovers the new tools automatically.

## Demo script (for the video)

1. "Is Theory of Machines available?" → Library
2. "What's for lunch today?" → Cafeteria
3. "What events are happening this week?" → Events
4. "What is the attendance policy?" → Academics (handbook retrieval)
5. "What's for lunch and what events are on?" → routes to **two** servers at once

Step 5 is the money shot: one question, multiple independent MCP servers,
answered live.
