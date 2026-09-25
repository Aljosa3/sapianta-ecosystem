# Project Services Structured Discovery Relevance Contract V1

Contract ID: PROJECT_SERVICES_STRUCTURED_DISCOVERY_RELEVANCE_V1.
Ruleset: SOURCE_BOUND_WHOLE_FIELD_RELEVANCE_V1.
Design authority: STEP78CJ minimum contract, explicitly authorized for implementation by STEP78CK.
Status: minimum implementation; acceptance and release evidence belongs to the STEP78CK G48 report. Not certified.

## Scope and existing path

Validated structured requirement -> governed whole-field comparison -> existing candidate-owned evidence -> traceable inspection relevance -> existing Project Services discovery artifact.

Only platform_core_project_services.py and platform_knowledge_runtime.py implement this binding. No new capability map, database, query registry, descriptor inventory or authority path. Legacy discovery remains unchanged when structured input is absent. In structured mode its keyword/profile matches are locator context only and never semantic evidence or relevance scores.

The existing G28 descriptor API supplies its unchanged five-adapter inventory. No G29 selection or invocation occurs. G47/G63 authority and all existing execution gates remain unchanged.

## Structured input

The existing discovery and Knowledge APIs accept optional structured_requirement_state, containing the full validated Semantic CWM state. A candidate projection alone is insufficient: it omits slot statuses/provenance. Keep the full source state, source-state digest, semantic revision, slot IDs, canonical values, statuses, completeness, provenance and dependencies in the requirement binding. Validate using the existing CWM validator.

Eligibility requires at least one complete ASSERTED or CONFIRMED operative subject, desired outcome or explicit output qualifier. Its dependencies must also be usable. Identifier hints alone are insufficient. Optional fields are not prerequisites merely to inspect. Invalid structure fails closed. Valid insufficient input returns QUERY_INSUFFICIENT and UNKNOWN_RELEVANCE assessments, not absence.

This evaluates a supplied requirement snapshot; it does not assert present-day Human intent, renew an expired conversation, create an Objective or synthesize confirmation. Non-active source state cannot produce an unqualified positive or negative relevance classification.

| Field | Existing source/type | Use |
|---|---|---|
| Action | OPERATIVE_ACTION/PRIMARY, canonical text | Whole-field action relation |
| Subject | OPERATIVE_SUBJECT/PRIMARY, canonical text | Semantic anchor |
| Desired outcomes | DESIRED_OUTCOME primary/secondary text | Preserve each requested outcome |
| Work type | WORK_TYPE closed enum | Bounded descriptor compatibility |
| Scope | SEMANTIC_REFERENCE/SCOPE, exact reference string | Preserve; no operational containment inference |
| Constraints | GOVERNING_QUALIFIER clauses | Preserve role/materiality/status; no free-text solver |
| Capability/reuse hints | SEMANTIC_REFERENCE/CAPABILITY_HINT | Locator only, never positive semantic evidence |
| Required effects | Explicit desired outcomes and OUTPUT qualifiers | Requested outputs only; no inferred effects |

Do not require planning or execution readiness for inspection. Missing required comparisons remain UNKNOWN; stale/conflicted/partial values are not usable positive inputs. Unresolved dependencies and explicit conflicts remain visible.

## Candidate evidence

| Source | Identity/owner/scope | Allowed use |
|---|---|---|
| D1 observation | Existing candidate/claim hash, source path/digest/selector; observation owner unestablished | Identity/development/currentness context only |
| D1 G47 owner assertion | Existing validated CDD/snapshot, evidence ID, canonical owner, source digest and declared responsibilities | Exact subject-to-declared-responsibility relation only |
| G28 descriptor | Existing descriptor hash, exact registry identity, Platform Core owner, unchanged adapter scope | Declared actions, subjects, expected outcomes, exclusions and work types |
| Certification record | Existing registry identity/hash/owner/scope | Independent metadata, never relevance by certification alone |
| G63 signature/usage/equivalence context | Existing signature/proof and candidate/source bindings | Preserve through existing context; structural validity alone supplies no new positive relation |
| Legacy catalog/workspace result | Existing discovery provenance | Locator context only |

A locator is not semantic evidence. A hash is not ownership proof. G47 assertions pass existing P1/G47 validation. Descriptor declarations are obtained from the existing owner API and rebound during validation. Join descriptors only on exact candidate identity. Unsupported aliases/version-like names remain distinct. Ambiguous duplicate identities reject rather than silently merge.

