"""
Outcome events — human-confirmed labels only (ontology contract §8).

These are training labels for a future predictive model, not routine
observations. Rules:
  - Never inferred from vague speech ("była słaba" is NOT an event)
  - Near-fall → mobility.unsteadiness; actual fall → OutcomeEventType.FALL
  - Each event needs its own confirmation (not the main Potwierdzam alone)
  - No injury assessment or clinical interpretation in the structure

went_missing / care_home_admission are open product items (contract C1).
"""

from enum import Enum


class OutcomeEventType(str, Enum):
    FALL = "fall"
    HOSPITALIZATION = "hospitalization"
    URGENT_VISIT = "urgent_visit"
    INFECTION_DIAGNOSED = "infection_diagnosed"
    WENT_MISSING = "went_missing"  # open C1 — confirm with product + clinician
    CARE_HOME_ADMISSION = "care_home_admission"  # open C1
