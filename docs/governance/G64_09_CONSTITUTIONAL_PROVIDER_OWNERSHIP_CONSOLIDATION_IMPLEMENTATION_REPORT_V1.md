# 1. Implementation Summary

Generation: G64-09

Report identity: G64_09_CONSTITUTIONAL_PROVIDER_OWNERSHIP_CONSOLIDATION_IMPLEMENTATION_REPORT_V1

Constitutional baseline: `constitutional-governance-finalize-v1`; certified
G64-01 through G64-08, including G64-05's authenticated direct provider
selection finding.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
G61-01 Existing Central LLM Services Discovery and Constitutional Integration
Audit Report V1; G62-01 Complete Constitutional Architecture Reconstruction
and Readiness Audit Report V1; G64-05 Constitutional Governance Revalidation
Report V1; G64-06 through G64-08 certified repairs.

Reporting date: 2026-08-02.

Objective:

Repair only the two authenticated provider-selection exceptions identified by
G64-01 and retained by G64-05: the native provider execution runtime and the
single-provider LLM cognition runtime. Each must obtain an explicit provider
selection from the existing Unified Resource Selection owner before invocation.

Implementation scope:

- Added one non-selecting integration binding that calls and validates the
  existing Unified Resource Selection owner.
- Bound both formerly direct runtime entry points to that binding and to its
  nested, replay-visible selection evidence.
- Bound terminal Replay reconstruction to the selection evidence and added
  focused regression coverage for success, missing selection, and tampering.

Modified modules:

- `aigol/runtime/authenticated_provider_selection_runtime.py` — shared
  authenticated selection binding; it delegates candidate selection to the
  existing Unified Resource Selection runtime.
- `aigol/runtime/native_provider_execution_runtime.py` — requires and records
  authenticated selection before native provider invocation.
- `aigol/runtime/llm_cognition_provider_runtime.py` — requires and records
  authenticated selection before cognition provider invocation.
- `tests/test_g64_09_constitutional_provider_ownership_v1.py` — focused
  ownership and fail-closed regression suite.

Intentionally unchanged modules:

- `aigol/runtime/unified_resource_selection_runtime.py` remains the existing
  authenticated provider-selection owner; its policy and candidate algorithm
  were not modified.
- Platform Core, Conversation Layer semantics, Development Governance,
  Constitutional Reuse Proof, Certification Completion Gate, Authorization,
  Worker, and AiCLI positive lineage are unchanged.
- Repository-wide negative closure validation is not introduced; it remains a
  separately sequenced future generation.

Architectural boundaries preserved:

- Unified Resource Selection selects but does not invoke; the new binding
  preserves that separation and carries only its immutable selection evidence.
- The specialized runtimes retain their existing single invocation, human
  approval, credential, transport, normalization, and Replay responsibilities.
- No provider gains governance, Authorization, Worker, execution-dispatch, or
  Replay-mutation authority.

# 2. Code Evidence

## Public API

`aigol/runtime/authenticated_provider_selection_runtime.py` exposes the shared
binding rather than a second candidate-selection algorithm:

```python
def select_authenticated_provider(
    *,
    selection_id: str,
    provider_id: str,
    workflow_type: str,
    required_capability: str,
    domain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Require the canonical selection owner to select one explicit provider."""
```

## Orchestration Entry Point

Both authenticated exceptions now call the same binding before their existing
credential and invocation stages. The native entry point is representative:

```python
provider_selection = select_authenticated_provider(
    selection_id=f"{execution_id}:UNIFIED-PROVIDER-SELECTION",
    provider_id=provider_id,
    workflow_type=PROVIDER_SELECTION_WORKFLOW,
    required_capability=PROVIDER_SELECTION_CAPABILITY,
    domain_id=PROVIDER_SELECTION_DOMAIN,
    created_at=created_at,
    replay_dir=replay_path,
)
```

The cognition entry point uses the same call with its own fixed workflow and
domain identifiers in `aigol/runtime/llm_cognition_provider_runtime.py`.

## Semantic Reductions

The binding delegates to the authenticated owner and requires an exact
provider identity; it neither scores candidates nor dispatches them:

```python
capture = select_unified_resource(
    selection_id=_require_string(selection_id, "selection_id"),
    workflow_type=_require_string(workflow_type, "workflow_type"),
    required_capability=_require_string(required_capability, "required_capability"),
    requested_role_type=PROVIDER_ROLE,
    domain_id=_require_string(domain_id, "domain_id"),
    provider_necessity_classification=PROVIDER_REQUIRED,
    preferred_resource_id=expected_resource_id,
    created_at=_require_string(created_at, "created_at"),
    replay_dir=selection_path,
)
```

## Public Validators

Native invocation now rejects a request that does not carry the authenticated
binding before it reaches a transport:

```python
_verify_artifact_hash(provider_request)
validate_authenticated_provider_selection(
    binding=provider_request.get("provider_selection"),
    provider_id=provider_request.get("provider_id"),
    required_capability=PROVIDER_SELECTION_CAPABILITY,
)
if not _is_nonempty_string(credential_secret):
    raise FailClosedRuntimeError("provider credential secret is unavailable")
```

The cognition request validator performs the equivalent binding validation.

## Canonical Data Models

The shared binding records the existing owner, exact selection identity, and
reconstructed selection Replay hash:

```python
binding = {
    "artifact_type": AUTHENTICATED_PROVIDER_SELECTION_BINDING_V1,
    "selection_owner": AUTHENTICATED_PROVIDER_SELECTION_OWNER,
    "selection_id": artifact["selection_id"],
    "selection_hash": artifact["artifact_hash"],
    "selection_replay_hash": reconstructed["replay_hash"],
    "selected_resource_id": expected_resource_id,
    "provider_id": normalized_provider_id,
    "required_capability": artifact["required_capability"],
    "workflow_type": artifact["workflow_type"],
    "domain_id": artifact["domain_id"],
    "replay_visible": True,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_requested": False,
    "authorization_created": False,
}
```

## Deterministic Algorithms

The binding reconstructs the existing owner's nested Replay evidence and
rejects any mismatch with the request-bound artifact:

```python
reconstructed = reconstruct_unified_resource_selection_replay(Path(replay_dir) / SELECTION_REPLAY_DIRECTORY)
if reconstructed["selection_id"] != validated["selection_id"]:
    raise FailClosedRuntimeError("authenticated provider selection replay reference mismatch")
if reconstructed["selected_resource_id"] != validated["selected_resource_id"]:
    raise FailClosedRuntimeError("authenticated provider selection replay resource mismatch")
if reconstructed["required_capability"] != validated["required_capability"]:
    raise FailClosedRuntimeError("authenticated provider selection replay capability mismatch")
if reconstructed["replay_hash"] != validated["selection_replay_hash"]:
    raise FailClosedRuntimeError("authenticated provider selection replay hash mismatch")
```

## Responsibility Boundaries

`aigol/runtime/unified_resource_selection_runtime.py` remains the selection
owner. Its public contract continues to state:

```python
"""Select an eligible resource and active role without invoking it."""
```

The G64-09 binding calls that owner and validates its result; it does not
duplicate registry traversal, eligibility evaluation, priority ordering, or
invocation authority.

# 3. Constitutional Self-Assessment

## Verified

- The two G64-01/G64-05 direct selection exceptions now obtain provider
  identity through `UNIFIED_RESOURCE_SELECTION_RUNTIME_V1`.
- Both request artifacts bind the selection artifact hash and nested selection
  Replay hash; both terminal Replay reconstructors revalidate that nested
  evidence.
- Native invocation fails closed before transport when the authenticated
  selection binding is absent.
- Selection evidence remains non-invoking and non-authoritative; existing
  human approval, credential, invocation, response, and Replay boundaries are
  preserved.
- Focused regression compatibility, governance conformance, Python
  compilation, and whitespace integrity completed successfully.

## Not Verified

