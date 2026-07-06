# G14_46_PROVIDER_ATTACHMENT_LEGACY_RETIREMENT_V1

Status: IMPLEMENTED

Final verdict: PROVIDER_ATTACHMENT_LEGACY_RETIRED

## Objective

Complete the G14.44 Provider Platform consolidation by retiring or formally isolating legacy provider attachment implementations without redesigning Platform Core, Runtime Entry, Human Interfaces, Governance, Project Services, Conversation, Provider Runtime, or Certified Provider Attachment.

## Scope Boundary

This milestone only changes legacy provider attachment cleanup and regression coverage.

It does not change the canonical provider architecture:

Platform Core
-> Certified Provider Attachment
-> Provider Runtime
-> Provider Adapter
-> External Provider
-> Worker Platform
-> Replay

## Implementation Report

The production-facing OpenAI external worker adapter now invokes providers through:

`run_certified_provider_attachment(...)`

Evidence:

- `aigol/runtime/openai_external_worker_provider_adapter.py` imports `run_certified_provider_attachment`.
- `run_openai_external_worker_provider_adapter(...)` creates an `OpenAIProviderAdapter`, registers OpenAI provider metadata, and calls the Certified Provider Attachment.
- The external worker replay contract remains compatible: provider capture still records provider status, raw provider text hash, provider evidence hash, fail-closed state, and result package lineage.

No Platform Core, Runtime Entry, Human Interface, Governance, Conversation, Provider Runtime, or Certified Provider Attachment redesign occurred.

## Legacy Component Classification

| Component | Classification | Evidence | Disposition |
|---|---|---|---|
| `aigol/provider/certified_provider_attachment.py` | ACTIVE_CANONICAL | Defines `run_certified_provider_attachment(...)` and records `CERTIFIED_PROVIDER_ATTACHMENT_ARTIFACT_V1`. | Retained as the single production provider attachment boundary. |
| `aigol/provider/provider_runtime.py` | ACTIVE_CANONICAL | Implements provider lookup, readiness, adapter validation, request validation, fail-closed capture, and replay reconstruction beneath the certified boundary. | Retained as Provider Runtime, not a production boundary exposed to callers. |
| `aigol/provider/provider_adapter.py` | ACTIVE_CANONICAL | Defines the provider adapter protocol. | Retained. |
| `aigol/provider/providers/openai_provider.py` | ACTIVE_CANONICAL | Implements the OpenAI provider adapter contract used by Certified Provider Attachment. | Retained. |
| `aigol/runtime/openai_external_worker_provider_adapter.py` | ACTIVE_CANONICAL | Now calls `run_certified_provider_attachment(...)`; no longer imports or calls legacy OpenAI adapter. | Retained as a worker-facing adapter using the canonical provider boundary. |
| `aigol/runtime/provider_attachment.py` | LEGACY_COMPATIBILITY | Marked `LEGACY_PROVIDER_ATTACHMENT_CLASSIFICATION = "LEGACY_COMPATIBILITY"`, `PRODUCTION_PROVIDER_ROUTING_ALLOWED = False`, `CERTIFIED_RUNTIME_REACHABLE = False`. | Retained only for historical REAL_PROVIDER_ATTACHMENT_V1 replay reconstruction and compatibility tests. |
| `aigol/runtime/openai_provider_adapter.py` | LEGACY_COMPATIBILITY | Marked `LEGACY_PROVIDER_ATTACHMENT_CLASSIFICATION = "LEGACY_COMPATIBILITY"`, `PRODUCTION_PROVIDER_ROUTING_ALLOWED = False`, `CERTIFIED_RUNTIME_REACHABLE = False`. | Retained only for historical OPENAI_PROVIDER_ADAPTER_V1 replay reconstruction and compatibility tests. |

No inspected legacy component was classified UNUSED or OBSOLETE, because both legacy modules still have historical replay and regression coverage.

## Legacy Retirement Report

The legacy provider attachment implementations were formally isolated rather than deleted.

Retirement actions:

- Legacy modules now explicitly declare compatibility-only status.
- Production routing from `openai_external_worker_provider_adapter.py` was migrated away from `aigol/runtime/openai_provider_adapter.py`.
- New regression coverage prevents production code from importing or calling legacy attachment paths.
- Historical tests can continue to validate old replay formats without granting those modules production routing authority.

## Production Path Audit

Certified production provider invocation now follows:

Certified Provider Attachment
-> Provider Runtime
-> Provider Adapter
-> External Provider

Implementation evidence:

- `aigol/runtime/openai_external_worker_provider_adapter.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/provider_assisted_intent_classification.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/provider_assisted_conversation_runtime.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/provider_proposal_production_runtime.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/provider_proposal_repair_and_retry_runtime.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/domain_execution_binding_runtime.py` calls `run_certified_provider_attachment(...)`.
- `aigol/runtime/multi_provider_competitive_proposal_runtime.py` calls `run_certified_provider_attachment(...)`.
- `aigol/cli/commands/run_governed.py` calls `run_certified_provider_attachment(...)`.

Regression evidence:

- `tests/test_g14_46_provider_attachment_legacy_retirement_v1.py` scans production `aigol` sources and rejects imports or calls to:
  - `aigol.runtime.provider_attachment`
  - `aigol.runtime.openai_provider_adapter`
  - `attach_real_provider_response(...)`
  - `invoke_openai_provider_adapter(...)`
- The same test confirms no production caller invokes `run_provider_attachment(...)` directly outside Provider Runtime and Certified Provider Attachment.
- The same test confirms the repository has exactly one production provider attachment boundary definition: `aigol/provider/certified_provider_attachment.py`.

## Compatibility Assessment

Compatibility-only code remains for replay safety, not production routing.

Retained compatibility surfaces:

- REAL_PROVIDER_ATTACHMENT_V1 replay reconstruction.
- OPENAI_PROVIDER_ADAPTER_V1 replay reconstruction.
- Historical regression tests for fail-closed behavior, replay determinism, append-only protection, and authority separation.

These compatibility modules have:

- no production routing authority;
- no certified runtime reachability;
- no standing as production provider attachment boundaries.

## Regression Report

Added:

`tests/test_g14_46_provider_attachment_legacy_retirement_v1.py`

Coverage proves:

- legacy modules are explicitly compatibility-only;
- production code cannot import legacy provider attachment paths;
- production code cannot invoke legacy attachment functions;
- production provider invocation goes through Certified Provider Attachment;
- the OpenAI external worker adapter no longer uses legacy OpenAI provider attachment;
- the repository has exactly one production provider attachment boundary.

## Governance Report

The milestone preserves:

- fail-closed provider semantics;
- replay-visible provider evidence;
- provider adapter substitutability;
- Certified Provider Attachment as the single production provider boundary;
- Provider Runtime as the internal runtime below the certified boundary;
- historical replay compatibility without granting legacy modules production authority.

Repository-wide provider boundary status is architecturally clean for G14.46.

This makes the project eligible for repository-wide:

UNIVERSAL_BOUNDARY_ARCHITECTURE_CERTIFIED

without further Provider Platform refactoring.

