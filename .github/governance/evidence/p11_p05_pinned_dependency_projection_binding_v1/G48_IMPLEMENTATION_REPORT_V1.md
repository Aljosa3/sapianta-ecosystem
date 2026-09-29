# 1. Implementation Summary

Report identity: P11_P05_PINNED_DEPENDENCY_PROJECTION_BINDING_G48_V1.
Reporting date: 2026-09-29. Baseline: constitutional-governance-finalize-v1;
entry commit 9a0ae8357a6e35e7f6adea39279c331f70d055db.
Contract: this closure's authenticated user specification, sections 3-13.
Reporting source: docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md.
The repository identifies that standard as V1; a distinct V1.d text was not
located. The requested six-section structure is preserved; no unseen version
requirements are claimed verified.

FM now authenticates the fixed independent nested source, materializes the
parent as before, invokes the same materializer for the derived nested path,
and independently reobserves both identities. Readiness additionally validates
nested runtime blob bytes and rejects checkout namespace shadows.
The source correction is CLOSED_PASS. Native SAME-R remains pending.

Scope: one FM caller/readiness module, focused tests, two dependent regression
fixtures, this single G48 report and CERTIFICATION_V1.json. No governance,
authority, ER import, guest mount, or materializer implementation changed.
The specification authorized this correction and ordinary commit/push, but
no operational attempt. Test lifecycle inputs are isolated fixtures under /tmp.

# 2. Code Evidence

Repository reference: `.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py`.
Exact representative orchestration excerpt follows; unrelated entry admission
checks and subsequent export/overlay construction are omitted.

```python
    nested_source = authenticate_pinned_nested_source(repository_root)
    checkout_materialization = materialize_guest_self_contained_checkout(
        source_repository=repository_root,
        checkout_path=Path(checkout_binding["path"]),
        expected_head=checkout_binding["head"],
        expected_tree=checkout_binding["tree"],
    )
    checkout_path = Path(checkout_binding["path"])
    if _er_consumer_git(
        checkout_path, "ls-tree", checkout_binding["tree"], "--", "sapianta_system"
    ):
        raise RuntimeError("nested destination collides with parent tracked content")
    nested_materialization = materialize_guest_self_contained_checkout(
        source_repository=nested_source,
        checkout_path=checkout_path / "sapianta_system",
        expected_head=NESTED_DEPENDENCY_HEAD,
        expected_tree=NESTED_DEPENDENCY_TREE,
    )
    checkout_materialization = _materialized_checkout_observation(
        checkout_path, checkout_binding["head"], checkout_binding["tree"]
    )
    nested_projection = authenticate_nested_projection(context)
    operation_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    if operation_scoped_checkout:
        if transient_root.is_symlink() or not transient_root.is_dir():
            raise RuntimeError("checkout materializer did not create the transient root")
        if set(transient_root.iterdir()) != {Path(checkout_binding["path"])}:
            raise RuntimeError("transient root contains state outside checkout lifecycle")
```

`authenticate_pinned_nested_source(repository_root)` derives the sole source,
checks canonical path and Git root, exact current HEAD/tree and cleanliness.
It cannot accept a dependency source parameter. The materializer's unchanged
canonical parent/destination-absence checks apply to its second invocation.
Parent tracked-content collision is rejected before nested materialization.

`authenticate_nested_projection(context)` derives the destination, validates
its separate detached/object-local Git identity, and hashes actual runtime
bytes using the Git blob format against the pinned tree. This does not depend
on status alone. Namespace module/package shadows at the two native checkout
import roots, nested package initializer/runtime shadows, symlinks and extra
runtime files are rejected. No canonical context data model is changed;
materialization/readiness evidence gains independent nested observations.

`validate_checkout_preboot_readiness` preserves all parent checks and requires
the new observation. `authority_free_static_readiness` reuses the fixed-source
validator. AST comparison confirms only these three existing functions changed;
two directly required validators were added. The existing materializer is
structurally unchanged. Exact source hashes and static comparison are recorded
in CERTIFICATION_V1.json.

# 3. Constitutional Self-Assessment

## Verified

- Both actual materializer calls run in focused composition fixtures, including
  the operation-scoped destination layout, with exact parent and nested pins.
- Independent nested raw-byte checks reject status-clean assume-unchanged
  tampering and ignored import shadows. Parent authentication remains intact.
- Existing read-only mount/source contract and native ER source are preserved.
- 27 focused/regression tests pass. Git diff whitespace check passes.
- S3 terminal record digest verifies using the existing canonical newline
  serialization; terminal evidence and consumed authority remain untouched.
- Production route count remains 0 under the native P11 contract. The one FM
  orchestration route remains one; the two clone calls are not execution routes.

## Not Verified

- No native guest P05, SAME-R, or E05 acceptance was executed. Host tests do not
  provide native commissioning evidence or authorize a new lifecycle.
- Composition fixtures isolate admission/freshness and qemu-img construction;
  they certify source composition, not operational admission or VM lifecycle.
- Preboot integrity is an observation of the projected runtime surface, not
  generic host/guest filesystem hardening or a guarantee against later hostile
  host mutation. Installed guest packages and the native guest environment
  remain part of the separately required native proof.
- No whole-repository conformance or full regression claim is made.
- A distinct G48 V1.d source was unavailable; canonical repository V1 was used.

## SAME-R boundary and critical-path assessment

