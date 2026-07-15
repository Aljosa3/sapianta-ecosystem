# G30-08 Reference AiCLI Final Operational Certification

Status: audit and certification complete.

Verdict: `REFERENCE_AICLI_OPERATIONALLY_CERTIFIED_WITH_OBSERVATIONS`

## Scope

G30-08 certifies the repository-local `./aicli` as the reference thin Human
Interface to the implemented Platform Core, Generation 29, G28, canonical
presentation, and Replay lifecycle.

The audit introduced no runtime, routing, semantic-selection, clarification,
Worker, Provider, Replay, Governance, or Human Interface functionality. No
bounded repair was required. All operational artifacts were created under
`/tmp/g30-08`; test-generated tracked runtime drift was removed after
validation.

The certification does not change the repository's
`PARTIALLY_CONFORMANT` governance status or certify the two known hook-drift
findings.

## Terminal certification matrix

All scenarios were executed on 2026-07-15 through the real `./aicli`
executable. Scenario 10 used a PTY-backed child process and direct SIGINT.

| # | Scenario | Expected boundary | Observed behavior | Result |
|---|---|---|---|---|
| 1 | `What is Platform Core?` | Platform Query Router and read-only knowledge | `PLATFORM_QUERY`, `ARCHITECTURAL_KNOWLEDGE`, `PLATFORM_KNOWLEDGE_RUNTIME`, `PRESENTATION_READY`; no clarification, Provider, Worker, or mutation | Pass |
| 2 | Registered capabilities query | Knowledge route, not default implementation | `PLATFORM_QUERY` and `PLATFORM_KNOWLEDGE_RUNTIME`; `INFORMATIONAL_QUERY`, no implementation classification or invocation | Pass with presentation observation |
| 3 | Runtime status query | Informational runtime evidence | `PLATFORM_QUERY`, read-only Platform Knowledge, `PRESENTATION_READY`; no capability, Provider, Worker, or mutation | Pass with presentation observation |
| 4 | Governed implementation | Summary and human approval boundary | Governed implementation summary; `pending_approval: True`, `approval_count: 0`, no runtime entry or mutation | Pass |
| 5 | Direct `AUDIT_ONLY` | Governed read-only binding | `AUDIT_ONLY`, `GOVERNED_READ_ONLY_WORK_BOUND`, `PLATFORM_KNOWLEDGE_RUNTIME`, `PRESENTATION_READY`; no Provider, Worker, or mutation | Pass |
| 6 | G29 semantic clarification | Owner-specific `input_artifact_family` gap | G29 clarification emitted with no G28 invocation; persisted envelope identifies owner `G29_SEMANTIC_CAPABILITY_SELECTION` and slot `input_artifact_family` | Pass |
| 7 | Valid in-session attachment | Opaque transport through unchanged lifecycle | G29-08 ingress completed; G29-06, Platform Knowledge, G29-04, G28, and presentation completed; no Provider, Worker, or mutation | Pass |
| 8 | Invalid then valid retry | Fail closed, preserve owner/slot, ordered retry | Attempt 1 `FAILED_CLOSED` and `ATTACHMENT_RETRY_ELIGIBLE`; attempt 2 `ATTACHMENT_RETRY_COMPLETED` and `PRESENTATION_READY`; same owner, slot, objective, and envelope | Pass |
| 9 | Cancellation | Consume clarification and reject later attachment | `/cancel` returned canonical cancellation text; later `/attach` reported no active clarification; no continuation or invocation | Pass |
| 10 | Keyboard interruption | Deterministic interruption without approval or execution | Compose wait and pending-clarification wait both returned `REFERENCE_UHI_SESSION_INTERRUPTED`, `KEYBOARD_INTERRUPT`, exit 0, zero approval, and no execution | Pass with timing observation |
| 11 | Replay reconstruction | Complete positive chain and fail-closed tamper checks | Operational turn, Project Context hash, clarification, ingress attempts, G29 selection, Platform Knowledge route, G29-04, G28, and presentation reconstructed; required substitutions and ordering attacks failed closed in regression evidence | Pass |

There were no terminal scenario failures.

## Observed operational evidence

### Informational separation

Scenarios 1 through 3 were classified by the existing Platform Query Router
before governed-development handling:

```text
operational_turn_classification: PLATFORM_QUERY
selected_query_class: ARCHITECTURAL_KNOWLEDGE
selected_service: PLATFORM_KNOWLEDGE_RUNTIME
work_type: INFORMATIONAL_QUERY
presentation_status: PRESENTATION_READY
```

They did not enter the default `IMPLEMENTATION` path. Scenario 5 independently
preserved `AUDIT_ONLY`. Scenario 4 alone produced an approval-gated
implementation summary.

### Attachment completion

The compatible immutable composition-coverage wrapper completed:

```text
G29 clarification
  -> opaque /attach
  -> G29-08 ingress
  -> G29-06 continuation
  -> Platform Knowledge
  -> G29-04 lifecycle
  -> G28 certified invocation
  -> canonical presentation
```

The reconstructed route selected
`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` and reported:

- `CAPABILITY_SELECTED`;
- `SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_COMPLETED`;
- `CERTIFIED_CAPABILITY_INVOCATION_COMPLETED`;
- `PRESENTATION_READY`;
- Provider, Worker, and repository mutation all false.

### Retry continuity

The invalid wrapper was tampered after wrapper hashing. G29-08 rejected it
before semantic continuation. Replay recorded:

1. `ATTACHMENT_RETRY_ELIGIBLE`;
2. `ATTACHMENT_RETRY_COMPLETED`.

