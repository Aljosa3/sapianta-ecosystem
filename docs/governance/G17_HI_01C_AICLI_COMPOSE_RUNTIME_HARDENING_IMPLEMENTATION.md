# G17-HI-01C - AiCLI Compose Runtime Hardening Implementation

Status: IMPLEMENTED

Date: 2026-07-09

Final result: AICLI_COMPOSE_RUNTIME_HARDENED

## Summary

This milestone applies the minimal Human Interface hardening identified by G17-HI-01B.

The `./aicli` compose loop remains a thin adapter. It now suppresses repeated compose prompts while a request is being buffered, preserves deterministic submit and cancel behavior, and handles `KeyboardInterrupt` without exposing a Python traceback to the human operator.

No Platform Core, Governance, Replay, PCCL, Provider Platform, or Worker behavior was changed.

## Root Cause Addressed

G17-HI-01B identified that `./aicli` used a line-oriented `input()` loop that rendered `aicli compose>` before each physical terminal read while `compose_buffer` was non-empty.

During line-by-line terminal paste, that prompt could interleave with pasted content and make the interface appear to be repeatedly re-entering compose mode.

The hardened behavior preserves the same input loop and compose buffer lifecycle while rendering a visible prompt only at top-level entry. Buffered compose reads now use an empty prompt.

The same local input boundary now catches `KeyboardInterrupt`, cancels any local compose buffer, records a deterministic interrupt event, and exits cleanly.

## Files Changed

- `aigol/cli/aicli.py`
- `tests/test_g15_aicli_01_compose_runtime_stability.py`
- `docs/governance/G17_HI_01C_AICLI_COMPOSE_RUNTIME_HARDENING_IMPLEMENTATION.md`

## Boundary Preservation Statement

The hardening is limited to Human Interface input collection and presentation.

`./aicli` still does not own:

- semantic interpretation
- Human Intent Resolution
- clarification logic
- Knowledge Reuse
- cognition orchestration
- governance
- replay
- certification
- runtime orchestration
- provider selection
- capability discovery
- proposal lifecycle
- PCCL responsibilities

All semantic and runtime decisions remain delegated to certified Platform Core services through the existing call sites.

## Validation Performed

- `python -m pytest tests/test_g15_aicli_01_compose_runtime_stability.py tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g15_aicli_02_submission_mode.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py -q`
- `git diff --check`

Result: all validation passed.

## Final Result

AICLI_COMPOSE_RUNTIME_HARDENED
