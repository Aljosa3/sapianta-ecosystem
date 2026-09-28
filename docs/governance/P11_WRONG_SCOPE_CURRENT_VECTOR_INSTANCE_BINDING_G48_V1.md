# 1. Implementation Summary

Report identity: P11_WRONG_SCOPE_CURRENT_VECTOR_INSTANCE_BINDING_G48_V1.
Generation: P11_WRONG_SCOPE_CURRENT_VECTOR_INSTANCE_BINDING_IMPLEMENTATION.
Reporting date: 2026-09-28.
Constitutional baseline: constitutional-governance-finalize-v1.
Authenticated entry: 9a8f8b15eacf9dcdc55caf3dd48cff89cd728da1,
tree acf32cdc6d164029845dcb9e7fa17bca2b8ba3df,
branch g77-256fl-wrong-attempt-preboot-blocker; clean, upstream/live remote equal.

Implementation contracts: the user's bounded implementation authorization;
JL existing custody temporal-owner contract; JJ CURRENT baseline; LE scope-only
model; JR deterministic guest validity/submission mechanics; G48 reporting
standard. The predecessor's semantic-change hypothesis remains closed.

The existing owner now selects an explicit WRONG_SCOPE instance carrying
preclaim/submission 500 and validity [100,1000). The producer, schema, consumer,
and existing LG guest specialization bind the same instance. Other vectors
retain their existing temporal producer/consumer selection. EXPIRED remains
1000 against [100,1000), yielding EXPIRED.

A necessary binding correction also updates FM's guest checkout selection for
WRONG_SCOPE: the historical LH checkout contains the old consumer and cannot
execute the corrected binding. The same checkout route now authenticates the
requested committed HEAD/TREE and exact consumer, adapter and specification
hashes, including matching working bytes. No second checkout or execution
route is introduced. EXPIRED's stable checkout and hashes are unchanged.

No temporal predicate, policy owner, scope comparator, authority contract,
revocation/supersession behavior, consumption behavior or acceptance requirement
changes. No VM, QEMU, operational method, authority issuance/consumption or
protected effect occurred. All synthetic objects are repository fixtures,
not issued Human authority. E05 remains 12/18, credit delta zero.

# 2. Code Evidence

New minimal instance:
`.github/governance/evidence/p11_wrong_scope_current_binding_v1/WRONG_SCOPE_CURRENT_VECTOR_INSTANCE_V1.json`.
Whole-file SHA-256:
`770b8ca7ee8b3df46268acf12b3a48e48792fc05b48f1e7e1ebd2bd62f35bbbe`.
It binds unchanged JJ and LE source hashes, the existing policy owner, the
CURRENT tuple, scope-only mismatch and `operational_authority=false`.
The single containing implementation commit is its canonical recovery point.

Representative exact producer excerpt (unrelated lines omitted):

```python
    if generation_identity.endswith(WRONG_SCOPE_GENERATION_SUFFIX):
        instance = authenticate_wrong_scope_current_instance(repository_root)
```

The existing `materialize_preclaim_temporal_binding` has no coordinate argument.
`authenticate_wrong_scope_current_instance` authenticates the fixed instance
hash and its source hashes. Existing `validate_preclaim_temporal_binding`
rematerializes and compares the complete binding. The fixed instance uses
JJ's baseline, not JJ's expired mutation; LE establishes both baseline and
presented scope states as CURRENT.

Exact consumer excerpt (unrelated lines omitted):

```python
    if value["generation_identity"].endswith(WRONG_SCOPE_GENERATION_SUFFIX):
        expected.update({
            "vector_specification_path": WRONG_SCOPE_CURRENT_SPECIFICATION_PATH,
            "vector_specification_sha256": WRONG_SCOPE_CURRENT_SPECIFICATION_SHA256,
            "vector_specification_identity": WRONG_SCOPE_CURRENT_SPECIFICATION_IDENTITY,
            "coordinate_unix_ns": 500,
        })
```

