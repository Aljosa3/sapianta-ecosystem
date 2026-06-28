# UBTR HIRR Final Boundary Specification V1

Status: final architectural boundary specification.

Scope: permanent responsibility boundary between Universal Bidirectional Translation Runtime and Human Intent Resolution Runtime.

This artifact does not implement runtime code, modify tests, change routing behavior, retire compatibility layers, or alter governance authority.

## 1. Purpose

Platform Core Generation 1 is certified.

UBTR is beta ready.

Batch 01 and Batch 02 are certified:

- Batch 01: ACLI CSA-first routing subset.
- Batch 02: HIRR ambiguous-intent clarification intake CSA-first subset.

The HIRR post-UBTR responsibility audit concluded:

- HIRR still contains compatibility-era semantic interpretation that should migrate to UBTR.
- HIRR permanently owns lifecycle orchestration and boundary enforcement.

This specification freezes the final permanent architectural boundary between UBTR and HIRR.

## 2. Boundary Rule

UBTR owns meaning.

HIRR owns clarification lifecycle.

CSA is the canonical semantic artifact consumed by HIRR.

HIRR may never independently reinterpret natural language after migration completion, except for compatibility-only rollback paths that remain explicitly documented and replay-visible.

UBTR may never approve, execute, mutate governance, invoke workers, select providers, or replace HIRR lifecycle enforcement.

## 3. Responsibilities Permanently Owned By UBTR

UBTR permanently owns:

1. human natural-language normalization;
2. deterministic semantic interpretation;
3. ambiguity detection;
4. confidence and semantic fidelity evaluation;
5. intent-family semantic identity;
6. domain and entity semantic extraction;
7. requested-action semantic extraction;
8. clarification-required semantic assessment;
9. OCS cognition request creation when deterministic translation is insufficient;
10. integration of OCS cognition result into CSA;
11. Canonical Semantic Artifact generation;
12. Governance -> Human semantic projection when operator-facing explanation is migrated;
13. semantic lineage references and source artifact hashes.

UBTR owns these as semantic evidence only.

UBTR does not own:

- approval;
- execution authorization;
- provider selection;
- worker invocation;
- replay mutation;
- HIRR lifecycle state;
- clarification reply binding;
- supported workflow allowlists;
- governance authority.

## 4. Responsibilities Permanently Owned By HIRR

HIRR permanently owns:

1. clarification-first orchestration;
2. HIRR artifact shape and compatibility contract;
3. CSA consumption validation;
4. clarification request creation from CSA-derived need;
5. active clarification state reconstruction;
6. one-active-clarification invariant;
7. clarification reply binding to the original request;
8. canonical chain identity preservation across clarification turns;
9. clarification response replay hashing;
10. supported target workflow allowlist after clarification;
11. workflow selection after clarification using CSA-derived semantics and HIRR lifecycle rules;
12. unsafe escalation fail-closed enforcement;
13. provider, worker, approval, execution, governance, and replay non-authority assertions;
14. rollback visibility while compatibility layers exist;
15. downstream handoff after clarification resolution.

HIRR owns these even after all semantic markers are retired.

## 5. Shared During Migration Only

The following are shared only while migration is incomplete:

| Responsibility | UBTR Role | HIRR Role | End State |
| --- | --- | --- | --- |
| Intent-family classification | Produce CSA semantic identity | Preserve local marker parity and HIRR artifact shape | UBTR-owned, HIRR consumes CSA |
| Ambiguous-intent intake | Produce ambiguity and clarification-required state | Gate CSA with compatibility parity | UBTR-owned; HIRR lifecycle only |
| Development-intent HIRR classification | Produce development action/domain/entities | Preserve current HIRR compatibility path | UBTR-owned; HIRR consumes CSA |
| Clarification response interpretation | Translate reply and ambiguity reduction | Preserve local refinement until parity | UBTR-owned semantics; HIRR binds and enforces lifecycle |
| Advisory versus governed target meaning | Produce semantic target evidence | Preserve supported target and safety gate | UBTR-owned semantics; HIRR allowlists target |
| Proposal-only after clarification | Produce no-execution/advisory semantics | Preserve OCS/human-confirmation guard | UBTR-owned semantics; HIRR lifecycle and OCS boundary |
| Multilingual semantic interpretation | Normalize and translate multilingual input | Preserve current multilingual marker coverage | UBTR-owned |
| Compatibility parity evidence | Produce CSA source fields | Compare against prior local interpretation | Retired after compatibility retirement |

