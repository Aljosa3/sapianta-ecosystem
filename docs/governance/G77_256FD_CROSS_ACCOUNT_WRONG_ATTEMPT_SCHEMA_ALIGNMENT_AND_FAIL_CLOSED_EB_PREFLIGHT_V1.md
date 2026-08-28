# 1. Implementation Summary

Generation: `G77-256FD`

Report identity: `G77_256FD_CROSS_ACCOUNT_WRONG_ATTEMPT_SCHEMA_ALIGNMENT_AND_FAIL_CLOSED_EB_PREFLIGHT_V1`

Reporting standard: `G48 Constitutional Evidence Reporting Standard V1`

Constitutional baseline: HEAD `08b7e7406396b7d6d93023baa30bc689a3aa572f`, tree `b68657113493475e68a9cd36f02e69e0d53ab6b1`, subject `G77-256FC fail closed WRONG_ATTEMPT at DU`.

Implementation contracts: committed G77-256EX common-substrate certification, G77-256DU canonical continuation-manifest contract, G77-256EB candidate-bound receipt contract, G77-256EE runtime-consumer binding contract, G77-256EZ static binding hardening, and the Human-authorized cross-account FD continuation.

Objective:

Resume the same interrupted, repository-only G77-256FD generation from authenticated uncommitted SPCE state; preserve the WRONG_ATTEMPT semantics outside DU's fixed `selected_case`; create at most one candidate; run DU once, then EB once, then EE only after EB passes; and stop without operational execution.

Outcome:

- `CROSS_ACCOUNT_CONTINUATION_RESULT = PASS__PERSISTED_UNCOMMITTED_SPCE_STATE_AUTHENTICATED_AND_REUSED` (`PROVEN`).
- `PHASE_A_CONTINUATION_AUTHENTICATION = PASS__REUSED_WITHOUT_RECONSTRUCTION` (`PROVEN`).
- `WRONG_ATTEMPT_SEMANTIC_PRESERVATION = PASS` and `DU_MODIFICATION_REQUIRED = NO` (`PROVEN`).
- `DU_RESULT = PASS` (`MEASURED`).
- `EB_RESULT = FAIL_CLOSED__VALIDATION_PROFILE_INVALID` (`MEASURED`). The supplied generation-specific profile did not equal EB's fixed canonical profile. No receipt was created.
- `EE_RESULT = NOT_RUN__EB_FAILED_FIRST` (`FACT`).
- `FIRST_AUTHORITATIVE_FAILURE = EB_VALIDATION_PROFILE_INVALID`.
- `FD_PREFLIGHT_RESULT = FAIL_CLOSED__DU_PASS__EB_VALIDATION_PROFILE_INVALID__EE_NOT_RUN`.

Scope and unchanged boundaries:

- Repository-only schema alignment and preflight evidence were authorized.
- No materialization, VM, boot, QEMU, P11 request/entry/invocation, protected effect, E05 execution, P12 entry, or production route occurred.
- E05 remains factually `6/18`; 12 cases remain; WRONG_ATTEMPT remains `UNSATISFIED`; no constitutional credit was awarded.
- The candidate remained immutable after sealing. EB was not retried, the candidate was not repaired, and EE was not invoked.
- EX, DU, EB, EE, EZ, FC, and all common infrastructure remained byte-unchanged.

Cross-account SPCE evidence:

- `CROSS_ACCOUNT_CONTINUATION_USED = YES`.
- `PREVIOUS_SESSION_CHECKPOINT_REUSED = YES`.
- `PHASE_A_RECONSTRUCTION_COUNT = 0`.
- `EXISTING_FD_ARTIFACT_RECONSTRUCTION_COUNT = 0`.
- `CONVERSATION_HISTORY_REQUIRED = NO`.
- `FULL_HISTORY_RECONSTRUCTION_REQUIRED = NO`.
- `CANDIDATE_RECONSTRUCTION_REQUIRED = NO`.
- `EXECUTION_REPLAY_REQUIRED = NO`.
- `MATERIALIZATION_REPLAY_REQUIRED = NO`.
- `SPCE_REPOSITORY_RESUMABILITY = PASS`.
- `SPCE_CROSS_ACCOUNT_RESUMABILITY = PASS`.
- `SPCE_OPERATIONAL_RESUMABILITY = NOT_ESTABLISHED__NO_OPERATIONAL_EXECUTION`.

