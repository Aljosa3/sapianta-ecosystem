# G3-04 Phase 4 ACLI UHCL Adapter Rendering V1

Status: runtime extension implemented.

Final verdict: G3_04_PHASE_4_READY

## 1. Executive Summary

The Universal Human Communication Layer is functionally complete for the
current Generation 3 communication scope.

This phase implements ACLI as the first interface adapter consumer of UHCL.
ACLI renders UHCL artifacts into deterministic terminal text and captures human
responses as canonical UHCL confirmation response classes.

The adapter does not generate communication meaning. It does not perform
semantic translation, explanation generation, confirmation logic, provider
orchestration, worker orchestration, governance, replay logic, approval,
authorization, execution, deployment, or repository mutation.

## 2. Files Changed

Runtime:

- `aigol/runtime/acli_uhcl_adapter_rendering.py`

Tests:

- `tests/test_acli_uhcl_adapter_rendering_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_4_ACLI_UHCL_ADAPTER_RENDERING_V1.md`

## 3. Rendering Model

The ACLI adapter now supports deterministic rendering of UHCL artifacts using a
terminal card format.

Supported source artifact families:

- canonical communication artifacts;
- typed communication section artifacts;
- progressive explanation derivation artifacts;
- shared confirmation artifacts;
- Provider/Worker/Product communication binding artifacts;
- recovery guidance artifacts.

Every render artifact records:

- render id;
- source artifact type;
- source artifact hash;
- source artifact replay reference;
- selected communication level;
- terminal format;
- rendered section keys;
- rendered lines;
- rendered text hash;
- adapter render evidence;
- non-authority and no-execution flags.

## 4. Adapter Responsibilities

ACLI owns:

- terminal formatting;
- deterministic terminal card layout;
- communication level selection for rendering;
- capture of raw human input hash;
- mapping of human input to canonical UHCL confirmation response classes;
- adapter render replay evidence.

ACLI does not own:

- communication meaning;
- semantic translation;
- explanation generation;
- confirmation model semantics;
- provider orchestration;
- worker orchestration;
- governance;
- replay reconstruction semantics;
- approval;
- authorization;
- execution;
- deployment;
- repository mutation.

Canonical response classes captured by ACLI:

- `CONFIRMATION`
- `CLARIFICATION`
- `MODIFICATION`
- `REJECTION`
- `CONTINUATION`

Unknown input fails closed rather than inventing adapter-local communication
semantics.

## 5. Replay Impact

ACLI adapter replay records:

- render event ordering;
- response event ordering;
- wrapper replay hash;
- render artifact hash;
- response artifact hash;
- source UHCL artifact hash;
- rendered text hash;
- operator input hash;
- canonical response class;
- no-authority flags.

Replay reconstruction verifies wrapper hashes, event ordering, event hashes,
artifact hashes, and response class membership.

## 6. Compatibility Impact

Existing ACLI operator rendering and confirmation modules remain intact as
compatibility paths.

This phase adds a UHCL-specific adapter path that can be adopted incrementally
by ACLI commands and future interfaces. Existing terminal behavior is not
removed.

## 7. Certification Impact

This phase proves the architecture invariant:

```text
UHCL owns communication meaning.
ACLI owns terminal presentation only.
```

The adapter consumes UHCL artifacts without duplicating reusable communication
logic. It records render evidence separately from UHCL source evidence so replay
can distinguish platform communication meaning from interface presentation.

## 8. Rollback Impact

Rollback is low-risk.

The change adds a new ACLI adapter runtime and tests. Existing UHCL runtime
artifacts and existing ACLI compatibility renderers are unchanged.

Rollback consists of removing:

- `aigol/runtime/acli_uhcl_adapter_rendering.py`;
- `tests/test_acli_uhcl_adapter_rendering_v1.py`;
- this governance document.

## 9. Remaining Work

Remaining UHCL/ACLI work:

1. wire selected ACLI commands to consume UHCL render artifacts;
2. compare old ACLI rendering output against UHCL adapter output;
3. certify compatibility parity;
4. complete final UHCL certification.

## 10. Final Determination

ACLI UHCL adapter rendering is implemented and validated as a deterministic,
presentation-only interface adapter.

Final verdict: G3_04_PHASE_4_READY
