import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { useState, useEffect } from "react";
import "./index.css";

// Components
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

// Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import DataSourceSetup from "./pages/DataSourceSetup";
import QueryPage from "./pages/QueryPage";
import NotFound from "./pages/NotFound";

function AppContent({ isAuthenticated, handleLogin, handleLogout, loading }) {
  const location = useLocation();
  const hideFooter =
    location.pathname.includes("/datasource/") &&
    location.pathname.includes("/query");
  const hideNavbar =
    location.pathname.includes("/datasource/") &&
    location.pathname.includes("/query");

  // Protected Route wrapper
  const ProtectedRoute = ({ children }) => {
    if (loading) {
      return (
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow-500"></div>
        </div>
      );
    }
    return isAuthenticated ? children : <Navigate to="/login" />;
  };

  return (
    <div className="flex flex-col min-h-screen bg-black">
      {!hideNavbar && (
        <Navbar isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      )}
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/datasource/:type/setup"
            element={
              <ProtectedRoute>
                <DataSourceSetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/datasource/:type/query"
            element={
              <ProtectedRoute>
                <QueryPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      {!hideFooter && <Footer />}
    </div>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const user = localStorage.getItem("user");
    if (user) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-yellow-500"></div>
      </div>
    );
  }

  return (
    <Router>
      <AppContent
        isAuthenticated={isAuthenticated}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
        loading={loading}
      />
    </Router>
  );
}

export default App;
