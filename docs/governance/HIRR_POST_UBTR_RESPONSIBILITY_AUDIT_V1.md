# HIRR Post UBTR Responsibility Audit V1

Status: governance audit artifact.

Scope: Human Intent Resolution Runtime responsibility classification after UBTR Consumer Migration Batch 01 and Batch 02.

This audit does not modify runtime, tests, routing, replay, governance, approval, OCS, providers, or workers.

## 1. Context

Platform Core Generation 1 is certified.

UBTR is beta ready.

Completed migrations:

- Batch 01: ACLI routing CSA-first subset, parity-gated.
- Batch 02: HIRR ambiguous-intent clarification intake CSA-first subset, parity-gated.

Batch 02 establishes that HIRR can consume Canonical Semantic Artifacts where CSA and previous HIRR compatibility interpretation deterministically agree.

HIRR is now partially migrated, not fully migrated.

## 2. Audit Question

This audit determines:

1. which HIRR responsibilities are still semantic interpretation;
2. which HIRR responsibilities are lifecycle orchestration;
3. which semantic responsibilities should migrate to UBTR;
4. which responsibilities must permanently remain in HIRR.

## 3. Current HIRR Surfaces

Primary HIRR-related runtime surfaces:

- `aigol/runtime/human_intent_clarification_intake_runtime.py`
- `aigol/runtime/human_intent_clarification_continuity_runtime.py`
- `aigol/runtime/clarification_lifecycle_resolution_runtime.py`
- HIRR integration inside `aigol/runtime/conversational_cli_runtime.py`

Post Batch 02, HIRR intake includes a CSA-consuming path:

- `classify_human_intent_for_clarification_from_canonical_semantic_artifact(...)`

That path is primary only for the certified ambiguous-intent clarification intake parity subset.

## 4. Responsibility Classification Legend

Each responsibility is classified as one of:

- `UBTR responsibility`: semantic translation should live in UBTR/CSA.
- `HIRR responsibility`: orchestration, replay, state, lifecycle, or boundary enforcement should remain in HIRR.
- `Shared during migration only`: HIRR compatibility markers remain active until CSA parity is certified.
- `Compatibility-only`: retained for rollback, legacy prompts, or unsupported UBTR field gaps.
- `Candidate for retirement`: may be retired only after parity, replay reconstruction, rollback proof, and full certification.

## 5. Final HIRR Responsibility Matrix

