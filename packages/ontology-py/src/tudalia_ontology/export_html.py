"""
Generate a client-friendly HTML overview of the ontology.

Output: packages/ontology-py/dist/ontology-v0.2.html
Open in any browser / send as a file / host statically.

Run:
  python -m tudalia_ontology.export_html
"""

from __future__ import annotations

import html
from pathlib import Path

from .domains import DOMAINS
from .outcome_events import OutcomeEventType
from .relations import RelationKind
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .vocabulary import get_vocabulary

OUT_DIR = Path(__file__).resolve().parents[2] / "dist"
OUT_FILE = OUT_DIR / f"ontology-{ONTOLOGY_VERSION}.html"


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def main() -> None:
    vocab = get_vocabulary()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    domain_sections: list[str] = []
    for d in DOMAINS:
        concepts = vocab.by_domain.get(d.code, ())
        rows: list[str] = []
        for c in concepts:
            options = ", ".join(c.options) if c.options else "—"
            unit = c.unit or "—"
            omaha = c.omaha_problem or "—"
            icf = c.icf_ref or "—"
            katz = c.katz_lawton or "—"
            kinds = " / ".join(c.kinds)
            vtypes = " / ".join(c.value_types)
            flags = []
            if c.trendable:
                flags.append("trend")
            if c.clinician_review:
                flags.append("clinician review")
            flag_txt = ", ".join(flags) if flags else "—"
            rows.append(
                f"""
            <tr>
              <td><code>{_esc(c.code)}</code></td>
              <td><strong>{_esc(c.label_pl)}</strong></td>
              <td>{_esc(c.definition)}</td>
              <td>{_esc(kinds)}</td>
              <td>{_esc(vtypes)}</td>
              <td>{_esc(options)}</td>
              <td>{_esc(unit)}</td>
              <td>{_esc(omaha)}</td>
              <td>{_esc(icf)}</td>
              <td>{_esc(katz)}</td>
              <td>{_esc(flag_txt)}</td>
            </tr>"""
            )

        domain_sections.append(
            f"""
      <section class="domain" id="{_esc(d.code)}">
        <h2>{_esc(d.label_pl)} <span class="meta">{_esc(d.code)} · {len(concepts)} concepts</span></h2>
        <p class="domain-en">{_esc(d.label_en)} · CSV key: <code>{_esc(d.vocab_key)}</code></p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Polish label</th>
                <th>Definition</th>
                <th>Kind</th>
                <th>Value type</th>
                <th>Options</th>
                <th>Unit</th>
                <th>Omaha</th>
                <th>ICF</th>
                <th>Katz / Lawton</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {"".join(rows)}
            </tbody>
          </table>
        </div>
      </section>"""
        )

    nav = "\n".join(
        f'<a href="#{_esc(d.code)}">{_esc(d.label_pl)} '
        f'<small>{len(vocab.by_domain.get(d.code, ()))}</small></a>'
        for d in DOMAINS
    )

    events = "".join(
        f"<li><code>{_esc(e.value)}</code></li>" for e in OutcomeEventType
    )
    relations = "".join(
        f"<li><code>{_esc(r.value)}</code></li>" for r in RelationKind
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tudalia Care Ontology { _esc(ONTOLOGY_VERSION) }</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f3efe6;
      --surface: #fffdf8;
      --text: #1c1914;
      --muted: #5c564c;
      --brand: #0f6b64;
      --border: #d4cdc0;
      --sunken: #e8e2d6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Figtree, system-ui, sans-serif;
      color: var(--text);
      background:
        radial-gradient(900px 400px at 0% 0%, #e4efe9, transparent 55%),
        var(--bg);
      line-height: 1.45;
    }}
    header {{
      padding: 2.5rem 1.5rem 1.5rem;
      max-width: 1100px;
      margin: 0 auto;
    }}
    header h1 {{
      margin: 0 0 0.35rem;
      font-size: 2rem;
      letter-spacing: -0.02em;
      color: var(--brand);
    }}
    header .sub {{ color: var(--muted); margin: 0 0 1rem; }}
    .badge {{
      display: inline-block;
      background: var(--brand);
      color: #fff;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      margin-right: 0.4rem;
    }}
    .intro {{
      max-width: 1100px;
      margin: 0 auto 1.5rem;
      padding: 0 1.5rem;
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem 1.1rem;
    }}
    .card h3 {{ margin: 0 0 0.5rem; font-size: 0.95rem; color: var(--brand); }}
    .card ul {{ margin: 0; padding-left: 1.1rem; color: var(--muted); font-size: 0.9rem; }}
    .card p {{ margin: 0; color: var(--muted); font-size: 0.9rem; }}
    nav.domains {{
      max-width: 1100px;
      margin: 0 auto 1.5rem;
      padding: 0 1.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    nav.domains a {{
      text-decoration: none;
      color: var(--text);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.45rem 0.85rem;
      font-size: 0.9rem;
      font-weight: 600;
    }}
    nav.domains a small {{
      color: var(--muted);
      font-weight: 500;
      margin-left: 0.25rem;
    }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 0 1.5rem 3rem; }}
    .domain {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.25rem;
      margin-bottom: 1.25rem;
    }}
    .domain h2 {{
      margin: 0 0 0.25rem;
      font-size: 1.25rem;
      letter-spacing: -0.01em;
    }}
    .domain h2 .meta {{
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--muted);
    }}
    .domain-en {{ margin: 0 0 1rem; color: var(--muted); font-size: 0.9rem; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
    }}
    th, td {{
      text-align: left;
      vertical-align: top;
      padding: 0.55rem 0.5rem;
      border-bottom: 1px solid var(--sunken);
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      white-space: nowrap;
      position: sticky;
      top: 0;
      background: var(--surface);
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.78rem;
      background: var(--sunken);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
    }}
    footer {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 1.5rem 2.5rem;
      color: var(--muted);
      font-size: 0.85rem;
    }}
    @media print {{
      body {{ background: #fff; }}
      nav.domains a {{ border: 1px solid #ccc; }}
      .domain {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Tudalia Care Ontology</h1>
    <p class="sub">Structured care vocabulary for voice reports — labels only, no diagnosis.</p>
    <span class="badge">v{_esc(ONTOLOGY_VERSION)}</span>
    <span class="badge">{_esc(VOCABULARY_RELEASE)}</span>
    <span class="badge">{len(vocab)} concepts</span>
    <span class="badge">8 domains</span>
  </header>

  <div class="intro">
    <div class="card">
      <h3>What this is</h3>
      <p>When a caregiver speaks, the AI maps speech onto these concepts.
      The caregiver confirms before anything enters the Senior Journal.</p>
    </div>
    <div class="card">
      <h3>Knowledge-graph relations</h3>
      <ul>{relations}</ul>
    </div>
    <div class="card">
      <h3>Outcome events (separate confirm)</h3>
      <ul>{events}</ul>
    </div>
    <div class="card">
      <h3>Standards (mappings only)</h3>
      <p>Omaha · Katz ADL · Lawton IADL · ICF — used as references,
      never as clinical scores in the MVP.</p>
    </div>
  </div>

  <nav class="domains" aria-label="Domains">{nav}</nav>

  <main>
    {"".join(domain_sections)}
  </main>

  <footer>
    Generated from <code>{_esc(vocab.source)}</code> ·
    Tudalia Care Ontology · for internal / client review ·
    Print this page (Ctrl/Cmd+P) to PDF if needed.
  </footer>
</body>
</html>
"""

    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    print("Open in browser, or File → Print → Save as PDF for the client.")


if __name__ == "__main__":
    main()
