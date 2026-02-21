import ChatQueryRunner from "../common/ChatQueryRunner";

export default function MongoQueryPanel({ datasourceId, sessionId, onSessionChange, initialMessages }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. Find orders from last month"
      sessionId={sessionId}
      onSessionChange={onSessionChange}
      initialMessages={initialMessages}
    />
  );
}
