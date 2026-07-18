# G31-20E Governed-Development Request Routing Re-Audit

## Verdict

`G31_GOVERNED_DEVELOPMENT_ROUTING_BLOCKED_BY_CANONICAL_CONTRACT`

The prior marker-reading request was correctly routed to Platform Knowledge.
A genuinely repository-grounded patch request was correctly routed to the
existing governed-development path without a production classifier change.
The single live confirmation then failed closed after the first human decision
because the disposable repository did not satisfy the existing Repository
Cognition grounding contract. No CODEX process, transport receipt, Worker
output, result capture, or semantic validation was created. The run was not
retried.

## Baseline

- Parent HEAD: `027ff3cadaf746ac925fc7178edfdf404ec9d0b7`
- Parent subject: `fix(governance): isolate evidence and clarify result validation`
- Nested `sapianta_system` HEAD:
  `31522024b38bc08a60ea2152122bc2b399e1235e`
- Nested worktree: clean before and after
- Canonical validation meaning:
  `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY`
- Task-outcome satisfaction is outside that validation meaning.

## Canonical Routing Ownership

| Responsibility | Existing canonical owner | Entry point / evidence |
|---|---|---|
| Platform intent/service classification | Platform Core Query Router | `aigol/runtime/platform_query_router.py::route_platform_query` |
| Knowledge evidence | Platform Knowledge Runtime | `aigol/runtime/platform_knowledge_runtime.py::query_platform_knowledge` |
| Governed-development eligibility | Platform Core Project Services | `aigol/runtime/platform_core_project_services.py::resolve_development_intent` |
| `summary_admissible` | Platform Core Project Services | `resolve_development_intent`; implementation, specificity, work type, mutation, and conflict gates |
| Knowledge/development candidate scores | Platform Core Query Router | `_knowledge_score`; `_development_score` |
| Service selection | Platform Core Query Router | `_candidate_routes`; `_select_route`; `_apply_lifecycle_precedence` |
| Operational turn binding | Platform Core Project Services | `_classify_new_operational_turn`; `validate_operational_turn_binding` |
| Human presentation and decision transport | AiCLI, non-authoritative | `aigol/cli/aicli.py::run_reference_uhi_session` |
| Worker activation after three decisions | G31 activation binding | `codex_worker_activation_binding_runtime.activate_bounded_codex_worker` |

AiCLI does not classify the request, grant execution authority, select the
Worker, own Replay, validate the result, or accept the result.

## Routing Contract Findings

The smallest canonical distinction is evidence-based:

| Request class | Canonical characteristic | Execution consequence |
|---|---|---|
| Knowledge | asks for architectural/capability information or a read-only return without a sufficiently grounded implementation objective | Platform Knowledge; no approval or Worker |
| Repository-grounded development | names a concrete implementation/test defect and requests a bounded engineering result | governed-development summary; approval-gated continuation |
| Execution | separately approved execution review after repository grounding | may continue toward Worker selection |
| Mutation | implementation work type and mutation authority are explicit; proposal approval alone is not execution authorization | remains separately governed |
| Ambiguous | target or outcome is insufficiently deterministic | clarification/non-execution; no Worker |

This is not a keyword override. The existing development-intent artifact binds
guided development, specificity, native development admissibility, work type,
mutation allowance, and conflict state before making the summary admissible.

### Prior request

Exact request (165 characters):

> Improve the human interface terminal summary behavior. Read KNOWN_INPUT.txt
> and include its exact marker in your short read-only final response. Do not
> modify files.

Deterministic evidence:

- selected service: `PLATFORM_KNOWLEDGE_RUNTIME`;
- knowledge score: `55`;
- governed-development score: `21`;
- `summary_admissible=false`;
- requested action clause: only the underspecified terminal-summary
  improvement;
- the marker-reading instruction is a non-mutating return operation;
- final operational mode: informational;
- approvals consumed: `0`;
- process starts: `0`.

This is correct knowledge routing and was not repaired.

### Grounded development fixture

Exact request (113 characters):

> Fix the failing addition test in calc.py and test_calc.py. Return a minimal
> unified diff only; do not edit files.

Deterministic evidence:

- selected service: `GOVERNED_DEVELOPMENT_RUNTIME`;
- governed-development score: `53`;
- knowledge score: `20`;
- route status: `ROUTE_READY`;
- `summary_admissible=true`;
- `runtime_binding_admissible=true`;
- human approval required: true.

The existing contract therefore distinguishes a concrete failing-test patch
request from the earlier marker-return request. No production routing defect
was proven and no production routing line changed.

## Focused Fail-Closed Coverage

`tests/test_g31_20e_governed_development_request_routing_reaudit.py` proves:

1. the previous marker request remains knowledge-routed and consumes no
   approval;
2. the grounded failing-test patch request selects the existing governed-
   development route;
3. ambiguous and pure-summary requests start no Worker and consume no
   approval;
4. route substitution fails on the canonical router artifact hash;
5. summary-admissibility substitution fails on the same bound evidence;
6. cross-session clarification-routing evidence fails closed.

## Changed Surface

| Path | Change |
|---|---|
| `tests/test_g31_20e_governed_development_request_routing_reaudit.py` | Seven routing, non-execution, substitution, and session-lineage tests |
| `docs/governance/G31_20E_GOVERNED_DEVELOPMENT_REQUEST_ROUTING_REAUDIT.md` | This evidence report |

Production change count: **0 added, 0 removed**. No nested-repository file
changed.

## Validation Results