ER P05 imports at lines 1129-1136, checks live SO_PEERCRED and emits P05 evidence
at lines 1170-1178. It continues at line 1180 and sends CREATE_ACT at line 1344.
The pre-act checkpoint is evidence, not an enforced stop. No existing lawful
non-operational native proof route was positively established.
NATIVE_SAME_R_ROUTE = NOT_ESTABLISHED.
SAME_REQUIREMENT_RECOMPUTATION_RESULT = UNSATISFIED_PENDING_NATIVE_GUEST_PROOF.
ORIGINAL_TASK_CONTROL_RETURNED = NO. PROPOSED_SUCCESSOR = NONE.
The next boundary is a governed native proof scope with an enforced stop before
act creation and P11/E05. Human decision necessity is not established; none was
requested. S3 cannot supply reusable authority.

Raw-byte integrity is mandatory for the exact claimed nested import surface:
Git status accepts the tested assume-unchanged mutation. The critical-path gate
therefore retains blob comparison and namespace shadow checks within authorized
readiness scope, with no new materializer or capability. Failure novelty,
NRDRL disposition, reuse and compact CCWIM are consolidated in the JSON record.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| A Exact parent identity | actual composition + parent rejection tests | pytest | PASS |
| B Independent exact nested HEAD/tree | pinned clone and negative pins | pytest | PASS |
| C Fixed source to derived destination | both canonical composition fixtures | pytest | PASS |
| D Composed authenticated nested path | nested blob/identity observation | pytest | PASS |
| E Guest path presentation | existing GP mount/source contract + composed path | static non-operational readiness | PASS |
| F Wrong nested HEAD | source observation negative and substituted clone HEAD | pytest | PASS |
| G Wrong nested TREE | source observation and projection pin negatives | pytest | PASS |
| H Import-relevant tampering | assume-unchanged bytes, ignored pyc, shadows, symlink | pytest | PASS |
| I Missing projection | readiness rejection | pytest | PASS |
| J Substituted source | contains pinned commit but wrong HEAD; wrong root, symlink | pytest | PASS |
| K Parent checks unchanged | AST and GP/GQ regressions | comparison + pytest | PASS |
| L Identities independent | separate observations, parent/nested role mismatch | pytest | PASS |
| M Read-only mount | contract checks and readonly=off negative | pytest | PASS |
| N ER P05 unchanged | exact baseline source comparison | static | PASS |
| O No second materializer/path/authority | unchanged materializer AST, exact diff, zero route count | static | PASS |
| Clean source, destination collision, tracked collision | focused negative probes | pytest | PASS |
| S3 preservation | committed terminal source and canonical record hash | static digest check | PASS |
| Native guest SAME-R | unavailable lawful stopping route | not executed | NOT_RUN |
| G48 distinct V1.d requirements | unavailable text; repository V1 applied | version limitation | BLOCKED |

The final two rows limit proof/reporting-version claims; they do not negate the
explicitly authorized non-operational implementation certification.

# 5. Repository Mutation Summary

Modified existing paths:

- FM launcher identified above: minimum composition and readiness integrity.
- g77_256gp_guest_checkout_tree_precondition_v1/tests/test_g77_256gp_guest_checkout_tree_precondition_v1.py:
  valid fixture now contains the independently pinned dependency.
- g77_256gq_guest_self_contained_checkout_v1/tests/test_g77_256gq_guest_self_contained_checkout_v1.py:
  valid fixture gains dependency; stale fake-identity test now asserts the
  pre-existing admission rejection, independently reproduced on entry source.

New paths in this report's evidence directory:

- tests/test_pinned_projection.py: focused positive/negative certification.
- CERTIFICATION_V1.json: consolidated state, gates, failures, hashes and proof.
- G48_IMPLEMENTATION_REPORT_V1.md: this sole implementation report.

Unchanged: nested source, S3 evidence, ER, guest bootstrap/mounts, context model,
materializer, operational and authority routes, constitution and governance.
API additions are scoped validators and nested evidence keys. Parent-only P05
readiness is now intentionally rejected. Existing materializer API is unchanged.
Pre-existing untracked S1/S2/S3 and other evidence remains untouched and unstaged.
No nested repository commit/push occurs. Exact staging/commit/push commands and
post-publication checkpoint are reported in the final handoff rather than
fabricated prospectively in this precommit record.

## Interruption recovery authentication

The resumed session authenticated class B: all six closure files already staged
against entry HEAD/tree, with no unstaged tracked changes. Tracking and live
remote both matched entry HEAD. Source and tests were recovered unchanged.
The existing 27-test matrix passed again (27 passed in 12.27s). All four recorded
SHA256 references, unchanged ER/materializer structure, and canonical S3 record
digest were independently verified. The nested repository remained clean at
its required HEAD/tree. All 71 pre-existing untracked evidence files are bound
by SHA256 in the existing certification record and excluded from this closure.
The platform interruption established no new native semantic failure.

Recovery authentication, current critical-path gates and exact source/evidence
references are consolidated in CERTIFICATION_V1.json. No second report or
implementation was created. Two technical edges are closed: source correction
and non-operational certification; recovery inspection is not a separate edge.
Native SAME-R remains unexecuted and its lawful proof route is not established.
The publication commit containing these artifacts supplies the exact subject
identity; final handoff authenticates that commit against the live remote.

# 6. Certification Verdict

The verdict covers the bounded implementation and non-operational certification
only. It does not certify native SAME-R, operational acceptance, or unavailable
reporting-version requirements.

P11_P05_PINNED_DEPENDENCY_PROJECTION_BINDING_IMPLEMENTED_AND_CERTIFIED
