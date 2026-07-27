# G35-05 Canonical Governed Development Condensation Contract Specification

Status: SPECIFIED — NO RUNTIME IMPLEMENTATION  
Version: 1.0.0  
Authority: Governed Development Intake / Project Objective boundary  
Dependencies: completed governed-development objective; G31 bounded CODEX synthesis preflight  
Scope: constitutional input preparation only

## 1. Purpose

This specification defines the minimum constitutional contract for producing a
bounded, reviewable synthesis input from a completed human governed-development
dialogue. It addresses `BOUNDED_SYNTHESIS_INPUT_CAPABILITY_GAP` without
changing the existing G31 CODEX synthesis preflight contract.

The contract introduces no execution authority. It does not authorize a Worker,
change the selected Worker, modify a request, alter Replay history, or change
the current 240 Unicode-code-point bound. Its future purpose is limited to
making a proposed bounded input reviewable and verifiable before that existing
bound is applied.

The existing G31 preflight remains authoritative for admission. A condensation
artifact is not a preflight result and cannot make an over-bound, invalid, or
unapproved request eligible.

## 2. Scope and Non-Goals

### 2.1 In scope

This specification defines:

- an immutable canonical condensation artifact;
- source-lineage and semantic-fidelity requirements;
- deterministic validation and human-review requirements;
- a bounded synthesis-request projection for existing G31 preflight; and
- required Replay-visible evidence and fail-closed outcomes.

### 2.2 Explicit non-goals

This specification does not:

- implement condensation, summarization, or an LLM integration;
- change the canonical prefix, the 240-code-point maximum, or G31 validation;
- permit truncation, paraphrase-by-assertion, silent omission, or substitution;
- grant approval, authorization, assignment, dispatch, Provider, Worker, or
  repository-mutation authority;
- replace the original request or alter clarification evidence; or
- alter the certified Platform Core baseline, Validator, Replay, Governance,
  Certification, or external-adapter architecture.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Original request | Immutable human request at governed-development intake; primary intent authority. |
| Clarification evidence | Immutable questions and answers bound to the original request; it explains but never overwrites that request. |
| Completed objective | Resolved governed-development objective derived from source lineage; primary operational source. |
| Condensation | A proposed bounded representation retaining all material requirements; it is not ordinary summarization. |
| Condensation artifact | Immutable artifact defined here, containing structured retained semantics, lineage, and a proposed synthesis body. |
| Review envelope | Human-visible comparison record containing source, proposal, validation, and approval or rejection. |
| Bounded synthesis request | Exact string submitted to G31: `runtime validation: <approved synthesis body>`. |
| Material requirement | A capability, outcome, permission, prohibition, placement, acceptance condition, validation requirement, exclusion, or safety/governance constraint whose loss can change approved work. |

## 4. Authority and Ownership

### 4.1 Authoritative source

The immutable original human request, bound to completed clarification lineage,
is the authoritative intent source. The completed governed-development objective
is authoritative operational evidence only when traceably bound to that source.

Neither a condensation artifact nor a synthesis request replaces the original
request. A condensation artifact may be used as a G31 input only after a human
approves a review envelope displaying both source evidence and the exact
condensed representation.

### 4.2 Ownership model

| Responsibility | Owner | May | Must not |
| --- | --- | --- | --- |
| Original request and clarification | Existing human-intent/governed-development owners | Record and resolve human input | Be replaced by condensation |
| Completed objective | Existing objective owner | State resolved operational objective | Authorize a Worker merely by existing |
| Condensation proposal | Future Condensation owner | Produce non-authoritative immutable proposal | Approve itself, execute, or mutate sources |
| Condensation validation | Future deterministic validator | Verify structure, lineage, fidelity, and bound | Infer missing intent, repair ambiguity, or authorize |
| Human review | Human Authority | Approve/reject exact review envelope | Approve unseen or substituted content |
| Replay | Existing Platform Replay owner | Record/reconstruct evidence | Condense or authorize |
| G31 preflight | Existing G31 owner | Validate exact final request | Trust an unapproved proposal |
| CODEX Worker | Existing Worker owner | Consume separately authorized handoff | Condense, approve, or reinterpret source intent |

### 4.3 Placement

