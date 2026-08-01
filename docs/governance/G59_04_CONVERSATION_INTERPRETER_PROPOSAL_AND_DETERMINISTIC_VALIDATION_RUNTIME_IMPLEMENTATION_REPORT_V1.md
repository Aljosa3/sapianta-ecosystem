# 1. Implementation Summary

Generation: G59-04

Report identity:
G59_04_CONVERSATION_INTERPRETER_PROPOSAL_AND_DETERMINISTIC_VALIDATION_RUNTIME_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline: CONVERSATION_STATE_MACHINE_RUNTIME_ESTABLISHED

Authenticated repository anchor:
`f1a8aebf56b30beda1ebcefbd26bfb0bd66416d1`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G57-02 Typed Semantic Slot Taxonomy Validation Report V1
- G57-03 Conversation Envelope Architecture Report V1
- G57-04 Conversation State Machine and Objective Commitment Protocol Report V1
- G58-01 Conversation Interpreter Architecture Report V1
- G59-01 Conversation Layer V2 Runtime Foundation Implementation Report V1
- G59-02 Conversation Layer V2 Semantic Slot Runtime Implementation Report V1
- G59-03 Conversation Layer V2 State Machine Runtime Implementation Report V1

Objective:

Establish the isolated receiving boundary through which interchangeable
interpreters can submit bounded, versioned semantic proposals. The runtime
authenticates local proposal structure and bindings, performs deterministic
validation, and reduces an admissible proposal only to a non-authoritative
candidate operation set. It grants no interpreter authority over Semantic
CWM, conversation transitions, Objective Commitment, Platform Core, or
execution.

Implementation scope:

- Added one closed V1 proposal schema with content bounds, deterministic
  proposal identity, and SHA-256 integrity.
- Added a caller-supplied closed interpreter registry boundary for the four
  G58-01 interpreter classes; class and confidence never alter authority.
- Added exact Conversation Envelope, source-turn, global CWM revision, and
  semantic revision bindings.
- Added six proposed operation types over the six G57-02 semantic slot
  classes: creation, revision, equivalence, conflict, clarification, and
  reference attachment.
- Added closed taxonomy, source-span, evidence-reference, dependency,
  equivalence, relationship, ambiguity, conflict, and forbidden-authority
  validation.
- Added deterministic proposal-to-candidate reduction without persistence or
  state mutation.
- Added order-independent multi-interpreter comparison. Compatible proposals
  form a non-authoritative union; material conflicts require clarification;
  majority and confidence have no selection effect.
- Added focused rejection, determinism, compatibility, and import-isolation
  tests.

Modified modules:

- `aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py`:
  new isolated proposal schema, validator, candidate reducer, and comparator.
- `tests/test_g59_04_conversation_interpreter_proposal_runtime_v2.py`: focused
  G59-04 behavior, boundary, negative-path, and compatibility suite.
- `docs/governance/G59_04_CONVERSATION_INTERPRETER_PROPOSAL_AND_DETERMINISTIC_VALIDATION_RUNTIME_IMPLEMENTATION_REPORT_V1.md`:
  this G48 implementation report.

Intentionally unchanged modules:

- G59-01 atomic Conversation Working Memory V2 schema and persistence.
- G59-02 Semantic Slot Runtime and its mutation authority.
- G59-03 Conversation State Machine Runtime and transition authority.
- External providers and central Language Services/model registries.
- Objective Commitment, Objective creation, Platform Core admission and
  execution, Development Governance, capability selection, Authorization,
  Worker, completion, and Replay.
- AiCLI, Human Interface Runtime, Conversation Boundary, Project Services,
  PCBV31, G31, G35, and existing governance artifacts.

Architectural boundaries preserved:

- The runtime imports only the common fail-closed error model and the G59-01
  isolated schema/taxonomy owner.
- Proposal and candidate results contain fixed false authority, mutation,
  transition, Objective, and execution fields.
- No provider client, network library, Objective owner, Replay owner,
  Authorization owner, Worker owner, Development Governance owner, or PCBV31
  owner is imported or invoked.
- Validation ends at a candidate operation set; there is no persistence API,
  Semantic CWM reducer call, state-machine transition, or pipeline handoff.

# 2. Code Evidence

## Authenticated Baseline

The implementation begins at commit
`f1a8aebf56b30beda1ebcefbd26bfb0bd66416d1`, parent
`d36f8647c10bfd0adacfedaad1eb6ddf2171c332`, tree
`932cbee55330ed374ec85df0a828cab8e6f05ad5`.

