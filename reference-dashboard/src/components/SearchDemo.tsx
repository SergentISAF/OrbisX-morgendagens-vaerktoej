import { useState } from "react";

const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

type Article = {
  article_id: number;
  site_name: string;
  article_url: string;
  article_title: string | null;
  article_created: string | null;
  time_on_frontpage: number | null;
};

type SearchResponse = {
  results: Article[];
  total_cluster_articles: number;
};

export default function SearchDemo() {
  const [query, setQuery] = useState("Carlsberg");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SearchResponse | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `${API_URL}/api/search?q=${encodeURIComponent(query)}&limit=10`,
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-12">
      <form onSubmit={submit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Søg efter brand eller emne..."
          className="flex-1 rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 text-base placeholder:text-[rgb(var(--muted))] focus:border-brand-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 transition"
        >
          {loading ? "Søger..." : "Søg"}
        </button>
      </form>

      {error && (
        <p className="mt-4 text-sm text-red-500">Fejl: {error}</p>
      )}

      {data && (
        <div className="mt-6">
          <p className="text-sm text-[rgb(var(--muted))]">
            {data.total_cluster_articles.toLocaleString("da-DK")} artikler matcher.
            Viser de {data.results.length} nyeste.
          </p>
          <ul className="mt-4 divide-y divide-[rgb(var(--border))] rounded-xl border border-[rgb(var(--border))]">
            {data.results.map((a) => (
              <li key={a.article_id} className="p-4">
                <a
                  href={a.article_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block hover:opacity-70 transition"
                >
                  <div className="text-base font-medium leading-snug">
                    {a.article_title ?? "(uden titel)"}
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-[rgb(var(--muted))]">
                    <span className="font-medium">{a.site_name}</span>
                    {a.article_created && <span>· {a.article_created}</span>}
                    {a.time_on_frontpage != null && (
                      <span>· {a.time_on_frontpage}t på forsiden</span>
                    )}
                  </div>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
