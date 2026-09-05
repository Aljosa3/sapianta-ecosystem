# 1. Implementation Summary

Generation: G77-256IC

Report identity: G77_256IC_G48_PREAUTHORIZATION_CHECKPOINT_REPORT_V1

Reporting date: 2026-09-04

Constitutional baseline: `constitutional-governance-finalize-v1`; exact
committed G77-256IB base
`ec2c4997ba62fbaa5e774fc9ba010f6319926c73` /
`887f329b030582f01a49f6c0c97f54ed4f55a818`

Implementation contracts: G77-256IC same-generation continuation directive,
G48 Constitutional Evidence Reporting Standard V1.d, HZ WRONG_PROVENANCE
semantics, IA single-route support, IB preoperational readiness, HX/HP
split-phase operational pattern, FM/GN/GL, DU/EB/EE, P11/CHE/FK, and EX.

Objective:

Recover the interrupted uncommitted G77-256IC state from repository evidence,
complete exactly one nonauthority WRONG_PROVENANCE preauthorization chain,
and stop before Human authority, PRE, FM operational invocation, QEMU, VM boot,
P11 entry, or protected effect.

Implementation scope:

- authenticated the exact IB base, matching remote branch, ancestry, and clean,
  detached, tag-pinned nested authority;
- recovered two untracked IC source files and no prior generated IC identity,
  request, grant, receipt, execution, or reduction artifact;
- repaired the same inherited materializer/test delta where it contained stale
  HP/HO/GY bindings and one invalid IB readiness lookup;
- materialized one exact IB head/tree candidate rebind, byte-identical runtime
  projection, one sealed context, one sealed request, and one GN presentation;
- sealed repository-only validation at the Human authorization barrier.

Modified modules:

- `.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/orchestration/G77_256IC_PREAUTHORIZATION_MATERIALIZER_V1.py` — IC-only nonoperational materialization and validation sealing;
- `.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/tests/test_g77_256ic_preauthorization_barrier_v1.py` — exact IC/IB barrier verification;
- `.github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/` — one pregrant candidate/context/request/presentation/evidence chain and this report.

Intentionally unchanged modules:

- HZ semantics, IA adapter and bootstrap, IB readiness owner, FM sole launcher,
  GN presentation owner, GL admission-equivalence owner, DU/EB/EE, P11/CHE/FK,
  EX, Layer 0, and `sapianta_system`;
- `/home/pisarna/work/sapianta` remained read-only;
- no authority controller, operational launcher, runtime owner, generic
  framework, P11 core change, second route, or G77-256ID was created.

Architectural boundaries preserved:

- `BASE_HEAD = ec2c4997ba62fbaa5e774fc9ba010f6319926c73`;
- `BASE_TREE = 887f329b030582f01a49f6c0c97f54ed4f55a818`;
- `UNCOMMITTED_DELTA = .github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/`;
- remote branch HEAD equals the base HEAD;
- nested authority is clean, detached, and pinned at
  `3183bab71f8f30397c0309dd2e6d846d14a11f66` / `7c32ec05efc2be43297849bc38ec8766514a523d`;
- production route count remains one and all IC changes remain unstaged.

# 2. Code Evidence

## Orchestration Entry Point

The IC materializer has no operational launcher entry point and rejects a
second materialization namespace:

```python
def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise RuntimeError("IC one-shot namespace is not fresh")
    entry = authenticate_entry(args.remote_head)
    ib = authenticate_ib()
```

The only executable top-level branch is materialization or repository-only
validation sealing; it never calls FM `main()`:

```python
if __name__ == "__main__":
    arguments = parse_args()
    if arguments.seal_validation_only:
        finalize_validation()
    else:
        if None in (
            arguments.remote_head,
            arguments.primary_used_percent,
            arguments.secondary_used_percent,
        ):
            raise SystemExit("materialization requires remote and capacity observations")
        materialize(arguments)
```

## Semantic Reduction

The sealed checkpoint preserves the HZ vector boundary:

```python
"independent_mutation_count": 1,
"independent_mutated_coordinate": "provenance_identity",
"dependent_recomputation_count": 1,
"dependent_recomputed_coordinate": "record_identity",
"semantic_mutation_count": 1,
"unrelated_mutation_count": 0,
"expected_differing_fields": ["provenance_identity", "record_identity"],
"authoritative_provenance": "existing protected custody owner-state",
"expected_denial_reason": "operational Human act input_record_identity binding is invalid",
"provenance_specific_comparison_reached": False,
```

