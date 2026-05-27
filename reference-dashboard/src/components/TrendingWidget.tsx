import { useEffect, useState } from "react";
import { API_URL, authHeaders } from "../lib/auth";

type Story = {
  thread_id: number | null;
  title: string | null;
  url: string | null;
  site_count: number | null;
  article_count: number | null;
  expected_views: number | null;
  latest_created: string | null;
};

type TrendingResponse = {
  fetched_at: string;
  country: string;
  timerange_days: number;
  stories: Story[];
};

const nf = new Intl.NumberFormat("da-DK");

function compactNum(n: number | null): string {
  if (n === null || n === undefined) return "?";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "k";
  return nf.format(n);
}

export default function TrendingWidget({
  limit = 8,
  days = 2,
}: {
  limit?: number;
  days?: number;
}) {
  const [data, setData] = useState<TrendingResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancel = false;
    fetch(`${API_URL}/api/trending?limit=${limit}&days=${days}`, {
      headers: authHeaders(),
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => {
        if (!cancel) setData(d);
      })
      .catch((e) => {
        if (!cancel) setErr(e.message);
      });
    return () => {
      cancel = true;
    };
  }, [limit, days]);

  return (
    <section className="rounded-xl border border-[rgb(var(--border))] p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-serif text-lg font-semibold">
          Trender lige nu i medierne
        </h3>
        <span className="text-xs text-[rgb(var(--muted))]">
          {days === 1 ? "sidste døgn" : `sidste ${days} dage`}
        </span>
      </div>

      {err && (
        <p className="mt-4 text-sm text-red-500">
          Kunne ikke hente trending: {err}
        </p>
      )}
      {!data && !err && (
        <p className="mt-4 text-sm text-[rgb(var(--muted))]">Henter...</p>
      )}
      {data && data.stories.length === 0 && (
        <p className="mt-4 text-sm text-[rgb(var(--muted))]">
          Ingen trending stories
        </p>
      )}

      {data && data.stories.length > 0 && (
        <ol className="mt-4 space-y-3">
          {data.stories.map((s, i) => (
            <li key={s.thread_id ?? i} className="flex gap-3">
              <span className="font-mono text-xs text-[rgb(var(--muted))] pt-0.5">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="flex-1 min-w-0">
                <a
                  href={s.url ?? "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="line-clamp-2 text-sm font-medium hover:underline"
                >
                  {s.title ?? "(uden titel)"}
                </a>
                <div className="mt-0.5 flex flex-wrap gap-x-3 text-[11px] text-[rgb(var(--muted))]">
                  <span>{compactNum(s.article_count)} artikler</span>
                  <span>{compactNum(s.site_count)} medier</span>
                  <span>{compactNum(s.expected_views)} forventet visninger</span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
