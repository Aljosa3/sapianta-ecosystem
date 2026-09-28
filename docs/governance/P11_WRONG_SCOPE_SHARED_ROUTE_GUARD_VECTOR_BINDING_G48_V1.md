# Implementation Summary

Report identity: P11_WRONG_SCOPE_SHARED_ROUTE_GUARD_VECTOR_BINDING_G48_V1.
Generation: P11_WRONG_SCOPE_SHARED_ROUTE_GUARD_VECTOR_BINDING_IMPLEMENTATION_AND_VALIDATION.
Date: 2026-09-28. Baseline: constitutional-governance-finalize-v1.
Contract: current Human implementation prompt; G48 Constitutional Evidence
Reporting Standard; existing FM context, selector, materializer and static validator.
Entry HEAD ea643f0e75665dd11574f5315aa947cd04e59d76, tree
91e58cab951a52959304a965ab465c77dfe0694a; branch
`g77-256fl-wrong-attempt-preboot-blocker`; tracking/live remote matched.
Three predecessor evidence directories were untracked and remain preserved.

The existing shared FM route guard now accepts an optional sealed context.
After preserving the current HEAD/tree checks, it validates that context and,
only for WRONG_SCOPE, reuses `governed_checkout_identity` to authenticate the
exact committed and working consumer, adapter and CURRENT specification.
Both materialization and static-readiness call sites pass their context.
Absent context and all six non-WRONG_SCOPE vectors retain the legacy consumer
check. No second registry, guard, checkout route or P11 path was introduced.

SAME-R is SATISFIED for consistent consumer binding. The preserved operation
was resumed with no authority or VM entry. Its checkout, corrected consumer,
overlay, freshness and visibility passed. Full readiness is not established:
the aggregate correctly rejected the dirty implementation worktree; remaining
read-only component checks independently found the immutable cloud-init
pre-request argument mismatch described below. No second source fix was made.
E05 remains 12/18, delta zero.

# Code Evidence

Exact guard excerpt; surrounding HEAD/tree and legacy checks omitted:

```python
    if context is not None:
        fresh_context.validate_context(context, repository_root=repository_root)
        if context_vector(context) == fresh_context.WRONG_SCOPE:
            # Reuse the selector's exact committed/working consumer, adapter,
            # and CURRENT specification checks; never accept a caller hash.
            governed_checkout_identity(
                repository_root, fresh_context.WRONG_SCOPE,
                repository_head, repository_tree,
            )
            return
```

The unchanged selector requires consumer SHA256
`9207bb4a2907225674b38c5fd12a20745363d4a36c7ea83e3aea0dfd7c0a133b`,
plus exact adapter/specification hashes and working/committed byte agreement.
The legacy constant remains
`38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5`.
The new focused tests exercise both native call sites using a guard sentinel
that stops before any effect, all six other vectors, EXPIRED stable selection,
invalid contexts, both wrong consumer classes, working-byte corruption and
HEAD/tree mismatch. Consumer source bytes and selector AST equal entry.

Native recovery references, outside this commit's staging scope:

- Operation: `G77_256P11PF20260928A_E05_WRONG_SCOPE_PREFLIGHT_001`.
- Context: `.github/governance/evidence/p11_wrong_scope_non_consuming_preflight_v1/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json`.
- Context seal: `ce43284d6414f58a71490e1e4358cadd5573569d8ffba61ef2a16db2f2058a1e`.
- Context file hash: `b5eebee7e37c8c0c2ccc64482d64cd0becc7906462e89b792ce6f1320848fa4f`.
- Checkout: `/tmp/p11_wrong_scope_pf_20260928a/checkout`, detached and clean at entry HEAD/tree; no borrowed Git object database.
- Overlay: `/tmp/p11_wrong_scope_pf_20260928a/guest-overlay.qcow2`; QCOW2, check-errors 0, sole backing file the pinned base.
- Base: `/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img`; before/after SHA256 `6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733`.
- Native preparation result: `FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU`.
- Native checkout result: `PREAUTH_GUEST_CHECKOUT_TREE_AUTHENTICATION_PASS`.
- Native freshness: complete_sink_count 11, complete_sink_absence PASS.
- Native visibility: `PREBOOT_VISIBILITY_COMPOSITION_PASS`.
- Native consumer authentication of the same context: coordinate 500, CURRENT specification hash `770b8ca7ee8b3df46268acf12b3a48e48792fc05b48f1e7e1ebd2bd62f35bbbe`.

The directly dependent `prove_guest_adapter_binding` fails with
`cloud-init pre-request argument binding mismatch`. The pinned LJ V3 seed
matches its declared hash and extracted YAML. That YAML's actual command
contains adapter hash `035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f`,
checkout HEAD `f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe` and tree
`968704d8915edf6d524a8a7705591788d8333bdd`.
The preserved context instead binds adapter hash
`a59efdf4166fbc9c013a7ad7ddb23782d2fc7bc5873792960ec45b789e2df44c`
and entry HEAD/tree. Exact bootstrap argument equality is mandatory;
ordinary checkout/overlay preparation cannot rewrite this immutable seed or
its source/hash bindings. This is a separate binding defect, not authority
absence and not permission to change bootstrap semantics in this closure.

# Constitutional Self-Assessment

## Verified