Constitutional continuation progress:

`ET -> EU -> EV -> EW -> EX -> EY -> EZ -> FA -> FB [ZERO MUTATION] -> HUMAN WRONG_ATTEMPT SELECTION -> FC [DU FAIL CLOSED] -> FD ACCOUNT 1 [PHASE A + ADAPTER + USAGE LIMIT] -> FD ACCOUNT 2 [PHASE A/ADAPTER REAUTHENTICATED; ONE CANDIDATE; DU PASS; EB FAIL CLOSED; STOP]`.

The account switch is not a new constitutional generation.

# 2. Code Evidence

## Public API

DU's committed Canonical V1 schema fixes `selected_case` to two required fields and rejects additions:

```json
"selected_case": {
  "oneOf": [
    {"type": "null"},
    {
      "type": "object",
      "required": ["case_class", "case_id"],
      "additionalProperties": false,
      "properties": {
        "case_class": {"$ref": "#/$defs/nonempty"},
        "case_id": {"$ref": "#/$defs/nonempty"}
      }
    }
  ]
}
```

Source: `.github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json`, SHA-256 `a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e`.

## Orchestration Entry Point

The FD builder enforces the one-candidate overwrite boundary:

```python
if output.exists() or runtime_output.exists():
    raise RuntimeError("FD candidate or runtime projection already exists")
payload = du.canonical_bytes(build(repository_root))
output.parent.mkdir(parents=True, exist_ok=True)
runtime_output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(payload)
runtime_output.write_bytes(payload)
```

The ordering actually exercised was candidate seal -> DU once -> EB once -> fail-closed stop. EE was correctly not called after EB failed.

## Semantic Reductions

The candidate contains only the canonical case fields:

```python
"selected_case": {
    "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
    "case_id": "G77_256FD_E05_WRONG_ATTEMPT_PREFLIGHT_PATTERN_001",
},
```

The exact FD vector-evidence extension preserves the five displaced facts: authorized attempt identity, supplied wrong attempt identity, obligation identity, isolated semantic mutation field `attempt_identity`, and `other_vector_mutation_count = 0`. Its inner SHA-256 is `687f6fb9f63c2a30add428ea33dbf67de6c21c87429cd02c5a62da5723ac20ac`; its file SHA-256 is `7408c00b00db9225fa77a52840b54a9ae3b13fa195af8580d1822dee14dc7faf`.

The committed FC vector adapter independently establishes the runtime pattern: authorized input/act attempt binding, supplied wrong attempt substitution, exact differing-field computation, semantic mutation at `attempt_identity`, dependent `record_identity` recomputation, and zero other-vector mutations. FD does not claim that this future operational behavior was executed.

## Public Validators

- EX validator: 12/12 regressions passed; 17 common components certified.
- DU validator SHA-256: `27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d`.
- EB validator SHA-256: `8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43`.
- EE validator SHA-256: `5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410`.
- No validator was created or modified by FD.

DU returned exactly:

```json
{"constitutional_admissibility":"PASS","cryptographic_authenticity":"PASS","semantic_contract_compatibility":"PASS","structural_schema_validity":"PASS"}
```

EB returned exactly:

```json
{"candidate_validation_pass_claimed":false,"failure_code":"VALIDATION_PROFILE_INVALID","overall_result":"FAIL_CLOSED","schema_id":"G77_256EB_CANDIDATE_VALIDATION_FAILURE_V1"}
```

## Canonical Data Models

