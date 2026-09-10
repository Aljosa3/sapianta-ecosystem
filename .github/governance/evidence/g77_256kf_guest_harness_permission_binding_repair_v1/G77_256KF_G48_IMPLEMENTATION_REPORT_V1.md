# 1. Implementation Summary

Generation: G77-256KF — GUEST HARNESS PERMISSION BINDING REPAIR V1

Report identity: `G77_256KF_G48_IMPLEMENTATION_REPORT_V1`

Reporting date: 2026-09-10

Constitutional baseline: committed KE HEAD `cdfc2ae475a58d20a6ba48d6a0e573c7dbcfcefa`, tree `ab41528f8a9b2c475f5a44cc61a58144050dd40d`, subject `G77-256KE reduce terminal guest custody failure`, plus nested authority `3183bab71f8f30397c0309dd2e6d846d14a11f66` / tree `7c32ec05efc2be43297849bc38ec8766514a523d`.

Implementation contracts: G77-256KF recovery directive; G48 Constitutional Evidence Reporting Standard V1; committed KE terminal and guest-custody failure evidence; constitutional baseline `constitutional-governance-finalize-v1`.

Objective:

Repair only the authenticated guest-custody projection-root traversal failure in the existing FM materialization owner and verify that permission contract repository-only.

Implementation scope:

- preserve owner-private `0700` construction;
- bind final projection-root presentation to `0701` after all projected sources are written;
- validate the final root binding in the existing guest-adapter proof;
- formalize pre-repair denial, post-repair access, and negative permission predicates without entering an operational route.

Modified modules:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: one existing operational binding owner receives the final root-mode binding and validation.
- `.github/governance/evidence/g77_256kf_guest_harness_permission_binding_repair_v1/`: repository-only formalizer, regression tests, canonical reduction, and this report.

Intentionally unchanged modules:

- committed KE evidence and its consumed, nonreusable, nontransferable Human authority;
- P11 implementation, ER harness, GN/JZ/JX/JR/KD/KB owners, EX certificate, nested authority, and the sole production route.

Architectural boundaries preserved:

- no new owner, route, registry, generic abstraction, constitutional concept, authority path, retry, replay, P11 mutation, QEMU invocation, or VM activity;
- `CERTIFIED != AUTHORIZED`; `REPOSITORY_VERIFIED != OPERATIONALLY_PROVEN`;
- `EXPIRED = NOT_PROVEN_OPERATIONALLY`; E05 remains `VERIFIED__11_OF_18` with `VERIFIED__7_UNSATISFIED_OF_18` and zero credit.

# 2. Code Evidence

## Public API and orchestration entry point

The existing public owner remains `materialize_operation_state`; no new entry point exists. Exact bounded construction and presentation excerpt:

```python
adapter_projection_root.mkdir(
    mode=GUEST_HARNESS_PROJECTION_ROOT_CONSTRUCTION_MODE,
    parents=False,
    exist_ok=False,
)
adapter_source = repository_root / adapter_binding["source_path"]
adapter_bytes = adapter_source.read_bytes()
Path(adapter_binding["projected_path"]).write_bytes(adapter_bytes)
Path(adapter_binding["bootstrap_projected_path"]).write_bytes(adapter_bytes)
context_owner_source = repository_root / FRESH_OPERATION_CONTEXT_OWNER
context_owner_projection = (
    adapter_projection_root
    / FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME
)
context_owner_projection.write_bytes(context_owner_source.read_bytes())
adapter_projection_root.chmod(
    GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE
)
```

The caller is the existing generation preauthorization materializer chain. The authoritative owner is `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py:materialize_operation_state`; the current interface is `FM.materialize_operation_state`; the adaptation boundary is the existing FM adapter projection root after complete owner-private materialization and before read-only guest use.

## Semantic reductions and canonical data model

`G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json` is compact canonical JSON plus LF, wrapped by an inner SHA-256 seal. It binds entry identity, nested authority, KE terminal/blocker evidence, exact delta reconstruction, permission contract, zero counters, E05 non-credit, EX reuse, architecture, frontier, CCWIM, validation scope, and artifact identities.

## Public validators and deterministic algorithms

The existing validator now requires the final root binding:

```python
if projection_root.stat().st_mode & 0o777 != (
    GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE
):
    raise RuntimeError("adapter projection root permission binding mismatch")
```

The KF formalizer evaluates the applicable POSIX permission triad for host owner `1000/1000` and custody `3/3`. The exact mode delta is one bit: `0700 ^ 0701 == 0001`. Before repair, custody has no root permission and fails parent search. After repair, custody has only other-search on the root. The committed projected Python sources are Git mode `100644`, so other-read is independently present while other-write and all execute bits are absent.

The authenticated adapter calls `importlib.util.spec_from_file_location`, `module_from_spec`, and `specification.loader.exec_module`. Therefore the interpreter requires parent search plus source read; the Python source execute bit is not required.

## Responsibility boundaries

