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
type AveBreakdown = {
  total_dkk: number;
  avg_per_article_dkk: number;
  sample_size: number;
  tier_distribution: Record<string, number>;
};

type CoMention = {
  sponsor_total_matches: number;
  sponsor_sampled: number;
  intersection_count: number;
  intersection_pct_of_sponsored_sample: number;
  intersection_articles: Article[];
  intersection_ave_dkk: number;
  method: string;
};

type Report = {
  sponsored: string;
  sponsor: string | null;
  period_label: string;
  total_matches: number;
  sampled: number;
  unique_outlets: number;
  avg_time_on_frontpage: number;
  median_time_on_frontpage: number;
  total_time_on_frontpage: number;
  availability: { free: number; paid: number };
  top_outlets: OutletStat[];
  sample_articles: Article[];
  ave_sample: AveBreakdown;
  ave_extrapolated_dkk: number;
  co_mention: CoMention | null;
  co_mention_note: string;
};

function readQuery() {
  if (typeof window === "undefined") return { sponsored: "", sponsor: "" };
  const p = new URLSearchParams(window.location.search);
  return {
    sponsored: p.get("sponsored") ?? "",
    sponsor: p.get("sponsor") ?? "",
  };
}

function InlineReportForm() {
  const [s, setS] = useState("");
  const [sp, setSp] = useState("");
  const go = (e: React.FormEvent) => {
    e.preventDefault();
    const p = new URLSearchParams();
    if (s.trim()) p.set("sponsored", s.trim());
    if (sp.trim()) p.set("sponsor", sp.trim());
    window.location.search = p.toString();
  };
  return (
    <form onSubmit={go} className="rounded-xl border border-[rgb(var(--border))] p-6">
      <h2 className="font-serif text-2xl font-semibold">Lav en rapport</h2>
      <p className="mt-2 text-sm text-[rgb(var(--muted))]">
        Indtast en sponseret entitet (klub, hold, event) og valgfrit en sponsor.
      </p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Sponseret
          </span>
          <input
            type="text"
            value={s}
            onChange={(e) => setS(e.target.value)}
            placeholder="fx Aalborg Håndbold"
            required
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
          />
        </label>
        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Sponsor (valgfri)
          </span>
          <input
            type="text"
            value={sp}
            onChange={(e) => setSp(e.target.value)}
            placeholder="fx Carlsberg"
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 focus:border-brand-500 focus:outline-none"
          />
        </label>
      </div>
      <button
        type="submit"
        className="mt-5 rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
      >
        Generer rapport
      </button>
    </form>
  );
}