Shared status is temporary and must be replay-visible.

## 6. Responsibilities That Must Be Retired

The following must be retired after parity certification:

1. HIRR local business-goal semantic markers;
2. HIRR local problem-statement semantic markers;
3. HIRR local automation semantic markers;
4. HIRR local compliance semantic markers;
5. HIRR local general-improvement semantic markers;
6. HIRR local continuation semantic markers;
7. HIRR local bounded file-write proof semantic markers;
8. HIRR local development-intent semantic markers;
9. HIRR unknown-intent semantic fallback where CSA can represent the ambiguity;
10. HIRR clarification-response advisory/governed/bounded-proof semantic marker groups;
11. HIRR proposal-only-after-clarification semantic marker groups;
12. previous-compatibility parity gates for fully retired prompt families.

The following must not be retired:

- HIRR lifecycle state;
- HIRR replay validation;
- HIRR artifact compatibility;
- active clarification reconstruction;
- one-active-clarification invariant;
- reply binding;
- supported target allowlist;
- unsafe escalation fail-closed enforcement;
- non-authority flags;
- rollback visibility for retained compatibility paths.

## 7. Canonical CSA Consumption Contract For HIRR

HIRR may consume CSA only through a validated contract.

Required CSA fields:

| CSA Field | HIRR Use |
| --- | --- |
| `artifact_type` | Confirm canonical semantic artifact type |
| `schema_version` | Confirm supported CSA schema |
| `artifact_hash` | Bind HIRR replay to semantic source |
| `semantic_identity.intent_family` | HIRR intake family or clarification reply family |
| `semantic_identity.domain` | Confirm unknown/domain-specific scope |
| `semantic_identity.requested_actions` | Determine whether action is absent, advisory, create, update, implement, review, or bounded |
| `semantic_identity.entities` | Preserve target entity references |
| `workflow_identity.workflow_id` | Candidate HIRR or downstream workflow |
| `confidence.semantic_confidence` | Determine whether HIRR may consume or must request clarification/fallback |
| `ambiguity.ambiguity_status` | Determine material/unsafe/no ambiguity |
| `clarification_state.clarification_required` | Create or continue clarification lifecycle |
| `clarification_state.clarification_questions` | Candidate questions, subject to HIRR output parity rules |
| `approval_state.approval_required` | Preserve no approval bypass |
| `execution_intent.execution_requested` | Preserve no execution before authorization |
| `provider_projection.provider_invoked` | Must be false for deterministic HIRR intake |
| `worker_projection.worker_invoked` | Must be false for HIRR intake |
| `authority_flags` | Must deny governance, approval, execution, mutation, provider, worker, and replay mutation authority |
| `replay_identity.semantic_replay_reference` | Link HIRR artifact to CSA replay |
| `translation_lineage.translation_artifact_hash` | Link HIRR to UBTR source lineage |

HIRR must fail closed or use documented compatibility fallback when:

- CSA is missing;
- CSA hash is invalid;
- CSA schema is unsupported;
- authority flags grant non-semantic authority;
- CSA requests direct execution;
- CSA indicates provider or worker invocation occurred in a path that must be deterministic;
- CSA workflow candidate is unsupported;
- semantic confidence is insufficient for the target HIRR decision;
- required replay lineage is absent.

## 8. Lifecycle Interaction Between UBTR And HIRR

Final interaction sequence:

```text
Human prompt
  |
  v
UBTR Human -> Governance translation
  |
  v
Canonical Semantic Artifact
  |
  v
HIRR CSA validation
  |
  +--> CSA unsupported / invalid / insufficient
  |       |
  |       v
  |   fail closed or documented compatibility fallback during migration
  |
  v
HIRR clarification intake artifact
  |
  v
HIRR active clarification lifecycle state
  |
  v
Human clarification reply
  |
  v
UBTR translates clarification reply and links original CSA
  |
  v
HIRR binds reply to original clarification request
  |
  v
HIRR validates lifecycle, chain, target allowlist, and unsafe escalation boundary
  |
  v
HIRR selects supported downstream workflow or remains clarification-first
  |
  v
Replay records CSA source, HIRR lifecycle artifacts, and downstream handoff
```

