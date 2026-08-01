# 1. Implementation Summary

Generation: G61-02

Report identity: G61_02_CENTRAL_LLM_SERVICES_REUSE_AND_INTEGRATION_PLAN_V1

Reporting date: 2026-08-01

Constitutional baseline:
EXISTING_CENTRAL_LLM_SERVICES_LOCATED_AND_CHARACTERIZED

Authenticated repository anchor:

- Commit: `1b0364fa6dc8c3170a71c9cf618dee8d07a28b79`
- Direct parent: `19c3e17045ef9b17d1aa59e02450c7d557a767df`
- Tree: `37c109477aa4a7e1d8a155dec994ec5d792c6baf`
- Subject: `G61-01: characterize existing central LLM services`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G61-01 Existing Central LLM Services Discovery and Constitutional
  Integration Audit Report V1
- G6-02 External Provider Platform Canonicalization V1
- G6-03 External Provider Platform Public API and Index V1
- G6-12 Generation 6 Architectural Consolidation and Closure Audit V1
- AiGOL Canonical Provider Contract V1
- LLM Role and Boundary Model V1
- G58-01 Conversation Interpreter Architecture Report V1
- G59-04 Conversation Interpreter Proposal and Deterministic Validation Runtime
  Implementation Report V1
- G59-05 Conversation Layer V2 Proposal Commit Runtime Implementation Report V1
- G59-06 Conversation Layer V2 Objective Readiness Runtime Implementation
  Report V1
- G59-07 Conversation Layer V2 Objective Commitment Runtime Implementation
  Report V1
- PCBV31 Baseline Identity Record V1

Objective:

Define the authoritative, minimum-change implementation plan for reusing EPP —
the authenticated Central LLM Services architecture — as the external model
boundary for Conversation Interpreter assistance. No implementation, provider
call, registry mutation, or execution integration is authorized by this report.

Implementation scope:

- Identified the exact existing modules and public APIs to reuse unchanged.
- Fixed the authoritative registry, selection, credential, provider adapter,
  semantic validation, commit, readiness, and Objective ownership boundaries.
- Defined one thin provider-neutral Conversation Interpreter/EPP adapter and
  one versioned selection/binding profile as the only required runtime-facing
  additions.
- Defined content-locality, Replay, failure, timeout, substitution,
  Authorization, Worker, and Objective Commitment rules.
- Defined a no-data-migration, opt-in rollout and rollback strategy.
- Defined the implementation sequence and certification checkpoints required
  before any live external model may participate.

Modified modules:

- `docs/governance/G61_02_CENTRAL_LLM_SERVICES_REUSE_AND_INTEGRATION_PLAN_V1.md`:
  this planning-only G48 report.

Intentionally unchanged modules:

- All runtime source, including EPP, Platform Core, Conversation Layer V2,
  provider infrastructure, Objective Commitment, Replay, Authorization, and
  Worker.
- All provider/resource registries, model/role metadata, provider adapters,
  credentials, manifests, tests, CLI entry points, and PCBV31.
- Git history and external provider state.

Architectural boundaries preserved:

- The plan introduces no replacement Central LLM Services subsystem.
- EPP remains the sole external provider integration architecture.
- The Conversation Layer remains the sole owner of interpreter request
  construction, deterministic proposal validation, Semantic CWM mutation,
  state transitions, readiness, and commitment eligibility.
- Providers and models remain non-authoritative. Selection remains distinct
  from provider invocation policy, Authorization, Worker dispatch, and
  execution.
- No human turn, raw provider output, interpreter proposal, confidence,
  comparison, or validation disposition is planned for Replay persistence.

## Plan Determination

The certified reuse direction is:

```text
Conversation Layer V2
  -> thin Conversation Interpreter/EPP assistance adapter
  -> existing EPP selection, identity, credential, adapter, and timeout owners
  -> external model as an untrusted proposal source
  -> existing G59-04 deterministic proposal validator
  -> existing G59-05 atomic commit owner
```

Only two bounded additions are planned:

1. `CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1`, a versioned
   profile that binds an enabled G58 interpreter identity/version to one
   existing EPP provider resource, provider identity, model/configuration, and
   proposal-only capability.
