import { createContext, useContext, useEffect, useState } from "react";
import { setAuthToken } from "../api/client";

const AuthContext = createContext(null);
const STORAGE_KEY = "deficiency_detector_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY));
  const [username, setUsername] = useState(() => localStorage.getItem(STORAGE_KEY + "_user"));

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  function login(newToken, newUsername) {
    localStorage.setItem(STORAGE_KEY, newToken);
    localStorage.setItem(STORAGE_KEY + "_user", newUsername);
    setToken(newToken);
    setUsername(newUsername);
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_KEY + "_user");
    setToken(null);
    setUsername(null);
  }

  return (
    <AuthContext.Provider value={{ token, username, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
