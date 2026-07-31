# 1. Implementation Summary

Generation: G54-09

Report identity:
G54_09_PLATFORM_CORE_ADMISSION_PRECEDENCE_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline: FIRST_END_TO_END_CAPABILITY_EXECUTION_CERTIFIED

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G54-08 Canonical Admission Architecture Audit
- Platform Core Capability Constitution
- Platform Core Capability Registry
- existing G29 semantic capability selection and explicit canonical artifact
  ingress contracts
- existing G31 synthesis preflight and limit contracts
- existing Replay, Authorization, Worker lifecycle, Completion Adapter, and
  Human Interface contracts

Objective:

Implement the smallest versioned Platform Core admission decision that gives
an explicit certified capability request precedence over generic
active-workspace continuation while retaining existing continuation for
ordinary governed development and retaining deterministic clarification or
fail-closed behavior for ambiguous or incomplete capability admission.

Implementation scope:

- Added one versioned Platform Core admission-precedence runtime and immutable
  replay artifact.
- Reused the existing clause-role interpreter, certified semantic descriptors,
  certification registry, invocation-adapter metadata, and canonical artifact
  hashes.
- Integrated the decision before generic capability-catalog and
  active-workspace fallback in the existing new-turn project-services path.
- Preserved the exact operative request and output constraints for an admitted
  certified capability.
- Preserved existing generic continuation semantics when no explicit
  capability request is established.
- Kept admission clarification fail-closed through the existing context
  sufficiency projection.
- Added focused deterministic, replay, AiCLI/HIR, routing, continuation,
  ambiguity, missing-evidence, and tamper tests.

Modified modules:

- `aigol/runtime/platform_core_admission_precedence_runtime.py`: new versioned
  admission classifier, canonical evidence record, validator, and
  reconstructor.
- `aigol/runtime/platform_core_project_services.py`: additive new-turn
  orchestration, controlled fallback flags, exact-request non-mutating
  projection, replay references, and clarification preservation.
- `tests/test_g54_09_platform_core_admission_precedence.py`: focused G54-09
  deterministic and regression tests.
- `docs/governance/G54_09_PLATFORM_CORE_ADMISSION_PRECEDENCE_IMPLEMENTATION_REPORT_V1.md`:
  this G48 implementation report.

Intentionally unchanged modules:

- PCBV31 and every PCBV31 identity or execution-protocol file.
- Platform Core Constitution, Capability Constitution, Capability Registry,
  Capability Interaction Constitution, and Capability Composition
  Constitution.
- Replay protocol and existing downstream replay owners.
- Authorization protocol and execution-authorization owners.
- Worker request, assignment, dispatch, invocation, execution, capture,
  validation, and lifecycle owners.
- Completion Adapter.
- G31 synthesis preflight, G31 synthesis limits, and G35.
- Capability execution contracts, AiCLI behavior, Providers, and Approval.

Architectural boundaries preserved:

- Platform Core owns admission; AiCLI remains transport-only.
- Admission records a candidate destination but explicitly does not perform
  capability selection, invocation, authorization, Worker invocation, or
  Provider invocation.
- Existing G29 selection remains the selection owner and remains
  non-authorizing.
- Existing Authorization remains the only execution-authorization owner.
- No implementation artifact is inferred from natural-language payload.
- Existing active clarification continuity remains owned by its established
  owner; admission precedence applies to new turns before generic
  active-workspace continuation.

# 2. Code Evidence

## Admission Decision Flow

The implemented decision flow is:

```text
new human turn
  -> existing clause-role interpretation
  -> certified descriptor + registry + adapter comparison
  -> authenticated canonical artifact type/hash compatibility
       -> one exact compatible candidate:
            EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED
            exact request retained; generic workspace fallback suppressed
       -> one incomplete or multiple semantic candidates:
            CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED
            no selection; no fallback substitution
       -> no certified semantic candidate:
            GENERIC_GOVERNED_DEVELOPMENT_ADMISSION
            existing catalog and active-workspace continuation retained
```

Admission occurs before generic fallback but not before an already-active
owner-specific clarification continuation. That distinction preserves the
existing clarification owner rather than reinterpreting a clarification reply
as a new capability request.

## Versioned Runtime Changes

The public version and three exhaustive admission states are:

```python
PLATFORM_CORE_ADMISSION_PRECEDENCE_VERSION = (
    "G54_09_PLATFORM_CORE_ADMISSION_PRECEDENCE_RUNTIME_V1"
)
PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1 = (
    "PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1"
)

EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED = (
    "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
)
GENERIC_GOVERNED_DEVELOPMENT_ADMISSION = (
    "GENERIC_GOVERNED_DEVELOPMENT_ADMISSION"
)
CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED = (
    "CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED"
)
```