Expected denial stage:
`D2 preclaim authority-binding validation before preclaim ledger append, claim,
P11 entry, protected invocation, or protected effect`.

## Canonical Objects and Identities

- `REQUEST_SHA256 = 1a3486563fc2c650561f872e9639e28ad11d5e090e57ec36e39afc8db98400f7`;
- `REQUEST_FILE_SHA256 = 2546938c34898edd0e8fc8609d24b07a74cd77b2773d6353f0ede614717347a4`;
- `OPERATION_ID = G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001`;
- `CANDIDATE_IDENTITY = f3b89e5c87a867e025f63b82150c580823454fb88b0fa6a082fa4ddaa02f1533`;
- `CONTEXT_IDENTITY = 4837e55e8354c44b209d0bd411b6b3b07c3111a1411285c8b91f145e267414de`;
- `CANONICAL_ARGV_IDENTITY = b2be4c56b989dbfde79cdfdcc86354b23c3d4d3d8c3b80b06aaead99336d4bf9`;
- `GN_PRESENTATION_SHA256 = 1e1df925922dbde924c17f46189b40ed3e39968b772c4536d081fa48d1c79051`;
- `CHECKPOINT_INNER_SHA256 = 5a1c04e726b8ab27742c8c17c5ad1062bb331e8824a43fbb6239adcabe5b0f15`;
- `VALIDATION_INNER_SHA256 = 8abbf6a2e7e528d1c90058b309bb59f2efc555d88da6412ea3fd92c4c2ab2fbe`.

Candidate and runtime bytes are identical. The context binds the exact IB
HEAD/TREE, IA adapter, IA NoCloud image, operation-scoped checkout, one
canonical argv, `-nic none`, and zero retry/repair/replay policy. No future
commit identity appears.

## Responsibility Boundaries

`REQUEST != AUTHORIZATION`. The request and GN presentation both state that
they are nonauthority. Validation sealing fails if any grant, authority
handoff, PRE/post receipt, serial output, or guest operation output exists.

# 3. Constitutional Self-Assessment

## Verified

- `IC_OPERATION_ID_STATUS = VERIFIED`;
- `IC_CANDIDATE_STATUS = VERIFIED`;
- `IC_RUNTIME_PROJECTION_STATUS = VERIFIED`;
- `IC_CONTEXT_STATUS = VERIFIED`;
- `IC_REQUEST_STATUS = VERIFIED`;
- `IC_GN_PRESENTATION_STATUS = VERIFIED`;
- `HUMAN_OPERATIONAL_AUTHORITY_STATUS = NOT_PROVEN` with durable count zero;
- `AUTHORITY_CONSUMPTION_STATUS = NOT_PROVEN` with durable count zero;
- `PRE_STATUS = NOT_PROVEN` with durable count zero;
- `FM_OPERATIONAL_STATUS = NOT_PROVEN` with durable count zero;
- `QEMU_STATUS = NOT_PROVEN` with durable count zero;
- `VM_STATUS = NOT_PROVEN` with durable count zero;
- `OPERATION_ATTEMPT_STATUS = NOT_PROVEN` with durable count zero;
- `REDUCTION_STATUS = NOT_APPLICABLE` before operation;
- WRONG_PROVENANCE formalization, repository capability, route support,
  current committed IA binding, and preoperational readiness are `VERIFIED`;
- WRONG_PROVENANCE operational capability remains `NOT_PROVEN`;
- E05 is authenticated as 9/18; no IC credit has been awarded.

## Reuse Impact Assessment

- `REUSED_CERTIFIED_CAPABILITY_SET = VERIFIED__HZ_IA_IB_HX_HP_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_17_OF_17_GOVERNANCE_LAYER_0`;
- `NEW_CAPABILITY_SET = VERIFIED__NONE__IC_OPERATION_SCOPED_PREAUTHORIZATION_EVIDENCE_ONLY`;
- `UNREACHABLE_PREEXISTING_CAPABILITY_SET = VERIFIED__EMPTY`;
- `PRODUCTION_ROUTE_BEFORE = VERIFIED__1`;
- `PRODUCTION_ROUTE_AFTER = VERIFIED__1`;
- `PRODUCTION_ROUTE_DELTA = VERIFIED__0`;
- `NEW_GENERIC_FRAMEWORK_COUNT = VERIFIED__0`;
- `NEW_AUTHORITY_LAYER_COUNT = VERIFIED__0`;
- `NEW_PRODUCTION_ROUTE_COUNT = VERIFIED__0`;
- `NEW_RUNTIME_OWNER_COUNT = VERIFIED__0`.