| Baseline evidence | Git blob | Use |
|---|---|---|
| G58-01 interpreter architecture | `7525ff59955ef80e449824f73998e2ff04efa6cb` | Proposal-only trust boundary, interpreter classes, comparison, and provider separation. |
| G59-01 V2 foundation | `4bd2e7e4f84a95e09402314945b6a6bece51231a` | Atomic state validation, Envelope bindings, six-class taxonomy, canonical JSON, digests, and bounds. |
| G59-02 semantic reducer | `94f79a7779b16675de79679ca85b8e8e6d765883` | Active slot lifecycle and identities against which candidate operations are checked. |
| G59-03 state machine | `74d92bbc410deabbcdef9a1d1c8a068a9b127ebe` | Active pre-commit phases and transition authority that remain outside G59-04. |

## Public Runtime API

Repository reference:
`aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py`.

The public receiving surface is additive and local:

```python
def create_conversation_interpreter_proposal_v2(
    *,
    interpreter_identity: str,
    interpreter_class: str,
    interpreter_version: str,
    conversation_identity: str,
    workspace_identity_hash: str,
    session_identity_hash: str,
    source_turn_identity: str,
    source_turn_digest: str,
    expected_cwm_revision: int,
    expected_semantic_revision: int,
    proposed_semantic_operations: list[dict[str, Any]],
    evidence_references: list[dict[str, Any]] | None = None,
    advisory_confidence: dict[str, Any] | None = None,
    ambiguity_declaration: dict[str, Any] | None = None,
    conflict_declaration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one canonical proposal envelope without accepting its meaning."""
```

```python
def validate_conversation_interpreter_proposal_v2(
    proposal: dict[str, Any],
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    interpreter_registry: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate one proposal and return candidate operations without mutation."""
```

The excerpts omit the function bodies. The complete public surface also
provides source-turn binding, source-span, evidence-reference, proposed
operation, fail-closed assessment, and multi-interpreter comparison helpers.

There is no orchestration or persistence entry point in this runtime.

## Proposal Schema

The schema is closed by exact field sets. Interpreter classes are descriptive
only:

```python
INTERPRETER_CLASSES = frozenset(
    {
        DETERMINISTIC_PARSER,
        EXTERNAL_LANGUAGE_MODEL,
        RULE_BASED_INTERPRETER,
        OTHER_CERTIFIED_INTERPRETER,
    }
)

PROPOSED_OPERATION_TYPES = frozenset(
    {
        PROPOSE_SLOT_CREATION,
        PROPOSE_SLOT_REVISION,
        PROPOSE_SEMANTIC_EQUIVALENCE,
        PROPOSE_CONFLICT,
        PROPOSE_CLARIFICATION_REQUIREMENT,
        PROPOSE_REFERENCE_ATTACHMENT,
    }
)
```

The proposal constructor canonicalizes operation and evidence order before
deriving identity and integrity:

```python
        "proposed_semantic_operations": sorted(
            deepcopy(proposed_semantic_operations),
            key=lambda operation: operation.get("operation_id", ""),
        ),
        "evidence_references": sorted(
            deepcopy(evidence_references or []),
            key=lambda reference: reference.get("reference_id", ""),
        ),
        "advisory_confidence": deepcopy(
            advisory_confidence or _default_confidence()
        ),
        "ambiguity_declaration": deepcopy(
            ambiguity_declaration or _empty_declaration()
        ),
        "conflict_declaration": deepcopy(
            conflict_declaration or _empty_declaration()
        ),
        "boundary_flags": deepcopy(_BOUNDARY_FLAGS),
        "integrity_checksum": None,
```

The excerpt begins and ends inside the proposal dictionary; unrelated binding
fields and the closing identity call are omitted.

## Deterministic Validation Rules

Proposal type, version, integrity, and identity fail closed before semantic
reduction:

```python
    if candidate["proposal_type"] != (
        PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1
    ) or candidate["proposal_version"] != "V1":
        _reject("UNKNOWN_PROPOSAL_VERSION", "proposal type or version is unknown")
    supplied_integrity = candidate["integrity_checksum"]
    integrity_body = deepcopy(candidate)
    integrity_body.pop("integrity_checksum")
    if supplied_integrity != _checksum(integrity_body):
        _reject("INVALID_INTEGRITY", "proposal integrity is invalid")
    identity_body = deepcopy(candidate)
    identity_body["proposal_id"] = None
    identity_body["integrity_checksum"] = None
    expected_id = "interpreter-proposal-local-sha256:" + hashlib.sha256(
        _canonical_bytes(identity_body)
    ).hexdigest()
    if candidate["proposal_id"] != expected_id:
        _reject("INVALID_PROPOSAL_IDENTITY", "proposal identity is invalid")
```

