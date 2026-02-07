import ChatQueryRunner from "../common/ChatQueryRunner";

export default function MongoQueryPanel({ datasourceId }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. Find orders from last month"
    />
  );
}
