# 1. Implementation Summary

G77-256LU proves that the independently Human-authenticated LT capability can
surround exactly one future, separately Human-authorized existing FM
invocation through an exact static binding. No executable adapter, controller,
authority mechanism, receipt format, production owner, production route, or
production file is added or changed.

The authenticated entry is branch
`g77-256fl-wrong-attempt-preboot-blocker`, LT HEAD
`f22fae2529de35eaf8093776c04a6a8e05a097f6`, tree
`921382a2b0f852150037db4c7eff4d9884693211`, subject
`G77-256LT add session-independent one-shot supervision harness`, clean index
and worktree, equal live remote HEAD, with LS HEAD
`8b3bff5ee417333ebe97df3b42e62462b8e21f62` as an ancestor. The nested
authority is clean and detached at HEAD
`3183bab71f8f30397c0309dd2e6d846d14a11f66`, tree
`7c32ec05efc2be43297849bc38ec8766514a523d`, with equal local/live tag
`sapianta-system-nested-authority-3183bab-v1`.

Proof layers remain separate:

- `PRODUCTION SEMANTICS`: unchanged; FM still owns final admission, PRE, the
  one QEMU call site, and POST on the sole FM→ER→P11 route.
- `LT HARNESS CAPABILITY`: independently authenticated, generation-local,
  nonauthority, one-shot, session-independent host supervision.
- `STATIC INTEGRATION READINESS`: proven by an exact, non-executable field
  relation between the future authorized invocation, LT input, FM input,
  receipts, guest evidence, and reducer.
- `SYNTHETIC/STATIC PROOF`: cases A–N and all binding rejections execute with
  static fixture values and never launch a child.
- `OPERATIONAL PROOF`: none in LU; no authority, FM operation, QEMU, VM, or P11.
- `UNKNOWN`: the future terminal operational WRONG_SCOPE outcome remains
  unknown and cannot be inferred from host supervision.

`INTEGRATION_READINESS = PROVEN`

`NEW_CAPABILITY_REQUIRED = NO`

`NEW_CAPABILITY_CREATED = NO`

`PROJECT_STATE = EXACT_LT_TO_EXISTING_FM_STATIC_COMPOSITION_PROVEN__OPERATIONAL_WRONG_SCOPE_PROOF_STILL_REQUIRED`

# 2. Static Integration Evidence

The exact LT child is the unmodified `final_fm_argv` returned by the existing
FM preconsumption binding owner and extended only by the already-existing
committed-review-transition arguments. The authenticated historical LR
instance demonstrates its shape:

```text
/usr/bin/python
.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py
--operation-context <exact future context path>
--operation-context-sha256 <exact future context-file hash>
--live-candidate-binding <exact future candidate path>
--execution-authority <exact future authority path>
--execution-authority-sha256 <exact future authority-file hash>
--committed-review-transition <exact future transition path>
--committed-review-transition-sha256 <exact future transition-file hash>
```

The historical values are evidence only. They are not reusable operational
inputs. Every operational placeholder above must be materialized freshly after
a new Phase-A object and separate Human decision.

Answers to the exact integration questions:

| Question | Static answer and authenticated basis |
|---|---|
| A | The exact child is the existing FM `final_fm_argv` above; FM and LR binding code authenticate its builder and hash. |
| B | Yes. Its second argv element is the existing FM launcher; no replacement executable or route is introduced. |
| C | Yes. LT seals opaque lifecycle, invocation, FM-binding, context, admission, and authority identities; neither LT nor LU creates authority. |
| D | Yes. FM performs final admission and writes PRE before its sole `subprocess.run(argv, check=False)` QEMU call. |
| E | Yes. FM writes POST in `finally` after that QEMU call returns or raises. |
| F | Yes. LT events state `authority_effect = NONE`, `consumability = NONAUTHORITY`, and host-supervision-only receipt semantics. |
| G | Yes. LT passes the exact sealed argv and working directory to its sole child launch site without reconstructing FM inputs. |
| H | Yes. GN, ER, and P11 remain downstream of the unchanged FM/QEMU route and are not referenced as LT owners. |
| I | Yes. The lawful order is exact seal, authority consumption, one exclusive LT reservation, and at most one FM child. |
| J | Yes. LT forbids relaunch from existing reservation, STARTED, RUNNING, TERMINATED, malformed, stale, or UNKNOWN state. |
| K | Yes. LT terminal/UNKNOWN evidence may be an independent reducer input, but cannot prove WRONG_SCOPE, P11=0, or protected effect=0. |
| L | Yes. Route count remains `1 -> 1`; LT surrounds rather than replaces the exact FM child. |