The exact state and source turn must match the proposal:

```python
    if candidate["expected_cwm_revision"] != state["revision"] or candidate[
        "expected_semantic_revision"
    ] != state["semantic_revision"]:
        _reject("STALE_CWM_REVISION", "proposal CWM revision binding is stale")
    expected_bindings = {
        "conversation_identity": envelope["conversation_identity"],
        "workspace_identity_hash": envelope["workspace_identity_hash"],
        "session_identity_hash": envelope["session_identity_hash"],
    }
    for field, expected in expected_bindings.items():
        if candidate[field] != expected:
            _reject("CONVERSATION_BINDING_MISMATCH", f"{field} binding is invalid")
```

The validator additionally checks the closed interpreter registry, active
pre-commit phase, bounded content, source spans, evidence identities, six-class
taxonomy, derived slot identities, canonical values, dependencies, operation
relationships, declarations, and all forbidden authority fields. Stable
rejection codes are returned through `assess_conversation_interpreter_proposal_v2`.

## Candidate Operation Model

Each validated operation is newly projected as candidate-only data:

```python
        validated.append(
            {
                "candidate_operation_type": _CANDIDATE_OPERATION_TYPE[operation_type],
                "operation_id": item["operation_id"],
                "slot_class": slot_class,
                "slot_role": slot_role,
                "cardinality_key": cardinality,
                "proposed_slot_id": expected_slot_id,
                "target_slot_id": target,
                "surface_value": item["surface_value"],
                "canonical_value": canonical_value,
                "validator_derived_equivalence_key": equivalence_key,
                "source_spans": spans,
                "depends_on_slot_ids": depends_on,
                "evidence_reference_ids": evidence_ids,
                "clarification_reason": item["clarification_reason"],
                "advisory_confidence": deepcopy(advisory_confidence),
                "authority_effect": False,
            }
        )
```

The candidate set records immutable bindings and a digest of the semantic
projection. Independent comparison validation re-derives the candidate slot
taxonomy, canonical equivalence keys, semantic reduction digest, conflict
bindings, and disposition before comparing sets. Recomputed outer identity
and integrity therefore cannot conceal a forged semantic digest.

## Conflict and Ambiguity Handling

Conflict declarations must exactly equal deterministically detected conflicts:

```python
    detected_conflicts = _detect_internal_conflicts(operations)
    if set(conflict["operation_ids"]) != detected_conflicts:
        _reject(
            "CONFLICT_DECLARATION_MISMATCH",
            "proposal conflict declaration is not deterministic",
        )
    clarification_ids = {
        operation["operation_id"]
        for operation in operations
        if operation["candidate_operation_type"]
        == _CANDIDATE_OPERATION_TYPE[PROPOSE_CLARIFICATION_REQUIREMENT]
    }
    clarification_required = bool(
        ambiguity["operation_ids"] or conflict["operation_ids"] or clarification_ids
    )
```

Multi-interpreter comparison is input-order independent. Conflicting values
for the same canonical slot position produce `MATERIAL_CONFLICT`; two matching
interpreters cannot outvote a conflicting third interpreter. Compatible
differences may form a non-authoritative union, while every incoming
clarification requirement remains fail closed.

## Central Language Services Compatibility

The boundary accepts a registered interpreter identity, declared class, and
version without any provider-specific field. `EXTERNAL_LANGUAGE_MODEL` uses
the same proposal schema, validator, false authority flags, and candidate
reducer as deterministic and rule-based interpreters.

The G59-04 module contains no OpenAI, Claude, Gemini, Mistral, provider-client,
HTTP, socket, subprocess, or central-model-registry import. A future central
Language Services owner can construct this schema and supply its certified
descriptor through the same registry argument, but that owner, its provider
selection, network execution, authentication, and lifecycle are not
implemented or certified here.

## Constitutional Boundary Verification

The module-level contract is explicit:

```python
"""Pure, non-authoritative Conversation Interpreter proposal boundary.

Interpreters submit bounded data.  This module validates, compares, and
reduces that data only into non-authoritative candidate operations.  It never
mutates Conversation Working Memory, advances the Conversation State Machine,
creates an Objective, or invokes any execution-pipeline owner or provider.
"""
```

