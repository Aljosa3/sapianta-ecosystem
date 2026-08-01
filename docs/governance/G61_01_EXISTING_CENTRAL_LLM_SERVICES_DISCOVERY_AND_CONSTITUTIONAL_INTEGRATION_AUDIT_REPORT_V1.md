# 1. Implementation Summary

Generation: G61-01

Report identity:
G61_01_EXISTING_CENTRAL_LLM_SERVICES_DISCOVERY_AND_CONSTITUTIONAL_INTEGRATION_AUDIT_REPORT_V1

Reporting date: 2026-08-01

Constitutional baseline: REAL_WORLD_CONVERSATION_EXECUTION_CERTIFIED

Authenticated repository anchor:

- Commit: `19c3e17045ef9b17d1aa59e02450c7d557a767df`
- Direct parent: `4e12b88371a5375bf39ceb089a0a5b975c7490c0`
- Tree: `8331ce8ce1c10a482dea16005dfee9b43f24e5ca`
- Subject: `G60-03: certify real-world conversation execution`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G6-01 Existing External Provider Platform Reuse Audit V1
- G6-02 External Provider Platform Canonicalization V1
- G6-03 External Provider Platform Public API and Index V1
- G6-12 Generation 6 Architectural Consolidation and Closure Audit V1
- AiGOL Canonical Provider Contract V1
- LLM Role and Boundary Model V1
- G58-01 Conversation Interpreter Architecture Report V1
- G59-04 Conversation Interpreter Proposal and Deterministic Validation Runtime
  Implementation Report V1
- PCBV31 Baseline Identity Record V1

Objective:

Locate and constitutionally characterize the existing central LLM, model, and
provider architecture without designing a replacement. Determine its canonical
identity, concrete implementation surfaces, consumers, provider and role
coverage, selection and authority boundaries, direct-provider exceptions, and
the smallest safe integration path for Conversation Interpreter assistance.

Implementation scope:

- Performed a read-only semantic and identifier search across runtime, provider,
  Worker, capability, CLI, tests, specifications, governance, GitHub governance,
  registry, manifest, and authenticated Git-history surfaces.
- Traced current imports, callers, registry entries, provider identities, model
  fields, role bindings, credential references, public APIs, transport edges,
  failure paths, replay reconstructors, and certification records.
- Reconstructed the existing architecture and classified each material
  discovered component under exactly one required G61-01 classification.
- Compared the located system to Conversation Layer V2, G58-01, G59-04,
  G59-05, Objective Commitment, Replay, Authorization, Worker, and PCBV31.
- Identified bounded versioned extension work. No replacement architecture is
  justified.

Modified modules:

- `docs/governance/G61_01_EXISTING_CENTRAL_LLM_SERVICES_DISCOVERY_AND_CONSTITUTIONAL_INTEGRATION_AUDIT_REPORT_V1.md`:
  this read-only discovery and constitutional integration audit.

Intentionally unchanged modules:

- All runtime source, including EPP, Platform Core, Conversation Layer V2,
  Objective Commitment, Replay, Authorization, Worker, and provider runtimes.
- All tests, registries, manifests, provider adapters, credentials, CLI entry
  points, governance source artifacts, and PCBV31.
- Git history and external provider state.

Architectural boundaries preserved:

- No external provider or network endpoint was called.
- No registry, credential, provider, model, role, selection, runtime, Replay,
  Authorization, Worker, Conversation Layer, Platform Core, or PCBV31 state was
  changed.
- Provider selection is characterized as non-authorizing evidence; it is not
  reinterpreted as execution authorization.
- External models remain non-authoritative proposal sources. Only deterministic
  Conversation Layer owners may validate and commit semantic operations.

## Executive Determination

The existing central system is called **EPP — External Provider Platform**.
EPP is not one monolithic service or one runtime facade. It is the canonical,
governed architectural index over several existing Provider Services surfaces:

```text
EPP
  = provider and resource identity/registry surfaces
  + governed resource-selection policy
  + role and capability bindings
  + credential and provider lifecycle boundaries
  + provider adapters/connectors/transports
  + cognition and provider-proposal runtimes
  + evidence and Replay reconstruction
```

Several historically evolved registries and provider-contract dialects remain
in the repository, but G6-02 and G6-03 already canonicalize them under EPP and
publish their owning APIs. They are overlapping implementation surfaces, not
independent constitutional authorities. G6-12 explicitly closes the
architecture and rejects creating another provider subsystem.

The Gap Analysis finding is **B**: the existing central system is mostly
sufficient but requires a bounded, versioned Conversation Interpreter
extension. The required work is not a provider platform replacement or broad
consolidation.

# 2. Code Evidence

## Discovery Method

The audit used four evidence passes.

1. **Semantic inventory:** searched all required repository areas for LLM,
   provider, model, selection, role, worker, helper, local-model, Codex, OpenAI,
   Anthropic/Claude, Gemini, Mistral, and concrete network-call vocabulary.
2. **Runtime tracing:** inspected definitions and call sites for provider
   registries, ERR, unified selection, provider attachment, cognition,
   credential, governance, transport, Worker adapters, Conversation Layer V2,
   and CLI entry points.
3. **Governance authentication:** compared runtime findings with G6-01,
   G6-02, G6-03, G6-12, the canonical provider contract, LLM role model,
   G11 Codex role separation, G58-01, and G59-04.
4. **History and integrity:** traced introducing commits for the EPP
   canonicalization and principal registry/runtime files and calculated current
   SHA-256 digests for the primary evidence set.

Repository naming differences were handled explicitly: the prompt's
`aigol/providers/` corresponds in the authenticated tree to `aigol/provider/`
and `aigol/runtime/providers/`, with an additional historical provider
abstraction in `sapianta_bridge/providers/`.

