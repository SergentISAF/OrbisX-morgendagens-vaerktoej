import { useState } from "react";

export default function ReportForm() {
  const [sponsored, setSponsored] = useState("");
  const [sponsor, setSponsor] = useState("");

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (sponsored.trim()) params.set("sponsored", sponsored.trim());
    if (sponsor.trim()) params.set("sponsor", sponsor.trim());
    window.location.href = `/report?${params.toString()}`;
  };

  return (
    <form onSubmit={submit} className="mt-6 space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Sponseret (klub, hold, event)
          </span>
          <input
            type="text"
            value={sponsored}
            onChange={(e) => setSponsored(e.target.value)}
            placeholder="Aalborg Håndbold"
            required
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 text-base placeholder:text-[rgb(var(--muted))] focus:border-brand-500 focus:outline-none"
          />
        </label>
        <label className="block">
          <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
            Sponsor (valgfri)
          </span>
          <input
            type="text"
            value={sponsor}
            onChange={(e) => setSponsor(e.target.value)}
            placeholder="Carlsberg"
            className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 text-base placeholder:text-[rgb(var(--muted))] focus:border-brand-500 focus:outline-none"
          />
        </label>
      </div>
      <button
        type="submit"
        className="rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
      >
        Generer rapport
      </button>
      <p className="text-xs text-[rgb(var(--muted))]">
        Eksempler:{" "}
        <a
          href="/report?sponsored=Aalborg+H%C3%A5ndbold&sponsor=Carlsberg"
          className="underline-offset-2 hover:underline"
        >
          Aalborg Håndbold → Carlsberg
        </a>{" "}
        ·{" "}
        <a
          href="/report?sponsored=FCK&sponsor=Carlsberg"
          className="underline-offset-2 hover:underline"
        >
          FCK → Carlsberg
        </a>{" "}
        ·{" "}
        <a
          href="/report?sponsored=Aalborg+Pirates&sponsor=Spar+Nord"
          className="underline-offset-2 hover:underline"
        >
          Aalborg Pirates → Spar Nord
        </a>
      </p>
    </form>
  );
}
