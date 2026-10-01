"""
Hard product / MDR-safety rules encoded as flags.

These are not toggles for production experiments — they document invariants
the extraction schema and DB confirm path must uphold. See also
reference/ontology-contract.md §2 and the product brief red lines.
"""

ONTOLOGY_RULES = {
    # Outcome events are facts stated/confirmed by a human, never model guesses
    "no_inferred_outcome_events": True,
    # No RecordEntry without caregiver confirmation
    "no_record_from_unconfirmed_report": True,
    # Omaha KBS 1–5 (and similar clinical scales) are never auto-assigned
    "no_automatic_kbs_rating": True,
    # Design assumption: delete raw audio after transcript + confirm
    "delete_audio_after_confirm": True,
    # Prefer "needs_review" / abstain over confident wrong structure
    "prefer_abstention_over_hallucination": True,
    # AI service may write transcript + extraction proposal only
    "engine_never_writes_record": True,
    # Every item must point at a transcript span
    "every_item_must_be_grounded": True,
    # No severity, risk, diagnosis, or advice fields in the schema
    "no_severity_scores_or_diagnoses": True,
}