No network operation, provider invocation, credential read, or mutation command
was used.

### Authenticated evidence anchors

| Evidence | Authenticated identity |
|---|---|
| G6-01 EPP reuse audit | Commit `7497c3143eaf7abb632e324d908ad9b4a2f1633d`; SHA-256 `9bb86829c1fd05a92db24166d179bebb62322c7f2ca044031d59c55f1841491b` |
| G6-02 EPP canonicalization | Commit `e450f556a64c0cd540e374792ca2055938edd442`; SHA-256 `09d4cc71ec19d96f0560e2150f1be7d2cf7b3aaa9f6521a488abe1ea4a9608c8` |
| G6-03 EPP public API/index | Commit `716546ffdebf2685fb8584d5213fdff8168f85de`; SHA-256 `2f74e935164ec756ec051a725fe24fdc99f6ead7a6c884393de9aefa76dbc35b` |
| ERR runtime | Introduced by `405c84991f886006fbdac77eb2f478b8e59bfd37`, real providers added by `3e8d5a1c0c5eba7afd1af7d8f2e482948865e909`; current SHA-256 `a9d7eb50c6c08f32afd236abd6897c3cab03dc45f007d4bcc43938a2a64c34c0` |
| Unified selection runtime | Certified by `efd12b0dd5304f581ff647462c003ee10c123364`; current SHA-256 `fc36fda533e053d6bceffad5d84af0df9ce0eed7caa54e3d805038b172f23473` |
| Provider metadata registry | Provider epoch commits `5261636a6913476420e507e61cfcf42ab945c7dd` and `3061e473e4e93eeca806cd4b5c727ee18b575a9e` |
| Bridge provider abstraction | Introduced by `5e8c19a76f8284eeed9fded9135971e91741226f` |
| G58-01 Interpreter architecture | SHA-256 `61ff5427e7cd8980e49303bf1207f187482f3c003ae80f191aa5d74be1fdf4ce` |
| G59-04 proposal validator | SHA-256 `bab87dee4df9ef4f64ca5b7f9f56a57f79fd71cc913ded6f14bec7922830f5f4` |

## Located Central LLM Architecture

### Canonical name and constitutional position

The canonical subsystem name is:

```text
EPP — External Provider Platform
```

G6-02 defines EPP as the canonical external integration architecture. G6-03
defines its public API as a documented index over existing owning runtimes,
rather than requiring a new facade. G6-12 confirms that EPP owns external
provider integration and that no new authority layer or provider architecture
is required.

EPP is broader than LLMs. LLM cognition is its most developed provider family,
while execution-provider and local-provider contracts remain separately bounded.

### Canonical ownership graph

```text
Human / interface adapter
  -> PGSP governed session protocol
  -> UBTR semantic translation / CSA canonical semantics
  -> OCS orchestration and provider-necessity decision
  -> Governance admissibility checkpoint
  -> EPP identity, capability, role, credential, adapter and transport surfaces
  -> external provider boundary
  -> EPP normalization and evidence
  -> Replay reconstruction owner
  -> UHCL / OCS consumer

Worker execution, when requested, remains a separate Worker Platform path.
```

EPP owns provider integration surfaces. It does not own semantic truth,
Conversation CWM mutation, Objective Commitment, execution authorization,
Worker authority, governance decisions, or Replay authority.

### One subsystem or several systems

There is one canonical architecture and several partially overlapping runtime
dialects:

- `aigol/provider/` provides the current metadata registry, proposal envelope,
  certified provider attachment, and OpenAI proposal adapter.
- ERR provides passive cognition-provider and execution-worker capability
  metadata.
- Unified Resource Selection provides deterministic role/capability/policy
  selection without invocation.
- OCS cognition runtimes provide single- and multi-provider request,
  normalization, comparison, failure isolation, and Replay evidence.
- Provider Governance and the credential vault provide lifecycle, metric,
  participation, credential, and secret-free evidence.
- `sapianta_bridge/providers/`, `provider_connectors/`, and
  `real_provider_transport/` retain the earlier bounded execution-provider,
  Codex connector, and file-transport substrate.
- Several concrete OpenAI/Claude/native runtimes remain as specialization,
  certification, legacy, or direct-call paths.

The overlaps are authenticated and already governed by EPP canonicalization.
They do not justify finding C because consolidation is not a prerequisite for
the bounded interpreter extension.

## Runtime and Registry Inventory

The following table classifies every material architecture component found by
the audit. Each row has exactly one G61-01 classification. Test files and
homogeneous schema/evidence files are grouped only when they implement one
bounded component and share the same classification.