The component belongs at the **Governed Development Intake / Project Objective
completion boundary**, after clarification is complete and before CODEX
synthesis preparation. It does not belong in the Human Interaction Layer,
which is transport-only; the CODEX Worker, which cannot transform its own
authority source; or existing preflight, which must remain a deterministic
verification gate.

## 5. Lifecycle

```text
Immutable human request + clarification evidence + completed objective
                              |
                              v
            Canonical Condensation Proposal (non-authoritative)
                              |
                              v
       Deterministic Condensation Validation (read-only, fail closed)
                              |
                              v
Human Review Envelope: source comparison + proposal + validation result
                              |
                  human approves exact hashes
                              v
            Approved Bounded Synthesis Request Projection
                              |
                              v
               Existing G31 synthesis preflight (unchanged)
                              |
                              v
                    Existing CODEX synthesis lifecycle
```

Every transition is one-way. Rejection, missing evidence, or failed validation
terminates the lifecycle without creating Worker, Provider, authorization, or
repository-mutation authority.

## 6. Canonical Condensation Artifact

### 6.1 Identity

The artifact type is
`CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_ARTIFACT_V1`.

Its fixed identity fields are:

```text
schema_id: CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_SCHEMA_V1
schema_version: 1.0.0
artifact_version: 1.0.0
creation_authority: GOVERNED_DEVELOPMENT_CONDENSATION_OWNER
validation_authority: DETERMINISTIC_GOVERNED_DEVELOPMENT_CONDENSATION_VALIDATOR
authority_effect: NONE
```

`condensation_id` MUST be deterministically derived from the canonical,
hash-excluded serialization. `condensation_hash` MUST be the SHA-256 canonical
hash of that serialization. Any changed field produces a new identity and hash.
Mutable registry resolution and timestamps as identity inputs are prohibited.

### 6.2 Required logical schema

| Section | Mandatory fields |
| --- | --- |
| Artifact identity | type, schema ID/version, artifact version, deterministic ID, canonical hash, creation and validation authority, `authority_effect: NONE` |
| Source lineage | original-request ID/hash; ordered clarification question and answer IDs/hashes; completed-objective ID/hash; project/workspace ID/hash; applicable session, invocation, and chain IDs |
| Semantic commitments | requested capability; user-visible outcome; allowed/prohibited operations; architectural placement; acceptance conditions; testing/validation requirements; explicit exclusions; safety/governance constraints |
| Proposed body | `proposed_synthesis_body`, Unicode code-point count, canonical body hash |
| Requirement map | source requirement ID/hash, target semantic field, and exact condensed representation for each material requirement |
| Proposal method | `DETERMINISTIC_RULES`, `LLM_PROPOSAL_VALIDATED`, or a separately registered governed process, plus immutable method evidence |

Serialization MUST use UTF-8 canonical JSON, canonical key ordering, no
duplicate keys, explicit `null` where applicable, and a hash computed without
the hash field. Invocation and chain IDs are required when present in the source
lifecycle and otherwise MUST be explicit `null`; unbound free-form references
are prohibited.

## 7. Source Lineage and Semantic Fidelity

### 7.1 Lineage rule

The original request is primary intent evidence. Clarification questions and
answers are supporting evidence. The completed objective is the primary
operational source. Project/workspace identity and applicable session,
invocation, and chain IDs bind the artifact to one governed context.

The validator MUST verify every listed source hash against its authoritative
artifact and MUST verify that the completed objective itself is bound to the
original request and clarification evidence. A valid hash is insufficient if
the source belongs to another project, workspace, session, invocation, or
chain.

### 7.2 Material requirement preservation

Each semantic-commitment field is mandatory, non-empty, and MUST be represented
in the proposed synthesis body or by a deterministic reference syntax defined by
this schema. The requirement map MUST give every material requirement a source
identifier, source hash, target field, and exact condensed representation.

The validator MUST reject an unmapped material requirement, a contradictory
mapping, a weakened prohibition, a broadened permission, a changed target, a
changed acceptance condition, or unresolved ambiguity.

The compact representation may remove rhetorical wording and duplicated
phrasing only. It MUST NOT infer a requirement, resolve an ambiguity, substitute
a target, turn a prohibition into advice, or omit a material constraint to fit
the bound.

## 8. Proposal Method and Determinism

