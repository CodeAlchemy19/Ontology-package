"""
Tudalia Care Ontology — Python package for the AI extraction engine.

Pipeline position:
  audio → STT → LLM JSON → validate_extraction() → caregiver confirm
  → confirm_to_journal_entries() → Senior Journal (DB write is outside this package)

The engine only *proposes*. It never writes the care record by itself.
See reference/ontology-contract.md for product rules.
"""

from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .domains import Domain, DOMAINS, DOMAIN_BY_VOCAB_KEY, domain_from_vocab_key
from .vocabulary import Concept, Vocabulary, load_vocabulary, get_vocabulary
from .relations import RelationKind
from .outcome_events import OutcomeEventType
from .rules import ONTOLOGY_RULES
from .extraction import (
    ExtractionItem,
    ExtractionRelation,
    ProposedOutcomeEvent,
    ExtractionResult,
    validate_extraction,
    validate_extraction_safe,
    ValidationError,
)
from .flow import (
    ConfirmView,
    ConfirmedJournal,
    to_confirm_view,
    confirm_to_journal_entries,
)

__all__ = [
    "ONTOLOGY_VERSION",
    "VOCABULARY_RELEASE",
    "Domain",
    "DOMAINS",
    "DOMAIN_BY_VOCAB_KEY",
    "domain_from_vocab_key",
    "Concept",
    "Vocabulary",
    "load_vocabulary",
    "get_vocabulary",
    "RelationKind",
    "OutcomeEventType",
    "ONTOLOGY_RULES",
    "ExtractionItem",
    "ExtractionRelation",
    "ProposedOutcomeEvent",
    "ExtractionResult",
    "validate_extraction",
    "validate_extraction_safe",
    "ValidationError",
    "ConfirmView",
    "ConfirmedJournal",
    "to_confirm_view",
    "confirm_to_journal_entries",
]

__version__ = ONTOLOGY_VERSION
