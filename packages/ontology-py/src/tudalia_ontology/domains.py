"""
Eight product domains — top level of the Tudalia Care Ontology tree.

Tree: domain → subdomain → concept → value

- `Domain` / `code`: Polish snake_case used in APIs and the Senior Journal
  (e.g. leki, dieta). This is the backend/UI contract.
- `vocab_key`: English key in vocabulary-v0.2.csv (e.g. medication, diet).

Omaha / Katz / Lawton / ICF are *mappings on concepts*, not these domain ids.
"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class Domain(str, Enum):
    """Product-level domain codes (Polish snake_case backend contract)."""

    STAN_FIZYCZNY = "stan_fizyczny"  # physical condition / symptoms / vitals
    PSYCHIKA = "psychika"  # mood, memory, social life
    LEKI = "leki"  # medication
    DIETA = "dieta"  # meals, fluids, appetite
    HIGIENA = "higiena"  # bathing, dressing, toileting
    MOBILNOSC = "mobilnosc"  # walking, transfers, balance
    DOM = "dom"  # home / housework / hazards
    LOGISTYKA = "logistyka"  # shopping, appointments, paperwork (affairs)


class DomainInfo(NamedTuple):
    """One domain with both CSV key and product code."""

    code: Domain  # Polish product code
    vocab_key: str  # English key in the CSV `domain` column
    label_pl: str
    label_en: str


# Fixed set of 8 — changing this is a product/UI decision, not a quiet code edit.
DOMAINS: tuple[DomainInfo, ...] = (
    DomainInfo(Domain.STAN_FIZYCZNY, "condition", "Stan fizyczny", "Physical condition"),
    DomainInfo(Domain.PSYCHIKA, "mood", "Psychika", "Mood & cognition"),
    DomainInfo(Domain.LEKI, "medication", "Leki", "Medication"),
    DomainInfo(Domain.DIETA, "diet", "Dieta", "Diet & nutrition"),
    DomainInfo(Domain.HIGIENA, "hygiene", "Higiena", "Personal hygiene"),
    DomainInfo(Domain.MOBILNOSC, "mobility", "Mobilność", "Mobility"),
    DomainInfo(Domain.DOM, "home", "Dom", "Home environment"),
    DomainInfo(Domain.LOGISTYKA, "affairs", "Logistyka", "Personal affairs / logistics"),
)

DOMAIN_BY_VOCAB_KEY: dict[str, DomainInfo] = {d.vocab_key: d for d in DOMAINS}
DOMAIN_BY_CODE: dict[Domain, DomainInfo] = {d.code: d for d in DOMAINS}


def domain_from_vocab_key(key: str) -> DomainInfo:
    """Map CSV English domain (e.g. 'medication') → product DomainInfo."""
    try:
        return DOMAIN_BY_VOCAB_KEY[key]
    except KeyError as exc:
        raise KeyError(f"Unknown vocabulary domain key: {key}") from exc
