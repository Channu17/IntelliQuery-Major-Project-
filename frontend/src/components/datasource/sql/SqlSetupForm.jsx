import { useEffect, useMemo, useState } from "react";
import Input from "../../Input";
import Button from "../../Button";
import { datasourceAPI, formatApiError } from "../../../utils/api";
import { saveDatasourceId } from "../common/storage";

const DEFAULTS = {
  mysql: { port: 3306 },
  psql: { port: 5432 },
};

export default function SqlSetupForm({ disabled, onConnected, onConnecting }) {
  const [formData, setFormData] = useState({
    type: "mysql",
    host: "localhost",
    port: DEFAULTS.mysql.port,
    username: "",
    password: "",
    database: "",
  });
  const [apiError, setApiError] = useState("");
  const [savedConnections, setSavedConnections] = useState([]);
  const [loadingSaved, setLoadingSaved] = useState(true);

  // Load saved connections on mount
  useEffect(() => {
    const fetchSaved = async () => {
      try {
        const res = await datasourceAPI.getAll();
        const sqlConns = (res.data ?? []).filter(
          (d) => d.type === "mysql" || d.type === "psql"
        );
        setSavedConnections(sqlConns);
      } catch {
        // ignore
      } finally {
        setLoadingSaved(false);
      }
    };
    fetchSaved();
  }, []);

  const handleUseSaved = (conn) => {
    saveDatasourceId("sql", conn.id);
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

  const portHint = useMemo(() => {
    const p = DEFAULTS[formData.type]?.port;
    return p ? `Default: ${p}` : "";
  }, [formData.type]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "port" ? Number(value) : value,
    }));
  };

  const connect = async (e) => {
    e.preventDefault();
    setApiError("");
    onConnecting?.(true);

    try {
      const res = await datasourceAPI.connectSql({
        type: formData.type,
        host: formData.host,
        port: Number(formData.port),
        username: formData.username,
        password: formData.password,
        database: formData.database,
      });

      let datasourceId = res.data?.datasource_id;
      if (!datasourceId) {
        const list = await datasourceAPI.getAll();
        const match = (list.data ?? []).find(
          (d) =>
            (d.type === formData.type || d.type === "sql") &&
            d.details?.host === formData.host &&
            d.details?.database === formData.database,
        );
        datasourceId = match?.id;
      }

      if (!datasourceId) {
        throw new Error(
          "Connected, but could not determine datasource id. Please try again.",
        );
      }

      saveDatasourceId("sql", datasourceId);
      onConnected?.(datasourceId);
    } catch (err) {
      const msg =
        formatApiError(err.response?.data) ||
        err.message ||
        "Failed to connect to SQL database.";
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
                      ({conn.type === "psql" ? "PostgreSQL" : "MySQL"})
                    </span>
                  </p>
                  <p className="text-gray-400 text-sm truncate">
                    {conn.details?.host}:{conn.details?.port}
                  </p>
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

        <div>
          <label className="block text-gray-300 font-medium mb-2">
            SQL Type <span className="text-yellow-400">*</span>
          </label>
          <select
            name="type"
            value={formData.type}
            onChange={(e) => {
              const nextType = e.target.value;
              setFormData((prev) => ({
                ...prev,
                type: nextType,
                port: DEFAULTS[nextType]?.port ?? prev.port,
              }));
            }}
            disabled={disabled}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            <option value="mysql">MySQL</option>
            <option value="psql">PostgreSQL</option>
          </select>
        </div>

        <Input
          label="Host"
          name="host"
          value={formData.host}
          onChange={handleChange}
          placeholder="localhost"
          disabled={disabled}
          required
        />

        <Input
          label={`Port ${portHint ? `(${portHint})` : ""}`}
          name="port"
          type="number"
          value={formData.port}
          onChange={handleChange}
          placeholder={String(DEFAULTS[formData.type]?.port ?? 0)}
          disabled={disabled}
          required
        />

        <Input
          label="Username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="db user"
          disabled={disabled}
          required
        />

        <Input
          label="Password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="db password"
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

        <Button type="submit" disabled={disabled}>
          {disabled ? "Connecting..." : "Connect & Save"}
        </Button>
      </form>
    </div>
  );
}
