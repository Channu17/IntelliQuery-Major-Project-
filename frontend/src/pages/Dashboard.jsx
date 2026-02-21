import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Button from "../components/Button";
import { datasourceAPI, formatApiError } from "../utils/api";

const typeRouteMap = {
  mysql: "sql",
  psql: "sql",
  mongo: "mongo",
  pandas: "spreadsheet",
};

const typeLabelMap = {
  mysql: "MySQL",
  psql: "PostgreSQL",
  mongo: "MongoDB",
  pandas: "Spreadsheet",
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [savedDatasources, setSavedDatasources] = useState([]);
  const [loadingDs, setLoadingDs] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem("user");
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      navigate("/login");
    }
  }, [navigate]);

  // Fetch saved datasources
  useEffect(() => {
    const fetchDatasources = async () => {
      try {
        const res = await datasourceAPI.getAll();
        setSavedDatasources(res.data ?? []);
      } catch {
        // ignore - user may not be logged in yet
      } finally {
        setLoadingDs(false);
      }
    };
    if (user) fetchDatasources();
  }, [user]);

  const quickActions = [
    {
      title: "SQL Query",
      description: "Query your SQL databases",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
          />
        </svg>
      ),
      color: "from-yellow-600 to-yellow-500",
      routeType: "sql",
    },
    {
      title: "MongoDB Query",
      description: "Access NoSQL databases",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
      ),
      color: "from-yellow-500 to-yellow-400",
      routeType: "mongo",
    },
    {
      title: "Spreadsheet Analysis",
      description: "Analyze CSV/Excel files",
      icon: (
        <svg
          className="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      ),
      color: "from-yellow-400 to-yellow-600",
      routeType: "spreadsheet",
    },
  ];

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black pt-24 pb-12 px-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-96 h-96 bg-yellow-600/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-yellow-600/5 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back,{" "}
            <span className="bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
              {user.username ?? user.email}
            </span>
            !
          </h1>
          <p className="text-gray-400">Ready to query your data?</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">Total Queries</p>
                <p className="text-3xl font-bold text-yellow-400">
                  --
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-600 to-yellow-500 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-black"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">Data Sources</p>
                <p className="text-3xl font-bold text-yellow-400">
                  {savedDatasources.length}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-400 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-black"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                  />
                </svg>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">Last Active</p>
                <p className="text-3xl font-bold text-yellow-400">
                  {new Date().toLocaleDateString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-linear-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-black"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickActions.map((action, index) => (
              <Card
                key={index}
                hover
                onClick={() =>
                  navigate(`/datasource/${action.routeType}/setup`)
                }
              >
                <div
                  className={`w-14 h-14 bg-gradient-to-br ${action.color} rounded-lg flex items-center justify-center mb-4 text-black`}
                >
                  {action.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {action.title}
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  {action.description}
                </p>
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/datasource/${action.routeType}/setup`);
                  }}
                >
                  Start Query
                </Button>
              </Card>
            ))}
          </div>
        </div>

        {/* Saved Connections */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">
            Saved Connections
          </h2>
          <Card>
            <div className="space-y-4">
              {!loadingDs && savedDatasources.length > 0 ? (
                savedDatasources.map((ds) => {
                  const routeType = typeRouteMap[ds.type] || "sql";
                  const label = typeLabelMap[ds.type] || ds.type;
                  const name = ds.details?.database || ds.details?.filename || ds.type;
                  return (
                    <div
                      key={ds.id}
                      className="flex items-start justify-between border-b border-gray-800 pb-4 last:border-0 last:pb-0"
                    >
                      <div className="flex-1">
                        <p className="text-white font-medium mb-1">
                          {name}
                        </p>
                        <div className="flex items-center space-x-4 text-sm text-gray-400">
                          <span className="flex items-center">
                            <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>
                            {label}
                          </span>
                          {ds.details?.host && <span>{ds.details.host}</span>}
                          {ds.details?.collection && <span>{ds.details.collection}</span>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="ghost"
                          onClick={() =>
                            navigate(`/datasource/${routeType}/query`, {
                              state: { datasourceId: ds.id },
                            })
                          }
                        >
                          Query
                        </Button>
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              await datasourceAPI.delete(ds.id);
                              setSavedDatasources((prev) =>
                                prev.filter((d) => d.id !== ds.id)
                              );
                            } catch (err) {
                              console.error("Failed to delete datasource", err);
                            }
                          }}
                          className="text-gray-500 hover:text-red-400 transition-colors p-1"
                          title="Delete connection"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                            <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.519.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8">
                  <svg
                    className="w-16 h-16 text-gray-700 mx-auto mb-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                    />
                  </svg>
                  <p className="text-gray-400">No saved connections</p>
                  <p className="text-gray-500 text-sm mt-2">
                    Connect a datasource to see it here
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