Exact excerpt from
`aigol/runtime/platform_core_admission_precedence_runtime.py`.

The public construction and reconstruction API is:

```python
def determine_platform_core_admission_precedence(
    *,
    request: str,
    explicit_canonical_artifacts: list[dict[str, Any]]
    | tuple[dict[str, Any], ...] = (),
    active_workspace_objective: Any = None,
    replay_reference: str | Path,
) -> dict[str, Any]:
```

```python
def reconstruct_platform_core_admission_precedence(
    replay_reference: str | Path,
) -> dict[str, Any]:
    """Reconstruct one immutable admission decision from its exact reference."""

    return validate_platform_core_admission_precedence(
        load_json(Path(replay_reference))
    )
```

Exact excerpts from
`aigol/runtime/platform_core_admission_precedence_runtime.py`.

## Deterministic Semantic Reduction

The outcome reduction has no probabilistic or workspace-dependent semantic
expansion:

```python
def _admission_outcome(
    *,
    semantic_candidates: list[dict[str, Any]],
    compatible_candidates: list[dict[str, Any]],
    invalid_artifact_count: int,
) -> tuple[str, str | None, str | None, str | None, bool]:
    if len(semantic_candidates) == 1 and len(compatible_candidates) == 1:
        return (
            EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED,
            str(compatible_candidates[0]["capability_identifier"]),
            None,
            "ANALYSIS",
            False,
        )
    if semantic_candidates:
        clarification_reason = (
            "MULTIPLE_EXPLICIT_CERTIFIED_CAPABILITY_REQUESTS"
            if len(semantic_candidates) > 1
            else "AUTHENTICATED_CANONICAL_CAPABILITY_INPUT_REQUIRED"
        )
        if invalid_artifact_count:
            clarification_reason = "INVALID_CANONICAL_CAPABILITY_INPUT_EVIDENCE"
        return (
            CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED,
            None,
            clarification_reason,
            None,
            False,
        )
    return (
        GENERIC_GOVERNED_DEVELOPMENT_ADMISSION,
        None,
        None,
        None,
        True,
    )
```

Exact excerpt from
`aigol/runtime/platform_core_admission_precedence_runtime.py`.

Only an operative clause containing both a supported action and supported
subject can create a semantic candidate. Quoted runtime evidence is excluded,
and output constraints are separated but retained. Compatibility additionally
requires a current certification record, an existing invocation adapter, and a
canonical input artifact type accepted by the descriptor. The admission
record carries artifact type and immutable artifact hash; it does not derive
artifact bytes from request prose. Existing downstream capability owners still
perform their full canonical validation.

## Orchestration Entry Point

The existing Human Interface project-services entry now records admission
before ordinary workspace fallback:

```python
        admission_precedence = determine_platform_core_admission_precedence(
            request=message,
            explicit_canonical_artifacts=validated_explicit_artifacts,
            active_workspace_objective=(
                prior_state.get("active_development_objective")
                if isinstance(prior_state, dict)
                else None
            ),
            replay_reference=admission_reference,
        )
```

```python
        development_intent = resolve_development_intent(
            message=message,
            workspace_state=prior_state,
            admission_precedence=admission_precedence,
        )
```

Exact excerpts from
`aigol/runtime/platform_core_project_services.py`.

Candidate discovery retains backward-compatible defaults:

```python
def discover_candidate_capabilities(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    active_workspace_fallback_allowed: bool = True,
    generic_capability_catalog_allowed: bool = True,
) -> dict[str, Any]:
```

The two flags are false only for explicit capability admission or capability
admission clarification. Calls that do not provide admission evidence retain
the historical catalog and active-workspace behavior.

## Canonical Artifact and Replay Preservation

Each new-turn decision is written immutably under the session:

```text
<session>/admission_precedence/<index>_admission_precedence_recorded.json
```

The artifact includes:

- exact source request and source-request hash;
- operative clauses and output-constraint clauses;
- canonical artifact type/hash evidence;
- certification, adapter, and descriptor hashes for each candidate;
- admission state, candidate identifier, clarification reason, and fallback
  disposition;
- a path-independent admission decision hash; and
- a path-independent full artifact hash.

The validator recalculates clause roles, semantic candidates, compatibility,
outcome, decision hash, and full artifact hash. A forged semantic reduction
is rejected even if both stored hashes are recomputed. Reconstructing from two
different replay locations produced identical decision artifacts and hashes.

The exact responsibility flags are:

```python
BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "capability_selection_performed": False,
    "capability_invoked": False,
    "execution_authorized": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "canonical_artifact_inferred_from_text": False,
    "active_workspace_state_modified": False,
    "replay_visible": True,
}
```

Exact excerpt from
`aigol/runtime/platform_core_admission_precedence_runtime.py`.

## Explicit Capability Evidence

The focused AiCLI/HIR test uses the previously over-expanded request:

