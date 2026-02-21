import { useMemo, useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import Card from "../components/Card";
import Button from "../components/Button";

import SqlQueryPanel from "../components/datasource/sql/SqlQueryPanel";
import MongoQueryPanel from "../components/datasource/mongo/MongoQueryPanel";
import SpreadsheetQueryPanel from "../components/datasource/spreadsheet/SpreadsheetQueryPanel";
import SessionSidebar from "../components/datasource/common/SessionSidebar";
import { loadDatasourceId } from "../components/datasource/common/storage";
import { datasourceAPI, aiAPI } from "../utils/api";

const typeTitle = {
  sql: "SQL",
  mongo: "MongoDB",
  spreadsheet: "Spreadsheet",
};

export default function QueryPage() {
  const navigate = useNavigate();
  const { type } = useParams();
  const location = useLocation();
  const [datasourceName, setDatasourceName] = useState("");

  // Session management state
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [initialMessages, setInitialMessages] = useState(null);

  const datasourceIdFromState = location.state?.datasourceId;
  const datasourceIdFromStorage = loadDatasourceId(type);
  const datasourceId = datasourceIdFromState ?? datasourceIdFromStorage;

  // Load a past session's messages and convert to ChatQueryRunner format
  const handleSelectSession = useCallback(async (sessionId) => {
    try {
      const res = await aiAPI.getSession(sessionId);
      const msgs = [];
      (res.data ?? []).forEach((entry, idx) => {
        // User message
        msgs.push({
          id: idx * 2,
          type: "user",
          content: entry.natural_query,
          timestamp: new Date(entry.created_at),
        });
        // AI response
        msgs.push({
          id: idx * 2 + 1,
          type: "ai",
          content: entry.natural_query,
          response: {
            success: entry.success,
            generated_query: entry.generated_query,
            datasource_type: entry.datasource_type,
            row_count: entry.row_count,
            llm_used: entry.llm_used,
            error: entry.error,
            // Results are not stored in history — only metadata
            results: null,
          },
          timestamp: new Date(entry.created_at),
        });
      });
      setInitialMessages(msgs);
      setActiveSessionId(sessionId);
    } catch (err) {
      console.error("Failed to load session:", err);
    }
  }, []);

  // Start a fresh chat (clear session)
  const handleNewChat = useCallback(() => {
    setActiveSessionId(null);
    setInitialMessages([]);
  }, []);

  // When backend returns a session_id after first query
  const handleSessionChange = useCallback((newSessionId) => {
    setActiveSessionId(newSessionId);
  }, []);

  // Fetch datasource details to get the name
  useEffect(() => {
    const fetchDatasourceName = async () => {
      if (!datasourceId) {
        setDatasourceName("");
        return;
      }

      try {
        const res = await datasourceAPI.getAll();
        const datasources = res.data; // API returns array directly
        const datasource = datasources?.find((ds) => ds.id === datasourceId);
        if (datasource) {
          // Extract database name based on type
          if (type === "sql") {
            setDatasourceName(datasource.details?.database || datasourceId);
          } else if (type === "mongo") {
            setDatasourceName(datasource.details?.database || datasourceId);
          } else if (type === "spreadsheet") {
            setDatasourceName(datasource.details?.filename || datasourceId);
          } else {
            setDatasourceName(datasourceId);
          }
        } else {
          setDatasourceName(datasourceId);
        }
      } catch (err) {
        console.error("Failed to fetch datasource name:", err);
        setDatasourceName(datasourceId);
      }
    };

    fetchDatasourceName();
  }, [datasourceId, type]);

  const Panel = useMemo(() => {
    if (type === "sql") return SqlQueryPanel;
    if (type === "mongo") return MongoQueryPanel;
    if (type === "spreadsheet") return SpreadsheetQueryPanel;
    return null;
  }, [type]);

  if (!Panel) {
    return (
      <div className="min-h-screen bg-black pt-24 pb-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card>
            <h1 className="text-2xl font-bold text-white mb-2">
              Unsupported datasource
            </h1>
            <Button onClick={() => navigate("/dashboard")}>Back</Button>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-black flex flex-col overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-yellow-600/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-yellow-600/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <div className="relative z-10 border-b border-gray-800 bg-black/90 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    fillRule="evenodd"
                    d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z"
                    clipRule="evenodd"
                  />
                </svg>
                Back
              </Button>
              <div className="border-l border-gray-700 h-8"></div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold text-white">
                    {typeTitle[type] ?? "Database"}
                  </h1>
                  <span className="text-gray-500">•</span>
                  <p className="text-sm text-gray-400">
                    <span className="text-gray-500">DB Name:</span>{" "}
                    {datasourceName || "None"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 relative z-10 overflow-hidden">
        <div className="max-w-6xl mx-auto h-full">
          {!datasourceId ? (
            <div className="flex items-center justify-center h-full px-4">
              <Card>
                <div>
                  <p className="text-red-400 mb-4">
                    No datasource selected. Please connect first.
                  </p>
                  <Button onClick={() => navigate(`/datasource/${type}/setup`)}>
                    Go to Setup
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            <Panel
              datasourceId={datasourceId}
              sessionId={activeSessionId}
              onSessionChange={handleSessionChange}
              initialMessages={initialMessages}
            />
          )}
        </div>
      </div>

      {/* Session Sidebar */}
      {datasourceId && (
        <SessionSidebar
          datasourceId={datasourceId}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
        />
      )}
    </div>
  );
}