| Component | Exact repository surface | Classification | Current responsibility |
|---|---|---|---|
| EPP canonical architecture and public index | `G6_01...`, `G6_02...`, `G6_03...`, `G6_12...` | `CENTRAL_LLM_SERVICE_CORE` | Canonical provider architecture, ownership, and public discovery surface. |
| Current provider metadata registry | `aigol/provider/provider_registry.py` | `PROVIDER_REGISTRY` | Passive hashed provider metadata; no dispatch, execution, or authority. |
| External Resource Registry | `aigol/runtime/external_resource_registry_runtime.py` | `PROVIDER_REGISTRY` | Passive resource/capability registration and first-match selection evidence. |
| Provider governance registry/lifecycle | `aigol/runtime/provider_governance_runtime.py` | `PROVIDER_REGISTRY` | Provider aliases, credential references, lifecycle, metrics, participation, and queries. |
| Provider capability catalog | `docs/governance/PROVIDER_CAPABILITY_CATALOG_V1.json` | `PROVIDER_REGISTRY` | Governance catalog of provider capability and certification status. |
| Unified resource selection | `aigol/runtime/unified_resource_selection_runtime.py` | `MODEL_SELECTION_POLICY` | Deterministic role, capability, domain, trust, necessity, priority, and authority-profile selection. |
| Provider necessity policy | `aigol/runtime/provider_necessity_policy_runtime.py` | `MODEL_SELECTION_POLICY` | Classifies provider use as required, optional, or prohibited. |
| Role-separated LLM identity certification | `aigol/runtime/role_separated_llm_identity_certification_v1.py` | `MODEL_ROLE_REGISTRY` | Static, replay-visible cognition, translation, and repair role identities. |
| Codex provider/Worker identity split | `aigol/runtime/codex_worker_platform_integration.py` | `MODEL_ROLE_REGISTRY` | Registers independent `codex-cognition` provider and `codex-execution` Worker identities. |
| Canonical cognition-provider schema | `docs/governance/AIGOL_CANONICAL_PROVIDER_CONTRACT_V1.md` | `CONVERSATION_INTERPRETER_COMPATIBLE` | Non-authoritative provider contract/input/output and normalized cognition schema. |
| Provider proposal envelope/attachment | `aigol/provider/provider_proposal_envelope.py`, `provider_runtime.py`, `certified_provider_attachment.py` | `CONVERSATION_INTERPRETER_COMPATIBLE` | Proposal-only request/response envelope, readiness, failure, and Replay reconstruction. |
| Current OpenAI proposal adapter | `aigol/provider/providers/openai_provider.py` | `PROVIDER_ADAPTER` | Single non-streaming, no-tools Responses API adapter returning only a provider proposal envelope. |
| Live OpenAI/Claude executors | `aigol/runtime/live_openai_executor.py`, `live_claude_executor.py` | `PROVIDER_ADAPTER` | Concrete bounded HTTP executors with injected opener/timeout handling. |
| Live provider HTTP transport | `aigol/runtime/live_provider_http_transport.py` | `PROVIDER_ADAPTER` | Governed request/response/error/audit transport with redaction and fail-closed response checks. |
| Bridge provider abstraction/adapters | `sapianta_bridge/providers/` | `PROVIDER_ADAPTER` | Bounded execution-provider contracts and structural Codex, Claude, local, and mock adapters. |
| Connector and transport substrate | `sapianta_bridge/provider_connectors/`, `sapianta_bridge/real_provider_transport/` | `PROVIDER_ADAPTER` | Codex artifact/process connector and bounded file transport; not provider routing. |
| Single-provider cognition runtime | `aigol/runtime/llm_cognition_provider_runtime.py` | `DIRECT_PROVIDER_BYPASS` | OpenAI-specific contract, credential loading, direct HTTP invocation, raw response, and Replay; does not require EPP selection. |
| Native provider execution runtime | `aigol/runtime/native_provider_execution_runtime.py` | `DIRECT_PROVIDER_BYPASS` | CLI-reachable OpenAI-specific native execution path with direct concrete transport. |
| Current provider runtime OpenAI adapter | `aigol/runtime/providers/openai_provider.py` | `HISTORICAL_OR_DEPRECATED` | Earlier direct OpenAI provider implementation; no current runtime import consumers located. |
| Legacy OpenAI provider adapter | `aigol/runtime/openai_provider_adapter.py` | `HISTORICAL_OR_DEPRECATED` | Legacy adapter retained for retirement/pressure tests; replacement is `aigol/provider/providers/openai_provider.py`. |
| Legacy provider attachment | `aigol/runtime/provider_attachment.py` | `HISTORICAL_OR_DEPRECATED` | Explicit `LEGACY_COMPATIBILITY`; production routing and certified reachability are false. |
| Older real OpenAI invocation family | `real_openai_api_invocation.py`, `real_runtime_activation.py`, related experiment/usage runtimes | `HISTORICAL_OR_DEPRECATED` | Earlier direct SDK path retained for tests and historical operator experiments. |
| Multi-provider cognition runtime | `aigol/runtime/multi_provider_cognition_runtime.py` | `CAPABILITY_HELPER_BINDING` | OCS helper cognition across approved contracts with per-provider failure isolation and usage evidence. |
| OCS cognition orchestration | `ocs_llm_cognition_end_to_end_runtime.py`, cognition artifact/comparison/continuity runtimes | `CAPABILITY_HELPER_BINDING` | Context assembly, provider availability, cognition normalization, comparison, clarification, and human-facing output. |
| Provider-assisted intent/conversation | `provider_assisted_intent_classification.py`, `provider_assisted_conversation_runtime.py` | `CAPABILITY_HELPER_BINDING` | Deterministic-first fallback to provider proposal, followed by local validation. |
| ACLI assisted explanation | `acli_llm_assisted_explanation_runtime.py` | `CAPABILITY_HELPER_BINDING` | Optional provider explanation with deterministic fallback and authoritative-state fidelity checks. |
| Provider proposal production bridges | `clarified_intent_provider_proposal_bridge.py`, `provider_proposal_production_runtime.py`, related integrations | `CAPABILITY_HELPER_BINDING` | Bind clarified governed intent to provider proposal production without provider authority. |
| OpenAI external Worker adapter | `openai_external_worker_provider_adapter.py`, `first_external_llm_worker_runtime.py` | `WORKER_PROVIDER_BINDING` | Converts authorized external Worker task packages to bounded OpenAI calls and normalized Worker results. |
| Universal provider/Worker runtime | `universal_provider_worker_runtime.py` | `WORKER_PROVIDER_BINDING` | Preserves separate provider and Worker roles over unified selection. |
| Codex bounded execution connector | `sapianta_bridge/provider_connectors/bounded_execution_runtime.py`, `aigol/runtime/codex_worker_activation_binding_runtime.py` | `WORKER_PROVIDER_BINDING` | Authorized, workspace-bounded `codex exec` Worker execution and completion evidence. |
| Conversation Interpreter proposal runtime | `aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py` | `CONVERSATION_INTERPRETER_COMPATIBLE` | Closed, local, non-authoritative proposal validation/comparison; no provider invocation or persistence. |
| Provider and Conversation test suites | Relevant `tests/test_*provider*`, `test_*cognition*`, `test_g59_04_*`, fixtures and certification runners | `TEST_OR_TOOLING_ONLY` | Deterministic fixtures, injected transports, regression, pressure, and certification support. |

