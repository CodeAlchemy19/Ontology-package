"""
Ontology / vocabulary version stamps.

Every extraction and every journal row must remember which vocabulary
classified it (contract §13). Never silently change a concept's meaning —
add a new code and deprecate the old one instead.
"""

# Semver for this Python package + extraction schema shape
ONTOLOGY_VERSION = "0.2.0"

# Human-readable release id pinned on recorded items (YYYY.MM.DD-vX)
VOCABULARY_RELEASE = "2026.09.30-v0.2"