Sequence invariants:

- UBTR precedes HIRR semantic consumption.
- HIRR validates CSA before use.
- HIRR owns lifecycle state after CSA consumption.
- Clarification replies are translated by UBTR for semantic evidence but bound by HIRR for lifecycle continuity.
- HIRR may not select unsupported workflow targets.
- Provider/worker/approval/execution authority remains downstream and explicit.

## 9. Replay Ownership

UBTR owns replay evidence for:

- translation request;
- normalized semantic payload;
- ambiguity and confidence;
- CSA generation;
- OCS cognition request and integration lineage where applicable;
- Governance -> Human projection where applicable.

HIRR owns replay evidence for:

- CSA consumption decision;
- HIRR intake artifact;
- clarification request artifact;
- active clarification state;
- reply binding;
- clarification response hash;
- target refinement lifecycle artifact;
- clarification resolution artifact;
- workflow selection after clarification;
- non-authority assertions;
- compatibility fallback source while migration remains active.

Replay reconstruction must prove:

```text
original human input
-> UBTR translation
-> CSA
-> HIRR consumption or fallback
-> clarification lifecycle
-> reply binding
-> resolution / workflow selection
```

Historical replay must never be reinterpreted after compatibility retirement.

## 10. Governance Ownership

Governance ownership remains outside UBTR and HIRR.

UBTR governance role:

- produce semantic evidence;
- assert non-authority;
- expose ambiguity and confidence;
- preserve translation lineage.

HIRR governance role:

- enforce clarification-first boundaries;
- fail closed on unsafe escalation;
- prevent approval bypass;
- prevent execution inference;
- prevent worker/provider invocation during clarification;
- preserve replay evidence.

Neither UBTR nor HIRR may:

- mutate constitutional governance;
- approve execution;
- bypass human authority;
- certify compliance;
- hide partial migration status.

## 11. Clarification Ownership

UBTR owns semantic clarification meaning:

- whether the original request is ambiguous;
- what ambiguity is present;
- whether a clarification reply reduces ambiguity;
- what semantic target the reply expresses;
- whether advisory/no-execution semantics are present.

HIRR owns clarification lifecycle:

- whether a clarification request is active;
- how the request is represented as HIRR artifact;
- whether a reply is bound to the active request;
- whether a reply belongs to the same chain;
- whether the reply attempts unsafe escalation;
- which supported workflow target may be selected;
- whether clarification remains unresolved.

Final rule:

UBTR can say what the clarification means.

HIRR decides whether that meaning may advance lifecycle state.

## 12. Failure Handling Responsibilities

| Failure | UBTR Responsibility | HIRR Responsibility |
| --- | --- | --- |
| Missing or malformed human input | Fail closed before CSA | No HIRR intake |
| Unknown intent | Produce low-confidence ambiguity CSA | Create clarification intake if CSA valid |
| Unsafe ambiguity | Mark unsafe ambiguity | Fail closed or ask non-bypass clarification |
| Missing CSA | None after UBTR failure | Fail closed or documented migration fallback |
| CSA hash mismatch | None after invalid artifact | Reject CSA and fail closed |
| CSA grants non-semantic authority | Should never emit valid CSA | Reject and fail closed |
| Unsupported workflow candidate | Produce candidate only as semantic evidence | Reject unsupported target |
| Multiple active clarifications | None | Fail closed |
| Clarification reply chain mismatch | None | Fail closed |
| Reply attempts approval bypass or worker invocation | Mark unsafe when translated | HIRR fail-closed enforcement remains mandatory |
| Provider unavailable during UBTR/OCS escalation | Record OCS failure lineage | Do not infer HIRR resolution from missing provider |
| Compatibility parity divergence during migration | Record CSA evidence | Use compatibility fallback or fail closed per batch rules |

## 13. Final Responsibility Matrix