Existing certified capabilities are reused; no existing capability becomes
unreachable, no parallel flow is created, and the production path count does
not change.

## Infrastructure Amortization

- `DID_IC_REQUIRE_NEW_COMMON_INFRASTRUCTURE = VERIFIED__NO`;
- `DID_IC_REQUIRE_NEW_VECTOR_SPECIFIC_INFRASTRUCTURE = VERIFIED__NO`;
- `DID_IC_REQUIRE_NEW_GENERIC_FRAMEWORK = VERIFIED__NO`;
- `DID_IC_REQUIRE_NEW_AUTHORITY_LAYER = VERIFIED__NO`;
- `DID_IC_REQUIRE_NEW_RUNTIME_OWNER = VERIFIED__NO`;
- `DID_IC_REQUIRE_NEW_PRODUCTION_ROUTE = VERIFIED__NO`;
- `DID_IC_REQUIRE_P11_CORE_CHANGE = VERIFIED__NO`;
- `DID_IC_REUSE_HZ_REPOSITORY_CAPABILITY = VERIFIED__YES`;
- `DID_IC_REUSE_IA_ROUTE_SUPPORT = VERIFIED__YES`;
- `DID_IC_REUSE_IB_READINESS = VERIFIED__YES`;
- `DID_IC_REUSE_HX_OPERATIONAL_PATTERN = VERIFIED__YES`;
- `DID_IC_REUSE_FM_GN_GL = VERIFIED__YES`;
- `DID_IC_REUSE_DU_EB_EE = VERIFIED__YES`;
- `DID_IC_REUSE_P11_CHE_FK = VERIFIED__YES`;
- `DID_IC_REUSE_EX_17_OF_17 = VERIFIED__YES`;
- `GENERATIONS_SINCE_E05_9_OF_18 = VERIFIED__5`;
- `E05_CREDITS_SINCE_9_OF_18 = VERIFIED__0`;
- `OPERATIONAL_ATTEMPTS_SINCE_E05_9_OF_18 = VERIFIED__0`;
- `E05_GENERATIONS_PER_CREDIT = NOT_MEASURED__ZERO_NEW_CREDIT_DENOMINATOR`;
- `OPERATIONAL_ATTEMPTS_PER_CREDIT = NOT_MEASURED__ZERO_NEW_CREDIT_DENOMINATOR`;
- `MARGINAL_E05_GENERATION_COST = NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT`;
- `MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT = NOT_MEASURED__ZERO_NEW_CREDIT_DENOMINATOR`;
- `INFRASTRUCTURE_AMORTIZATION_SIGNAL = ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_TOKEN_OR_MONETARY_INFERENCE`.

## CCWIM

- `CCWIM_MATURITY_LEVEL = ESTIMATED__L4_LIKE__NO_L5_CLAIM`;
- `CROSS_WORKER_STATE_RECOVERY_LEVEL = VERIFIED__REPOSITORY_AUTHENTICATED_UNCOMMITTED_DELTA`;
- `REPOSITORY_DERIVED_CONTEXT_RATIO = ESTIMATED__DOMINANT`;
- `HUMAN_HANDOFF_INFORMATION_REQUIRED = VERIFIED__CHECKPOINT_SCOPE_PROHIBITIONS_AND_REPOSITORY_LOCATORS`;
- `PREVIOUS_WORKER_CONVERSATION_REQUIRED = VERIFIED__NO`;
- `PREVIOUS_WORKER_IDENTITY_REQUIRED = VERIFIED__NO`;
- `PREVIOUS_WORKER_MEMORY_REQUIRED = VERIFIED__NO`;
- `AUTHENTICATED_REPOSITORY_CONTINUATION = VERIFIED__YES`;
- `INTER_GENERATION_CROSS_WORKER_CONTINUATION = NOT_APPLICABLE__SAME_IC_GENERATION`;
- `INTRA_GENERATION_CROSS_WORKER_CONTINUATION = VERIFIED__YES`;
- `UNCOMMITTED_DELTA_RECOVERY = VERIFIED__YES`;
- `AUTHORITY_STATE_RECOVERY = VERIFIED__NOT_GRANTED__ALL_OPERATIONAL_COUNTERS_ZERO`;
- `CROSS_WORKER_CONSTITUTIONAL_DRIFT = VERIFIED__0`;
- `HANDOFF_SUFFICIENCY_STATUS = VERIFIED`;
- `HANDOFF_STATE_COMPLETENESS = VERIFIED__COMPLETE_FOR_PREGRANT_BARRIER`;
- `HANDOFF_RECONSTRUCTION_REQUIRED = VERIFIED__YES`;
- `HANDOFF_RECONSTRUCTION_SUCCESS = VERIFIED__YES`;
- `HANDOFF_AMBIGUITY_COUNT = VERIFIED__0`;
- `UNAUTHENTICATED_HANDOFF_ASSUMPTION_COUNT = VERIFIED__0`.