Minimum exact binding relation:

| Source identity | Bound destination | Rule |
|---|---|---|
| future lifecycle ID | LT lifecycle ID | exact equality |
| future invocation ID | LT invocation ID | exact equality |
| future FM binding hash | LT invocation-binding identity | domain-labelled exact equality |
| future context-file hash | LT FM-input identity | domain-labelled exact equality |
| current admission HEAD/tree | LT admission identity | exact pair equality |
| future authority-file hash | LT opaque authority-binding hash | exact equality; nonauthority |
| FM final argv | LT argv | byte-for-byte list equality |
| FM final argv hash | LT argv hash | canonical digest equality |
| repository root | LT working directory | exact absolute path equality |
| FM context receipt paths | FM PRE/POST paths | transitive through exact context hash |
| FM context serial path | direct serial sink | transitive through exact context hash |
| FM context runtime export and output list | guest evidence paths | transitive through exact context hash |
| FM/guest evidence plus LT result | post-op reducer inputs | independent evidence; no proof inflation |
| one-shot/retry limits | LT attempt/retry limits | `1` / `0` |

The exact context file binds the Phase-A lifecycle identities, canonical QEMU
argv, receipt namespace, serial sink, runtime export root, guest-output names,
and sealed assets. Its whole-file hash appears in the exact final FM argv. LT
then seals that entire FM argv and its canonical hash. This transitive relation
preserves identity without adding these fields to LT or changing FM input
semantics.

The mandatory future order is:

`fresh Phase A → separate Human decision → fresh authority → final FM admission → sealed nonauthority LT input → authority consumption → exclusive LT reservation → at most one exact FM child`.

The reservation must not precede authority consumption. If authority is
consumed and the process disappears before reservation or child start, the
authority remains spent and no relaunch is lawful. If reservation is durable
but STARTED is absent, if STARTED exists but RUNNING is absent, if child state
is stale or reused, if FM PRE exists without POST, or if any recovery view is
ambiguous, the result is UNKNOWN or incomplete and relaunch remains forbidden.

Cross-vector and generation reuse was traced through WRONG_ATTEMPT,
WRONG_INPUT, WRONG_CONTRACT, WRONG_PROVENANCE, WRONG_CALLER, FUTURE, EXPIRED,
and LG–LT. LG supplies existing-route WRONG_SCOPE semantics; LI/LJ preserve
context and stable-checkout roles; LK/LQ preserve Phase-A object semantics;
LL/LR show the existing controller-to-FM handoff and one-shot consumption; LM
preserves receipt-parent ownership; LN preserves fail-closed preauthority
admission; LO/LP preserve committed-review transition identity; LS localizes
the terminal-observation edge; LT closes the host-session-lifetime edge.

Reuse candidates before implementation:

| Candidate | Classification |
|---|---|
| sole existing FM operational invocation route | `EXACT_REUSE_POSSIBLE` |
| FM admission interface | `EXACT_REUSE_POSSIBLE` |
| FM PRE receipt | `EXACT_REUSE_POSSIBLE` |
| FM POST receipt | `EXACT_REUSE_POSSIBLE` |
| canonical executed argv | `EXACT_REUSE_POSSIBLE` |
| invocation/context binding | `EXACT_REUSE_POSSIBLE` |
| admission HEAD/tree binding | `EXACT_REUSE_POSSIBLE` |
| authority hash/ID binding | `EXACT_REUSE_POSSIBLE` as opaque future input |
| existing controller-to-FM handoff | `PARTIAL_REUSE`; exact call boundary, future LT handoff only |
| direct serial sink | `EXACT_REUSE_POSSIBLE` |
| guest runtime export/seals | `EXACT_REUSE_POSSIBLE` |
| post-op reducers | `VECTOR_SPECIFIC` |
| LT sealed supervisor input | `EXACT_REUSE_POSSIBLE` |
| LT exact invocation-binding identity | `EXACT_REUSE_POSSIBLE` |
| LT argv hash binding | `EXACT_REUSE_POSSIBLE` |
| existing durable lifecycle/receipt namespace | `PARTIAL_REUSE`; ownership remains separate |

