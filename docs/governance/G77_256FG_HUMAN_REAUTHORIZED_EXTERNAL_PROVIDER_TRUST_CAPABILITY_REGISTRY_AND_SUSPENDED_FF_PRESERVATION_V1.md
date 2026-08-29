# 1. Implementation Summary

Generation: G77-256FG

Report identity: G77_256FG_HUMAN_REAUTHORIZED_EXTERNAL_PROVIDER_TRUST_CAPABILITY_REGISTRY_AND_SUSPENDED_FF_PRESERVATION_V1

Reporting date: 2026-08-29

Constitutional baseline: `constitutional-governance-finalize-v1`; FE HEAD
`92ccdedb2d846c91878bf7a5b2ac958c547d60a1`, tree
`7cf4ab8dc22849db2445a80bf9e1dcae639747b0`, subject
`G77-256FE admit WRONG_ATTEMPT through DU EB EE preflight`

Implementation contracts: current Human G77-256FG corrected continuation;
G77-256EX common-substrate certificate; authenticated and suspended G77-256FF
repository evidence; provider identity and authority-separation contracts; and
G48 Constitutional Evidence Reporting Standard V1.

Objective:

Extend the existing non-executing AiGOL provider registry with one central,
evidence-backed, identity- and scope-bound external capability fact store and
one role/task/operation-aware eligibility resolver, while preserving the same
materialized, unbooted FF generation and producing a repository-mediated Human
return contract.

Implementation scope:

- generic provider capability facts keyed by provider, account/workspace,
  access path, worker, capability, and authorized scope;
- consumer-specific role, task, operation, capability, scope, and quota policy;
- one central fail-closed resolver returning eligibility without selection,
  dispatch, authority, provider invocation, or execution;
- replay hashes, evidence SHA-256 binding, strict non-transferability, and
  secret-like material rejection;
- Trusted Access represented only as one generic capability instance;
- repository-only Phase A/B/C/D evidence and an FF return contract.

Modified modules:

- `aigol/provider/provider_registry.py`: bounded extension of the existing
  provider metadata registry;
