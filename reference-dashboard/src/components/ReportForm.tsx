import { useState } from "react";

const COLOR_PRESETS: { label: string; hex: string }[] = [
  { label: "Blå (default)", hex: "#5b6ef0" },
  { label: "Rød", hex: "#dc2626" },
  { label: "Grøn", hex: "#16a34a" },
  { label: "Carlsberg-grøn", hex: "#005f3c" },
  { label: "AaB-rød", hex: "#c8102e" },
  { label: "Aalborg Pirates", hex: "#fbb800" },
  { label: "Norlys-orange", hex: "#f47b20" },
  { label: "DBU-rød", hex: "#c8102e" },
];

export default function ReportForm() {
  const [sponsored, setSponsored] = useState("");
  const [sponsor, setSponsor] = useState("");
  const [logo, setLogo] = useState("");
  const [color, setColor] = useState("#5b6ef0");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (sponsored.trim()) params.set("sponsored", sponsored.trim());
    if (sponsor.trim()) params.set("sponsor", sponsor.trim());
    if (logo.trim()) params.set("logo", logo.trim());
    if (color && color !== "#5b6ef0") params.set("color", color);
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
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-xs uppercase tracking-wider text-[rgb(var(--muted))] hover:text-[rgb(var(--fg))] transition"
      >
        {showAdvanced ? "− Skjul" : "+ Tilpas"} udseende (logo, farve)
      </button>

      {showAdvanced && (
        <div className="space-y-4 rounded-md border border-dashed border-[rgb(var(--border))] p-4">
          <label className="block">
            <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Logo-URL (valgfri)
            </span>
            <input
              type="url"
              value={logo}
              onChange={(e) => setLogo(e.target.value)}
              placeholder="https://eksempel.dk/logo.png"
              className="mt-2 w-full rounded-md border border-[rgb(var(--border))] bg-transparent px-4 py-2 text-base placeholder:text-[rgb(var(--muted))] focus:border-brand-500 focus:outline-none"
            />
            <span className="mt-1 block text-xs text-[rgb(var(--muted))]">
              Paste en URL til kundens logo. Vises øverst i rapporten.
            </span>
          </label>

          <div>
            <span className="text-xs uppercase tracking-wider text-[rgb(var(--muted))]">
              Accent-farve
            </span>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {COLOR_PRESETS.map((c) => (
                <button
                  key={c.hex + c.label}
                  type="button"
                  onClick={() => setColor(c.hex)}
                  title={c.label}
                  className={`size-8 rounded-md border-2 transition ${
                    color === c.hex
                      ? "border-[rgb(var(--fg))]"
                      : "border-transparent hover:border-[rgb(var(--border))]"
                  }`}
                  style={{ backgroundColor: c.hex }}
                />
              ))}
              <input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="size-8 cursor-pointer rounded-md border border-[rgb(var(--border))] bg-transparent"
              />
              <span className="font-mono text-xs text-[rgb(var(--muted))]">{color}</span>
            </div>
          </div>
        </div>
      )}

      <button
        type="submit"
        className="rounded-md bg-brand-500 px-5 py-2 text-sm font-medium text-white hover:bg-brand-600 transition"
      >
        Generer rapport
      </button>

      <p className="text-xs text-[rgb(var(--muted))]">
        Eksempler:{" "}
        <a
          href="/report?sponsored=Aalborg+H%C3%A5ndbold&sponsor=Carlsberg&color=%23c8102e"
          className="underline-offset-2 hover:underline"
        >
          Aalborg Håndbold (rød)
        </a>{" "}
        ·{" "}
        <a
          href="/report?sponsored=FCK&sponsor=Carlsberg&color=%23005f3c"
          className="underline-offset-2 hover:underline"
        >
          FCK (Carlsberg-grøn)
        </a>{" "}
        ·{" "}
        <a
          href="/report?sponsored=Aalborg+Pirates&sponsor=Spar+Nord&color=%23fbb800"
          className="underline-offset-2 hover:underline"
        >
          Aalborg Pirates (gul)
        </a>
      </p>
    </form>
  );
}