| Responsibility | Current Owner | Classification | UBTR Responsibility | HIRR Responsibility | Migration Status | Retirement Candidate |
| --- | --- | --- | --- | --- | --- | --- |
| Ambiguous-intent clarification intake for CSA `CLARIFICATION_REQUIRED` / unknown domain / material ambiguity | CSA plus HIRR parity gate | Shared during migration only | Produce canonical ambiguity, workflow candidate, confidence, and clarification-required state | Validate compatibility parity, emit HIRR artifact, preserve clarification-first workflow | Migrated for certified subset | Compatibility marker for this subset is a future retirement candidate |
| Business-goal intent family detection | HIRR local markers | Shared during migration only | Represent business-goal semantic family, domain, ambiguity, and likely target | Preserve HIRR artifact shape and clarification questions during migration | Not migrated | Candidate after CSA parity corpus exists |
| Problem-statement intent family detection | HIRR local markers | Shared during migration only | Represent problem-statement semantics and ambiguity | Preserve clarification-first artifact and target defaults | Not migrated | Candidate after CSA parity corpus exists |
| Automation intent family detection | HIRR local markers | Shared during migration only | Represent automation intent, requested action, domain, and ambiguity | Preserve questions and expected target behavior | Not migrated | Candidate after CSA parity corpus exists |
| Compliance intent family detection | HIRR local markers | Shared during migration only | Represent compliance/audit semantic family and evidence intent | Preserve clarification questions and no-execution flags | Not migrated | Candidate after CSA parity corpus exists |
| General-improvement intent family detection | HIRR local markers | Shared during migration only | Represent advisory/improvement semantics and OCS-cognition target eligibility | Preserve clarification-first behavior and OCS target hint | Not migrated | Candidate after CSA parity corpus exists |
| Continuation intent family detection | HIRR local markers | Shared during migration only | Represent continuation semantic intent and missing replay context | Preserve clarification questions asking what to continue | Not migrated | Candidate after CSA parity corpus exists |
| Bounded file-write proof intent detection | HIRR local markers | Shared during migration only | Represent bounded proof-file action and required approval/worker relevance | Preserve safe target `BOUNDED_FILE_WRITE_WORKER_USER_SESSION` and no immediate execution | Not migrated | Candidate after CSA parity corpus exists |
| Development intent detection for governed routing | HIRR local markers plus Batch 01 CSA-derived intake for governed-development route subset | Shared during migration only | Represent development action/domain/entity fields | Preserve HIRR-compatible intake shape and downstream governed workflow handoff | Partially migrated through ACLI Batch 01, not HIRR-complete | Candidate after non-ACLI HIRR parity exists |
| Unknown prompt fallback to `AMBIGUOUS_INTENT` | HIRR local fallback, CSA migrated for one subset | Shared during migration only | Represent unknown action/domain/material ambiguity | Preserve low-confidence clarification-first behavior | Partially migrated | Candidate only after all unknown-prompt parity and negative cases are certified |
| Clarification question selection | HIRR local deterministic question map | HIRR responsibility | UBTR may provide semantic reason and ambiguity evidence | HIRR must preserve certified operator question wording until explicit output parity | Not migrated | Not currently a retirement candidate |
| Expected workflow target selection from intent family | HIRR local map | HIRR responsibility with semantic input migration | UBTR may propose workflow candidate or target class | HIRR owns certified target mapping until downstream workflow parity is proven | Not migrated | Candidate only after target mapping parity and downstream tests |
| HIRR artifact shape and non-authority flags | HIRR | HIRR responsibility | None beyond supplying source semantic evidence | Preserve artifact compatibility, replay safety, no provider/worker/approval/execution authority | Active | Not a retirement candidate |
| CSA/HIRR parity gate | HIRR | HIRR responsibility | Supply validated CSA fields | Validate deterministic parity before CSA becomes primary | Active Batch 02 pattern | Not a retirement candidate while compatibility exists |
| Previous compatibility interpretation capture | HIRR/ACLI routing replay | HIRR responsibility | None | Preserve rollback evidence and auditability | Active Batch 02 pattern | Not a retirement candidate until compatibility is retired |
| Replay lineage for HIRR intake | HIRR/ACLI routing replay | HIRR responsibility | Supply CSA hash/reference | Persist source, prior compatibility, parity evidence, and lineage | Active | Not a retirement candidate |
| Active clarification discovery | Clarification lifecycle runtime | HIRR responsibility | None | Determine active/open/responded/resolved/superseded clarification state from replay | Active | Must remain in HIRR |
| One-active-clarification invariant | Clarification lifecycle runtime | HIRR responsibility | None | Fail closed on multiple active clarification states | Active | Must remain in HIRR |
| Clarification reply binding | HIRR continuity runtime | HIRR responsibility | UBTR may translate reply for semantic comparison in later migration | Bind reply to original clarification request and chain | Active | Must remain in HIRR |
| Clarification response hashing and replay | HIRR continuity runtime | HIRR responsibility | None | Preserve append-only replay-visible reply evidence | Active | Must remain in HIRR |
| Clarification target refinement from reply text | HIRR continuity local markers | Shared during migration only | Translate reply semantics and ambiguity reduction through linked CSA artifacts | Preserve target refinement, unsafe escalation checks, and workflow selection during migration | Not migrated | Semantic marker portions are retirement candidates after CSA parity |
| Unsafe clarification escalation blocking | HIRR continuity runtime | HIRR responsibility | UBTR may mark unsafe ambiguity | HIRR must enforce fail-closed boundary for bypass approval, credentials, worker invocation, unrestricted autonomy | Active | Must remain in HIRR |
| Proposal-only cognition routing after clarification | HIRR continuity local markers | Shared during migration only | Represent advisory/no-execution clarification response semantics | Preserve proposal-only routing and human-confirmation guard | Not migrated | Candidate after CSA parity and OCS ownership certification |
| Workflow selection after clarification | HIRR continuity runtime | HIRR responsibility | UBTR may supply semantic evidence for target refinement | Select only supported target workflows and preserve replay lineage | Active | Must remain in HIRR |
| Supported target workflow allowlist | HIRR continuity runtime | HIRR responsibility | None | Enforce bounded workflow targets | Active | Must remain in HIRR |
| Provider, worker, approval, execution non-authority assertions | HIRR intake and continuity | HIRR responsibility | UBTR also asserts non-authority in CSA | HIRR must preserve no-provider/no-worker/no-approval/no-execution behavior | Active | Must remain in HIRR |
| Rendering HIRR clarification summaries | HIRR renderer | HIRR responsibility with possible UBTR output support | Governance -> Human UBTR may eventually render operator wording | HIRR must preserve certified operator visibility until output parity | Active | Not currently a retirement candidate |