```text
Normalize this platform change:

Add a comment saying "Hello".

Return only the normalized platform change.
```

The source request is 107 characters. With an existing active workspace and a
canonical implementation manifest transported through the existing AiCLI
JSON-object argument, the recorded results were:

| Evidence field | Result |
|---|---|
| Admission state | `EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED` |
| Admission candidate | `PLATFORM_CHANGE_NORMALIZATION` |
| Operative clause | `Normalize this platform change:` |
| Output constraint | `Return only the normalized platform change.` |
| Governed request | Exact 107-character human request |
| Canonical runtime prompt | Exact 107-character human request |
| Active workspace continuation available | `True` |
| Active workspace fallback allowed | `False` |
| Existing semantic route | `ROUTE_COMPLETED` |
| Existing G29 selected capability | `PLATFORM_CHANGE_NORMALIZATION` |
| Runtime prompts sent to G31 | none |

No G31 limit is bypassed: this request is admitted to its certified
non-mutating capability route, so it is not submitted as a generic
implementation synthesis request. G31 remains available and unchanged for
requests that actually require its synthesis owner.

## Normal Development Continuation Evidence

For `Continue implementing the current runtime workflow.`, the test compares
the admission-integrated result against the historical
`resolve_development_intent` call without admission evidence. The governed
request, goal mapping, candidate discovery, and `active_objective` target are
equal. The new admission record states
`GENERIC_GOVERNED_DEVELOPMENT_ADMISSION` and permits existing fallback.

## Ambiguity and Fail-Closed Evidence

The combined request `Normalize this platform change and analyze its platform
impact.` creates two certified semantic candidates and records
`CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED`. Generic workspace fallback is
suppressed, no semantic capability route is created, and context-sufficiency
cannot erase this admission clarification.

The exact normalization request without canonical artifact evidence also
requires clarification with
`AUTHENTICATED_CANONICAL_CAPABILITY_INPUT_REQUIRED`. The artifact records
`canonical_artifact_inferred_from_text=False` and performs no selection.
The same request with a substituted artifact hash records
`INVALID_CANONICAL_CAPABILITY_INPUT_EVIDENCE` and creates no route.

Tampered authority flags and a forged semantic reduction with recomputed
decision and artifact hashes both raise `FailClosedRuntimeError`.

## Authorization Preservation Assessment

Admission records `execution_authorized=False`. The existing G29 and G54
regressions confirm `selection_treated_as_authorization=False`, while the
unchanged Authorization owner remains responsible for later
`EXECUTION_AUTHORIZED` evidence. No Authorization module is in the repository
diff.

## Worker Preservation Assessment

Admission records `worker_invoked=False` and never calls a Worker owner. The
unchanged G54-03, G54-05, and G54-06 suites still pass through their existing
binder, independent Authorization, Worker, completion, and replay sequence.
No Worker or Completion Adapter module is in the repository diff.

# 3. Constitutional Self-Assessment

## Verified

- Explicit certified capability admission is evaluated before generic
  active-workspace continuation on a new human turn.
- The operative action, authenticated canonical subject evidence, and output
  constraint are retained without active-objective expansion.
- The actual AiCLI parser and Human Interface entry admit the exact
  107-character request to the existing `PLATFORM_CHANGE_NORMALIZATION`
  selection route.
- Ordinary active-workspace development continuation retains its existing
  semantic resolution.
- Multiple explicit candidates and missing canonical input evidence require
  clarification and cannot fall through to an unrelated active objective.
- Natural-language payload is never converted into a canonical implementation
  artifact.
- Admission is deterministic across replay locations and fully reconstructs
  from immutable evidence.
- Stored authority-boundary and semantic-outcome tampering fails closed.
- Capability selection remains distinct from authorization.
- G31, G35, synthesis limits, PCBV31, Replay protocol, Authorization, Worker
  lifecycle, Completion Adapter, and capability execution contracts were not
  modified.
- Focused admission, capability-routing, adjacent Human Interface/project
  services, existing G54 end-to-end, syntax, governance conformance tests, and
  repository whitespace validation passed.

## Not Verified

- The complete repository-wide test suite was not run. Validation is bounded
  to the targeted admission, capability routing, adjacent project-services,
  existing G54 end-to-end, and governance-conformance suites listed below.
- Only existing certified descriptor/adapter combinations present in the
  repository were evaluated; future capability registrations require their
  own onboarding and regression evidence.
- No Provider, filesystem mutation, Approval, Worker termination, or external
  process was exercised because admission has no authority to perform those
  actions.
- The supplemental read-only governance conformance engine remains
  `PARTIALLY_CONFORMANT` because of pre-existing root and system pre-commit hook
  drift. It reported 18 checks passed, 2 checks failed, 0 critical violations,
  and did not identify a G54-09 runtime violation.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Versioned deterministic admission | G54-09 runtime version, artifact type, and three-state reduction | Focused construction and validation tests | PASS |
