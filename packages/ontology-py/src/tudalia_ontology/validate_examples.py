"""
Curated valid / invalid extraction examples for validation demos.
"""

from __future__ import annotations

from .domains import Domain
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE

# --- VALID -----------------------------------------------------------------

VALID_EXAMPLES: list[dict] = [
    {
        "id": "valid-insulin",
        "title": "Valid — medication given",
        "why": "Known concept, matching domain, grounded evidence, allowed value type.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Podałam insulinę o czternastej.",
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
                }
            ],
            "overall_confidence": 0.94,
        },
    },
    {
        "id": "valid-meal",
        "title": "Valid — meal portion option",
        "why": "Option value `half` is in the closed list for diet.meal_eaten.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Zjadła tylko połowę obiadu.",
            "items": [
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
                }
            ],
            "overall_confidence": 0.91,
        },
    },
]

# --- INVALID ---------------------------------------------------------------

INVALID_EXAMPLES: list[dict] = [
    {
        "id": "invalid-unknown-concept",
        "title": "Invalid — unknown concept_code",
        "why": "LLM invented a code that is not in vocabulary-v0.2.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Podałam insulinę.",
            "items": [
                {
                    "concept_code": "medication.invented_dose",
                    "domain": Domain.LEKI.value,
                    "kind": "care_activity",
                    "value_type": "time",
                    "value": "14:00",
                    "evidence_span": "Podałam insulinę",
                    "confidence": 0.9,
                }
            ],
            "overall_confidence": 0.9,
        },
    },
    {
        "id": "invalid-domain-mismatch",
        "title": "Invalid — domain does not match concept",
        "why": "medication.given belongs to leki, not dieta.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Podałam insulinę.",
            "items": [
                {
                    "concept_code": "medication.given",
                    "domain": Domain.DIETA.value,
                    "kind": "care_activity",
                    "value_type": "time",
                    "value": "14:00",
                    "care_activity_outcome": "done",
                    "evidence_span": "Podałam insulinę",
                    "confidence": 0.9,
                }
            ],
            "overall_confidence": 0.9,
        },
    },
    {
        "id": "invalid-bad-option",
        "title": "Invalid — option not in closed list",
        "why": "`almost_all` is not allowed; vocabulary only has none/little/half/most/all.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Zjadła prawie wszystko.",
            "items": [
                {
                    "concept_code": "diet.meal_eaten",
                    "domain": Domain.DIETA.value,
                    "kind": "observation",
                    "value_type": "option",
                    "value": "almost_all",
                    "evidence_span": "Zjadła prawie wszystko",
                    "confidence": 0.8,
                }
            ],
            "overall_confidence": 0.8,
        },
    },
    {
        "id": "invalid-no-evidence",
        "title": "Invalid — missing grounding (empty evidence_span)",
        "why": "Contract requires every item to point at the transcript.",
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": "Podałam insulinę o 14:00.",
            "items": [
                {
                    "concept_code": "medication.given",
                    "domain": Domain.LEKI.value,
                    "kind": "care_activity",
                    "value_type": "time",
                    "value": "14:00",
                    "care_activity_outcome": "done",
                    "evidence_span": "",
                    "confidence": 0.9,
                }
            ],
            "overall_confidence": 0.9,
        },
    },
]
