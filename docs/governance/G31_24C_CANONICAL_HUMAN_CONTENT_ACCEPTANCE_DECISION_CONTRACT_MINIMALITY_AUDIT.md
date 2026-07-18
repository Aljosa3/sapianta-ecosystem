# G31-24C Canonical Human Content-Acceptance Decision Contract Minimality Audit

Date: 2026-07-18  
Verdict: `EXISTING_HUMAN_DECISION_ARTIFACT_VERSIONED_EXTENSION_REQUIRED`

## Scope and conclusion

This audit determines only the minimum truthful representation of a human decision to accept one exact G31-23B validated V2 replacement result. It creates, collects, consumes, accepts, authorizes, mutates, applies, invokes, and dispatches nothing. The only audit change is this report.

No existing public decision contract can be reused unchanged. The smallest truthful canonical path is a V2 extension of the existing `human_decision_runtime` artifact and Replay family, with a narrowly typed `CONTENT_ACCEPTANCE_ONLY` subject projection from reconstructed G31-23B evidence. This preserves V1 decision bytes, hashes, vocabulary, reconstruction, and callers. It avoids a new standalone approval/acceptance authority family.

The extension must be a new version, not a V1 field addition or a projection of old approval artifacts. V1 accepts generic `APPROVE`/`YES`, is subject-bound to a PPP `HUMAN_APPROVAL_REQUIRED` execution chain, and may expose implementation authorization. Calling that a content decision would be a false historical claim. V2 affirmative vocabulary is exactly `ACCEPTED`; its scope is exactly `CONTENT_ACCEPTANCE_ONLY`; all execution and mutation flags remain false. `generated_content_acceptance_runtime` remains the only owner that marks a result accepted.

## Baseline and audit boundaries

| Check | Result |
|---|---|
| Required G31-23A, G31-23B, G31-23B test, and G31-24A | tracked at `HEAD` `cb3fee48` |
| G31-24B | no repository change: `HEAD` is unchanged from committed G31-24A; only known protected paths/root markers are dirty/untracked |
| Nested repositories | `sapianta-domain-credit`, `sapianta_system`, and `sapianta-domain-trading` clean before and after inspection |
| Protected evidence | all nine SHA-256 values unchanged and equal to G31-24A |
| Runtime behavior | unchanged; no decision, acceptance, mutation authorization, patch application, CODEX, Provider, or runtime command runner was invoked |

The accepted pre-decision truth remains `acceptance_prerequisites_satisfied=true`, `ready_for_acceptance=true`, `result_accepted=false`, `mutation_authorized=false`, and `main_repository_mutated=false`.

## Existing decision-contract inventory

| Owner / public symbols | Artifact, vocabulary, and subject | Replay, authority, and content-acceptance fitness |
|---|---|---|
| `human_decision_runtime.py:record_human_decision`, `reconstruct_human_decision_replay`, `render_human_decision_summary` | `HUMAN_DECISION_ARTIFACT_V1` / returned V1; `APPROVE`, `REJECT`, `REQUEST_MODIFICATION`; normalizer also permits `YES`/`NO`. Subject is an authenticated PPP `HUMAN_APPROVAL_REQUIRED` execution and approval packet. | Two ordered wrappers; used by G31 task-outcome/disposable bindings and conversation continuation. V1 is non-mutating but a request may permit implementation authorization. Closest canonical owner, not directly truthful. |
| `codex_task_outcome_human_review_runtime.py:prepare_codex_task_outcome_review`, `record_codex_task_outcome_human_decision`, reconstructors/renderers | G31 review packet/required/request V1; `TASK_OUTCOME_SATISFIED`, `TASK_OUTCOME_UNSATISFIED`, `REWORK_REQUESTED`; maps to generic decision vocabulary. Subject is exact Worker output and pre-execution criteria. | Ordered review + generic-decision Replay; rejects bytes, source, cross-session, duplicate, and truth substitution. Explicitly returns `result_accepted=false`. `SATISFIED` is not accepted validated content. |
| `codex_satisfied_outcome_disposable_validation_binding_runtime.py:record_disposable_patch_validation_human_decision` | `DISPOSABLE_PATCH_VALIDATION_*_V1`; generic `APPROVE` for one disposable application/test scope. | Reconstructs G31 lineage and rejects duplicate approval. Positive decision is disposable-action authority, so cannot be content acceptance. |
| `execution_summary_runtime.py:create_execution_summary_confirmation` | `EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1`; confirmation response vocabulary. Subject is an execution plan/summary. | Hash-verified artifact used by execution/improvement flows; not a G31-23B content subject. Incompatible. |
| `grounded_execution_authorization_human_decision_binding.py:bind_distinct_human_execution_decision` / reconstructor | `GROUNDED_EXECUTION_AUTHORIZATION_HUMAN_DECISION_RESULT_ARTIFACT_V1`; execution approved/rejected. Subject is G31-08 authorization review and execution summary. | Ordered specialized Replay and one-time guard; deliberately execution-authorizing lineage. Incompatible. |
| `proposal_approval_runtime.py:decide_proposal_approval`; `acli_proposal_approval_bridge.py:record_conversational_approval_decision` | proposal/bridge V1 artifacts; approve/reject/clarify variants. Subject is a proposal/conversation turn. | Ordered Replay and non-authority presentation, but proposal approval is not validated-result acceptance. Incompatible. |
| `improvement_approval_runtime.py:decide_improvement_approval`; `implementation_approval_resume.py:create_human_implementation_approval` | improvement/implementation approvals V1; `APPROVED`/`REJECTED`. Subjects are improvement review/proposal or PPP implementation request. | Replay-backed, but can enable later implementation/handoff. Incompatible. |
| `generated_content_acceptance_runtime.py:accept_generated_content`, prerequisite binder, verifier | Acceptance evidence V1 plus prerequisite V2; expects plain human evidence containing `ACCEPTED`, `CONTENT_ACCEPTANCE_ONLY`, exact statement, actor, timestamp. | Hash-bound and replay-visible, but has no decision artifact input or Replay directory/reconstructor. Correct consumer, not human-evidence owner. |
| `result_evaluation_runtime.py:evaluate_result` | `RESULT_EVALUATION_ARTIFACT_V1`; evaluates legacy `RESULT_ARTIFACT_V1`. | Two-wrapper Replay, explicitly no approval/certification authority, no production caller, and wrong subject. Incompatible. |
| `filesystem_mutation_authorization_runtime.py:authorize_filesystem_mutation` | V1 create-only authorization with separate `AUTHORIZED` human evidence. | Non-mutating but authorizing and V1/`CREATE_ONLY` only. Rejects V2 replacement; not reusable. |

