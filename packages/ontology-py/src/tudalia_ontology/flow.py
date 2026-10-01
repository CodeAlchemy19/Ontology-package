"""
Confirm-screen helpers and journal materialisation.

Typical app/engine order after LLM output:
  1. validate_extraction(raw)       — ontology gate
  2. to_confirm_view(result)        — Polish labels for caregiver UI
  3. caregiver taps Potwierdzam
  4. confirm_to_journal_entries(...) — build RecordEntry rows
  5. DB layer persists + delete audio

This module does not talk to Postgres; it only shapes the confirmed payload.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .extraction import ExtractionResult
from .outcome_events import OutcomeEventType
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .vocabulary import get_vocabulary

# Below this, confirm UI should highlight the item for caregiver attention
LOW_CONFIDENCE = 0.7


class ConfirmItemView(BaseModel):
    """One chip / row on the caregiver confirmation screen."""

    model_config = ConfigDict(extra="forbid")

    concept_code: str
    label_pl: str
    domain: str
    kind: str
    value: Any
    confidence: float
    evidence_span: str
    needs_review: bool
    low_confidence: bool
    review_flags: list[str] = Field(default_factory=list)
    wording: str | None = None
    care_activity_outcome: str | None = None


class ConfirmView(BaseModel):
    """Full payload the ReportConfirmCard / PWA can render."""

    ontology_version: str
    vocabulary_release: str
    transcript: str
    items: list[ConfirmItemView]
    unmapped_spans: list[str]
    proposed_outcome_events: list[dict[str, Any]]
    overall_confidence: float
    requires_attention: bool  # any low-confidence item or proposed event


class RecordEntry(BaseModel):
    """
    One Senior Journal row ready for the DB (after human confirm).

    type is observation | care_activity here; outcome events use OutcomeEventRecord.
    """

    care_recipient_id: str
    visit_id: str
    ontology_version: str
    vocabulary_release: str
    domain: str
    concept_code: str | None
    type: str  # observation | care_activity
    value: Any
    value_secondary: float | None = None
    unit: str | None = None
    attributes: dict[str, Any] | None = None
    wording: str | None = None
    observed_at: str
    source: str = "voice"
    said_by: str | None = None
    evidence_span: str | None = None


class OutcomeEventRecord(BaseModel):
    """Confirmed outcome event — only after separate event confirmation."""

    care_recipient_id: str
    visit_id: str | None = None
    type: OutcomeEventType
    description: str
    confirmed_by: str
    confirmed_at: str
    evidence_span: str | None = None


class ConfirmedJournal(BaseModel):
    """Result of confirm_to_journal_entries — persist then delete audio."""

    ontology_version: str
    vocabulary_release: str
    entries: list[RecordEntry]
    outcome_events: list[OutcomeEventRecord]
    delete_audio: bool = True  # product rule: raw audio must not be retained


def concept_label_pl(code: str) -> str:
    """Polish UI label for a concept code (fallback: the code itself)."""
    concept = get_vocabulary().get(code)
    return concept.label_pl if concept else code


def to_confirm_view(result: ExtractionResult) -> ConfirmView:
    """Turn a validated extraction into caregiver-facing confirm UI data."""
    items: list[ConfirmItemView] = []
    for item in result.items:
        low = item.confidence < LOW_CONFIDENCE
        items.append(
            ConfirmItemView(
                concept_code=item.concept_code,
                label_pl=concept_label_pl(item.concept_code),
                domain=item.domain.value,
                kind=item.kind,
                value=item.value,
                confidence=item.confidence,
                evidence_span=item.evidence_span,
                needs_review=item.needs_review,
                low_confidence=low,
                review_flags=list(item.review_flags),
                wording=item.wording,
                care_activity_outcome=item.care_activity_outcome,
            )
        )

    return ConfirmView(
        ontology_version=result.ontology_version,
        vocabulary_release=result.vocabulary_release,
        transcript=result.transcript,
        items=items,
        unmapped_spans=list(result.unmapped_spans),
        proposed_outcome_events=[
            e.model_dump() for e in result.proposed_outcome_events
        ],
        overall_confidence=result.overall_confidence,
        requires_attention=any(i.needs_review or i.low_confidence for i in items)
        or bool(result.proposed_outcome_events),
    )


def confirm_to_journal_entries(
    *,
    care_recipient_id: str,
    visit_id: str,
    confirmed_by: str,
    confirmed_at: str,
    observed_at: str,
    extraction: ExtractionResult,
    value_overrides: dict[str, Any] | None = None,
    removed_concept_codes: list[str] | None = None,
    confirmed_outcome_event_types: list[str] | None = None,
) -> ConfirmedJournal:
    """
    Materialise Senior Journal rows AFTER caregiver confirmation.

    - value_overrides: edits made on the confirm screen (concept_code → new value)
    - removed_concept_codes: items the caregiver deleted before confirming
    - confirmed_outcome_event_types: events that got their *separate* yes
      (main Potwierdzam alone is not enough for falls/hospital etc.)
    """
    removed = set(removed_concept_codes or [])
    overrides = value_overrides or {}
    confirmed_events = set(confirmed_outcome_event_types or [])

    entries: list[RecordEntry] = []
    for item in extraction.items:
        if item.concept_code in removed:
            continue
        value = overrides.get(item.concept_code, item.value)
        entry_type = (
            "care_activity" if item.kind == "care_activity" else "observation"
        )
        entries.append(
            RecordEntry(
                care_recipient_id=care_recipient_id,
                visit_id=visit_id,
                ontology_version=ONTOLOGY_VERSION,
                vocabulary_release=VOCABULARY_RELEASE,
                domain=item.domain.value,
                concept_code=item.concept_code,
                type=entry_type,
                value=value,
                value_secondary=item.value_secondary,
                unit=item.unit,
                attributes=item.attributes,
                wording=item.wording,
                observed_at=observed_at,
                source="voice",
                said_by=item.said_by,
                evidence_span=item.evidence_span,
            )
        )

    outcome_events: list[OutcomeEventRecord] = []
    for proposed in extraction.proposed_outcome_events:
        if not proposed.human_stated:
            continue
        if proposed.type.value not in confirmed_events:
            # Separate confirmation required — skip unless explicitly listed
            continue
        outcome_events.append(
            OutcomeEventRecord(
                care_recipient_id=care_recipient_id,
                visit_id=visit_id,
                type=proposed.type,
                description=proposed.description,
                confirmed_by=confirmed_by,
                confirmed_at=confirmed_at,
                evidence_span=proposed.evidence_span,
            )
        )

    return ConfirmedJournal(
        ontology_version=ONTOLOGY_VERSION,
        vocabulary_release=VOCABULARY_RELEASE,
        entries=entries,
        outcome_events=outcome_events,
        delete_audio=True,
    )