No authenticated general-purpose `MODEL_REGISTRY` component was located. Model
names are adapter/request configuration or evidence metadata. This absence is a
specific finding, not an unresolved search result. No component is therefore
assigned `MODEL_REGISTRY` or `UNRESOLVED` merely to populate those categories.

## Public API Evidence

G6-03 authenticates the public EPP index. The principal current APIs are:

| Area | Public APIs | Constitutional effect |
|---|---|---|
| Provider metadata | `ProviderRegistry.register_provider`, `lookup_provider`, `provider_metadata` | Metadata only. |
| Bridge execution providers | `ProviderRegistry.register`, `get`, `metadata`, `validate` | Passive execution-provider registration only. |
| ERR | `register_resource`, `get_resource_by_id`, `find_resources_by_capability`, `select_resource_for_capability` | Passive lookup and replay-visible first-match evidence; no invocation. |
| Unified selection | `default_resource_registry`, `select_unified_resource`, `reconstruct_unified_resource_selection_replay` | Deterministic policy selection; no dispatch or authorization. |
| Credential boundary | `add_provider_credential`, `verify_provider_credential`, `rotate_provider_credential`, `disable_provider_credential`, `delete_provider_credential`, `retrieve_provider_credential` | Secret lifecycle, approval gates, and secret-free evidence. |
| Provider governance | `execute_provider_lifecycle_operation`, `record_provider_usage_metric`, `record_cognition_participation`, query/reconstruct APIs | Lifecycle and evidence; no model authority. |
| Provider proposal | `run_provider_attachment`, `run_certified_provider_attachment`, reconstructors | Proposal creation and validation with Replay. |
| Single cognition | `run_llm_cognition_provider_runtime`, `create_default_openai_cognition_provider_contract`, `create_llm_cognition_provider_request`, `invoke_approved_cognition_provider` | OpenAI-specific governed cognition and Replay. |
| Multi-provider cognition | `run_multi_provider_cognition_runtime`, `create_default_cognition_provider_contract`, reconstructor/renderer | Provider-neutral transport registry, bounded comparison input, and failure isolation. |
| Live transport | `run_live_provider_http_transport`, request/response/error/audit constructors, reconstructor | Bounded HTTP transport evidence. |
| PGSP cognition | `run_g5_pgsp_bound_read_only_provider_cognition_runtime`, `run_g5_live_pgsp_provider_cognition_entrypoint` | Read-only proposal cognition under PGSP/governance evidence. |
| Conversation proposal validation | `create_conversation_interpreter_proposal_v2`, `validate_conversation_interpreter_proposal_v2`, `compare_validated_candidate_operation_sets_v2` | Local candidate operations only; no invocation or mutation. |

Representative exact registry boundary:

```python
class ProviderRegistry:
    """Deterministic metadata registry. It does not dispatch or execute providers."""
```

Representative exact selection boundary:

```python
def select_unified_resource(
    *,
    selection_id: str,
    workflow_type: str,
    required_capability: str,
    requested_role_type: str,
    domain_id: str,
    created_at: str,
    replay_dir: str | Path,
    provider_necessity_classification: str | None = None,
    worker_authorization_required: bool = False,
    min_trust_level: str = "STANDARD",
    preferred_resource_id: str | None = None,
    context_assembly_output: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select an eligible resource and active role without invoking it."""
```

The algorithm sorts eligible candidates by `selection_priority`,
`resource_id`, and role. It fails closed when the two leading candidates have
the same priority. Selection is therefore deterministic and policy-driven,
with an optional explicit preferred resource. It is neither provider-driven
nor execution-authorizing.

## Current Consumer Map

| Consumer | Current use | EPP surface consumed |
|---|---|---|
| OCS cognition | Single/multi-provider analysis, comparison, clarification, continuity | ERR, cognition contracts, transport registry, normalization, Replay. |
| Provider-assisted conversation and intent classification | Deterministic-first semantic fallback | Current provider registry, certified attachment, OpenAI proposal adapter. |
| ACLI/HIR helper presentation | Advisory explanation and provider-unavailable fallback | Callable provider boundary, deterministic fallback, UHCL wrapper, Replay. |
| Provider proposal production | Proposal generation/repair after governed clarification | Unified selection and provider proposal attachment/validation. |
| Worker Platform | External OpenAI Worker and bounded Codex execution | Separate Worker adapter, Authorization evidence, connector/transport, result normalization. |
| PGSP | Read-only provider cognition sessions | Provider identity, governance checkpoint, request/response envelopes, participation evidence. |
| Provider lifecycle/operator CLI | Onboard, verify, rotate, disable, inspect, invoke specialized native paths | Provider Governance, vault, ERR, specialized invocation entry points. |
| Conversation Layer V2 | None for provider invocation | G59-04 currently imports only CWM V2 and common fail-closed errors. |

The same EPP architecture can support interpreters, helpers, cognition/planning
assistants, and provider-backed Workers only through separate role identities
and contracts. A shared provider family or credential backend does not merge
roles. Coding agents remain Worker Platform consumers when they execute; a
coding model used only to propose must use a provider role instead.

## Provider and Model Role Map

### Registered provider identities