2. `conversation_interpreter_epp_assistance_runtime_v1.py`, a thin adapter that
   prepares bounded requests, invokes an already-configured EPP adapter,
   converts structured output into the existing G59-04 proposal schema, and
   calls the existing deterministic validator.

No new provider registry, model registry, credential owner, model router,
provider facade, transport, Replay writer, Authorization mechanism, Worker
binding, Objective type, or Platform Core integration is planned.

# 2. Code Evidence

## Planning Evidence

G61-01 authenticated EPP as the canonical Central LLM Services architecture
and returned finding B: the existing system is mostly sufficient but requires
a bounded, versioned extension. Its exact findings govern this plan:

- EPP is a canonical index over existing registry, selection, credential,
  adapter, transport, cognition, and evidence owners.
- the current architecture contains no general model registry;
- provider/resource selection is deterministic and non-authorizing;
- G58-01 requires a distinct interpreter identity and proposal-only boundary;
- G59-04 accepts external-language-model proposals but intentionally performs
  no provider invocation or persistence;
- current provider/cognition Replay schemas cannot be reused unchanged because
  G58-01 makes conversation turns and interpreter proposal material local; and
- a direct OpenAI/Claude/native runtime is not an acceptable Conversation
  Interpreter integration edge.

The implementation plan therefore extends only the missing edge. It does not
reopen the G6 EPP architecture or consolidate historical dialects.

## Reuse Matrix

| Existing surface | Reuse disposition | Reused API or contract | Change permitted by plan |
|---|---|---|---|
| EPP canonical architecture | Reuse unchanged | G6-02 and G6-03 ownership/public index | None |
| Provider metadata registry | Reuse unchanged | `ProviderRegistry.lookup_provider`, `provider_metadata` | None |
| ERR | Reuse unchanged for provider identity/capability evidence where needed | `get_resource_by_id`, `find_resources_by_capability` | None |
| Unified Resource Selection algorithm | Reuse unchanged | `select_unified_resource`, `reconstruct_unified_resource_selection_replay` | Add a separate V1 interpreter selection/binding profile; do not alter selection semantics |
| Provider necessity policy | Reuse unchanged | `PROVIDER_REQUIRED`, `PROVIDER_OPTIONAL`, `PROVIDER_PROHIBITED` and current policy API | None |
| Provider credential vault | Reuse unchanged | `resolve_provider_credential_reference`, `retrieve_provider_credential`, diagnostics | None |
| Provider Governance | Reuse unchanged | lifecycle/status/metric/participation queries and evidence | No new authority; optional content-free operational metric only after separate certification |
| Provider adapter protocol | Reuse unchanged | `ProviderAdapter.generate_proposal` contract | None |
| OpenAI proposal adapter | Reuse unchanged as first eligible concrete adapter | `OpenAIProviderAdapter`, `openai_provider_metadata` | None |
| Other provider adapters | Reuse only after independent EPP certification for the exact role | Existing adapter contracts | No implied readiness from registry presence |
| Current certified provider attachment | Do not call from the interpreter adapter V1 | `run_certified_provider_attachment` remains unchanged for current consumers | None; excluded because it persists proposal/raw response evidence |
| Single-provider OpenAI cognition runtime | Do not reuse as the integration entry point | Current APIs remain available to current consumers | None; excluded because it is OpenAI-specific and Replay-coupled |
| Multi-provider cognition runtime | Do not reuse in V1 | Current transport-registry and comparison APIs remain available elsewhere | None; V1 interpreter selection is single explicit provider, with no substitution |
| Live provider HTTP transport | Reuse only through the selected existing provider adapter/composition | Existing bounded transport/timeout behavior | None |
| G59-04 proposal runtime | Reuse unchanged and mandatory | `create_conversation_interpreter_proposal_v2`, `validate_conversation_interpreter_proposal_v2`, assessment/comparison APIs | None |
| G59-05 Proposal Commit Runtime | Reuse unchanged; invoked by its existing Conversation Layer owner after validation | Existing atomic commit API | None |
| G59-03 State Machine and G59-06 Readiness | Reuse unchanged | Existing transition/readiness APIs | None |
| G59-07 Objective Commitment | Reuse unchanged and remains downstream | Existing commitment API | None |
| Authorization and Worker | No interpreter-path invocation | Existing certified owners | None |
| Replay | Reuse unchanged for content-free EPP selection evidence only | Unified selection reconstructor | No new interpreter-content Replay schema in V1 |