Other discovered approval families (governed implementation, capability/domain, live-provider, validation, patch/multi-file mutation, rollback, and git-commit approvals) are each bound to their named action. None has a G31-23B caller or V2 validated-result subject; reuse would falsely authorize or misdescribe the decision.

## Semantic compatibility and vocabulary

| Candidate | Exact result/hash subject | `ACCEPTED` / `CONTENT_ACCEPTANCE_ONLY` | Non-authorizing | Extension | Finding |
|---|---:|---:|---:|---:|---|
| Generic human decision V1 | no | no; aliases `YES` | conditional only | yes, V2 | VERSIONED_EXTENSION_REQUIRED |
| G31 task-outcome review | Worker output/criteria only | no; satisfied/unsatisfied/rework | yes | technically but semantically false | INCOMPATIBLE |
| Disposable application decision | patch/test action | no; approve/reject | no: disposable-action authority | no truthful projection | INCOMPATIBLE |
| Execution confirmation/decision | execution plan | no | no: execution lineage | no truthful projection | INCOMPATIBLE |
| Proposal/improvement/implementation approvals | proposal/review | no | may lead to implementation | no truthful projection | INCOMPATIBLE |
| Generated-content acceptance | exact manifest/validations | values are plain input | yes | strict consumer projection needed | BOUNDED_CONSUMER_PROJECTION_REQUIRED |
| Result evaluation | legacy result artifact | no | yes | wrong artifact family | INCOMPATIBLE |

The required negative is not another approval family: V2 should record `REJECTED` as terminal content-result rejection. `REWORK_REQUESTED` remains the G31 task-outcome lifecycle state and is not silently reinterpretable. `APPROVE`, `YES`, and `SATISFIED` must fail closed at V2.

## Minimum V2 contract and ownership

The owner is `human_decision_runtime`: it already owns human-decision identity, hash verification, append-only Replay, return shape, and generic presentation. Human Conversation Experience/AiCLI is a contextual presenter and collector only. `generated_content_acceptance_runtime` remains a non-authorizing consumer; it must never create human evidence. Governance and Replay remain validators/reconstructors, not decision owners.

| Surface | Future bounded design |
|---|---|
| Artifact family | `HUMAN_DECISION_ARTIFACT_V2` and returned V2, a versioned extension; all V1 artifact bytes/hashes/reconstructor behavior stay unchanged. |
| Constructor and validator | Public content-acceptance constructor/verifier/reconstructor in `human_decision_runtime`; reconstruct G31-23B binding and prerequisite evidence instead of trusting copied fields. |
| Exact subject | Session; manifest reference/artifact/manifest hashes; source path/preimage; replacement/postimage hashes; V2 content/test validations; G31-23A outcome; G31-23B prerequisite/binding; required Replay hashes. |
| Vocabulary / scope | only `ACCEPTED` or `REJECTED`; exactly `CONTENT_ACCEPTANCE_ONLY`; aliases and unrelated scopes rejected. |
| Boundaries | `execution_authorized=false`, `mutation_authorized=false`, `main_repository_mutated=false`, `provider_invoked=false`, `worker_invoked=false`; no authorization/patch/application imports. |
| Acceptance consumer | Strict public projection from verified V2 decision to existing five-field `human_acceptance_evidence`, then existing `accept_generated_content`; no second algorithm. |
| AiCLI | One context rendering the reconstructed validated result, collecting only explicit positive/negative commands, and passing raw response to the V2 owner. It cannot construct hashes, infer a decision, or call mutation. |

