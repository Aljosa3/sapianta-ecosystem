# 1. Implementation Summary

Generation: G77-256JZ

Report identity: G77_256JZ_G48_IMPLEMENTATION_REPORT_V1

Mode: `REPOSITORY_ONLY__NO_HUMAN_AUTHORITY__NO_OPERATION`

Reporting standard: G48 Constitutional Evidence Reporting Standard V1.d

Constitutional baseline: `constitutional-governance-finalize-v1`

Authenticated entry: branch `g77-256fl-wrong-attempt-preboot-blocker`; HEAD `673b8ce72c09252c9cf462ac4c96878a8dbad06c`; tree `3ca4f1f0a695edf97680e5ebc973a1a52029860d`; subject `G77-256JY localize FM authority digest handoff blocker`; origin `git@github.com:Aljosa3/sapianta-ecosystem.git`; direct remote branch HEAD `673b8ce72c09252c9cf462ac4c96878a8dbad06c`; clean worktree and empty index before the first JZ mutation.

The unchanged nested authority was clean, detached, and pinned at tag `sapianta-system-nested-authority-3183bab-v1`, HEAD `3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree `7c32ec05efc2be43297849bc38ec8766514a523d`, with read-only remote tag equality.

Objective: close only the JY caller-construction defect by adding an exact authenticated authority-digest-preserving FM invocation binding that is built and validated before any future authority consumption. The builder accepts the canonical authority handoff path, not a caller/provider digest. It derives SHA-256 from the exact canonical handoff bytes, places that value into all sealed digest fields and the final FM argv, and immediately revalidates the envelope against independently re-read repository files.

JY was authenticated from committed evidence. Its correct canonical handoff digest is `7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d`; the caller supplied the 63-character value `7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9`, omitting the final `d`. Shell/CLI transport preserved that literal and FM correctly failed closed at `HEX_64` before PRE. The JY authority remains historical, consumed, nonreusable, nontransferable, and closed for operation. Its bytes are used here only as a committed repository test fixture; the binding is explicitly not authority and does not authorize execution.

Modified modules:

- `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: one existing-owner production mutation adding pure build/validate functions; no execution call was added.
- `.github/governance/evidence/g77_256jz_fm_authority_digest_handoff_repair_v1/`: five bounded evidence files comprising the sealed binding, formalizer, focused tests, terminal reduction, and this report.

Intentionally unchanged modules: P11, ER, GL, GN, JX runtime/admission separation, JR stable checkout, JV request projection, JT bootstrap separation, and all Human-authority artifacts. The sole production route remains 1 → 1.

# 2. Code Evidence

## Public API and deterministic algorithm

The following representative excerpt is exact; unrelated construction fields are omitted:

```python
def build_preconsumption_invocation_binding(
    *,
    repository_root: Path,
    operation_context: Path,
    live_candidate_binding: Path,
    execution_authority: Path,
) -> dict[str, Any]:
    """Build and seal the exact FM argv without accepting a caller digest.

    This function is pure with respect to governance state: it reads canonical
    repository inputs, writes nothing, consumes no authority, and starts no
    process.  A future orchestration owner must validate its result before any
    one-shot authority-consumption transition and execute the returned argv
    without reconstruction.
    """
```

The builder calls `_authenticated_authority_digest(authority_path)`, whose source is `load_authority(path)`: unique canonical JSON bytes plus the existing authority envelope and inner-seal semantics. It then constructs exactly one `final_fm_argv`, inserting `authority_digest` immediately after `--execution-authority-sha256`. Its public signature has no digest override.

## Public validator

The following equality gate is exact; surrounding schema, field-set, canonical path, argv seal, context digest, zero-counter, and phase checks are omitted:

```python
    for field in (
        "authenticated_canonical_authority_digest",
        "sealed_invocation_authority_digest",
        "final_fm_argv_authority_digest",
    ):
        value = binding.get(field)
        if not isinstance(value, str) or not HEX_64.fullmatch(value):
            raise RuntimeError(f"preconsumption {field} malformed")
        if value != authority_digest:
            raise RuntimeError(f"preconsumption {field} mismatch")
    if binding.get("final_fm_argv") != expected_argv:
        raise RuntimeError("preconsumption final FM argv mismatch")
```

The validator does not trust the sealed fields. It re-resolves the canonical repository files, re-reads and authenticates the authority handoff, re-derives both file digests, reconstructs the expected argv, and requires exact equality. Recomputed unkeyed seals therefore cannot authorize a substitute value.

## Canonical evidence and responsibility boundaries

`G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_V1.json` is sorted compact JSON plus LF. Its inner seal is `72d2aa91a1627a9cae5e4799dc458f32a5ffb364d2196f8d7b71c165b3b2ddd6`; its file SHA-256 is `cbe77d8e611df7fc2505ac43bfdf5967360020ee8e70a3f919f210a71fc5bd9c`. It proves:

`AUTHENTICATED_CANONICAL_AUTHORITY_DIGEST = SEALED_INVOCATION_AUTHORITY_DIGEST = FINAL_FM_ARGV_AUTHORITY_DIGEST = 7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d`.

The binding phase is `BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION`. `binding_is_authority`, `execution_authorized_by_binding`, and `process_started` are false. Caller/provider digest input, authority consumption, and FM operational invocation counts are zero. The existing `main()` and sole `subprocess.run(argv, check=False)` execution site are unchanged.

# 3. Constitutional Self-Assessment

## Verified

- JY cause: correct canonical 64-hex handoff, caller-created 63-hex literal, literal-preserving CLI transport, correct FM `HEX_64` failure, and no PRE.
- Exact full-digest derivation from canonical handoff bytes with no caller/provider digest parameter.
- Sealed preconsumption equality across authenticated handoff, binding fields, and final FM argv.
- Fail-closed detection for the exact JY truncation, 65 characters, wrong nibble, nonhex, case substitution, whitespace, prefix/suffix injection, wrong/stale/unrelated digest, caller/provider substitution, missing argv argument, handoff-to-seal mismatch, and seal-to-argv mismatch.
- Existing FM final-admission semantics retained; one execution call site and production route 1 → 1 retained.
- P11 implementation SHA-256 remains `38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5`.
- All JZ operational counters are zero. No Human authority, consumption, PRE, FM operation, QEMU, VM, operation, request, P11 entry, protected effect, retry, repair retry, or replay occurred.
- EX_REUSED = `VERIFIED__17_OF_17`; EX_RECONSTRUCTED = `VERIFIED__0`.

## Not Verified

- A fresh Human-authorized EXPIRED operational denial before P11 entry is not proven in JZ; that requires a separate commissioning generation.
- E05 remains `VERIFIED__11_OF_18`, frontier `VERIFIED__7_UNSATISFIED_OF_18`, credit `VERIFIED__0`, and EXPIRED `NOT_PROVEN_OPERATIONALLY`.
- HAC / HAI / HAE remain `NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED`; no meanings were invented.
- The compact CCWIM maturity is `ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`.

## Minimal governance reporting

- PROJECT_PROGRESS = `VERIFIED__JZ_REPOSITORY_REPAIR_COMPLETE_WITH_OPERATIONAL_FRONTIER_UNCHANGED`
- PROJECT_PROGRESS_ESTIMATE = `ESTIMATED__REPOSITORY_BINDING_COMPLETE__OPERATIONAL_RECOMMISSIONING_PENDING`
- INFORMAL_PROJECT_PROGRESS_ESTIMATE = `ESTIMATED__ONE_NARROW_OPERATIONAL_GENERATION_REMAINS_FOR_E05_EXPIRED_CASE`
- CONSTITUTIONAL_HEALTH_EVIDENCE = `VERIFIED__FAIL_CLOSED_REPLAY_SAFE_MUTATION_BOUNDED`
- SHADOW_AUTOMATION_STATUS = `NOT_APPLICABLE__NO_SHADOW_AUTOMATION`
- CONSTITUTIONAL_FRONTIER_DISTANCE = `VERIFIED__7_UNSATISFIED_OF_18`
- E05_STATE = `VERIFIED__11_OF_18`; E05_FRONTIER = `VERIFIED__7_UNSATISFIED_OF_18`; E05_CREDIT = `VERIFIED__0`
- GOVERNANCE_EFFICIENCY = `VERIFIED__ONE_EXISTING_OWNER_MUTATION_ONE_CAPABILITY`
- OVERENGINEERING_RISK = `VERIFIED__LOW__NO_NEW_OWNER_ROUTE_REGISTRY_OR_GENERIC_ABSTRACTION`
- COGNITION_PROVENANCE = `VERIFIED__COMMITTED_REPOSITORY_EVIDENCE_AND_DETERMINISTIC_LOCAL_VALIDATION`
- COGNITION_ASSISTED_HANDOFF = `VERIFIED__PROMPT_TO_AUTHENTICATED_REPOSITORY_CONTINUATION`
- CANDIDATE_CAPABILITY = `VERIFIED__PRECONSUMPTION_INVOCATION_BINDING_REPOSITORY_ONLY`
- SHADOW_DESIGN_TARGET = `FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING`
- CONSTITUTIONAL_CONTINUATION_PROGRESS = `VERIFIED__JY_FIRST_BROKEN_EDGE_CLOSED_REPOSITORY_ONLY`
- LAST_VERIFIED_EDGE = `EXACT_AUTHENTICATED_AUTHORITY_DIGEST_PRESERVING_FM_INVOCATION_BINDING_REPOSITORY_VERIFIED`
- FIRST_BROKEN_EDGE = `FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING_NOT_YET_REPROVEN_AFTER_JZ`
- MINIMUM_MISSING_CAPABILITY = `FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY`
- MINIMUM_LEGAL_NEXT_DELTA = `SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_GENERATION`
- ARCHITECTURAL_DELTA_BUDGET = `VERIFIED__ONE_EXISTING_OWNER_PRODUCTION_MUTATION__ALL_OTHER_COUNTS_ZERO__ROUTE_1_TO_1`
- PROOF_YIELD = `VERIFIED__ONE_NEW_REPOSITORY_CAPABILITY__ZERO_NEW_BLOCKER__ZERO_E05_CREDIT__17_REUSED_PROOFS`