One owner and path; exact vector isolation; legacy behavior preserved;
EXPIRED stable checkout unchanged; fail-closed negatives; unchanged scope,
temporal, authority and consumption code; no issued Human Act; zero operational
attempts; no VM boot; unchanged base bytes. Context generation naming is not
authority issuance. Repository fixtures are not operational evidence.

The authorized preparation created one checkout and overlay and operation-local
runtime projections. No historical authority or candidate identity was replayed.
No production path was added. SAME-R consumer authentication passes both native
owner checks and actual materialized consumer bytes.

## Not Verified

Full non-consuming readiness and operational acceptance remain unproved.
Authority identity/currentness, revocation, supersession and final consumption
bindings remain PENDING_AUTHORITY. No global conformance or fresh EX 17/17
recertification is claimed; known partial conformance remains visible.

After the authorized source commit, the preserved context still names the
entry HEAD. The existing committed-review transition requires a canonical
committed `live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json`; this
predecessor context is untracked at the evidence-root level. Post-commit
admission must therefore be re-evaluated without pretending the old context
already binds a new HEAD. No ephemeral state or predecessor evidence is staged
in this implementation commit. This recovery/admission limitation and the
independently observed bootstrap mismatch remain explicit for the successor.

Cross-vector reuse: FM selector/context/checkouts and EX custody semantics
reused; no new capability; authority reuse NO; operational proof transfer NO;
EX reconstruction zero. Required later work is bounded bootstrap/admission
binding resolution, not another generic architecture or temporal investigation.

# Validation Matrix

Executed command (bytecode and pytest cache disabled):

```text
python -m pytest -q -p no:cacheprovider tests/test_p11_wrong_scope_route_guard_v1.py tests/test_p11_wrong_scope_current_binding_v1.py tests/test_g77_256di_p11_da_operational_consumer_v1.py .github/governance/evidence/g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1/tests/test_g77_256jm_option_a_temporal_binding_v1.py
74 passed, 1 failed
```

The one failure, `test_ex_is_reused_17_of_17_without_reconstruction`, asserts
that the current uncommitted diff includes a consumer edit. This closure does
not edit the consumer. The same assertion failed on the clean, unchanged
entry checkout (PYTHONPATH supplied only for existing nested runtime imports).
An initial isolated attempt could not collect because that checkout lacks the
nested package; it was not counted as a semantic test failure. Historical tests
were not rewritten. Excluding only that generation-specific diff assertion:
74 passed, 1 deselected. The new focused guard suite contains 21 passing cases.

| Requirement | Evidence / verification | Result |
|---|---|---|
| Context-selected corrected consumer | native guard/selector and consumer checks | PASS |
| Both mandatory call sites | native entry sentinels before effects | PASS |
| Checkout/consumer exact identity | real native materialization and SHA256 | PASS |
| Other six vectors / EXPIRED | exact legacy guard outcomes and stable selector | PASS |
| Fail-closed negatives | old/arbitrary consumer, corrupted context/bytes, HEAD/tree | PASS |
| Scope/temporal/authority semantics | unchanged consumer bytes and existing regressions | PASS |
| SAME-R consumer binding | native owner + actual checkout + consumer validator | PASS |
| Fresh overlay/base preservation | qemu-img info/check, equal before/after base hashes | PASS |
| Freshness/visibility | unchanged native component validators | PASS |
| Full static readiness before commit | actual repository dirty guard, no override | BLOCKED |
| Bootstrap consistency | native adapter validator; immutable YAML arguments differ | FAIL |
| Historical EX diff-shape assertion | same failure on clean entry baseline | FAIL |
| Applicable focused/regression suite | 74 passes, one documented exclusion | PASS |
| Authority / operational effect | zero creation/consumption/VM/attempt calls | PASS |
| Post-commit preserved-context admission | requires fresh native evaluation | NOT_RUN |
| G48 / exact mutation / whitespace | six H1 sections, three-file staging scope, diff check | PASS |

Bootstrap readiness, historical generation-specific diff shape and post-commit
review sealing are not represented as implementation acceptance passes. All
bounded guard-correction acceptance criteria pass; operational readiness does
not. No defect was repaired outside the authorized guard delta.

# Repository Mutation Summary

Exactly three implementation files:

1. `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`: context-aware reuse of existing selector and both call sites.
2. `tests/test_p11_wrong_scope_route_guard_v1.py`: focused non-operational proof.
3. `docs/governance/P11_WRONG_SCOPE_SHARED_ROUTE_GUARD_VECTOR_BINDING_G48_V1.md`: this report only.

Runtime preparation remains untracked: existing predecessor evidence root's
`operation_state` projections plus `/tmp/p11_wrong_scope_pf_20260928a` checkout
and overlay. The predecessor context, blocker report and reacquisition evidence
remain unchanged. No ephemeral runtime state is included in the commit.
No consumer, cloud-init, seed, schema, governance semantics or authority files
were modified. The one authorized implementation commit is the recovery point
for the source change; final Git identifiers are reported by the execution
handoff rather than embedding a self-referential commit hash here.

# Certification Verdict

Bounded FM binding implementation and SAME-R pass. Original non-consuming
preflight resumed and advanced through real checkout/overlay preparation to
an independently authenticated bootstrap argument mismatch. Full readiness
and E05 operational acceptance are not certified. E05 is 12/18. Stop before
any second source delta, Human Authority issuance or operational attempt.

P11_WRONG_SCOPE_ROUTE_BINDING_IMPLEMENTED_PREFLIGHT_ADVANCED_TO_NEXT_BLOCKER
