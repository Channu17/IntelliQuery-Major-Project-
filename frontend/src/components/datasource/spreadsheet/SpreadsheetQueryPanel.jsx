import ChatQueryRunner from "../common/ChatQueryRunner";

export default function SpreadsheetQueryPanel({ datasourceId }) {
  return (
    <ChatQueryRunner
      datasourceId={datasourceId}
      placeholder="e.g. What are the top 5 products by revenue?"
    />
  );
}
