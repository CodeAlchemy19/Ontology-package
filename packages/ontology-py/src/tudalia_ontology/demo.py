"""
CLI demo: walk the ontology flow without STT/LLM.

Simulates LLM JSON → validate → confirm view → journal rows.
Run:  python -m tudalia_ontology.demo
"""

from __future__ import annotations

from .domains import Domain
from .extraction import validate_extraction_safe
from .flow import confirm_to_journal_entries, to_confirm_view
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .vocabulary import get_vocabulary


def main() -> None:
    # 1) Load controlled vocabulary (67 concepts from CSV)
    vocab = get_vocabulary()
    print(f"Tudalia ontology {ONTOLOGY_VERSION} ({VOCABULARY_RELEASE})")
    print(f"Loaded {len(vocab)} concepts from {vocab.source}")
    print(f"Domains: {len(vocab.by_domain)}\n")

    transcript = (
        "Podałam insulinę o czternastej. Zjadła tylko połowę obiadu. "
        "Pomogłam wstać z łóżka."
    )

    # 2) Simulated LLM extraction (in production this comes from the local model)
    raw = {
        "ontology_version": ONTOLOGY_VERSION,
        "vocabulary_release": VOCABULARY_RELEASE,
        "transcript": transcript,
        "items": [
            {
                "concept_code": "medication.given",
                "domain": Domain.LEKI.value,
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
                "domain": Domain.DIETA.value,
                "kind": "observation",
                "value_type": "option",
                "value": "half",
                "attributes": {"meal": "obiad"},
                "evidence_span": "Zjadła tylko połowę obiadu",
                "confidence": 0.91,
                "said_by": "caregiver_observed",
            },
            {
                "concept_code": "mobility.transfer",
                "domain": Domain.MOBILNOSC.value,
                "kind": "observation",
                "value_type": "option",
                "value": "with_help",
                "evidence_span": "Pomogłam wstać z łóżka",
                "confidence": 0.88,
                "said_by": "caregiver_observed",
            },
        ],
        "overall_confidence": 0.91,
    }

    # 3) Ontology gate — reject unknown codes / illegal values
    result, errors = validate_extraction_safe(raw)
    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err['path']}: {err['message']}")
        raise SystemExit(1)

    assert result is not None

    # 4) Shape for caregiver confirm UI (Polish labels)
    view = to_confirm_view(result)
    print("Confirm view:")
    for item in view.items:
        print(f"  • [{item.domain}] {item.label_pl}: {item.value!r}")

    # 5) After Potwierdzam — journal rows (+ delete_audio flag)
    journal = confirm_to_journal_entries(
        care_recipient_id="11111111-1111-1111-1111-111111111111",
        visit_id="22222222-2222-2222-2222-222222222222",
        confirmed_by="caregiver-anna",
        confirmed_at="2026-09-30T12:00:00+00:00",
        observed_at="2026-09-30T12:00:00+00:00",
        extraction=result,
    )
    print(f"\nJournal entries: {len(journal.entries)}")
    print(f"delete_audio: {journal.delete_audio}")
    print("OK")


if __name__ == "__main__":
    main()
