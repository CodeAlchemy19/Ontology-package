#!/usr/bin/env python3
"""
Validate extraction objects against the Tudalia ontology.

Run from packages/ontology-py (with venv active):

  python examples/validate_objects.py

Or validate a custom JSON file:

  python examples/validate_objects.py path/to/extraction.json

Edit YOUR_OBJECT below to try your own payload.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tudalia_ontology import (
    ONTOLOGY_VERSION,
    VOCABULARY_RELEASE,
    validate_extraction_safe,
)

# ---------------------------------------------------------------------------
# Example objects — copy / edit these
# ---------------------------------------------------------------------------

VALID_OBJECT = {
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

# Wrong concept_code — not in vocabulary
INVALID_UNKNOWN_CONCEPT = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Podałam insulinę.",
    "items": [
        {
            "concept_code": "medication.invented_dose",
            "domain": "leki",
            "kind": "care_activity",
            "value_type": "time",
            "value": "14:00",
            "evidence_span": "Podałam insulinę",
            "confidence": 0.9,
        }
    ],
    "overall_confidence": 0.9,
}

# Domain does not match the concept (medication.given → leki, not dieta)
INVALID_DOMAIN_MISMATCH = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Podałam insulinę.",
    "items": [
        {
            "concept_code": "medication.given",
            "domain": "dieta",
            "kind": "care_activity",
            "value_type": "time",
            "value": "14:00",
            "care_activity_outcome": "done",
            "evidence_span": "Podałam insulinę",
            "confidence": 0.9,
        }
    ],
    "overall_confidence": 0.9,
}

# Option value not in the closed list for diet.meal_eaten
INVALID_BAD_OPTION = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Zjadła prawie wszystko.",
    "items": [
        {
            "concept_code": "diet.meal_eaten",
            "domain": "dieta",
            "kind": "observation",
            "value_type": "option",
            "value": "almost_all",
            "evidence_span": "Zjadła prawie wszystko",
            "confidence": 0.8,
        }
    ],
    "overall_confidence": 0.8,
}

# Empty evidence_span — grounding required
INVALID_NO_EVIDENCE = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Podałam insulinę o 14:00.",
    "items": [
        {
            "concept_code": "medication.given",
            "domain": "leki",
            "kind": "care_activity",
            "value_type": "time",
            "value": "14:00",
            "care_activity_outcome": "done",
            "evidence_span": "",
            "confidence": 0.9,
        }
    ],
    "overall_confidence": 0.9,
}

# Paste / edit your own object here, then set RUN_OBJECT = YOUR_OBJECT
YOUR_OBJECT = VALID_OBJECT


def print_result(label: str, raw: dict) -> bool:
    """Validate one object and print input + VALID / INVALID. Returns True if valid."""
    result, errors = validate_extraction_safe(raw)
    print("=" * 60)
    print(label)
    print("-" * 60)

    print("INPUT (full extraction):")
    print(json.dumps(raw, ensure_ascii=False, indent=2))
    print()

    print("INPUT (concept items):")
    for i, item in enumerate(raw.get("items") or []):
        print(f"  [{i}] {json.dumps(item, ensure_ascii=False)}")
    if not raw.get("items"):
        print("  (none)")
    print()

    if result is not None and not errors:
        print("OUTPUT: VALID ✓")
        print(f"  items: {len(result.items)}")
        for item in result.items:
            print(
                f"    • concept={item.concept_code}"
                f"  domain={item.domain}"
                f"  value={item.value!r}"
                f"  kind={item.kind}"
            )
        return True

    print("OUTPUT: INVALID ✗")
    for err in errors:
        print(f"  • {err['path']}: {err['message']}")
    return False


def main() -> int:
    # Optional: python examples/validate_objects.py my.json
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        raw = json.loads(path.read_text(encoding="utf-8"))
        ok = print_result(f"File: {path}", raw)
        return 0 if ok else 1

    # Built-in examples
    cases = [
        ("VALID_OBJECT (expected VALID)", VALID_OBJECT, True),
        ("INVALID_UNKNOWN_CONCEPT (expected INVALID)", INVALID_UNKNOWN_CONCEPT, False),
        ("INVALID_DOMAIN_MISMATCH (expected INVALID)", INVALID_DOMAIN_MISMATCH, False),
        ("INVALID_BAD_OPTION (expected INVALID)", INVALID_BAD_OPTION, False),
        ("INVALID_NO_EVIDENCE (expected INVALID)", INVALID_NO_EVIDENCE, False),
        ("YOUR_OBJECT", YOUR_OBJECT, None),
    ]

    mismatched = 0
    for label, raw, expect_ok in cases:
        ok = print_result(label, raw)
        if expect_ok is not None and ok != expect_ok:
            mismatched += 1
            print(f"  !! unexpected (expected {'VALID' if expect_ok else 'INVALID'})")
        print()

    if mismatched:
        print(f"Done with {mismatched} unexpected result(s).")
        return 1
    print("Done — all expected outcomes matched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