## Authoritative Registries

The following existing registries retain their present authority and scope:

| Registry | Authority retained | Explicit non-authority |
|---|---|---|
| `aigol/provider/provider_registry.py` | Provider metadata identity and availability lookup | Model routing, semantic validation, dispatch, execution, Authorization |
| `aigol/runtime/external_resource_registry_runtime.py` | Passive resource type and capability metadata | Provider invocation, ranking authority, Authorization |
| `aigol/runtime/unified_resource_selection_runtime.py` registry | Resource category, role binding, capability, domain, trust, lifecycle, priority, authority profile | Credential ownership, dispatch, Worker authorization, semantic meaning |
| `aigol/runtime/provider_governance_runtime.py` provider registry | Provider alias, lifecycle, credential reference, metrics and participation evidence | Model-level selection, semantic authority, execution authority |
| G59-04 caller-supplied interpreter registry | Exact interpreter identity/class/version enablement | Provider identity, model identity, credential, Semantic CWM mutation |

The new selection/binding profile is not a replacement registry. It is a
versioned cross-reference joining one existing G58 interpreter registry entry
to one existing EPP resource/provider/model configuration. It must not copy
provider lifecycle state or credential material.

No general model registry will be added in this generation. The selected model
is immutable configuration within the role-specific binding profile. If three
or more independently governed consumers later require model-level lifecycle
and routing, a separate reuse audit must precede any model-registry proposal.

## Module Inventory

### Modules reused unchanged

| Module | Planned use |
|---|---|
| `aigol/provider/provider_adapter.py` | Provider-neutral proposal adapter interface. |
| `aigol/provider/provider_registry.py` | Exact provider metadata and availability validation. |
| `aigol/provider/provider_proposal_envelope.py` | Validate the bounded response envelope returned by an existing adapter. |
| `aigol/provider/providers/openai_provider.py` | First concrete proposal-only provider adapter; no tools, streaming, function calling, memory, or retries. |
| `aigol/runtime/external_resource_registry_runtime.py` | Optional consistency check between provider identity and passive EPP metadata. |
| `aigol/runtime/unified_resource_selection_runtime.py` | Existing deterministic selection algorithm and content-free selection Replay. |
| `aigol/runtime/provider_necessity_policy_runtime.py` | Required/optional/prohibited decision vocabulary. |
| `aigol/runtime/provider_credential_vault.py` | Existing credential reference and retrieval boundary. |
| `aigol/runtime/provider_governance_runtime.py` | Existing lifecycle and availability evidence. |
| `aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py` | Sole external proposal schema, deterministic validator, assessor, and comparator. |
| `aigol/runtime/platform_core_conversation_proposal_commit_runtime_v2.py` | Sole atomic application of already validated candidate operations. |
| `aigol/runtime/platform_core_conversation_state_machine_runtime_v2.py` | Conversation transition and clarification owner. |
| `aigol/runtime/platform_core_conversation_objective_readiness_runtime_v2.py` | Objective readiness owner. |
| `aigol/runtime/platform_core_objective_commitment_runtime_v2.py` | Objective Commitment owner after readiness and confirmation. |
| `aigol/runtime/transport/serialization.py` | Canonical in-memory hashing/serialization utilities only; no interpreter Replay writes. |

### Existing modules explicitly not reused by the new path

