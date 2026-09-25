# Project Services P1 Source-Claim Admission Contract V1

Status: IMPLEMENTED_AND_AUTHENTICATED under STEP78CH — NOT CERTIFIED

Contract ID: PROJECT_SERVICES_P1_SOURCE_CLAIM_ADMISSION_CONTRACT_V1

Contract version: 1

Owner: Platform Core Project Services, under G14-08A and G14-47.

Design source: STEP78CD Human-authorized minimum P1 formalization, P1-R01–P1-R12, C1–C9 and P1F1–P1F12/F1–F13. This artifact persists that design for STEP78CE. It does not certify it.

Authority effect: only the Human-authorized D1 design scope. Admission creates no certification, authority, reuse approval, execution permission, novelty proof or project capability gap proof.

## P1-R01 — Strict envelope and admission input

P1_ADMISSION_INPUT is a closed JSON object with exactly:

- schema_version: PROJECT_SERVICES_P1_SOURCE_CLAIM_ADMISSION_CONTRACT_V1;
- subject_identity: SubjectIdentity;
- source_claims: nonempty array of SourceClaim;
- admission_context: AdmissionContext.

Every defined object is closed. Unknown keys, duplicate JSON keys, missing required keys, wrong types and unsupported versions fail closed. JSON numbers must be finite. No Boolean/string/null coercion is permitted.

AdmissionContext has exactly repository_checkpoint (lowercase 40-hex Git commit), baseline_id (nonempty string or null), and owner_context (null or an object containing existing cdd_classification and evidence_snapshot representations). The checkpoint must resolve in the existing service-owned checkout. Payloads cannot select a filesystem root. Owner context is required only for owner assertions and is not a trusted=true flag.

Producer: source adapter or existing governed caller. Consumer: P1 admission helper inside Project Services. P1 creates no producer, watcher or update loop.

## P1-R02 — Identity

SubjectIdentity has exactly subject_id (nonempty string), raw_subject_ids (nonempty sorted unique string array), and identity_evidence (nonempty SourceReference array).

SourceReference has exactly path (repository-relative POSIX path), content_hash (sha256: followed by 64 lowercase hexadecimal digits), and pointer (JSON Pointer or null).

Retain every raw identity. An audit subject may use the existing CAPABILITY:: locator supported by its normalization record and rules. Automatic version/suffix collapse is grouping evidence only. Different raw subjects may share an admitted identity only through an explicit source identity/alias relationship. Collision or unsupported collapse blocks the merged candidate. G47-backed claims retain their exact G47 subject_id; they are not automatically equated with audit locators. Candidate identity does not establish certification-subject equivalence.

## P1-R03 — Exact source-claim fields

All twelve fields are required exactly once:

| Field | Type and rule |
|---|---|
| claim_subject_id | Nonempty string equal to admitted subject_id |
| claim_type | DEVELOPMENT_STATE or REALIZATION_COMPLETENESS |
| claim_value | Exact permitted string for its type and source |
| source_owner | Closed object with id and authority_reference; both null for unestablished observation ownership; both nonempty strings for owner assertions |
| source_artifact | SourceReference, exact file/hash/selector |
| source_version_or_digest | String exactly equal to source_artifact.content_hash |
| source_scope | Nonempty sorted unique string array; exact source-record scope or G47 declared responsibilities |
| source_authority_effect | Literal NONE |
| claim_mode | OBSERVATION or OWNER_ASSERTION |
| observed_or_asserted_at | Source-established UTC RFC3339 timestamp or null; no fabricated timestamp |
| currentness_status | Input UNKNOWN; derived output CURRENT, STALE or UNKNOWN |
| invalidation_status | Input UNKNOWN; derived output INVALID, UNKNOWN or NOT_ESTABLISHED |

source_owner.authority_reference is an evidence ID in the supplied existing G47 snapshot, not an arbitrary validator name, URL or authority declaration. These are nested extension fields; legacy candidates do not already contain them.

## P1-R04 — Minimum claim types and vocabulary

DEVELOPMENT_STATE admits IMPLEMENTED, PARTIAL or NOT_STARTED in OBSERVATION mode only. It is the exact source observation, not authoritative whole-capability state.