# 3. Constitutional Self-Assessment

Mandatory failure novelty and convergence classification, before and after the
static proof:

`FAILURE_CLASS = PROOF_GAP`

`NOVELTY = NEW_STATIC_INTEGRATION_EVIDENCE__NO_NEW_SEMANTIC_CONSTITUTIONAL_AUTHORITY_OR_PRODUCTION_EDGE`

`AFFECTED_INVARIANT = ONE_HUMAN_DECISION_ONE_AUTHORITY_ONE_CONSUMPTION_AT_MOST_ONE_FM_INVOCATION_AT_MOST_ONE_LT_CHILD_NO_RETRY`

`PREVIOUS_CLOSEST_EDGE = LT_EXACT_INVOCATION_BINDING_TO_SESSION_INDEPENDENT_AT_MOST_ONE_CHILD_AND_TERMINAL_OR_UNKNOWN`

`SEMANTIC_DIFFERENCE = EXACT_LT_TO_EXISTING_FM_COMPOSITION_RELATION_IS_NOW_STATICALLY_AUTHENTICATED`

`PRODUCTION_BEHAVIOR_IMPACT = NONE`

`NEW_CAPABILITY_REQUIRED = NO`

`NEW_PROOF_REQUIRED = YES__STATIC_RELATION_PROVEN_HERE__OPERATIONAL_WRONG_SCOPE_PROOF_REMAINS`

`CONVERGENCE_SIGNAL = EXISTING_FM_INVOCATION_CONTRACT_PLUS_LT_SUPERVISOR_IS_SUFFICIENT_VIA_EXACT_STATIC_BINDING`

`REPETITION_PRESSURE = REDUCED__NO_NEW_INTEGRATION_CAPABILITY_AND_NO_LR_REUSE`

`VERIFICATION_AMPLIFICATION_RISK = LOW_TO_BOUNDED__ONE_STATIC_RELATION_VERIFIER`

This is not a duplicate of LT: LT proves the supervisor in isolation, while LU
proves the exact non-interfering LT↔FM relation. The frontier moves once, only
statically, and no generic integration machinery is created.

Post-analysis cross-vector classification:

| Vector | Reuse result |
|---|---|
| WRONG_ATTEMPT | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| WRONG_INPUT | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| WRONG_CONTRACT | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| WRONG_PROVENANCE | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| WRONG_CALLER | `SEMANTICALLY_EQUIVALENT`; denial proof remains vector-specific |
| FUTURE | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| EXPIRED | `EXACT_REUSE_POSSIBLE` for supervision relation only |
| WRONG_SCOPE | `EXACT_REUSE_POSSIBLE`; no acceptance credit transfers |
| future E05 vectors | `PARTIAL_REUSE`; each retains its acceptance requirement |

Forward compatibility is `STRONGER` for AMBIGUOUS and STALE because ambiguous
or unauthenticated process state is terminal UNKNOWN with no relaunch. It is
`UNCHANGED` for REVOKED, SUPERSEDED, WRONG_SCOPE, and COHERENT_COPY. No vector
becomes weaker.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?

   Existing FM admission, canonical invocation, PRE/POST ownership, direct
   serial capture, guest runtime export and seals, vector reducers, the LT
   supervisor, the sole ER→P11 route, and EX 17/17.

2. Katere nove zmogljivosti (če sploh) nastanejo?

   None. LU adds only a non-executable static relation, read-only verifier,
   synthetic tests, decision evidence, and report.

3. Ali katera obstoječa zmogljivost postane nedosegljiva?

   No.

