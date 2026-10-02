import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser, apiErrorMessage } from "../api/client";

export default function Register() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await registerUser(form.username, form.email, form.password);
      navigate("/login", { state: { justRegistered: true } });
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm px-6 py-16">
      <h1 className="text-3xl">Create an account</h1>
      <p className="mt-2 text-sm text-ink/60">
        Already registered? <Link to="/login" className="text-teal underline">Log in</Link>
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <Field label="Username" value={form.username} onChange={update("username")} required minLength={3} />
        <Field label="Email" type="email" value={form.email} onChange={update("email")} required />
        <Field
          label="Password"
          type="password"
          value={form.password}
          onChange={update("password")}
          required
          minLength={8}
          hint="At least 8 characters"
        />

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-ink py-3 font-medium text-paper hover:bg-teal transition-colors disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Register"}
        </button>
      </form>
    </div>
  );
}

function Field({ label, hint, ...inputProps }) {
  return (
    <label className="block">
      <span className="text-sm font-medium">{label}</span>
      <input
        {...inputProps}
        className="mt-1.5 w-full rounded border border-line bg-white px-3 py-2 text-ink focus:border-amber outline-none"
      />
      {hint && <span className="mt-1 block text-xs text-ink/50">{hint}</span>}
    </label>
  );
}
