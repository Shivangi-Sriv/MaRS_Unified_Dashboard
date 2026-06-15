"use client";

import { useEffect, useRef, useState } from "react";

const API = "http://localhost:8000";

// Maps a raw MCP tool name to the human-facing server it belongs to.
const TOOL_TO_SERVER: Record<string, string> = {
  search_book: "Library",
  list_books: "Library",
  get_events: "Events",
  find_events_by_club: "Events",
  get_todays_menu: "Cafeteria",
  get_menu_for_day: "Cafeteria",
  search_handbook: "Academics",
};

type Msg = { role: "user" | "assistant"; text: string; servers?: string[] };

export default function Home() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      text:
        "Hi! I'm your Campus Assistant. Ask me about the library, today's menu, " +
        "upcoming events, or academic policies and I'll fetch it live.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const [events, setEvents] = useState<any[]>([]);
  const [menu, setMenu] = useState<any>(null);
  const [books, setBooks] = useState<any[]>([]);

  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API}/events`).then((r) => r.json()).then(setEvents).catch(() => {});
    fetch(`${API}/menu`).then((r) => r.json()).then(setMenu).catch(() => {});
    fetch(`${API}/books`).then((r) => r.json()).then(setBooks).catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setBusy(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      const servers = Array.from(
        new Set((data.tools_used || []).map((t: string) => TOOL_TO_SERVER[t] || t))
      ) as string[];
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.answer || "(no answer)", servers },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "Couldn't reach the backend. Is it running on port 8000?",
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  const samples = [
    "Is Theory of Machines available?",
    "What's for lunch today?",
    "What events are happening this week?",
    "What is the attendance policy?",
    "What's for lunch and what events are on?",
  ];

  return (
    <main className="page">
      <header className="bar">
        <div className="brand">
          <span className="dot" />
          Campus Intelligence
        </div>
        <div className="status">4 MCP servers connected</div>
      </header>

      <div className="grid">
        {/* Chat — the hero */}
        <section className="chat card">
          <div className="thread">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div className="bubble">{m.text}</div>
                {m.servers && m.servers.length > 0 && (
                  <div className="route">
                    routed to
                    {m.servers.map((s) => (
                      <span key={s} className="pill">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <div className="msg assistant">
                <div className="bubble thinking">routing your question…</div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          <div className="samples">
            {samples.map((s) => (
              <button key={s} className="chip" onClick={() => setInput(s)}>
                {s}
              </button>
            ))}
          </div>

          <div className="composer">
            <input
              value={input}
              placeholder="Ask about the library, menu, events, or policies…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button onClick={send} disabled={busy}>Send</button>
          </div>
        </section>

        {/* Live data cards */}
        <aside className="rail">
          <div className="card">
            <h3>Today&apos;s Menu</h3>
            {menu ? (
              <>
                <p className="line"><span>Breakfast</span>{menu.breakfast}</p>
                <p className="line"><span>Lunch</span>{menu.lunch}</p>
                <p className="line"><span>Dinner</span>{menu.dinner}</p>
              </>
            ) : (
              <p className="empty">Start the backend to load the menu.</p>
            )}
          </div>

          <div className="card">
            <h3>Upcoming Events</h3>
            {events.length ? (
              events
              .sort(() => Math.random() - 0.5)
              .slice(0, 5)
              .map((e) => (
                <p className="line" key={e.name}>
                  <span>{e.date.slice(5)}</span>
                  {e.name}
                </p>
              ))
            ) : (
              <p className="empty">No events loaded.</p>
            )}
          </div>

          <div className="card">
            <h3>Library</h3>
            {books.length ? (
              books
                .sort(() => Math.random() - 0.5)
                .slice(0, 5)
                .map((b) => (
                  <p className="line" key={b.title}>
                    <span className={b.available ? "ok" : "no"}>
                      {b.available ? "in" : "out"}
                    </span>
                    {b.title}
                  </p>
                ))
            ) : (
              <p className="empty">No catalog loaded.</p>
            )}
          </div>
        </aside>
      </div>
    </main>
  );
}