Authority flags are fixed false rather than supplied as policy choices:

```python
_BOUNDARY_FLAGS = {
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "semantic_cwm_mutation_authority": False,
    "conversation_state_transition_authority": False,
    "human_confirmation_authority": False,
    "objective_commitment_authority": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
    "platform_core_invocation_supported": False,
    "replay_visible": False,
    "replay_mutation_supported": False,
    "development_governance_supported": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "tool_execution_supported": False,
}
```

Proposal keys for CWM mutation, confirmation, commitment, Objective,
capability, Platform Core, Development Governance, Authorization, Worker,
Replay, execution, tool calls, shell commands, and approval decisions are
recursively rejected. Natural-language confirmation and Objective Commitment
operation tokens are also rejected as control acts.

Confidence is validated only as bounded advisory data with
`authority_effect: false`. Candidate sets and comparison results additionally
fix `confidence_authority_effect`, `majority_authority_effect`,
`semantic_cwm_mutated`, `conversation_transition_applied`,
`objective_created`, and `execution_invoked` to false.

# 3. Constitutional Self-Assessment

## Verified

- The proposal schema is closed, versioned, bounded to 65,536 canonical JSON
  bytes, and protected by deterministic proposal identity and integrity.
- All four interpreter classes pass through one authority-neutral schema and
  registry binding; an external-LLM-class proposal performs no provider or
  network execution.
- Exact conversation, workspace, session, source-turn, CWM revision, and
  semantic revision mismatches fail closed.
- The six proposed operation types are constrained to the six canonical slot
  classes and validator-derived slot and equivalence identities.
- Unknown versions, identities, classes, slot classes, operations, stale
  bindings, malformed spans, invalid integrity, contradictory operations,
  confirmation, commitment, direct mutation, and execution fields have stable
  rejection behavior.
- Proposal reduction produces candidate data only and leaves the supplied
  G59-01/02/03 state byte-for-byte unchanged.
- Ambiguity, explicit clarification, and material conflict prevent reduction;
  majority and confidence never resolve conflict or grant authority.
- Candidate comparison is order-independent and independently revalidates
  semantic projection digests and fail-closed dispositions.
- The 107-test combined G59-01/02/03/04 suite, 38 adjacent Conversation Layer
  regressions, 5 governance conformance tests, Python compilation, and
  repository whitespace validation pass.
- Static import and source tests demonstrate absence of execution-pipeline and
  provider imports or invocation paths.

## Not Verified

- No deterministic parser, rule-based interpreter, external language model,
  provider client, central Language Services registry, model selection,
  network transport, or interpreter lifecycle host is implemented or invoked;
  G59-04 certifies only the receiving boundary.
- No accepted candidate operation is applied to Semantic CWM, persisted,
  transitioned by the Conversation State Machine, confirmed by a human,
  committed to an Objective, or delivered to Platform Core. Those authorities
  remain explicitly outside this generation.
- Real AiCLI/HIR transport and end-to-end interpreter proposal production are
  not integrated or exercised.
- The read-only governance conformance engine remains
  `PARTIALLY_CONFORMANT` because of the repository's pre-existing root and
  system pre-commit hook drift. It reports 18 checks passed, 2 failed, zero
  critical violations, deterministic/fail-closed/read-only operation, and
  report hash
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.
- The complete repository regression was not run. The generation contract
  defines it as optional additional evidence; every mandatory focused,
  adjacent, governance, compilation, and whitespace validation completed.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Closed versioned proposal schema | Exact `_PROPOSAL_FIELDS`, V1 type/version gate, canonical constructor | Valid proposal plus unknown-version, unknown-field, malformed-content, and size-bound tests | PASS |