| Explicit capability precedence | Exact 107-character AiCLI request, active workspace, canonical manifest | Actual parser/HIR test admitted `PLATFORM_CHANGE_NORMALIZATION` without workspace expansion | PASS |
| Preserve operative action | Admission operative-clause evidence and exact governed request | Asserted `Normalize this platform change:` and exact request equality | PASS |
| Preserve authenticated subject | Canonical manifest type/hash, descriptor, certification, and adapter hashes | Existing G29 route completed with the exact manifest | PASS |
| Preserve output constraints | Admission output-constraint evidence | Asserted exact `Return only...` clause and exact request equality | PASS |
| No unnecessary active-objective expansion | Admission fallback disposition and project-services resolution | Active objective was available; governed request and canonical prompt remained exact | PASS |
| Normal development continuation unchanged | Historical resolution compared with admission-integrated generic resolution | Governed request, goal mapping, discovery, and active-objective target were equal | PASS |
| Ambiguous request handling | Two-candidate normalization/impact request | Clarification remained required; no route or read-only result was created | PASS |
| Missing authenticated input handling | Exact normalization request without canonical artifact | Required clarification; no artifact inference or selection occurred | PASS |
| No implicit capability execution | Admission boundary flags and absent route on incomplete input | Asserted no selection at admission and no route on missing evidence | PASS |
| Replay visibility | Immutable admission file, decision hash, artifact hash, project-context reference | Public reconstruction returned the exact artifact | PASS |
| Replay determinism | Same evidence written to two replay roots | Complete artifacts, decision hashes, and artifact hashes were identical | PASS |
| Fail-closed tamper rejection | Recomputed-hash authority and semantic forgeries | Public validator raised `FailClosedRuntimeError` | PASS |
| Selection/authorization separation | Admission flags and existing route flag | Admission authorized nothing; route remained non-authorizing | PASS |
| Replay, Authorization, and Worker preservation | Repository diff plus G54-03/G54-05/G54-06 regressions | Existing binder-through-completion behavior remained green | PASS |
| PCBV31 and constitutional preservation | Repository mutation review | No PCBV31 or constitutional specification changed | PASS |
| G31/G35 and limit preservation | Repository mutation review | No G31, G35, preflight, or limit file changed | PASS |
| Targeted admission tests | `tests/test_g54_09_platform_core_admission_precedence.py` | `9 passed` | PASS |
| Capability routing and existing G54 regressions | G29-02, G29-04, G29-06, G29-08, G54-03, G54-05, G54-06, and G54-09 suites | `84 passed` | PASS |
| Adjacent Human Interface/project-services regressions | G14, G19-HI, G21, G30-04, G31-20E, and G47 adjacent suites | `95 passed` | PASS |
| Python syntax | Changed runtime and focused test modules | `python -m py_compile ...` completed successfully | PASS |
| Governance conformance tests | `tests/test_governance_conformance.py` | `5 passed` | PASS |
| Repository whitespace | Complete repository diff | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/platform_core_admission_precedence_runtime.py`: additive
  versioned admission artifact, deterministic reduction, fail-closed
  validation, and replay reconstruction.
- `aigol/runtime/platform_core_project_services.py`: additive new-turn
  admission orchestration, controlled generic fallback, exact-request
  non-mutating binding, project-context evidence, and admission-clarification
  preservation.
- `tests/test_g54_09_platform_core_admission_precedence.py`: nine focused
  admission and regression tests.
- `docs/governance/G54_09_PLATFORM_CORE_ADMISSION_PRECEDENCE_IMPLEMENTATION_REPORT_V1.md`:
  G48 evidence report.

Unchanged subsystems:

- PCBV31; Platform Core and Capability constitutional specifications; G31;
  G35; Replay protocol; Authorization; Workers; Completion Adapter; Providers;
  Approval; capability execution contracts; and AiCLI runtime.

API compatibility:

- Existing `discover_candidate_capabilities` calls remain compatible because
  both new controls default to the historical behavior.
- Existing `resolve_development_intent` calls remain compatible because
  admission evidence is optional.
- Project-context consumers receive additive admission fields; no existing
  field was removed or renamed.

Boundary preservation:

- Admission has Platform Core authority only and records no selection,
  invocation, authorization, Worker, Provider, artifact-inference, or
  workspace-mutation authority.
- Existing downstream owners and their protocols remain unchanged.
- Existing generic continuation remains available whenever explicit certified
  capability admission is not established.

Unrelated pre-existing changes:

- None observed at the start of G54-09.

# 6. Certification Verdict

PLATFORM_CORE_ADMISSION_PRECEDENCE_ESTABLISHED
