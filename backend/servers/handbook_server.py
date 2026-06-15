"""
Handbook MCP Server (retrieval / RAG-lite).
Independent MCP server that searches the student handbook and returns the
most relevant passages for a natural-language question. This is the
"academics" data source: the AI calls search_handbook(query) and gets back
grounded text to answer from.

Retrieval here is keyword-overlap scoring over paragraph chunks. It is real
retrieval and demos reliably. To upgrade to embeddings (vector RAG), replace
the score() function with cosine similarity over embedding vectors -- see the
note at the bottom of this file.

Run standalone with: python servers/handbook_server.py
"""
import re
from pathlib import Path
from mcp.server.fastmcp import FastMCP

TEXT = (Path(__file__).parent.parent / "data" / "handbook.txt").read_text()
# Split the handbook into paragraph-sized chunks.
CHUNKS = [c.strip() for c in re.split(r"\n\s*\n", TEXT) if c.strip()]

mcp = FastMCP("handbook")


def _tokens(s: str) -> set:
    return set(re.findall(r"[a-z]+", s.lower()))


@mcp.tool()
def search_handbook(query: str) -> str:
    """Search the student handbook for policies (attendance, exams, grading,
    fees, hostel, library, leave, grievances) and return the most relevant
    passages to answer the question."""
    q = _tokens(query)
    scored = []
    for chunk in CHUNKS:
        score = len(q & _tokens(chunk))
        if score:
            scored.append((score, chunk))
    scored.sort(reverse=True, key=lambda x: x[0])
    top = [c for _, c in scored[:2]]
    if not top:
        return "No relevant section found in the student handbook."
    return "\n\n---\n\n".join(top)


if __name__ == "__main__":
    mcp.run()

# ---------------------------------------------------------------------------
# OPTIONAL upgrade to true vector RAG (only if you have spare time):
#   pip install google-genai numpy
#   1. At startup, embed every chunk once:
#        client.models.embed_content(model="text-embedding-004", contents=CHUNKS)
#   2. In search_handbook, embed the query the same way.
#   3. Rank chunks by cosine similarity instead of keyword overlap.
# The tool signature stays identical, so nothing else in the project changes.
# ---------------------------------------------------------------------------