REALIZATION_COMPLETENESS admits COMPLETE, INCOMPLETE, UNKNOWN or NOT_APPLICABLE in OWNER_ASSERTION mode only. It reuses the existing G47 claim unchanged. No conversion between IMPLEMENTED/COMPLETE or PARTIAL/INCOMPLETE is permitted.

Implemented/missing scope stays in G47 implemented/residual responsibility evidence. Currentness is validation metadata. Supersession is existing evidence metadata. Dependency, blocker and continuation claims are excluded from this minimum contract. CERTIFIED is not a development-state value; certification remains separate C4 evidence.

## P1-R05 — Observation and owner validation

Observation: resolve exact source, validate bytes/hash and JSON source-record pointer, verify raw subject identity and exact status, restrict scope to that record. Owner fields remain null unless independently established; an owner name in an audit row is insufficient.

Owner assertion: validate the existing CDD classification, then invoke the public G47 evidence-snapshot validator using that CDD ID and baseline. Resolve authority_reference to exactly one item. Require exact equality of subject, canonical owner, source path/hash, claim type/value and declared scope. Accept only REALIZATION_COMPLETENESS and preserve its implemented/residual responsibility evidence. G47 rejection rejects owner admission; never silently downgrade it to observation.

This does not add G47 evidence types or relax its certification requirements. An uncertified subject unable to provide G47 evidence may still provide a valid observation. Self-asserted owner, authority, certification and currentness are not accepted.

## P1-R06 — Integrity, scope and currentness

Resolved paths must remain in the checkout. Reject absolute paths, traversal and symlink escape. No network fetch. Hash exact source bytes with SHA-256. Checkpoint binding is observation context, not semantic applicability.

CURRENT requires agreeing source bytes/checkpoint, valid identity and applicable baseline/lifecycle checks. STALE applies when source changed/disappeared/superseded or binding/scope/baseline became incompatible. UNKNOWN applies where required applicability/lifecycle information is unavailable.

For observations, CURRENT means the scoped source observation is current at the checked context; it proves no implementation completeness/certification/readiness. INVALID requires a detected invalidation. NOT_ESTABLISHED means no invalidation was established by performed checks, not universal validity.

Missing/mismatched bytes cannot create a newly validated claim. Previously admitted hash-bound claims may remain historical inspection evidence with revalidation required. Without prior evidence, fail closed. Revalidate on changed source/checkpoint, identity, scope, baseline, supersession, retirement, withdrawal or invalidation evidence.

## P1-R07 — Multiple claims

Deduplicate only byte-equivalent canonical validated bodies. Sort lexicographically by canonical serialization. Preserve distinct versions/provenance. Never choose by MAX(status), permissiveness or timestamp alone. Different values for the same subject/type and overlapping scope create ambiguity. Non-identical scopes potentially overlap unless existing evidence establishes disjointness.

Owner evidence outranks audit observation only within its owned scope. G47-rejected contradictory owner assertions remain rejection diagnostics, not admitted claims. Conflicting observations may coexist with ambiguity=true. No ambiguous set yields authoritative aggregate development state.

## P1-R08 — Validation order

Strict parse/version → identity/collision → source references → mode/owner → integrity → scoped currentness/invalidation → conflicts → canonical ordering/deduplication → inspection-only projection.

Structural errors, unsupported versions, invalid ownership and authority/certification assertions reject live admission. Historical evidence follows R06. No failure becomes legacy interpretation, no-match or absence.

## P1-R09 — D1 projection and persistence boundary

The existing candidate receives exactly this nested d1 extension:

- schema_version: PROJECT_SERVICES_CANDIDATE_D1_V1;
- disposition: INSPECTION_ONLY;
- source_claims: validated canonical claims;
- currentness: CURRENT, STALE or UNKNOWN;
- ambiguity: Boolean;
- revalidation_required: true.

Aggregate currentness is STALE if any claim is stale, otherwise UNKNOWN if any is unknown, otherwise CURRENT. It is inspection metadata only.

