import { useEffect, useState } from "react";

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
type Report = {
  total_matches: number;
  unique_outlets: number;
  avg_time_on_frontpage: number;
  top_outlets: OutletStat[];
  top_stories: Article[];
  ave_extrapolated_dkk: number;
};
type SharedReport = {
  sponsored_name: string;
  sponsor_name: string | null;
  color: string | null;
  logo_url: string | null;
  tenant_name: string;
  report: Report;
  view_count: number;
};

function getToken(): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("t") ?? "";
}

export default function SharedReportView() {
  const [data, setData] = useState<SharedReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setError("Manglende token i URL");
      setLoading(false);
      return;
    }
    fetch(`${API_URL}/api/shared/${token}`)
      .then((r) => {
        if (!r.ok) throw new Error(r.status === 410 ? "Linket er udløbet" : `HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-8 text-[rgb(var(--muted))]">Indlæser rapport...</p>;
  if (error) {
    return (
      <div className="mx-auto max-w-md rounded-xl border border-[rgb(var(--border))] p-8 text-center">
        <p className="font-medium">Kunne ikke åbne rapport</p>
        <p className="mt-2 text-sm text-[rgb(var(--muted))]">{error}</p>
      </div>
    );
  }
  if (!data) return null;

  const nf = new Intl.NumberFormat("da-DK");
  const accent = data.color ?? "#5b6ef0";
  const today = new Intl.DateTimeFormat("da-DK", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date());
  const r = data.report;
  const maxOutlet = r.top_outlets[0]?.count ?? 0;

  return (
    <div
      style={
        {
          "--accent": accent,
          "--accent-soft": accent + "14",
          "--accent-border": accent + "4d",
        } as React.CSSProperties
      }
    >
      <div className="mb-6 flex items-start justify-between gap-4 no-print">
        <p className="text-sm text-[rgb(var(--muted))]">
          Delt af <span className="font-medium text-[rgb(var(--fg))]">{data.tenant_name}</span>
        </p>
        <button
          onClick={() => window.print()}
          className="rounded-md px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
          style={{ backgroundColor: "var(--accent)" }}
        >
          Print
        </button>
      </div>

      <header className="border-b border-[rgb(var(--border))] pb-6">
        {data.logo_url && (
          <img
            src={data.logo_url}
            alt={`${data.sponsored_name} logo`}
            className="mb-6 h-16 w-auto object-contain"
            onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
          />
        )}
        <p className="text-xs uppercase tracking-widest text-[rgb(var(--muted))]">
          Mediedækningsrapport
        </p>
        <h1 className="mt-3 font-serif text-4xl font-semibold leading-tight tracking-tight">
          {data.sponsored_name}
        </h1>
        {data.sponsor_name && (
          <p className="mt-3 text-base text-[rgb(var(--muted))]">
            Lavet til:{" "}
            <span className="font-medium text-[rgb(var(--fg))]">{data.sponsor_name}</span>
          </p>
        )}
        <p className="mt-1 text-sm text-[rgb(var(--muted))]">Genereret {today}</p>
      </header>

      <section
        className="mt-10 rounded-2xl border p-8"
        style={{
          backgroundColor: "var(--accent-soft)",
          borderColor: "var(--accent-border)",
        }}
      >
        <div className="text-xs uppercase tracking-widest" style={{ color: accent }}>
          Samlet annonceværdi
        </div>
        <div className="mt-3 font-serif text-5xl font-semibold leading-none tracking-tight md:text-6xl">
          {nf.format(r.ave_extrapolated_dkk)} kr
        </div>
        <p className="mt-4 max-w-2xl text-sm text-[rgb(var(--muted))]">
          Estimat for hvad medieomtalen ville have kostet som købte annoncer.
          Bygget på {nf.format(r.total_matches)} samlede omtaler i {r.unique_outlets} medier.
        </p>
      </section>

      <section className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-3">
        <StatTile value={nf.format(r.total_matches)} label="Omtaler" />
        <StatTile value={nf.format(r.unique_outlets)} label="Medier" />
        <StatTile value={`${Math.round(r.avg_time_on_frontpage)}t`} label="Gns. forsidetid" />
      </section>

      {r.top_stories.length > 0 && (
        <section className="mt-12">
          <h2 className="font-serif text-xl font-semibold">Top historier</h2>
          <ol className="mt-5 space-y-3">
            {r.top_stories.map((a, i) => (
              <li key={a.article_id} className="rounded-xl border border-[rgb(var(--border))] p-5">
                <a
                  href={a.article_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block hover:opacity-70 transition"
                >
                  <div className="flex items-start gap-4">
                    <span
                      className="font-serif text-3xl font-semibold tabular-nums leading-none"
                      style={{ color: accent }}
                    >
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="font-serif text-lg font-medium leading-snug">
                        {a.article_title ?? "(uden titel)"}
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[rgb(var(--muted))]">
                        <span className="font-medium">{a.site_name}</span>
                        {a.article_created && <span>· {a.article_created}</span>}
                        {a.time_on_frontpage != null && (
                          <span className="font-mono tabular-nums">
                            · {a.time_on_frontpage}t på forsiden
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </a>
              </li>
            ))}
          </ol>
        </section>
      )}

      {r.top_outlets.length > 0 && (
        <section className="mt-12">
          <h2 className="font-serif text-xl font-semibold">Top medier</h2>
          <ol className="mt-5 divide-y divide-[rgb(var(--border))]">
            {r.top_outlets.map((o) => {
              const pct = maxOutlet > 0 ? (o.count / maxOutlet) * 100 : 0;
              return (
                <li key={o.site_name} className="grid grid-cols-[1fr_auto] items-center gap-3 py-2">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{o.site_name}</div>
                    <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[rgb(var(--border))]">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${pct}%`, backgroundColor: accent }}
                      />
                    </div>
                  </div>
                  <div className="font-mono text-sm tabular-nums">{o.count}</div>
                </li>
              );
            })}
          </ol>
        </section>
      )}

      <footer className="mt-16 border-t border-[rgb(var(--border))] pt-6 text-xs text-[rgb(var(--muted))]">
        Bygget med OrbisX · {data.view_count} visninger
      </footer>
    </div>
  );
}

function StatTile({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl border border-[rgb(var(--border))] p-5">
      <div className="font-serif text-3xl font-semibold tabular-nums">{value}</div>
      <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">{label}</div>
    </div>
  );
}
