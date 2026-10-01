# Tudalia Care Ontology (Python)

Machine-readable care vocabulary for the AI engine:

**voice → STT → LLM → `validate_extraction()` → caregiver confirm → Senior Journal**

The engine only **proposes**. It never writes the care record by itself.

| | |
|---|---|
| Vocabulary | `data/vocabulary-v0.2.csv` (also `../../reference/vocabulary-v0.2.csv`) |
| Contract | `../../reference/ontology-contract.md` |
| Version | **0.2.0** · vocabulary **2026.09.30-v0.2** |

---

## What it is

A controlled dictionary of care: fixed codes for what can be stored after a visit.

```
8 domains → subdomain → concept (67 in v0.2) → value type + options / units
```

| Domain | CSV key | Meaning |
|---|---|---|
| `stan_fizyczny` | `condition` | Pain, sleep, vitals, skin… |
| `psychika` | `mood` | Mood, memory, social life |
| `leki` | `medication` | Giving / taking / missing meds |
| `dieta` | `diet` | Meals, fluids, appetite |
| `higiena` | `hygiene` | Bathing, dressing, toileting |
| `mobilnosc` | `mobility` | Walking, transfers, balance |
| `dom` | `home` | Housework, hazards |
| `logistyka` | `affairs` | Shopping, appointments, paperwork |

| Kind | Meaning |
|---|---|
| `observation` | About the senior (“ate half of lunch”) |
| `care_activity` | What the caregiver did (“I gave insulin”) |
| `outcome_event` | Rare labels (fall, hospital…) — separate human confirm |

**Rules:** no diagnosis, no severity scores, no auto KBS; every item needs transcript `evidence_span`; audio deleted after confirm.

Optional CSV mappings (never scored in MVP): `omaha_problem`, `icf_ref`, `katz_lawton`.  
Graph edges: `DISLIKES` · `FLAGGED_MISSING` · `ORDERED_BY`.

---

## Setup

```bash
cd packages/ontology-py
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Use the venv’s Python after activate (`python`, or `.venv/bin/python` if `python` is missing).

---

## Run demos

```bash
# Valid / invalid concept objects (prints INPUT + OUTPUT)
python examples/validate_objects.py

# Same objects as pytest
pytest tests/test_validate_examples.py -v

# CLI walkthrough of one sample extraction
python -m tudalia_ontology.demo

# List all 67 concepts by domain
python -m tudalia_ontology.list_vocab

# Live browser playground → http://127.0.0.1:8765
python -m tudalia_ontology.validate_playground

# HTML: vocabulary tables / clickable flow
python -m tudalia_ontology.export_html        # → dist/ontology-0.2.0.html
python -m tudalia_ontology.export_flow_demo   # → dist/flow-demo-0.2.0.html
```

Validate your own JSON file:

```bash
python examples/validate_objects.py path/to/extraction.json
```

---

## Example: valid / invalid objects

Script: `examples/validate_objects.py` — prints the input concept object, then `VALID` / `INVALID`.

**Valid**

```python
from tudalia_ontology import ONTOLOGY_VERSION, VOCABULARY_RELEASE, validate_extraction_safe

raw = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Podałam insulinę o czternastej. Zjadła tylko połowę obiadu.",
    "items": [
        {
            "concept_code": "medication.given",
            "domain": "leki",
            "kind": "care_activity",
            "value_type": "time",
            "value": "14:00",
            "attributes": {"name": "insulina"},
            "care_activity_outcome": "done",
            "evidence_span": "Podałam insulinę o czternastej",
            "confidence": 0.94,
            "said_by": "caregiver_observed",
        },
        {
            "concept_code": "diet.meal_eaten",
            "domain": "dieta",
            "kind": "observation",
            "value_type": "option",
            "value": "half",
            "attributes": {"meal": "obiad"},
            "evidence_span": "Zjadła tylko połowę obiadu",
            "confidence": 0.91,
            "said_by": "caregiver_observed",
        },
    ],
    "overall_confidence": 0.92,
}

