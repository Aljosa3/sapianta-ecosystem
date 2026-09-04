#!/usr/bin/env python3
"""Write the sealed canonical HV reduction; never invoke an operation."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
AUDITOR_PATH = Path(__file__).with_name(
    "G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_AUDITOR_V1.py"
)
OUTPUT = ROOT / (
    ".github/governance/evidence/"
    "g77_256hv_wrong_contract_checkout_bootstrap_correction_v1/"
    "G77_256HV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)


def load_auditor():
    specification = importlib.util.spec_from_file_location("g77_256hv_auditor", AUDITOR_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("HV_AUDITOR_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules["g77_256hv_auditor"] = module
    specification.loader.exec_module(module)
    return module


def main() -> int:
    auditor = load_auditor()
    reduction = auditor.terminal_reduction(ROOT)
    envelope = {
        "schema_id": "G77_256HV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(auditor.canonical_bytes(reduction)).hexdigest(),
    }
    OUTPUT.write_bytes(auditor.canonical_bytes(envelope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
