import ChatQueryRunner from "../common/ChatQueryRunner";

export default function SqlQueryPanel({ datasourceId, sessionId, onSessionChange, initialMessages }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. Show top 10 customers by total spend"
      sessionId={sessionId}
      onSessionChange={onSessionChange}
      initialMessages={initialMessages}
    />
  );
}
