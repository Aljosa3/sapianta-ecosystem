# G7-04 Platform Conflict And Fallback Canonicalization V1

Status: fourth Generation 7 canonicalization package implemented.

Final verdict: FOURTH_GENERATION_7_CANONICALIZATION_PACKAGE_IMPLEMENTED

## 1. Implementation Summary

This artifact implements the fourth optimized Generation 7 canonicalization package:

```text
G7_04_PLATFORM_CONFLICT_AND_FALLBACK_CANONICALIZATION_V1
```

It unifies canonicalization for:

- Platform Reconstruction Conflict Policy;
- Capability Discovery Fallback Policy.

This is a documentation-first policy artifact. It defines deterministic fail-closed rules, conflict classes, stale evidence handling, missing replay handling, ownership conflict rules, governance routing, and manual capability discovery fallback conditions.

It does not introduce:

- runtime conflict engines;
- fallback subsystems;
- authority layers;
- replay replacements;
- reconstruction subsystems;
- projection subsystems;
- capability discovery runtimes.

## 2. Reused Platform Core Assets

This package reuses existing certified Platform Core assets:

| Source Asset | Reused For | Authority Preserved |
| --- | --- | --- |
| `docs/governance/G7_01_PLATFORM_SOURCE_RECORD_AND_IDENTIFIER_STANDARD_V1.md` | Source records, identifiers, authority boundaries, hash policy, collision policy. | G7-01 remains source and identifier standard. |
| `docs/governance/G7_02_PLATFORM_RECONSTRUCTION_AND_PROJECTION_CANONICALIZATION_V1.md` | Reconstruction manifest, projection envelope, status vocabulary, certification vocabulary. | G7-02 remains reconstruction/projection schema source. |
| `docs/governance/G7_03_PLATFORM_MAPPING_AND_LINEAGE_CANONICALIZATION_V1.md` | Mapping records, ownership mappings, replay mappings, lineage links, cross-references. | G7-03 remains mapping and lineage schema source. |
| `docs/governance/G6_05_PLATFORM_CAPABILITY_DISCOVERY_AND_REUSE_POLICY_V1.md` | Current capability discovery workflow and reuse-before-redesign decision rules. | G6-05 remains current development policy source. |
| `docs/governance/G6_06_DETERMINISTIC_PLATFORM_MEMORY_ALIGNMENT_AUDIT_V1.md` | Classification of manual discovery as temporary methodology and future fallback path. | G6-06 remains deterministic memory alignment source. |
| `docs/governance/G6_10_PLATFORM_STATE_RECONSTRUCTION_ARCHITECTURE_AUDIT_V1.md` | Reconstruction conflict model, determinism gaps, missing source handling. | G6-10 remains reconstruction architecture source. |
| `docs/governance/G6_08_PLATFORM_CANONICAL_PROJECTION_ARCHITECTURE_AUDIT_V1.md` | Projection conflict and authority separation model. | G6-08 remains projection architecture source. |
| `docs/governance/GOVERNANCE_LINEAGE_MODEL.md` | Governance lineage and limitation preservation. | Governance lineage remains authoritative. |
| Existing Replay contracts and artifacts | Missing replay and replay conflict handling. | Replay remains evidence reconstruction authority. |

This package routes conflicts to existing owners. It does not resolve conflicts by itself.

## 3. Canonicalization Performed

This package canonicalizes:

- conflict taxonomy;
- fail-closed rules;
- stale evidence handling;
- missing replay handling;
- ownership conflict handling;
- certification conflict handling;
- source record conflict handling;
- mapping and lineage conflict handling;
- manual capability discovery fallback triggers;
- fallback retirement criteria;
- governance routing expectations;
- examples for common conflict and fallback cases.

It does not:

- run conflict detection;
- decide governance outcomes;
- mutate source records;
- mutate replay;
- approve implementation;
- authorize execution;
- create new discovery workflows outside the existing G6-05 policy.

## 4. Conflict Taxonomy

Canonical conflict classes:

| Conflict Class | Description | Default Handling |
| --- | --- | --- |
| `source_identity_conflict` | Two source records claim the same deterministic identifier for different sources. | Fail closed; route to canonicalization review or Governance if authoritative. |
| `source_status_conflict` | Source status differs across records or projections. | Fail closed for readiness claims; preserve both statuses. |
| `certification_conflict` | Final verdict, certification scope, or inheritance claim conflicts. | Fail closed; route to Governance. |
| `ownership_conflict` | Multiple sources claim incompatible owners for the same capability or artifact. | Fail closed; route to Governance or certified owner review. |
| `public_api_conflict` | Public API mapping conflicts with certified contract or successor contract. | Mark stale or conflict; route to public API owner and Governance if certified. |
| `runtime_entrypoint_conflict` | Runtime entrypoint mapping conflicts with source contract or behavior evidence. | Mark conflict; do not invoke; route to owner review. |
| `replay_evidence_conflict` | Replay mapping conflicts with replay artifact, replay function, hash, ordering, or reconstruction behavior. | Fail closed; Replay remains authority. |
| `lineage_conflict` | Predecessor, successor, gap, implementation, validation, or verdict lineage conflicts. | Preserve both links; route to Governance lineage review. |
| `stale_source_conflict` | Source has been superseded but still appears as current. | Mark stale; require successor review. |
| `missing_evidence_conflict` | Required evidence is absent but a projection claims readiness. | Fail closed; mark missing. |
| `scope_conflict` | Domain-scoped, partial, or advisory evidence is presented as full platform readiness. | Fail closed; preserve scope limitation. |
| `authority_boundary_conflict` | A record or projection implies authority it does not own. | Fail closed; route to Governance. |

## 5. Fail-Closed Rules

All conflicts default to fail-closed behavior.

Fail-closed means:

1. Do not infer missing evidence.
2. Do not merge conflicting records automatically.
3. Do not promote partial evidence to certified readiness.
4. Do not invoke runtime behavior based on conflicting mappings.
5. Do not approve, authorize, dispatch, mutate, or deploy.
6. Preserve all conflicting source references.
7. Mark the affected record, manifest, projection, mapping, or lineage link as `conflict`.
8. Route the issue to the existing authority owner.
9. Use manual capability discovery only as a bounded fallback when deterministic records cannot answer safely.

Fail-closed status values should use the G7-02 vocabulary:

- `conflict`;
- `missing`;
- `stale`;
- `partial`;
- `blocked`;
- `certification_required`;
- `canonicalization_required`.

## 6. Stale Evidence Handling

Evidence is stale when a newer certified source, successor milestone, public API contract, runtime mapping, replay contract, or governance verdict supersedes it.

Stale evidence rules:

| Rule | Requirement |
| --- | --- |
| Preserve stale source | Do not delete or hide stale source records. |
| Mark stale status | Use `stale` in manifest, projection, mapping, or lineage records. |
| Require successor reference | Cite successor source when known. |
| Block readiness claims | Stale evidence cannot support current readiness unless explicitly reaffirmed. |
| Preserve history | Stale does not mean invalid; it means not current without review. |
| Route review | Governance review is required when stale evidence affects certification or ownership. |

Manual discovery may be used to locate successor sources when the successor link is missing.

## 7. Missing Replay Handling

Replay remains the runtime evidence reconstruction authority.

Missing replay rules:

| Case | Handling |
| --- | --- |
| Runtime behavior claims replay evidence but no replay reference exists | Mark `missing`; fail closed for runtime-readiness claims. |
| Documentation-only source has no replay evidence | Mark `documentation_only`; do not treat as runtime-enforced. |
| Replay function is named but artifact is missing | Mark `missing`; route to Replay owner or runtime owner. |
| Replay hash or ordering conflict exists | Mark `conflict`; Replay remains authority. |
| Projection consumes replay reference that is stale | Mark `stale`; require review before use. |

Missing replay must not be inferred from logs, prose, or source names.

## 8. Ownership Conflict Rules

Ownership conflicts occur when capability, runtime, replay, public API, governance, provider, Worker, or adapter ownership is ambiguous or contradictory.

Ownership conflict rules:

1. Preserve each ownership source.
2. Do not transfer ownership through a mapping or projection.
3. Prefer constitutional and certified architecture sources over convenience mappings.
4. Treat adapter ownership as capture/rendering only unless a certified source says otherwise.
5. Treat Replay as evidence reconstruction authority only.
6. Treat Governance as certification and admissibility authority.
7. Treat runtime registries as metadata sources unless certified selection policy says otherwise.
8. Route unresolved ownership conflicts to Governance.