Candidates lacking semantic evidence remain visible as UNKNOWN_RELEVANCE. The descriptor inventory is neither extended nor persisted elsewhere. Existing candidate bodies, especially immutable P1 bodies, are not annotated or rewritten with relevance.

## Exact field outcomes

Outcomes: MATCH, CONTRADICTION, UNKNOWN, NOT_APPLICABLE.

Compare complete usable canonical field values as whole strings, without new lowercasing, substring matching, stemming, synonyms, embeddings or LLM relations.

| Field | MATCH | CONTRADICTION | Otherwise |
|---|---|---|---|
| Action | Exact supported_actions member | Exact applicable excluded_meanings member | UNKNOWN |
| Subject | Exact supported_subjects member or validated declared responsibility | Exact applicable exclusion | UNKNOWN |
| Outcome/output | Exact expected_outcomes member | Exact applicable exclusion | UNKNOWN |
| Work type | Exact supported_work_types member | Supplied enum outside that bounded supported set | UNKNOWN without descriptor evidence |
| Supplied operational scope | No comparator admitted in V1 | No inequality-based inference | SCOPE_UNKNOWN |
| Supplied unsupported free-text constraint | No general comparator admitted | Preserve explicit source conflict, do not infer negation | UNKNOWN |
| Required-effect coverage | Each requested output has its own supported relation | Applicable explicit exclusion | Partial/unestablished coverage remains UNKNOWN |
| Hint/evidence locator | Never semantic support | Never identifier-derived semantic rejection | NOT_APPLICABLE to semantic comparison; preserve diagnostics |

Absent optional scope/constraint is NOT_APPLICABLE. Unsupported supplied fields are UNKNOWN, never NOT_APPLICABLE. Missing action/subject/primary-outcome/work-type comparison is UNKNOWN. Nonmembership in descriptive action/subject/outcome lists is not contradiction. Work type uses the existing bounded compatibility exception.

Minimum semantic anchor: a source-bound subject/responsibility or outcome/output relation beyond identity. Action/work-type matching alone is insufficient. Match traces cite only the particular claim/descriptor supporting the relation.

## Scope, conflicts and composition

D1 source-record scope, G47 baseline scope and certification scope are distinct from operational scope. V1 never emits operational SCOPE_MATCH, SCOPE_SUBSUMPTION or SCOPE_CONFLICT without an authenticated typed relation; none is introduced here. Supplied operational scope is SCOPE_UNKNOWN and blocks unqualified positive relevance. Absent operational scope is NOT_APPLICABLE. Same words cannot silently broaden scope.

Composition:

1. Malformed evidence: fail closed.
2. Conflicting evidence: preserve it; no definitive positive/negative promotion.
3. Established contradiction, with current evidence and no unresolved conflict: NOT_RELEVANT_WITHIN_PROVEN_SCOPE, limited to the evidenced field/descriptor scope.
4. Semantic anchor, all required comparisons MATCH, current evidence, and no unresolved supplied qualifier/ambiguity: RELEVANT_FOR_INSPECTION.
5. Semantic anchor with partial, stale, unknown-currentness or ambiguous support: POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION.
6. No anchor and no established applicable contradiction: UNKNOWN_RELEVANCE.

QUERY_INSUFFICIENT always yields UNKNOWN_RELEVANCE. Historical or unknown-currentness contradictions cannot become definitive current negative findings. Conflicting aliases, candidate claims, requirement meanings and constraints remain explicit. No LLM preference breaks a tie.

These outcomes do not establish satisfaction, capability absence, certified reuse, NEW_CAPABILITY, EXTENDS_EXISTING_CAPABILITY, PROJECT_CAPABILITY_GAP, planning eligibility or execution authority.

## Currentness and historical evidence

CURRENT permits only the bounded comparisons above. STALE/UNKNOWN can support at most possibly relevant inspection. Source-state non-active status also blocks an unqualified result. No wall-clock timestamp is generated by comparison.

Changed/unverifiable live P1 evidence fails closed. Optional prior_d1_candidates reuses P1's existing prior_candidate admission mechanism for explicit historical inspection; the parent admission inputs, original prior bodies and resulting historical candidates remain hash-bound. It is not a source refresh producer. Identity-evidence changes still reject. A stale positive descriptor association cannot make a stale D1 candidate current.

