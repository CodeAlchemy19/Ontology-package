from __future__ import annotations

from tudalia_ontology import (
    ONTOLOGY_VERSION,
    Domain,
    get_vocabulary,
    validate_extraction,
    validate_extraction_safe,
    to_confirm_view,
    confirm_to_journal_entries,
)

def test_vocabulary_loads_eight_domains_and_67_concepts():
    vocab = get_vocabulary()
    assert len(vocab) == 67
    assert len(vocab.by_domain) == 8
    assert Domain.LEKI in vocab.by_domain
    assert vocab.get("medication.given") is not None


def test_valid_extraction():
    raw = {
        "ontology_version": ONTOLOGY_VERSION,
        "transcript": "Podałam insulinę o 14:00.",
        "items": [
            {
                "concept_code": "medication.given",
                "domain": "leki",
                "kind": "care_activity",
                "value_type": "time",
                "value": "14:00",
                "care_activity_outcome": "done",
                "evidence_span": "Podałam insulinę o 14:00",
                "confidence": 0.9,
            }
        ],
        "overall_confidence": 0.9,
    }
    result = validate_extraction(raw)
    assert result.items[0].concept_code == "medication.given"
    view = to_confirm_view(result)
    assert view.items[0].label_pl == "Podanie leków"


def test_rejects_unknown_concept():
    raw = {
        "ontology_version": ONTOLOGY_VERSION,
        "transcript": "x",
        "items": [
            {
                "concept_code": "medication.invented",
                "domain": "leki",
                "kind": "observation",
                "value_type": "presence",
                "value": True,
                "evidence_span": "x",
                "confidence": 0.5,
            }
        ],
        "overall_confidence": 0.5,
    }
    result, errors = validate_extraction_safe(raw)
    assert result is None
    assert errors


def test_rejects_ungrounded_item():
    raw = {
        "ontology_version": ONTOLOGY_VERSION,
        "transcript": "test",
        "items": [
            {
                "concept_code": "medication.given",
                "domain": "leki",
                "kind": "care_activity",
                "value_type": "time",
                "value": "14:00",
                "evidence_span": "",
                "confidence": 0.9,
            }
        ],
        "overall_confidence": 0.9,
    }
    result, errors = validate_extraction_safe(raw)
    assert result is None
    assert any("evidence_span" in e["path"] for e in errors)


def test_confirm_to_journal():
    raw = {
        "ontology_version": ONTOLOGY_VERSION,
        "transcript": "Zjadła połowę.",
        "items": [
            {
                "concept_code": "diet.meal_eaten",
                "domain": "dieta",
                "kind": "observation",
                "value_type": "option",
                "value": "half",
                "evidence_span": "Zjadła połowę",
                "confidence": 0.9,
            }
        ],
        "proposed_outcome_events": [
            {
                "type": "fall",
                "human_stated": True,
                "description": "Przewróciła się w łazience",
                "evidence_span": "przewróciła się w łazience",
                "confidence": 0.95,
            }
        ],
        "overall_confidence": 0.9,
    }
    result = validate_extraction(raw)
    journal = confirm_to_journal_entries(
        care_recipient_id="11111111-1111-1111-1111-111111111111",
        visit_id="22222222-2222-2222-2222-222222222222",
        confirmed_by="c1",
        confirmed_at="2026-09-30T12:00:00+00:00",
        observed_at="2026-09-30T12:00:00+00:00",
        extraction=result,
        # fall NOT in confirmed list → not written
    )
    assert len(journal.entries) == 1
    assert journal.outcome_events == []
    assert journal.delete_audio is True

    journal2 = confirm_to_journal_entries(
        care_recipient_id="11111111-1111-1111-1111-111111111111",
        visit_id="22222222-2222-2222-2222-222222222222",
        confirmed_by="c1",
        confirmed_at="2026-09-30T12:00:00+00:00",
        observed_at="2026-09-30T12:00:00+00:00",
        extraction=result,
        confirmed_outcome_event_types=["fall"],
    )
    assert len(journal2.outcome_events) == 1
