import ChatQueryRunner from "../common/ChatQueryRunner";

export default function SpreadsheetQueryPanel({ datasourceId, sessionId, onSessionChange, initialMessages }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. What are the top 5 products by revenue?"
      sessionId={sessionId}
      onSessionChange={onSessionChange}
      initialMessages={initialMessages}
    />
  );
}