- `tests/test_external_provider_capability_registry_v1.py`: focused
  fail-closed, isolation, authority, reuse, and extensibility validation;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/`:
  corrected Phase A, Phase B, Phase C, Phase D, and FF return evidence;
- this G48 report.

Intentionally unchanged modules:

- the complete FF evidence namespace, including its sole candidate,
  materialization, overlay, seed, QEMU argv, launcher, and unsealed preboot
  artifact;
- provider identity boundaries and the credential vault;
- provider necessity, unified resource selection, worker selection, task and
  execution admission, SPCE/CLREC routing, P11, P12, and production routing;
- EX common proof substrate and all 17 certified components.

Architectural boundaries preserved:

- `ProviderRegistry` remains metadata-only and non-executing;
- provider facts do not grant Human, P11, execution, dispatch, or selection
  authority;
- consumer policy does not own or duplicate provider facts;
- raw credentials remain outside repository evidence;
- current worker Trusted Access and the exact FF external-capability
  requirement remain `NOT_ESTABLISHED`;
- the FF preboot file remains unchanged and invalid because existing checkpoint
  authority does not permit replacing an already existing output;
- no FF boot, QEMU execution, WRONG_ATTEMPT execution, retry, repair, replay,
  E05 credit, P12 entry, or production mutation occurred.

## Final state and decisions

| Field | Evidence classification | Result |
|---|---|---|
| `PROJECT_PROGRESS_ESTIMATE` | `NOT_MEASURED` for whole project; `MEASURED` for bounded FG | FG repository objective complete; E05 remains 6/18 |
| `CONSTITUTIONAL_HEALTH_EVIDENCE` | `PROVEN` | Phase A/B/C/D hash chain, 220 unique focused tests, EX 12/12, current engine 20/20, FF hash reauthentication |
| `CONSTITUTIONAL_HEALTH` | `DERIVED` | PASS with open preboot and external-capability limitations |
| `SHADOW_AUTOMATION_STATE` | `FACT` | Unchanged; not entered |
| `SHADOW_AUTOMATION_READINESS` | `NOT_ESTABLISHED` | Not authorized |
| `CONSTITUTIONAL_FRONTIER_DISTANCE` | `NOT_MEASURED` | No certified whole-project denominator |
| `CONSTITUTIONAL_FRONTIER_DISTANCE_E05` | `MEASURED` | 12/18 items remain; WRONG_ATTEMPT is unsatisfied |
| `GOVERNANCE_EFFICIENCE` | `DERIVED` | Existing EX and provider control plane reused; no operational replay |
| `COGNITION_ASSISTED_HANDOFF` | `PROVEN` | Sealed FF return contract exists |
| `AIGOL_CODEX_WORK_SHARE` | `NOT_MEASURED` | No direct telemetry |
| `OVERENGINEERING_RISK` | `ESTIMATED` | LOW_TO_MODERATE: three data models and one resolver in one existing registry; no service or executor |
| `COGNITION_PROVENANCE` | `FACT` | Human corrected FF boundary; repository evidence remained authoritative; Codex performed repository-only work |
| `CANDIDATE_CAPABILITY` | `NOT_APPLICABLE` to FG | FF candidate unchanged |
| `SHADOW_DESIGN_TARGET` | `NOT_APPLICABLE` | No shadow automation change |
| `CONSTITUTIONAL_CONTINUATION_PROGRESS` | `DERIVED` | FG complete; FF ready for Human review, not automatic resume |
| `PROMPT_CONTEXT_REUSE_RATIO` | `NOT_EXACTLY_MEASURABLE` | Structural continuation reuse only |
| `TOKEN_BENCHMARK` | `NOT_MEASURED` | No direct token telemetry |
| `LLM_COST_REDUCTION_RATIO` / `LCRR` | `NOT_MEASURED` | No direct cost telemetry |
| `SPCE_HANDOFF_EFFICIENCY` / `SHER` | `DERIVED` / `NOT_EXACTLY_MEASURABLE` | Avoided Phase A, candidate, and materialization reconstruction |
| `EXTERNAL_PROVIDER_REGISTRY_STATE` | `PROVEN` | Central bounded extension complete; execution consumers not integrated |
| `TRUSTED_ACCESS_CAPABILITY_STATE` | `EXTERNAL_PROVIDER_FACT` | `NOT_ESTABLISHED` for the current worker |
| `FF_SUSPENSION_STATE` | `FACT` | `MATERIALIZED__NOT_BOOTED` |
| `FF_RETURN_READINESS` | `PROVEN` | PASS for Human review; blocked for automatic resume |
| `PRE_BOOT_SEALING_DECISION` | `DERIVED` | `NEW_AUTHORITY_OR_NEW_OPERATIONAL_ACTION_REQUIRED` |
| `ISOLATION_DECISION` | `PROVEN` | Same FE-pinned FF worktree remains valid; any pre-completion FG commit must use a separate branch/worktree |
| `PROVIDER_CONTROL_PLANE_REUSE_DECISION` | `DERIVED` | Extend `aigol.provider.ProviderRegistry` |
| `CENTRAL_CAPABILITY_MODEL_STATE` | `PROVEN` | PASS |
| `MULTI_ROLE_CAPABILITY_RESOLUTION_STATE` | `PROVEN` | PASS |
| `MULTI_CONSUMER_CAPABILITY_REUSE_STATE` | `PROVEN` | PASS; two consumers resolve one fact hash |
| `PROVIDER_FACT_CONSUMER_POLICY_SEPARATION` | `PROVEN` | PASS |
| `TRUST_CAPABILITY_STATE_DUPLICATION_COUNT` | `MEASURED` | 0 |
| `CAPABILITY_CONSUMER_COUNT` | `MEASURED` in focused demonstration | 2 |
| `CENTRAL_CAPABILITY_QUERY_COUNT` | `MEASURED` as public resolver interfaces | 1 |
| `PARALLEL_CAPABILITY_REGISTRY_COUNT` | `MEASURED` | 0 |

Direct context, five-hour, seven-day, and elapsed-time telemetry were not
available. Structural savings are proven by EX reuse, the existing provider
control-plane extension, zero candidate reconstruction, zero materialization
replay, one provider fact for multiple consumer policies, and one resolver.

## Reuse impact assessment

1. Reused certified capabilities: all 17 applicable EX common components.
2. New capability: one bounded generic provider-capability extension composed
   of three immutable data models and one resolver.
3. Existing capability reachability loss: 0.
4. Parallel flow created: no.
5. Production paths: unchanged, delta 0.
6. Provider capability is reachable through one central registry by multiple
   consumer policies; no consumer-specific Trusted Access truth was created.
7. Provider facts and consumer policy are separate immutable representations.
8. A future provider/capability requires provider and fact registration plus
   only relevant policy bindings; the central resolver does not change.

| Reuse/complexity metric | Result |
|---|---|
| `CERTIFIED_COMPONENT_REUSE_COUNT` | 17 |
| `EX_RECONSTRUCTION_COUNT` | 0 |
| `EXISTING_PROVIDER_CAPABILITY_REUSE_COUNT` | 5 |
| `NEW_COMMON_COMPONENT_COUNT` | 0 |
| `NEW_PROVIDER_COMPONENT_COUNT` | 1 bounded extension |
| `NEW_PROVIDER_CONTROL_PLANE_COUNT` | 0 |
| `CAPABILITY_REACHABILITY_LOSS` | 0 |
| `PARALLEL_FLOW_CREATED` | NO |
| `DUPLICATE_PROVIDER_CONTROL_PLANE_CREATED` | NO |
| `DUPLICATE_CAPABILITY_STATE_CREATED` | NO |
| `PRODUCTION_PATH_DELTA` | 0 |
| `NEW_SCHEMA_COUNT` | 3 immutable runtime data models |
| `NEW_SERVICE_COUNT` | 0 |
| `NEW_EXECUTOR_COUNT` | 0 |
| `NEW_CAPABILITY_RESOLVER_COUNT` | 1 |
| `DUPLICATE_PROOF_PATH_COUNT` | 0 |
| `DUPLICATE_PROVIDER_FACT_COUNT` | 0 |
| `PREMATURE_GENERALIZATION_RISK` | LOW: only fields exercised by identity, role/policy, evidence, quota, and one non-Trusted-Access capability probe |

## Human-readable completion answers

1. Yes. The corrected FF state was reauthenticated as 1 candidate, 1
   materialization, 1 VM creation, 0 boot, 0 QEMU execution, and 0
   WRONG_ATTEMPT execution.
2. The interrupted preboot placeholder was authenticated and left byte-for-byte
   unchanged.
3. No. Deterministic replacement was not permitted by the existing atomic
   checkpoint-writer authority because that protocol refuses an existing
   output.
4. The existing `aigol.provider.ProviderRegistry`, provider identity boundary,
   credential vault, provider necessity policy, and unified resource-selection
   architecture were found.
5. Yes. The existing provider registry was extended; no second control plane
   was created.
6. Canonical provider capability truth is represented by exactly keyed
   `ExternalProviderCapabilityFact` records held by `ProviderRegistry`.
7. Trusted Access is a generic capability value bound to provider,
   account/workspace, access path, worker, and scope; it is not global or
   transferable.
8. Yes. The same fact hash served two different consumer roles/policies in the
   focused validation.
9. Yes. `ExternalProviderCapabilityFact` is distinct from
   `ExternalCapabilityRequirement`.
10. Yes. Unknown or missing exact capability state makes the worker ineligible
    and requires Human action.
11. No. Account/workspace/access-path mismatches produce no fact match.
12. No duplicate provider control plane was created.
13. No duplicate Trusted Access state was created.
14. Yes. The sole FF candidate remains SHA-256
    `371663c5afec8baa9513da0a6e14566ffe1a8f9f62d2e274a47a90dcd43f4447`.
15. Yes. The materialization, overlay, and seed remain unchanged.
16. Final FF counters are `1/1/1/0/0/0`; retry, repair, and replay are all 0.
17. Yes, under proven isolation: any FG commit before FF completion must occur
    in a separate branch/worktree, leaving the original FE-pinned FF worktree
    and bindings unchanged. Committing FG into that FF worktree first is not
    permitted.
18. Human review must decide and explicitly authorize a new repository action
    for the existing preboot placeholder, or supply another constitutionally
    valid preboot authority; the Human must also establish the exact FF external
    capability policy and evidence state.
19. If FF policy confirms Trusted Access is required, actual external provider
    verification/activation and evidence capture are still required. None was
    performed here.
20. The minimum next step is Human review of FG and the return contract,
    followed by explicit preboot-replacement and external-capability decisions;
    reauthentication is required before any separately authorized boot.

# 2. Code Evidence

## Public API

Repository reference: `aigol/provider/provider_registry.py`.

The public extension adds registration, exact lookup, deterministic fact
listing, and one resolver. Representative exact signatures are:

```python
    def register_capability_fact(
        self,
        fact: ExternalProviderCapabilityFact | dict[str, Any],
    ) -> dict[str, Any]:
        """Register one exact, non-transferable provider capability fact."""
