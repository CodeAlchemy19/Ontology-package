"""
Interactive validation playground for client demos.

Shows:
  - Ready VALID examples → green / pass
  - Ready INVALID examples → red / errors
  - Paste your own JSON → live validate

Run (opens locally):
  python -m tudalia_ontology.validate_playground
  # then open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from .extraction import validate_extraction_safe
from .validate_examples import INVALID_EXAMPLES, VALID_EXAMPLES
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE

HOST = "127.0.0.1"
PORT = 8765


def _run_case(raw: dict) -> dict:
    result, errors = validate_extraction_safe(raw)
    if result is None:
        return {"ok": False, "errors": errors, "summary": None}
    return {
        "ok": True,
        "errors": [],
        "summary": {
            "items": len(result.items),
            "relations": len(result.relations),
            "events": len(result.proposed_outcome_events),
            "overall_confidence": result.overall_confidence,
            "labels": [
                f"{it.concept_code}={it.value!r}" for it in result.items
            ],
        },
    }


def _catalog() -> list[dict]:
    rows: list[dict] = []
    for ex in VALID_EXAMPLES:
        rows.append(
            {
                "id": ex["id"],
                "title": ex["title"],
                "why": ex["why"],
                "expect": "valid",
                "raw": ex["raw"],
                "result": _run_case(ex["raw"]),
            }
        )
    for ex in INVALID_EXAMPLES:
        rows.append(
            {
                "id": ex["id"],
                "title": ex["title"],
                "why": ex["why"],
                "expect": "invalid",
                "raw": ex["raw"],
                "result": _run_case(ex["raw"]),
            }
        )
    return rows


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Tudalia — ontology validation demo</title>
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg:#f3efe6; --surface:#fffdf8; --text:#1c1914; --muted:#5c564c;
      --brand:#0f6b64; --border:#d4cdc0; --ok:#1f6b3a; --ok-bg:#dcefe3;
      --bad:#8a2f24; --bad-bg:#f4d9d4;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; font-family: Figtree, system-ui, sans-serif; color: var(--text);
      background: radial-gradient(900px 400px at 0% 0%, #e4efe9, transparent 55%), var(--bg);
      line-height: 1.45;
    }
    .wrap { max-width: 960px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
    h1 { margin: 0; color: var(--brand); letter-spacing: -0.02em; }
    .sub { color: var(--muted); margin: 0.35rem 0 1.25rem; }
    .grid { display: grid; gap: 1rem; grid-template-columns: 1fr 1fr; }
    @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 14px; padding: 1rem;
    }
    .card h2 { margin: 0 0 0.75rem; font-size: 1.05rem; }
    .ex {
      border: 1px solid var(--border); border-radius: 10px; padding: 0.75rem;
      margin-bottom: 0.6rem; cursor: pointer; background: #faf7f0;
    }
    .ex:hover { border-color: var(--brand); }
    .ex.active { border-color: var(--brand); background: #d7ebe8; }
    .ex strong { display: block; }
    .ex .why { color: var(--muted); font-size: 0.85rem; margin-top: 0.2rem; }
    .badge {
      display: inline-block; font-size: 0.72rem; font-weight: 700;
      padding: 0.15rem 0.5rem; border-radius: 999px; margin-bottom: 0.35rem;
    }
    .badge.ok { background: var(--ok-bg); color: var(--ok); }
    .badge.bad { background: var(--bad-bg); color: var(--bad); }
    textarea {
      width: 100%; min-height: 280px; font-family: ui-monospace, Menlo, monospace;
      font-size: 0.8rem; padding: 0.75rem; border-radius: 10px;
      border: 1px solid var(--border); background: #fff; resize: vertical;
    }
    .btn {
      margin-top: 0.6rem; min-height: 44px; padding: 0 1rem; border: none;
      border-radius: 10px; background: var(--brand); color: #fff;
      font: inherit; font-weight: 600; cursor: pointer;
    }
    .result {
      margin-top: 0.75rem; padding: 0.85rem; border-radius: 10px; font-size: 0.9rem;
    }
    .result.ok { background: var(--ok-bg); color: var(--ok); }
    .result.bad { background: var(--bad-bg); color: var(--bad); }
    .result ul { margin: 0.4rem 0 0; padding-left: 1.1rem; }
    pre {
      margin: 0.5rem 0 0; white-space: pre-wrap; word-break: break-word;
      font-size: 0.78rem; color: var(--text);
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Ontology validation demo</h1>
    <p class="sub">Tudalia v__VERSION__ · vocabulary __RELEASE__ · click an example or paste JSON</p>
    <div class="grid">
      <div class="card">
        <h2>Ready examples</h2>
        <div id="examples"></div>
      </div>
      <div class="card">
        <h2>Input (extraction JSON)</h2>
        <textarea id="input" spellcheck="false"></textarea>
        <button class="btn" id="validate">Validate</button>
        <div id="out"></div>
      </div>
    </div>
  </div>
  <script>
    const CATALOG = __CATALOG__;
    const input = document.getElementById("input");
    const out = document.getElementById("out");
    const box = document.getElementById("examples");

    function showResult(data) {
      if (data.ok) {
        out.className = "result ok";
        out.innerHTML = `<strong>✓ VALID</strong>
          <div>${data.summary.items} item(s) · confidence ${data.summary.overall_confidence}</div>
          <ul>${data.summary.labels.map(l => `<li><code>${l}</code></li>`).join("")}</ul>`;
      } else {
        out.className = "result bad";
        out.innerHTML = `<strong>✗ INVALID</strong>
          <ul>${data.errors.map(e => `<li><code>${e.path}</code>: ${e.message}</li>`).join("")}</ul>`;
      }
    }

    async function validateRaw(rawObj) {
      const res = await fetch("/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rawObj),
      });
      const data = await res.json();
      showResult(data);
    }

    CATALOG.forEach((ex, i) => {
      const div = document.createElement("div");
      div.className = "ex";
      const badge = ex.expect === "valid"
        ? `<span class="badge ok">EXPECTED VALID</span>`
        : `<span class="badge bad">EXPECTED INVALID</span>`;
      const actual = ex.result.ok
        ? `<span class="badge ok">got VALID</span>`
        : `<span class="badge bad">got INVALID</span>`;
      div.innerHTML = `${badge} ${actual}<strong>${ex.title}</strong><div class="why">${ex.why}</div>`;
      div.onclick = () => {
        [...box.children].forEach(c => c.classList.remove("active"));
        div.classList.add("active");
        input.value = JSON.stringify(ex.raw, null, 2);
        showResult(ex.result);
      };
      box.appendChild(div);
      if (i === 0) div.click();
    });

    document.getElementById("validate").onclick = async () => {
      let raw;
      try { raw = JSON.parse(input.value); }
      catch (e) {
        showResult({ ok: false, errors: [{ path: "(json)", message: "Invalid JSON: " + e.message }] });
        return;
      }
      await validateRaw(raw);
    };
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    catalog_json: str = "[]"

    def log_message(self, fmt: str, *args) -> None:  # quieter demo server
        if args and str(args[0]).startswith("POST"):
            super().log_message(fmt, *args)

    def do_GET(self) -> None:
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = (
            PAGE.replace("__VERSION__", ONTOLOGY_VERSION)
            .replace("__RELEASE__", VOCABULARY_RELEASE)
            .replace("__CATALOG__", self.catalog_json)
            .encode("utf-8")
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/validate":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw_bytes = self.rfile.read(length)
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except json.JSONDecodeError as exc:
            data = {
                "ok": False,
                "errors": [{"path": "(json)", "message": str(exc)}],
            }
        else:
            data = _run_case(payload)
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    catalog = _catalog()
    Handler.catalog_json = json.dumps(catalog, ensure_ascii=False)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Ontology validation playground → {url}")
    print("Click VALID / INVALID examples, or paste JSON and press Validate.")
    print("Ctrl+C to stop.")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