- Phase A checkpoint: file SHA-256 `30680009fa71a83cc5654c676a49f2a3eb26eea058e8ff2d1245ce5906893082`, inner `c5b0b5304e90ce14e1ec3f0d6adbb4e6467adfd916f0482a46c9e00ddf9c854b`.
- Existing FD preflight adapter: SHA-256 `ba9767aa2437bc76ffb2fdb8eee2c5281333a3e963f8e8d632d5525d7b0b2910`; reused unchanged.
- Candidate and runtime projection: identical SHA-256 `b87e0e49815cb01755be8c983cc5751529dd996cd3a63788466e32ce22f5def9`; manifest inner `908e9f6ae4421a02087db0039457f48a0ae016385108bfeea56af386479e377d`.
- Phase B candidate seal inner SHA-256: `d4215fd3abc29f92a63e3f465048c0a7703ca784e8bee3ae3b26c500ad681495`.
- Phase C failure checkpoint inner SHA-256: `f227e45b571528badf6a2027eef562ba7cd1974d4091f916a1cec3900e506059`.
- Phase D independent reduction inner SHA-256: `537c5c6051965934338f1c1890ec8682878548e5da634fe9af698cd0d8728fab`.

## Deterministic Algorithms

JSON inner identities use canonical sorted compact JSON plus LF and SHA-256. Candidate/runtime equality uses exact byte comparison. All committed bindings were reread and hashed. JSON unique-key validation is part of final validation. The candidate count is derived from filesystem evidence across the complete FD generation, not reset by account change.

## Responsibility Boundaries

- HUMAN: initial and continuation authorization, later review, and any later commit or separately authorized operational generation.
- CERTIFIED AIGOL/GOVERNANCE: EX, DU, EB, EE, EZ, and constitutional invariants.
- DETERMINISTIC SYSTEM: hashes, schema validation, binding validation, candidate seals, and checkpoints.
- CODEX: repository authentication, root-cause reauthentication, bounded vector-local construction, orchestration, and evidence reduction proposal.
- `AIGOL_CODEX_WORK_SHARE = NOT_MEASURED` numerically.
- `PREVIOUS_CODEX_CONVERSATION_CONTEXT = NON_CONSTITUTIONAL`.
- `PERSISTED_UNCOMMITTED_FD_EVIDENCE = RESUMABLE_ONLY_IF_AUTHENTICATED_AGAINST_COMMITTED_AUTHORITY`.

# 3. Constitutional Self-Assessment

## Verified

- Exact FC HEAD, tree, and subject; empty continuation-entry index; only expected FD uncommitted state.
- Phase A unique-key JSON, inner hash, outer hash, repository cross-bindings, FC fail-closed result, E05 `6/18`, and zero operational progression.
- Existing adapter static EE path declarations, exact committed FC adapter binding, vector-local scope, and `OPERATIONAL_AUTHORITY = False`; adapter modified count zero.
- Canonical `selected_case = {case_class, case_id}` and extension-binding semantic boundary.
- WRONG_ATTEMPT representation preserved without common-schema change or semantic deletion; other-vector mutation count zero in the repository pattern.
- EX 12/12 regression validation and 17/17 applicable certified common components reused; zero common reconstruction, new common infrastructure, or parallel proof stack.
- One generation-wide candidate, zero replacement candidate, exact candidate/runtime identity, and candidate immutability after seal.
- DU one-shot PASS.
- EB one-shot fail-closed behavior on invalid profile, no PASS claim, and no receipt.
- First-failure stop: zero EB retry, zero repair-and-continue, and EE not run.
- Zero materialization, VM, boot, QEMU, P11, E05 execution, protected effect, P12, production route, or production effect.
- E05 remains `6/18`; WRONG_ATTEMPT remains `UNSATISFIED`; constitutional credit not awarded.
- No staging, commit, push, reset, clean, or stash.

## Not Verified

