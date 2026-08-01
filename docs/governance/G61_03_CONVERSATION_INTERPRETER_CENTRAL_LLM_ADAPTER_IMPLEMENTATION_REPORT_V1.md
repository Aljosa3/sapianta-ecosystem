# 1. Implementation Summary

Generation: G61-03

Report identity:
G61_03_CONVERSATION_INTERPRETER_CENTRAL_LLM_ADAPTER_IMPLEMENTATION_REPORT_V1

Reporting date: 2026-08-01

Certified development baseline:
CENTRAL_LLM_SERVICES_REUSE_PLAN_CERTIFIED

Authenticated repository anchor:

- Commit: `822d8feaeb858ee9b003729eff50046b2f5b3693`
- Direct parent: `1b0364fa6dc8c3170a71c9cf618dee8d07a28b79`
- Tree: `d8755e2a3440000a1e1083073bcbf509feae086d`
- Subject: `G61-02: certify Central LLM services reuse plan`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G61-01 Existing Central LLM Services Discovery and Constitutional
  Integration Audit Report V1
- G61-02 Central LLM Services Reuse and Integration Plan V1
- G58-01 Conversation Interpreter Architecture Report V1
- G59-04 Conversation Interpreter Proposal and Deterministic Validation Runtime
  Implementation Report V1
- G59-05 Conversation Layer V2 Proposal Commit Runtime Implementation Report V1
- Existing AiGOL Provider Adapter, Provider Registry, Provider Proposal Envelope,
  Provider Necessity Policy, and Unified Resource Selection contracts

Objective:

Implement the minimum provider-neutral adapter between the Conversation
Interpreter boundary and the existing authenticated External Provider Platform
(EPP), normalize one provider result into the existing G59-04 Interpreter
Proposal format, and submit it to deterministic validation without acquiring
semantic, commitment, or execution authority.

Implementation scope:

- Added the versioned
  `CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1` immutable
  cross-reference. It is not a provider or model registry.
- Added a bounded request translator with source-turn, Conversation Envelope,
  Semantic CWM revision, model, and integrity bindings.
- Reused the existing `ProviderRegistry`, unified resource-selection algorithm,
  `ProviderAdapter`, and `ProviderProposalEnvelope` unchanged.
- Added a closed response schema and deterministic conversion to G59-04 source
  spans, evidence references, semantic operations, ambiguity declarations,
  conflict declarations, and advisory confidence.
- Reused the existing G59-04 assessment owner for all semantic acceptance.
- Added stable fail-closed handling for registry, selection, provider, timeout,
  envelope, schema, identity, model, revision, and semantic validation failure.
- Added focused tests proving compatibility with the concrete existing OpenAI
  proposal adapter through an injected local client and with the separate
  G59-05 Proposal Commit Runtime.

Modified modules:

- `aigol/runtime/conversation_interpreter_epp_assistance_runtime_v1.py`:
  new thin Conversation Interpreter/EPP selection, request, response, and
  validation adapter.
- `tests/test_g61_03_conversation_interpreter_epp_assistance_runtime_v1.py`:
  focused positive, negative, compatibility, determinism, privacy, and
  authority-isolation coverage.
- `docs/governance/G61_03_CONVERSATION_INTERPRETER_CENTRAL_LLM_ADAPTER_IMPLEMENTATION_REPORT_V1.md`:
  this G48 implementation report.

Intentionally unchanged modules:

- Existing provider registry, resource registry, model configuration, provider
  adapters, credential owner, provider transports, provider governance, and
  unified selection runtime.
- Conversation Working Memory V2, Semantic Slot Runtime, Conversation State
  Machine, G59-04 proposal validator, G59-05 Proposal Commit Runtime, readiness,
  and Objective Commitment.
- Platform Core, AiCLI, HIR, Replay owners, Authorization, Worker, Development
  Governance, capability selection, PCBV31, and Git history.

Architectural boundaries preserved:

- Provider selection remains non-authorizing and is not semantic acceptance.
- Provider output remains an untrusted proposal.
- The adapter never mutates Semantic CWM and never invokes G59-05.
- Only the existing G59-04 owner determines proposal admissibility.
- Objective creation, Objective Commitment, Platform Core admission,
  Authorization, Worker dispatch, and execution remain unreachable.
- Human turn text, raw provider output, normalized proposal content, and
  validation content are not written to Replay. Only the existing content-free
  resource-selection evidence is written by its existing owner.

# 2. Code Evidence

## Implemented Runtime Surface

The new runtime exports these bounded public APIs:

```text
create_conversation_interpreter_epp_selection_and_binding_profile_v1
create_conversation_interpreter_epp_request_v1
adapt_epp_response_to_interpreter_proposal_v1
run_conversation_interpreter_epp_assistance_v1
```

Their deterministic interaction is:

```text
Conversation Envelope + Semantic CWM + exact human turn
  -> immutable interpreter/EPP selection and binding profile
  -> existing ProviderRegistry lookup
  -> existing select_unified_resource(PROVIDER_ROLE)
  -> bounded request through existing ProviderAdapter.generate_proposal
  -> existing ProviderProposalEnvelope validation
  -> closed normalized response vocabulary
  -> existing G59-04 proposal constructors
  -> existing G59-04 deterministic assessment
  -> candidate operation set or stable refusal
```

The adapter stops at the candidate-operation boundary. The focused compatibility
test calls G59-05 separately and proves that the returned candidate is usable by
the existing commit owner without giving the adapter commit authority.

## Reuse Evidence

| Existing surface | Reused API | Modification | Adapter authority |
|---|---|---|---|
| Provider metadata registry | `ProviderRegistry.lookup_provider` | None | Read-only exact identity, version, availability, and capability check |
| Unified resource selection | `select_unified_resource` | None | Requests one exact provider role and validates returned evidence |
| Provider necessity policy | `PROVIDER_REQUIRED` | None | Classification input only |
| Provider protocol | `ProviderAdapter.generate_proposal` | None | One bounded call; no retry or substitution |
| Provider envelope | `validate_provider_proposal_envelope` | None | Integrity and authority-bearing-field rejection |
| Concrete OpenAI proposal adapter | `OpenAIProviderAdapter` | None | Exercised using an injected deterministic local client; no network |
| Canonical serialization | `canonical_serialize`, `replay_hash` | None | In-memory request/result integrity only |
| G59-04 Interpreter Proposal | constructors and `assess_conversation_interpreter_proposal_v2` | None | Sole semantic proposal validator |
| G59-05 Proposal Commit | `commit_proposal_candidate_operations_v2` | None | Compatibility test only; never imported by runtime adapter |

No provider-specific adapter is imported by the new runtime. The concrete
OpenAI adapter appears only in the focused test to prove compatibility with an
existing EPP implementation.

## Selection and Binding Profile

The immutable profile binds:

- exact interpreter identity, class, and version;
- exact G59-04 proposal schema;
- existing EPP resource, provider identity, and provider version;
- immutable model and model-configuration version;
- provider-composition-owned credential reference identity, never a secret;
- existing `PROPOSAL_GENERATION`, `PROVIDER_ROLE`, `GOVERNANCE`,
  `PROVIDER_REQUIRED`, and `PROVIDER_PROPOSAL_ONLY` vocabulary;
- configured timeout and input/output byte bounds;
- external-data-processing declaration; and
- false streaming, tools, function calling, automatic retry, substitution,
  memory, semantic, Objective, commit, execution, and Worker authority.

G61-03 expressly prohibited modification of existing registries. Therefore the
profile uses the already registered `PROPOSAL_GENERATION` capability and
`GOVERNANCE` domain instead of mutating the unified resource registry to add
new conversation-specific tokens. The exact immutable profile digest binds
this compatibility choice.

## Request Translation and Integrity

The request translator:

- validates the current native V2 state;
- binds exact conversation, workspace, session, CWM revision, semantic
  revision, source-turn identity, and source-turn digest;
- carries a bounded semantic-slot snapshot without filesystem/runtime handles;
- binds the exact configured model and response schema;
- produces a deterministic provider proposal identity and canonical request
  integrity hash;
- applies the profile input-byte bound; and
- instructs the provider to return proposal data only, never tool calls,
  commitment, or execution instructions.

The provider envelope is accepted only when provider identity/version,
provider proposal identity, model, and original request binding match. The
generic request-binding check supports existing adapters that wrap the
original request in their own provider-neutral envelope shape.

## Response Normalization and Validation

The adapter accepts one closed JSON object containing only:

- semantic operations;
- exact source-span indexes;
- evidence references;
- advisory confidence with `authority_effect = false`;
- ambiguity operation indexes; and
- conflict operation indexes.

Unknown top-level, operation, source-span, evidence, or confidence fields fail
closed. The adapter resolves provider-local evidence keys and operation indexes
into deterministic G59-04 identities, then calls the existing G59-04
constructors and assessor. The assessor continues to own exact revision,
source-span, slot taxonomy, relationship, conflict, confidence, interpreter,
integrity, and authority validation.

Provider confidence never changes validation authority. An admissible result
means only that a G59-04 candidate operation set exists.