| Identity | Located status | Capabilities/role evidence |
|---|---|---|
| `openai` | Active/current; only provider certified for both governed cognition and supervised external Worker use | ERR reasoning/planning/summarization/analysis/generation; unified proposal generation/repair/clarification; OpenAI adapter. |
| `claude` / `ANTHROPIC` | Registry and credential identity; live Claude executor/certification exists; Worker catalog remains structural/not certified | Cognition provider metadata and proposal/helper role candidate. |
| `gemini` | Registry, ERR, credential, and onboarding identity only | Cognition metadata; no authenticated live adapter located. |
| `mistral` | Registry, ERR, credential, and onboarding identity; remote/local candidate in catalog | No authenticated live adapter or local-model runtime registration located. |
| `codex-cognition` | Registered inactive Provider Platform identity | Non-authoritative cognition/proposal identity. |
| `codex-execution` | Separate Worker Platform identity | Bounded coding Worker only after authorization. |
| `CODEX` | Unified-selection hybrid resource with separate provider and Worker bindings | Provider proposal/implementation assistance vs authorized implementation/filesystem Worker. |
| `CLAUDE_CODE` | Unified-selection hybrid candidate with separate provider and Worker bindings | Approved structural role bindings, not proof of live execution certification. |
| `standards_adapter` | G13 deterministic/injected cognition participant | Test/certification cognition comparison role, not an external model registry entry. |

### Model identities

- `gpt-5.1` is the current default in the OpenAI proposal and single-provider
  cognition adapters.
- `gpt-5-mini` and `gpt-5-nano` appear in multi-provider cost tables, not as
  independently registered model resources.
- `codex-governed-cognition` is the model identity attached to the
  `codex-cognition` provider identity.
- `standards-adapter-cognition-v1` is deterministic certification metadata.
- Claude, Gemini, and Mistral model-version identities are not centrally
  registered in the located current architecture.

There is no canonical runtime model registry with independent model lifecycle,
version, role, capability, or selection records. EPP currently selects a
provider/resource role; the selected adapter or caller supplies the model
string. This is sufficient for existing bounded flows but insufficient for
claiming model-level centralized routing.

### Role separation

The repository explicitly separates:

- provider identity from concrete model metadata;
- cognition provider from translation and repair Worker identities;
- `codex-cognition` from `codex-execution`;
- provider proposal authority from deterministic validation authority;
- provider selection from Authorization;
- Worker execution from cognition/helper output; and
- Replay evidence ownership from provider response ownership.

The role-separated certification defines `openai-cognition`,
`openai-translation`, and `openai-repair` with separate credential references,
participation locations, lifecycle evidence, metrics, and authority flags.

## Selection and Dispatch Flow

### Selection character

| Question | Finding |
|---|---|
| Deterministic? | Yes for ERR registry order and unified priority policy; unified equal-priority ambiguity fails closed. |
| Advisory? | Provider output is advisory; selection evidence itself is deterministic metadata. |
| Policy-driven? | Yes: necessity, role, capability, domain, lifecycle, trust, authority profile, preferred resource, and Worker-authorization precondition. |
| Provider-driven? | No provider may select itself or authorize invocation. |
| Does selection dispatch? | No. Both ERR and unified selection record `provider_invoked = false`, `worker_invoked = false`, and no dispatch/authorization. |

### A. Existing Worker/provider use

```text
Human / Objective
  -> Platform Core admission and Development Governance
  -> Capability Selection
  -> Unified Resource Selection [role=WORKER_ROLE]
  -> Authorization owner validates exact Worker request
  -> Worker Platform
  -> role-specific adapter (OpenAI external Worker or codex-execution)
  -> bounded connector/transport
  -> external provider/process
  -> normalized Worker result
  -> Completion and Replay evidence
  -> HIR / AiCLI
```

Selection does not authorize the Worker. The Worker adapter cannot convert a
provider identity into authorization, and provider response text cannot become
a governance decision.

### B. Existing helper/collaborator use

```text
Human request / OCS context
  -> deterministic self-resolution or provider-necessity policy
  -> ERR or Unified Resource Selection [role=PROVIDER_ROLE]
  -> approved provider contract and role identity
  -> provider adapter / cognition transport
  -> untrusted provider response
  -> deterministic schema, authority-text, and lineage validation
  -> normalized cognition/proposal/helper artifact
  -> comparison or deterministic fallback
  -> OCS / UHCL consumer
  -> Replay evidence owned by the current helper/cognition runtime
```

Provider failures are isolated where multi-provider cognition is used. Helper
output remains non-authoritative and cannot invoke a Worker.

### C. Proposed Conversation Interpreter use through EPP

```text
Human turn
  -> Conversation Layer V2 immutable interpreter request capsule
  -> Conversation Layer provider-necessity policy
  -> versioned EPP interpreter-assistance adapter
  -> Unified Resource Selection
       role=PROVIDER_ROLE
       capability=LANGUAGE_UNDERSTANDING_PROPOSAL
       authority=PROVIDER_PROPOSAL_ONLY
  -> role-specific interpreter/provider identity and bounded credential reference
  -> existing EPP adapter/transport
  -> untrusted external response
  -> adapter validates closed response shape and strips transport metadata
  -> G59-04 create/validate proposal APIs
  -> non-authoritative candidate operation set
  -> G59-05 deterministic atomic commit owner
  -> Conversation State Machine / Objective Readiness

Stop: no Objective Commitment or execution authority is granted by this flow.
```

Only non-content provider selection/availability/transport disposition may be
Replay-visible. Human turn text, raw provider output, interpreter proposal,
confidence, comparison, and validation disposition remain local Conversation
Working Memory data as required by G58-01 and G59-04.

### Failure, timeout, evidence, and substitution rules

