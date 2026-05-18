import { useEffect, useState } from "react";

const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

type ReportLite = {
  sponsored: string;
  total_matches: number;
  ave_extrapolated_dkk: number;
  unique_outlets: number;
};

function readQuery() {
  if (typeof window === "undefined") {
    return { sponsored: "", color: "", label: "" };
  }
  const p = new URLSearchParams(window.location.search);
  return {
    sponsored: p.get("sponsored") ?? "",
    color: p.get("color") ?? "#5b6ef0",
    label: p.get("label") ?? "Mediedækning",
  };
}

export default function EmbedAve() {
  const [params, setParams] = useState(readQuery);
  const [data, setData] = useState<ReportLite | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setParams(readQuery());
  }, []);

  useEffect(() => {
    if (!params.sponsored) return;
    const url = new URL(`${API_URL}/api/sponsorship/report`);
    url.searchParams.set("sponsored", params.sponsored);
    url.searchParams.set("sample_size", "100");
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, [params.sponsored]);

  const nf = new Intl.NumberFormat("da-DK");
  const accent = params.color || "#5b6ef0";

  if (!params.sponsored) {
    return (
      <div className="p-4 text-sm text-gray-500">
        Tilføj <code>?sponsored=...</code> til URL'en.
      </div>
    );
  }

  if (error) {
    return <div className="p-4 text-sm text-red-500">Fejl: {error}</div>;
  }

  if (!data) {
    return (
      <div className="p-6">
        <div className="h-3 w-24 animate-pulse rounded-full bg-gray-200" />
        <div className="mt-3 h-10 w-48 animate-pulse rounded bg-gray-200" />
      </div>
    );
  }

  return (
    <div
      className="p-6"
      style={
        {
          "--accent": accent,
        } as React.CSSProperties
      }
    >
      <div
        className="text-[10px] font-semibold uppercase tracking-widest"
        style={{ color: accent }}
      >
        {params.label}
      </div>
      <div className="mt-2 font-serif text-4xl font-semibold leading-none tracking-tight md:text-5xl">
        {nf.format(data.ave_extrapolated_dkk)} kr
      </div>
      <div className="mt-3 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-xs text-gray-500">
        <span>
          <span className="font-medium text-gray-800">
            {nf.format(data.total_matches)}
          </span>{" "}
          omtaler
        </span>
        <span>
          <span className="font-medium text-gray-800">
            {data.unique_outlets}
          </span>{" "}
          medier
        </span>
        <span className="text-[10px] uppercase tracking-wider">
          Powered by OrbisX
        </span>
      </div>
    </div>
  );
}