## 6. Semantic Interpretation Still In HIRR

HIRR still performs semantic interpretation in these areas:

1. intent-family classification for business-goal, problem-statement, automation, compliance, general-improvement, continuation, bounded file-write proof, and non-migrated ambiguous prompts;
2. development-intent classification outside the Batch 01/Batch 02 parity-gated paths;
3. expected workflow target derivation from local intent family;
4. clarification reply interpretation in `_refined_workflow_target(...)`;
5. proposal-only cognition routing after clarification;
6. unsafe clarification escalation signal detection;
7. fallback unknown-intent classification where CSA parity is not certified.

These responsibilities are semantic or semi-semantic and should migrate toward CSA/UBTR only through deterministic parity batches.

## 7. Lifecycle Orchestration Still In HIRR

HIRR lifecycle responsibilities include:

1. maintaining clarification-first workflow state;
2. preserving HIRR-compatible artifact shapes;
3. binding clarification replies to the original request;
4. preserving canonical chain identity;
5. reconstructing active clarification state from replay;
6. enforcing one active clarification at a time;
7. marking clarification state as open, active, responded, resolved, or superseded;
8. preserving append-only replay evidence;
9. selecting only supported workflow targets after clarification;
10. preventing provider, worker, approval, execution, governance, or replay authority drift.

These responsibilities must permanently remain in HIRR or adjacent lifecycle/replay runtimes. They are not UBTR responsibilities.

## 8. Semantic Responsibilities That Should Migrate To UBTR

The following should migrate to CSA/UBTR in future batches:

1. remaining HIRR intent-family classification;
2. non-migrated ambiguous prompt interpretation;
3. development-intent HIRR classification outside Batch 01 route parity;
4. clarification response semantic interpretation;
5. ambiguity reduction detection between original prompt and clarification reply;
6. advisory versus governed-workflow target semantics;
7. proposal-only cognition eligibility after clarification;
8. multilingual semantic interpretation currently encoded as HIRR marker phrases.

These migrations must not remove HIRR lifecycle enforcement.

## 9. Responsibilities That Must Permanently Remain In HIRR

The following must remain HIRR responsibilities:

1. clarification-first orchestration;
2. HIRR artifact compatibility during all migrations;
3. active clarification lifecycle reconstruction;
4. one-active-clarification invariant;
5. reply binding to original clarification request;
6. replay lineage and hash validation;
7. supported workflow allowlist after clarification;
8. unsafe escalation fail-closed enforcement;
9. non-authority boundary assertions;
10. rollback and compatibility visibility until explicitly retired;
11. downstream handoff after clarification resolution.

UBTR may supply semantic evidence, but HIRR remains the lifecycle and boundary controller.

## 10. Remaining Migration Batches

### HIRR Batch 03: Remaining Intake Families CSA Parity

Scope:

- business-goal;
- problem-statement;
- automation;
- compliance;
- general-improvement;
- continuation;
- bounded file-write proof.

Objective:

Generate HIRR-compatible intake artifacts from CSA where family, confidence, clarification-required status, questions, and expected workflow targets match compatibility behavior.

