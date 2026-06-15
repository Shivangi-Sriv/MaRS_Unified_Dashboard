# MaRS Unified Dashboard

A unified campus web dashboard with an embedded AI assistant powered by **Model Context Protocol (MCP)**. Instead of one monolithic database, each campus data source runs as its own independent MCP server. The AI reads a student's natural-language question, decides which server(s) to query, calls them live, and responds with real data.

**Live website:** [https://ma-rs-unified-dashboard-seven.vercel.app](https://ma-rs-unified-dashboard-seven.vercel.app)

> The backend runs on Render's free tier and spins down after inactivity. The first request after idle may take 30–60 seconds to wake up — the sidebar cards will be empty until it responds.

---

## What it does

Ask the campus assistant anything in natural language:

| Question | Server(s) used |
|---|---|
| "Is Theory of Machines available?" | Library |
| "What's for lunch today?" | Cafeteria |
| "What events are happening this week?" | Events |
| "What is the attendance policy?" | Academics |
| "What's for lunch and what events are on?" | Cafeteria + Events (multi-server) |

The UI shows a **"routed to"** badge on each response so you can see exactly which MCP server(s) handled the query.

---

## Architecture

```
        Next.js dashboard  (chat UI + live data cards)
                    |  HTTP
                    v
         FastAPI backend  ─── main.py
                    |
         MCP host / router ── agent.py
                    |
         Gemini decides which tool(s) to call
           |           |           |           |
        Library     Events    Cafeteria   Academics
        MCP server  MCP server  MCP server  MCP server
        (stdio)     (stdio)     (stdio)     (stdio)
           |           |           |           |
       books.json  events.json  menu.json  handbook.txt
```

Each MCP server is a Python subprocess communicating over stdio. The agent opens a client session to all four servers, hands their tools to Gemini, and the SDK handles the full decide → call → feed-back → answer loop automatically.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 (App Router, TypeScript) |
| Backend | FastAPI (Python) |
| MCP servers | Python `mcp` SDK (FastMCP) |
| AI | Gemini (`google-genai`) with MCP tool-calling |
| Frontend hosting | Vercel |
| Backend hosting | Render |

---

## Local development

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Gemini API key → [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Set your Gemini key
export GEMINI_API_KEY="your_key_here"        # macOS / Linux
# $env:GEMINI_API_KEY="your_key_here"        # Windows PowerShell

uvicorn main:app --reload --port 8000
```

The backend starts all four MCP servers automatically when a question arrives — you don't run them separately. To verify it's up:

```bash
curl http://localhost:8000/menu
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The frontend points at the production Render backend by default (`API` constant in `app/page.tsx`). Change that to `http://localhost:8000` if you want to run against a local backend.

---

## Deployment

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com), connected to this repo.
2. Set **Root Directory** to `backend`.
3. Set **Build Command** to `pip install -r requirements.txt`.
4. Set **Start Command** to `uvicorn main:app --host 0.0.0.0 --port 8000`.
5. Add environment variable: `GEMINI_API_KEY` = your key.

### Frontend → Vercel

1. Import this repo on [vercel.com](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Framework will auto-detect as **Next.js**.
4. Set the **Build Command** to `next build --webpack` (required for Next.js 16 on Vercel).
5. No environment variables needed — the backend URL is set in `app/page.tsx`.
6. Deploy.

---

## How the AI routing works

`backend/agent.py` is the core. It:

1. Opens an MCP client session to each of the 4 servers.
2. Collects all available tools from every server.
3. Passes them all to Gemini in a single call.
4. Gemini decides which tool(s) to call based on the question.
5. The SDK executes the tool calls and feeds results back automatically.
6. Returns the final answer + the list of tools used (so the UI can show the routing badges).

---

## Adding a new data source

1. Drop a data file in `backend/data/`.
2. Copy any file in `backend/servers/` and expose tools with `@mcp.tool()`.
3. Add the new server script path to the `SERVERS` list in `backend/agent.py`.
4. Add its tool names to `TOOL_TO_SERVER` in `frontend/app/page.tsx` for the routing badge.

The AI discovers new tools automatically — no other changes needed.

---

## Project structure

```
MaRS_Unified_Dashboard/
├── backend/
│   ├── main.py              # FastAPI app (HTTP endpoints)
│   ├── agent.py             # MCP host + Gemini routing
│   ├── requirements.txt
│   ├── data/
│   │   ├── books.json
│   │   ├── events.json
│   │   ├── menu.json
│   │   └── handbook.txt
│   └── servers/
│       ├── library_server.py
│       ├── events_server.py
│       ├── menu_server.py
│       └── handbook_server.py
└── frontend/
    ├── app/
    │   ├── page.tsx         # Main dashboard UI
    │   ├── layout.tsx
    │   └── globals.css
    ├── next.config.ts
    └── package.json
```