- EB candidate-bound admissibility: `FAIL` because the sole invocation supplied a noncanonical validation profile.
- EE candidate-to-runtime static consumer binding: `NOT_RUN` because EB failed first.
- `B6_REPOSITORY_PRECONDITION`: `NOT_ESTABLISHED__EE_NOT_REACHED`.
- `B1`, `B2`, and operational B6: `NOT_RUN__REPOSITORY_ONLY_GENERATION`.
- Future WRONG_ATTEMPT operational denial, P11 behavior, and E05 credit: `NOT_VERIFIED` and outside FD authority.
- Automated end-to-end repository preflight readiness: `BLOCKED` at EB invocation-profile orchestration.
- SPCE operational resumability: `NOT_ESTABLISHED`; no operational state exists.
- Current Codex `/status` telemetry, elapsed time, token benchmark, numeric work-share, and exact LLM cost-reduction ratio: `NOT_MEASURED` or `NOT_EXACTLY_MEASURABLE`.
- Global project completion percentages lack a certified denominator and remain `ESTIMATED`, not certified facts.

## Constitutional Health Evidence

`CONSTITUTIONAL_HEALTH = FAIL_CLOSED_BOUNDARY_INTACT__FD_PREFLIGHT_INCOMPLETE`. The exact FC baseline, bounded dirty worktree, authenticated Phase A seal, zero reconstruction, adapter reuse, cross-account candidate counting, canonical DU authority, semantic preservation, DU/EB/EE ordering, first-failure stop, zero retry/repair, and zero operational/production effects are preserved. The failed EB invocation is visible and is not reframed as full conformance.

## Shadow Automation and Candidate Capability

- `SHADOW_AUTOMATION_STATE = PARTIAL__REPOSITORY_TO_VECTOR_BINDING_TO_CANDIDATE_TO_DU_PROVEN__EB_FAILED_CLOSED__EE_NOT_REACHED`.
- `SHADOW_AUTOMATION_READINESS = BLOCKED__CANONICAL_EB_PROFILE_ORCHESTRATION_REQUIRES_SEPARATE_HUMAN_DECISION`.
- `AUTOMATED_PREFLIGHT_READINESS = NOT_ESTABLISHED`.
- `CANDIDATE_CAPABILITY = DU_ADMITTED_WRONG_ATTEMPT_SCHEMA_ALIGNED_REPOSITORY_CANDIDATE__EB_AND_EE_NOT_ADMITTED`.
- Shadow design remains `HUMAN_SELECTION -> COMMITTED_REPOSITORY -> EX -> SMALL_WRONG_ATTEMPT_DELTA -> DU -> EB -> EE -> STOP -> NEW_HUMAN_OPERATIONAL_AUTHORIZATION -> FRESH_B1_B2_B6 -> ONE_OPERATIONAL_ATTEMPT -> REDUCTION`; FD stopped at EB.

## Frontier, Progress, and Cost

- `CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__MULTIDIMENSIONAL_FRONTIER`.
- `CONSTITUTIONAL_FRONTIER_DISTANCE_E05 = FACT__12_CASES_REMAIN`.
- `WRONG_ATTEMPT_FRONTIER = BLOCKED__EB_CANONICAL_PROFILE_VALIDATION_NOT_ESTABLISHED`.
- `PROJECT_PROGRESS_ESTIMATE`, `ARCHITECTURAL_PROGRESS_ESTIMATE`, `IMPLEMENTATION_MATURITY_ESTIMATE`, `OPERATIONAL_COMMISSIONING_MATURITY_ESTIMATE`, and `AUTOMATION_MATURITY_ESTIMATE` are `ESTIMATED__NO_CERTIFIED_GLOBAL_DENOMINATOR`. E05 is separately factual at `6/18`.
- `PROMPT_CONTEXT_REUSE_RATIO = STRUCTURAL_CONTEXT_REUSE_HIGH__TOKEN_LEVEL_CONTEXT_REUSE_NOT_MEASURED`: committed context, Phase A, adapter, and EX were reused; full conversation history was not required.
- `LLM_COST_REDUCTION_RATIO = NOT_EXACTLY_MEASURABLE` and `LCRR = NOT_EXACTLY_MEASURABLE`.
- Avoided work: Phase A reconstruction, EX reconstruction, full-history reconstruction, adapter reconstruction, VM execution, and operational retry.