Both attempts retained session `G30-08-S8`, owner
`G29_SEMANTIC_CAPABILITY_SELECTION`, semantic slot
`input_artifact_family`, and the same clarification-envelope and Project
Objective lineage.

## Authority ownership

The terminal and Replay evidence confirms:

- AiCLI captures input, transports opaque references, renders Platform Core
  artifacts, and records no semantic decision;
- Platform Core owns query classification, work-type binding, clarification
  semantics, owner and slot continuity, ingress eligibility, capability
  selection, and retry eligibility;
- only explicit human `/approve` can cross the governed implementation
  approval boundary;
- Scenario 4 was deliberately not approved;
- AiCLI reports `aicli_authorizes: False`, `aicli_executes: False`, and
  `aicli_owns_replay: False`;
- no audited scenario granted Worker, Provider, certification, Replay, or
  repository-mutation authority to the Human Interface.

Human Interface neutrality is therefore preserved.

## Replay coverage

Successful reconstruction verified:

- operational turn classification and owner-specific continuation;
- the recorded Project Context artifact hash;
- clarification envelope identity;
- explicit-ingress references and hashes;
- ordered attachment-attempt lineage;
- G29 selection Replay;
- Platform Knowledge evidence;
- G29-04 lifecycle Replay;
- G28 certified invocation Replay;
- canonical presentation hash and completed route.

Existing deterministic G28-G30 regression cases were rerun to verify
fail-closed rejection of:

- owner substitution;
- semantic-slot substitution;
- route tampering;
- ingress-wrapper and ingress-Replay tampering;
- removed or reordered retry attempts;
- attachment substitution;
- selection or presentation lineage substitution.

No invalid artifact influenced semantic selection or invocation.

## Validation results

All commands completed with zero test failures:

- all Generation 30 tests: 37 passed;
- G29 regressions: 59 passed;
- G28 regressions: 14 passed;
- Project Services tests: 4 passed;
- Platform Query Router tests: 8 passed;
- Human Interface tests: 21 passed;
- AiCLI tests: 20 passed;
- clarification tests: 100 passed;
- Replay tests: 245 passed;
- Governance tests: 96 passed;
- full repository suite: 6,166 passed, 4 skipped, 0 failed;
- targeted `py_compile`: passed;
- `git diff --check`: passed.

The full-suite count includes the focused groups and is not an additive total.

## Governance result

The deterministic governance conformance engine returned:

- status: `PARTIALLY_CONFORMANT`;
- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- fail-closed, deterministic, and read-only: true.

Both findings are pre-existing hook drift:

1. root expected and installed pre-commit hooks are missing;
2. the system pre-commit hook lacks `promotion_gate_v02` and
   `check_layer_freeze`.

No new governance finding was introduced by G30-08. These findings do not
invalidate any audited AiCLI operational scenario.

## Observations

### Informational presentation specificity

The registered-capabilities and runtime-status requests route correctly, but
their one-line canonical summaries are less query-specific than a terminal
user may expect. The registered-capabilities response does not enumerate the
registry, and the runtime-status response presents selected certified runtime
evidence rather than a consolidated status view.

This is a canonical presentation-content observation. It is not classifier,
routing, authority, or lifecycle drift and is not an architectural blocker.

### SIGINT timing window

SIGINT delivered while AiCLI is stably awaiting the next compose or
clarification line is handled deterministically with no traceback. A synthetic
signal injected immediately after Enter, during the few instructions that
normalize the returned line rather than during an input wait, can escape the
input-scoped `KeyboardInterrupt` handler and display a traceback.

This narrow robustness observation did not occur in either certified
input-wait scenario and does not authorize, approve, invoke, or mutate
anything. It should be considered for a future bounded Human Interface
hardening milestone, not treated as a new Platform Core responsibility.

## Certification answers

1. AiCLI remains a thin Human Interface: yes.
2. Semantic decisions remain exclusively Platform Core-owned: yes.
3. Clarification ownership is preserved: yes.
4. `input_artifact_family` continuity is preserved: yes.
5. informational, `IMPLEMENTATION`, and `AUDIT_ONLY` work are separated:
   yes.
6. valid attachment completes the certified lifecycle: yes.
7. invalid attachment fails closed and preserves bounded retry: yes.
8. Replay reconstructs the complete workflow: yes.
9. Worker, Provider, authorization, mutation, and certification boundaries
   are preserved: yes.
10. Remaining issues are operational presentation and interruption-hardening
    observations, not architectural blockers.

## Constitutional acceptance scope

Generation 30 is accepted as the operational Human Interface integration and
certification generation for the certified Platform Core semantic capability
runtime. Acceptance covers informational routing, governed implementation
approval boundaries, read-only audit routing, G29 clarification, explicit
canonical artifact ingress, in-session attachment, failed-ingress retry,
canonical presentation, and deterministic Replay reconstruction.

Acceptance does not:

- claim full repository governance conformance;
- resolve or conceal the two hook-drift findings;
- grant AiCLI semantic or execution authority;
- authorize Worker, Provider, or repository mutation;
- add an artifact-discovery or Conversation Layer;
- reopen Generation 29, G28, Replay, Governance, or Platform Core ownership.

## Recommendation

Close Generation 30 with
`REFERENCE_AICLI_OPERATIONALLY_CERTIFIED_WITH_OBSERVATIONS`.

The next major development phase should return to the canonical Product 1
direction: bounded AI Decision Validator enterprise operationalization. Focus
on enterprise-readable decision evidence, audit visualization, explainability,
demo acceptance, and governed release readiness while preserving Replay,
constitutional mutation boundaries, known limitation visibility, and the
existing Human Interface authority model.
