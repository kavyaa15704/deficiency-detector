import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginUser, apiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const justRegistered = location.state?.justRegistered;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await loginUser(username, password);
      login(data.access_token, username);
      navigate("/predict");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm px-6 py-16">
      <h1 className="text-3xl">Log in</h1>
      {justRegistered && (
        <p className="mt-2 text-sm text-teal">Account created — log in to continue.</p>
      )}
      <p className="mt-2 text-sm text-ink/60">
        New here? <Link to="/register" className="text-teal underline">Register</Link>
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <label className="block">
          <span className="text-sm font-medium">Username</span>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="mt-1.5 w-full rounded border border-line bg-white px-3 py-2 focus:border-amber outline-none"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1.5 w-full rounded border border-line bg-white px-3 py-2 focus:border-amber outline-none"
          />
        </label>

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-ink py-3 font-medium text-paper hover:bg-teal transition-colors disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>
    </div>
  );
}