## Cognition-Assisted Handoff

`COGNITION_ASSISTED_HANDOFF = PASS__NEW_CODEX_ACCOUNT_DISTINGUISHED_COMMITTED_AUTHORITY_FROM_REAUTHENTICATED_UNCOMMITTED_SPCE_EVIDENCE_AND_NONAUTHORITATIVE_CONTEXT`. The persisted bytes, not conversation claims, established the resumable state.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact FC baseline | Git HEAD/tree/subject | `git log -1`, `git rev-parse` | PASS |
| Empty index and authorized continuation scope | Git status/index and two initial FD files | entry-gate commands | PASS |
| Phase A authentication without reconstruction | Phase A inner/outer hashes and committed bindings | unique-key parse and deterministic rehash | PASS |
| Existing adapter reuse unchanged | adapter SHA-256 `ba9767aa...2910` | AST/static path and hash validation | PASS |
| EX common substrate | committed EX certificate | EX validator, 12/12 | PASS |
| Canonical two-field `selected_case` | DU schema and candidate | schema review plus candidate inspection | PASS |
| WRONG_ATTEMPT semantic preservation | FD vector evidence and FC adapter | hash binding and deterministic source review | PASS |
| One candidate across accounts | candidate/runtime files and Phase B seal | filesystem count, SHA-256, byte comparison | PASS |
| DU structural/semantic/cryptographic/constitutional gates | canonical DU stdout | one authoritative DU invocation | PASS |
| EB candidate-bound validation | EB failure output | one authoritative EB invocation | FAIL |
| EE runtime-consumer binding | no EE invocation | correctly gated by EB failure | NOT_RUN |
| Candidate immutable after failure | SHA-256 before/after | deterministic rehash | PASS |
| Zero retry and repair | Phase C/D counters | independent reduction | PASS |
| Zero operational progression and credit | Phase A/B/C/D counters | independent reduction | PASS |
| E05 and WRONG_ATTEMPT frontier unchanged | FA/EM lineage and FD reduction | deterministic comparison | PASS |
| G48 exact six-section structure | this report | heading validation | PASS |
| JSON unique keys, inner hashes, cross-bindings | FD JSON evidence | final deterministic validation | PASS |
| Whitespace validity | repository diff | `git diff --check` | PASS |
| Current telemetry benchmark | no `/status` interface available | direct observation unavailable | NOT_RUN |

# 5. Repository Mutation Summary

## Bounded Files

Created files: 11 across the complete FD generation, comprising two authenticated persisted Account 1 artifacts, the vector evidence, builder, one candidate, one byte-identical runtime projection, Phase B/C/D evidence, this report, and the final validation seal. `FILES_CREATED = 11`; `FILES_MODIFIED = 0`; `LINES_ADDED = 1202`; `LINES_REMOVED = 0`; `ELAPSED_TIME = NOT_MEASURED`.

The authoritative failure did not create an EB receipt. No historical file was modified.

## Governance Efficience

- `PHASE_A_RECONSTRUCTION_COUNT = 0`.
- `EXISTING_FD_ARTIFACT_RECONSTRUCTION_COUNT = 0`.
- `COMMON_SUBSTRATE_RECONSTRUCTION_COUNT = 0`.
- `NEW_COMMON_COMPONENT_COUNT = 0`.
- `NEW_COMMON_INFRASTRUCTURE_COUNT = 0`.
- `TOTAL_FD_CANDIDATE_COUNT = 1`.
- `SECOND_CANDIDATE_COUNT = 0`.
- `REPLACEMENT_CANDIDATE_COUNT = 0`.
- `AUTOMATIC_RETRY_COUNT = 0`.
- `REPAIR_AND_CONTINUE_COUNT = 0`.
- `MATERIALIZATION_COUNT = 0`; `VM_CREATION_COUNT = 0`; `QEMU_EXECUTION_COUNT = 0`.

