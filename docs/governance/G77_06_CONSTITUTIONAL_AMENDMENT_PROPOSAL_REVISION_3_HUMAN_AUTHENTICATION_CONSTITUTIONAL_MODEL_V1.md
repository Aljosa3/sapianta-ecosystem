# 1. Implementation Summary

Generation: G77-06

Report and proposal identity:
G77_06_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1

Proposal revision: `3`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: G0 through G77-05. G77-04 is immutable Proposal
Revision 2. G77-05 is its sole authoritative G70-03 assessment and classifies
Revision 2 as `UNRESOLVED_CONSTITUTIONAL_IMPACT`. Every predecessor remains
closed and unchanged.

Authenticated repository identity:

- Commit: `c13b9c708afc65d8611dabd5386443665db0c8d3`
- Tree: `19ed1de107291583b6cffa42409bcc000df576bd`
- Subject: `G77-05: assess human authentication CAP proposal revision 2`
- Immediate parent: `b4f048d089fae9e881631b0f14c48ca0a8800fa8`
- Revision-start worktree state: clean
- Authenticated G77-04 SHA-256:
  `8136bbb3fa6c1d0c137656a6d6ed25b01b5c9fca7cc83df43b014193b2673cfe`
- Authenticated G77-05 SHA-256:
  `fae1f0e357bfd08eb784369da15487c2c8abe9f0ec0ee6d753a2b9263f03f96a`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G77_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1` |
| previous proposal revision | `2` |
| previous proposal digest | `sha256:8136bbb3fa6c1d0c137656a6d6ed25b01b5c9fca7cc83df43b014193b2673cfe` |
| previous proposal status | `PROPOSAL_ONLY_UNASSESSED` |
| authoritative assessment identity | `G77_05_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_REVISION_2_V1` |
| authoritative assessment digest | `sha256:fae1f0e357bfd08eb784369da15487c2c8abe9f0ec0ee6d753a2b9263f03f96a` |
| authoritative assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |

Constitutional Gap identity:
`G77_01_GATE_0B_PRODUCTION_HUMAN_AUTHENTICATION_NORM_ABSENT`

Target Constitutional artifact:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED`

Target Constitutional version: `V1`

Proposed successor identity:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_HUMAN_AUTHENTICATION_REVISION_3_PROPOSED`

Proposed successor version:
`V1.1-HUMAN-AUTHENTICATION-R3-PROPOSED`

Proposed Constitutional capability identity:
`CANONICAL_PRODUCTION_HUMAN_IDENTITY_AUTHENTICATION_MODEL_V1`

Proposed Constitutional owner:
`CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Invariants; Governance Enforcement Hierarchy; Governance
Lineage Model; G69-02 Canonical CHE Request; G69-03/G69-05 CHE Continuation,
owner transition, idempotency, and advancement; G69-07 Canonical Human
Authority Act; G69-11 CHE evidence correlation; G69-13 complete HIC
conformance; G69-18 Replay and CRO; G69-19 Production Cutover; G70-02
Constitutional Amendment Proposal; G70-03 Constitutional Impact Assessment;
G70-04 Human Ratification; G70-06 publication and activation; G70-07 CAP
Closure; G72-00 Constitutional Core Baseline; G73-00 Human Constitution;
G76-06 Constitutional Artifact Identity Model; G76-07 Release Decision
Proposal Revision 4; G77-01 Gate 0 classification; G77-02/G77-04 Human
Authentication Proposals; G77-03; and G77-05 authoritative Revision 2 Impact
Assessment.

Reporting date: 2026-08-07.

Objective:

Create only the exact Revision 3 successor of G77-04. Resolve every
`UNRESOLVED` and `PARTIALLY_RESOLVED` G77-05 finding concerning first-time
enrollment, Human-subject sources, initial trust bootstrap, revocation and
lifecycle completeness, binding-consumption ownership, and an authentication-
aware Production Cutover successor. Introduce no unrelated capability. Do not
implement, Ratify, certify, publish, activate, deploy, or mutate runtime state.

Revision result:

Revision 3 retains every resolved Revision 2 boundary and replaces each open
edge with one closed forward lifecycle.

First-time enrollment is now separate from proof verification:

~~~text
active trust-root head
+ exact issuer-produced HumanSubjectSourceAssertionV1
-> Human sends structured HUMAN_AUTHENTICATION_ENROLLMENT_REQUEST
-> canonical HIC transports
-> sole CHE
-> authentication owner validates source
-> CanonicalCredentialSubjectIdentityV1
-> HumanAuthenticationActorNamespaceV1-derived actor identity
-> HumanAuthenticationEnrollmentReceiptV1
-> sole CHE Response/Continuation
-> same HIC

only after enrollment:

enrollment receipt + canonical subject + actor identity
-> challenge Request
-> challenge
-> Human-produced HumanAuthenticationProofPresentationV1
-> structured proof Request through same HIC/CHE
-> owner-produced HumanAuthenticationProofEnvelopeV1
-> verification receipt or refusal receipt
-> Human assertion
-> authenticated session
~~~

The incoming proof Request no longer depends on an artifact that can be
created only after owner invocation. It binds the Human-produced presentation;
the downstream owner then produces the canonical proof envelope from already
finalized subject and presentation predecessors.

Human-subject sources are closed. The issuer assertion has an exact schema,
owner, subject class, signature/profile, scope, time, identity, digest,
revocation source, Replay, and CRO rule. `human_presence_class` is exactly
`CHALLENGE_BOUND_ACTIVE_HUMAN_CONTROL`; `proof_control_class` is exactly
`SUBJECT_BOUND_CRYPTOGRAPHIC_CONTROL`. Actor namespaces are immutable,
deployment-scoped, certified artifacts. No implementation may invent a Human
classification, issuer authority, presence class, control class, or namespace.

Initial trust bootstrap is a declared one-time Constitutional root rather than
an inferred pre-existing authenticated session. It uses the non-production
HIC profile and same sole CHE:

~~~text
active Human Authentication Constitutional successor
+ its exact Human Ratification and Activation
+ certified candidate root and transition intent
-> bootstrap-only challenge under the certified candidate verifier
-> exact Ratification-actor continuity proof
-> exact CanonicalHumanAuthorityActV1 AUTHORIZATION
-> InitialHumanAuthenticationTrustBootstrapAuthorityV1
-> applied root transition -> one active head -> read-back receipt
~~~

The bootstrap authority is predecessor-free only in the narrow sense allowed
by G76-06 for a certified Human Authority root. Its identity is content-derived
from the complete Ratification, active successor, candidate Certification,
intent, challenge/proof receipt, Human act, actor continuity, and scope. It is
single-use, deployment-specific, non-production, non-renewable, and cannot
create a session or production Request. The candidate verifier has only
`BOOTSTRAP_VERIFICATION_ONLY` eligibility until head activation. Later trust
transitions require an active authenticated Human session and Request binding.

Revocation is now a complete owner-local barrier. Exact issuer and security
source assertions feed normalized evidence. The authentication owner commits
one target-specific revocation index state atomically before descendant
projection. Admissions validate the committed index/head generation, so a
crash during propagation cannot preserve authority. A sorted propagation
manifest and receipts reconstruct projections without becoming the barrier.

Lifecycle status has one source of current truth. Challenge, session, and
binding artifacts contain only `initial_status`. The latest validated
`HumanAuthenticationLifecycleStateV1` is current. Proof refusal has its own
closed immutable Receipt. Status transition kinds have exact subject/from/to
rules. Replay never chooses among two status authorities.

Admission binding consumption has one owner and one atomic order:

~~~text
CHE receives exact Request + binding
-> CHE preflight validates closed correlation
-> authentication owner atomically revalidates and commits binding CONSUMED
-> authentication owner returns AdmissionBindingConsumptionReceiptV1
-> CHE validates/persists that receipt under existing idempotency
-> CHE advances the exact Request at most once
~~~

CHE never writes authentication state. The authentication owner never admits
the semantic Request. Revocation and consumption share the authentication
owner's exact transition ordering; CHE advancement remains sole-CHE-owned.

Production Cutover receives one exact V2 successor. Its Certification and
state bind the active Human Authentication Constitution, implementation
Certification, trust-root head/generation, subject/proof profiles, migration
closure, and Release Decision. The existing state path and production owner
remain singular. Once Human Authentication is active, a V1 or other non-
authenticating Cutover state cannot be active production. Rollback is eligible
only to an authentication-enforcing V2 predecessor; otherwise production is
atomically `INACTIVE`.

Strategy A remains unchanged:

~~~text
active V1
-> proposed Human Authentication Revision 3 successor
-> future exact active Human Authentication successor
-> mandatory G76 Release Decision Revision 5 rebase
~~~

All G77-05 unresolved and partial findings are resolved in proposal content.
This is not an Impact Assessment finding. Revision 3 remains:

~~~text
PROPOSAL_ONLY_UNASSESSED
~~~

A new complete G70-03 assessment is mandatory before Human Ratification. No
implementation authority exists unless the complete CAP lifecycle later
activates the exact successor and a separate CDP generation is authorized.

Added artifact:

- `docs/governance/G77_06_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  — this proposal-only G48 Revision 3 artifact.

Intentionally unchanged:

- G77-04, G77-05, and every G0 through G77-03 artifact;
- G76-07 and the complete Release Decision proposal lineage;
- active Constitution, CAP, CDP, Human Authority, HIC, CHE, Production
  Cutover, Replay, CRO, Governance, routing, workflow, owner-chain, release,
  deployment, and runtime behavior; and
- all code, tests, schemas, configuration, credentials, trust roots, sessions,
  providers, and runtime state.

Architectural boundaries preserved by the proposal stage:

- one canonical production HIC family remains;
- one CHE remains for non-production bootstrap, enrollment, authentication,
  and production admission;
- HIC remains transport only;
- one production owner chain remains;
- one production path remains;
- zero parallel production paths remain;
- Human Authority remains the sole Human decision source;
- authentication remains identity attribution only;
- Replay remains read-only and non-authoritative;
- CRO remains passive and non-authoritative; and
- no proposed artifact or capability is active.

## Revision 2 -> Revision 3 Comparison

| Domain | Revision 2 | Revision 3 successor |
|---|---|---|
| first-time subject | proof Request presupposed owner-produced credential subject/envelope | enrollment Request finalizes subject/actor before challenge; proof Request carries Human presentation |
| issuer source | signed assertion referenced without contract | closed `HumanSubjectSourceAssertionV1` and subject profile |
| presence/control | open permitted class | two exact singleton classes |
| actor namespace | identity referenced without source owner | closed certified `HumanAuthenticationActorNamespaceV1` |
| initial root | pre-cutover authenticated profile assumed | one-time Ratification-bound bootstrap root through non-production HIC and sole CHE |
| trust Human act | intent target defined; Continuation absent | bootstrap challenge, Response/Continuation, act, continuity proof, authority artifact |
| proof refusal | transition kind without source artifact | closed `HumanAuthenticationProofRefusalReceiptV1` |
| current status | source status and lifecycle state both present | source `initial_status`; lifecycle state sole current authority |
| revocation sources | issuer/security source names only | two exact source schemas plus normalized evidence |
| revocation application | new semantics without full schema | complete revocation/index/commit/manifest/receipt schemas |
| binding consumption | CHE receipt versus authentication state owner | authentication owner commits and receipts; CHE only advances |
| Cutover | authentication binding asserted against closed V1 | exact Certification V2, state V2, activation, validation, and rollback eligibility |

## G77-05 Resolution Matrix

| G77-05 finding | Revision 3 resolution | Result |
|---|---|---|
| first-time credential/proof ordering | separate enrollment and Human proof presentation | `RESOLVED` |
| issuer assertion source absent | closed issuer assertion artifact and owner | `RESOLVED` |
| presence/control vocabularies open | exact singleton closed values | `RESOLVED` |
| actor namespace source absent | closed namespace artifact and owner | `RESOLVED` |
| proof envelope only partially revised | complete owner-produced successor binding presentation/subject | `RESOLVED` |
| initial root actor authentication | one-time Ratification-bound bootstrap authority root | `RESOLVED` |
| trust intent Human Response/Continuation absent | exact non-production bootstrap capability and Continuation | `RESOLVED` |
| proof refusal source absent | closed refusal Receipt and reasons | `RESOLVED` |
| dual current-status authority | initial-only source status and one lifecycle state authority | `RESOLVED` |
| revocation source schemas absent | exact issuer/security source artifacts | `RESOLVED` |
| revocation application schema incomplete | complete target/index/manifest/receipt model | `RESOLVED` |
| binding-consumption state owner absent | authentication owner exclusively commits/receipts | `RESOLVED` |
| cross-owner crash order absent | owner commit precedes CHE idempotent advancement | `RESOLVED` |
| Replay source completeness | every source/transition/state/receipt now closed | `RESOLVED` |
| CRO source completeness | exact non-secret observation projections defined | `RESOLVED` |
| Cutover authentication binding absent | versioned Cutover Certification/State V2 | `RESOLVED` |
| unauthenticated rollback eligibility open | V2-auth-preserving target or production inactive | `RESOLVED` |

## Human Subject Source and Enrollment Model

### Closed profile vocabularies

~~~text
subject_class = HUMAN_NATURAL_PERSON
issuer_class = CERTIFIED_HUMAN_IDENTITY_ASSERTION_ISSUER
human_presence_class = CHALLENGE_BOUND_ACTIVE_HUMAN_CONTROL
proof_control_class = SUBJECT_BOUND_CRYPTOGRAPHIC_CONTROL
~~~

No other value is permitted in V1. A proof profile may choose algorithms and
providers through later CDP, but it cannot weaken or rename these semantics.

### `HumanSubjectAssertionProfileV1`

Closed fields:

~~~text
artifact_type
artifact_version
subject_profile_identity
subject_profile_digest
subject_class
issuer_class
human_presence_class
proof_control_class
allowed_proof_classes
audience_identity
deployment_scope_identity
canonical_hic_family_identity
che_identity
producing_owner
metadata
~~~

`allowed_proof_classes` is the canonical ordered subset of Revision 2's three
challenge-bound proof classes. The producing owner is
`CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER` under the active Constitutional
contract. The profile is an immutable candidate dependency of the trust-root
candidate and is covered by the root package's later CDP Certification; it
does not reference that later Certification.

### `HumanSubjectSourceAssertionV1`

Closed fields:

~~~text
artifact_type
artifact_version
source_assertion_identity
source_assertion_digest
issuer_assertion_identity
issuer_assertion_digest
issuer_authority_identity
issuer_authority_digest
issuer_class
subject_profile_identity
subject_profile_digest
subject_class
opaque_subject_key_digest
assertion_material_digest
signature_profile_identity
trust_root_candidate_identity
trust_root_candidate_digest
audience_identity
deployment_scope_identity
issued_at
expires_at
revocation_source_identity
revocation_source_digest
producing_owner
metadata
~~~

The producing owner is exactly the issuer authority identified by the subject
profile and, for ordinary authentication, by the active trust-root head. The
assertion is signed external-source evidence normalized into this closed
artifact before CHE submission. Its identity/digest covers the exact signed
assertion digest, authority, HUMAN class, profile, scopes, times, and
revocation source. HIC transports it opaquely; CHE validates only closed
form/capability/correlation; the authentication owner validates signature,
issuer trust, class, scope, time, and revocation.

Before the initial active head exists, this source may be evaluated only by
the bootstrap capability against the exact certified candidate bound by the
bootstrap challenge. That evaluation deterministically derives the candidate-
scoped credential subject and actor used by the bootstrap proof Receipt; it
creates no Enrollment Receipt, session, binding, active issuer authority, or
production eligibility. After the head activates, ordinary enrollment must
revalidate the same source against the active head and must derive the exact
same credential-subject identity or fail closed.

### `HumanAuthenticationActorNamespaceV1`

Closed fields:

~~~text
artifact_type
artifact_version
actor_namespace_identity
actor_namespace_digest
namespace_version
active_constitution_identity
active_constitution_digest
deployment_scope_identity
audience_identity
actor_derivation_contract_identity
producing_owner
metadata
~~~

The producing owner is the authentication owner. The artifact is immutable,
deployment-scoped, covered by the authentication implementation
Certification, and activated as part of Cutover V2 readiness. The actor
identity remains:

~~~text
human-actor-sha256:SHA256(canonical({
  namespace identity/digest,
  credential subject identity/digest,
  deployment scope
}))
~~~

### Enrollment CHE capability

`HUMAN_AUTHENTICATION_ENROLLMENT_REQUEST` uses `STRUCTURED` modality, the same
sole CHE, the canonical HIC family, and the authentication owner as sole
eligible owner. First submission requires no authentication Continuation but
binds an exact source assertion, subject profile, trust-head generation,
audience, deployment/runtime/workspace, HIC, CHE, request, interaction, and
idempotency identity/digest. It cannot carry proof, a Human decision, semantic
content, workflow, Authorization, execution, mutation, or Cutover authority.

The owner returns `HUMAN_AUTHENTICATION_ENROLLMENT_RESPONSE` containing either:

- exact `CanonicalCredentialSubjectIdentityV1`, actor identity, enrollment
  Receipt, and challenge-request Continuation; or
- an exact terminal enrollment refusal Receipt.

Same idempotency identity plus same canonical Request returns the same
Response. Same identity plus different content fails closed. A current
unrevoked subject returns the exact existing identity; it is not duplicated.

### `HumanAuthenticationEnrollmentReceiptV1`

Closed fields:

~~~text
artifact_type
artifact_version
enrollment_receipt_identity
enrollment_receipt_digest
che_request_identity
che_request_digest
source_assertion_identity
source_assertion_digest
credential_subject_identity
credential_subject_digest
actor_namespace_identity
actor_namespace_digest
actor_identity
trust_root_head_identity
trust_root_head_digest
subject_profile_identity
subject_profile_digest
enrollment_result
failure_reason
enrolled_at
idempotency_identity
producing_owner
metadata
~~~

`enrollment_result` is `ENROLLED`, `ALREADY_ENROLLED_IDENTICAL`, or `REFUSED`.
Failure reasons are closed to issuer, signature, subject class, scope, time,
revocation, profile, duplicate conflict, or malformed source failure. Only an
`ENROLLED`/identical Receipt may support a challenge.

### Proof presentation and owner envelope

`HumanAuthenticationProofPresentationV1` is Human-produced source evidence
transported through HIC/CHE. Closed fields:

~~~text
artifact_type
artifact_version
proof_presentation_identity
proof_presentation_digest
challenge_identity
challenge_digest
credential_subject_identity
credential_subject_digest
enrollment_receipt_identity
enrollment_receipt_digest
claimed_actor_identity
proof_class
proof_profile_identity
proof_material_digest
proof_material_encoding
session_request_identity
audience_identity
deployment_scope_identity
proof_issued_at
proof_expires_at
producing_owner
metadata
~~~

`producing_owner` is `HUMAN_AUTHORITY` as source of the presented control act;
the artifact does not itself create a Human decision. The structured
`HUMAN_AUTHENTICATION_PROOF_RESPONSE` CHE Request binds this presentation,
not the later proof envelope.

The authentication owner then produces the complete successor
`HumanAuthenticationProofEnvelopeV1` with closed fields:

~~~text
artifact_type
artifact_version
proof_envelope_identity
proof_envelope_digest
proof_presentation_identity
proof_presentation_digest
proof_class
proof_profile_identity
trust_root_identity
trust_root_digest
trust_root_head_identity
trust_root_head_digest
challenge_identity
challenge_digest
credential_subject_identity
credential_subject_digest
enrollment_receipt_identity
enrollment_receipt_digest
claimed_actor_identity
session_request_identity
proof_material_digest
proof_material_encoding
audience_identity
deployment_scope_identity
issued_at
expires_at
producing_owner
metadata
~~~

This is a forward-only transformation. Enrollment precedes challenge;
challenge and Human presentation precede owner envelope; envelope precedes
verification.

## Authentication Lifecycle

### Sole current status authority

Revision 3 changes the inherited source fields as follows:

~~~text
HumanAuthenticationChallengeV1.challenge_status
  -> initial_status = ISSUED

AuthenticatedHumanSessionV1.session_status
  -> initial_status = AUTHENTICATED_ACTIVE

HumanAuthenticationAdmissionBindingV1.binding_status
  -> initial_status = ISSUED
~~~

These fields are immutable genesis facts only. The latest validated
`HumanAuthenticationLifecycleStateV1` for the exact subject lineage is the
sole current status. If no lifecycle state exists, the validated source's
initial status is generation zero. Conflicting heads, missing predecessor,
multiple current states, or a source/current mismatch fails closed.

### Closed transition table

| Subject | Transition | Required from | Exact to | Authority/evidence |
|---|---|---|---|---|
| challenge | `CHALLENGE_CONSUMED` | `ISSUED` | `CONSUMED` | verified or rejected proof Receipt |
| challenge | `CHALLENGE_EXPIRED` | `ISSUED` | `EXPIRED` | committed expiry time |
| challenge | `CHALLENGE_CANCELLED` | `ISSUED` | `CANCELLED` | exact CHE control/owner policy |
| challenge | `CHALLENGE_REPLACED` | `ISSUED` | `REPLACED` | replacement Request/Continuation |
| session | `SESSION_CLOSED` | `AUTHENTICATED_ACTIVE` | `CLOSED` | exact session-close artifact |
| session | `SESSION_EXPIRED` | `AUTHENTICATED_ACTIVE` | `EXPIRED` | committed expiry time |
| session | `SESSION_REVOKED` | `AUTHENTICATED_ACTIVE` | `REVOKED` | committed revocation index state |
| binding | `BINDING_CONSUMED` | `ISSUED` | `CONSUMED` | owner consumption transition |
| binding | `BINDING_EXPIRED` | `ISSUED` | `EXPIRED` | committed expiry time |
| binding | `BINDING_REVOKED` | `ISSUED` | `REVOKED` | committed revocation index state |

No other from/to pair is valid. Terminal status has no outgoing transition.
Delivery uncertainty is an observation Receipt, not a lifecycle status change.

### `HumanAuthenticationProofRefusalReceiptV1`

Closed fields:

~~~text
artifact_type
artifact_version
proof_refusal_receipt_identity
proof_refusal_receipt_digest
che_request_identity
che_request_digest
challenge_identity
challenge_digest
proof_presentation_identity
proof_presentation_digest
credential_subject_identity
credential_subject_digest
trust_root_head_identity
trust_root_head_digest
refusal_reason
refused_at
idempotency_identity
producing_owner
metadata
~~~

Reasons are exactly `CHALLENGE_NOT_CURRENT`, `ROOT_NOT_CURRENT`,
`SUBJECT_NOT_CURRENT`, `SCOPE_MISMATCH`, `TIME_INVALID`, `REVOKED`,
`PROFILE_MISMATCH`, `MALFORMED_PRESENTATION`, or `DUPLICATE_CONFLICT`.
Refusal means verification did not run. `HumanAuthenticationVerificationReceiptV1`
remains closed to `VERIFIED` or `REJECTED`. Both Receipts are immutable and
mutually exclusive for one proof Request/idempotency identity.

Session `established_at` and identity time derive exactly from the committed
`verified_at` in the verified receipt. Retry cannot select a new time or
session identity. A verified Receipt without a session commit may produce only
the one deterministic session while all predecessors remain current.

### Binding-consumption ownership and atomicity

Revision 3 replaces Revision 2's CHE-produced consumption Receipt. The
authentication owner exclusively owns:

- binding current lifecycle state;
- validation against current root, subject, session, scope, time, Request,
  and revocation epoch;
- atomic `ISSUED -> CONSUMED` transition; and
- `HumanAuthenticationAdmissionBindingConsumptionReceiptV1`.

The Receipt closed fields are:

~~~text
artifact_type
artifact_version
admission_consumption_receipt_identity
admission_consumption_receipt_digest
admission_binding_identity
admission_binding_digest
production_request_identity
production_request_digest
authenticated_session_identity
authenticated_session_digest
predecessor_binding_state_identity
predecessor_binding_state_digest
consumed_binding_state_identity
consumed_binding_state_digest
root_head_generation
revocation_epoch
che_request_identity
che_request_digest
che_idempotency_identity
consumption_result
consumed_at
producing_owner
metadata
~~~

`producing_owner` is exactly the authentication owner. `consumption_result` is
`CONSUMED` or `ALREADY_CONSUMED_IDENTICAL`. Revocation and consumption are
linearized under the authentication owner's exact subject/scope transition
lock. A revocation committed first rejects consumption; consumption committed
first yields one Receipt, after which CHE must still revalidate the Receipt's
epoch/head before advancement. A later revocation can stop downstream owners
at their existing admission boundary but cannot make the binding reusable.

CHE owns only Request admission and advancement. It validates the owner
Receipt, persists it in existing delivery/idempotency evidence, and advances
the same Request at most once. Crash behavior is:

| Crash point | Authoritative recovery |
|---|---|
| before owner consumption | binding remains `ISSUED`; same Request/key may retry |
| after owner commit before Receipt delivery | same Request/key reconstructs exact owner Receipt |
| after CHE receives Receipt before advancement | CHE existing idempotency resumes same Request only |
| after CHE advancement | existing CHE advancement/result evidence returns exact disposition |

A different Request, digest, actor, session, or idempotency identity can never
reuse the consumed binding.

## Trust Bootstrap Model

### Bootstrap capability and topology

The exact capability is:

~~~text
capability = HUMAN_AUTHENTICATION_INITIAL_TRUST_BOOTSTRAP_AUTHORIZATION
modality = STRUCTURED
profile = NON_PRODUCTION_CONSTITUTIONAL_GOVERNANCE
entry = sole CHE
eligible_owner = CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER
production_execution_eligible = false
~~~

The non-production HIC profile transports one bootstrap challenge, one
candidate-bound proof presentation, and one `CanonicalHumanAuthorityActV1`
`AUTHORIZATION`. It is not a canonical production HIC peer and cannot reach a
semantic workflow, Authorization owner, Worker, mutation, or production
execution.

The owner first issues `HUMAN_AUTHENTICATION_INITIAL_TRUST_BOOTSTRAP_CHALLENGE`
through CHE with an exact active Continuation. The challenge binds the active
Human Authentication Constitutional successor, its Ratification/Activation,
candidate/Certification, transition intent, deployment scope, candidate proof
profile, one nonce, expiry, and the Ratification actor identity. The candidate
verifier may evaluate only this challenge under
`BOOTSTRAP_VERIFICATION_ONLY`; it may not establish a session or verify a
production Request before activation.

### `InitialHumanAuthenticationTrustBootstrapChallengeV1`

Closed fields:

~~~text
artifact_type
artifact_version
bootstrap_challenge_identity
bootstrap_challenge_digest
active_constitution_identity
active_constitution_digest
constitutional_ratification_identity
constitutional_ratification_digest
constitutional_activation_identity
constitutional_activation_digest
ratification_actor_identity
candidate_trust_root_identity
candidate_trust_root_digest
candidate_certification_identity
candidate_certification_digest
transition_intent_identity
transition_intent_digest
actor_namespace_identity
actor_namespace_digest
subject_profile_identity
subject_profile_digest
proof_profile_identity
proof_profile_digest
deployment_scope_identity
audience_identity
nonce_digest
issued_at
expires_at
che_request_identity
che_request_digest
producing_owner
metadata
~~~

The producing owner is exactly the authentication owner. The finalized
challenge precedes the CHE Response and active Continuation; those envelopes
bind the challenge identity/digest, so the challenge never references either
later artifact. The Human returns the unchanged Continuation with one exact
bootstrap proof presentation and one `CanonicalHumanAuthorityActV1`. Wrong,
missing, stale, expired, reused, or cross-scope challenge/Continuation
evidence fails closed.

### `InitialHumanAuthenticationTrustBootstrapProofPresentationV1`

Closed fields:

~~~text
artifact_type
artifact_version
bootstrap_proof_presentation_identity
bootstrap_proof_presentation_digest
bootstrap_challenge_identity
bootstrap_challenge_digest
source_assertion_identity
source_assertion_digest
claimed_credential_subject_identity
claimed_credential_subject_digest
actor_namespace_identity
actor_namespace_digest
claimed_actor_identity
ratification_actor_identity
candidate_trust_root_identity
candidate_trust_root_digest
proof_class
proof_profile_identity
proof_material_digest
proof_material_encoding
deployment_scope_identity
audience_identity
proof_issued_at
proof_expires_at
producing_owner
metadata
~~~

This is the bootstrap-only Human source artifact and does not require an
Enrollment Receipt or active trust head. `producing_owner` is
`HUMAN_AUTHORITY` as the source of the exact control presentation; it is not a
Human decision. The HIC may serialize and transport the exact fields but may
not derive the subject, actor, proof class, candidate, or authority. The
authentication owner recomputes the credential subject and actor from the
source assertion and proposed namespace; mismatch with either claimed value
fails closed.

### `InitialHumanAuthenticationTrustBootstrapProofReceiptV1`

Closed fields:

~~~text
artifact_type
artifact_version
bootstrap_proof_receipt_identity
bootstrap_proof_receipt_digest
bootstrap_challenge_identity
bootstrap_challenge_digest
proof_presentation_identity
proof_presentation_digest
source_assertion_identity
source_assertion_digest
credential_subject_identity
credential_subject_digest
actor_namespace_identity
actor_namespace_digest
derived_actor_identity
ratification_actor_identity
candidate_trust_root_identity
candidate_trust_root_digest
candidate_certification_identity
candidate_certification_digest
proof_profile_identity
proof_profile_digest
che_request_identity
che_request_digest
continuation_identity
continuation_digest
verification_result
verified_at
producing_owner
metadata
~~~

`verification_result` is exactly `BOOTSTRAP_VERIFIED`; failure creates no
bootstrap proof Receipt. The producing owner is the authentication owner
operating the candidate verifier under `BOOTSTRAP_VERIFICATION_ONLY`. The
Receipt proves exact candidate-bound control and actor continuity only; it
creates no session, active root, Ratification, production admission, or
execution authority.

Bootstrap failure produces one
`InitialHumanAuthenticationTrustBootstrapProofRefusalReceiptV1` with the
closed payload:

~~~text
artifact_type
artifact_version
bootstrap_proof_refusal_receipt_identity
bootstrap_proof_refusal_receipt_digest
bootstrap_challenge_identity
bootstrap_challenge_digest
proof_presentation_identity
proof_presentation_digest
candidate_trust_root_identity
candidate_trust_root_digest
che_request_identity
che_request_digest
continuation_identity
continuation_digest
refusal_reason
refused_at
idempotency_identity
producing_owner
metadata
~~~

Reasons are exactly `CHALLENGE_NOT_CURRENT`, `CANDIDATE_NOT_CERTIFIED`,
`SUBJECT_SOURCE_INVALID`, `ACTOR_CONTINUITY_MISMATCH`, `SCOPE_MISMATCH`,
`TIME_INVALID`, `PROFILE_MISMATCH`, `MALFORMED_PRESENTATION`, or
`DUPLICATE_CONFLICT`. The owner is the authentication owner. A proof Receipt
and refusal Receipt are mutually exclusive for the same Request and
idempotency identity.

### `InitialHumanAuthenticationTrustBootstrapAuthorityV1`

Closed fields:

~~~text
artifact_type
artifact_version
bootstrap_authority_identity
bootstrap_authority_digest
active_constitution_identity
active_constitution_digest
constitutional_ratification_identity
constitutional_ratification_digest
constitutional_activation_identity
constitutional_activation_digest
ratification_actor_identity
candidate_trust_root_identity
candidate_trust_root_digest
candidate_certification_identity
candidate_certification_digest
transition_intent_identity
transition_intent_digest
bootstrap_challenge_identity
bootstrap_challenge_digest
bootstrap_proof_receipt_identity
bootstrap_proof_receipt_digest
bootstrap_actor_continuity_digest
human_authority_act_identity
human_authority_act_digest
che_request_identity
che_request_digest
continuation_identity
continuation_digest
deployment_scope_identity
bootstrap_generation
bootstrap_status
producing_owner
metadata
~~~

`bootstrap_generation` is exactly `1`; `bootstrap_status` is exactly
`AUTHORIZED_SINGLE_USE`. The producing ownership is `HUMAN_AUTHORITY`; the
authentication owner validates and consumes it but cannot create it. The
Human act's target is the finalized transition intent, kind is
`AUTHORIZATION`, expected owner is the authentication owner, and payload binds
every candidate, Certification, Ratification, Activation, challenge, proof,
actor, and scope field above.

`bootstrap_actor_continuity_digest` is the canonical digest of the exact
Ratification actor identity, issuer-backed credential subject, candidate-bound
proof subject, and proposed actor namespace. The credential subject from the
source assertion and the proof subject must be identical, and applying the
proposed actor derivation contract to that subject and namespace must produce
the exact `ratification_actor_identity`; any inequality fails closed. The
Ratification is the sovereign predecessor authority; candidate proof shows
current control by that same Human subject. Candidate proof alone never
authorizes its root, and the later continuity proof cannot repair or replace a
different Ratification actor.

The authority is committed and consumed atomically with initial root
activation. Missing, duplicate-conflicting, expired, stale, cross-deployment,
wrong-actor, unratified, uncertified, or already-consumed authority fails
closed. It is retained for Replay, observed passively by CRO without proof
material, and never renewable or reusable. Later transitions cannot use this
artifact.

### Trust lifecycle after bootstrap

Revision 2's candidate -> intent -> Human act -> transition -> head -> Receipt
DAG remains. Initial activation additionally requires the bootstrap authority.
Rotation, supersession, retirement, rollback, and Human-directed revocation
require a current authenticated session, Request-specific binding, sole-CHE
Human Authority Act, and exact transition intent. Certified emergency
revocation uses only the closed source model below.

## Revocation Source and Lifecycle Model

### `HumanIdentityIssuerCredentialRevocationAssertionV1`

Closed fields:

~~~text
artifact_type
artifact_version
issuer_revocation_assertion_identity
issuer_revocation_assertion_digest
issuer_authority_identity
issuer_authority_digest
issuer_class
subject_profile_identity
subject_profile_digest
credential_subject_identity
credential_subject_digest
trust_root_identity
trust_root_digest
revocation_sequence
revocation_reason
effective_at
assertion_material_digest
signature_profile_identity
producing_owner
metadata
~~~

The producing owner is the exact issuer authority in the credential subject
and active trust root. Sequence is strictly monotonic. Reasons are
`CREDENTIAL_COMPROMISED`, `CREDENTIAL_RETIRED`, `SUBJECT_BINDING_INVALIDATED`,
or `ISSUER_AUTHORITY_WITHDRAWN`.

### `HumanAuthenticationSecurityCompromiseAssertionV1`

Closed fields:

~~~text
artifact_type
artifact_version
security_assertion_identity
security_assertion_digest
security_authority_identity
security_authority_digest
security_authority_class
trust_root_identity
trust_root_digest
target_type
target_identity
target_digest
compromise_class
evidence_digest
observed_at
effective_at
producing_owner
metadata
~~~

The producing owner is the exact security authority identity/class named by
the trust-root candidate and Certification. `compromise_class` is exactly
`ROOT_KEY_COMPROMISE`, `ISSUER_COMPROMISE`, or
`CREDENTIAL_CONTROL_COMPROMISE`. The source cannot target an unrelated scope
or create positive authentication authority.

### Complete `HumanAuthenticationRevocationV1`

Closed fields:

~~~text
artifact_type
artifact_version
revocation_identity
revocation_digest
revocation_evidence_identity
revocation_evidence_digest
source_artifact_identity
source_artifact_digest
target_type
target_identity
target_digest
trust_root_head_identity
trust_root_head_digest
head_generation
predecessor_revocation_index_identity
predecessor_revocation_index_digest
revocation_epoch
revocation_reason
effective_at
propagation_policy
idempotency_identity
producing_owner
metadata
~~~

`propagation_policy` is exactly `ROOT_DESCENDANTS`,
`CREDENTIAL_DESCENDANTS`, or `SESSION_BINDINGS` and must match target type.
The producing owner is the authentication owner. Revocation is content-derived,
monotonic, terminal, and cannot be reversed.

### Revocation index barrier and propagation

`HumanAuthenticationRevocationIndexStateV1` has closed fields:

~~~text
artifact_type
artifact_version
revocation_index_identity
revocation_index_digest
target_type
target_identity
target_digest
predecessor_index_identity
predecessor_index_digest
applied_revocation_identity
applied_revocation_digest
index_generation
revocation_epoch
current_status = REVOKED
committed_at
producing_owner
metadata
~~~

The authentication owner commits this state atomically under the same
subject/scope ordering used by session and binding admission. Once committed,
root, subject, session, and binding validators fail closed through ancestry and
epoch comparison even before descendant projections complete.

`HumanAuthenticationRevocationPropagationManifestV1` is produced after the
barrier with this closed payload:

~~~text
artifact_type
artifact_version
propagation_manifest_identity
propagation_manifest_digest
revocation_identity
revocation_digest
revocation_index_identity
revocation_index_digest
propagation_policy
descendant_predecessor_state_references
manifest_generation
producing_owner
metadata
~~~

`descendant_predecessor_state_references` is a canonically sorted closed tuple
of exact descendant type/identity/digest and previous lifecycle-state
identity/digest tuples. The manifest does not grant authority; it makes the
projection scope deterministic.

`HumanAuthenticationRevocationCommitReceiptV1` has the closed payload:

~~~text
artifact_type
artifact_version
revocation_commit_receipt_identity
revocation_commit_receipt_digest
revocation_identity
revocation_digest
revocation_index_identity
revocation_index_digest
read_back_index_digest
commit_result
committed_at
idempotency_identity
producing_owner
metadata
~~~

`commit_result` is `COMMITTED` or `ALREADY_COMMITTED_IDENTICAL`.

`HumanAuthenticationRevocationPropagationReceiptV1` has the closed payload:

~~~text
artifact_type
artifact_version
propagation_receipt_identity
propagation_receipt_digest
revocation_index_identity
revocation_index_digest
propagation_manifest_identity
propagation_manifest_digest
resulting_lifecycle_state_references
projection_result
projected_at
idempotency_identity
producing_owner
metadata
~~~

`resulting_lifecycle_state_references` is the canonically sorted exact tuple
corresponding one-for-one with the manifest. `projection_result` is
`PROJECTED` or `ALREADY_PROJECTED_IDENTICAL`. A crash after the index barrier
leaves the target unavailable and recovery resumes the same manifest and
projections. It can never restore authority.

Replay reconstructs source -> normalized evidence -> revocation -> index
barrier -> commit Receipt -> manifest -> lifecycle projections -> propagation
Receipt. CRO observes only identities, target type, non-sensitive reason
class, epoch/generation, result, and times. Neither can commit, retry, revoke,
or restore.

## Updated Dependency DAG

~~~text
active Constitution
  -> SubjectAssertionProfile
  -> ActorNamespace
  -> TrustRootCandidate
      -> candidate Certification
          -> TransitionIntent

initial root only:
  Constitutional Ratification + Activation
  + candidate/Certification + TransitionIntent
  + candidate-bound HumanSubjectSourceAssertion
      -> bootstrap credential subject + proposed actor derivation
  -> BootstrapChallenge
      -> candidate-bound BootstrapProofReceipt
          -> CanonicalHumanAuthorityAct
              -> InitialTrustBootstrapAuthority
                  -> AppliedTrustTransition
                      -> ActiveHead -> TransitionReceipt

ordinary Human authentication:
  ActiveHead + issuer-produced HumanSubjectSourceAssertion
  -> CanonicalCredentialSubjectIdentity
      + ActorNamespace -> actor identity
      -> EnrollmentReceipt
          -> Challenge
              -> Human ProofPresentation
                  -> owner ProofEnvelope
                      -> VerificationReceipt OR ProofRefusalReceipt
                          -> AuthenticatedHumanSubjectAssertion
                              -> AuthenticatedSession
                                  -> AdmissionBinding
                                      + independent production Request
                                      -> owner ConsumptionTransition/State
                                          -> ConsumptionReceipt
                                              -> CHE advancement

revocation:
  issuer/security/Human source
  -> RevocationEvidence
      -> Revocation
          -> RevocationIndexState -> CommitReceipt
              -> PropagationManifest
                  -> LifecycleStates -> PropagationReceipt

production activation:
  Authentication Constitution Activation
  + implementation Certification
  + ActiveHead + profiles + migration closure + Release Decision
  -> CutoverCertificationV2
      -> CutoverStateV2 -> CutoverActivationReceiptV2

all committed owner artifacts -> Replay -> passive CRO
~~~

Every arrow points from an already finalized predecessor to a successor that
binds its identity/digest. Source artifacts never reference later Receipts,
Replay, or CRO. Transition intents never reference later Human acts or states.
Production Requests are independently finalized and do not reference their
later binding/consumption Receipt. The graph is finite and acyclic.

All new artifacts use canonical versioned closed payloads, type-namespaced
SHA-256 identities, and `sha256:` digests over every field except their own
derived identity/digest. Owner-issued source/idempotency identities are bound
with exact content digests and scopes under G76-06.

## Authentication-Aware Production Cutover Successor

### `ConstitutionalProductionCutoverAuthenticationCertificationV2`

Closed fields:

~~~text
artifact_type
artifact_version
cutover_certification_identity
cutover_certification_digest
predecessor_g69_19_certification_identity
predecessor_g69_19_certification_digest
human_authentication_constitution_identity
human_authentication_constitution_digest
human_authentication_activation_identity
human_authentication_activation_digest
authentication_implementation_certification_identity
authentication_implementation_certification_digest
actor_namespace_identity
actor_namespace_digest
subject_profile_identity
subject_profile_digest
proof_profile_identity
proof_profile_digest
trust_root_head_identity
trust_root_head_digest
trust_root_head_generation
enrollment_readiness_evidence_identity
enrollment_readiness_evidence_digest
migration_closure_identity
migration_closure_digest
release_decision_identity
release_decision_digest
rollback_policy_identity
rollback_policy_digest
canonical_hic_family_identity
che_identity
production_owner_chain_count
production_path_count
parallel_production_path_count
activated_at
producing_owner
metadata
~~~

The producing owner remains the G69-19 release/cutover Certification owner.
Counts are exactly `1`, `1`, and `0`; the existing sole CHE and HIC family must
match. The V1 Certification is retained as exact predecessor evidence, not
treated as an active authentication Certification.

### `ConstitutionalProductionCutoverAuthenticationStateV2`

Closed fields:

~~~text
state_version = CONSTITUTIONAL_PRODUCTION_CUTOVER_AUTHENTICATION_STATE_V2
state_identity
state_digest
predecessor_state_identity
predecessor_state_digest
state_status
cutover_certification_identity
cutover_certification_digest
human_authentication_enforcement = REQUIRED
human_authentication_constitution_identity
human_authentication_activation_identity
trust_root_head_identity
trust_root_head_digest
trust_root_head_generation
actor_namespace_identity
subject_profile_identity
proof_profile_identity
canonical_hic_family_identity
che_identity
surface_dispositions
rollback_decision_identity
rollback_decision_digest
effective_at
producing_owner
metadata
~~~

The state uses the existing one Production Cutover state path and one atomic
transition lock. The producing owner remains the production-status owner. A
valid active state requires `state_status =
CONSTITUTIONAL_PRODUCTION_CUTOVER_AUTHENTICATION_ESTABLISHED`, exact V2
Certification, `REQUIRED`, one current active trust head/generation, and all
profile/Constitution/owner/topology equality. A V1 state remains historical
but is not active after Human Authentication Constitutional Activation.

### Activation and rollback

Activation validates every predecessor, acquires the existing exclusive
Cutover lock, atomically replaces the one current state, re-reads it, validates
identity/digest and authentication readiness, and emits
`ConstitutionalProductionCutoverAuthenticationActivationReceiptV2` derived
from the committed state. That Receipt has the closed payload:

~~~text
artifact_type
artifact_version
activation_receipt_identity
activation_receipt_digest
predecessor_state_identity
predecessor_state_digest
committed_state_identity
committed_state_digest
cutover_certification_identity
cutover_certification_digest
release_decision_identity
release_decision_digest
runtime_scope_identity
activation_result
activated_at
producing_owner
metadata
~~~

`activation_result` is `ACTIVATED`, `ALREADY_ACTIVE_IDENTICAL`, or
`PRODUCTION_INACTIVE`. The producing owner is the production-status owner.
The Receipt is created only after validated read-back and cannot activate or
repair state.

An active rollback target is eligible only when it is an exact validated V2
predecessor whose authentication enforcement remains `REQUIRED`, whose
Constitution/profile/head lineage is eligible, and whose release/rollback
decision authorizes that exact target. Sessions and bindings from the replaced
generation become terminal and every Human reauthenticates.

If the requested predecessor is V1, lacks authentication enforcement, has a
stale/revoked head, or otherwise fails V2 validation, rollback cannot activate
it. The production-status owner atomically writes a V2
`PRODUCTION_INACTIVE` state retaining exact rollback evidence. Production CLIA
fails closed before submission. No active Constitution may coexist with an
unauthenticated active production state.

Historical V1 Requests, sessions, Cutover state, Replay, and CRO evidence
remain readable and immutable but receive no grandfathered authority.

## CAP Ordering and Compatibility

Strategy A from Revision 2 is retained exactly. Human Authentication Revision
3 is the only proposed next active successor in this ordering. G76-07 remains
immutable inactive evidence. Release Decision Revision 5 must rebase on the
exact activated Human Authentication successor and must bind the Cutover V2
responsibilities before any authentication-aware production activation.

No proposal, report presence, CDP implementation, or deployment can compose
the two successors implicitly. The later Release Decision revision must pass
its own G70-03 assessment and complete CAP.

## Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Revision 3 reuses the active Constitution; G48; complete G70 CAP; G76-06
   identity model; Human Authority and exact G69-07 acts; canonical structured
   Request/Response/Continuation, sole CHE, owner transition, idempotency,
   delivery, and advancement; one canonical production HIC family and the
   non-production governance profile; G69-18 owner-local Replay and passive
   CRO; G69-19 Cutover ownership/atomic-state model; G76-07 immutable proposal
   evidence; G77-01 Gate 0B; Revision 2's resolved topology/trust DAG/CAP order;
   and G77-05's sole authoritative findings.

2. **Which new Constitutional capabilities are proposed?**

   New Revision 3 capabilities are first-time enrollment; exact Human source,
   subject profile, actor namespace, proof presentation/envelope order;
   one-time Ratification-bound initial trust bootstrap; refusal and sole-status
   lifecycle rules; complete revocation source/index/propagation; authentication-
   owner binding consumption; and versioned authentication-aware Cutover V2.
   Each is necessary to close a G77-05 finding and no unrelated domain is
   introduced.

3. **Does any certified capability become unreachable?**

   No active capability changes because this proposal is inactive. If later
   activated and implemented, existing semantic, Governance, Authorization,
   Worker, Replay, CRO, release, and Cutover responsibilities remain reachable
   through the same certified preconditions. Unauthenticated production
   Requests and non-authenticating Cutover states intentionally fail closed.

4. **Does the proposal create a parallel production path?**

   No. Enrollment, challenge, proof, Human control, and production Requests
   use the same sole CHE. The non-production bootstrap profile cannot execute
   production work. Cutover V2 replaces current state at the same single path.

5. **Does it decrease or increase the number of production paths?**

   Neither. The count remains exactly one production path with zero parallel
   production paths.

# 2. Code Evidence

## Public API

G77-06 adds or changes no runtime API. After complete CAP activation, a
separate CDP generation may propose implementations only for responsibilities
defined here, conceptually including:

~~~text
create_human_subject_source_assertion_v1(...)
enroll_canonical_human_subject_v1(...)
create_human_authentication_proof_presentation_v1(...)
create_human_authentication_proof_envelope_v1(...)
create_initial_human_authentication_trust_bootstrap_authority_v1(...)
commit_human_authentication_revocation_index_v1(...)
consume_human_authentication_admission_binding_v1(...)
create_constitutional_production_cutover_authentication_certification_v2(...)
activate_constitutional_production_cutover_authentication_v2(...)
validate_active_constitutional_production_cutover_authentication_v2(...)
~~~

These are proposed duty labels, not implemented or authorized functions. No
API, model, validator, serializer, command, provider, route, store, state, or
deployment is created.

## Orchestration Entry Point

The one Human ingress remains:

~~~text
Human -> permitted HIC profile -> sole CHE -> exact eligible owner
-> sole CHE Response/Continuation -> same HIC
~~~

Capability selects enrollment, challenge, proof, close, initial bootstrap, or
existing production/Human Authority responsibilities without creating a new
entry. Only the production profile can later carry production Requests, and
only after Cutover V2 validation.

## Semantic Reductions

### First-time enrollment

~~~text
valid source assertion + active head + exact enrollment Request
-> canonical subject + actor + enrollment Receipt
-> challenge eligible

otherwise -> no challenge/session
~~~

### Initial trust

~~~text
Ratification/Activation continuity
+ certified candidate/bootstrap proof
+ exact Human AUTHORIZATION
+ single-use bootstrap authority
-> initial root transition eligible

otherwise -> no active root
~~~

### Binding consumption

~~~text
owner commits exact binding consumed state
-> owner Receipt
-> CHE may advance same Request idempotently

no owner Receipt -> no CHE advancement
~~~

### Production rollback

~~~text
eligible authentication-enforcing V2 predecessor
-> active rollback permitted

non-authenticating or invalid predecessor
-> PRODUCTION_INACTIVE
-> fail closed before CLIA submission
~~~

## Public Validators

No validator is implemented. Future validators must reject:

- enrollment or proof material bypassing sole CHE;
- non-Human subject class or untrusted issuer/source profile;
- open presence/control/namespace values;
- proof Request that references a post-owner artifact;
- bootstrap without exact Ratification/Activation/candidate/Certification/
  challenge/proof/Human act/Continuation continuity;
- bootstrap reuse or production use;
- two current lifecycle states or source status treated as current;
- refusal without exact Receipt;
- revocation without an exact source, index barrier, epoch, and owner Receipt;
- binding consumption or CHE advancement without exact owner commit;
- Cutover V1/non-auth state treated as active after Constitutional Activation;
- rollback to a non-authenticating active target;
- any identity self-edge, forward reference, or cycle; and
- any path/topology other than `1 / 1 / 1 / 1 / 0`.

## Canonical Data Models

| Model family | Exact source/current owner | Purpose |
|---|---|---|
| subject/profile/namespace | issuer source plus authentication owner | Human classification and stable actor |
| enrollment/challenge/proof | authentication owner after sole CHE | first-time and recurring authentication |
| bootstrap authority | Human Authority root; authentication owner consumes | one initial trust head only |
| trust head | authentication owner | one current root tuple |
| lifecycle state | authentication owner | sole current auth status |
| revocation index | authentication owner | immediate terminal barrier |
| binding consumption | authentication owner | atomic single-use state |
| CHE advancement | sole CHE | one Request admission/owner transition |
| Cutover V2 state | production-status owner | one auth-enforcing production state |
| Replay | each owner-local custodian | read-only reconstruction |
| CRO | passive Observatory | non-secret observation only |

## Deterministic Algorithms

### Canonical identity

1. Validate exact artifact type/version/closed fields/owner.
2. Resolve all finalized predecessor identity/digest pairs.
3. Reject missing, mutable, self, forward, conflicting, or circular edges.
4. Exclude only own identity/digest fields.
5. Canonically serialize all remaining fields.
6. SHA-256 exact bytes once.
7. construct type namespace identity and `sha256:` digest.
8. Revalidate and persist only the completed artifact through its owner.

### Owner-local commit

1. Validate authority, source, current predecessor, scope, epoch, and
   idempotency.
2. Create immutable transition without successor references.
3. Acquire exact owner transition lock.
4. Revalidate current state and conflicts.
5. Atomically replace current state with successor referencing transition.
6. Flush, re-read, validate, and emit post-commit Receipt.
7. Return same Receipt for exact duplicate; reject conflict.

CHE consumes no authentication state. It consumes only the exact owner Receipt
as evidence for its separately owned advancement.

## Responsibility Boundaries

| Responsibility | Exact owner | Negative boundary |
|---|---|---|
| source HUMAN assertion | certified issuer authority | no session, decision, or execution authority |
| transport | HIC | no semantics, verification, owner selection, or route creation |
| admit Human/auth requests | sole CHE | no proof decision or auth-state mutation |
| authenticate/enroll/custody | authentication owner | no Human decision, semantic workflow, execution, Cutover, or provider law |
| initial trust decision | Human Authority through bootstrap authority | authentication owner cannot create it |
| later trust decisions | authenticated Human Authority through exact acts | no inference or model substitution |
| revocation source | Human/issuer/security authority | no positive authority creation |
| revocation/application/consumption | authentication owner | no semantic Request admission |
| advance production Request | sole CHE | exact owner consumption Receipt required |
| activate production | release/cutover owner | exact Cutover V2 only |
| reconstruct | owner-local Replay | read-only and non-authoritative |
| observe | CRO | passive and non-authoritative |
| evolve/implement | CAP/CDP | proposal grants neither authority |

## Repository Evidence

Revision 3 uses only authenticated G77-05 findings and certified predecessors.
No historical provider, implementation, test, runtime behavior, deployment,
credential, or configuration defines a norm. G69/G70/G76/G77 evidence supplies
the owner, topology, identity, CAP, Cutover, Replay, CRO, and fail-closed
constraints applied here.

# 3. Constitutional Self-Assessment

## Verified

- The baseline is the clean authenticated G77-05 successor commit.
- G77-04 and G77-05 bytes match their exact SHA-256.
- Revision 3 binds the exact proposal and sole authoritative assessment.
- First-time enrollment precedes actor/challenge/proof and removes the prior
  artifact-order contradiction.
- Issuer source, subject profile, presence/control classes, actor namespace,
  enrollment Receipt, proof presentation, and proof envelope are closed.
- Initial root bootstrap has an exact one-time Human Authority root,
  challenge/Continuation, candidate proof, actor continuity, and no production
  capability.
- Lifecycle source status is initial-only and one lifecycle state is current.
- Proof refusal has exact immutable evidence.
- Revocation sources, application, index barrier, manifest, and Receipts are
  complete and fail closed across crashes.
- The authentication owner alone commits binding consumption before CHE
  advancement.
- Cutover Certification/State V2 binds authentication and prohibits active
  rollback to a non-authenticating state.
- Replay has complete source lineage and remains read-only.
- CRO observes complete non-secret lineage and remains passive.
- The updated identity graph is finite and acyclic.
- Strategy A, Human Authority, sole CHE, transport-only HIC, one chain/path,
  and zero parallel paths remain preserved.
- No implementation, Ratification, Certification, publication, activation,
  deployment, or runtime mutation occurs.

## Not Verified

- Revision 3 has not received its mandatory new G70-03 Impact Assessment.
- No Human Ratification, amendment Certification, publication, or activation
  exists for Revision 3.
- Revision 3 is not active Constitutional law and authorizes no CDP work.
- No Release Decision Revision 5 rebase exists.
- No schema, validator, serializer, cryptographic proof profile, provider,
  persistence primitive, CHE capability, Cutover V2 implementation, migration,
  rollback, or deployment is implemented.
- No live issuer assertion, enrollment, challenge, proof, bootstrap authority,
  trust root, session, binding, revocation, Cutover, Replay, or CRO artifact is
  created.
- No implementation, integration, crash, security, deployment, rollback, or
  live production test is run because this generation is proposal-only.
- Provider choice, algorithm choice, key custody, privacy controls, external
  issuer/security integration, and storage primitives remain later CDP/
  deployment responsibilities bounded by the proposed norms.
- Existing enforcement, hook, privacy, identity, deployment, rollback, and
  external-system limitations remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and required Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject, parent, clean start, exact digests | Git/SHA-256 inspection | `PASS` |
| Revision 2 successor | exact G77-04 identity/revision/digest | lineage review | `PASS` |
| authoritative assessment | exact G77-05 identity/digest/class | lineage review | `PASS` |
| proposal-only status | no later CAP act or implementation | scope review | `PASS` |
| G77-05 finding completeness | seventeen exact resolution rows | one-to-one assessment comparison | `PASS` |
| first-time enrollment | source -> subject/actor -> challenge -> presentation -> envelope | topology/DAG review | `PASS` |
| Human source semantics | closed issuer/profile/presence/control/namespace | schema/owner review | `PASS` |
| initial trust bootstrap | Ratification-bound one-time authority through sole CHE | authority/DAG review | `PASS` |
| Human Authority | bootstrap root exact; later current-session acts | semantic review | `PASS` |
| sole lifecycle status | initial source plus one current state | state-authority review | `PASS` |
| proof refusal | closed Receipt/reasons/owner | lifecycle review | `PASS` |
| revocation lifecycle | sources/index barrier/manifest/Receipts | crash/owner review | `PASS` |
| binding consumption | authentication-owner commit before CHE advancement | ordering/ownership review | `PASS` |
| Replay completeness | exact source-to-Receipt lineage | dependency review | `PASS` |
| CRO compatibility | complete passive non-secret projection | boundary review | `PASS` |
| Cutover V2 | exact Certification/state/auth binding | cross-contract review | `PASS` |
| rollback safety | V2 auth-preserving target or inactive production | invariant review | `PASS` |
| CAP ordering | Strategy A retained, R5 rebase mandatory | lineage review | `PASS` |
| identity DAG | complete forward graph/no cycles | G76-06 comparison | `PASS` |
| topology | 1 HIC / 1 CHE / 1 chain / 1 path / 0 parallel | route review | `PASS` |
| no implementation/Ratification/activation | report-only mutation | repository review | `PASS` |
| implementation tests | proposal-only generation | scope review | `NOT_APPLICABLE` |
| whitespace integrity | complete report diff | `git diff --check` equivalent | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_06_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  as the sole G77-06 artifact.

No existing file changed.

Unchanged subsystems:

- active Constitution, CAP, CDP, Human Authority, Governance, Production
  Cutover, production status, release, CLIA, HIC, CHE, Conversation, Platform,
  Replay, CRO, Authorization, Workers, runtime, deployment, configuration,
  schema, policy, routing, workflow, and owner chain;
- G77-04, G77-05, and all preceding artifacts;
- G76 Release Decision proposal lineage; and
- all code, tests, credentials, trust roots, sessions, providers, and runtime
  state.

API compatibility:

- No active API, schema, model, validator, serializer, command, profile, route,
  owner, caller, workflow, production, authentication, Ratification,
  Certification, publication, activation, or Constitutional contract changes.

Boundary preservation:

- The proposal grants no Human, authentication, implementation, deployment,
  Ratification, Certification, publication, or activation authority.
- Human Authority remains the sole Human decision source.
- HIC remains transport only and CHE remains sole.
- Replay remains read-only and CRO remains passive.
- Cutover V2 is proposed only and creates no active state.
- The active one-HIC-family, one-CHE, one-owner-chain, one-production-path
  topology remains unchanged, with zero parallel production paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at revision start.

# 6. Certification Verdict

CONSTITUTIONAL_HUMAN_AUTHENTICATION_CAP_PROPOSAL_REVISION_3_ESTABLISHED