The guest harness is still exported by exactly one `-virtfs` argument ending `security_model=none,readonly=on`. Host ownership is unchanged; custody receives no ownership, write permission, UID substitution, alternate projection, copy bypass, root execution, or source execute permission. Construction stays private until all source bytes exist.

# 3. Constitutional Self-Assessment

## Verified

- Entry is authenticated at exact local/remote HEAD `cdfc2ae475a58d20a6ba48d6a0e573c7dbcfcefa`, tree `ab41528f8a9b2c475f5a44cc61a58144050dd40d`, and subject `G77-256KE reduce terminal guest custody failure`; the index is empty.
- Nested authority is clean, detached, pinned, and remote-tag-equal at the required commit and tree.
- Provider limit interruption is observed and same-generation KF recovery is permitted; provider capability is not execution authority.
- The initial interrupted delta was exactly the reported launcher `+14/-1` plus 521-line formalizer, totaling `+535/-1`, with no unrelated mutation or cross-worker drift.
- Committed KE terminal is `M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST`; its one authority and one attempt remain terminal and immutable with zero retry, repair-retry, or replay.
- Exact blocker is `PermissionError: [Errno 13] Permission denied: /mnt/dp-harness/sapianta_fresh_operation_context_v1.py`; root cause is authenticated `0700`, owner `1000/1000`, custody `3/3`, and failure at parent traversal before request or P11 entry.
- The smallest mode-bit repair is final root `0701`: it adds only other-search. Root read/write, source write/execute, and guest projection write remain denied.
- EX common proof remains reusable `VERIFIED__17_OF_17`; zero proof is reconstructed. The launcher is not an EX-bound artifact, and EX continues to exclude vector-specific and actual operational facts.
- All KF operational and recovery-specific counters are zero.

## Not Verified

- Guest custody success is not operationally proven.
- EXPIRED denial, P11 behavior on a fresh successor operation, and E05 `12/18` are not proven.
- HAC/HAI/HAE meanings are not asserted: `NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`.

## Minimal governance reporting

`PROJECT_PROGRESS = VERIFIED__KE_GUEST_PERMISSION_BLOCKER_REPAIRED_REPOSITORY_ONLY`

`PROJECT_PROGRESS_ESTIMATE = NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR`

`INFORMAL_PROJECT_PROGRESS_ESTIMATE = ESTIMATED__ONE_PRE_REQUEST_GUEST_CUSTODY_BLOCKER_REMOVED_REPOSITORY_ONLY`

`CONSTITUTIONAL_HEALTH_EVIDENCE = VERIFIED__FAIL_CLOSED_REPOSITORY_ONLY_REPAIR_WITH_ZERO_KF_OPERATIONAL_COUNTERS`

`SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`

`CONSTITUTIONAL_FRONTIER_DISTANCE = NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR`

`GOVERNANCE_EFFICIENCE = ESTIMATED__HIGH__ONE_EXISTING_OWNER_PERMISSION_BINDING_WITH_NO_NEW_ROUTE`

`OVERENGINEERING_RISK = ESTIMATED__LOW__ONE_PERMISSION_EDGE_REPAIR`

`COGNITION_PROVENANCE = VERIFIED__COMMITTED_KE_TERMINAL_RAW_GUEST_RECEIPT_SERIAL_LAUNCHER_AND_CURRENT_REPOSITORY_EVIDENCE_PRIMARY`

`COGNITION_ASSISTED_HANDOFF = VERIFIED__PROVIDER_INTERRUPTED_KF_RECONSTRUCTED_FROM_COMMITTED_AND_UNCOMMITTED_REPOSITORY_EVIDENCE`

`CANDIDATE_CAPABILITY = VERIFIED__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_ONLY`

`SHADOW_DESIGN_TARGET = VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT`

`CONSTITUTIONAL_CONTINUATION_PROGRESS = VERIFIED__KE_TERMINAL_GUEST_PERMISSION_BLOCKER_TO_KF_REPOSITORY_BINDING_REPAIR`

`LAST_VERIFIED_EDGE = GUEST_CUSTODY_PERMISSION_CONTRACT_REPOSITORY_VERIFIED`

`FIRST_BROKEN_EDGE = FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING_NOT_YET_REPROVEN_AFTER_KF`

`MINIMUM_MISSING_CAPABILITY = FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY`

`MINIMUM_LEGAL_NEXT_DELTA = AFTER_KF_COMMIT_AND_HUMAN_REVIEW__SEPARATE_FRESH_OPERATIONAL_GENERATION_SPCE_PHASE_A_PREAUTHORIZATION_ONLY`

`PROOF_YIELD = NEW_VERIFIED_CAPABILITY_COUNT: VERIFIED__1_REPOSITORY_ONLY_PERMISSION_BINDING_CAPABILITY; NEW_BLOCKER_LOCALIZED_COUNT: VERIFIED__0__PRIOR_KE_BLOCKER_REUSED; E05_CREDIT: VERIFIED__0; PROOF_REUSE_COUNT: VERIFIED__17`

