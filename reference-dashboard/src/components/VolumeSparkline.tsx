import { useEffect, useState } from "react";
import { API_URL, authHeaders } from "../lib/auth";

type VolumePoint = {
  date: string;
  articles: number;
  minutes_on_frontpage: number;
};

type VolumeResponse = {
  entity_id: number;
  keyword: string;
  total_articles: number;
  total_minutes_on_frontpage: number;
  timerange_days: number;
  daily: VolumePoint[];
};

type Props = {
  entityId: number;
  days?: number;
  color?: string | null;
  height?: number;
};

const nf = new Intl.NumberFormat("da-DK");

export default function VolumeSparkline({
  entityId,
  days = 30,
  color,
  height = 48,
}: Props) {
  const [data, setData] = useState<VolumeResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancel = false;
    fetch(`${API_URL}/api/entities/${entityId}/volume?days=${days}`, {
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
  }, [entityId, days]);

  if (err) {
    return (
      <div className="text-xs text-[rgb(var(--muted))]">
        Volume: kunne ikke hentes
      </div>
    );
  }
  if (!data) {
    return (
      <div className="text-xs text-[rgb(var(--muted))]">Henter volume...</div>
    );
  }
  if (data.daily.length === 0) {
    return (
      <div className="text-xs text-[rgb(var(--muted))]">
        Ingen data sidste {days} dage
      </div>
    );
  }

  const max = Math.max(...data.daily.map((d) => d.articles), 1);
  const width = 100;
  const barWidth = width / data.daily.length;
  const accent = color ?? "#5b6ef0";

  return (
    <div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        className="w-full"
        style={{ height: `${height}px` }}
        aria-label={`Volume sidste ${days} dage`}
      >
        {data.daily.map((d, i) => {
          const h = (d.articles / max) * (height - 2);
          return (
            <rect
              key={d.date}
              x={i * barWidth + 0.5}
              y={height - h}
              width={Math.max(barWidth - 1, 0.5)}
              height={h}
              fill={accent}
              opacity={0.85}
            >
              <title>{`${d.date}: ${d.articles} artikler`}</title>
            </rect>
          );
        })}
      </svg>
      <div className="mt-1 flex items-center justify-between text-[10px] text-[rgb(var(--muted))]">
        <span>{data.daily[0]?.date}</span>
        <span>
          {nf.format(data.total_articles)} omtaler · {days}d
        </span>
        <span>{data.daily[data.daily.length - 1]?.date}</span>
      </div>
    </div>
  );
}