| Module/family | Reason for exclusion |
|---|---|
| `aigol/runtime/llm_cognition_provider_runtime.py` | Concrete OpenAI selection and Replay-coupled raw response are incompatible with the provider-neutral, local G58 boundary. |
| `aigol/runtime/native_provider_execution_runtime.py` | Execution-capable direct-provider path; wrong authority and role. |
| `aigol/runtime/multi_provider_cognition_runtime.py` | Writes provider request/result bundles to Replay and adds comparison semantics outside minimal V1. |
| `aigol/provider/certified_provider_attachment.py` and `provider_runtime.py` orchestration | Persist proposal and returned-provider artifacts; current consumers remain unchanged, but G58 proposal content must stay local. |
| `aigol/runtime/provider_assisted_intent_classification.py` | Owns legacy intent classification/Replay behavior, not typed Semantic CWM proposals. |
| `aigol/runtime/provider_assisted_conversation_runtime.py` | Produces explanatory conversation response artifacts, not G59-04 semantic operations. |
| External Worker adapters and Codex execution connectors | Worker/execution role, unavailable to Conversation Interpreter assistance. |
| Legacy and native OpenAI paths | Historical or direct-provider selection bypass; no new dependency permitted. |

## Adapter Inventory

### New adapter required

Planned module:

```text
aigol/runtime/conversation_interpreter_epp_assistance_runtime_v1.py
```

Planned owner:

```text
Conversation Layer request/response edge
with EPP owning provider identity, selection, credential and concrete invocation
```

The module is a thin integration adapter, not a Central LLM Service, model
router, Conversation Layer semantic owner, or execution owner.

Planned public surface:

```python
def create_conversation_interpreter_epp_request_v1(
    *,
    interpreter_request: dict[str, Any],
    interpreter_epp_binding: dict[str, Any],
    selection_capture: dict[str, Any],
) -> dict[str, Any]:
    """Create a bounded, immutable provider request without state handles."""


def adapt_epp_response_to_interpreter_proposal_v1(
    *,
    epp_response: dict[str, Any],
    interpreter_request: dict[str, Any],
    interpreter_epp_binding: dict[str, Any],
) -> dict[str, Any]:
    """Create a G59-04 proposal; never accept its semantic meaning."""


def run_conversation_interpreter_epp_assistance_v1(
    *,
    interpreter_request: dict[str, Any],
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    interpreter_registry: list[dict[str, Any]],
    interpreter_epp_binding: dict[str, Any],
    provider_registry: ProviderRegistry,
    provider_adapter: ProviderAdapter,
    selection_replay_dir: str | Path,
) -> dict[str, Any]:
    """Select, invoke, adapt, and validate one proposal without mutation."""
```

These signatures are planning contracts, not implemented code.

### Adapter responsibilities

The new adapter must:

- validate the G58 interpreter request capsule and enabled interpreter identity;
- validate the immutable interpreter-to-EPP binding profile;
- invoke `select_unified_resource` with the exact provider role, capability,
  domain, trust, and necessity constraints;
- verify selected EPP resource, provider metadata, adapter `provider_id`, model
  configuration, and interpreter binding are identical;
- create one bounded non-streaming, no-tools, no-function-calling, no-memory,
  no-retry provider request;
- receive one complete bounded provider proposal envelope;
- reject malformed, partial, over-limit, authority-bearing, stale, or
  identity-mismatched output;
- deterministically map only the closed structured operation vocabulary into
  `create_conversation_interpreter_proposal_v2`;
- call `validate_conversation_interpreter_proposal_v2` before returning;
- return only a G59-04 assessment/candidate set or a stable fail-closed local
  disposition; and
- expose no Semantic CWM mutator, Objective service, Platform Core service,
  Replay writer, Authorization client, Worker dispatcher, shell, filesystem,
  network client, or credential value to the interpreter.

The new adapter must not:

- select a provider by concrete code branch;
- infer semantic acceptance from provider confidence or EPP selection;
- write raw request/response/proposal content to Replay;
- call G59-05 directly unless the existing Conversation Layer orchestrator
  already owns that exact post-validation call;
- create or commit an Objective;
- request Authorization or dispatch a Worker;
- retry, fall back, or substitute another provider silently; or
- mutate any registry or lifecycle state.

### No other adapter required

No new OpenAI, Claude, Gemini, Mistral, Codex, local-model, Worker, Replay,
Authorization, or Objective adapter is required. Provider-family additions
remain separate EPP certification work and are not prerequisites for the first
interpreter integration.

## Selection and Binding Profile

Planned artifact identity:

```text
CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1
```

Required fields:

