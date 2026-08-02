# 1. Implementation Summary

Generation: G65-07

Report identity: G65_07_SELF_KNOWLEDGE_INTENT_ROUTING_INTEGRATION_IMPLEMENTATION_REPORT_V1

Constitutional baseline: `CONSTITUTIONAL_GOVERNANCE_CLOSED` and
`SELF_KNOWLEDGE_PLATFORM_CONVERSATION_INTEGRATION_ESTABLISHED`.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1
and the certified G65-01 through G65-06 architecture, manifest, snapshot,
validation, query, and Platform Core/Conversation integration contracts.

Reporting date: 2026-08-02.

Objective:

Recognize the eight closed Self Knowledge Conversation requests before Project
Objective inference and route them through the certified G65-06 Platform Core
entry to G65-05, while leaving every other request on the existing governed
development path.

Implementation scope:

- Add one deterministic, hash-bound request classification artifact with
  `SELF_KNOWLEDGE_QUERY`, `DEVELOPMENT_OBJECTIVE`, and fail-closed
  `CLARIFICATION_REQUIRED` outcomes.
- Match only the eight prescribed `Show <closed subject>.` forms and retain the
  two exact G65-06 explicit request forms.
- Invoke classification at the Platform Core project-services boundary before
  admission precedence and Project Objective inference.
- Wrap a positive classification in the existing Platform Query Router
  contract and delegate to `route_explicit_self_knowledge_query`.
- Return the existing G65-06 non-authoritative canonical presentation to
  AiCLI/Conversation without an approval, Governance, Reuse Proof,
  Authorization, Worker, provider, or execution transition.
- Preserve the existing admission, Objective, Governance, and Platform Core
  path for `DEVELOPMENT_OBJECTIVE` classifications.

Modified modules:

- `aigol/runtime/self_knowledge_request_classification.py` — closed
  pre-objective request classifier and validator.
- `aigol/runtime/platform_query_router.py` — validated Self Knowledge router
  envelope that reuses the G65-06 entry.
- `aigol/runtime/platform_core_project_services.py` — classification placement
  before admission/Objective inference and bounded routing branch.
- `tests/test_g65_07_self_knowledge_intent_routing.py` — focused positive,
  negative, ambiguous, AiCLI, determinism, tamper, and boundary regressions.
- `docs/governance/G65_07_SELF_KNOWLEDGE_INTENT_ROUTING_INTEGRATION_IMPLEMENTATION_REPORT_V1.md`
  — this G48 implementation report.

Intentionally unchanged modules:

- AiCLI input and rendering ownership; Human Interface Runtime Entry;
  Conversation state ownership; all G65-02 through G65-06 runtime owners;
  canonical presentation behavior; Development Governance; Constitutional
  Reuse Proof; G48 completion; Authorization; Replay; Worker; provider
  selection; and execution runtimes.

Architectural boundaries preserved:

- Classification is a closed lexical reduction. It performs no repository
  search, natural-language inference, LLM call, provider call, Worker call,
  Objective creation, governance decision, Replay write, or mutation.
- Platform Core remains the classification and routing authority. AiCLI and
  Conversation carry no classification, evidence, or execution authority.
- The classifier produces only a route identity. G65-06 remains the sole
  Platform Core/Conversation integration owner and G65-05 remains the query
  owner.
- Active clarification ownership is not preempted. The new classification is
  applied only to a new operational turn.

# 2. Code Evidence

## Public API

The new runtime exposes one builder and one deterministic validator:

```python
def classify_self_knowledge_request(request_text: str) -> dict[str, Any]:
    """Classify one request before any Project Objective inference."""

def validate_self_knowledge_request_classification(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a classification by deterministic reconstruction."""
```

The public Platform Query Router API retains its existing behavior and accepts
two additive inputs: `repository_root` for authenticated G65 evidence and an
optional already validated `request_classification` from the canonical
project-services boundary.

## Orchestration Entry Point

`prepare_unified_human_interface_project_context` classifies a new turn before
the existing admission-precedence call:

```python
request_classification = validate_self_knowledge_request_classification(
    classify_self_knowledge_request(message)
)
if request_classification["request_classification"] == DEVELOPMENT_OBJECTIVE:
    admission_precedence = determine_platform_core_admission_precedence(...)
```

The same validated artifact is passed to the existing Platform Query Router.
For a bounded Self Knowledge result, project services binds an operational
Platform query and sets `objective_inference_allowed: False`. The existing
`informational_router_response` branch then deliberately leaves
`project_objective` as `None`.

## Semantic Reductions

The natural Conversation map contains exactly:

```text
Show architecture.              -> ARCHITECTURE
Show runtime inventory.         -> RUNTIME_INVENTORY
Show certified capabilities.    -> CERTIFIED_CAPABILITIES
Show governance state.          -> GOVERNANCE_STATE
Show execution boundaries.      -> EXECUTION_BOUNDARIES
Show certified history.         -> CERTIFIED_HISTORY
Show known limitations.         -> KNOWN_LIMITATIONS
Show ownership.                 -> OWNERSHIP
```