- Provider metadata and selection validate fail closed on unknown identities,
  inactive status, missing capabilities, role mismatch, trust mismatch,
  authority mismatch, necessity mismatch, and ambiguous priority.
- OpenAI proposal and cognition paths use bounded non-streaming calls, fixed
  timeouts, no tools/function calling, and no automatic retries.
- Live transports classify timeout, HTTP, unavailable, malformed-response,
  credential, and authority-bearing-response failures and redact secrets.
- Multi-provider cognition isolates individual provider failure and records
  usage/cost metadata when available; it does not silently promote a failed
  provider result.
- Current architecture generally prohibits implicit fallback, retry, or model
  substitution. Deterministic fallback is explicit in helper runtimes; another
  provider may be tried only through a separately governed selection/request.
- Provider lifecycle operations such as disable, rotate, replace, and delete
  require explicit approval where specified by the vault/governance owner.
- Replay reconstructors validate file sets, order, hashes, references, and
  authority flags; secrets are excluded.
- Replay records what happened but does not authorize a provider or Worker.

## Direct Provider Bypass Audit

Concrete provider calls exist. They fall into three different conditions:

1. **Expected adapter boundary:** `aigol/provider/providers/openai_provider.py`,
   `live_openai_executor.py`, `live_claude_executor.py`, and
   `live_provider_http_transport.py` call concrete endpoints only as bounded
   adapter/transport implementations. They are not authority bypasses when
   reached through their governed caller.
2. **Selection bypass:** `llm_cognition_provider_runtime.py` and
   `native_provider_execution_runtime.py` can select OpenAI by local constant
   and invoke it without consuming ERR or Unified Resource Selection evidence.
   Their credential, approval, timeout, response, and Replay checks may still
   be governed, but they bypass the canonical central selection surface.
3. **Historical/legacy direct paths:** `runtime/providers/openai_provider.py`,
   `real_openai_api_invocation.py`, and the legacy OpenAI adapter retain earlier
   concrete calls or SDK paths. Current evidence identifies them as unused,
   experimental, or explicitly retired/legacy rather than suitable new
   integration points.

The CLI still exposes specialized native/provider commands, so direct-provider
selection bypass cannot be declared absent repository-wide. No import or call
from Conversation Layer V2 into any concrete provider was located.

The interpreter integration must therefore enter through EPP selection and a
role-specific adapter, not through any direct OpenAI/Claude function.

## Conversation Interpreter Compatibility

### Compatible existing properties

- Provider metadata and canonical cognition contracts explicitly set all
  authority flags false.
- Current proposal adapters produce proposal envelopes, not Objectives,
  authorization, dispatch, or semantic state mutations.
- Unified selection already contains provider-only capabilities including
  `PROPOSAL_GENERATION`, `PROPOSAL_REPAIR`, and `CLARIFICATION_ASSISTANCE`.
- EPP supports interchangeable provider identities and injected transport
  registries.
- Deterministic validation, provider failure isolation, timeout bounds,
  credential separation, and secret-free evidence already exist.
- Role separation prevents the same external family from inheriting Worker or
  execution authority in a cognition role.
- G59-04 accepts an `EXTERNAL_LANGUAGE_MODEL` identity but treats class and
  confidence as non-authoritative.

### Incompatibilities preventing direct reuse

- G58-01 requires a distinct interpreter identity/version and immutable request
  capsule. No current EPP registry entry binds a provider to the exact
  Conversation Interpreter descriptor and G59-04 proposal schema.
- G59-04 exposes no provider invocation API and intentionally imports neither
  EPP nor Replay.
- Existing cognition outputs normalize findings/assumptions/risks, not the six
  typed semantic slot operation schema required by G59-04.
- Current cognition and provider attachment runtimes persist raw responses,
  prompts, or proposal artifacts to Replay. G58-01 requires human turns, raw
  interpreter output, interpreter proposals, confidence, comparison, and
  validation dispositions to remain local and non-Replay-visible.
- No current capability ID exactly means bounded language-understanding
  proposal for Conversation Layer V2.
- No general model registry guarantees an immutable provider/model/version
  binding for an interpreter descriptor.

Therefore EPP is constitutionally compatible as the provider boundary, but no
current API is a drop-in Conversation Interpreter integration.

## Constitutional Ownership Assessment

| Concern | Existing/future owner | Compatibility finding |
|---|---|---|
| Human turn and session context | Conversation Envelope / Conversation Layer V2 | EPP receives only a bounded immutable capsule; it owns no session state. |
| Semantic interpretation proposal | Interpreter identity through EPP adapter | Proposal only; no semantic authority. |
| Proposal validation/comparison | G59-04 deterministic validator | Must remain the sole admission owner for interpreter outputs. |
| Semantic CWM mutation | G59-05 Proposal Commit Runtime and G59-02 slot owner | EPP and interpreters receive no mutation handle. |
| Conversation transitions/readiness | G59-03 and G59-06 | Provider confidence or selection cannot change readiness. |
| Objective Commitment | G59-07 commitment owner | Occurs only after Conversation Layer readiness and confirmation. |
| Provider identity/lifecycle/credential | EPP Provider Services | Reused; distinct interpreter role reference required. |
| Provider selection | Unified Resource Selection / OCS policy | Deterministic evidence only; never authorization. |
| Worker execution | Worker Platform after Authorization | Separate identity and request; unavailable to interpreter role. |
| Authorization | Authorization owner | Not supplied by EPP, model, interpreter, or selection. |
| Replay | Replay owner | Records permitted EPP operational evidence only; Conversation proposal content stays local. |
| Platform Core | Existing certified pipeline owners | Not entered by interpreter assistance; only committed Objective can cross boundary. |
| PCBV31 | Existing baseline identity record | No source, socket, membership, or authority change is proposed. |

The architecture satisfies the constitutional rule:

