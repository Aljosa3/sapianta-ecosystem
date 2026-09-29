# Implementation Summary

Report: P11_S1_MATERIALIZATION_ADMISSION_BINDING_G48_V1. Date: 2026-09-28.
Standard: G48 V1.d. Baseline: constitutional-governance-finalize-v1.
Authorized scope: existing FM materializer caller binding correction, focused
validation, unchanged S1 runtime materialization and non-consuming preflight.
Entry HEAD: 6e71901b2a3cfa1857d8f98733a472b3295e5f8c; TREE:
917c940df1e43e7806a93830e8e396638f9a5b48. Branch, tracking and live remote matched.

The materializer now observes current HEAD/tree, authenticates their relationship
to the sealed review subject using the existing FM admission authenticator, and
only then invokes the unchanged current-route guard. It accepts the existing
committed-review proof list, not caller-selected admission coordinates. Review,
checkout, candidate and bootstrap identities remain sealed and unchanged.

Forty-two focused tests passed. Actual native materialization of the existing S1
passed with no QEMU system invocation: detached self-contained checkout, overlay,
runtime projections and empty receipt directory were prepared. Native asset
observation, checkout validation and guest adapter/bootstrap binding passed.
SAME materialization requirement R is SATISFIED. Full native preflight follows
the implementation commit because it requires an actually clean tracked repository.
This same report will record its actual result; no additional report is created.

# Code Evidence

Production owner:
`.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`.
Exact changed caller composition (surrounding unchanged body omitted):

```python
    observed_head = git(repository_root, "rev-parse", "HEAD")
    observed_tree = git(repository_root, "rev-parse", "HEAD^{tree}")
    repository_identity = authenticate_review_to_current_admission(
        repository_root=repository_root, context=context,
        observed_head=observed_head, observed_tree=observed_tree,
        committed_review_transitions=committed_review_transitions,
    )
    authenticate_current_committed_jm_route(
        repository_root, observed_head, observed_tree, context=context,
    )
```

The optional `committed_review_transitions` argument has the existing preflight
type and semantics. A cross-HEAD subject without its exact native transition fails
before the guard or effects. Same-HEAD contexts retain their existing equality
path. The materialization result records authenticated admission HEAD/tree and
the native relation/transition digest. The existing immutable-binding validator
and checkout materializer still receive the unchanged context and sealed checkout.

Evidence root:
`.github/governance/evidence/p11_s1_materialization_admission_binding_v1/`.
`ENTRY_PRESERVATION_V1.json` binds all 31 predecessor subject/evidence/runtime
files and the entry checkpoint. `MATERIALIZATION_VALIDATION_V1.json` contains
the actual materializer return, native admission proof, receipt readiness,
asset observations, checkout proof and guest adapter/bootstrap proof.

# Constitutional Self-Assessment

## Verified

- Existing FM admission authenticator and route guard reused without modification.
- Authentication occurs before the route guard; raw coordinates and wrong proofs
  cannot authorize a cross-HEAD materialization.
- Review-base, detached checkout and bootstrap candidate remain ea643f0e / 91e58cab;
  current admission remains a distinct authenticated repository endpoint.
- S0/S1 bytes, S1 seal and old bootstrap assets are unchanged. No S2 or reseal.
- Native S0/S1 admission revalidated. All 31 preserved file hashes remain equal.
- SAME-R and actual runtime materialization passed; existing receipt preparation,
  asset observation and guest checkout/bootstrap validators passed.
- No Human Act creation, consumption or replay; no operational attempt, VM boot,
  E05 acceptance or authority transfer. E05 remains WRONG_SCOPE, 12/18.
- One canonical path; no second admission owner, guard, context system or capability.

## Not Verified

Full non-consuming preflight is pending the clean implementation commit at this
report revision. Authority-dependent validity/consumption and operational acceptance
are outside scope. No global governance or EX recertification is claimed; existing
constitutional limitations remain visible. Materialization is preparation only.

# Validation Matrix

| Requirement | Evidence / validation | Result |
|---|---|---|
| Caller authenticates before guard | Native pass-through ordering test and actual materializer relation | PASS |
| No raw Git substitution | Missing/empty/raw proof rejected before guard | PASS |
| Current identity and subject negatives | Wrong HEAD/tree, S0 proof for S1, resealed review/checkout/bootstrap/candidate rejected | PASS |
| Review-base cannot stand for current admission | Existing guard rejects retained review coordinates | PASS |
| Same-HEAD and directly affected vectors | Seven-vector focused materializer compatibility | PASS |
| Focused regression | 42 tests in 5.53 seconds | PASS |
| S0/S1 immutability and admission | Native load/admission plus 31 before/after hashes | PASS |
| SAME materialization requirement R | Actual materializer authenticates transition then current guard; sealed checkout unchanged | PASS |
| Runtime materialization | Native self-contained detached checkout, overlay and projections | PASS |
| Receipt preparation | Empty unused directory; no receipts/guest outputs | PASS |
| Asset/checkout/bootstrap integrity | Actual asset hashes; native checkout and guest-adapter proof | PASS |
| Full non-consuming preflight | Requires clean committed implementation endpoint | NOT_RUN |
| Authority and operation exclusion | Producer/materializer/validators only; zero QEMU system invocation | PASS |
| G48 and whitespace | Six H1 sections; exact diff review and git diff --check | PASS |

# Repository Mutation Summary

Production: only `materialize_operation_state` in FM (12 added, 4 removed lines).
Tests: `tests/test_p11_s1_materialization_admission_v1.py`.
Evidence: the new `p11_s1_materialization_admission_binding_v1` directory.
Report: this single six-section G48 file, finalized in place.
Runtime: S1's already-sealed operation_state and transient destinations were
materialized by the existing owner. Runtime projections are not staged as code.

All existing source owners, S0/S1 subjects, bootstrap assets and predecessor
evidence remain unchanged. Existing untracked evidence is preserved and excluded
from staging. Source, tests and named canonical evidence only are staged after
review; normal additive commits/push, no history rewrite.

EX base/custody, FM checkout/projection and receipt mechanisms reused; reconstructed
capabilities zero. No historical authority or operational proof transfer.
The detached checkout is recoverable from its sealed Git commit/tree; projections
from their pinned canonical source bytes; the never-booted overlay from the pinned
base via the existing materializer. Recovery must revalidate all native bindings.
No unique required subject or proof exists only in temporary diagnostic files.

# Certification Verdict

P11_WRONG_SCOPE_S1_MATERIALIZATION_BINDING_CORRECTED_PREFLIGHT_ADVANCED_TO_NEXT_BLOCKER