Matching uses whitespace normalization, case folding, and removal of one
terminal period only for a `show` form. There is no scoring, synonym map,
token completion, subject inference, or multiple-subject choice. Exact G65-06
`/self-knowledge <SUBJECT>` and `SELF_KNOWLEDGE:<SUBJECT>` forms remain
compatible. Malformed explicit forms or `Show` wording containing a closed
subject without resolving to exactly one map entry returns
`CLARIFICATION_REQUIRED`.

## Public Validators

The classification validator requires an exact closed schema, artifact type,
version, boundary flags, source request, normalized request, classification,
subject, canonical request, reason, inference permission, match/ambiguity
flags, and artifact hash. It reconstructs the complete artifact from
`request_text` and rejects any difference.

The existing Platform Query Router validator authenticates the wrapper hash.
The G65-06 validator authenticates the nested Self Knowledge response, and the
existing presentation validator authenticates the non-authoritative rendered
artifact. No new evidence or response validator is duplicated.

## Canonical Data Models

`SELF_KNOWLEDGE_REQUEST_CLASSIFICATION_V1` contains only:

```text
artifact_type
runtime_version
request_text
normalized_request
request_classification
query_subject
canonical_self_knowledge_request
classification_reason
objective_inference_allowed
deterministic_exact_match
ambiguous_self_knowledge_request
boundary_flags
artifact_hash
```

Positive classifications bind one G65-05 subject and its canonical G65-06
request. Development classifications bind no subject and explicitly allow the
existing Objective path. Ambiguous Self Knowledge-shaped requests bind no
subject and explicitly prohibit Objective inference.

## Deterministic Algorithms

The fixed routing algorithm is:

1. Normalize the new Conversation request lexically.
2. Reconstruct and validate one classification artifact.
3. For `SELF_KNOWLEDGE_QUERY`, skip admission and Project Objective inference,
   bind the existing Platform Query Router, and call the G65-06 exact entry.
4. G65-06 validates the manifest/snapshot and invokes G65-05; the existing
   presentation owner renders the result.
5. For `CLARIFICATION_REQUIRED`, skip admission and Objective inference, do
   not invoke G65-06, and return the existing router-only clarification
   presentation.
6. For `DEVELOPMENT_OBJECTIVE`, execute the pre-existing admission,
   Project Objective, Governance, and Platform Core sequence unchanged.

Repeated classifications and Self Knowledge router responses over unchanged
authenticated evidence are byte-for-byte equal in value.

## Responsibility Boundaries

- Platform Core owns classification and routing; the classifier has no
  authority to answer, plan, approve, authorize, or execute.
- G65-06 owns authenticated loading and Platform Core/Conversation transport;
  G65-05 owns snapshot projection. Neither implementation is duplicated.
- Conversation renders the existing canonical presentation and remains
  non-authoritative.
- Development Governance, Reuse Proof, Authorization, Replay, Worker, and
  provider owners are unreachable from the positive classification branch.
- Development requests still produce existing admission and Project Objective
  artifacts and then obey the current constitutional gates.

# 3. Constitutional Self-Assessment

## Verified

- Each of the eight required natural forms deterministically selects
  `SELF_KNOWLEDGE_QUERY_RUNTIME` and returns its corresponding G65-05 subject.
- Positive requests have no admission-precedence artifact, Project Objective,
  Development Governance artifact, Reuse Proof admission, human approval, or
  governed runtime entry.
- A fail-if-called regression proves Project Objective inference is not
  reached for every supported subject.
- An isolated router regression proves generic Platform Knowledge probing and
  development-intent resolution are not reached by the positive branch.
- A real `run_reference_uhi_session` request for `Show architecture.` returns
  `PRESENTATION_READY`, the authenticated Architecture facts and sources, and
  no governed-execution clarification or approval prompt.
- The two G65-06 explicit request forms remain compatible.
- Repeated classifications and routed responses are identical.
- Multi-subject and non-exact Self Knowledge-shaped requests return the
  existing fail-closed clarification presentation without Objective inference.
- Classification tampering fails deterministic reconstruction.
- A governed implementation control is classified `DEVELOPMENT_OBJECTIVE`,
  creates the existing admission and Project Objective artifacts, and does not
  select the Self Knowledge service.
- Exact snapshot identity, digest, subject, facts, source references, and
  source digests remain preserved through the existing G65-06 presentation.
- The focused suite passed 26 tests; the selected current G65, Conversation,
  router, presentation, admission, AiCLI lineage, and conformance set passed
  138 tests.

## Not Verified

- No arbitrary natural-language Self Knowledge inference, synonyms, semantic
  matching, multi-subject response, LLM routing, or dynamic subject discovery
  is implemented.
- Active clarification replies retain their existing owner and are not
  reclassified as new Self Knowledge turns.
