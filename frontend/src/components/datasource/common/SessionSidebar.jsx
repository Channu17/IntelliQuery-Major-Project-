import { useState, useEffect, useCallback } from "react";
import { aiAPI } from "../../../utils/api";

/**
 * Collapsible sidebar showing past chat sessions for a datasource.
 *
 * Props:
 *  - datasourceId   – filter sessions for this datasource
 *  - activeSessionId – currently active session (highlighted)
 *  - onSelectSession(sessionId) – called when user clicks a session
 *  - onNewChat()     – called to start a fresh chat
 */
export default function SessionSidebar({
  datasourceId,
  activeSessionId,
  onSelectSession,
  onNewChat,
}) {
  const [sessions, setSessions] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchSessions = useCallback(async () => {
    if (!datasourceId) return;
    try {
      setLoading(true);
      const res = await aiAPI.getHistory(datasourceId);
      setSessions(res.data ?? []);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    } finally {
      setLoading(false);
    }
  }, [datasourceId]);

  // Refresh sessions when sidebar opens or datasource changes
  useEffect(() => {
    if (open) fetchSessions();
  }, [open, datasourceId, fetchSessions]);

  // Also refresh when activeSessionId changes (new session created)
  useEffect(() => {
    if (open && activeSessionId) fetchSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSessionId]);

  const handleDeleteSession = async (e, sessionId) => {
    e.stopPropagation();
    if (!window.confirm("Delete this chat session?")) return;
    try {
      await aiAPI.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      // If the deleted session was the active one, start a new chat
      if (sessionId === activeSessionId) {
        onNewChat?.();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return "";
    const d = new Date(isoString);
    const now = new Date();
    const diffMs = now - d;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) return `${diffH}h ago`;
    const diffD = Math.floor(diffH / 24);
    if (diffD < 7) return `${diffD}d ago`;
    return d.toLocaleDateString();
  };

  return (
    <>
      {/* Toggle button — always visible */}
      <button
        onClick={() => setOpen((v) => !v)}
        title={open ? "Close history" : "Chat history"}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-40 bg-gray-900 hover:bg-gray-800 border border-gray-700 border-l-0 rounded-r-lg px-1.5 py-3 text-gray-400 hover:text-yellow-500 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className={`w-5 h-5 transition-transform ${open ? "rotate-180" : ""}`}
        >
          <path
            fillRule="evenodd"
            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* Sidebar panel */}
      <div
        className={`fixed left-0 top-0 h-full z-30 bg-gray-950 border-r border-gray-800 transition-transform duration-200 ease-in-out flex flex-col ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        style={{ width: "280px" }}
      >
        {/* Sidebar header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
            History
          </h2>
          <button
            onClick={() => {
              onNewChat?.();
              fetchSessions();
            }}
            title="New chat"
            className="flex items-center gap-1.5 text-xs bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1.5 rounded-full transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="w-3.5 h-3.5"
            >
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Session list */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
          {loading && sessions.length === 0 ? (
            <p className="text-xs text-gray-500 text-center py-6">Loading...</p>
          ) : sessions.length === 0 ? (
            <p className="text-xs text-gray-500 text-center py-6">
              No past sessions yet.
            </p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.session_id}
                onClick={() => onSelectSession?.(s.session_id)}
                className={`w-full text-left rounded-lg px-3 py-2.5 group transition-colors ${
                  s.session_id === activeSessionId
                    ? "bg-yellow-600/20 border border-yellow-600/40"
                    : "hover:bg-gray-800 border border-transparent"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm text-gray-200 truncate flex-1 leading-snug">
                    {s.title}
                  </p>
                  <button
                    onClick={(e) => handleDeleteSession(e, s.session_id)}
                    title="Delete session"
                    className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-opacity flex-shrink-0 mt-0.5"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 16 16"
                      fill="currentColor"
                      className="w-3.5 h-3.5"
                    >
                      <path
                        fillRule="evenodd"
                        d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] text-gray-500">
                    {s.message_count} {s.message_count === 1 ? "query" : "queries"}
                  </span>
                  <span className="text-[10px] text-gray-600">·</span>
                  <span className="text-[10px] text-gray-500">
                    {formatDate(s.last_queried_at)}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </>
  );
}