| Validation | Result |
|---|---|
| Targeted `py_compile` | passed |
| Focused G31-20E routing | `7 passed in 0.33s` |
| G31-17B through G31-20E | `60 passed in 173.67s` |
| Explicit disposable runtime-root CLI/provider/continuity group | `72 passed in 0.64s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Governance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 known hook drifts, 0 critical violations |
| Complete suite | `6453 passed, 4 skipped in 444.64s` |
| Parent `git diff --check` | passed |
| Nested `git diff --check` | passed |

The two known hook drifts remain visible and were not reframed as full
conformance.

## Single Disposable Live Confirmation

### Preflight and fixture

- Workspace: `/tmp/g31-20e-live-0djDRP/workspace`
- Runtime root: `/tmp/g31-20e-live-0djDRP/runtime`
- Source: `calc.py`; focused test: `test_calc.py`
- Known defect: `add(2, 3)` returned `-1`, while the test required `5`
- Raw request: `113` characters
- Canonical prefix: `20` characters
- Final synthesized request: `133/240` characters
- Preflight status: `SYNTHESIS_PREFLIGHT_READY`
- Preflight hash:
  `sha256:f2baef9b25785455e06d1e68e640b841720607ba14aed2123b6f80dd9a1509f9`
- Final request SHA-256:
  `0b9a3a9c85025fd32d8bc8b2ce370bd4c0994a33e0faa961e7af462bda01614e`

### Truthful stop boundary

| Field | Observed value |
|---|---|
| Governed-development route selected | true |
| `summary_admissible` | true |
| Human decision count | `1` |
| Required human decision count reached | false |
| Process start count | `0` |
| Transport status | not created |
| Return code | not created |
| Timed out | not applicable |
| Authentic Worker output present | false |
| Semantic Worker result captured | false |
| Capture count | `0` |
| Semantic validation performed | false |
| Validation count | `0` |
| Validation status | not created |
| Canonical validation meaning | `GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY` (contract only; not invoked) |
| Task-outcome satisfaction evaluated | false |
| Task-outcome satisfied | false |
| Result accepted | false |
| Repository source mutated | false |
| Provider invoked | false |
| Automatic retry | false |
| Additional Worker process | false |
| Commit created | false |

The first approval entered the existing governed-development runtime. The
canonical repository grounding artifact then returned:

- status: `CANONICAL_REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED`;
- capability target: `general_project_goal`;
- failure: `Repository Cognition requires a Git workspace with one exact compatible implementation-and-test evidence match`.

The downstream execution-authorization review truthfully returned
`GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED` with
`execution authorization review requires grounded repository scope`.

The repository cognition owner scans existing `aigol/runtime/*.py` and
`tests/test_*.py` capability pairs and requires the exact canonical capability
key. The disposable root-level `calc.py` fixture and generic
`general_project_goal` target did not satisfy that production contract. The
fixture was not staged, reshaped, or retried after this evidence was created.

### Replay evidence

| Family | Count | Identity / hash |
|---|---:|---|
| Operational routing binding | 1 | `PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1`; `sha256:75aeea5d87673ccb18e59edf67ac09ab3900f1ee046d002136fe455ee5b832e4` |
| Router response bound inside routing artifact | 1 | `sha256:97ceef619d94b0b6a69803909e62a2ddb1670bc6569ba18cdc2fcc248b8ef8ff` |
| Repository grounding Replay | 2 | grounding artifact `sha256:9c6689ee7e45aac9432d57ca0b7240408e65c09a1c1c080badc1200ee6a42f1d`; returned wrapper `sha256:a18985c3a0b31e6661acdf9623b4611e4c7af4a0c49e9dd7141f1dc95bf04e7c` |
| Execution-authorization review Replay | 2 | failed review artifact `sha256:1eb4874d08a3ab9856795429007755cb1441c797580ea3cdd23f34be5f4c2840`; returned wrapper `sha256:6c3efdc3abd63f727c26f23c85b59892cce891e576178e81adbab5da54f062c7` |
| CODEX activation Replay | 0 | not created |
| G31-18 capture Replay | 0 | not created |
| G31-20 validation Replay | 0 | not created |

No proposed patch was observed. There was no authentic stdout to accept,
rewrite, repair, or report. Process inspection after the stop found no
`codex exec` process.

## Hash Preservation

### Protected parent paths

All start, post-focused, post-regression, post-full-suite, and post-live values
were identical.

| Path | SHA-256 before and after |
|---|---|
| `diagnostic_evidence.json` | `a626a69a8020bc730876119c52701a94de9ab6e4772cc64c1f5d017296650203` |
| `governed_return.json` | `e82f47c0c13678725993b21e2af2e0437edccaed324f861a7b58e77d7f8e787d` |
| `lineage.json` | `07b95505521e70f51cdddecc1057fd3a208b198445693c9a8da1e996df5799dd` |
| `provider_stderr.txt` | `d47a06d59aba2814c3fb7460049fc2ccbfc834196c956d6c6558e8be8b079e24` |
| `provider_stdout.txt` | `a73a499e2e9133c03d7babfd5c4dec7967f31e2bfb354ea9dd41df0a15c08cb3` |
| `governed_returns.jsonl` | `dbc7b63f2a17c50c43bbb4fde4f44c1dbae8d25d550fb6b4d4daa14e17126161` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

### Disposable source paths

| Path | SHA-256 before | SHA-256 after |
|---|---|---|
| `calc.py` | `8f85450200db13108dc37d54ada5376d715d7c7aff3bceb5ffa1f6a75b0c8a03` | identical |
| `test_calc.py` | `cac4bf2b856d89f3deae7ec90005b7be26a43dafc22c7af5b6637519c20f30ed` | identical |

The pre-live focused test created an untracked `__pycache__/` in the disposable
repository before AiCLI execution. Neither source file changed during the live
call.

## Git Status and Commit Commands

Parent status preserves the six pre-existing modified runtime evidence paths
and the three pre-existing untracked root markers. G31-20E adds only the new
focused test and this report. Nested status remains clean.

Report-only staging and commit commands, explicitly excluding protected paths:

```bash
git add \
  tests/test_g31_20e_governed_development_request_routing_reaudit.py \
  docs/governance/G31_20E_GOVERNED_DEVELOPMENT_REQUEST_ROUTING_REAUDIT.md
git commit -m "test(governance): re-audit governed development routing"
```

No commit was created by this task.

## Progress and Recommended Next State

Evidence-scoped whole-project progress is **91.2%**. The routing ambiguity is
closed: knowledge requests and grounded development requests reach distinct
existing routes without classifier changes. The remaining live gap is now
narrower and occurs at the canonical Repository Cognition compatibility
contract, before execution authorization or Worker activation.

Recommended next state:

`G31_DISPOSABLE_REPOSITORY_SCOPE_GROUNDING_FIXTURE_CONTRACT_AUDIT_REQUIRED`

That phase should be read-only first. It should identify a truthful disposable
repository layout and request-derived canonical capability target already
accepted by the existing Repository Cognition owner. It must not weaken exact
capability matching, bypass grounding, or reuse this stopped live attempt.
