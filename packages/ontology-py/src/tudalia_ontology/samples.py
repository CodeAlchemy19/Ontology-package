"""
Sample caregiver scenarios for demos (pre-MVP — stands in for Whisper+LLM).

Each sample's `raw` extraction is validated against the real ontology when
building client HTML or running the CLI demo.
"""

from __future__ import annotations

from .domains import Domain
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE

SAMPLES: list[dict] = [
    {
        "id": "insulin-lunch",
        "title_pl": "Insulina + obiad + wstawanie",
        "title_en": "Insulin + lunch + transfer",
        "transcript": (
            "Podałam insulinę o czternastej. Zjadła tylko połowę obiadu. "
            "Pomogłam wstać z łóżka."
        ),
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": (
                "Podałam insulinę o czternastej. Zjadła tylko połowę obiadu. "
                "Pomogłam wstać z łóżka."
            ),
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
        },
    },
    {
        "id": "mood-hygiene",
        "title_pl": "Nastrój + kąpiel + zakupy",
        "title_en": "Mood + bathing + shopping",
        "transcript": (
            "Była w dobrym humorze. Umyłam ją wieczorem. Zrobiłam zakupy."
        ),
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": (
                "Była w dobrym humorze. Umyłam ją wieczorem. Zrobiłam zakupy."
            ),
            "items": [
                {
                    "concept_code": "mood.mood",
                    "domain": Domain.PSYCHIKA.value,
                    "kind": "observation",
                    "value_type": "option",
                    "value": "good_spirits",
                    "evidence_span": "Była w dobrym humorze",
                    "confidence": 0.9,
                    "said_by": "caregiver_observed",
                },
                {
                    "concept_code": "hygiene.bathing",
                    "domain": Domain.HIGIENA.value,
                    "kind": "care_activity",
                    "value_type": "option",
                    "value": "done_by_caregiver",
                    "care_activity_outcome": "done",
                    "evidence_span": "Umyłam ją wieczorem",
                    "confidence": 0.92,
                    "said_by": "caregiver_observed",
                },
                {
                    "concept_code": "affairs.shopping_done",
                    "domain": Domain.LOGISTYKA.value,
                    "kind": "care_activity",
                    "value_type": "presence",
                    "value": True,
                    "care_activity_outcome": "done",
                    "evidence_span": "Zrobiłam zakupy",
                    "confidence": 0.93,
                    "said_by": "caregiver_observed",
                },
            ],
            "overall_confidence": 0.92,
        },
    },
    {
        "id": "sleep-pain-fall",
        "title_pl": "Sen + ból + upadek (osobne potwierdzenie)",
        "title_en": "Sleep + pain + fall (separate event confirm)",
        "transcript": (
            "Spała dobrze. Skarżyła się na ból w biodrze. "
            "Mówiła, że wczoraj wieczorem przewróciła się w łazience, sama wstała."
        ),
        "raw": {
            "ontology_version": ONTOLOGY_VERSION,
            "vocabulary_release": VOCABULARY_RELEASE,
            "transcript": (
                "Spała dobrze. Skarżyła się na ból w biodrze. "
                "Mówiła, że wczoraj wieczorem przewróciła się w łazience, sama wstała."
            ),
            "items": [
                {
                    "concept_code": "condition.sleep",
                    "domain": Domain.STAN_FIZYCZNY.value,
                    "kind": "observation",
                    "value_type": "option",
                    "value": "slept_well",
                    "evidence_span": "Spała dobrze",
                    "confidence": 0.9,
                    "said_by": "caregiver_observed",
                },
                {
                    "concept_code": "condition.pain",
                    "domain": Domain.STAN_FIZYCZNY.value,
                    "kind": "observation",
                    "value_type": "presence",
                    "value": True,
                    "body_site": "biodro",
                    "evidence_span": "ból w biodrze",
                    "confidence": 0.87,
                    "said_by": "senior_reported",
                },
            ],
            "proposed_outcome_events": [
                {
                    "type": "fall",
                    "human_stated": True,
                    "description": "Przewróciła się w łazience, sama wstała",
                    "evidence_span": "przewróciła się w łazience, sama wstała",
                    "confidence": 0.95,
                    "said_by": "senior_reported",
                    "details": {
                        "place": "łazienka",
                        "got_up_unaided": True,
                    },
                }
            ],
            "overall_confidence": 0.9,
        },
    },
]