```text
profile_version
interpreter_identity
interpreter_version
interpreter_class = EXTERNAL_LANGUAGE_MODEL
proposal_schema_version
epp_resource_id
provider_id
provider_role = PROVIDER_ROLE
provider_capability = LANGUAGE_UNDERSTANDING_PROPOSAL
authority_profile = PROVIDER_PROPOSAL_ONLY
model_id
model_configuration_version
credential_reference_id
domain_scope = CONVERSATION_LAYER
minimum_trust_level
timeout_seconds
maximum_input_bytes
maximum_output_bytes
external_data_processing = true
streaming = false
tools = false
function_calling = false
automatic_retries = false
substitution = false
semantic_authority = false
objective_authority = false
execution_authority = false
worker_authority = false
profile_digest
```

The profile references but does not duplicate provider status, credentials, or
adapter implementation. A profile is enabled only when its interpreter entry,
EPP provider metadata, unified resource role binding, model configuration, and
credential reference all match.

The existing unified selection algorithm remains unchanged. A future versioned
registry update may add `LANGUAGE_UNDERSTANDING_PROPOSAL` to explicitly eligible
provider resources. It must preserve the old registry builder/version for
existing callers and must not change existing priorities or role bindings.

## Ownership Matrix

| Responsibility | Owner | Adapter permission | Forbidden transfer |
|---|---|---|---|
| Human turn/session metadata | Conversation Envelope | Read bounded immutable capsule | EPP persistence or mutation |
| Interpreter identity/version enablement | Conversation Layer interpreter registry | Validate exact entry | Provider self-registration |
| Provider identity/lifecycle | EPP Provider Registry/Governance | Lookup only | Conversation Layer ownership |
| Provider capability/resource selection | Unified Resource Selection | Request and validate selection | Treat selection as authorization |
| Model/configuration binding | Versioned interpreter/EPP binding profile | Validate exact immutable binding | Dynamic provider-selected model |
| Credential storage/retrieval | Provider credential vault | Receive only through provider composition; never expose to proposal data | Interpreter or Conversation CWM access |
| Concrete provider request | Existing provider adapter | Invoke once within bounds | Adapter-owned routing/retry/substitution |
| Raw provider response | Ephemeral adapter scope | Validate and transform | Replay, CWM, Objective, Worker payload persistence |
| Semantic proposal schema/validation | G59-04 | Call existing constructor/validator | EPP semantic acceptance |
| Semantic mutation | G59-05 through existing Conversation Layer orchestration | None before validated candidate set | Provider/interpreter mutation |
| Conversation state/readiness | G59-03/G59-06 | Consume resulting Conversation Layer state only | Provider confidence transition |
| Objective Commitment | G59-07 | None | Model-created Objective or commitment |
| Replay | Replay owner | Existing selection evidence only | Interpreter content/proposal persistence |
| Authorization | Authorization owner | None | Provider selection or model output as authorization |
| Worker execution | Worker Platform | None | Interpreter role reuse as Worker |
| Platform Core | Existing admission/pipeline owners | None before committed Objective | Pre-commit pipeline entry |
| PCBV31 | Existing identity record | None | Membership/socket/authority change |

## Replay, Evidence, Authorization, and Failure Impact

### Replay impact

V1 creates no new Replay writer and no new interpreter-content Replay schema.

Permitted existing Replay evidence:

- unified EPP selection identity, resource, role, capability, trust, priority,
  registry hash, selection result, and failure reason;
- all flags proving no provider/Worker invocation, dispatch, execution request,
  or authorization was created by selection.

Forbidden Replay content:

- human turn text or semantic capsule;
- raw or normalized provider response;
- proposed semantic operations;
- interpreter confidence, alternatives, comparison, or validation disposition;
- Conversation CWM values; and
- credential values or secret material.

Provider invocation success/failure remains local to the Conversation session
in V1. A later content-free operational-metric profile requires separate Replay
and privacy certification; it is not part of the minimum implementation.

### Authorization and Worker impact

- No Authorization API is imported or called.
- `select_unified_resource` is called with `PROVIDER_ROLE`, never
  `WORKER_ROLE`.