Compact CCWIM: maturity `ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`; authenticated repository continuation `VERIFIED__YES`; previous worker conversation required `VERIFIED__NO`; previous worker memory required `VERIFIED__NO`; handoff reconstruction success `VERIFIED__YES`; ambiguity count `VERIFIED__0`; observed artifact-level cross-worker drift `VERIFIED__0`; cross-account recovery `VERIFIED`; provider-interruption recovery `VERIFIED`.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   Committed KE terminal evidence, EX 17/17, KD, KB, JZ, JX, JR, GN, FM, ER, P11, the sole route, and pinned nested authority are authenticated and reused.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   One repository-only guest-harness permission-binding capability.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No authenticated existing capability becomes unreachable.

4. Ali implementacija ustvarja vzporedni tok?

   No. The repair remains in the existing materialization owner and existing route.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. Production routes remain `1 → 1`.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact entry and remote equality | Git HEAD/tree/subject/origin and direct `ls-remote` | deterministic repository and remote probes | PASS |
| Nested clean/detached/pinned/remote-tag equality | nested Git identity and immutable tag | local and direct remote probes | PASS |
| Exact interrupted delta | launcher diff plus original formalizer line count | path inventory and numstat | PASS |
| Committed KE terminal and blocker provenance | sealed terminal, observation, receipt, raw teardown, serial, launcher | hash, seal, field, mount, and identity checks | PASS |
| Pre-repair regression | POSIX triad model for `0700`, `1000/1000`, and `3/3` | dedicated KF suite, 11 passed | PASS |
| Post-repair and minimality | exact `0700 → 0701` one-bit delta plus source `100644` | dedicated KF suite and AST/source review | PASS |
| Negative permission regressions | root read/write, source write/execute, ordering, and read-only mount | dedicated KF suite | PASS |
| Existing owner and no new route | FM launcher diff and P11 identity | hash/diff/AST checks | PASS |
| EX common proof applicability | EX certificate/seal and exclusions | 17-certified matrix and bound-path review | PASS |
| Canonical reduction and seals | KF terminal envelope | replay and canonical-byte test | PASS |
| Applicable repository regressions | KE/KD/KB/JZ/JX/JR/GN nonoperational suites | 117 passed; 16 lifecycle-pinned historical assertions explicitly deselected | PASS |
| Governance conformance | governance test and read-only conformance engine | 9 passed; 20/20 checks, zero violations/warnings | PASS |
| G48, RIA, AST/compile, diff hygiene, empty index | report/source/Git | deterministic structure and syntax checks | PASS |
| Operational guest success and EXPIRED denial | none; prohibited in KF | no operational validation run | NOT_APPLICABLE |

# 5. Repository Mutation Summary

Modified files:

- the existing FM launcher: 14 insertions and one deletion for two mode constants, one fail-closed presentation-mode check, private construction binding, and one final `chmod(0701)`;
- four KF evidence files: formalizer, regression suite, canonical terminal reduction, and report.

Unchanged subsystems:

- KE evidence, P11 implementation, Human authority, EX certificate, nested authority, ER/GN/JZ/JX/JR/KD/KB semantics, and route topology.

API compatibility:

- `materialize_operation_state` signature and caller chain are unchanged. Existing construction and QEMU argument interfaces are unchanged.

Boundary preservation:

- `EXISTING_OPERATIONAL_BINDING_OWNER_MUTATION_COUNT = 1`
- `PRODUCTION_MUTATION_COUNT = 1`
- `P11_IMPLEMENTATION_MUTATION_COUNT = 0`
- `NEW_OWNER_COUNT = 0`; `NEW_ROUTE_COUNT = 0`; `NEW_REGISTRY_COUNT = 0`; `NEW_GENERIC_ABSTRACTION_COUNT = 0`; `NEW_CONSTITUTIONAL_CONCEPT_COUNT = 0`
- `PRODUCTION_ROUTE_BEFORE = 1`; `PRODUCTION_ROUTE_AFTER = 1`
- `ONE_EXISTING_OWNER`; `ONE_EXISTING_ROUTE`; `ONE_PERMISSION_BINDING`; `NO_PARALLEL_FLOW`

Unrelated pre-existing changes:

- None observed. The recovered dirty state authenticated exactly as interrupted KF work.

Historical lifecycle assertions:

- The broad nonoperational sweep first produced 117 passes and 16 expected failures tied to older fixed HEADs, the pre-KF launcher hash, or those generations' then-current mutation sets. Those assertions are inapplicable to the KF lifecycle and were left byte-identical; the applicable rerun passed 117 tests with exactly those 16 deselected.

Operational firewall:

- all 15 KF operational counters are `0`;
- all 13 recovery-specific counters are `0`;
- `E05_STATE = VERIFIED__11_OF_18`; `E05_FRONTIER = VERIFIED__7_UNSATISFIED_OF_18`; `E05_CREDIT = VERIFIED__0`; `EXPIRED = NOT_PROVEN_OPERATIONALLY`;
- `AUTO_CONTINUABLE = NO`; `HUMAN_REVIEW_REQUIRED = YES`.

# 6. Certification Verdict

`A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED`