| Domain | Permanent UBTR Owner | Permanent HIRR Owner | Migration-Only Shared | Retire After Certification |
| --- | --- | --- | --- | --- |
| Intent family meaning | Yes | No | HIRR markers validate parity | HIRR semantic markers |
| Ambiguity classification | Yes | No | HIRR compares with compatibility | HIRR ambiguity markers |
| Clarification question semantic basis | Yes | HIRR preserves certified output contract | Output parity migration | Local semantic question triggers |
| Clarification lifecycle state | No | Yes | No | Never |
| Reply semantic interpretation | Yes | HIRR validates lifecycle effects | HIRR reply markers until parity | Reply semantic markers |
| Reply binding | No | Yes | No | Never |
| Target workflow semantic candidate | Yes | HIRR allowlists and gates | Parity comparison | Local semantic target triggers |
| Supported workflow allowlist | No | Yes | No | Never |
| Unsafe escalation semantics | Yes | Yes, as enforcement | Shared evidence during migration | Local unsafe markers only after CSA parity; enforcement remains |
| Replay translation lineage | Yes | Consumes and links | No | Never |
| HIRR lifecycle replay | No | Yes | No | Never |
| Previous compatibility interpretation | No | Yes during migration | Yes | Retire only after compatibility retirement |
| Governance authority | No | No | No | Never owned by either |
| Approval authority | No | No | No | Never owned by either |
| Provider selection | No | No | No | OCS owns |
| Worker invocation | No | No | No | Downstream governed worker path owns |

## 14. Migration Completion Criteria

HIRR semantic migration is complete only when:

1. every HIRR intake family consumes CSA as primary source;
2. clarification response interpretation consumes linked original and reply CSA artifacts;
3. advisory/governed/bounded-proof target refinement is CSA-derived;
4. proposal-only-after-clarification uses CSA no-execution/advisory semantics;
5. multilingual HIRR cases are represented by CSA or explicitly retained as documented compatibility;
6. replay records CSA source for every HIRR semantic decision;
7. prior compatibility interpretation is either retired or diagnostic-only;
8. all HIRR lifecycle tests remain green;
9. full pytest passes;
10. certification states that UBTR owns HIRR semantic meaning and HIRR owns lifecycle enforcement.

Completion does not require retiring lifecycle orchestration.

Completion does require retiring HIRR semantic marker authority.

## 15. Retirement Criteria

A HIRR compatibility semantic marker may be retired only when:

- CSA field coverage exists;
- positive, negative, ambiguous, unsafe, multilingual, and fail-closed cases are tested;
- replay can reconstruct CSA source and HIRR lifecycle result;
- rollback has been proven before retirement;
- no downstream artifact shape changes unexpectedly;
- OCS, provider, worker, approval, and governance boundaries remain unchanged;
- governance documentation explicitly certifies retirement.

A HIRR responsibility may not be retired when it is:

- lifecycle state management;
- reply binding;
- replay hash validation;
- chain continuity validation;
- supported target enforcement;
- unsafe escalation enforcement;
- non-authority assertion;
- governance boundary preservation.

## 16. Certification Impact

This boundary specification freezes final ownership:

- UBTR is final owner of semantic interpretation for HIRR.
- HIRR is final owner of clarification lifecycle orchestration and boundary enforcement.
- Shared responsibility is allowed only during migration and must be replay-visible.
- Compatibility-era HIRR semantic markers are retirement candidates, not permanent architecture.
- HIRR lifecycle machinery is permanent architecture, not compatibility debt.

Certification language after this specification may say:

```text
HIRR is the lifecycle and boundary controller for human intent resolution.
UBTR is the canonical semantic source consumed by HIRR.
Compatibility semantic markers remain only until parity-gated migration and retirement certification complete.
```

Certification language must not say:

- HIRR has no remaining migration work;
- UBTR owns clarification lifecycle;
- CSA can bypass HIRR lifecycle enforcement;
- HIRR compatibility semantic markers are already retired;
- provider or worker authority moved into UBTR or HIRR.

## 17. Explicit Non-Goals

This specification does not:

- implement migration;
- modify tests;
- change runtime behavior;
- retire compatibility layers now;
- redesign HIRR;
- redesign UBTR;
- redesign OCS;
- redesign approval;
- redesign PPP;
- redesign workers;
- change governance authority;
- reinterpret historical replay.

## Final Verdict

UBTR_HIRR_FINAL_BOUNDARIES_FROZEN