Persisted SPCE state avoided repeating Phase A, the adapter, EX, history reconstruction, and any execution replay. `OVERENGINEERING_RISK = LOW`: account change created no duplicate persisted artifact or common infrastructure; the five-field placement defect remained vector-local. The terminal EB failure is an orchestration defect and remains explicit.

## EX Amortization

- `CERTIFIED_COMMON_COMPONENTS_AVAILABLE = 17`.
- `CERTIFIED_COMMON_COMPONENTS_APPLICABLE = 17`.
- `CERTIFIED_COMMON_COMPONENTS_REUSED = 17`.
- `CERTIFIED_COMMON_COMPONENTS_RECONSTRUCTED = 0`.
- `COMMON_VALIDATORS_REUSED = 3`; `COMMON_VALIDATORS_CREATED = 0`.
- `VECTOR_SPECIFIC_COMPONENT_COUNT = 3` (persisted adapter, vector evidence, bounded builder).
- `REUSE_ARCHITECTURE_REGRESSION = NO`.
- `EX_AMORTIZATION_RESULT = PASS__COMMON_REUSE_DOMINATED__BOUNDED_VECTOR_SCHEMA_DELTA`.

## Reuse Impact Assessment

1. Katere obstojece certificirane zmogljivosti se ponovno uporabijo? Vseh 17 uporabljivih komponent EX ter kanonicni DU, EB in EE validatorji; EZ staticna vezava in FC WRONG_ATTEMPT semantika se ponovno uporabijo kot tocno vezana podpora.
2. Katere nove zmogljivosti, ce sploh, nastanejo? Samo omejena vektorska predstavitev WRONG_ATTEMPT, graditelj in en kandidat; nova skupna zmogljivost ne nastane.
3. Ali katera obstojeca zmogljivost postane nedosegljiva? Ne; `CAPABILITY_REACHABILITY_LOSS = NONE_PROVEN`.
4. Ali implementacija ustvarja vzporedni tok? Ne; `PARALLEL_FLOW_CREATED = NO` in `DUPLICATE_PROOF_PATH_CREATED = NO`.
5. Ali zmanjsuje ali povecuje stevilo produkcijskih poti? Ne; `PRODUCTION_PATH_DELTA = 0`.

`CERTIFIED_COMPONENT_REUSE_COUNT = 17`; `PERSISTED_FD_ARTIFACT_REUSE_COUNT = 2`; `NEW_COMMON_COMPONENT_COUNT = 0`; `VECTOR_SPECIFIC_COMPONENT_COUNT = 3`; `PRODUCTION_PATH_DELTA = 0`.

## Token Benchmark

`CODEX_SESSION_ID`, `CONTEXT_TOTAL`, start/end context use, start/end context remaining, 5h and 7d start/end limits, all deltas, and elapsed time are `NOT_MEASURED` because no direct `/status` or equivalent interface was available. Previous-session telemetry remains Human-supplied contextual evidence only and is not current-account telemetry.

## Human Control Boundary

Index remains empty. No stage, commit, push, reset, clean, stash, materialization, VM, boot, QEMU, P11, E05 execution, E05 credit, P12, production change, second vector, second candidate, repair, retry, or automatic continuation occurred. `HUMAN_AUTHORIZATION_REQUIRED = YES`; `AUTO_CONTINUABLE = NO`.

# 6. Certification Verdict

FAIL_CLOSED__CROSS_ACCOUNT_SPCE_CONTINUATION_AUTHENTICATED__WRONG_ATTEMPT_SCHEMA_ALIGNED__DU_PASS__EB_VALIDATION_PROFILE_INVALID__EE_NOT_RUN__REPOSITORY_ONLY
