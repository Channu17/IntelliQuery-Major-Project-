import ChatQueryRunner from "../common/ChatQueryRunner";

export default function SqlQueryPanel({ datasourceId }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. Show top 10 customers by total spend"
    />
  );
}