The canonical artifact and its validation result MUST be deterministic for an
identical selected proposal and source bundle. A proposal MAY be generated by:

1. deterministic rules only; or
2. an LLM or another bounded governed process only as a non-authoritative
   proposal producer.

An LLM proposal has no truth, approval, or execution authority. It MUST be
recorded as proposal-method evidence and pass deterministic schema, lineage,
hash, requirement-map, ambiguity, and bound validation. Deterministic validation
cannot claim semantic equivalence beyond the explicit mapping; human review is
therefore mandatory for every proposal method.

No proposal method may silently retry with changed semantics, use an unrecorded
external source, or discard a constraint to obtain a shorter result. An unknown
proposal method fails closed.

## 9. Human Review and Approval

The human approves a **review envelope containing both** the original,
clarification-aware source view and the complete condensation artifact.
Approval of the original request alone cannot approve an unseen representation.
Approval of the proposed body alone cannot establish source fidelity.

The review envelope MUST display:

- original-request ID/hash and readable text;
- clarification evidence IDs/hashes and resolved answers;
- completed-objective ID/hash;
- condensation ID, semantic commitments, requirement map, proposed body, and
  body length;
- deterministic validation result and validation hash;
- exact final bounded request, prefix, prefix length, final length, and bound;
- a visible material-difference report; an empty report MUST be explicit; and
- human decision, actor identity, time, approval scope, and all bound hashes.

Approval is valid only for one condensation hash, validation hash, source-bundle
hash, and final-request hash. Any changed source, proposal, validation, prefix,
length, or final request invalidates it. Rejection creates no fallback authority.

## 10. Bounded Synthesis Request Projection

The approved projection is exactly:

```text
runtime validation: <approved proposed_synthesis_body>
```

The prefix is the existing `CODEX_SYNTHESIS_PREFIX` value, `runtime
validation: `, and is exactly 20 Unicode code points. The final request MUST be
measured as Python/Unicode code points, matching the existing G31 contract:

```text
len(prefix + approved_proposed_synthesis_body) <= 240
```

The projection MUST retain the condensation and approval hashes in
Replay-visible evidence. It is the sole input forwarded to existing
`preflight_codex_worker_synthesis(...)` once a future G31 binding is certified.

The projection MUST NOT alter the prefix, truncate text (including by ellipsis
or byte slicing), omit a mapped requirement after approval, bypass preflight,
use another counting scheme, or replace the approved body with the original
request.

If the final request exceeds 240 code points, condensation validation and G31
preflight MUST both reject it. The second check is deliberate defence in depth;
the artifact never weakens G31 admission.

## 11. Deterministic Validation Contract

The validation artifact is
`CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_VALIDATION_RESULT_V1`.

It MUST have a deterministic ID and canonical hash and include the condensation
ID/hash, all source references/hashes, validation version, ordered failure
codes, final-request hash, body/final code-point counts, and these flags:

```text
read_only: true
approval_created: false
authorization_created: false
worker_assigned: false
worker_invoked: false
provider_invoked: false
repository_mutated: false
```

| Failure code | Fail-closed condition |
| --- | --- |
| `MISSING_SOURCE_LINEAGE` | Required source identity, artifact, or hash is absent. |
| `SOURCE_HASH_MISMATCH` | Source hash or project/workspace/session/invocation/chain binding is inconsistent. |
| `INCOMPLETE_CLARIFICATION` | Clarification is unresolved, contradictory, or required evidence is absent. |
| `INVALID_SCHEMA` | Artifact type, version, identity, serialization, or required field is invalid. |
| `MATERIAL_REQUIREMENT_UNMAPPED` | A material requirement has no complete mapping. |
| `MATERIAL_REQUIREMENT_LOSS` | A representation omits, weakens, broadens, or contradicts a source requirement. |
| `AMBIGUOUS_CONDENSED_OBJECTIVE` | The body or mapping retains unresolved material ambiguity. |
| `UNSUPPORTED_PROPOSAL_METHOD` | Proposal method or evidence is missing, unknown, or prohibited. |
| `EXCESSIVE_CANONICAL_REQUEST_LENGTH` | Prefixed final request exceeds 240 Unicode code points. |
| `REPLAY_IDENTITY_MISMATCH` | Artifact, validation, projection, or approval identity/hash cannot reconstruct. |
| `UNAPPROVED_CONDENSATION` | Approval is missing, rejected, stale, or binds another artifact. |
| `VALIDATOR_DISAGREEMENT` | Required deterministic validations have inconsistent canonical results. |

