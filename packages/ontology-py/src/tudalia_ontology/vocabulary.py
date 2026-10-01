"""
Controlled vocabulary loaded from vocabulary-v0.2.csv.

This CSV is the source of truth for what the LLM may emit as concept_code.
Each row is one Concept. Standards columns are optional mappings only:
  - omaha_problem  → Omaha System problem name (not KBS scores)
  - icf_ref        → WHO ICF functioning code(s)
  - katz_lawton    → Katz ADL / Lawton IADL coverage tag

Edit the CSV to grow the ontology; then bump VOCABULARY_RELEASE.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from .domains import Domain, domain_from_vocab_key

# observation = about the senior; care_activity = what the caregiver did
ConceptKind = Literal["observation", "care_activity"]

# How the concept's value is represented in extraction JSON
ValueType = Literal["presence", "option", "quantity", "text", "time", "date"]

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VOCABULARY_CSV = _PACKAGE_ROOT / "data" / "vocabulary-v0.2.csv"
# Prefer monorepo reference/ copy when present (single source for the team)
_REFERENCE_CSV = _PACKAGE_ROOT.parents[1] / "reference" / "vocabulary-v0.2.csv"


@dataclass(frozen=True)
class Concept:
    """One leaf in the ontology: domain → subdomain → concept."""

    code: str  # stable id, e.g. medication.given
    domain: Domain  # product code (Polish snake_case)
    domain_vocab_key: str  # English CSV domain key
    subdomain: str  # grouping only; not part of the public UI tree depth
    label_pl: str
    definition: str
    kinds: tuple[ConceptKind, ...]  # some hygiene concepts allow both kinds
    value_types: tuple[ValueType, ...]
    options: tuple[str, ...] | None  # closed list when value_type includes option
    unit: str | None  # UCUM-ish unit when value_type includes quantity
    # --- standard mappings (reference only; never scored) ---
    omaha_problem: str | None
    icf_ref: str | None
    katz_lawton: str | None
    trendable: bool  # safe to show as a simple time series (no thresholds)
    clinician_review: bool  # flag for geriatric consultant before pilot


@dataclass(frozen=True)
class Vocabulary:
    """Indexed view of all concepts for lookup during validation."""

    concepts: tuple[Concept, ...]
    by_code: dict[str, Concept]
    by_domain: dict[Domain, tuple[Concept, ...]]
    source: str  # path loaded from (useful in logs)

    def get(self, code: str) -> Concept | None:
        return self.by_code.get(code)

    def require(self, code: str) -> Concept:
        concept = self.by_code.get(code)
        if concept is None:
            raise KeyError(f"Unknown concept code: {code}")
        return concept

    def __len__(self) -> int:
        return len(self.concepts)


def _parse_pipe_list(raw: str) -> tuple[str, ...]:
    """CSV cells like 'observation|care_activity' or 'quantity|option'."""
    return tuple(part.strip() for part in raw.split("|") if part.strip())


def _parse_options_and_unit(
    value_types: tuple[ValueType, ...],
    options_or_unit: str,
) -> tuple[tuple[str, ...] | None, str | None]:
    """
    Parse the options_or_unit column:
      - option only:          half;most;all
      - quantity only:        kg
      - quantity|option:      mL | little;as_usual;plenty
    """
    trimmed = options_or_unit.strip()
    if not trimmed:
        return None, None

    if "quantity" in value_types and "option" in value_types:
        unit_part, _, option_part = trimmed.partition("|")
        options = tuple(
            o.strip() for o in option_part.split(";") if o.strip()
        ) or None
        unit = unit_part.strip() or None
        return options, unit

    if "option" in value_types:
        return tuple(o.strip() for o in trimmed.split(";") if o.strip()), None

    if "quantity" in value_types:
        return None, trimmed

    return None, None


def _yes(raw: str) -> bool:
    return raw.strip().lower() == "yes"


def load_vocabulary(csv_path: Path | None = None) -> Vocabulary:
    """
    Load and index the controlled vocabulary from CSV.

    Prefer reference/vocabulary-v0.2.csv in the monorepo; fall back to
    packages/ontology-py/data/ for standalone installs.
    """
    path = csv_path
    if path is None:
        if _REFERENCE_CSV.is_file():
            path = _REFERENCE_CSV
        else:
            path = DEFAULT_VOCABULARY_CSV

    concepts: list[Concept] = []
    # utf-8-sig strips a BOM if the spreadsheet exported one
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = {
            "code",
            "domain",
            "subdomain",
            "label_pl",
            "definition",
            "kind",
            "value_type",
            "options_or_unit",
            "omaha_problem",
            "icf_ref",
            "katz_lawton",
            "trendable",
            "clinician_review",
        }
        if reader.fieldnames is None or set(reader.fieldnames) != expected:
            raise ValueError(
                f"Unexpected CSV header in {path}: {reader.fieldnames}"
            )

        seen: set[str] = set()
        for row in reader:
            code = row["code"].strip()
            if not code:
                continue
            if code in seen:
                raise ValueError(f"Duplicate concept code: {code}")
            seen.add(code)

            vocab_key = row["domain"].strip()
            domain_info = domain_from_vocab_key(vocab_key)
            kinds = _parse_pipe_list(row["kind"])
            value_types = _parse_pipe_list(row["value_type"])
            options, unit = _parse_options_and_unit(
                value_types,  # type: ignore[arg-type]
                row.get("options_or_unit") or "",
            )

            concepts.append(
                Concept(
                    code=code,
                    domain=domain_info.code,
                    domain_vocab_key=vocab_key,
                    subdomain=row["subdomain"].strip(),
                    label_pl=row["label_pl"].strip(),
                    definition=row["definition"].strip(),
                    kinds=kinds,  # type: ignore[arg-type]
                    value_types=value_types,  # type: ignore[arg-type]
                    options=options,
                    unit=unit,
                    omaha_problem=(row.get("omaha_problem") or "").strip() or None,
                    icf_ref=(row.get("icf_ref") or "").strip() or None,
                    katz_lawton=(row.get("katz_lawton") or "").strip() or None,
                    trendable=_yes(row.get("trendable") or "no"),
                    clinician_review=_yes(row.get("clinician_review") or "no"),
                )
            )

    by_code = {c.code: c for c in concepts}
    by_domain: dict[Domain, list[Concept]] = {}
    for c in concepts:
        by_domain.setdefault(c.domain, []).append(c)

    return Vocabulary(
        concepts=tuple(concepts),
        by_code=by_code,
        by_domain={k: tuple(v) for k, v in by_domain.items()},
        source=str(path),
    )


@lru_cache(maxsize=1)
def get_vocabulary() -> Vocabulary:
    """Cached vocabulary singleton for validation hot path."""
    return load_vocabulary()
