"""
Pydantic extraction contract for Agent 0 (Ingestor).

Role of this module:
  - Define the JSON shape the local LLM must produce
  - Reject unknown concept codes, wrong domains, illegal options
  - Require grounding (evidence_span) so the confirm UI never shows invented facts

The engine PROPOSES only. Writing to Postgres happens after caregiver confirm
(see flow.confirm_to_journal_entries). Contract: reference/ontology-contract.md §2–3.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from .domains import Domain
from .outcome_events import OutcomeEventType
from .relations import RelationKind
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .vocabulary import ConceptKind, ValueType, get_vocabulary

# --- Closed enums used on every extracted item (contract §3) ---

Presence = Literal["present", "absent"]  # supports negation ("nie bolało")
SaidBy = Literal[
    "caregiver_observed",
    "senior_reported",
    "family_reported",
    "other_reported",
]
TimePrecision = Literal["exact", "hour", "part_of_day", "day", "approximate"]
TimeContext = Literal["during_visit", "since_last_visit", "ongoing"]
# Only if someone actually said a comparison — never inferred
StatedComparison = Literal["less_than_usual", "as_usual", "more_than_usual"]
CareActivityOutcome = Literal[
    "done",
    "partly_done",
    "declined_by_senior",
    "not_needed",
]
# Rule-based flags for the confirm screen (P6); calibrated scores come later
ReviewFlag = Literal[
    "number_heard",
    "time_unresolved",
    "nothing_fits",
    "name_heard",
    "non_polish_words",
    "low_confidence",
]


class ExtractionItem(BaseModel):
    """
    One proposed observation or care activity.

    Must map to a vocabulary concept. Must cite evidence_span from the transcript.
    No severity, diagnosis, or clinical score fields exist here on purpose.
    """

    model_config = ConfigDict(extra="forbid")

    concept_code: str  # e.g. medication.given — must exist in vocabulary
    domain: Domain  # must match the concept's domain
    kind: ConceptKind
    value_type: ValueType
    value: bool | float | int | str | None = None
    value_secondary: float | None = None  # e.g. diastolic BP
    unit: str | None = None
    wording: str | None = Field(
        default=None,
        description="Short text as said / confirmed, Polish surface form",
    )
    language: str = "pl"
    presence: Presence | None = None
    said_by: SaidBy = "caregiver_observed"
    # Time: keep original phrase ("wczoraj wieczorem") + resolved value when possible
    when_resolved: str | None = None
    when_precision: TimePrecision | None = None
    when_original: str | None = None
    time_context: TimeContext | None = None
    duration_original: str | None = None
    body_site: str | None = None  # as said ("biodro"), not coded
    stated_comparison: StatedComparison | None = None
    care_activity_outcome: CareActivityOutcome | None = None
    attributes: dict[str, str | float | bool] | None = None  # name, meal, …
    # Grounding — required (contract §2 rule 4). Empty span → validation error.
    evidence_span: str = Field(min_length=1)
    evidence_start: int | None = None  # optional char offsets into transcript
    evidence_end: int | None = None
    # Extraction confidence only — NEVER a clinical rating / KBS
    confidence: float = Field(ge=0.0, le=1.0)
    needs_review: bool = False
    review_flags: list[ReviewFlag] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_against_vocabulary(self) -> ExtractionItem:
        """Cross-check item against the pinned vocabulary (codes, types, options)."""
        vocab = get_vocabulary()
        concept = vocab.get(self.concept_code)
        if concept is None:
            raise ValueError(f"Unknown concept_code: {self.concept_code}")

        if concept.domain != self.domain:
            raise ValueError(
                f"Domain {self.domain.value} does not match "
                f"{self.concept_code} ({concept.domain.value})"
            )

        if self.kind not in concept.kinds:
            raise ValueError(
                f"Kind {self.kind} not allowed for {self.concept_code}"
            )

        if self.value_type not in concept.value_types:
            raise ValueError(
                f"Value type {self.value_type} not allowed for {self.concept_code}"
            )

        if (
            self.value_type == "option"
            and concept.options
            and isinstance(self.value, str)
            and self.value not in concept.options
        ):
            raise ValueError(
                f'Option "{self.value}" not in {", ".join(concept.options)}'
            )

        if self.value_type == "presence":
            if self.presence is None and not isinstance(self.value, bool):
                raise ValueError(
                    "presence items need presence=present|absent or boolean value"
                )

        if self.value_type == "quantity" and not isinstance(
            self.value, (int, float)
        ):
            raise ValueError("quantity value must be a number")

        # Soft rules: flag for caregiver review instead of hard-failing
        if self.kind == "care_activity" and self.care_activity_outcome is None:
            if "low_confidence" not in self.review_flags:
                self.review_flags = [*self.review_flags, "low_confidence"]
                self.needs_review = True

        if self.confidence < 0.7 and "low_confidence" not in self.review_flags:
            self.review_flags = [*self.review_flags, "low_confidence"]
            self.needs_review = True

        return self


class ExtractionRelation(BaseModel):
    """
    Knowledge-graph edge proposed from speech (contract §7).

    DISLIKES / FLAGGED_MISSING / ORDERED_BY — stored after confirm as relation rows.
    """

    model_config = ConfigDict(extra="forbid")

    kind: RelationKind
    subject: str
    object: str
    object_lemma: str | None = None  # base form, e.g. rosół not rosołu
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_span: str = Field(min_length=1)
    needs_review: bool = False


class ProposedOutcomeEvent(BaseModel):
    """
    Candidate outcome event (fall, hospital, …).

    Never auto-written to the journal. Needs its *own* caregiver confirmation
    (separate from the main Potwierdzam). See flow.confirmed_outcome_event_types.
    """

    model_config = ConfigDict(extra="forbid")

    type: OutcomeEventType
    human_stated: Literal[True] = True  # model must not invent events
    description: str = Field(min_length=1)
    said_by: SaidBy = "senior_reported"
    evidence_span: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_review: bool = True
    details: dict[str, str | bool | None] | None = None


class ExtractionResult(BaseModel):
    """Full Ingestor output for one voice report (or family needs intake)."""

    model_config = ConfigDict(extra="forbid")

    ontology_version: Literal["0.2.0"] = ONTOLOGY_VERSION  # type: ignore[assignment]
    vocabulary_release: str = VOCABULARY_RELEASE
    transcript: str
    items: list[ExtractionItem]
    relations: list[ExtractionRelation] = Field(default_factory=list)
    proposed_outcome_events: list[ProposedOutcomeEvent] = Field(
        default_factory=list
    )
    # Phrases the model could not map — caregiver decides on confirm screen
    unmapped_spans: list[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("items")
    @classmethod
    def drop_ungrounded_is_already_enforced(cls, items: list[ExtractionItem]):
        # evidence_span min_length=1 already rejects empty grounding per item
        return items


def validate_extraction(raw: Any) -> ExtractionResult:
    """
    Validate model JSON against the ontology contract.
    Raises pydantic.ValidationError on failure (use in engine retry loops).
    """
    return ExtractionResult.model_validate(raw)


def validate_extraction_safe(
    raw: Any,
) -> tuple[ExtractionResult | None, list[dict[str, str]]]:
    """Return (result, []) on success, or (None, [{path, message}, ...]) on failure."""
    try:
        return validate_extraction(raw), []
    except ValidationError as exc:
        errors = [
            {
                "path": ".".join(str(p) for p in err.get("loc", ())) or "(root)",
                "message": err.get("msg", "invalid"),
            }
            for err in exc.errors()
        ]
        return None, errors