```

```python
    def resolve_external_capability(
        self,
        query: ExternalCapabilityQuery | dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve eligibility without selecting, dispatching, or granting authority."""
```

Each excerpt ends before its method body, which is represented in the
following subsections.

## Orchestration Entry Point

The one central resolver first binds a consumer query to an exact central fact:

```python
        capability_query = _capability_query_to_dict(query)
        requirement = capability_query["requirement"]
        provider_id = capability_query["provider_id"]

        try:
            provider = self.lookup_provider(provider_id)
        except FailClosedRuntimeError:
            return _capability_resolution(
                capability_query,
                capability_fact=None,
                state=CAPABILITY_UNKNOWN,
                reason="PROVIDER_NOT_ESTABLISHED",
                human_action_required=True,
            )

        fact_key = (
            provider_id,
            capability_query["account_or_workspace_id"],
            capability_query["access_path"],
            capability_query["worker_identity"],
            requirement["required_capability"],
            requirement["authorized_scope"],
        )
        capability_fact = self._capability_facts.get(fact_key)
        if capability_fact is None:
            return _capability_resolution(
                capability_query,
                capability_fact=None,
                state=CAPABILITY_UNKNOWN,
                reason="CAPABILITY_FACT_NOT_ESTABLISHED_FOR_EXACT_IDENTITY_AND_SCOPE",
                human_action_required=True,
            )
```

## Semantic Reductions

Unknown, unavailable, invalid, and policy-required quota states fail closed;
only the final branch is eligible:

```python
        if capability_fact["verification_state"] == UNKNOWN_OR_NOT_ESTABLISHED:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=CAPABILITY_UNKNOWN,
                reason="CAPABILITY_UNKNOWN_OR_NOT_ESTABLISHED",
                human_action_required=True,
            )
        if capability_fact["verification_state"] == PROVEN_UNAVAILABLE:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="CAPABILITY_PROVEN_UNAVAILABLE",
                human_action_required=True,
            )
        if capability_fact["validity_state"] != VALID:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="CAPABILITY_EVIDENCE_NOT_VALID",
                human_action_required=True,
            )
        if (
            requirement["requires_available_quota"]
            and capability_fact["quota_state"] != QUOTA_AVAILABLE
        ):
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="REQUIRED_QUOTA_NOT_PROVEN_AVAILABLE",
                human_action_required=True,
            )
        return _capability_resolution(
            capability_query,
            capability_fact=capability_fact,
            state=ELIGIBLE,
            reason="REQUIRED_EXTERNAL_CAPABILITY_PROVEN_AVAILABLE",
            human_action_required=False,
        )
```

## Public Validators

Proven state requires valid SHA-256-bound evidence, and all authority,
transferability, and secret-presence flags must remain false:

```python
    if verification_state in {PROVEN_AVAILABLE, PROVEN_UNAVAILABLE}:
        if evidence_sha256 is None:
            raise FailClosedRuntimeError(
                "proven provider capability state requires evidence SHA-256"
            )
        if validity_state != VALID:
            raise FailClosedRuntimeError(
                "proven provider capability state requires valid evidence"
            )
    for field_name in (
        "provider_capability_authority",
        "human_authority",
        "p11_authority",
        "execution_authority",
        "dispatch_authority",
        "transferable_between_accounts",
        "transferable_between_workspaces",
        "transferable_between_access_paths",
        "secret_material_present",
    ):
        if _require_bool(fact.get(field_name), field_name) is not False:
            raise FailClosedRuntimeError(
                f"provider capability fact cannot set {field_name}"
            )
    _reject_secret_material(fact)
```

## Canonical Data Models

Provider facts and consumer policy are separate frozen models:

```python
@dataclass(frozen=True)
class ExternalProviderCapabilityFact:
    """One identity- and scope-bound external provider capability fact."""

    provider_id: str
    account_or_workspace_id: str
    access_path: str
    worker_identity: str
    capability: str
    authorized_scope: str
    verification_state: str
    validity_state: str
    evidence_source: str
    quota_state: str = QUOTA_NOT_APPLICABLE
    evidence_sha256: str | None = None
    human_owner_or_authority_reference: str = "NOT_ESTABLISHED"

@dataclass(frozen=True)
class ExternalCapabilityRequirement:
    """Consumer policy describing one required external capability."""

    consumer_id: str
    task_id: str
    aigol_role: str
    operation_class: str
    required_capability: str
    authorized_scope: str
    requires_available_quota: bool = False
```

The excerpt omits serialization methods and the query wrapper.

## Deterministic Algorithms

The fact identity is exact and deterministic:

```python
def _capability_fact_key(fact: dict[str, Any]) -> tuple[str, ...]:
    return (
        fact["provider_id"],
        fact["account_or_workspace_id"],
        fact["access_path"],
        fact["worker_identity"],
        fact["capability"],
        fact["authorized_scope"],
    )
```

Returned decisions bind the query, requirement, and exact fact hashes and
explicitly deny downstream effects:

```python
        "worker_eligible": state == ELIGIBLE,
        "human_action_required": human_action_required,
        "action_state": (
            HUMAN_ACTION_REQUIRED if human_action_required else "NO_HUMAN_ACTION_REQUIRED"
        ),
        "worker_selected": False,
        "human_authority_granted": False,
        "p11_authority_granted": False,
        "execution_authority_granted": False,
        "dispatch_performed": False,
        "provider_invoked": False,
        "execution_requested": False,
        "automatic_continuation": False,
```

The excerpt omits adjacent hash and reason fields.

## Responsibility Boundaries

The existing registry contract remains exact:

```python
class ProviderRegistry:
    """Deterministic metadata registry. It does not dispatch or execute providers."""
```

The implementation adds no provider adapter, transport, credential store,
worker selector, dispatcher, executor, P11 authority, SPCE continuation, or
production route. The return contract is evidence and is explicitly not
authority.

# 3. Constitutional Self-Assessment

## Verified

- the corrected FF `1/1/1/0/0/0` state and exact candidate, materialization,
  overlay, seed, and preboot hashes remain authenticated;
- the interrupted preboot artifact remains the original unsealed placeholder;
- existing checkpoint-writer authority does not permit overwriting that output;
- EX passes 12/12 with 17 applicable certified components and zero
  reconstruction, operational effect, or credit effect;
- the existing provider registry was reused and no second control plane,
  service, executor, proof path, production route, or consumer-specific Trusted
  Access truth was added;
- provider facts are exact-account/workspace/path/worker/capability/scope
  records, while task/role/operation/quota requirements remain consumer policy;
- unknown, unavailable, invalid evidence, missing exact identity/scope, and
  missing required quota fail closed;
- one fact hash supports multiple roles and consumer policies whose eligibility
  outcomes may differ;
- provider availability does not grant Human, P11, worker-selection, dispatch,
  execution, or continuation authority;
- secret-like material is rejected and existing credential-vault boundaries are
  unchanged;
- a non-Trusted-Access provider/capability pair uses the same interface;
- 220 unique focused tests, EX validation, Python compilation, JSON key/hash
  checks, governance checks, and whitespace validation passed;
- the index is empty and no staging, commit, push, boot, QEMU, operational
  execution, retry, repair, replay, E05 credit, P12, or production mutation
  occurred.

## Not Verified

- the exact FF required external-capability policy is `NOT_ESTABLISHED`; a
  Human-supplied provider UI trigger alone was not converted to repository
  policy;
- the current worker Trusted Access state is `NOT_ESTABLISHED`; no external
  verification or activation occurred;
- the canonical query interface was validated with multiple consumers, but no
  execution consumer was integrated in this bounded FG scope;
- full repository regression was not run; validation covered 220 unique focused
  tests plus EX and governance checks;
- the focused current conformance engine result does not reclassify separately
  recorded historical partial-conformance or hook-drift limitations;
- FF cannot resume until Human review supplies explicit valid preboot authority
  and required external-capability policy/evidence is established;
- numeric token, context, cost, work-share, and elapsed-time telemetry were not
  available.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Correct FE baseline | Git HEAD/tree/subject | Exact Git identity commands | PASS |
| Empty index | Git index | `git diff --cached --name-only` | PASS |
| Corrected FF state | Phase A, materialization, return contract | Independent hash and artifact review | PASS |
| Candidate unchanged and count 1 | Candidate SHA-256 | File hash and inventory | PASS |
| Materialization/VM unchanged and count 1/1 | Materialization, overlay, seed hashes | File hash and transient checkout review | PASS |
| Boot/QEMU/WRONG_ATTEMPT remain 0 | No process, serial, B1, or operational evidence | Process and artifact inventory | PASS |
| Retry/repair/replay remain 0 | FF counters | Artifact reduction | PASS |
| Preboot provenance truthful | Original SHA and sentinel | Byte hash and sentinel inspection | PASS |
| No fabricated preboot sealing | Preboot file unchanged | Original and final SHA comparison | PASS |
| EX common proof reuse | EX certificate and validator | EX 12/12; 17 certified components | PASS |
| Existing provider control plane reused | Provider architecture discovery and diff | Static architecture review | PASS |
| Unknown capability fails closed | Resolver and focused test | Negative capability probe | PASS |
| Unavailable capability fails closed | Resolver and focused test | Negative capability probe | PASS |
| Available state requires evidence | Fact validator | Missing-SHA probes | PASS |
| Account A does not transfer to B | Exact fact key | Cross-account probe | PASS |
| Workspace A does not transfer to B | Exact fact key | Cross-workspace probe | PASS |
| Codex path does not imply API path | Exact fact key | CODEX-to-API probe | PASS |
| API path does not imply Codex path | Exact fact key | API-to-CODEX probe | PASS |
| Provider capability does not imply Human authority | Resolution flags | Eligible-result assertions | PASS |
| Provider capability does not imply P11 authority | Resolution flags | Eligible-result assertions | PASS |
| P11 authority does not imply provider capability | P11 absent from query model | Missing-fact probe | PASS |
| Worker eligibility does not imply execution authority | Resolution flags | Eligible-result assertions | PASS |
| Required capability excludes missing worker | Missing exact fact reduction | Negative query probe | PASS |
| Eligible worker not automatically executed | Resolution flags | No-selection/no-dispatch/no-execution assertions | PASS |
| One fact supports multiple consumers | Same fact hash, two requirements | Multi-consumer focused test | PASS |
| Consumer policy differs without fact duplication | Quota-required and quota-neutral policies | One-fact/two-outcome test | PASS |
| Consumer cannot own provider truth | Requirement validator | Ownership-tampering probe | PASS |
| Raw secrets excluded | Secret marker validator | Secret-like negative probe and evidence review | PASS |
| Trusted Access is not global | Generic fact fields | Dataclass-field assertion | PASS |
| Trusted Access is not transferable | False transfer fields and exact key | Field and mismatch assertions | PASS |
| Future provider/capability extensible | Generic models | Regional-availability probe | PASS |
| Duplicate facts fail closed | Registry duplicate guard | Duplicate-registration probe | PASS |
| Existing provider API compatibility | Existing provider consumers | 215 provider-registry consumer tests | PASS |
| Focused capability behavior | New focused suite | 16 tests | PASS |
| Governance checks | Governance test and engine | 5 tests; 20 checks, 0 failures | PASS |
| JSON unique keys and inner seals | FG evidence namespace | Duplicate-key and canonical-newline hash audit | PASS |
| G48 six-section structure | This report | Exact heading count/order audit | PASS |
| Patch whitespace | Repository diff | `git diff --check` | PASS |
| No production path | Mutation inventory | Static diff review | PASS |
| Full repository regression | Whole repository | Not executed in bounded scope | NOT_RUN |
| Current worker Trusted Access availability | External provider evidence | No evidence supplied or fabricated | BLOCKED |
| Exact FF external capability requirement | Repository policy binding | Human UI trigger only | BLOCKED |
| Valid FF preboot authorization | Existing unsealed output | Existing writer prohibits replacement | BLOCKED |

# 5. Repository Mutation Summary

Modified files:

- `aigol/provider/provider_registry.py`: one central fact store, three immutable
  models, strict validation, and one eligibility resolver;
- `tests/test_external_provider_capability_registry_v1.py`: 16 focused tests;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/G77_256FG_SPCE_PHASE_A_CORRECTED_CONTINUATION_CHECKPOINT_V1.json`:
  corrected continuation and isolation checkpoint;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/G77_256FG_SPCE_PHASE_B_IMPLEMENTATION_CHECKPOINT_V1.json`:
  implementation binding;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/G77_256FG_SPCE_PHASE_C_VALIDATION_CHECKPOINT_V1.json`:
  validation evidence;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/G77_256FG_SPCE_PHASE_D_FINAL_REDUCTION_V1.json`:
  independent final reduction;
- `.github/governance/evidence/g77_256fg_external_provider_capability_registry_v1/G77_256FF_POST_PROVIDER_WORK_RETURN_CONTRACT_V1.json`:
  repository-mediated FF handoff;
- this report.

Unchanged subsystems:

- FF candidate, materialization, VM/overlay, seed, launcher, QEMU vector,
  admission receipts, and unsealed preboot bytes;
- provider adapters, credential vault, provider identity boundaries, provider
  necessity, resource selection, worker selection, execution admission, SPCE,
  CLREC, P11, P12, shadow automation, and production routing;
- all EX common components and proof hierarchy.

API compatibility:

- all pre-existing `ProviderRegistry` methods and `ProviderMetadata` semantics
  remain available and passed the 215-test provider-consumer selection;
- the extension adds methods and immutable models without changing existing
  execution or dispatch behavior.

Boundary preservation:

- no parallel provider registry or control plane was added;
- capability resolution remains read-only with respect to external providers
  and machine effects;
- `PROVIDER_CAPABILITY_AVAILABLE != HUMAN_AUTHORIZED`,
  `PROVIDER_CAPABILITY_AVAILABLE != P11_AUTHORIZED`, and
  `WORKER_ELIGIBLE != EXECUTION_AUTHORIZED` are explicit result fields;
- production path delta is 0;
- `AUTO_CONTINUABLE = NO`, `HUMAN_REVIEW_REQUIRED = YES`, and
  `HUMAN_AUTHORIZATION_REQUIRED_FOR_NEXT_STEP = YES`.

Unrelated pre-existing changes:

- `.github/governance/evidence/g77_256ff_wrong_attempt_operational_v1/` is the
  intentionally persisted, Human-authorized suspended FF namespace. FG did not
  modify its bytes.

Commit topology:

- nothing was staged, committed, or pushed;
- if FG is committed before FF completes, it must be committed from a separate
  branch/worktree so the original FE-pinned FF worktree and one-shot launcher
  baseline remain unchanged.

# 6. Certification Verdict

PASS__CORRECTED_MATERIALIZED_FF_BOUNDARY_AUTHENTICATED__CENTRAL_EXTERNAL_PROVIDER_TRUST_CAPABILITY_REGISTRY_BOUNDED_EXTENSION__SUSPENDED_FF_PRESERVED