subject_id maps to capability_id and goal_target. Retain raw identities/evidence in the admission record alongside the candidate. certified_artifacts is empty. P1 populates no certification, owner-authority, reuse or gap-proof field. Selection never changes disposition.

Ingress is versioned d1_admission_inputs in the existing project_knowledge_index. Validate before projection. project_knowledge_index_model preserves this optional list/provenance through the existing workspace path, never certified_artifacts_by_target.

Return D1 records for inspection without semantic matching/recommendation scoring. Legacy ranking remains unchanged. A sole D1 candidate may be selected for inspection; multiple D1 candidates remain ambiguous. No new semantic selector. No database or automatic update producer.

## P1-R10 — Version, serialization and downgrade protection

Reuse canonical_serialize/replay_hash: sorted keys, compact separators, ASCII-safe JSON, UTF-8, SHA-256. Null is JSON null. Sort and exactly deduplicate claims and set-like evidence lists; reason codes are sorted unique strings. Generate no wall-clock validation timestamp.

Existing artifact hashes cover the extension and retained admission input. Legacy records without D1 remain unchanged. A parent admission list identifying a D1 candidate prevents interpreting that candidate as legacy after stripping its extension. Reject malformed/future live versions; do not rewrite historical bytes.

## P1-R11 — C4 PATH B

The Platform Knowledge response has d1_certification_binding with exactly:

- schema_version: PLATFORM_KNOWLEDGE_D1_CERTIFICATION_BINDING_V1;
- selected_subject_id;
- binding_status: UNBOUND;
- candidate_certification_state: UNKNOWN;
- lookup_result: independent registry result or null;
- reason_codes: sorted unique strings;
- revalidation_required: true.

P1 creates no certification-subject binding. Preserve independent lookup evidence. Flat fields cannot certify the selected D1 subject. No combined certified classification or registry-derived service recommendation. Legacy NOT_CERTIFIED behavior is unchanged for legacy-only calls. D1 no-match means applicability unknown, not absence.

## P1-R12 — Authority and malformed inputs

Admission authority effect is NONE. Malformed input, authority escalation and legacy downgrade fail closed. This includes unknown/missing/duplicate fields, wrong types, invalid digest/owner, inflated scope, unsupported versions, identity collisions and certification-as-development claims.

## C1–C9 consumer contract

| Consumer | Obligation |
|---|---|
| C1 discovery/selection | Validate admission; retain inspection; no NEW/EXTENDS from admission |
| C2 project knowledge | INSPECTION_REQUIRED, reuse false, new-work necessity unknown, no certified-family relation |
| C3 goal/objective | Preserve identity/provenance; inspection alone cannot enable implementation planning/runtime binding |
| C4 Platform Knowledge | R11 PATH B |
| C5 G20 | Inspection is not certified coverage or capability gap; existing failed-closed coverage for selected inspection target |
| C6 G63 | Existing proof requirements unchanged; unbound C4 cannot satisfy certified-target checks |
| C7 durable gap | Reject inspection-derived novelty/extension/gap; guard both fallback branches |
| C8 propagation | Preserve nested disposition/hash-bound provenance; stripping invalid |
| C9 G47 | No new evidence class/authority/validation semantics |

T1 requires applicable certified-relation proof; T2 exact scope proof; T3/T4 forbid novelty/gap from admission; T5 requires independent certification/G63/G47; T6 has no direct execution transition.

## Acceptance and requirement traceability

Fixtures are test recipes, not assertions of repository certification. Owner fixtures use existing G47 validators, never arbitrary trusted flags.