- `worker_authorization_required` remains false for the provider role.
- The adapter rejects any selected hybrid resource unless the selected binding
  is exactly its provider role; a Worker binding is never inherited.
- No Worker request, dispatch, execution, completion, or Replay chain is
  created.
- Objective Commitment remains the earliest constitutional gateway to the
  certified execution pipeline.

### Timeout, failure, and substitution

- One configured bounded timeout applies per invocation.
- Streaming, tools, function calling, automatic retry, and memory are disabled.
- Unknown/missing provider, inactive lifecycle, missing credential, selection
  ambiguity, timeout, transport error, malformed response, authority-bearing
  output, stale revision, invalid source span, conflict, and schema mismatch
  all fail closed with no Semantic CWM mutation.
- Provider failure returns control to the Conversation State Machine for
  deterministic clarification, suspension, or deterministic-parser fallback.
- No provider or model substitution is automatic. A different provider requires
  a separately enabled binding and a new explicit selection/invocation.
- Repeated identical requests remain independently revision-bound; cached model
  output is not reused unless a future separately certified local cache exists.

## Migration Strategy

No persisted Conversation CWM, provider registry, credential vault, Replay,
Objective, Authorization, or Worker data migration is required.

The rollout is additive and opt-in:

1. Existing deterministic/rule-based interpreters remain the default.
2. Add and certify the V1 selection/binding profile with all external bindings
   disabled.
3. Add the thin adapter behind an explicit Conversation Layer feature/config
   gate; no HIR or AiCLI default route changes.
4. Exercise only injected deterministic provider adapters in tests.
5. Enable one exact external interpreter identity/provider/model binding for a
   bounded certification session.
6. Preserve deterministic parser precedence where it resolves the turn; the
   external interpreter is requested only under the certified necessity policy.
7. Expand to another provider only through a new immutable binding version and
   provider-family certification.

Rollback is configuration-only:

- disable the exact interpreter binding;
- stop new provider-assisted invocations;
- retain existing Conversation CWM unchanged;
- continue with deterministic parser, clarification, suspension, or abandonment;
- do not rewrite prior Replay, provider lifecycle, or Conversation state.

Profile versions are immutable. Model, provider, timeout, limits, or privacy
changes create a new profile version; they never mutate an active profile in
place.

## Implementation Sequence

| Phase | Authorized future change | Existing owners reused | Exit criterion |
|---|---|---|---|
| 0. Contract certification | Governance-only selection/binding, request/response, privacy, and failure schemas | G58-01, G59-04, EPP contracts | Exact schemas and prohibited fields certified; no runtime change |
| 1. Selection profile | Add V1 interpreter/EPP binding and versioned capability eligibility while preserving existing selection algorithm and V1 callers | Unified selection, provider registry, provider necessity policy | Deterministic selection and equal-priority fail-closed tests pass |
| 2. Pure adapter functions | Add request builder, response validator/mapper, binding validator | Existing provider/proposal schemas, G59-04 | Pure tests prove deterministic mapping and zero mutation/import drift |
| 3. Bounded orchestration | Add one-run orchestration using an injected existing `ProviderAdapter` | Provider registry, adapter interface, credential composition, unified selection | Success/failure tests prove one invocation, timeout, no retry/substitution, content locality |
| 4. Conversation integration | Existing Conversation Layer orchestrator calls adapter, then existing G59-05 only after G59-04 admissibility | G59-03/04/05/06 | Candidate mutation occurs only through G59-05; state/readiness remain deterministic |
| 5. Isolation certification | Prove no Objective, Platform Core, Replay content, Authorization, Worker, tool, shell, filesystem, or network authority reaches interpreter data | Existing constitutional owners | Import graph, negative paths, and end-to-end injected tests pass |
| 6. One live-provider certification | Separately authorized, bounded session for one immutable provider/model binding | Existing EPP adapter/credential owner | Human-approved certification evidence; no execution pipeline entry |

Phases 0 through 5 must complete before Phase 6. Phase 6 requires separate
authorization because this planning generation does not authorize provider or
network execution.

## Certification Checkpoints

