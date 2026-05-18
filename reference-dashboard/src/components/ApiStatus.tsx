import { useEffect, useState } from "react";

type Status = "loading" | "ok" | "error";

const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

export default function ApiStatus() {
  const [status, setStatus] = useState<Status>("loading");
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/`)
      .then((r) => r.json())
      .then((data) => {
        setStatus("ok");
        setVersion(data.version ?? null);
      })
      .catch(() => setStatus("error"));
  }, []);

  const dot =
    status === "ok"
      ? "bg-green-500"
      : status === "error"
        ? "bg-red-500"
        : "bg-yellow-500";

  const label =
    status === "ok"
      ? `API kører (v${version})`
      : status === "error"
        ? "API ikke fundet"
        : "Tjekker API...";

  return (
    <div className="inline-flex items-center gap-2 rounded-md border border-[rgb(var(--border))] px-3 py-1.5 text-sm">
      <span className={`size-2 rounded-full ${dot}`} />
      {label}
    </div>
  );
}
