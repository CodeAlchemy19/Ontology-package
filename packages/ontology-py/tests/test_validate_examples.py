from __future__ import annotations

"""
pytest cases for valid / invalid extraction objects.

Run:
  cd packages/ontology-py
  source .venv/bin/activate
  pytest tests/test_validate_examples.py -v
"""

from tudalia_ontology import (
    ONTOLOGY_VERSION,
    VOCABULARY_RELEASE,
    validate_extraction,
    validate_extraction_safe,
)

VALID = {
    "ontology_version": ONTOLOGY_VERSION,
    "vocabulary_release": VOCABULARY_RELEASE,
    "transcript": "Podałam insulinę o czternastej.",
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
        }
    ],
    "overall_confidence": 0.94,
}

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


def test_valid_object_passes():
    result = validate_extraction(VALID)
    assert result.items[0].concept_code == "medication.given"
    assert result.items[0].value == "14:00"


def test_invalid_unknown_concept():
    result, errors = validate_extraction_safe(INVALID_UNKNOWN_CONCEPT)
    assert result is None
    assert errors
    assert any("concept" in e["message"].lower() or "concept_code" in e["path"] for e in errors)


def test_invalid_domain_mismatch():
    result, errors = validate_extraction_safe(INVALID_DOMAIN_MISMATCH)
    assert result is None
    assert errors


def test_invalid_bad_option():
    result, errors = validate_extraction_safe(INVALID_BAD_OPTION)
    assert result is None
    assert errors


def test_invalid_no_evidence():
    result, errors = validate_extraction_safe(INVALID_NO_EVIDENCE)
    assert result is None
    assert any("evidence_span" in e["path"] for e in errors)