| Fixture / requirement | Input | Expected; forbidden | Target |
|---|---|---|---|
| P1F1 / R05 | Valid CDD/snapshot and exact realization claim | Owner claim retained; no certification promotion | Owner admission |
| P1F2 / R03–05 | Exact audit row/digest, observation | Observation; no owner promotion | Observation validation |
| P1F3 / R01 | Missing/wrong/duplicate/unknown key | Reject; no fallback | Parser |
| P1F4 / R06 | Changed bytes after prior admission | Historical stale/revalidation; not current | Integrity |
| P1F5 / R02 | Unsupported alias collision | Block merge | Identity |
| P1F6 / R07 | Conflicting overlapping observations | Both retained, ambiguous | Claim set |
| P1F7 / R06 | Unknown applicability | Unknown inspection; not absence/certification | Currentness |
| P1F8 / R09 | Development claim projected as certified artifact | Reject | Candidate validator |
| P1F9 / R10 | Future version | Reject live use | Version |
| P1F10 / R10 | Legacy input | Existing behavior unchanged | Regression |
| P1F11 / R07 | Exact duplicate then different source | Deduplicate first, retain second | Canonicalization |
| P1F12 / R09–12 | Valid claim set | Inspection-only, authority none | Projection |
| F1 | P1F2 | Discoverable without promotion | C1 |
| F2 | F1 plus independent certificate | Preserve both, UNBOUND | C4 |
| F3 | Empty certification references | Unknown, not proven NOT_CERTIFIED | C4 |
| F4 | Audit CERTIFIED | No development-state admission/certified reuse | P1/C4 |
| F5 | P1F4 | No current reuse | Currentness |
| F6 | P1F5 | No silent merge | C1 |
| F7 | Selected inspection | No certified-family relation | C2 |
| F8 | Inspection plus forged gap | No gap proof | C7 |
| F9 | Inspection/no certificate | No NEW_CAPABILITY | C1/C2 |
| F10 | Inspection/no scope proof | No EXTENDS_EXISTING | C1/C2 |
| F11 | Legacy certified fixture | Existing behavior unchanged | Legacy consumers |
| F12 | Inspection/unbound evidence | No G63/G47 bypass | C6/C9 |
| F13 | Future version/stripped disposition/partial envelope | No legacy fallback | Ingress/consumers |

Also require hash changes on extension changes; malformed/rehashed inconsistent artifacts rejected; independent certificate retained; flat fields consistent with UNBOUND; selection/propagation retain disposition.

## Exact implementation surface

- platform_core_project_services.py: P1 helpers; project_knowledge_index_model; discover_candidate_capabilities; project_knowledge_context_from_workspace; goal_mapping_from_workspace; resolve_development_intent; direct propagation/validation guards.
- platform_project_objective_inference.py: infer_platform_project_objective and validate_platform_project_objective inspection guards.
- platform_knowledge_runtime.py: query_platform_knowledge, validate_platform_knowledge_response and D1 classification/service guards.
- platform_implementation_turn_durable_work_binding.py: prepare_implementation_turn_capability_coverage, _bounded_project_capability_gap_evidence, both gap/extension projections and validating entries.
- platform_capability_composition_coverage.py: discovery and validation inspection guards.

No mutation of G47, G63, registry, normalization or serialization implementations.

Tests: test_project_services_p1_source_claim_admission_v1.py; test_g14_47_human_intent_to_capability_resolution_v1.py; test_g21_02_platform_project_objective_inference.py; test_g19_02_platform_knowledge_runtime.py; test_g31_04_canonical_implementation_turn_durable_work_binding.py; test_g20_03_platform_capability_composition_coverage.py. Existing G63 direct regressions are read/run-only targets. Under STEP78CH's ordinary CF-contract fixture-repair authorization, the G14-19 legacy send/approve fixture is corrected for the independently HEAD-reproduced G59 readiness mismatch; its real intent delegation checks remain. No G14/G59 authority changes are authorized.

## Existing authority references and exclusions

- docs/governance/G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1.md
- docs/governance/G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1.md
- docs/governance/PLATFORM_CORE_CAPABILITY_CONSTITUTION_V1.md
- aigol/runtime/constitutional_development_governance_orchestration.py
- aigol/runtime/transport/serialization.py
- governance/AIGOL_CAPABILITY_NORMALIZATION_RULES_V1.json

No D2 semantic query/ranking, D3 expanded proof gate, D4 refresh/producer, D5 graph traversal/continuation or D6 workflow enforcement. No new registry/database/map/identity/authority/discovery path, operational attempt, F0 continuation or E05 execution. Implementation tests do not constitute certification.
