"""
Generate a clickable client demo of the visit-report flow.

Steps the client can click through:
  1. Choose a Polish caregiver transcript
  2. See ontology extraction (validated by this package)
  3. Confirm → Senior Journal (+ optional separate fall confirm)

Output: packages/ontology-py/dist/flow-demo-0.2.0.html

Run:
  python -m tudalia_ontology.export_flow_demo
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .extraction import validate_extraction
from .flow import confirm_to_journal_entries, to_confirm_view
from .samples import SAMPLES
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE

OUT_DIR = Path(__file__).resolve().parents[2] / "dist"
OUT_FILE = OUT_DIR / f"flow-demo-{ONTOLOGY_VERSION}.html"


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _build_scenarios() -> list[dict]:
    scenarios: list[dict] = []
    for sample in SAMPLES:
        result = validate_extraction(sample["raw"])
        view = to_confirm_view(result)
        journal = confirm_to_journal_entries(
            care_recipient_id="11111111-1111-1111-1111-111111111111",
            visit_id="22222222-2222-2222-2222-222222222222",
            confirmed_by="caregiver-anna",
            confirmed_at="2026-09-30T12:00:00+00:00",
            observed_at="2026-09-30T12:00:00+00:00",
            extraction=result,
            confirmed_outcome_event_types=[
                e.type.value for e in result.proposed_outcome_events
            ],
        )
        journal_without_events = confirm_to_journal_entries(
            care_recipient_id="11111111-1111-1111-1111-111111111111",
            visit_id="22222222-2222-2222-2222-222222222222",
            confirmed_by="caregiver-anna",
            confirmed_at="2026-09-30T12:00:00+00:00",
            observed_at="2026-09-30T12:00:00+00:00",
            extraction=result,
            confirmed_outcome_event_types=[],
        )
        scenarios.append(
            {
                "id": sample["id"],
                "title_pl": sample["title_pl"],
                "title_en": sample["title_en"],
                "transcript": sample["transcript"],
                "view": view.model_dump(),
                "journal": journal.model_dump(mode="json"),
                "journal_without_events": journal_without_events.model_dump(
                    mode="json"
                ),
                "has_events": bool(result.proposed_outcome_events),
            }
        )
    return scenarios


def main() -> None:
    scenarios = _build_scenarios()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data_json = json.dumps(scenarios, ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tudalia — flow demo { _esc(ONTOLOGY_VERSION) }</title>
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f3efe6; --surface: #fffdf8; --text: #1c1914; --muted: #5c564c;
      --brand: #0f6b64; --brand-hover: #0b554f; --border: #d4cdc0;
      --sunken: #e8e2d6; --ok: #1f6b3a; --ok-bg: #dcefe3; --warn-bg: #f5e6c8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: Figtree, system-ui, sans-serif; color: var(--text);
      background: radial-gradient(900px 400px at 10% -10%, #e4efe9, transparent 50%), var(--bg);
      line-height: 1.45;
    }}
    .wrap {{ max-width: 520px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }}
    h1 {{ margin: 0; color: var(--brand); font-size: 1.75rem; letter-spacing: -0.02em; }}
    .sub {{ color: var(--muted); margin: 0.25rem 0 1.25rem; }}
    .steps {{ display: flex; gap: 6px; margin-bottom: 1rem; }}
    .dot {{ flex: 1; height: 4px; border-radius: 99px; background: var(--sunken); }}
    .dot.on {{ background: var(--brand); }}
    .dot.done {{ background: color-mix(in srgb, var(--brand) 55%, var(--sunken)); }}
    .panel {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 18px; padding: 1.25rem; box-shadow: 0 1px 0 rgba(0,0,0,.03);
    }}
    .panel h2 {{ margin: 0 0 0.35rem; font-size: 1.25rem; }}
    .lead {{ color: var(--muted); margin: 0 0 1rem; }}
    .sample {{
      display: block; width: 100%; text-align: left; margin-bottom: 0.5rem;
      min-height: 48px; padding: 0.75rem 1rem; border-radius: 12px;
      border: 1px solid var(--border); background: var(--bg); cursor: pointer; font: inherit;
    }}
    .sample:hover, .sample.sel {{ border-color: var(--brand); background: #d7ebe8; }}
    .sample small {{ display: block; color: var(--muted); margin-top: 2px; font-size: 0.85rem; }}
    .btn {{
      width: 100%; min-height: 48px; border: none; border-radius: 12px;
      font: inherit; font-weight: 600; cursor: pointer; margin-top: 0.5rem;
    }}
    .btn-primary {{ background: var(--brand); color: #fff; }}
    .btn-primary:hover {{ background: var(--brand-hover); }}
    .btn-secondary {{ background: transparent; border: 1px solid var(--border); color: var(--muted); }}
    .item {{
      border: 1px solid var(--border); border-radius: 12px; padding: 0.85rem;
      margin-bottom: 0.6rem; background: var(--bg);
    }}
    .item.warn {{ background: var(--warn-bg); }}
    .item-top {{ display: flex; justify-content: space-between; gap: 0.5rem; font-weight: 600; }}
    .tag {{
      font-size: 0.7rem; font-weight: 600; color: #fff; background: var(--brand);
      border-radius: 99px; padding: 2px 8px; white-space: nowrap; align-self: flex-start;
    }}
    .meta {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }}
    .evidence {{ font-size: 0.85rem; color: var(--muted); font-style: italic; margin-top: 0.25rem; }}
    .event {{
      border: 1px dashed var(--brand); border-radius: 12px; padding: 0.85rem;
      margin: 0.75rem 0; background: #eef6f5;
    }}
    .ok {{
      background: var(--ok-bg); color: var(--ok); font-weight: 600;
      padding: 0.85rem; border-radius: 12px; margin-bottom: 0.75rem;
    }}
    .jrow {{
      display: flex; justify-content: space-between; gap: 0.75rem;
      padding: 0.65rem 0.85rem; background: var(--ok-bg); border-radius: 8px;
      margin-bottom: 0.4rem; font-weight: 600;
    }}
    .jrow span {{ color: var(--ok); font-variant-numeric: tabular-nums; }}
    .footnote {{ margin-top: 1rem; font-size: 0.8rem; color: var(--muted); }}
    .hidden {{ display: none; }}
    code {{ font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Tudalia</h1>
    <p class="sub">Pre-MVP flow demo · ontology {_esc(ONTOLOGY_VERSION)} · {_esc(VOCABULARY_RELEASE)}</p>
    <div class="steps" id="steps">
      <div class="dot on" data-s="0"></div>
      <div class="dot" data-s="1"></div>
      <div class="dot" data-s="2"></div>
    </div>

    <section class="panel" id="step-pick">
      <h2>1. Raport opiekuna</h2>
      <p class="lead">Wybierz przykładowy zapis głosu (symulacja STT). W produkcji: nagranie → Whisper.</p>
      <div id="samples"></div>
      <button class="btn btn-primary" id="btn-process" disabled>Przetwórz raport</button>
      <p class="footnote">Ekstrakcja jest już zwalidowana przez pakiet <code>tudalia-ontology</code> (nie mock w przeglądarce).</p>
    </section>

    <section class="panel hidden" id="step-confirm">
      <h2>2. Potwierdź raport</h2>
      <p class="lead">Zrozumiałem poniższe. Potwierdzasz? Dopiero wtedy trafia do dziennika.</p>
      <div id="transcript-box" class="meta" style="margin-bottom:1rem"></div>
      <div id="items"></div>
      <div id="events"></div>
      <label id="event-confirm-wrap" class="hidden" style="display:flex;gap:0.5rem;align-items:flex-start;margin:0.75rem 0;">
        <input type="checkbox" id="confirm-event" style="width:20px;height:20px;margin-top:2px" />
        <span>Osobno potwierdzam zdarzenie (np. upadek) — wymagane poza głównym „Potwierdzam”.</span>
      </label>
      <button class="btn btn-primary" id="btn-confirm">Potwierdzam</button>
      <button class="btn btn-secondary" id="btn-back">Wróć</button>
    </section>

    <section class="panel hidden" id="step-journal">
      <h2>3. Zapisano w dzienniku</h2>
      <div class="ok">Raport potwierdzony · nagranie do usunięcia (delete_audio)</div>
      <div id="journal"></div>
      <button class="btn btn-primary" id="btn-reset">Nowy raport</button>
      <p class="footnote">Silnik AI tylko proponuje. Zapis do Senior Journal = po potwierdzeniu opiekuna.</p>
    </section>
  </div>

  <script>
    const SCENARIOS = {data_json};
    let selected = null;
    let step = 0;

    const $ = (id) => document.getElementById(id);
    const samplesEl = $("samples");

    SCENARIOS.forEach((s, i) => {{
      const b = document.createElement("button");
      b.type = "button";
      b.className = "sample";
      b.innerHTML = `<strong>${{s.title_pl}}</strong><small>${{s.transcript.slice(0, 80)}}…</small>`;
      b.onclick = () => {{
        selected = s;
        [...samplesEl.children].forEach(c => c.classList.remove("sel"));
        b.classList.add("sel");
        $("btn-process").disabled = false;
      }};
      if (i === 0) {{ b.click(); }}
      samplesEl.appendChild(b);
    }});

    function setStep(n) {{
      step = n;
      $("step-pick").classList.toggle("hidden", n !== 0);
      $("step-confirm").classList.toggle("hidden", n !== 1);
      $("step-journal").classList.toggle("hidden", n !== 2);
      document.querySelectorAll(".dot").forEach((d, i) => {{
        d.classList.toggle("on", i === n);
        d.classList.toggle("done", i < n);
      }});
    }}

    function fmt(v) {{
      if (typeof v === "boolean") return v ? "tak" : "nie";
      if (v === null || v === undefined) return "—";
      return String(v);
    }}

    $("btn-process").onclick = () => {{
      if (!selected) return;
      $("transcript-box").textContent = "„" + selected.transcript + "”";
      const items = $("items");
      items.innerHTML = "";
      selected.view.items.forEach(it => {{
        const div = document.createElement("div");
        div.className = "item" + ((it.needs_review || it.low_confidence) ? " warn" : "");
        div.innerHTML = `
          <div class="item-top"><span>${{it.label_pl}}</span><span class="tag">${{it.domain}}</span></div>
          <div class="meta">Wartość: <code>${{fmt(it.value)}}</code> · pewność ${{Math.round(it.confidence*100)}}%</div>
          <div class="evidence">„${{it.evidence_span}}”</div>`;
        items.appendChild(div);
      }});
      const ev = $("events");
      ev.innerHTML = "";
      const wrap = $("event-confirm-wrap");
      const events = selected.view.proposed_outcome_events || [];
      if (events.length) {{
        wrap.classList.remove("hidden");
        wrap.style.display = "flex";
        $("confirm-event").checked = false;
        events.forEach(e => {{
          const d = document.createElement("div");
          d.className = "event";
          d.innerHTML = `<strong>Zdarzenie: ${{e.type}}</strong><div class="meta">${{e.description}}</div>
            <div class="evidence">„${{e.evidence_span}}”</div>`;
          ev.appendChild(d);
        }});
      }} else {{
        wrap.classList.add("hidden");
        wrap.style.display = "none";
      }}
      setStep(1);
    }};

    $("btn-back").onclick = () => setStep(0);
    $("btn-reset").onclick = () => setStep(0);

    $("btn-confirm").onclick = () => {{
      const includeEvents = selected.has_events && $("confirm-event").checked;
      const journal = includeEvents ? selected.journal : selected.journal_without_events;
      const box = $("journal");
      box.innerHTML = "";
      journal.entries.forEach(e => {{
        const row = document.createElement("div");
        row.className = "jrow";
        const label = (selected.view.items.find(i => i.concept_code === e.concept_code) || {{}}).label_pl || e.concept_code;
        row.innerHTML = `<strong>${{label}}</strong><span>${{fmt(e.value)}}</span>`;
        box.appendChild(row);
      }});
      (journal.outcome_events || []).forEach(e => {{
        const row = document.createElement("div");
        row.className = "jrow";
        row.innerHTML = `<strong>Zdarzenie: ${{e.type}}</strong><span>potwierdzone</span>`;
        box.appendChild(row);
      }});
      if (!(journal.outcome_events || []).length && selected.has_events) {{
        const note = document.createElement("p");
        note.className = "meta";
        note.textContent = "Upadek nie trafił do dziennika — nie zaznaczono osobnego potwierdzenia zdarzenia.";
        box.appendChild(note);
      }}
      setStep(2);
    }};
  </script>
</body>
</html>
"""
    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    print("Open in browser and click through: transcript → confirm → journal.")


if __name__ == "__main__":
    main()