- Repository-wide negative closure validation remains intentionally outside
  this generation and was not run. It is not required to demonstrate the two
  authenticated G64-09 exception paths and remains a later generation.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Unified provider ownership for native execution | Native request carries the shared binding and `provider_selection_owner` reconstructs as `UNIFIED_RESOURCE_SELECTION_RUNTIME_V1` | `pytest -q tests/test_g64_09_constitutional_provider_ownership_v1.py` | PASS |
| Unified provider ownership for single-provider cognition | Cognition request carries the same binding and nested Replay reconstruction | `pytest -q tests/test_g64_09_constitutional_provider_ownership_v1.py` | PASS |
| Eliminate duplicate selection at both authenticated exceptions | Both entry points call `select_authenticated_provider`, which delegates to `select_unified_resource`; no candidate-selection logic was added | Focused source/API regression plus owner assertions | PASS |
| Missing selection fails closed before native transport | `invoke_provider_once` validates `provider_selection` before credential or transport use | Focused missing-binding regression | PASS |
| Selection Replay tampering fails closed | Nested owner Replay reconstruction verifies immutable hashes | Focused tampering regression | PASS |
| Regression compatibility | Existing native and cognition runtime suites plus affected consumer suites | `pytest -q tests/test_execution_summary_enforcement_repair_v1.py tests/test_first_real_provider_runtime_v1.py tests/test_cognition_artifact_runtime_v1.py tests/test_conversational_progress_binding_v1.py tests/test_unified_resource_selection_runtime_v1.py tests/test_g64_09_constitutional_provider_ownership_v1.py` — 46 passed | PASS |
| Focused runtime compatibility | Existing direct runtime suites and G64-09 regression | `pytest -q tests/test_g64_09_constitutional_provider_ownership_v1.py tests/test_native_provider_execution_runtime_v1.py tests/test_llm_cognition_provider_runtime_v1.py` — 19 passed | PASS |
| Governance conformance | Existing conformance suite and read-only engine | `pytest -q tests/test_governance_conformance.py` — 5 passed; `python -m runtime.governance.governance_conformance_engine` — 20 passed, 0 failed, `CONFORMANT` | PASS |
| Python compilation | Modified runtime modules compile | `python -m py_compile aigol/runtime/authenticated_provider_selection_runtime.py aigol/runtime/native_provider_execution_runtime.py aigol/runtime/llm_cognition_provider_runtime.py` | PASS |
| Whitespace integrity | Repository diff | `git diff --check` | PASS |
| Repository-wide negative closure validation | Explicitly deferred by G64-09 scope | Not run; separate future generation | NOT_APPLICABLE |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/authenticated_provider_selection_runtime.py` — additive,
  shared binding to the authenticated Unified Resource Selection owner.
- `aigol/runtime/native_provider_execution_runtime.py` — authenticated
  selection admission, request lineage, invocation validation, and replay
  reconstruction binding.
- `aigol/runtime/llm_cognition_provider_runtime.py` — the equivalent
  selection admission, request lineage, and replay reconstruction binding.
- `tests/test_g64_09_constitutional_provider_ownership_v1.py` — focused
  success and fail-closed evidence.
- `docs/governance/G64_09_CONSTITUTIONAL_PROVIDER_OWNERSHIP_CONSOLIDATION_IMPLEMENTATION_REPORT_V1.md` — this G48 report.

Unchanged subsystems:

- Unified Resource Selection policy and registry; Platform Core; Conversation
  Layer semantics; Development Governance; Constitutional Reuse Proof Runtime;
  Certification Completion Gate; Authorization; Worker; existing AiCLI
  positive lineage; production admission.

API compatibility:

- Existing public runtime entry-point signatures are unchanged. Their returned
  request and Replay artifacts gain additive authenticated selection evidence.
- The two request-construction APIs now require an authenticated selection
  binding, preventing construction of a new directly-selected request.

Boundary preservation:

- Selection remains centralized in the existing non-invoking owner. The shared
  binding carries immutable evidence only; it grants no provider, governance,
  execution, Worker, Authorization, or Replay authority.

Unrelated pre-existing changes:

- None observed before the G64-09 mutation.

# 6. Certification Verdict

CONSTITUTIONAL_PROVIDER_OWNERSHIP_ESTABLISHED