`PASS` permits human review only. It does not authorize G31, CODEX, a Worker, a
Provider, or mutation. A valid approval followed by a separate successful G31
preflight is still required for downstream eligibility.

## 12. Replay and Evidence Requirements

Replay must allow a later reviewer to prove exactly what was requested,
clarified, proposed, validated, approved, and submitted. The following records
MUST be immutable and Replay-visible in causal order:

1. original human request;
2. clarification question and answer exchange, or explicit no-clarification
   resolution evidence;
3. completed governed-development objective;
4. canonical condensation proposal artifact;
5. deterministic validation result;
6. human review envelope and approval or rejection;
7. approved bounded synthesis-request projection;
8. existing G31 preflight capture; and
9. existing synthesis/activation records, only if the existing lifecycle later
   proceeds.

Replay ownership remains with the existing Platform Replay owner. The
condensation owner may create proposal evidence but MUST NOT append, edit, or
reinterpret Replay history. Reconstruction MUST prove exact equality between
the approved projected request and the request measured by G31 preflight.

## 13. Invariants

1. The original human request remains immutable primary intent evidence.
2. Clarification binds to the original request and never replaces it.
3. The completed objective is traceable to the complete source lineage.
4. Condensation is non-authoritative until exact human approval.
5. Every material requirement is mapped, visible, and preserved.
6. No material requirement may be silently removed, weakened, broadened, or
   reinterpreted to meet a length target.
7. The current 20-code-point prefix and 240-code-point final-input limit remain
   unchanged.
8. Unicode-code-point counting is canonical; byte, token, display-width, and
   grapheme counting are not substitutes.
9. Existing G31 preflight remains final admission authority.
10. Condensation, validation, review, and projection create no execution or
    authorization authority.
11. Approval binds source, proposal, validation, and final-projection hashes.
12. Replay reconstruction detects substitution at every boundary.

## 14. Compatibility with Existing G31 Preflight

This contract is compatible with current G31 because it produces the same input
kind that G31 already accepts: one exact string prefixed with `runtime
validation: ` and no longer than 240 Unicode code points. It neither changes
G31 length calculation nor asks G31 to interpret semantic fidelity.

The current G31 implementation accepts and later reconstructs the exact
original request, so it cannot consume this artifact today. A future integration
therefore requires a new certified binding that supplies the **approved bounded
projection** where current runtime supplies the direct original-request input.
That binding MUST retain original-request evidence in surrounding lineage and
MUST NOT change G31 preflight's prefix, bound, hash verification, or fail-closed
behavior.

## 15. Required Constitutional Determinations

| Question | Determination |
| --- | --- |
| Authoritative source object | Immutable original request contextualized by its clarification lineage; completed objective is primary operational evidence. |
| Canonical artifact | `CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_ARTIFACT_V1`. |
| Human approval boundary | Review envelope containing source evidence, exact proposal, validation result, and final request. |
| Validation owner | New deterministic Condensation Validator with no execution authority. |
| Replay owner | Existing Platform Replay owner; no parallel Replay owner is created. |
| Exact G31 handoff | `runtime validation: <approved proposed_synthesis_body>` passed to unchanged G31 preflight. |
| Future runtime mutation | Yes. A separately authorized and certified binding is required because current runtime passes the original request directly. This specification makes no change. |
| Capability classification | New certified Canonical Governed Development Condensation capability, followed by a versioned revision of G31 input binding. It is neither configuration nor a revision of G31 preflight itself. |

## 16. Implementation-Readiness Verdict

`CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_CONTRACT_SPECIFIED_NOT_IMPLEMENTATION_READY`

The constitutional contract is sufficient to begin a separately authorized
design and implementation generation. It is not ready to mutate certified
runtime: that generation must identify the exact source-object schemas for the
chosen governed-development path, specify deterministic extraction and
comparison rules for material requirements, define the review artifact, and
certify the new G31 binding.

Until that work is independently authorized and certified, current behavior
remains correct: an oversized exact synthesis input fails closed before human
approval, Worker execution, Provider invocation, or repository mutation.
