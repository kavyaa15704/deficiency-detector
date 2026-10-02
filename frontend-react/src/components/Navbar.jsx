import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { isAuthenticated, username, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="border-b border-line">
      <nav className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
        <Link to="/" className="font-display text-lg tracking-tight">
          Deficiency Detector
        </Link>
        <div className="flex items-center gap-6 text-sm">
          {isAuthenticated ? (
            <>
              <Link to="/predict" className="hover:text-amber">Check symptoms</Link>
              <span className="text-ink/60">{username}</span>
              <button onClick={handleLogout} className="text-teal hover:text-ink">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-amber">Log in</Link>
              <Link
                to="/register"
                className="rounded border border-ink px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