Minimum V2 Replay ordering is: (1) validated-result context presented, (2) explicit request recorded, (3) accepted/rejected decision recorded once, (4) decision returned/reconstructed, (5) on `ACCEPTED` only, canonical acceptance consumption and a versioned acceptance binding/replay record showing `mutation_authorized=false` and `main_repository_mutated=false`.

The V1 human-decision two-step Replay proves only decision/return. The current acceptance function has no Replay directory. A later binding must therefore version the existing acceptance family for consumption evidence; it cannot claim current acceptance already persists an ordered Replay. That remains an extension of canonical owners, not a parallel system.

## Reuse, compatibility, and fail-closed analysis

Direct reuse fails because V1 permits `YES`, requires a PPP packet, omits replacement/prerequisite binding, and may expose implementation authority. A direct plain-dictionary call to `accept_generated_content` loses authoritative decision identity, contextual request/presentation, one-time consumption, and decision Replay. Such a projection is safe only after V2 reconstructs every required fact. Versioning the generic decision family is truthful because it preserves the decision-owner role but establishes an explicit new subject and scope. A new standalone family is not justified.

Compatibility requirements: do not change V1 hash input, `VALID_DECISIONS`, normalizer, Replay steps, return shape, or callers; V2 uses distinct type, runtime version, vocabulary, hash domain, and Replay. V1 generated-content acceptance construction/reconstruction remains unchanged. Existing V1 authorization and filesystem mutation continue to reject V2 replacement.

Reusable fail-closed evidence: generic decision Replay rejects unavailable/reordered destinations and hash mismatch; G31 task review rejects source/output/criteria, cross-session, duplicate, Replay, and truth substitution; G31-23B rejects V1 substitution, changed bytes/path/type/mode, validation/prerequisite drift, cross-session/repeated consumption, and owner invocation; generated acceptance rejects invalid V1/V2 manifest/validation bindings, missing exact statement, and supplied duplicate lineage.

Missing today and required in V2: alias rejection; scope/subject substitution; stale presentation/request; duplicate accepted/rejected decision; repeated acceptance consumption; protected-hash or nested drift; and reuse of accepted content decision for mutation authorization. Invalid evidence must create no acceptance and must not modify valid Replay.

## Validation and audit state

| Validation | Result |
|---|---|
| Existing human decision, execution/proposal/improvement/implementation approvals, Human Interface/AiCLI, acceptance, manifest/validation, result evaluation, and mutation-boundary tests | `164 passed in 9.23s` |
| G31-22A/B/C current fixture invocation | Runner ended before pytest completion summary after initial progress; not recorded as pass/failure. Committed G31-23B regression evidence is non-conflicting. |
| Full suite | Not run: no focused conflict with committed certification evidence. |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook mismatches, 0 critical; deterministic/read-only/fail-closed; hash `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea` |
| Targeted `py_compile`; parent and all nested `git diff --check` | pass |

Inspected the inventory contracts, `aigol/cli/aicli.py`, G31-23A/B/24A, their focused tests, existing decision/approval/confirmation, result-evaluation, acceptance, manifest/validation, mutation, Replay, Human Interface, and AiCLI tests. Created only this report.

At report creation parent status contains the six protected modified runtime-evidence paths and three protected untracked root markers. This report is the only additional untracked path; nothing is staged. Documentation-only commit:

```bash
git add docs/governance/G31_24C_CANONICAL_HUMAN_CONTENT_ACCEPTANCE_DECISION_CONTRACT_MINIMALITY_AUDIT.md
git commit -m "docs(governance): audit content acceptance decision minimality"
```

Evidence-scoped progress is 95.5%: the missing contract is precisely located and bounded, while no acceptance or mutation gap is hidden.

Next state (exactly one): `G31_24D_VERSIONED_HUMAN_CONTENT_ACCEPTANCE_DECISION_IMPLEMENTATION_REQUIRED`

### Bounded G31-24D implementation prompt

Extend only `aigol/runtime/human_decision_runtime.py` with a V2 `CONTENT_ACCEPTANCE_ONLY` decision contract for one reconstructed G31-23B capture. Use only `ACCEPTED` and `REJECTED`; reject `APPROVE`, `YES`, prior decisions, other sessions, altered manifest/path/mode/bytes, altered validation/prerequisite/G31-23A evidence, Replay substitution/order changes, and repeated decisions. Persist V2 context/request/decision/return Replay and preserve V1 behavior byte-for-byte. Add a non-authoritative AiCLI presentation/collection context that passes raw response to the V2 owner and stops after the decision; do not call acceptance yet. Add focused tests for binding, rejection, aliases, cross-session/tamper/duplicate failures, V1 compatibility, no mutation/CODEX/Provider/source write, and protected/nested integrity. Do not change acceptance, mutation authorization, mutation, unrelated schemas, or Platform Core.
