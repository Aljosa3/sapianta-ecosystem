# G4-09 PGSP Facade Reuse Audit V1

Status: PGSP FACADE REUSE AUDIT COMPLETE

Final verdict: PGSP_EXISTING_API_SUFFICIENT

## 1. Objective

This audit determines whether PGSP, Platform Governed Session Protocol, needs a
new runtime facade, a lightweight alias, canonical public API naming, or no
implementation changes.

This is an audit-only artifact. It does not implement runtime code, introduce a
facade, add an alias, change G4-02, change G4-04, change G4-05, invoke
providers, execute workers, create approvals, create authorization, deploy
software, mutate repositories, or change replay behavior.

## 2. Audit Conclusion

An additional PGSP runtime layer is not required now.

The reusable PGSP-equivalent runtime already exists as the current G4-04
session runtime over the G4-02 scaffold. G4-05 is the ACLI live adapter
entrypoint into that existing session. The minimum required action is canonical
documentation: identify the existing G4-04 callable as the current canonical
PGSP/LGDS session API for Generation 4 development sessions, and identify G4-05
as an adapter-specific ACLI entrypoint.

A future lightweight alias may be useful when a second adapter or second
specialization needs a stable neutral import name. It should be additive and
delegating only. A new runtime facade that owns behavior would be unnecessary
indirection and would increase duplication risk.

## 3. Runtime Inventory

| Runtime | Public callable / surface | Current responsibility | PGSP finding |
| --- | --- | --- | --- |
| G4-02 governed development loop scaffold | `run_g4_governed_development_loop_scaffold(...)` | Executes the deterministic advisory loop through ACLI input evidence, UBTR, CSA, OCS proposal, governance checkpoint, UHCL, ACLI rendering, human response, advisory execution intent, and replay summary. | Protocol engine substrate; reusable by G4-04. |
| G4-02 replay reconstruction | `reconstruct_g4_governed_development_loop_scaffold_replay(...)` | Reconstructs scaffold replay and nested UBTR/CSA/OCS/UHCL/ACLI evidence. | Existing PGSP replay substrate. |
| G4-04 executable session | `run_g4_first_executable_governed_self_development_session(...)` | Creates a governed session envelope, calls G4-02, records governance and replay fixtures, and returns advisory execution intent. | Current canonical PGSP/LGDS session API for Generation 4 development sessions. |
| G4-04 replay reconstruction | `reconstruct_g4_first_executable_self_development_session_replay(...)` | Reconstructs top-level session replay and nested G4-02 replay. | Existing PGSP session replay API. |
| G4-05 live ACLI entrypoint | `run_g4_live_acli_governed_development_session_entrypoint(...)` | Captures live ACLI request/response, creates routing evidence, calls G4-04 unchanged, and binds nested replay. | Adapter-specific ACLI PGSP entrypoint. |
| G4-05 replay reconstruction | `reconstruct_g4_live_acli_governed_development_session_entrypoint_replay(...)` | Reconstructs live ACLI routing evidence and nested G4-04 replay. | Adapter replay API, not neutral PGSP core. |
| G4-05 CLI command | `aigol g4-live-session` | User-facing ACLI command for the first live development session. | ACLI productized entrypoint; not neutral facade. |

## 4. Public API Assessment

The current public API already separates the key responsibilities:

- G4-02 is the protocol engine substrate.
- G4-04 is the reusable governed session API.
- G4-05 is the live ACLI adapter API.
- Replay reconstruction APIs exist at each layer.

The naming is not fully canonical, but the callable structure is already
sufficient for the current certified scope. A facade that only calls G4-04 would
not add behavior, safety, replay coverage, or governance coverage.

Current canonical documentation mapping:

| PGSP concept | Current public API |
| --- | --- |
| PGSP/LGDS session execution | `run_g4_first_executable_governed_self_development_session(...)` |
| PGSP/LGDS session replay | `reconstruct_g4_first_executable_self_development_session_replay(...)` |
| PGSP development loop substrate | `run_g4_governed_development_loop_scaffold(...)` |
| ACLI adapter entrypoint | `run_g4_live_acli_governed_development_session_entrypoint(...)` |
| ACLI operator command | `aigol g4-live-session` |

## 5. Facade Necessity Assessment

