import { useEffect, useState } from "react";
import { API_URL, authHeaders, clearAuth, getAuth } from "../lib/auth";

type Entity = {
  id: number;
  name: string;
  entity_type: string;
  search_text: string;
  color: string | null;
  logo_url: string | null;
  sponsor_link: string | null;
  last_synced_at: string | null;
  last_match_count: number;
};

const ENTITY_TYPES = ["brand", "sponsor", "sponseret", "konkurrent"];

export default function Workspace() {
  const [auth, setAuthState] = useState(getAuth());
  const [entities, setEntities] = useState<Entity[] | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState("brand");
  const [color, setColor] = useState("#5b6ef0");
  const [sponsorLink, setSponsorLink] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!auth) {
      window.location.href = "/login";
      return;
    }
    load();
  }, []);

  const load = async () => {
    const r = await fetch(`${API_URL}/api/entities`, { headers: authHeaders() });
    if (r.status === 401) {
      clearAuth();
      window.location.href = "/login";
      return;
    }
    if (!r.ok) {
      setError(`HTTP ${r.status}`);
      return;
    }
    setEntities(await r.json());
  };

  const addEntity = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const r = await fetch(`${API_URL}/api/entities`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        name,
        entity_type: type,
        color,
        sponsor_link: sponsorLink || null,
      }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => null);
      setError(err?.detail ?? `HTTP ${r.status}`);
      return;
    }
    setName("");
    setSponsorLink("");
    setShowAdd(false);
    await load();
  };

  const sync = async (id: number) => {
    setBusyId(id);
    setError(null);
    try {
      const r = await fetch(`${API_URL}/api/entities/${id}/sync`, {
        method: "POST",
        headers: authHeaders(),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (id: number) => {
    if (!confirm("Slet denne entity? Article-matches forsvinder også.")) return;
    await fetch(`${API_URL}/api/entities/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    await load();
  };

  const logout = () => {
    clearAuth();
    window.location.href = "/";
  };

  if (!auth) return null;
  const nf = new Intl.NumberFormat("da-DK");

  return (
    <div>
      <header className="mb-12 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-[rgb(var(--muted))]">
            Workspace
          </p>
          <h1 className="mt-2 font-serif text-4xl font-semibold tracking-tight">
            {auth.tenant_name}
          </h1>
          <p className="mt-1 text-sm text-[rgb(var(--muted))]">
            {auth.email}
          </p>
        </div>
        <button
          onClick={logout}
          className="rounded-md border border-[rgb(var(--border))] px-3 py-1.5 text-sm hover:bg-[rgb(var(--border))]/30 transition"
        >
          Log ud
        </button>
      </header>

      <section>
        <div className="flex items-center justify-between">
          <h2 className="font-serif text-2xl font-semibold">Dine entities</h2>
          <button
            onClick={() => setShowAdd(!showAdd)}
            className="rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
          >
            {showAdd ? "Annullér" : "+ Tilføj entity"}
          </button>
        </div>

        {showAdd && (
          <form
            onSubmit={addEntity}
            className="mt-6 space-y-4 rounded-xl border border-[rgb(var(--border))] p-5"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                  Navn
                </span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="Aalborg Håndbold"
                  className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                  Type
                </span>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-[rgb(var(--bg))] px-4 py-2 focus:border-brand-500 focus:outline-none"
                >
                  {ENTITY_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                  Accent-farve
                </span>
                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="size-10 cursor-pointer rounded-md border border-[rgb(var(--border))] bg-transparent"
                  />
                  <span className="font-mono text-sm text-[rgb(var(--muted))]">{color}</span>
                </div>
              </label>
              <label className="block">
                <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                  Sponsor-link (valgfri)
                </span>
                <input
                  type="text"
                  value={sponsorLink}
                  onChange={(e) => setSponsorLink(e.target.value)}
                  placeholder="Carlsberg"
                  className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
                />
                <span className="mt-1 block text-xs text-[rgb(var(--muted))]">
                  Bruges som sponsor-navn når du åbner rapporten
                </span>
              </label>
            </div>
            <button
              type="submit"
              className="rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
            >
              Tilføj
            </button>
          </form>
        )}

        {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

        {entities === null && (
          <p className="mt-8 text-[rgb(var(--muted))]">Henter...</p>
        )}

        {entities && entities.length === 0 && (
          <div className="mt-8 rounded-xl border border-dashed border-[rgb(var(--border))] p-8 text-center">
            <p className="text-[rgb(var(--muted))]">
              Ingen entities endnu. Tilføj én for at komme i gang.
            </p>
          </div>
        )}

        {entities && entities.length > 0 && (
          <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {entities.map((e) => {
              const params = new URLSearchParams();
              params.set("sponsored", e.name);
              if (e.sponsor_link) params.set("sponsor", e.sponsor_link);
              if (e.color) params.set("color", e.color);
              if (e.logo_url) params.set("logo", e.logo_url);
              return (
                <li
                  key={e.id}
                  className="rounded-xl border border-[rgb(var(--border))] p-5"
                  style={
                    e.color
                      ? { borderColor: e.color + "33" }
                      : undefined
                  }
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p
                        className="text-xs uppercase tracking-wider"
                        style={{ color: e.color ?? "rgb(var(--muted))" }}
                      >
                        {e.entity_type}
                      </p>
                      <h3 className="mt-1 font-serif text-lg font-semibold">
                        {e.name}
                      </h3>
                      {e.sponsor_link && (
                        <p className="text-xs text-[rgb(var(--muted))]">
                          → {e.sponsor_link}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => remove(e.id)}
                      className="text-xs text-[rgb(var(--muted))] hover:text-red-500 transition"
                      title="Slet"
                    >
                      ×
                    </button>
                  </div>

                  <div className="mt-4 text-sm">
                    <div className="font-mono text-2xl font-semibold tabular-nums">
                      {nf.format(e.last_match_count)}
                    </div>
                    <div className="text-xs text-[rgb(var(--muted))]">
                      gemte artikler i corpus
                    </div>
                    {e.last_synced_at && (
                      <div className="mt-1 text-xs text-[rgb(var(--muted))]">
                        Synket: {new Date(e.last_synced_at).toLocaleString("da-DK")}
                      </div>
                    )}
                  </div>

                  <div className="mt-4 flex gap-2">
                    <button
                      onClick={() => sync(e.id)}
                      disabled={busyId === e.id}
                      className="rounded-md border border-[rgb(var(--border))] px-3 py-1.5 text-xs font-medium hover:bg-[rgb(var(--border))]/30 disabled:opacity-50 transition"
                    >
                      {busyId === e.id ? "Synker..." : "Sync nu"}
                    </button>
                    <a
                      href={`/report?${params.toString()}`}
                      className="rounded-md px-3 py-1.5 text-xs font-medium text-white transition hover:opacity-90"
                      style={{ backgroundColor: e.color ?? "#5b6ef0" }}
                    >
                      Åbn rapport
                    </a>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </div>
  );
}