## Required Metrics and Cognition Provenance

- `PROJECT_PROGRESS_ESTIMATE = NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`;
- `CONSTITUTIONAL_HEALTH_EVIDENCE = VERIFIED__FAIL_CLOSED_PREGRANT_BARRIER_AND_ZERO_OPERATION`;
- `SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`;
- `CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`;
- `E05_FRONTIER_DISTANCE = VERIFIED__9_OF_18_REMAIN`;
- `SELECTED_E05_LOCAL_FRONTIER_DISTANCE = ESTIMATED__ONE_HUMAN_AUTHORIZED_IC_OPERATIONAL_PHASE`;
- `GOVERNANCE_EFFICIENCE = ESTIMATED__TARGETED_AFFECTED_FRONTIER`;
- `ARCHITECTURAL_GOVERNANCE_EFFICIENCE = VERIFIED__ONE_ROUTE_RETAINED`;
- `PROOF_REUSE_EFFICIENCY = VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED`;
- `COGNITION_ASSISTED_HANDOFF = VERIFIED__REPOSITORY_AUTHENTICATED_SAME_GENERATION_CONTINUATION`;
- `AIGOL_CODEX_WORK_SHARE = NOT_MEASURED`;
- `OVERENGINEERING_RISK = ESTIMATED__LOW`;
- `PROOF_PROCESS_OVERHEAD_RISK = ESTIMATED__MODERATE`;
- `COGNITION_PROVENANCE = VERIFIED__GIT_IB_RECOVERED_IC_DELTA_HZ_IA_IB_HX_HP_HT_HV_HW_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_AND_FRESH_IC_EVIDENCE`;
- `CANDIDATE_CAPABILITY = VERIFIED__EXACT_IB_HEAD_TREE_REBIND`;
- `WRONG_PROVENANCE_CANDIDATE_CAPABILITY = VERIFIED`;
- `WRONG_PROVENANCE_REPOSITORY_CAPABILITY = VERIFIED`;
- `WRONG_PROVENANCE_ROUTE_SUPPORT = VERIFIED`;
- `WRONG_PROVENANCE_BINDING_STATUS = VERIFIED__CURRENT_COMMITTED_IA_LIVE_BINDING`;
- `WRONG_PROVENANCE_PREOPERATIONAL_READINESS = VERIFIED`;
- `WRONG_PROVENANCE_OPERATIONAL_CAPABILITY = NOT_PROVEN`;
- `SHADOW_DESIGN_TARGET = VERIFIED__FORMALIZE_REUSE_BIND_VERIFY_PRESENT_STOP`;
- `CONSTITUTIONAL_CONTINUATION_PROGRESS = VERIFIED__PREAUTHORIZATION_COMPLETE_AT_HUMAN_BARRIER`;
- `PROMPT_CONTEXT_REUSE_RATIO = NOT_MEASURED`;
- `TOKEN_BENCHMARK = NOT_MEASURED`;
- `LLM_COST_REDUCTION_RATIO = NOT_MEASURED`;
- `LCRR = NOT_MEASURED`;
- `EXPECTED_NEXT_CREDIT_GENERATION_COUNT = ESTIMATED__ONE_CURRENT_IC_OPERATIONAL_PHASE_AFTER_EXACT_GRANT`.

Previous-worker prose was used only as a locator. It supplied no proof.

## Not Verified

- Human operational authority, authority consumption, PRE, FM operational
  invocation, QEMU, VM creation/boot, operation attempt, observed denial,
  operational raw evidence, authoritative/independent operational reductions,
  reducer agreement, WRONG_PROVENANCE operational capability, and IC E05
  credit are not proven because the Human barrier has not been crossed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact IB local/remote base | Git HEAD/TREE/subject/origin and remote query | Exact authentication and remote `ls-remote` | PASS |