- The complete repository test suite was not run.
- Additional diagnostic runs of legacy G14/G15/G49 approval fixtures exposed
  15 historical expectation failures. Every affected implementation prompt
  was classified `DEVELOPMENT_OBJECTIVE`, reached admission and Project
  Objective inference, and then obeyed the current mandatory G64 Reuse Proof
  gate (`WAITING_FOR_REUSE_PROOF_EVIDENCE`) instead of the fixtures' pre-G64
  approval state. G65-07 does not alter or bypass that gate, and these fixtures
  were not rewritten as part of this bounded routing repair.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Pre-objective request classification | Classifier call precedes admission in Platform Core project services | Fail-if-called Project Objective regression for all eight subjects | `PASS` |
| Required positive vocabulary | Exact eight-entry natural request map | Eight parameterized project-context routes | `PASS` |
| Certified G65-05/G65-06 reuse | Canonical explicit request and `route_explicit_self_knowledge_query` | Subject, snapshot, source, and presentation bindings | `PASS` |
| G65-06 explicit compatibility | Existing slash and token request forms | Two explicit-form router cases | `PASS` |
| Deterministic classification | Closed normalization/map and reconstruction validator | Repeated equality for every subject | `PASS` |
| Deterministic routed response | Hash-bound router and G65-06 response | Repeated Architecture route equality | `PASS` |
| Real AiCLI positive routing | Existing AiCLI submission calls Platform Core project services | `Show architecture.` returns read-only presentation without approval/clarification | `PASS` |
| Development fallback | `DEVELOPMENT_OBJECTIVE` permits the existing branch | Admission and Project Objective artifacts present; Self Knowledge absent | `PASS` |
| Ambiguous request handling | Closed-subject shape without exact match | Three ambiguous forms return router clarification with no Objective | `PASS` |
| Tamper rejection | Deterministic classification reconstruction | Changed subject rejected with `FailClosedRuntimeError` | `PASS` |
| No generic inference on positive route | Early router branch | Generic knowledge/development functions replaced with fail-if-called controls | `PASS` |
| No execution/discovery owner in classifier | Minimal import and boundary surface | Static prohibited-import/token regression | `PASS` |
| Focused G65-07 suite | New regression module | `pytest -q tests/test_g65_07_self_knowledge_intent_routing.py` — 26 passed | `PASS` |
| Current certified compatibility | G65-02 through G65-07; router; presentation; Human Conversation Experience; admission; AiCLI positive lineage; conformance | Selected regression command — 138 passed | `PASS` |
| Legacy approval-fixture diagnostic | G14/G15/G49 pre-current-admission expectations | 15 assertions stop at mandatory Reuse Proof evidence; development routing confirmed | `KNOWN_BASELINE_MISMATCH` |
| Python compilation | New classifier and modified Platform Core modules | `python -m py_compile ...` | `PASS` |
| Governance conformance | Existing conformance owner | `python -m runtime.governance.governance_conformance_engine` — 20 passed, 0 failed, 0 warnings, `CONFORMANT` | `PASS` |
| Diff whitespace integrity | G65-07 changed files | `git diff --check` plus checks for new files | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/self_knowledge_request_classification.py` — deterministic
  classification schema, builder, and validator.
- `aigol/runtime/platform_query_router.py` — preclassified Self Knowledge
  response wrapper and G65-06 delegation.
- `aigol/runtime/platform_core_project_services.py` — pre-admission
  classification placement and bounded operational route.
- `tests/test_g65_07_self_knowledge_intent_routing.py` — focused regression
  evidence.
- `docs/governance/G65_07_SELF_KNOWLEDGE_INTENT_ROUTING_INTEGRATION_IMPLEMENTATION_REPORT_V1.md`
  — G48 implementation evidence.

Unchanged subsystems:

- AiCLI behavior outside its existing Platform Core delegation; Conversation
  state and rendering owners; G65-02 through G65-06 owners; Development
  Governance; Reuse Proof; G48 completion; Authorization; Replay; Worker;
  provider ownership; execution; Self Development; and IVE.

API compatibility:

- Existing calls to `route_platform_query` remain valid. Two optional inputs
  support authenticated Self Knowledge routing, while ordinary route outputs
  and the existing descriptor registry remain unchanged.
- The only new public runtime API is the isolated classifier/validator pair.
  No existing Objective, Governance, Conversation, provider, Worker,
  authorization, Replay, or execution schema was replaced.

Boundary preservation:

- The routing repair adds no knowledge implementation, source parser,
  repository search, LLM, provider/Worker invocation, Objective generation,
  governance decision, authorization, replay write, or execution behavior.
- G65-07 does not modify the mandatory Reuse Proof gate to satisfy historical
  approval fixtures.

Unrelated pre-existing changes:

- None observed at implementation start.

# 6. Certification Verdict

SELF_KNOWLEDGE_INTENT_ROUTING_ESTABLISHED