export default function SponsorshipReport() {
  const [{ sponsored, sponsor }, setParams] = useState(readQuery);
  const [data, setData] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setParams(readQuery());
  }, []);

  useEffect(() => {
    if (!sponsored) return;
    setLoading(true);
    setError(null);
    const url = new URL(`${API_URL}/api/sponsorship/report`);
    url.searchParams.set("sponsored", sponsored);
    if (sponsor) url.searchParams.set("sponsor", sponsor);
    url.searchParams.set("sample_size", "200");
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sponsored, sponsor]);

  const nf = new Intl.NumberFormat("da-DK");
  const today = new Intl.DateTimeFormat("da-DK", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date());

  if (!sponsored) {
    return <InlineReportForm />;
  }

  if (loading) return <p className="text-[rgb(var(--muted))]">Bygger rapport...</p>;
  if (error) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6">
        <p className="font-medium text-red-500">Kunne ikke hente rapport: {error}</p>
        <p className="mt-2 text-sm text-[rgb(var(--muted))]">
          OrbisX-API'et er nogle gange flaky. Prøv igen om et øjeblik.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
        >
          Prøv igen
        </button>
      </div>
    );
  }
  if (!data) return null;

  const maxOutlet = data.top_outlets[0]?.count ?? 0;
  const freePct = data.sampled > 0 ? Math.round((data.availability.free / data.sampled) * 100) : 0;

  return (
    <div className="print-compact">
      <div className="mb-6 flex items-start justify-between gap-4 no-print">
        <p className="text-sm text-[rgb(var(--muted))]">
          Klar til print. Tryk Cmd+P (Mac) eller Ctrl+P (Windows).
        </p>
        <button
          onClick={() => window.print()}
          className="print-keep rounded-md bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
        >
          Print rapport
        </button>
      </div>

      <header className="border-b border-[rgb(var(--border))] pb-6">
        <p className="text-xs uppercase tracking-widest text-[rgb(var(--muted))]">
          Mediedækningsrapport
        </p>
        <h1 className="mt-3 font-serif text-4xl font-semibold leading-tight tracking-tight">
          {data.sponsored}
        </h1>
        {data.sponsor && (
          <p className="mt-3 text-base text-[rgb(var(--muted))]">
            Lavet til hovedsponsor: <span className="font-medium text-[rgb(var(--fg))]">{data.sponsor}</span>
          </p>
        )}
        <p className="mt-1 text-sm text-[rgb(var(--muted))]">
          Genereret {today} · {data.period_label}
        </p>
      </header>

      <section className="mt-10 rounded-2xl border border-[rgb(var(--border))] bg-brand-500/5 p-8">
        <div className="text-xs uppercase tracking-widest text-brand-500">
          Samlet annonceværdi (AVE)
        </div>
        <div className="mt-3 font-serif text-5xl font-semibold leading-none tracking-tight md:text-6xl">
          {nf.format(data.ave_extrapolated_dkk)} kr
        </div>
        <p className="mt-4 max-w-2xl text-sm text-[rgb(var(--muted))]">
          Estimat for hvad medieomtalen ville have kostet som købte annoncer.
          Beregnet ud fra {data.ave_sample.sample_size} samplede artikler:
          gennemsnit {nf.format(data.ave_sample.avg_per_article_dkk)} kr per artikel
          × {nf.format(data.total_matches)} samlede omtaler.
        </p>
      </section>

      <section className="mt-10">
        <h2 className="font-serif text-xl font-semibold">Overblik</h2>
        <div className="mt-5 grid grid-cols-2 gap-6 md:grid-cols-4">
          <div>
            <div className="font-serif text-3xl font-semibold tabular-nums">
              {nf.format(data.total_matches)}
            </div>
            <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Omtaler i alt
            </div>
          </div>
          <div>
            <div className="font-serif text-3xl font-semibold tabular-nums">
              {nf.format(data.unique_outlets)}
            </div>
            <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Medier nået
            </div>
          </div>
          <div>
            <div className="font-serif text-3xl font-semibold tabular-nums">
              {data.avg_time_on_frontpage}t
            </div>
            <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Gns. forsidetid
            </div>
          </div>
          <div>
            <div className="font-serif text-3xl font-semibold tabular-nums">
              {nf.format(data.total_time_on_frontpage)}t
            </div>
            <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Total forsidetid
            </div>
          </div>
        </div>

        <div className="mt-6 text-sm text-[rgb(var(--muted))]">
          Heraf <span className="font-medium text-[rgb(var(--fg))]">{freePct}%</span> uden betalingsmur ({data.availability.free} af {data.sampled} i sample).
        </div>
      </section>

      <section className="mt-12">
        <h2 className="font-serif text-xl font-semibold">Top medier</h2>
        <p className="mt-1 text-sm text-[rgb(var(--muted))]">
          De {data.top_outlets.length} medier der har skrevet mest i seneste sample
        </p>
        <ol className="mt-5 divide-y divide-[rgb(var(--border))]">
          {data.top_outlets.map((o, i) => {
            const pct = maxOutlet > 0 ? (o.count / maxOutlet) * 100 : 0;
            return (
              <li key={o.site_name} className="grid grid-cols-[2rem_1fr_auto] items-center gap-3 py-2.5">
                <span className="font-mono text-xs tabular-nums text-[rgb(var(--muted))]">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="min-w-0">
                  <div className="text-sm font-medium">{o.site_name}</div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[rgb(var(--border))]">
                    <div className="h-full rounded-full bg-brand-500" style={{ width: `${pct}%` }} />
                  </div>
                </div>
                <div className="font-mono text-sm tabular-nums">{o.count}</div>
              </li>
            );
          })}
        </ol>
      </section>

      {data.co_mention && data.sponsor && (
        <section className="mt-12 rounded-2xl border-2 border-brand-500/30 bg-brand-500/5 p-6">
          <p className="text-xs uppercase tracking-widest text-brand-500">
            Sponsor-co-mention
          </p>
          <h2 className="mt-2 font-serif text-2xl font-semibold tracking-tight">
            Hvor {data.sponsored} og {data.sponsor} optræder sammen
          </h2>
          <div className="mt-6 grid gap-6 md:grid-cols-3">
            <div>
              <div className="font-serif text-3xl font-semibold tabular-nums">
                {data.co_mention.intersection_count}
              </div>
              <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                Fælles artikler i sample
              </div>
            </div>
            <div>
              <div className="font-serif text-3xl font-semibold tabular-nums">
                {data.co_mention.intersection_pct_of_sponsored_sample.toFixed(1)}%
              </div>
              <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                Andel af {data.sponsored}-omtaler
              </div>
            </div>
            <div>
              <div className="font-serif text-3xl font-semibold tabular-nums">
                {nf.format(data.co_mention.intersection_ave_dkk)} kr
              </div>
              <div className="mt-1 text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                AVE i co-mention-sample
              </div>
            </div>
          </div>
          {data.co_mention.intersection_articles.length > 0 ? (
            <ul className="mt-6 divide-y divide-[rgb(var(--border))]">
              {data.co_mention.intersection_articles.map((a) => (
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
          ) : (
            <p className="mt-6 text-sm text-[rgb(var(--muted))]">
              Ingen fælles artikler fundet i sample. Det er enten fordi sponsoratet
              ikke får direkte omtale i de seneste artikler, eller fordi vi har
              ramt sample-grænsen (kræver fuld OrbisX cluster-adgang for nøjagtige tal).
            </p>
          )}
          <p className="mt-4 text-xs text-[rgb(var(--muted))]">{data.co_mention.method}</p>
        </section>
      )}

      <section className="mt-12 page-break">
        <h2 className="font-serif text-xl font-semibold">Eksempler på dækning</h2>
        <p className="mt-1 text-sm text-[rgb(var(--muted))]">
          Et udvalg af de seneste {data.sample_articles.length} artikler i sample
        </p>
        <ul className="mt-5 divide-y divide-[rgb(var(--border))]">
          {data.sample_articles.map((a) => (
            <li key={a.article_id} className="py-3">
              <a
                href={a.article_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block hover:opacity-70 transition"
              >
                <div className="flex items-center gap-2">
                  {a.availability === "free" && (
                    <span className="rounded-md bg-green-500/15 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-green-700">
                      Gratis
                    </span>
                  )}
                  {a.availability === "paid" && (
                    <span className="rounded-md bg-blue-500/15 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-blue-700">
                      Betalingsvæg
                    </span>
                  )}
                </div>
                <div className="mt-1 text-sm font-medium leading-snug">
                  {a.article_title ?? "(uden titel)"}
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-[rgb(var(--muted))]">
                  <span className="font-medium">{a.site_name}</span>
                  {a.article_created && <span>· {a.article_created}</span>}
                  {a.time_on_frontpage != null && <span>· {a.time_on_frontpage}t på forsiden</span>}
                </div>
              </a>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-12 rounded-md border border-[rgb(var(--border))] bg-[rgb(var(--border))]/15 p-5 text-sm text-[rgb(var(--muted))]">
        <strong className="text-[rgb(var(--fg))]">Note om metode</strong>
        <p className="mt-2">{data.co_mention_note}</p>
        <p className="mt-2">
          Data fra OrbisX (134 danske medier). Forsidetid måler hvor længe artiklen lå synligt på mediets forside.
        </p>
        <p className="mt-2">
          AVE-værdier er rough industry estimates baseret på outlet-tier
          (broadcast/national/business/regional/niche) × forsidetid-prominence.
          Brancher generelt accepterer AVE som indikativ værdi, ikke præcis pris.
          Værdier kan justeres per kunde når rate-cards indsamles.
        </p>
      </section>
    </div>
  );
}