```text
models and providers may assist
-> interpreters may propose
-> deterministic Conversation Layer owners validate and commit
-> Objective Commitment may later create the pipeline hand-off
-> selection never equals authorization
```

## Gap Analysis

### Finding

**B — The existing central system is mostly sufficient but requires a bounded,
versioned extension.**

Finding A is too strong because current EPP Replay/output schemas and role
bindings are not directly compatible with G58-01 locality and G59-04 typed
operations. Finding C is not justified because G6-02/G6-03 already
canonicalized the overlapping surfaces and bounded reuse does not depend on a
broad consolidation. Finding D is disproved by authenticated EPP evidence.

### Exact gaps

| Order | Exact module/owner | Missing contract | Change type | Constitutional risk if omitted |
|---|---|---|---|---|
| 1 | New bounded module recommended as `aigol/runtime/conversation_interpreter_epp_assistance_runtime_v1.py`; joint boundary owned by Conversation Layer request construction and EPP provider invocation | `CONVERSATION_INTERPRETER_EPP_ASSISTANCE_CONTRACT_V1`: immutable G58 request capsule in, untrusted bounded provider response out; no CWM, Objective, Worker, tool, or pipeline handles | Additive, versioned adapter | Direct provider coupling, input overexposure, or transfer of provider metadata into semantic authority. |
| 2 | `aigol/runtime/unified_resource_selection_runtime.py`; OCS/EPP selection owner | Versioned role/capability binding for `PROVIDER_ROLE` + `LANGUAGE_UNDERSTANDING_PROPOSAL` + `PROVIDER_PROPOSAL_ONLY`, with exact interpreter identity/version and external-data-processing policy | Versioned registry/policy extension | Reusing generic clarification or implementation roles could conflate model role and authority. |
| 3 | New adapter above G59-04, calling existing `platform_core_conversation_interpreter_proposal_runtime_v2.py`; Conversation Layer validation owner | Deterministic mapping from a closed provider response schema to `create_conversation_interpreter_proposal_v2`, followed by mandatory `validate_conversation_interpreter_proposal_v2` | Additive adapter; no G59-04 semantic change | Raw provider text could bypass source-span, taxonomy, revision, conflict, and authority validation. |
| 4 | EPP evidence boundary in the new adapter, reusing selection/transport reconstructors; Replay owner | `CONVERSATION_INTERPRETER_EPP_EVIDENCE_PROFILE_V1`: Replay may contain provider identity/version, selection hash, timing/failure class, and content-free request/response digests only when approved; it must exclude human text, raw output, semantic proposal, confidence, comparison, and validation disposition | Versioned evidence profile | Existing raw-response Replay behavior would violate G58-01 conversation locality and may expose human content. |
| 5 | New interpreter descriptor/config record consumed by the adapter; Conversation Layer configuration owner with EPP identity reference | Immutable binding of `interpreter_identity`, interpreter version, provider resource ID, exact model/config version, supported proposal schema, limits, timeout, external processing flag, and disabled tools/streaming/retries | Additive versioned configuration | Provider identity alone cannot prove the model/config or interpreter role that generated a proposal. |

No new credential vault, provider registry, model router, provider transport,
Replay owner, Authorization owner, Worker path, Objective owner, or central LLM
subsystem should be created.

### Recommended implementation order

1. Certify the role/capability, privacy, and evidence contracts before runtime
   code.
2. Add the immutable interpreter descriptor-to-EPP resource/model binding.
3. Implement the thin EPP assistance adapter using existing selection,
   credential, adapter, timeout, and failure owners.
4. Implement the closed output-to-G59-04 mapping and require G59-04 validation
   before returning any candidate operation set.
5. Add deterministic/injected-provider tests for stale revisions, malformed
   output, authority claims, timeout, unavailable provider, content-free Replay,
   repeated evaluation, and role separation.
6. Certify an isolated Conversation Layer session that stops before Objective
   Commitment and proves zero Platform Core, Authorization, Worker, or execution
   reachability.

## Recommended Reuse Direction

Reuse EPP as the only external model/provider boundary. Reuse:

- current provider identity and lifecycle records;
- unified deterministic resource selection;
- credential vault and provider governance evidence;
- current role-specific provider adapters and bounded transports;
- timeout, no-retry/no-tool, redaction, failure, and substitution controls;
- G59-04 as the only interpreter proposal validator; and
- G59-05 as the only atomic semantic commit owner.

Do not reuse unchanged:

- the OpenAI-specific single-provider cognition entry point;
- native/direct provider execution;
- provider-assisted intent classification as semantic truth;
- current raw-response Replay schema; or
- Worker/coding identities for interpretation.

External Codex is both represented inside and outside EPP depending on role:

- `codex-cognition` is an EPP Provider Platform identity and may only provide
  non-authoritative cognition proposals;
- `codex-execution` and the bounded Codex CLI connector are Worker Platform
  execution identities, outside interpreter assistance;
- the unified `CODEX` resource is a hybrid metadata record whose provider and
  Worker bindings remain independently governed.

This role separation is the template for every provider family used by a
future Conversation Interpreter.

# 3. Constitutional Self-Assessment

## Verified

- The canonical existing system is authenticated as EPP by G6-02, G6-03, and
  G6-12; it was not inferred from filenames alone.
- EPP is a distributed canonical architecture over existing owners, not a new
  monolithic runtime or constitutional authority.
- Provider, resource, role, capability, credential, adapter, transport,
  cognition, Worker binding, evidence, and Replay surfaces were located and
  traced to current APIs and consumers.
- Current selection is deterministic and policy-driven and explicitly does not
  invoke, dispatch, authorize, or create execution authority.
- The repository has provider registries and role bindings but no general
  canonical model registry; model strings remain adapter/request metadata.
