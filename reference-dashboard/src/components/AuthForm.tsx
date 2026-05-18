import { useState } from "react";
import { API_URL, setAuth } from "../lib/auth";

type Mode = "login" | "signup";

export default function AuthForm({ mode }: { mode: Mode }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const body =
        mode === "signup"
          ? { email, password, tenant_name: tenantName }
          : { email, password };
      const r = await fetch(`${API_URL}/api/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) {
        const errBody = await r.json().catch(() => null);
        throw new Error(errBody?.detail ?? `HTTP ${r.status}`);
      }
      const data = await r.json();
      setAuth({
        token: data.access_token,
        user_id: data.user_id,
        tenant_id: data.tenant_id,
        email: data.email,
        tenant_name: data.tenant_name,
      });
      window.location.href = "/workspace";
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <h1 className="font-serif text-3xl font-semibold tracking-tight">
        {mode === "signup" ? "Opret konto" : "Log ind"}
      </h1>
      <p className="mt-2 text-sm text-[rgb(var(--muted))]">
        {mode === "signup"
          ? "Opret dit firmas workspace og tilføj brands du vil overvåge."
          : "Adgang til din workspace og gemte brands."}
      </p>

      <form onSubmit={submit} className="mt-8 space-y-4">
        {mode === "signup" && (
          <label className="block">
            <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Firma- eller workspace-navn
            </span>
            <input
              type="text"
              value={tenantName}
              onChange={(e) => setTenantName(e.target.value)}
              required
              placeholder="Aalborg Håndbold"
              className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
            />
          </label>
        )}

        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Email
          </span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="navn@firma.dk"
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
          />
        </label>

        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Password
          </span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
          />
        </label>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-brand-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 transition"
        >
          {loading ? "Et øjeblik..." : mode === "signup" ? "Opret konto" : "Log ind"}
        </button>

        <p className="text-center text-sm text-[rgb(var(--muted))]">
          {mode === "signup" ? (
            <>
              Har du allerede en konto?{" "}
              <a href="/login" className="text-brand-500 underline-offset-4 hover:underline">
                Log ind
              </a>
            </>
          ) : (
            <>
              Ny her?{" "}
              <a href="/signup" className="text-brand-500 underline-offset-4 hover:underline">
                Opret konto
              </a>
            </>
          )}
        </p>
      </form>
    </div>
  );
}
