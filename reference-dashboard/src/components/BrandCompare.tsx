import { useState } from "react";

const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

type OutletStat = { site_name: string; count: number };
type BrandShare = {
  query: string;
  total_matches: number;
  sampled: number;
  unique_outlets: number;
  avg_time_on_frontpage: number;
  top_outlets: OutletStat[];
  share_pct: number;
};
type CompareResponse = {
  total_combined: number;
  brands: BrandShare[];
};

const BRAND_COLORS = [
  "bg-brand-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-violet-500",
];

const BRAND_TEXT = [
  "text-brand-500",
  "text-emerald-500",
  "text-amber-500",
  "text-rose-500",
  "text-violet-500",
];

export default function BrandCompare() {
  const [brands, setBrands] = useState<string[]>(["Carlsberg", "Tuborg"]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<CompareResponse | null>(null);

  const addBrand = () => {
    const v = input.trim();
    if (!v || brands.length >= 5 || brands.includes(v)) return;
    setBrands([...brands, v]);
    setInput("");
  };

  const removeBrand = (b: string) =>
    setBrands(brands.filter((x) => x !== b));

  const compare = async () => {
    if (brands.length < 2) {
      setError("Tilføj mindst 2 brands");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const params = brands.map((b) => `brands=${encodeURIComponent(b)}`).join("&");
      const r = await fetch(`${API_URL}/api/compare/overview?${params}&sample_size=50`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const nf = new Intl.NumberFormat("da-DK");

  return (
    <div className="mt-24">
      <div className="max-w-2xl">
        <p className="mb-4 text-sm uppercase tracking-widest text-[rgb(var(--muted))]">
          Konkurrent-sammenligning (fase 8)
        </p>
        <h2 className="font-serif text-4xl font-semibold leading-tight tracking-tight">
          Hvem fylder mest i medierne?
        </h2>
        <p className="mt-4 text-base text-[rgb(var(--muted))]">
          Tilføj 2-5 brands og se Share-of-Voice, mediefordeling og volumen
          side-by-side.
        </p>
      </div>

      <div className="mt-8">
        <div className="flex flex-wrap items-center gap-2">
          {brands.map((b, i) => (
            <span
              key={b}
              className="inline-flex items-center gap-2 rounded-full border border-[rgb(var(--border))] bg-[rgb(var(--border))]/30 py-1 pl-3 pr-1 text-sm"
            >
              <span className={`size-2 rounded-full ${BRAND_COLORS[i]}`} />
              {b}
              <button
                onClick={() => removeBrand(b)}
                aria-label={`Fjern ${b}`}
                className="ml-1 inline-flex size-5 items-center justify-center rounded-full hover:bg-[rgb(var(--border))] transition"
              >
                ×
              </button>
            </span>
          ))}
          {brands.length < 5 && (
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addBrand();
                }
              }}
              placeholder="Tilføj brand + Enter"
              className="min-w-[180px] flex-1 rounded-md border border-[rgb(var(--border))] bg-transparent px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none"
            />
          )}
        </div>

        <button
          onClick={compare}
          disabled={loading || brands.length < 2}
          className="mt-4 rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50 transition"
        >
          {loading ? "Sammenligner..." : "Sammenlign"}
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

      {data && (
        <div className="mt-10 space-y-10">
          <div className="rounded-xl border border-[rgb(var(--border))] p-6">
            <h3 className="font-serif text-xl font-semibold">Share-of-Voice</h3>
            <p className="mt-1 text-sm text-[rgb(var(--muted))]">
              Andel af de samlede {nf.format(data.total_combined)} omtaler
            </p>

            <div className="mt-6 flex h-3 overflow-hidden rounded-full">
              {data.brands.map((b, i) => (
                <div
                  key={b.query}
                  className={`${BRAND_COLORS[i]} transition-all`}
                  style={{ width: `${b.share_pct}%` }}
                  title={`${b.query}: ${b.share_pct}%`}
                />
              ))}
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {data.brands.map((b, i) => (
                <div key={b.query} className="flex items-center gap-3">
                  <span className={`size-3 shrink-0 rounded-full ${BRAND_COLORS[i]}`} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium">{b.query}</div>
                    <div className="text-xs text-[rgb(var(--muted))]">
                      {nf.format(b.total_matches)} omtaler
                    </div>
                  </div>
                  <div className="font-mono text-base font-semibold tabular-nums">
                    {b.share_pct.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
            {data.brands.map((b, i) => (
              <div
                key={b.query}
                className="rounded-xl border border-[rgb(var(--border))] p-5"
              >
                <div className="flex items-center gap-2">
                  <span className={`size-2 rounded-full ${BRAND_COLORS[i]}`} />
                  <h4 className={`font-serif text-lg font-semibold ${BRAND_TEXT[i]}`}>
                    {b.query}
                  </h4>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <div>
                    <div className="font-mono text-xl font-semibold tabular-nums">
                      {nf.format(b.total_matches)}
                    </div>
                    <div className="mt-0.5 text-[10px] uppercase tracking-wider text-[rgb(var(--muted))]">
                      Total
                    </div>
                  </div>
                  <div>
                    <div className="font-mono text-xl font-semibold tabular-nums">
                      {b.unique_outlets}
                    </div>
                    <div className="mt-0.5 text-[10px] uppercase tracking-wider text-[rgb(var(--muted))]">
                      Medier
                    </div>
                  </div>
                  <div>
                    <div className="font-mono text-xl font-semibold tabular-nums">
                      {b.avg_time_on_frontpage}t
                    </div>
                    <div className="mt-0.5 text-[10px] uppercase tracking-wider text-[rgb(var(--muted))]">
                      Forsidetid
                    </div>
                  </div>
                </div>
                {b.top_outlets.length > 0 && (
                  <div className="mt-5">
                    <div className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
                      Top medier
                    </div>
                    <ul className="mt-2 space-y-1">
                      {b.top_outlets.map((o) => (
                        <li
                          key={o.site_name}
                          className="flex justify-between text-xs"
                        >
                          <span className="truncate">{o.site_name}</span>
                          <span className="font-mono tabular-nums text-[rgb(var(--muted))]">
                            {o.count}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