If a mapping record implies ownership transfer, mark `authority_boundary_conflict`.

## 9. Certification Conflict Rules

Certification conflicts occur when final verdicts, certification scope, inheritance, or limitations disagree.

Certification conflict rules:

- preserve exact final verdict text from all sources;
- never synthesize a new final verdict;
- do not inherit certification unless explicit source evidence allows it;
- preserve known gaps and limitations;
- mark conflicting certification records as `certification_conflict`;
- route certification conflict to Governance;
- block any projection from claiming certified readiness until conflict is resolved.

## 10. Capability Discovery Fallback Policy

G6-05 remains mandatory as a current development policy, but G6-06 classified routine manual discovery as temporary methodology.

Generation 7 therefore defines manual capability discovery as a fallback path, not the desired long-term path.

### 10.1 Fallback Triggers

Manual capability discovery is allowed when deterministic canonical records are:

| Trigger | Description |
| --- | --- |
| `missing_record` | No source record, mapping, manifest, or projection exists for the capability. |
| `stale_record` | Existing record may be superseded and successor link is absent or incomplete. |
| `conflicting_record` | Existing records conflict and cannot be safely consumed. |
| `uncertified_record` | Existing evidence is not certified for the proposed use. |
| `partial_scope` | Evidence applies only to a narrower domain or capability. |
| `missing_replay` | Runtime evidence is claimed but replay reference is absent. |
| `unknown_owner` | Canonical owner cannot be determined from existing records. |
| `new_capability_claim` | Proposal claims a genuinely new capability. |

### 10.2 Fallback Workflow

Fallback must follow G6-05:

1. State the requested capability in neutral Platform Core terms.
2. Search governance artifacts and final verdicts.
3. Search runtime modules, tests, public API docs, replay contracts, and registries.
4. Identify existing owners.
5. Map found evidence to source records, mappings, replay references, and governance status.
6. Classify as reuse unchanged, canonicalization, extension, facade, or genuinely new implementation.
7. Document duplication risk, governance impact, replay impact, and known gaps.
8. Feed the discovery result back into canonical source, mapping, lineage, or conflict records.

Fallback must not bypass deterministic canonicalization. It exists to repair or extend the canonical record set.

### 10.3 Fallback Retirement Criteria

Routine manual discovery can be retired for a capability when:

- a source record exists;
- a mapping record exists where applicable;
- ownership is unambiguous;
- replay evidence is present or explicitly not applicable;
- certification status is explicit;
- known gaps are visible;
- stale and successor relationships are resolved;
- PGSP projection lookup can consume the record safely.

Manual discovery remains available only for missing, stale, conflicting, partial, or uncertified evidence.

## 11. Governance Routing

Conflict routing:

| Conflict Type | Route To |
| --- | --- |
| Certification conflict | Governance. |
| Ownership conflict | Governance and certified owner review. |
| Replay evidence conflict | Replay owner, with Governance visibility. |
| Public API conflict | Public API owner and Governance if certified status is affected. |
| Runtime entrypoint conflict | Runtime owner and Governance if authority boundary is affected. |
| Source identity conflict | Canonicalization review; Governance if authoritative source is affected. |
| Lineage conflict | Governance lineage review. |
| Missing evidence | Canonicalization owner or relevant Platform Core owner. |
| Stale evidence | Successor source owner and Governance when certification is affected. |

Routing does not decide the outcome. It identifies the existing authority that must review.

## 12. Replay Implications

Replay implications:

- missing replay remains explicit;
- replay conflicts fail closed;
- projection and mapping records must cite Replay rather than duplicate it;
- runtime-produced conflict or fallback evidence should be replay-visible if later tooling exists;
- documentation-only fallback reviews remain source-visible;
- replay absence cannot be treated as proof of non-existence;
- replay presence cannot certify governance meaning by itself.

This package does not implement replay validation or replay reconstruction.

## 13. Governance Implications

Governance implications:

- Governance remains certification and admissibility authority;
- conflict policy prevents certification inflation;
- fallback policy preserves reuse-before-redesign while deterministic memory is incomplete;
- unresolved conflicts block readiness claims;
- manual discovery outputs should become canonical source or lineage records when certified;
- no conflict record may approve, authorize, execute, or mutate.

