"""
Knowledge-graph relation kinds (ontology contract §7).

These are the typed edges between care-record nodes in Postgres (MVP:
relational tables, not Neo4j). The LLM may propose them; caregiver confirm
persists them.

  DISLIKES         senior → item (lemma), e.g. does not like rosół
  FLAGGED_MISSING  something running out (milk, pads, tablets)
  ORDERED_BY       task → person who asked (family / senior / "doctor" as reported)

Never invent cause→effect links (MAY_CAUSE is out of scope / R&D only).
"""

from enum import Enum


class RelationKind(str, Enum):
    DISLIKES = "DISLIKES"
    FLAGGED_MISSING = "FLAGGED_MISSING"
    ORDERED_BY = "ORDERED_BY"