Existing seal, owner, producer, generation, operation and full expected-record
checks remain in force. The schema conditions the exact specification tuple
and coordinate on the same generation suffix. It additionally admits the
existing WRONG_SCOPE guest adapter identity/path, which its old enumeration
omitted. It does not accept arbitrary specification identifiers or time values.

LG reuses JR's specialization mechanics: authenticate immutable ER source,
replace its one wall-time validity construction with instance-derived
submission/validity constants, and insert the fixed submission coordinate into
its one existing submission call. The runtime scope mutation remains solely
`wrong_act_value["authority_scope"] = WRONG_SCOPE_ID`; dependent CHE identity
recomputation is unchanged.

The existing native `preclaim_temporal_decision`, `_validate_authority_sources`,
`claim_and_invoke_once`, `submit_human_act`, and `terminate_human_act` function
ASTs match the authenticated entry exactly. No comparator or temporal decision
code changed.

# 3. Constitutional Self-Assessment

## Verified

- Lineage and initial live remote match the authorized target.
- Exact instance/source hashes, deterministic recovery, CURRENT tuple and
  agreement across producer, canonical schema, consumer and guest construction.
- Full context creation and native validation against a real isolated Git
  fixture containing committed corrected sources; no main-worktree commit was
  required to test the checkout binding before acceptance.
- Synthetic guest baseline passes the native complete authority-source/payload
  validation. Only scope is changed, canonical correlation is rebound, and the
  same native validator returns the existing scope-specific denial.
- Existing temporal negatives, EXPIRED behavior and source/coordinate mismatch
  rejection pass. No caller override or authoritative wall clock is added.
- No operational custody method or protected-state initialization is used by
  the focused proof; sentinels fail the proof if those methods are reached.
- Original temporal predicates and scope/authority/consumption method bodies
  are unchanged; the existing 30-case JM/DI regression aggregate passes.
- Historical LD/MA/JJ/JL/JR/LE evidence and commits are not changed.
- SAME_REQUIREMENT_RECOMPUTED = YES.
- SAME_REQUIREMENT_RECOMPUTATION_RESULT = SATISFIED for repository characterization.
- ORIGINAL_TASK_CONTROL_RETURNED = YES; next proof is separately authorized
  operational WRONG_SCOPE acceptance, not another implementation loop.

## Not Verified

Fresh operational readiness, live authority currentness/revocation/supersession,
real guest execution, physical custody, operational scope denial and E05 13/18
are not established. Synthetic baseline validity is not live authority.
No full repository regression or global conformance claim is made.
Historical generation-specific fixtures with old checkout/hash expectations
are not rewritten or presented as acceptance tests for this new instance.

## Cross-vector reuse assessment

| Source | Mechanical reuse | Semantic reuse | Authority reuse | Scope reuse | Operational proof transfer |
|---|---|---|---|---|---|
| JJ | fixed authenticated tuple | CURRENT baseline and unchanged interval predicate | NO | temporal baseline only | NO |
| JL | seal and custody authentication | existing temporal ownership/lifetime | NO | same owner | NO |
| JR | fixed guest interval/submission specialization | deterministic consistency; no EXPIRED denial transfer | NO | mechanics only | NO |
| LE | scope mutation and correlated identity rebinding | isolated scope mismatch/currentness | NO | WRONG_SCOPE | NO |
| FM/P11 | same context, checkout and consumer | unchanged fail-closed and scope semantics | NO | existing single route | NO |

EX_REUSED = existing owner/context/guest/consumer mechanics and authenticated
source evidence; no fresh 17-component EX recertification is claimed.
EX_RECONSTRUCTED = 0. Failure class: missing vector-instance binding.
Convergence: native CURRENT and scope-only denial proven without operational
execution. No additional runtime capability, owner, policy or authority source.

## Reuse Impact Assessment

1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?
   Existing temporal owner, FM context/checkout transport, LG/JR guest mechanics,
   P11 source authentication, temporal predicate and scope comparator.
2. Katere nove zmogljivosti (če sploh) nastanejo?
   No new capability; one explicit CURRENT vector-instance binding.
3. Ali katera obstoječa zmogljivost postane nedosegljiva?
   No. Historical WRONG_SCOPE contexts cannot substitute for this new instance;
   historical authorities remain spent and are never reused.
