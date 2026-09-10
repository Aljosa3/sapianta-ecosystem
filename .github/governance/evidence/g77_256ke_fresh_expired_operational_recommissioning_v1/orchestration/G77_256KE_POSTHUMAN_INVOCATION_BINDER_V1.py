#!/usr/bin/env python3
"""Bind a future KE Human handoff through the sole JZ-owned FM route.

This module is inert in Phase A. It accepts paths, never an authority digest,
delegates digest derivation and validation to the existing FM owner, starts no
process, and consumes no authority.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)


def load_fm() -> ModuleType:
    specification = importlib.util.spec_from_file_location("g77_256ke_jz_fm", FM_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("JZ FM owner unavailable")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


FM = load_fm()


def bind_posthuman_invocation(
    *,
    operation_context: Path,
    live_candidate_binding: Path,
    execution_authority: Path,
) -> dict[str, Any]:
    """Return the validated JZ binding; no caller/provider digest is accepted."""

    envelope = FM.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=operation_context,
        live_candidate_binding=live_candidate_binding,
        execution_authority=execution_authority,
    )
    FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=operation_context,
        live_candidate_binding=live_candidate_binding,
        execution_authority=execution_authority,
        envelope=envelope,
    )
    return envelope