Revalidation is always required on consumption and on changed source/requirement/revision/identity/baseline/lifecycle evidence. Reconstruct comparisons from owner-validated inputs, not from a self-reported classification or a newly recomputed output hash.

## Result extension and ordering

Extend the existing Project Services discovery artifact with structured_relevance:

- schema_version; ruleset_version;
- requirement_binding: full validated source state and digest/revision, usable slots, eligibility, workspace snapshot, original discovery options and any prior D1 candidates;
- query_eligibility;
- candidate_assessments;
- ordered_candidate_keys;
- ambiguity; sorted unique reason_codes;
- inspection_only=true; authority_effect=NONE;
- relevance_binding_hash.

Each assessment carries candidate identity/hash/key, slot-bound comparison outcomes, exact source/owner evidence identities and digests, scope/currentness, ambiguity, reasons, revalidation_required=true and authority_effect=NONE.

Keep all parent d1_admission_inputs, original D1 candidate bodies and dispositions, unknown/unmatched candidates, and independent certification evidence. Structured mode sets INSPECTION_REQUIRED and selected_candidate_capability=null. No capability is automatically selected or invoked.

Group order: RELEVANT_FOR_INSPECTION; POSSIBLY_RELEVANT_REQUIRES_CLARIFICATION; UNKNOWN_RELEVANCE; NOT_RELEVANT_WITHIN_PROVEN_SCOPE. Within groups sort by exact candidate identity and evidence-bound candidate key. This is presentation ordering only. Multiple supported candidates keep ambiguity visible.

Use canonical_serialize/replay_hash for rule/version, source-state/revision/digest, candidate identities, evidence identities/digests, field results, scope/currentness, reasons and ordering. Parent discovery and Knowledge hashes cover the extension. Validation rebuilds the complete discovery from bound source inputs and current evidence. Rehashed forged comparisons and copied candidate bodies inconsistent with their bound parent reject. Standalone structured candidates cannot lose their comparison binding and fall back to legacy interpretation.

## Consumer and authority boundaries

Platform Knowledge composes the existing discovery result and preserves its structured extension through the existing inspection-discovery field. The existing C4 binding stays UNBOUND/UNKNOWN, with no automatically selected subject; independent registry lookup remains separate. Flat certification/reuse/service fields cannot promote relevance. No certification-subject binding resolver is added.

The shared inspection guard validates structured parents and exact candidate-list projections carried by existing consumers. Existing objective, G20 and durable binding/gap guards continue to reject inspection-derived authority. G63/G47 remain unchanged.

LLM role: clarification proposals and explanations of UNKNOWN only. LLM_AUTHORITY_EFFECT=NONE. G20_AUTHORITY_CHANGE=NO. G63_AUTHORITY_CHANGE=NO. G47_AUTHORITY_CHANGE=NO.

No D3-D6, mandatory workflow discovery, scope algebra, refresh loop, operational attempt, F0 continuation or E05 execution. The abstract F0 effects query is supported within declared evidence; general operational-scope compatibility and actual F0 coverage are not established.

## Acceptance fixtures and implementation surface

D2F1 identical state/evidence gives identical result/hash; D2F2 changed requirement gives changed binding; D2F3 exact declared effects find a candidate without its internal name; D2F4 explicit excluded outcome blocks positive relevance; D2F5 unsupported scope/constraints remain unknown; D2F6 observations alone are not semantic proof; D2F7 historical evidence is visible and revalidated; D2F8 conflicts/ambiguity survive; D2F9 independent certification stays UNBOUND; D2F10 no NEW/EXTENDS/GAP; D2F11 no planning/execution authority; D2F12 parent provenance and candidate bodies survive; D2F13 unsupported aliases do not join; D2F14 equal real owner responsibility matches remain multiple and ordered; D2F15 malformed, future and rehashed forged data reject.

Production: platform_core_project_services.py (query/evidence/comparison/validation helpers, discover_candidate_capabilities, shared inspection guard and knowledge projection validation order); platform_knowledge_runtime.py (optional structured/prior input transport through existing composition). No third production file.

Tests: test_project_services_structured_discovery_relevance_v1.py; existing P1, G19-02, G14-47, G21-02, G20-03, G31-04 and both G63 direct suites. All existing validators remain real. Test-local owner/source fixtures do not manufacture production certification.