4. Ali implementacija ustvarja vzporedni tok?

   No. LT surrounds the exact existing FM invocation and cannot launch from
   the LU static proof.

5. Ali zmanjšuje ali povečuje število produkcijskih poti?

   Neither. Production route count remains `1 -> 1`.

`EX_REUSED = VERIFIED__17_OF_17`

`EX_RECONSTRUCTED = VERIFIED__0`

`CONSTITUTIONAL_HEALTH_EVIDENCE = AUTHORITY_CARDINALITY_PRESERVED__OPERATION_CARDINALITY_PRESERVED__NO_RETRY__FAIL_CLOSED_UNKNOWN__NO_AUTHORITY_LAUNDERING__NO_SCOPE_REINTERPRETATION__NO_PROOF_INFLATION__NO_PRODUCTION_PATH_EXPANSION__NO_DUPLICATE_LAUNCH__NO_SYNTHETIC_POST__RECEIPT_OWNERSHIP_PRESERVED__LR_NONREUSE_PRESERVED`

`SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`

`GOVERNANCE_EFFICIENCE = HIGH__LT_AND_EXISTING_FM_CONTRACT_REUSED_WITH_STATIC_BINDING_ONLY`

`OVERENGINEERING_RISK = LOW_TO_BOUNDED`

`CANDIDATE_CAPABILITY = NONE_EXPECTED__STATIC_LT_TO_EXISTING_FM_BINDING_RELATION_ONLY`

`SHADOW_DESIGN_TARGET = HUMAN_DECISION_REJECTION_AND_REAUTHORIZATION_LIFECYCLE__HUMAN_REJECTION_FINALITY`

`IMPLEMENT_NOW = NO`

`HAC = NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN`

`HAI = NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN`

`HAE = NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN`

`COGNITION_PROVENANCE` distinguishes authenticated repository facts,
authenticated Git history, historical durable LR artifacts, static code
analysis, synthetic test results, the explicit transitive-binding inference,
and the future operational result that remains unknown.

`COGNITION_ASSISTED_HANDOFF = EXACT_LT_CHECKPOINT_AND_CAPABILITY__EXACT_STATIC_LT_TO_FM_RELATION__ZERO_AUTHORITY__ZERO_OPERATION__ZERO_E05_CREDIT__FRESH_PHASE_A_REMAINS_SEPARATE_HUMAN_BOUNDARY__NO_OPERATIONAL_PERMISSION_TRANSFER`

# 4. Validation Matrix

Static cases A–N:

| Case | Expected result |
|---|---|
| A exact valid future binding | integration ready |
| B mismatched invocation binding | reject |
| C mismatched admission HEAD/tree | reject |
| D mismatched argv hash | reject |
| E wrong working directory | reject |
| F duplicate supervisor reservation | reject |
| G STARTED/RUNNING exists | no relaunch |
| H TERMINATED exists | no relaunch |
| I UNKNOWN exists | no relaunch |
| J substituted FM executable/route | reject |
| K supervisor attempts PRE/POST ownership | reject |
| L host state attempts WRONG_SCOPE inference | reject |
| M integration metadata broadens scope | reject |
| N old LR authority/lifecycle reuse | reject |

Validation also authenticates the exact LT decision, report, harness, tests and
verifier; the existing FM launcher and context owner; the LR controller,
preconsumption binding and terminal reconstruction; FM argv identity; PRE
before QEMU and POST after QEMU; LT noninterference; one child call site; route
singularity; duplicate exclusion; UNKNOWN/no-relaunch; LR nonreuse; governance
conformance; deterministic conformance; G48 cardinality; and the production
mutation budget.

Historical fixed-head and fixed-byte failures in predecessor regression suites
are predecessor-fixture assertions, not current-successor failures. They must
be classified rather than rewritten. LU does not alter any historical fixture.
The LG–LT sweep result is `114 passed; 27 classified`: the classified set is
limited to older FM/bootstrap byte expectations, historical HEAD/successor
count limits, generation-exclusive dirty-namespace assertions, and the
historically consumed LR/LQ receipt namespace.