This package supports Governance. It does not replace Governance.

## 14. Examples

### 14.1 Missing Replay Example

```yaml
conflict_id: replay:conflict:g7_04:missing_pgsp_runtime_replay_reference_example
conflict_class: missing_evidence_conflict
affected_record: pgsp:mapping:runtime_entrypoint:example_runtime_entrypoint
status: missing
evidence_problem: Runtime-readiness claim lacks replay evidence mapping.
fail_closed_action:
  - Do not claim runtime-enforced readiness.
  - Keep documentation-only status visible.
  - Route to Replay owner or runtime owner for evidence review.
fallback_allowed: true
fallback_trigger: missing_replay
governance_route: Governance visibility required if certification claim is affected.
replay_route: Replay owner review required before runtime-readiness projection.
```

### 14.2 Ownership Conflict Example

```yaml
conflict_id: governance:conflict:g7_04:adapter_semantic_ownership_example
conflict_class: ownership_conflict
affected_records:
  - source:pgsp:public_api_contract:g4_10:g4_10_pgsp_public_api_documentation_and_adapter_contract_v1
  - mapping:adapter:mapping:ownership:example_adapter_semantic_claim
status: conflict
evidence_problem: Adapter mapping implies semantic interpretation ownership.
fail_closed_action:
  - Preserve both records.
  - Do not transfer UBTR ownership to adapter.
  - Mark adapter mapping as authority_boundary_conflict.
fallback_allowed: false
governance_route: Governance review required.
correct_owner_hint: UBTR remains semantic translation authority.
```

### 14.3 Stale Public API Example

```yaml
conflict_id: pgsp:conflict:g7_04:stale_public_api_reference_example
conflict_class: stale_source_conflict
affected_record: pgsp:mapping:public_api:legacy_session_entrypoint_example
status: stale
evidence_problem: Mapping references a legacy public API after a successor contract exists.
fail_closed_action:
  - Do not use stale mapping for current adapter integration.
  - Cite successor contract if known.
  - Require public API owner review if successor is unknown.
fallback_allowed: true
fallback_trigger: stale_record
governance_route: Governance review only if certification state changes.
```

### 14.4 Discovery Fallback Example

```yaml
fallback_id: platform:fallback:g7_04:unknown_capability_lookup_example
requested_capability: governed provider replacement through natural language
fallback_trigger: missing_record
reason: No canonical capability mapping record found in current Generation 7 indexes.
required_workflow:
  - Search governance artifacts and final verdicts.
  - Search public API docs and runtime entrypoints.
  - Search replay references and ownership mappings.
  - Classify result as reuse, canonicalization, extension, facade, or new implementation.
output_requirement:
  - Create or update source, mapping, lineage, or conflict records.
authority_boundary:
  - no_governance_authority
  - no_replay_authority
  - no_runtime_authority
  - no_execution_authority
```

## 15. Validation Strategy

Required validation for this documentation-first package:

```text
git diff --check
```

Validation status: passed.

Validation result:

```text
git diff --check
```

Result: clean.

## 16. Completion Criteria

This package is complete when:

- conflict taxonomy is defined;
- fail-closed rules are defined;
- stale evidence handling is defined;
- missing replay handling is defined;
- ownership conflict rules are defined;
- certification conflict rules are defined;
- capability discovery fallback triggers are defined;
- fallback workflow and retirement criteria are defined;
- governance routing is defined;
- replay and governance implications preserve existing authorities;
- examples cover missing replay, ownership conflict, stale API evidence, and fallback discovery;
- `git diff --check` passes.

Completion status: complete.

## 17. Remaining Gaps

Remaining Generation 7 work:

- PGSP projection lookup contract;
- Generation 7 canonicalization certification review.

Known limitation:

- This package defines deterministic policy only. It does not implement automated conflict detection, fallback execution, runtime lookup, or machine-readable conflict records.

## 18. Final Determination

The fourth optimized Generation 7 canonicalization package is implemented.

It reuses existing certified Platform Core assets, defines deterministic fail-closed conflict handling and capability discovery fallback policy, and preserves all existing authority boundaries.

Final verdict: FOURTH_GENERATION_7_CANONICALIZATION_PACKAGE_IMPLEMENTED