| Proposal identity and integrity | `_with_proposal_identity_and_integrity` and `_validate_proposal_envelope` | Identical-input byte determinism, tamper, identity, integrity, and self-consistent forged candidate-digest tests | PASS |
| Interpreter identity and class | Four-class vocabulary and closed registry descriptor | Deterministic-parser, external-LLM-class, unknown identity, class mismatch, and version mismatch paths | PASS |
| Source and state binding | Envelope comparison, source-turn identity/digest, revision checks | Stale revision and wrong conversation/session/workspace/source tests | PASS |
| Canonical slot compatibility | G59-01 six-class vocabulary, role/cardinality validators, derived slot identity | Unknown class, invalid slot identity, canonical value, dependency, and relationship tests | PASS |
| Bounded semantic operations | Six exact proposal operations and operation relationship validator | Creation, revision, equivalence, conflict, clarification, reference attachment, forbidden-operation, and contradiction tests | PASS |
| Candidate-only reduction | Candidate projection and fixed false authority/result fields | Positive proposal and G59 state-immutability assertions | PASS |
| Conflict and ambiguity handling | Declarations, `_detect_internal_conflicts`, deterministic comparator | Conflict, ambiguity, clarification, contradictory declaration, 2-vs-1 majority, and reversed-order tests | PASS |
| Confidence non-authority | Closed advisory confidence and semantic projection exclusion | Low/high confidence produces identical semantic digest and no authority | PASS |
| Confirmation and commitment exclusion | Forbidden control-operation vocabulary and recursive authority-key rejection | Natural-language confirmation and Objective Commitment proposal tests | PASS |
| Direct CWM and execution exclusion | Recursive forbidden-key scanner and fixed boundary flags | Direct CWM mutation, execution field, authority flag, and static import/source tests | PASS |
| Central Language Services compatibility | Provider-neutral registry descriptor and external-LLM-class fixture | Same validation API exercised without provider execution or provider imports | PASS |
| G59-01/02/03 compatibility | Existing focused suites plus G59-04 suite | Combined command completed with `107 passed` | PASS |
| Adjacent Conversation Layer regression safety | G55-03 CWM, G49-02 Conversation Boundary, G54-09 admission suites | Targeted adjacent command completed with `38 passed` | PASS |
| Governance conformance tests | Canonical governance conformance test module | `python -m pytest tests/test_governance_conformance.py -q` completed with `5 passed` | PASS |
| Repository hook installation conformance | Read-only governance conformance engine | Diagnostic remained `PARTIALLY_CONFORMANT`: 18 passed, 2 known hook checks failed, zero critical violations; hook installation is outside G59-04 authority | NOT_APPLICABLE |
| Python syntax and repository whitespace | New runtime, focused tests, report, and complete worktree diff | `python -m py_compile ...`; `git diff --check`; per-file `git diff --no-index --check /dev/null <new-file>` (difference exit with no whitespace diagnostics) | PASS |
| Optional complete repository regression | Generation contract classifies the run as additional evidence | Not run; mandatory bounded suites completed | NOT_APPLICABLE |
| External providers and execution-pipeline integration | Explicitly forbidden G59-04 surfaces | Static/runtime absence is required; functional integration is intentionally not implemented | NOT_APPLICABLE |
| G48 report structure | This report | Exactly six required top-level sections in required order | PASS |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py`:
  added the isolated proposal receiving boundary, validation, candidate
  reduction, and comparison runtime.
- `tests/test_g59_04_conversation_interpreter_proposal_runtime_v2.py`: added 26
  focused positive, negative, determinism, conflict, compatibility, and
  boundary tests.
- `docs/governance/G59_04_CONVERSATION_INTERPRETER_PROPOSAL_AND_DETERMINISTIC_VALIDATION_RUNTIME_IMPLEMENTATION_REPORT_V1.md`:
  added this G48 evidence report.

Unchanged subsystems:

- G59-01 atomic document schema and persistence.
- G59-02 Semantic Slot Runtime and mutation reducer.
- G59-03 Conversation State Machine Runtime and transition reducer.
- AiCLI, Human Interface Runtime, Conversation Boundary, Objective,
  Development Governance, capability selection, Platform Core execution,
  Authorization, Worker, completion, Replay, Providers, and Project Services.
- PCBV31, G31, G35, constitutional specifications, and Git history.

API compatibility:

- Existing G59-01, G59-02, and G59-03 public APIs and persisted document
  layouts are unchanged.
- G59-04 is an additive, separately versioned module. It consumes validated
  G59-01 state read-only and returns plain non-authoritative candidate data.
- No provider, transport, persistence, Objective, admission, or execution API
  is added or changed.

Boundary preservation:

- The implementation performs no filesystem persistence, Semantic CWM
  mutation, state transition, Objective creation, authorization, dispatch,
  execution, Replay write, or external network operation.
- Interpreter identity, class, confidence, and numerical majority remain
  evidence attributes without constitutional authority.
- Candidate operation sets cannot be mistaken for accepted Semantic CWM or
  execution evidence because their schemas and all authority/result flags are
  explicit and fail closed.

Unrelated pre-existing changes:

- None observed at the authenticated baseline or before G59-04 mutation.

# 6. Certification Verdict

CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_ESTABLISHED