Compact CCWIM: CCWIM_MATURITY_LEVEL = `ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION`; AUTHENTICATED_REPOSITORY_CONTINUATION = `VERIFIED__YES`; PREVIOUS_WORKER_CONVERSATION_REQUIRED = `VERIFIED__NO`; PREVIOUS_WORKER_MEMORY_REQUIRED = `VERIFIED__NO`; HANDOFF_RECONSTRUCTION_SUCCESS = `VERIFIED__YES`; HANDOFF_AMBIGUITY_COUNT = `VERIFIED__0`; OBSERVED_ARTIFACT_LEVEL_CROSS_WORKER_DRIFT = `VERIFIED__0`.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   EX 17/17, JY terminal evidence, JX role separation, JR stable runtime checkout, JV GN projection, JT bootstrap separation, FM final admission, GL, GN, ER, P11, the canonical Human-authority handoff representation, and existing hash/schema validators are reused without reconstruction.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   One repository-only capability: exact authenticated authority-digest-preserving preconsumption FM invocation binding.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No. Existing admission, validation, and runtime capabilities remain reachable through the same governed route.

4. Ali implementacija ustvarja vzporedni tok?

   No. The pure builder/validator is held by the existing FM owner and feeds the same launcher argv; it neither executes nor creates an alternate launcher or P11 route.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. Production paths remain exactly 1 → 1, delta 0.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Exact JY cause and counters | committed JY failure and recovery closure | focused JZ and JY regression tests | PASS |
| Canonical digest equality | sealed JZ binding plus FM re-derivation | exact equality test and formalizer | PASS |
| Malformed/substitute rejection | parameterized negative matrix | focused JZ tests | PASS |
| Existing FM final admission | unchanged admission API and strict `HEX_64` gate | relevant FO/FM regression | PASS |
| JX/JY semantics preserved | committed JX/JY evidence; role/substitution/delivery/temporal and Phase-B semantic tests | 11 JX and 15 JY semantic tests pass; historical exact-HEAD/current-file checkpoint guards excluded as generation-bound | PASS |
| Governance conformance | governance test suite | `pytest tests/test_governance_conformance.py` | PASS |
| Conformance engine | canonical engine | `python -m runtime.governance.governance_conformance_engine` | PASS |
| Canonical JSON and inner seals | binding and terminal reduction | formalizer plus focused tests | PASS |
| Python syntax | FM, formalizer, and tests | AST and `py_compile` validation | PASS |
| G48 structure and RIA questions | this report | exact six-H1 and five-question checks | PASS |
| Diff hygiene | complete bounded delta | `git diff --check` | PASS |
| Layer 0 and P11 unchanged | path accounting and exact P11 hash | diff-name and SHA-256 checks | PASS |
| Empty index and no operation | repository state and zero counters | cached-diff and artifact/call-site checks | PASS |

# 5. Repository Mutation Summary

Exact delta: one existing FM owner file modified and five files added under the bounded JZ evidence root. NEW_OWNER_COUNT = 0; NEW_ROUTE_COUNT = 0; NEW_REGISTRY_COUNT = 0; NEW_GENERIC_ABSTRACTION_COUNT = 0; NEW_CONSTITUTIONAL_CONCEPT_COUNT = 0; PRODUCTION_MUTATION_COUNT = 1; P11_IMPLEMENTATION_MUTATION_COUNT = 0; PRODUCTION_ROUTE_BEFORE = 1; PRODUCTION_ROUTE_AFTER = 1; PRODUCTION_ROUTE_DELTA = 0.

The FM change adds only pure read/derive/build/validate behavior. It does not alter `main()`, final admission, PRE receipt creation, QEMU execution, receipt semantics, or P11. No constitutional artifact, Human-authority artifact, route, owner, registry, or generic proof compiler was created. The index is empty; nothing was staged, committed, or pushed.

Proof yield: NEW_VERIFIED_CAPABILITY_COUNT = `VERIFIED__1`; NEW_BLOCKER_LOCALIZED_COUNT = `VERIFIED__0`; E05_CREDIT = `VERIFIED__0`; PROOF_REUSE_COUNT = `VERIFIED__17`.

Frontier after JZ: the exact digest-preserving repository binding is the last verified edge. Fresh EXPIRED operational recommissioning remains the first broken edge and must occur, if authorized, only in a separate fresh Human-authorized commissioning generation.

AUTO_CONTINUABLE = NO

HUMAN_REVIEW_REQUIRED = YES

# 6. Certification Verdict

`A__FM_AUTHORITY_DIGEST_PRESERVING_PRECONSUMPTION_INVOCATION_BINDING_REPOSITORY_VERIFIED`