- OpenAI, Claude/Anthropic, Gemini, Mistral, Codex cognition/execution, and
  structural local-provider evidence were characterized without invoking them.
- Concrete provider calls and selection-bypass paths were located; no
  Conversation Layer V2 concrete-provider call was found.
- G58-01 and G59-04 compatibility is partial but architecturally sound through
  a bounded versioned adapter and evidence profile.
- The proposed reuse direction preserves Conversation Layer, Objective,
  Platform Core, Replay, Authorization, Worker, Development Governance, and
  PCBV31 ownership.
- Only this G48 report was added; runtime, tests, registries, providers, and Git
  history remained unchanged.

## Not Verified

- No external provider availability, credential validity, response behavior,
  latency, pricing, or current vendor model catalog was verified because
  provider/network execution was forbidden.
- Claude, Gemini, Mistral, xAI/Grok, and local-model production readiness was
  not inferred beyond authenticated repository evidence. No xAI/Grok provider
  identity or live adapter was located.
- The recommended Conversation Interpreter EPP adapter, role/capability binding,
  descriptor binding, and privacy/evidence profile do not yet exist and were
  not implemented or executed.
- No end-to-end Conversation Interpreter provider session was run; doing so is
  outside this read-only audit.
- Historical Git was used to authenticate principal EPP and registry lineage,
  but unreachable external archives and remotes were not searched because
  current authenticated evidence was sufficient to locate and characterize the
  central system.
- Repository governance conformance remains `PARTIALLY_CONFORMANT`: the
  read-only engine reported 18 checks passed, two hook-drift checks failed,
  zero critical violations, and report hash
  `0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea`.
  This is a visible pre-existing repository limitation and is not caused or
  repaired by this audit.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Locate canonical central system | G6-01/G6-02/G6-03/G6-12 commits, hashes, and content | Cross-artifact identity and ownership review | PASS |
| Search complete required repository scope | Semantic inventory across `aigol`, `sapianta_bridge`, tests, docs, `.github`, registries/manifests, and Git history | Repository-wide `rg`, import/call-site tracing, `git log --follow` | PASS |
| Identify public APIs and registries | Provider Registry, ERR, unified selection, governance, vault, cognition, transport, G59-04 | Definition and caller review | PASS |
| Determine provider/model/role/capability coverage | Runtime constants, default registries, role identities, capability catalog | Cross-schema inventory | PASS |
| Determine model-selection semantics | `select_resource_for_capability`, `select_unified_resource` | Algorithm and negative-path review | PASS |
| Map current consumers | Runtime imports and call sites in OCS, helpers, CLI, PGSP, Workers, Conversation Layer | Import/caller tracing | PASS |
| Characterize Worker/helper/interpreter reuse | Role-separated identities, provider attachment, Worker adapters, G58-01/G59-04 | Ownership comparison and three sequence reconstructions | PASS |
| Audit direct concrete-provider calls | Network/SDK/credential identifier search and caller tracing | Concrete endpoint/import review | PASS |
| Characterize Replay, authorization, timeout, failure, substitution | Runtime validators/reconstructors, vault, selection, cognition, transport | Boundary and failure-path review | PASS |
| Characterize external Codex | G11-06A, Codex integration runtime, unified registry, connectors | Provider/Worker identity comparison | PASS |
| Assess G58-01 proposal-only compatibility | G58-01, canonical provider contract, proposal attachment, G59-04 | Contract-difference analysis | PASS |
| Select A/B/C/D gap finding | Authenticated architecture and exact missing contracts | Fail-closed alternative comparison | PASS |
| Focused runtime evidence | Provider registry, ERR, unified selection, single/multi cognition, provider helpers, Codex identity split, G59-04, governance tests | `python -m pytest` over 10 focused files: 105 passed | PASS |
| Repository governance conformance | Governance conformance engine | 18 passed, 2 known hook-drift checks failed, 0 critical violations; `PARTIALLY_CONFORMANT` | PARTIAL |
| External provider behavior | Forbidden network/provider execution | Not run by design | NOT_APPLICABLE |
| Runtime implementation of recommended extension | Read-only audit restriction | Not authorized | NOT_APPLICABLE |
| Governance report structure | G48 exact six-section rule | Top-level heading review | PASS |
| Repository mutation boundary | Git status and final diff review | Only required report permitted | PASS |
| Markdown/worktree hygiene | New report | `git diff --check` | PASS |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G61_01_EXISTING_CENTRAL_LLM_SERVICES_DISCOVERY_AND_CONSTITUTIONAL_INTEGRATION_AUDIT_REPORT_V1.md`:
  added this G61-01 read-only audit report.

Unchanged subsystems:

- EPP runtime, provider registries, model/role/capability metadata, adapters,
  connectors, transports, credential vault, provider governance, and CLI.
- Conversation Layer V2, Semantic CWM, Proposal Commit, State Machine,
  Objective Readiness, and Objective Commitment.
- Platform Core, Development Governance, Capability Selection, Authorization,
  Worker, Completion, Replay, HIR, AiCLI, PCBV31, and all tests.
- Existing governance artifacts and Git history.

API compatibility:

- No API, schema, registry, manifest, credential, provider, selection, routing,
  transport, Replay, or execution behavior changed.

Boundary preservation:

- The report identifies EPP for reuse and explicitly rejects a duplicate
  central model/provider architecture.
- Suggested work is future, bounded, versioned, and subordinate to existing
  Conversation Layer and EPP owners.
- Provider/model selection remains distinct from semantic validation,
  Objective Commitment, Authorization, Worker invocation, and execution.

Unrelated pre-existing changes:

- None observed at audit start.

# 6. Certification Verdict

EXISTING_CENTRAL_LLM_SERVICES_LOCATED_AND_CHARACTERIZED