| Checkpoint | Mandatory evidence | Blocking condition |
|---|---|---|
| CP-1 Contract closure | Closed fields, versions, byte/count limits, authority flags, privacy rules | Open-ended output, tool field, missing limits, or mutable version |
| CP-2 Registry continuity | Existing provider/resource identities and priorities unchanged; versioned interpreter capability/profile only | Duplicate provider registry, implicit model registration, existing caller breakage |
| CP-3 Selection separation | Selection Replay proves no invoke/dispatch/authorization/Worker effect | Selection treated as permission to execute |
| CP-4 Role separation | Exact provider role selected; hybrid Worker role inaccessible | Worker/coding identity inherited by interpreter |
| CP-5 Credential isolation | No credential in request, response, proposal, CWM, logs, or Replay | Secret or credential reference exposed to interpreter output |
| CP-6 Response locality | Raw response and proposal never written to Replay or persisted outside local bounded state | Any content-bearing Replay artifact |
| CP-7 G59-04 validation | Every output passes exact source, revision, taxonomy, conflict, integrity, and authority validation | Direct semantic operation or confidence-based acceptance |
| CP-8 Atomic commit boundary | Only G59-05 applies validated candidates | Adapter/CWM direct mutation |
| CP-9 Pipeline isolation | No Objective, Platform Core, Authorization, Worker, completion, or execution import/call before commitment | Any pre-commit reachability |
| CP-10 Failure determinism | Timeout/unavailable/malformed/stale/conflict repeated tests return stable refusal with no mutation | Retry, substitution, partial commit, or non-deterministic disposition |
| CP-11 Compatibility | G59, Conversation Layer, provider, selection, governance conformance, compile, and diff checks pass | Existing regression or hidden boundary drift |
| CP-12 Live certification | Separately authorized one-provider transcript and evidence | Network/provider use without explicit later authorization |

## Constitutional Impact Assessment

| Constitutional surface | Planned impact | Assessment |
|---|---|---|
| EPP | One role-specific consumer adapter and versioned selection profile | Additive; no authority or provider redesign |
| Conversation Layer V2 | Optional provider-assisted proposal source | Existing deterministic validator/commit/state owners unchanged |
| Platform Core | None before Objective Commitment | Preserved |
| Semantic CWM | No direct adapter access; G59-05 remains sole commit path | Preserved |
| Objective Commitment | No model/provider role; remains downstream | Preserved |
| Replay | Existing content-free selection evidence only | Preserved with stricter locality profile |
| Authorization | No call or schema change | Preserved |
| Worker lifecycle | No call or role inheritance | Preserved |
| Provider infrastructure | Existing identities, credentials, adapters, and transports reused | Preserved |
| PCBV31 | No membership, socket, identity, or authority change | Preserved |
| Migration compatibility | No persisted-state migration; disabled-by-default rollout | Low and reversible |

The principal constitutional risk is accidental collapse of four distinct
facts:

```text
provider selected
!= provider invocation admitted
!= semantic proposal accepted
!= Objective/execution authorized
```

Every planned contract and checkpoint preserves those inequalities.

# 3. Constitutional Self-Assessment

## Verified

- G61-01 is present at the authenticated G61-02 baseline and identifies EPP as
  the existing Central LLM Services architecture.
- The plan maximizes reuse: existing provider/resource registries, selection
  algorithm, necessity policy, credential vault, provider governance, adapter
  protocol, first OpenAI proposal adapter, G59-04 validator, G59-05 commit,
  state machine, readiness, and commitment owners remain unchanged.
- The only planned runtime module is a thin provider-neutral interpreter/EPP
  adapter; the only planned selection change is a versioned role/capability and
  immutable binding profile.
- No general model registry, provider facade, router, transport, Replay writer,
  Authorization path, Worker path, Objective type, or replacement subsystem is
  planned.
- Existing provider-attachment and cognition orchestrators are deliberately not
  reused where their raw-response Replay semantics conflict with G58-01.
- Replay, Authorization, Worker, Objective Commitment, failure, timeout,
  substitution, migration, rollout, and rollback rules are explicit.
- Each future phase has a bounded exit criterion and each constitutional
  boundary has a blocking certification checkpoint.
