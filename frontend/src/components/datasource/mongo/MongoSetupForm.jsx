import { useEffect, useState } from "react";
import Input from "../../Input";
import Button from "../../Button";
import { datasourceAPI, formatApiError } from "../../../utils/api";
import { saveDatasourceId } from "../common/storage";

export default function MongoSetupForm({
  disabled,
  onConnected,
  onConnecting,
}) {
  const [formData, setFormData] = useState({
    uri: "mongodb://localhost:27017",
    database: "",
    collection: "",
  });
  const [apiError, setApiError] = useState("");
  const [savedConnections, setSavedConnections] = useState([]);
  const [loadingSaved, setLoadingSaved] = useState(true);

  // Load saved connections on mount
  useEffect(() => {
    const fetchSaved = async () => {
      try {
        const res = await datasourceAPI.getAll();
        const mongoConns = (res.data ?? []).filter((d) => d.type === "mongo");
        setSavedConnections(mongoConns);
      } catch {
        // ignore
      } finally {
        setLoadingSaved(false);
      }
    };
    fetchSaved();
  }, []);

  const handleUseSaved = (conn) => {
    saveDatasourceId("mongo", conn.id);
    onConnected?.(conn.id);
  };

  const handleDeleteSaved = async (conn) => {
    try {
      await datasourceAPI.delete(conn.id);
      setSavedConnections((prev) => prev.filter((c) => c.id !== conn.id));
    } catch (err) {
      setApiError(formatApiError(err.response?.data) || "Failed to delete connection.");
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const connect = async (e) => {
    e.preventDefault();
    setApiError("");
    onConnecting?.(true);

    try {
      const res = await datasourceAPI.connectMongo({
        uri: formData.uri,
        database: formData.database,
        collection: formData.collection,
      });

      let datasourceId = res.data?.datasource_id;
      if (!datasourceId) {
        const list = await datasourceAPI.getAll();
        const match = (list.data ?? []).find(
          (d) =>
            d.type === "mongo" && d.details?.database === formData.database,
        );
        datasourceId = match?.id;
      }

      if (!datasourceId) {
        throw new Error(
          "Connected, but could not determine datasource id. Please try again.",
        );
      }

      saveDatasourceId("mongo", datasourceId);
      onConnected?.(datasourceId);
    } catch (err) {
      const msg =
        formatApiError(err.response?.data) ||
        err.message ||
        "Failed to connect to MongoDB.";
      setApiError(msg);
    } finally {
      onConnecting?.(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Saved Connections */}
      {!loadingSaved && savedConnections.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Previous Connections</h3>
          <div className="space-y-2">
            {savedConnections.map((conn) => (
              <div
                key={conn.id}
                className="flex items-center justify-between bg-gray-900 border border-gray-700 rounded-lg px-4 py-3"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">
                    {conn.details?.database}
                    <span className="text-gray-500 text-sm ml-2">
                      ({conn.details?.collection})
                    </span>
                  </p>
                  <p className="text-gray-400 text-sm truncate">MongoDB</p>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Button
                    variant="ghost"
                    onClick={() => handleUseSaved(conn)}
                    disabled={disabled}
                    className="text-yellow-400 hover:text-yellow-300"
                  >
                    Use
                  </Button>
                  <button
                    type="button"
                    onClick={() => handleDeleteSaved(conn)}
                    className="text-gray-500 hover:text-red-400 transition-colors p-1"
                    title="Remove saved connection"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                      <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.519.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="border-b border-gray-800 my-4"></div>
          <p className="text-gray-500 text-sm mb-2">Or create a new connection</p>
        </div>
      )}

      {/* New Connection Form */}
      <form onSubmit={connect} className="space-y-4">
        {apiError && (
          <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
            {apiError}
          </div>
        )}

        <Input
          label="MongoDB URI"
          name="uri"
          value={formData.uri}
          onChange={handleChange}
          placeholder="mongodb://user:pass@host:27017"
          disabled={disabled}
          required
        />

        <Input
          label="Database"
          name="database"
          value={formData.database}
          onChange={handleChange}
          placeholder="database name"
          disabled={disabled}
          required
        />

        <Input
          label="Collection"
          name="collection"
          value={formData.collection}
          onChange={handleChange}
          placeholder="collection name (e.g., sales_transactions)"
          disabled={disabled}
          required
        />

        <Button type="submit" disabled={disabled}>
          {disabled ? "Connecting..." : "Connect & Save"}
        </Button>
      </form>
    </div>
  );
}