All LU tests are static or synthetic and do not call the LT launch/supervise
interfaces. No FM operational invocation, QEMU, VM, ER/P11 operational path,
authority transition, operational PRE/POST, retry, replay, or protected effect
occurs.

# 5. Repository Mutation Summary

LU adds only generation-local evidence: one non-executable static binding
relation, one read-only verifier, one synthetic test module, this G48 report,
and one terminal decision object.

Architectural delta budget:

| Measure | Value |
|---|---|
| production files changed | 0 |
| FM production files changed | 0 |
| GN production files changed | 0 |
| ER production files changed | 0 |
| P11 production files changed | 0 |
| EX production files changed | 0 |
| owner delta | 0 |
| route count | 1 -> 1 |
| registry delta | 0 |
| constitutional concept delta | 0 |

Compact CCWIM:

| Measure | Value |
|---|---|
| Historical LR Human decisions | 1 |
| Historical authority created / consumed | 1 / 1 |
| Historical authority reusable | NO |
| Historical LR operations | 1 |
| Historical retries | 0 |
| LT harness capability | IMPLEMENTED |
| LU authorities created / consumed | 0 / 0 |
| LU operation attempts | 0 |
| LU QEMU / VM starts | 0 / 0 |
| LU P11 entries | 0 |
| Production route count | 1 -> 1 |
| Production capability delta | 0 |
| E05 | 12/18 -> 12/18 |
| LU credit | 0 |
| WRONG_SCOPE | UNSAT |

`CONSTITUTIONAL_CONTINUATION_PROGRESS` keeps two frontiers separate. Historical
operation reaches Human decision → authority creation → FM admission →
authority consumption → one operation → VM boot, after which the terminal
operational result is unproven. Static readiness now reaches LT supervisor
proven → exact LT↔FM composition proven. These proof layers are not merged.

`PROOF_YIELD`:

| Dimension | Result |
|---|---|
| ACCEPTANCE_CREDIT | 0 |
| STATIC_FRONTIER_MOVEMENT | exact LT-to-existing-FM readiness proven |
| OPERATIONAL_FRONTIER_MOVEMENT | 0 |
| REUSE_DISCOVERY | existing FM/LT/receipt/context/evidence/reducer contracts sufficient |
| CAPABILITY_DELTA | 0 |
| UNRESOLVED_EDGE | authenticated terminal operational WRONG_SCOPE denial before P11 |

# 6. Certification Verdict

`LAST_VERIFIED_OPERATIONAL_EDGE = LR_VM_BOOT_DURABLY_EVIDENCED`

`FIRST_UNVERIFIED_OPERATIONAL_EDGE = VM_BOOT_TO_GOVERNED_GUEST_EXECUTION`

`LAST_VERIFIED_STATIC_INTEGRATION_EDGE = EXACT_FUTURE_FM_INVOCATION_CONTRACT_TO_LT_SEALED_INPUT_AND_AT_MOST_ONE_CHILD_STATICALLY_BOUND`

`FIRST_BROKEN_STATIC_INTEGRATION_EDGE = NONE__STATIC_INTEGRATION_READY`

`MINIMUM_MISSING_CAPABILITY = NONE_FOR_LT_TO_EXISTING_FM_STATIC_INTEGRATION`

`MINIMUM_MISSING_PROOF = AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11`

`MINIMUM_LEGAL_NEXT_DELTA = FRESH_PHASE_A_WRONG_SCOPE_REVIEW_OBJECT`

`OPERATIONAL_RETRY_AUTHORIZED = NO`

The minimum next governed delta is a fresh Phase-A WRONG_SCOPE review object,
not an LU operation, LR replay, new authority abstraction, production adapter,
or route. LU creates no operational permission and stops for independent Human
authentication.

A__G77_256LU_LT_TO_EXISTING_FM_STATIC_INTEGRATION_READINESS_PROVEN__ZERO_AUTHORITY__ZERO_OPERATION__ZERO_PRODUCTION_MUTATION__FRESH_PHASE_A_IS_MINIMUM_NEXT_GOVERNED_DELTA__READY_FOR_HUMAN_REVIEW
