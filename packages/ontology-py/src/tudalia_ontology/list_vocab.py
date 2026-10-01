"""
CLI: print the full controlled vocabulary by domain.

Run:
  python -m tudalia_ontology.list_vocab
  # or after install:
  tudalia-ontology-list
"""

from __future__ import annotations

from .domains import DOMAINS
from .version import ONTOLOGY_VERSION, VOCABULARY_RELEASE
from .vocabulary import get_vocabulary


def main() -> None:
    vocab = get_vocabulary()
    print(f"Tudalia ontology {ONTOLOGY_VERSION} ({VOCABULARY_RELEASE})")
    print(f"{len(vocab)} concepts from {vocab.source}\n")

    for d in DOMAINS:
        concepts = vocab.by_domain.get(d.code, ())
        print(f"=== {d.label_pl} ({d.code}) — {len(concepts)} ===")
        for c in concepts:
            extras: list[str] = []
            if c.options:
                extras.append(f"options={','.join(c.options)}")
            if c.unit:
                extras.append(f"unit={c.unit}")
            if c.omaha_problem:
                extras.append(f"omaha={c.omaha_problem}")
            if c.icf_ref:
                extras.append(f"icf={c.icf_ref}")
            if c.katz_lawton:
                extras.append(c.katz_lawton)
            suffix = f"  [{'; '.join(extras)}]" if extras else ""
            print(f"  {c.code:32} {c.label_pl}{suffix}")
        print()


if __name__ == "__main__":
    main()