### Does a reusable PGSP runtime already exist?

Yes. G4-04 is the current reusable PGSP/LGDS session runtime. It is already
parameterized by session id, operator request, operator response, timestamp, and
replay directory. It calls G4-02 and reconstructs nested replay evidence.

### Can current entrypoints simply be documented as canonical PGSP API?

Yes, for the current Generation 4 development-session scope. Documentation is
enough to prevent a duplicate runtime and to guide future adapters toward G4-04
rather than copying G4-05.

### Would a facade introduce unnecessary indirection?

Yes, if introduced before a second adapter or second specialization exists. A
pure pass-through wrapper would add another name, artifact surface, and testing
burden without increasing governance safety.

### Would a facade improve future Web/REST/Voice/Mobile integration?

Eventually, yes. Once a second adapter is implemented, a lightweight neutral
alias can reduce adapter coupling to G4-04 self-development naming. That alias
should delegate without adding semantics or replay behavior.

### What is the minimum implementation required?

No implementation is required now. The minimum action is canonical API
documentation.

Future minimum, when justified:

- add a lightweight neutral alias module or function;
- delegate directly to G4-04;
- preserve G4-04 and G4-05 replay behavior;
- add targeted alias tests only.

## 6. Duplication Analysis

| Proposed addition | Duplication risk | Assessment |
| --- | --- | --- |
| New PGSP runtime engine | High | Would duplicate G4-02/G4-04 flow, replay, governance, and advisory intent semantics. |
| Runtime facade with new artifacts | Medium to high | Could fragment replay evidence and create another lifecycle layer. |
| Lightweight alias with no new artifacts | Low | Useful later if multiple adapters need a neutral import name. |
| Documentation-only canonical API naming | Lowest | Sufficient now and preserves certified behavior. |

Risk details:

- A behavior-owning facade could drift from G4-04.
- A facade with its own replay artifacts could create redundant evidence.
- Adapter authors may treat the facade as a new owner unless boundaries are
  documented.
- Public API documentation avoids these risks while preserving future optional
  aliasing.

## 7. Recommendation

Recommendation:

`PGSP_EXISTING_API_SUFFICIENT`

Current canonical API:

- use G4-04 as the canonical PGSP/LGDS session API for Generation 4 governed
  development sessions;
- use G4-05 only as the ACLI adapter entrypoint;
- use G4-02 only as the scaffold/protocol engine substrate;
- document future adapters as callers of the G4-04 session API unless and until
  a lightweight neutral alias is justified.

No new runtime facade should be created in the next batch.

## 8. Migration Impact

Migration impact is none.

No files need to move. No runtime names need to change. No replay artifacts need
to be rewritten. No tests need to change. Existing G4-02, G4-04, and G4-05
lineage remains canonical for Generation 4.

Future additive migration may add a neutral import alias, but only after a
second adapter or second PGSP specialization creates real naming friction.

## 9. Compatibility Impact

Compatibility impact is none for this audit.

The following remain unchanged:

- `run_g4_governed_development_loop_scaffold(...)`;
- `run_g4_first_executable_governed_self_development_session(...)`;
- `run_g4_live_acli_governed_development_session_entrypoint(...)`;
- all existing replay reconstruction functions;
- `aigol g4-live-session`;
- G4-02, G4-04, and G4-05 governance artifacts and evidence semantics.

## 10. Revised Next Implementation Batch

Recommended next batch:

`G4_10_PGSP_PUBLIC_API_DOCUMENTATION_AND_ADAPTER_CONTRACT_V1`

Scope:

- document the canonical PGSP public API mapping;
- document adapter invocation requirements for future Web/REST/Voice/Mobile
  adapters;
- document LGDS as the current development specialization using G4-04;
- avoid runtime aliases until a second adapter or specialization requires one.

Validation:

- `git diff --check`;
- no runtime tests unless code is changed.

## 11. Final Determination

PGSP does not currently need a new runtime facade.

The existing G4-04 session runtime is sufficient as the current PGSP/LGDS
session API. G4-05 is correctly scoped as the ACLI adapter entrypoint. G4-02 is
correctly scoped as the protocol engine substrate.

The correct next step is public API documentation and adapter contract
clarification, not a runtime facade.

Final verdict: PGSP_EXISTING_API_SUFFICIENT