4. Ali implementacija ustvarja vzporedni tok?
   No; the existing FM/context/LG/P11 path is extended in place.
5. Ali zmanjšuje ali povečuje število produkcijskih poti?
   Neither; production path delta is zero.

# 4. Validation Matrix

Commands (bytecode and pytest cache disabled):

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_p11_wrong_scope_current_binding_v1.py
24 passed
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_g77_256di_p11_da_operational_consumer_v1.py .github/governance/evidence/g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1/tests/test_g77_256jm_option_a_temporal_binding_v1.py
30 passed
```

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Lineage/scope | Git checkpoint and eight-file inventory | local/live comparison, exact diff review | PASS |
| A/B specification authenticity/recovery | pinned instance and JJ/LE hashes | native instance authentication; committed isolated Git fixture | PASS |
| C CURRENT | 500 in [100,1000) | existing native reducer | PASS |
| D/E/F full binding | producer/schema/consumer | full context and exact schema/native validation | PASS |
| G guest validity/submission | specialized ER/FC sources | actual pure guest constructor and submission-call AST | PASS |
| H/I mismatch/override | resealed field and coordinate corruptions | both native validators and schema negatives | PASS |
| J no wall-clock substitution | deterministic guest construction | 500/[100,1000) fixture, unchanged native predicate | PASS |
| K scope isolation / SAME-R | positive baseline, scope-only variant | full source validation then existing scope denial | PASS |
| L unchanged comparator | authenticated entry source | AST comparison | PASS |
| M EXPIRED | existing selection and boundary | new focused test and JM/DI regressions | PASS |
| N temporal negatives | FUTURE/CURRENT/EXPIRED boundaries | native predicate and JM negatives | PASS |
| O no operational effect | forbidden-entry sentinels, empty proof workspace | focused proof, no launcher/controller execution | PASS |
| Fresh guest checkout | committed consumer/adapter/spec hashes | isolated Git positive and tamper rejection | PASS |
| Historical evidence | unchanged predecessor directories | exact diff inventory | PASS |
| G48/diff | this six-section report | heading/verdict and git diff --check | PASS |
| Real operational acceptance | outside authorization | not executed | NOT_RUN |
| Global conformance/full regression | outside focused scope | not executed | NOT_RUN |

# 5. Repository Mutation Summary

Exactly eight authorized files:

- Existing FM `launcher/sapianta_fresh_operation_context_v1.py`: fixed instance
  authentication and WRONG_SCOPE selection.
- Existing FM `launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: current instance
  guest checkout authentication and exact owner/adapter/consumer hash bindings.
- Existing GD `SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json`: conditional
  exact instance binding and existing WRONG_SCOPE adapter admission.
- Existing LG `adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py`: authenticated
  deterministic guest validity and submission specialization.
- `tests/p11_da_operational_consumer_v1.py`: exact instance authentication only.
- `tests/test_p11_wrong_scope_current_binding_v1.py`: focused non-operational proof.
- New `p11_wrong_scope_current_binding_v1/WRONG_SCOPE_CURRENT_VECTOR_INSTANCE_V1.json`.
- This single G48 report under `docs/governance/`.

No unrelated pre-existing changes. Historical sealed evidence, runtime authority
contracts, temporal/scope semantics and operational acceptance requirements are
unchanged. Existing public method signatures remain unchanged. The schema delta
instantiates existing semantics; it does not alter governance ownership.
No second validator, vector engine, temporal policy, authority path or source.
No operation or authority is created by import or context construction.

# 6. Certification Verdict

Bounded repository implementation and SAME-R proof pass. This verdict grants
no operational authority or E05 credit. A future attempt needs a fresh exact
context and candidate from the committed implementation, applicable native
preflights, fresh Human operational authorization and an unused one-shot
lifecycle. MA authority cannot be reused. Stop before that attempt.

P11_WRONG_SCOPE_CURRENT_VECTOR_BINDING_IMPLEMENTED_READY_FOR_OPERATIONAL_AUTHORIZATION