result, errors = validate_extraction_safe(raw)
# result is set, errors == []
```

Example result (`python examples/validate_objects.py`):

```text
INPUT (concept items):
  [0] {"concept_code": "medication.given", "domain": "leki", "kind": "care_activity",
       "value_type": "time", "value": "14:00", "attributes": {"name": "insulina"},
       "care_activity_outcome": "done",
       "evidence_span": "Podałam insulinę o czternastej", "confidence": 0.94,
       "said_by": "caregiver_observed"}
  [1] {"concept_code": "diet.meal_eaten", "domain": "dieta", "kind": "observation",
       "value_type": "option", "value": "half", "attributes": {"meal": "obiad"},
       "evidence_span": "Zjadła tylko połowę obiadu", "confidence": 0.91,
       "said_by": "caregiver_observed"}

OUTPUT: VALID ✓
  items: 2
    • concept=medication.given  domain=leki  value='14:00'  kind=care_activity
    • concept=diet.meal_eaten  domain=dieta  value='half'  kind=observation
```

**Invalid** (bad option — not in closed list)

```python
raw = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Zjadła prawie wszystko.",
    "items": [
        {
            "concept_code": "diet.meal_eaten",
            "domain": "dieta",
            "kind": "observation",
            "value_type": "option",
            "value": "almost_all",  # not allowed
            "evidence_span": "Zjadła prawie wszystko",
            "confidence": 0.8,
        }
    ],
    "overall_confidence": 0.8,
}

result, errors = validate_extraction_safe(raw)
# result is None; errors explain the failure
```

Example result:

```text
INPUT (concept items):
  [0] {"concept_code": "diet.meal_eaten", "domain": "dieta", "kind": "observation",
       "value_type": "option", "value": "almost_all",
       "evidence_span": "Zjadła prawie wszystko", "confidence": 0.8}

OUTPUT: INVALID ✗
  • items.0: Value error, Option "almost_all" not in none, little, half, most, all
```

Other invalid cases in the script / tests: unknown `concept_code`, domain mismatch, empty `evidence_span`.

---

## Example: validate → confirm → journal

```python
from tudalia_ontology import (
    validate_extraction,
    to_confirm_view,
    confirm_to_journal_entries,
)

result = validate_extraction(raw)  # raises if illegal
view = to_confirm_view(result)
for item in view.items:
    print(item.label_pl, item.value, item.domain)

journal = confirm_to_journal_entries(
    care_recipient_id="11111111-1111-1111-1111-111111111111",
    visit_id="22222222-2222-2222-2222-222222222222",
    confirmed_by="caregiver-anna",
    confirmed_at="2026-09-30T12:00:00+00:00",
    observed_at="2026-09-30T12:00:00+00:00",
    extraction=result,
)
print(len(journal.entries), "entries; delete_audio =", journal.delete_audio)
```

Browse vocabulary:

```python
from tudalia_ontology import get_vocabulary, DOMAINS

vocab = get_vocabulary()
for d in DOMAINS:
    print(d.label_pl, len(vocab.by_domain.get(d.code, ())))
```

---

## Extend the ontology

Grow from real caregiver speech — do not invent hundreds of terms up front.

1. Domains/rules are fixed (`ontology-contract.md`, `rules.py`).
2. Edit `reference/vocabulary-v0.2.csv` (or `data/vocabulary-v0.2.csv`). One row = one concept.
3. Versioning: **add** concept → new release; **change meaning** → new code + deprecate old. Bump `ONTOLOGY_VERSION` / `VOCABULARY_RELEASE` in `version.py`.
4. Reload: `pytest` · `python -m tudalia_ontology.list_vocab` · export HTML demos.

| Column | Example |
|---|---|
| `code` | `medication.given` |
| `domain` | `medication` (CSV key) |
| `label_pl` | `Podanie leków` |
| `kind` | `observation` / `care_activity` |
| `value_type` | `presence` / `option` / `quantity` / `text` / `time` / `date` |
| `options_or_unit` | `half;most;all` or `kg` |

---

## Package layout

| Path | Role |
|---|---|
| `src/tudalia_ontology/` | Package (vocabulary, extraction, flow, demos) |
| `examples/validate_objects.py` | Print INPUT concept objects + VALID/INVALID |
| `tests/test_validate_examples.py` | pytest for valid / invalid objects |
| `data/vocabulary-v0.2.csv` | Bundled vocabulary |
| `dist/*.html` | Generated client pages |