- No runtime, registry, provider, test, Replay, Authorization, Worker, Platform
  Core, Conversation Layer, or PCBV31 file was modified by this planning
  generation.

## Not Verified

- The planned selection/binding profile and adapter do not yet exist; their API
  signatures in this report are planning contracts, not runtime evidence.
- No provider adapter was invoked and no network, credential, timeout, or live
  provider behavior was exercised.
- No Conversation Layer integration, proposal commit, state transition,
  readiness evaluation, or Objective Commitment was run for the planned path.
- Claude, Gemini, Mistral, Codex cognition, local-model, and multi-provider
  interpreter bindings remain outside the first implementation and require
  separate exact-role certification.
- A content-free operational provider-invocation metric is intentionally
  deferred; V1 records only existing selection evidence and local failure state.
- Implementation checkpoint results cannot be certified until a later
  implementation generation is expressly authorized.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Reuse authenticated Central LLM Services | G61-01, G6-02, G6-03, G6-12 | Baseline and architecture cross-reference review | PASS |
| Identify unchanged runtime modules | Code Evidence module inventory and exact repository paths | Current API/ownership comparison | PASS |
| Identify authoritative registries | Authoritative Registries matrix | Registry responsibility and non-authority review | PASS |
| Identify unchanged provider adapters | Reuse Matrix and Adapter Inventory | Current adapter contract review | PASS |
| Identify reused APIs | Reuse Matrix and planned public surface | API dependency review | PASS |
| Minimize new implementation | One planned runtime adapter and one versioned selection/binding profile | Alternative comparison against new facade/router/model registry | PASS |
| Distinguish additive and versioned changes | Plan Determination, Selection and Binding Profile, Implementation Sequence | Change classification review | PASS |
| Preserve ownership boundaries | Ownership Matrix and constitutional impact assessment | Owner-by-owner review | PASS |
| Define Replay and Authorization impact | Replay, Evidence, Authorization, and Failure Impact | Content-locality and no-Authorization review | PASS |
| Define migration strategy | Migration Strategy | Persisted-state, rollout, and rollback analysis | PASS |
| Define implementation sequence | Six-phase sequence | Dependency and exit-criterion review | PASS |
| Define certification checkpoints | CP-1 through CP-12 | Requirement-to-blocker review | PASS |
| Governance reporting conformance | G48 report structure and repository governance rules | `python -m pytest tests/test_governance_conformance.py`: 5 passed | PASS |
| Runtime implementation | Planning-only restriction | Not authorized | NOT_APPLICABLE |
| Live provider/network validation | Planning-only and no-network restriction | Not authorized | NOT_APPLICABLE |
| G48 exact structure | This report | Six top-level section review | PASS |
| Repository mutation boundary | Git status and report diff | Required report only | PASS |
| Markdown/worktree hygiene | New report | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G61_02_CENTRAL_LLM_SERVICES_REUSE_AND_INTEGRATION_PLAN_V1.md`:
  added this planning-only report.

Unchanged subsystems:

- EPP runtime, provider registries, resource selection, provider necessity,
  provider governance, credential vault, provider adapters, connectors,
  transports, model configuration, and CLI.
- Conversation Layer V2, Semantic CWM, proposal validation, proposal commit,
  state machine, readiness, and Objective Commitment.
- Platform Core, Replay, Authorization, Worker, Development Governance,
  capability selection, HIR, AiCLI, tests, PCBV31, and Git history.

API compatibility:

- No API or schema changed. Planned signatures and artifacts are future
  contracts only.
- Existing callers and provider consumers remain unaffected by the opt-in,
  versioned plan.

Boundary preservation:

- EPP remains the provider owner; Conversation Layer remains the semantic
  owner; Replay, Authorization, Worker, Objective Commitment, and Platform Core
  remain independent constitutional owners.
- The plan prohibits direct provider selection, direct Semantic CWM mutation,
  content-bearing Replay, implicit substitution, and pre-commit pipeline entry.

Unrelated pre-existing changes:

- None observed at planning start.

# 6. Certification Verdict

CENTRAL_LLM_SERVICES_REUSE_PLAN_CERTIFIED