| Stable ancestry and nested authority | HX/HY/HZ/IA/IB lineage; pinned nested tag | ancestry checks; nested status/HEAD/TREE/tag | PASS |
| Recovered delta and duplicate prevention | initial two-file enumeration; absent IC/transient objects | full file search and namespace checks | PASS |
| IB readiness and E05 9/18 | sealed IB terminal reduction | inner seal and exact-field reconstruction | PASS |
| HZ semantics and IA/IB/GN/GL chain | 135 current-applicable tests | pytest with four superseded historical assertions explicitly deselected | PASS |
| IC candidate/runtime/context/request/presentation barrier | IC focused suite | pytest, 6/6 | PASS |
| DU/EB/EE | IC receipts and owner verification | materialization-time validation and focused suite | PASS |
| IB negative matrix | 21-case sealed IB matrix | authenticated status and affected regression tests | PASS |
| Four-vector closed set | WRONG_ATTEMPT/INPUT/CONTRACT/PROVENANCE | authenticated IB evidence and affected tests | PASS |
| P11/CHE/FK non-regression | construction/consumer/CHE/FK tests | pytest, 72/72 | PASS |
| EX common proof substrate | certified EX validator | 12/12; 17 certified components reused | PASS |
| Governance and Layer 0 | conformance tests and engine | 9/9; engine 20/20, CONFORMANT, zero warnings/violations | PASS |
| Canonical JSON, duplicate keys, and seals | all IC JSON and Python literal dictionaries | canonical load, duplicate-key hooks, AST scan, inner-seal checks | PASS |
| Sole FM/QEMU route | committed FM AST | one `main`, one `subprocess.run` call site | PASS |
| No authority or operation | absent grant/handoff/receipts/serial/guest results; zero checkpoint counters | forbidden-artifact scan and focused suite | PASS |
| `git diff --check`; empty index | Git worktree | exact commands | PASS |
| Operational denial and E05 credit | no operation authorized | intentionally not run before Human grant | NOT_APPLICABLE |

The four deselected assertions are historical HY entry, pre-current IA
checkout, and two pre-IB entry/materialization assertions. Their historical
artifacts are unchanged; current IB state is validated independently.

# 5. Repository Mutation Summary

All G77-256IC files are untracked and unstaged. No tracked file, index entry,
commit, tag, branch, remote, nested-authority file, or historical/composite
worktree was mutated.

Pregrant counters:

```text
HUMAN_OPERATIONAL_AUTHORITY = 0
AUTHORITY_CONSUMPTION = 0
PRE = 0
FM_OPERATIONAL_LAUNCHER_INVOCATION = 0
QEMU = 0
VM_CREATION = 0
VM_BOOT = 0
OPERATION_ATTEMPT = 0
WRONG_PROVENANCE_OPERATION = 0
REQUEST = 0
P11_ENTRY = 0
PROTECTED_INVOCATION = 0
PROTECTED_EFFECT = 0
RETRY = 0
REPAIR_RETRY = 0
REPLAY = 0
E05_CREDIT = 0
E05_BEFORE_IC = 9/18
E05_AFTER_IC = 9/18
```

The sealed request exists, but its operational `REQUEST` counter is zero and
it grants no authority.

Terminal frontier: present the following exact sentence and stop. It is not
authority unless supplied afresh by the Human in this same IC generation:

```text
I explicitly authorize G77-256IC request 1a3486563fc2c650561f872e9639e28ad11d5e090e57ec36e39afc8db98400f7 for operation G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001, candidate f3b89e5c87a867e025f63b82150c580823454fb88b0fa6a082fa4ddaa02f1533, context 4837e55e8354c44b209d0bd411b6b3b07c3111a1411285c8b91f145e267414de, and canonical argv b2be4c56b989dbfde79cdfdcc86354b23c3d4d3d8c3b80b06aaead99336d4bf9, starting from E05 9/18, subject to exactly one authority consumption, PRE, FM invocation, no-network QEMU, VM creation, VM boot, and operation attempt, with zero retry, repair, replay, or protected effect.
```

# 6. Certification Verdict

VERIFIED__G77_256IC_PREAUTHORIZATION_COMPLETE__PRESENT_EXACT_REQUEST_AND_STOP