## Failure and Timeout Behavior

| Condition | Stable local disposition | Mutation or retry |
|---|---|---|
| Invalid profile, state, provider metadata, adapter identity, model, timeout, or bounds | `ADAPTER_INPUT_REJECTED` | None |
| Existing unified selection refusal | `RESOURCE_SELECTION_FAILED` | None |
| Provider call failure | `PROVIDER_FAILURE` | None; one call only |
| Direct or wrapped timeout cause | `PROVIDER_TIMEOUT` | None; no retry/substitution |
| Returned malformed/over-limit/authority-bearing/mismatched response | `PROVIDER_RESPONSE_REJECTED` | None |
| Validly normalized proposal rejected by G59-04 | `VALIDATION_REJECTED` with G59-04 reason | None |
| Valid proposal | `NORMALIZED_AND_VALIDATED` | Candidate only; no commit |

Timeout classification follows the existing fail-closed exception chain. This
preserves concrete adapter contracts that wrap transport causes without adding
provider-specific branches.

## Replay and Authority Evidence

The returned result exposes only provider/request/proposal integrity hashes,
the normalized local proposal and validation result, and explicit boundary
flags. It does not return raw provider response data or credentials.

The result fixes all of these to false:

```text
semantic_cwm_mutated
proposal_commit_performed
conversation_transition_applied
objective_created
objective_commitment_created
platform_core_invoked
development_governance_invoked
capability_selection_invoked
authorization_created
worker_invoked
execution_invoked
provider_content_replay_written
```

The test reads the selection Replay files and confirms that human turn text,
provider response fields, and semantic operations are absent.

## Focused Regression Evidence

The focused suite contains eight tests:

1. existing EPP result normalizes and validates without authority or CWM
   mutation;
2. the validated candidate commits only through a separate G59-05 call;
3. the existing concrete OpenAI proposal adapter works through an injected
   local client with one non-streaming call and no credential leakage;
4. repeated identical semantic inputs produce identical request, proposal,
   candidate, provider-envelope, and integrity bindings;
5. a timeout wrapped by the existing fail-closed provider contract returns
   `PROVIDER_TIMEOUT` with one call and no candidate;
6. provider-registry version mismatch fails before selection and invocation;
7. authority-shaped response content fails before normalization or validation;
8. the runtime import graph contains no provider-specific or execution-owner
   import.

Artifact SHA-256 values before report creation:

| Artifact | SHA-256 |
|---|---|
| `aigol/runtime/conversation_interpreter_epp_assistance_runtime_v1.py` | `22730a2e8f3bfbfcd4989abec0cdff630f6489da10b44c58eb5ad7c89d8cf430` |
| `tests/test_g61_03_conversation_interpreter_epp_assistance_runtime_v1.py` | `5a03289a333c38a4422867e1da643ecfca4e59f44681cfedad181fe8a9d5df2d` |

These hashes are evidence captured during implementation and are refreshed in
the validation matrix if formatting or repair changes alter either artifact.

# 3. Constitutional Self-Assessment

## Verified

- The G61-02 authenticated baseline is the direct repository anchor for this
  implementation.
- The runtime reuses the existing provider registry, unified resource
  selection, provider protocol, provider envelope, concrete provider adapter,
  and G59-04 proposal owner without modifying any of them.
- There is one provider-neutral adapter and no duplicate provider, model,
  credential, selection, transport, Replay, Authorization, Worker, Objective,
  or execution infrastructure.
- Provider and model configuration are immutable caller-supplied bindings, not
  dynamically registered or provider-selected authority.
- The existing OpenAI proposal adapter was exercised with a local injected
  client and no network access.
- Provider selection uses exactly `PROVIDER_ROLE`; hybrid resources can be
  accepted only when selection returns that provider role and the
  proposal-only authority profile.
- Every normalized result is passed to the unchanged G59-04 assessor.
- Semantic CWM mutation is absent from the adapter. The separate G59-05
  compatibility test confirms ownership remains downstream.
- Timeout, provider failure, registry mismatch, malformed content, and
  authority-shaped output fail closed without retry, substitution, partial
  mutation, Objective creation, or execution.
- Existing selection Replay contains no human turn, raw provider output,
  normalized semantic operations, credentials, or validation content.
- G59, G60, focused G61-03, provider proposal, selection, and governance
  conformance tests pass.

## Not Verified

- No live provider or network call was authorized or performed. The existing
  concrete OpenAI adapter was tested only through its injected local client.
- Provider-family bindings other than the already authenticated first OpenAI
  proposal adapter were not certified by this generation.