### HIRR Batch 04: Development Intent HIRR Parity

Scope:

- `classify_development_intent_for_governed_routing(...)` outside existing Batch 01 route subset.

Objective:

Use CSA development action/domain/entity semantics only when prior HIRR development classifier parity is proven.

### HIRR Batch 05: Clarification Reply CSA Lineage

Scope:

- translate clarification responses through UBTR;
- link original CSA and clarification-turn CSA;
- record ambiguity reduction evidence.

Objective:

Introduce replay-visible CSA comparison without changing selected workflow.

### HIRR Batch 06: Clarification Target Refinement Migration

Scope:

- migrate semantic parts of `_refined_workflow_target(...)`.

Objective:

Use linked CSA artifacts for advisory/governed/bounded-proof target refinement where parity is proven.

### HIRR Batch 07: Proposal-Only After Clarification

Scope:

- proposal-only cognition routing after unresolved ambiguity.

Objective:

Use CSA no-execution/advisory semantics while preserving OCS authority and human confirmation.

### HIRR Batch 08: Compatibility Retirement Audit

Scope:

- audit HIRR marker systems after all parity migrations.

Objective:

Classify each marker family as retired, diagnostic-only, or permanently retained with governance justification.

## 11. Retirement Candidates

Candidate for retirement after certification:

- local ambiguous-intent marker subset already migrated in Batch 02;
- business-goal marker family;
- problem-statement marker family;
- automation marker family;
- compliance marker family;
- general-improvement marker family;
- continuation marker family;
- bounded file-write proof marker family;
- development-intent marker family;
- advisory/governed/bounded-proof clarification response marker groups;
- proposal-only-after-clarification marker groups.

Not retirement candidates:

- HIRR artifact shape;
- replay validation;
- clarification lifecycle state;
- one-active-clarification invariant;
- supported target workflow allowlist;
- reply binding;
- unsafe escalation fail-closed enforcement;
- non-authority flags;
- rollback visibility until final retirement certification.

## 12. Implementation Priority

Recommended order:

1. HIRR Batch 03: remaining intake family parity.
2. HIRR Batch 04: development-intent HIRR parity.
3. HIRR Batch 05: replay-only clarification reply CSA lineage.
4. HIRR Batch 06: clarification target refinement migration.
5. HIRR Batch 07: proposal-only after clarification.
6. HIRR Batch 08: retirement audit.

Rationale:

- intake family parity is lower-risk than clarification continuity because it preserves first-turn behavior;
- development-intent HIRR parity should be separated from ambiguous HIRR intake to avoid collapsing native development, governed development, and HIRR semantics;
- clarification continuity should first gain replay-only CSA lineage before CSA becomes primary;
- proposal-only after clarification depends on OCS ownership and no-execution semantics, so it should follow clarification reply lineage;
- retirement should occur last.

## 13. Certification Impact

Post Batch 02 certification statement:

- HIRR is partially migrated to CSA.
- CSA is primary only for the certified ambiguous-intent clarification intake subset.
- HIRR compatibility classifiers remain active and required.
- HIRR remains the lifecycle controller for clarification state, reply binding, target allowlisting, replay continuity, and boundary enforcement.

Certification must not claim:

- full HIRR migration;
- full HIRR marker retirement;
- CSA authority over clarification continuity;
- UBTR authority over approval, execution, providers, workers, or governance.

Certification may claim:

- HIRR now has a certified CSA-primary intake pattern;
- HIRR semantic migration can continue by family-specific parity batches;
- lifecycle orchestration is intentionally retained in HIRR;
- remaining semantic compatibility paths are visible and bounded.

## 14. Final Finding

HIRR still contains semantic interpretation that should migrate to UBTR through additional parity-gated batches.

HIRR also contains lifecycle orchestration and boundary enforcement responsibilities that must permanently remain in HIRR.

Therefore HIRR is not ready for final migration or compatibility retirement.

## Final Verdict

HIRR_REQUIRES_ADDITIONAL_SEMANTIC_MIGRATION
