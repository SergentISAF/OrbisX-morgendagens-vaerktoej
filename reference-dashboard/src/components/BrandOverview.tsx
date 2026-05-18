import { useState } from "react";

const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

type OutletStat = { site_name: string; count: number };

type Article = {
  article_id: number;
  site_name: string;
  article_url: string;
  article_title: string | null;
  article_created: string | null;
  time_on_frontpage: number | null;
  availability: string | null;
};

type Overview = {
  query: string;
  total_matches: number;
  sampled: number;
  unique_outlets: number;
  avg_time_on_frontpage: number;
  free_pct: number;
  top_outlets: OutletStat[];
  recent_articles: Article[];
};

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-[rgb(var(--border))] p-5">
      <div className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
        {label}
      </div>
      <div className="mt-2 font-serif text-3xl font-semibold tracking-tight">
        {value}
      </div>
      {hint && (
        <div className="mt-1 text-xs text-[rgb(var(--muted))]">{hint}</div>
      )}
    </div>
  );
}

function OutletBar({
  outlet,
  max,
}: {
  outlet: OutletStat;
  max: number;
}) {
  const pct = max > 0 ? (outlet.count / max) * 100 : 0;
  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-3 py-2">
      <div className="min-w-0">
        <div className="truncate text-sm font-medium">{outlet.site_name}</div>
        <div className="mt-1 h-2 overflow-hidden rounded-full bg-[rgb(var(--border))]">
          <div
            className="h-full rounded-full bg-brand-500 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      <div className="font-mono text-sm tabular-nums text-[rgb(var(--muted))]">
        {outlet.count}
      </div>
    </div>
  );
}

export default function BrandOverview() {
  const [query, setQuery] = useState("Carlsberg");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<Overview | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `${API_URL}/api/brand/overview?q=${encodeURIComponent(query)}&sample_size=100`,
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const maxOutletCount = data?.top_outlets[0]?.count ?? 0;
  const nf = new Intl.NumberFormat("da-DK");

  return (
    <div className="mt-12">
      <form onSubmit={submit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Indtast brand eller emne..."
          className="flex-1 rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 text-base placeholder:text-[rgb(var(--muted))] focus:border-brand-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 transition"
        >
          {loading ? "Henter..." : "Analyser"}
        </button>
      </form>

      {error && <p className="mt-4 text-sm text-red-500">Fejl: {error}</p>}

      {data && (
        <div className="mt-8 space-y-8">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard
              label="Total omtaler"
              value={nf.format(data.total_matches)}
              hint="i OrbisX-corpus"
            />
            <StatCard
              label="Medier"
              value={nf.format(data.unique_outlets)}
              hint={`af 134 overvågede`}
            />
            <StatCard
              label="Gns. forsidetid"
              value={`${data.avg_time_on_frontpage}t`}
              hint="for seneste artikler"
            />
            <StatCard
              label="Gratis-andel"
              value={`${data.free_pct.toFixed(0)}%`}
              hint="uden betalingsmur"
            />
          </div>

          <section className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <div className="rounded-xl border border-[rgb(var(--border))] p-6">
              <h3 className="font-serif text-xl font-semibold">
                Top medier
              </h3>
              <p className="mt-1 text-sm text-[rgb(var(--muted))]">
                Hvor {data.query} blev omtalt i de seneste {data.sampled} artikler
              </p>
              <div className="mt-5 divide-y divide-[rgb(var(--border))]">
                {data.top_outlets.map((o) => (
                  <OutletBar
                    key={o.site_name}
                    outlet={o}
                    max={maxOutletCount}
                  />
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-[rgb(var(--border))] p-6">
              <h3 className="font-serif text-xl font-semibold">Seneste artikler</h3>
              <p className="mt-1 text-sm text-[rgb(var(--muted))]">
                Klik for at åbne hos kilden
              </p>
              <ul className="mt-5 divide-y divide-[rgb(var(--border))]">
                {data.recent_articles.map((a) => (
                  <li key={a.article_id} className="py-3">
                    <a
                      href={a.article_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block hover:opacity-70 transition"
                    >
                      <div className="text-sm font-medium leading-snug">
                        {a.article_title ?? "(uden titel)"}
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-xs text-[rgb(var(--muted))]">
                        <span className="font-medium">{a.site_name}</span>
                        {a.article_created && <span>· {a.article_created}</span>}
                      </div>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