- Credential vault composition and live credential retrieval were not invoked;
  the adapter receives an already composed `ProviderAdapter` and never sees a
  credential value.
- No default HIR/AiCLI route was enabled. Conversation integration remains
  opt-in and caller-owned.
- The governance conformance engine continues to report the repository's
  pre-existing hook drift as `PARTIALLY_CONFORMANT`: the root expected and
  installed pre-commit hooks are missing, and the system pre-commit hook lacks
  `promotion_gate_v02` and `check_layer_freeze`. It reports zero critical
  violations and this generation does not alter hooks.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Binding profile and provider registry compatibility | New runtime profile validator and provider lookup | Focused registry success/mismatch tests | PASS |
| Existing selection reuse | Unified resource selection call and selection evidence checks | Focused success test plus unified selection regressions | PASS |
| Existing provider interface reuse | `ProviderAdapter.generate_proposal` and provider envelope validator | Protocol double and concrete OpenAI adapter tests | PASS |
| Request translation | Bound request capsule, prompt, byte bound, request hash | Focused success and deterministic-repeat tests | PASS |
| Response normalization | Closed response/operation/evidence/span/confidence schema | Focused valid and authority-shaped response tests | PASS |
| Deterministic validation | Existing G59-04 assessor and candidate set | Focused success and 223-test adjacent aggregate | PASS |
| Proposal Commit separation | Runtime has no G59-05 import; test invokes G59-05 separately | Focused compatibility and import-boundary tests | PASS |
| Timeout/failure propagation | Exception-chain timeout classification and stable failure codes | Wrapped-timeout and mismatch tests | PASS |
| Replay content locality | Existing selection Replay only | Focused Replay content assertions | PASS |
| No execution authority | Explicit false boundary flags and import scan | Focused success, rejection, timeout, and import tests | PASS |
| Focused G61-03 regression suite | `tests/test_g61_03_conversation_interpreter_epp_assistance_runtime_v1.py` | `python -m pytest ... -q`: 8 passed | PASS |
| G59/G60 adjacent Conversation Layer, selection, provider proposal, governance conformance regressions | 14 selected test modules | `python -m pytest ... -q`: 223 passed | PASS |
| Governance conformance tests | `tests/test_governance_conformance.py` included in aggregate | All five governance conformance tests passed | PASS |
| Governance engine visibility | `python -m runtime.governance.governance_conformance_engine` | 18 checks passed, 2 pre-existing hook checks failed, 0 critical violations, deterministic/read-only/fail-closed, `PARTIALLY_CONFORMANT` | KNOWN_LIMITATION |
| Python compilation | New runtime/test and complete `aigol`/`tests` trees | `python -m py_compile ...`; `python -m compileall -q aigol tests` | PASS |
| Worktree hygiene | Runtime, test, and report | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/conversation_interpreter_epp_assistance_runtime_v1.py`:
  added the provider-neutral Conversation Interpreter/EPP assistance adapter,
  immutable binding profile, request translator, response normalizer,
  integrity binding, deterministic validation bridge, and fail-closed result.
- `tests/test_g61_03_conversation_interpreter_epp_assistance_runtime_v1.py`:
  added eight focused regression and compatibility tests.
- `docs/governance/G61_03_CONVERSATION_INTERPRETER_CENTRAL_LLM_ADAPTER_IMPLEMENTATION_REPORT_V1.md`:
  added this implementation evidence report.

Unchanged subsystems:

- Platform Core, Replay, Authorization, Worker, Development Governance,
  capability selection, Objective Commitment, PCBV31, HIR, and AiCLI.
- Existing provider registry, model configuration, resource registry, provider
  adapters, provider transports, credentials, provider governance, and unified
  selection algorithm.
- Existing G59 Conversation Layer runtime owners and G60 integration paths.

API compatibility:

- The implementation is additive. No existing public API, registry entry,
  priority, provider identity, provider adapter, schema, or persisted state was
  changed.
- The adapter is injected with existing provider and interpreter bindings; no
  default route or live provider is enabled.

Replay compatibility:

- Existing unified selection Replay format and reconstructor remain unchanged.
- No new Replay schema or content-bearing Replay artifact was introduced.

Boundary preservation:

- EPP owns provider metadata, selection, and invocation contracts.
- G59-04 owns proposal validation.
- G59-05 remains the only owner that may apply an admissible candidate.
- Objective Commitment and the certified execution pipeline remain downstream
  and unreachable from this runtime.

Unrelated pre-existing changes:

- None observed at implementation start.

# 6. Certification Verdict

CONVERSATION_INTERPRETER_CENTRAL_LLM_ADAPTER_ESTABLISHED
