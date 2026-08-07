# 1. Implementation Summary

Generation: G77-04

Report and proposal identity:
G77_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1

Proposal revision: `2`

Proposal status: `PROPOSAL_ONLY_UNASSESSED`

Amendment kind: `ADDITION`

Constitutional baseline: G0 through G77-03. G77-02 is immutable Proposal
Revision 1. G77-03 is its direct authenticated
`UNRESOLVED_CONSTITUTIONAL_IMPACT` G70-03 assessment. Every active predecessor
and every prior proposal remains closed and unchanged.

Authenticated repository identity:

- Commit: `d579c47c509d1dc24563d5a1c675ad183452a640`
- Tree: `9dc2be4129f71762881b324ad9c615feb0cef5dc`
- Subject: `G77-03: assess human authentication constitutional impact`
- Immediate parent: `2d024d34c70fdd1fe716ca03b94f7305133bced8`
- Revision-start worktree state: clean
- Authenticated G77-02 SHA-256:
  `9a40fa5d995534918d8dd0ea5afe4645e6e763b0f551b4b58fa116b928353dec`
- Authenticated G77-03 SHA-256:
  `cbc1d7031568a3c1bb7b975082956f5b394403e96768f57e9902ed18d512dfe5`
- Authenticated G76-06 SHA-256:
  `29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc`
- Authenticated G76-07 SHA-256:
  `c1149c62dea32ffc6b2bb7a3b417cb2079e4cae4905b3a194dcb7c1d127d2532`

Revision predecessor binding:

| Field | Exact binding |
|---|---|
| previous proposal identity | `G77_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1` |
| previous proposal revision | `1` |
| previous proposal digest | `sha256:9a40fa5d995534918d8dd0ea5afe4645e6e763b0f551b4b58fa116b928353dec` |
| previous proposal status | `PROPOSAL_ONLY_UNASSESSED` |
| previous assessment identity | `G77_03_CONSTITUTIONAL_IMPACT_ASSESSMENT_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1` |
| previous assessment digest | `sha256:cbc1d7031568a3c1bb7b975082956f5b394403e96768f57e9902ed18d512dfe5` |
| previous assessment class | `UNRESOLVED_CONSTITUTIONAL_IMPACT` |
| identity-model identity | `G76_06_CONSTITUTIONAL_ARTIFACT_IDENTITY_MODEL_RECONSTRUCTION_REPORT_V1` |
| identity-model digest | `sha256:29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc` |
| competing proposal identity | `G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_RELEASE_DECISION_ARTIFACT_V1` |
| competing proposal digest | `sha256:c1149c62dea32ffc6b2bb7a3b417cb2079e4cae4905b3a194dcb7c1d127d2532` |

Constitutional Gap identity:
`G77_01_GATE_0B_PRODUCTION_HUMAN_AUTHENTICATION_NORM_ABSENT`

Target Constitutional artifact:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED`

Target Constitutional version: `V1`

Proposed successor identity:
`AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_HUMAN_AUTHENTICATION_REVISION_2_PROPOSED`

Proposed successor version:
`V1.1-HUMAN-AUTHENTICATION-R2-PROPOSED`

Proposed Constitutional capability identity:
`CANONICAL_PRODUCTION_HUMAN_IDENTITY_AUTHENTICATION_MODEL_V1`

Proposed Constitutional owner:
`CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Invariants; Governance Enforcement Hierarchy; Governance
Lineage Model; G69-02 Canonical CHE Request; G69-03/G69-05 CHE Continuation and
advancement; G69-07 Canonical Human Authority Act; G69-11 CHE evidence
correlation; G69-13 complete HIC conformance; G69-18 Replay and CRO; G69-19
Production Cutover; G70-02 Constitutional Amendment Proposal; G70-03 Impact
Assessment; G70-04 Human Ratification; G70-06 publication and activation;
G70-07 CAP Closure; G72-00 Constitutional Core Baseline; G73-00 Human
Constitution; G76-06 Constitutional Artifact Identity Model; G76-07 Release
Decision Proposal Revision 4; G77-01 Gate 0 classification; G77-02 Human
Authentication Proposal Revision 1; and G77-03 Impact Assessment.

Reporting date: 2026-08-07.

Objective:

Create the exact Revision 2 successor of G77-02 and resolve every mandatory
G77-03 blocking impact. Define only the missing Human Authentication
Constitutional norms. Do not implement, Ratify, certify, publish, activate,
deploy, modify CDP, or mutate runtime behavior or state.

Revision result:

Revision 2 retains Revision 1's bounded, provider-neutral authentication
model and replaces its incomplete boundaries with one closed lifecycle:

~~~text
Human
-> one canonical HIC transports one authentication-only Request
-> sole CHE validates closed form and exact capability
-> CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER
-> sole CHE Response / Continuation
-> same canonical HIC presents mechanically

after exact Human-subject proof and session establishment:

Human production Request + one Request-specific admission binding
-> same canonical HIC
-> same sole CHE
-> existing single owner chain and production path
~~~

No Human proof reaches the authentication owner before CHE. CHE admits only
three closed bootstrap capabilities:

~~~text
HUMAN_AUTHENTICATION_CHALLENGE_REQUEST
HUMAN_AUTHENTICATION_PROOF_RESPONSE
HUMAN_AUTHENTICATION_SESSION_CLOSE
~~~

They are authentication-control capabilities, not semantic or production
workflows. Their only eligible owner is the authentication owner. They cannot
reach Conversation semantics, Governance decisions, Authorization, Workers,
mutation, or production execution.

Revision 2 adds a canonical Human-subject chain. A certified issuer assertion
must classify the subject exactly as `HUMAN_NATURAL_PERSON`. The
authentication owner normalizes that source into one
`CanonicalCredentialSubjectIdentityV1`, verifies challenge-bound proof, and
creates one `AuthenticatedHumanSubjectAssertionV1`. The production actor
identity is deterministically derived from the finalized credential-subject
identity, actor namespace, and deployment scope. Device, workload, agent,
service, model, process, machine, or mere credential-control evidence is
rejected as a Human subject even when its cryptography is valid.

Revision 2 separates a certified trust-root candidate from operational trust:

~~~text
certified HumanAuthenticationTrustRootV1 candidate
-> HumanAuthenticationTrustRootTransitionIntentV1
-> exact CanonicalHumanAuthorityActV1 targeting that finalized intent
-> HumanAuthenticationTrustRootTransitionV1
-> atomic HumanAuthenticationTrustRootActiveHeadV1 replacement
-> read-back HumanAuthenticationTrustRootTransitionReceiptV1
~~~

The authentication owner owns validation, transition execution, and custody;
it cannot issue the Human authority on which activation, planned rotation,
retirement, or rollback depends. Exactly one active head exists for each
deployment/proof-profile/audience tuple. Revocation uses a closed
`HumanAuthenticationRevocationEvidenceV1` source model and a deterministic
`HumanAuthenticationRevocationV1` application. No implementation may invent
an activating or revoking authority.

Revision 2 closes session and recovery behavior through immutable lifecycle
transitions and read-back receipts. A failed or uncertain attempt is never
treated as success. Repeated identical Requests use the same idempotency
identity and return the exact recorded disposition; conflicting duplicates
fail closed. A committed receipt may be reconstructed, but Replay cannot
create one. A terminal challenge, session, root generation, or admission
binding never becomes active again.

Competing successor ordering is Strategy A:

~~~text
AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED
-> proposed Human Authentication R2 successor
-> future active authenticated Human Authentication successor
-> required Release Decision Proposal Revision 5 rebase
-> future composed Release Decision successor
~~~

G76-07 Revision 4 remains immutable proposal evidence but may not proceed to
Ratification, Certification, publication, or activation against V1 after this
successor activates. Its next revision must bind the exact activated Human
Authentication predecessor identity/digest, preserve its already assessed
responsibilities, receive a new G70-03 assessment, and traverse the remaining
CAP stages. Two active successors and parallel Constitutional baselines are
prohibited.

Authentication becomes mandatory only through a later governed production
cutover after Constitutional activation, CDP implementation and Certification,
one active trust-root head, and migration readiness. Every pre-successor or
pre-cutover session and pending Request receives no grandfathered production
authority. Rollback preserves all evidence and terminates affected sessions
and bindings; it never revives old authentication authority.

All G77-03 blockers are resolved in proposal content. This is not an Impact
Assessment conclusion. Revision 2 remains:

~~~text
PROPOSAL_ONLY_UNASSESSED
~~~

It requires a new complete G70-03 Impact Assessment before any Human
Ratification. No implementation authority exists unless the complete CAP
lifecycle later activates the exact successor, after which a separately
authorized CDP generation remains mandatory.

Added artifact:

- `docs/governance/G77_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  — this proposal-only G48 Revision 2 artifact.

Intentionally unchanged:

- G77-02, G77-03, G76-06, G76-07, and every G0 through G77-01 artifact;
- active Constitution, CAP, CDP, Human Authority, Production Cutover, CLIA,
  HIC, CHE, Replay, CRO, Governance, release, deployment, routing, workflow,
  owner-chain, and runtime behavior;
- all code, tests, schemas, configuration, credentials, trust roots, sessions,
  providers, and runtime state; and
- every G76 Release Decision proposal byte and historical assessment.

Architectural boundaries preserved by this proposal stage:

- exactly one canonical production HIC family remains;
- exactly one CHE remains and mediates authentication bootstrap;
- HIC remains transport only;
- exactly one production owner chain remains;
- exactly one production path remains;
- zero parallel production paths remain;
- Human Authority remains the sole Human decision source;
- authentication remains identity attribution only;
- Replay remains read-only and non-authoritative;
- CRO remains passive and non-authoritative; and
- no proposed artifact or capability is active.

## Revision 1 -> Revision 2 Comparison Matrix

| Domain | Revision 1 | Revision 2 successor |
|---|---|---|
| bootstrap ingress | direct HIC-to-authentication-owner edge before CHE | all challenge, proof, and close Requests pass first through sole CHE |
| CHE capabilities | production admission binding only | three closed authentication-control capabilities plus existing production admission |
| Human subject | free credential/verified subject references | canonical credential subject plus exact HUMAN subject assertion and actor derivation |
| trust root | candidate carried mutable-looking status | immutable candidate, finalized intent, authority act, applied transition, atomic active-head snapshot, read-back receipt |
| activation authority | not exact | exact CanonicalHumanAuthorityActV1 plus validated candidate Certification |
| revocation evidence | identity/digest references without source contract | closed evidence artifact, source authority kinds, target model, propagation |
| credential subject target | no canonical identity/digest model | `CanonicalCredentialSubjectIdentityV1` |
| session close | prose control | exact close control, lifecycle transition, state commit, receipt |
| failure/recovery | incomplete | closed transition kinds, idempotency, duplicate, crash, uncertainty, and retry rules |
| CAP ordering | deferred | Strategy A fixed; G76-07 must be rebased after Human Authentication activation |
| cutover migration | high-level fail closed | exact prerequisite order, reauthentication barrier, rollback and historical rules |
| identity graph | acyclic core with missing nodes | finite complete DAG with no forward, self, or circular references |

## G77-03 Blocker Resolution Matrix

| G77-03 blocker | Revision 2 evidence | Resolution |
|---|---|---|
| sole-CHE authentication bootstrap | three exclusive CHE capabilities and one owner transition | `RESOLVED` |
| Human-subject identity binding | canonical credential subject, HUMAN assertion, deterministic actor mapping | `RESOLVED` |
| trust-root activation authority | candidate/intent/Human act/transition/head/receipt | `RESOLVED` |
| revocation source and target model | closed evidence artifact, credential subject identity, propagation rules | `RESOLVED` |
| session terminal controls and recovery | close control, lifecycle transition/receipt, closed crash/retry matrix | `RESOLVED` |
| competing active-successor lineage | Strategy A and mandatory G76 Revision 5 rebase | `RESOLVED` |
| Production Cutover migration/rollback | no-grandfather barrier and exact activation/rollback order | `RESOLVED` |

No mandatory blocker is classified `PARTIAL`. A later G70-03 assessment must
independently confirm or reject these proposal claims.

## Authentication Bootstrap Topology

### Closed Request modality

All three capabilities reuse the existing closed CHE modality and use:

~~~text
request_modality = STRUCTURED
exclusive_capability = one of the three HUMAN_AUTHENTICATION_* capabilities
eligible_owner = CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER
entry_owner = CANONICAL_HUMAN_ENTRY_OWNER
hic_family = CANONICAL_PRODUCTION_HIC_FAMILY
downstream_execution_eligible = false
~~~

The existing closed CHE Request is versioned only by a future successor
contract after activation; no metadata convention may create a capability.
The Request binds capability, Human-supplied payload digest, interaction,
interface, adapter, deployment/runtime/workspace scope, CHE, HIC family,
idempotency identity, and any required Continuation identity/digest.

### Capability contracts

| Capability | Exclusive semantics | Continuation | Source binding | Response class | Idempotency and duplicate rule | Terminal conditions |
|---|---|---|---|---|---|---|
| `HUMAN_AUTHENTICATION_CHALLENGE_REQUEST` | request one fresh challenge for one actor claim and session-request scope; no proof or production act | absent for first attempt; exact prior terminal/replacement Continuation required when replacing an existing attempt | actor claim, session-request identity, audience, scopes, proof profile, interface, HIC, CHE | `HUMAN_AUTHENTICATION_CHALLENGE_RESPONSE` containing challenge identity/digest and exact proof Continuation, or terminal refusal | same key/same digest returns same committed challenge/response; same key/different digest fails; active challenge cannot be duplicated | challenge committed, refused, expired, cancelled, or replaced |
| `HUMAN_AUTHENTICATION_PROOF_RESPONSE` | present one proof envelope for the one issued challenge; cannot request any semantic act | exact challenge Response Continuation mandatory | challenge identity/digest, proof envelope identity/digest, credential-subject source identity/digest, same session request and scopes | `HUMAN_AUTHENTICATION_VERIFICATION_RESPONSE` containing rejected/refused result or committed session/assertion identities and session-control Continuation | same key/same digest returns exact committed result; a consumed challenge cannot be reverified; conflict fails | verified session commit, rejection, refusal, challenge expiry/cancellation/replacement, or revocation |
| `HUMAN_AUTHENTICATION_SESSION_CLOSE` | request terminal close of exactly one active authenticated session | exact session-control Continuation mandatory | session identity/digest, actor identity, close reason, scopes, close-control payload digest | `HUMAN_AUTHENTICATION_SESSION_CLOSE_RESPONSE` containing terminal state and receipt, or exact already-terminal result | same key/same digest returns same close receipt; conflicting close fails; already terminal never changes | session `CLOSED`, `EXPIRED`, or `REVOKED` |

### Owner transition and response rules

CHE performs only closed-form, capability, Continuation, scope, correlation,
and eligible-owner validation. It then creates one exact owner transition to
the authentication owner. The authentication owner returns one canonical
Response correlated through CHE. CHE validates the Response owner and
Continuation lineage and HIC presents it mechanically.

No authentication-control Request may be transformed into or forwarded as:

- a Conversation or semantic Request;
- a Governance decision;
- an Approval, Ratification, or Authorization;
- a Worker or tool invocation;
- a mutation or release act;
- a Production Cutover transition; or
- a production execution Request.

HIC may carry bytes, opaque proof material, references, and mechanical
presentation. It cannot inspect proof semantics, select proof profile or owner,
declare identity, issue a challenge, create a session, repair a Continuation,
retry without the same Human act, or choose a production route.

## Human Subject Proof Model

### `CanonicalCredentialSubjectIdentityV1`

Closed fields:

~~~text
artifact_type
artifact_version
credential_subject_identity
credential_subject_digest
issuer_assertion_identity
issuer_assertion_digest
issuer_authority_identity
issuer_class
subject_assertion_profile_identity
subject_assertion_profile_version
subject_class
opaque_subject_key_digest
trust_root_identity
trust_root_digest
deployment_scope_identity
audience_identity
valid_from
valid_until
source_status
producing_owner
metadata
~~~

`subject_class` must be exactly `HUMAN_NATURAL_PERSON`. `issuer_class` must be
exactly `CERTIFIED_HUMAN_IDENTITY_ASSERTION_ISSUER` and must be authorized by
the active trust root's subject-assertion profile. `source_status` is
`VALIDATED_CURRENT` at creation. The opaque subject key is a non-secret digest;
it is not a username, display name, email address, device identifier, or
reusable credential.

The authentication owner produces this canonical artifact only after it
validates the exact signed issuer assertion, issuer authority, HUMAN subject
classification, validity, scope, trust-root relationship, and revocation
status. The issuer assertion remains exact predecessor evidence. The
authentication owner does not decide that a machine is Human; it validates the
certified issuer's exact HUMAN assertion under the active norm.

### Deterministic actor identity

~~~text
actor_identity_payload = {
  actor_identity_version,
  credential_subject_identity,
  credential_subject_digest,
  actor_namespace_identity,
  deployment_scope_identity
}

actor_identity =
  human-actor-sha256:<SHA-256(canonical(actor_identity_payload))>
~~~

The actor identity is derived from an already finalized credential-subject
artifact. It is never derived from display text, HIC input, a device, a model,
or the later Human-subject assertion. This direction avoids a circular edge.

### `AuthenticatedHumanSubjectAssertionV1`

Closed fields:

~~~text
artifact_type
artifact_version
human_subject_assertion_identity
human_subject_assertion_digest
credential_subject_identity
credential_subject_digest
verification_receipt_identity
verification_receipt_digest
trust_root_identity
trust_root_digest
challenge_identity
challenge_digest
proof_envelope_identity
proof_envelope_digest
actor_identity
subject_class
human_presence_class
proof_control_class
issuer_authority_identity
subject_assertion_profile_identity
audience_identity
deployment_scope_identity
runtime_scope_identity
workspace_scope_identity
canonical_hic_family_identity
che_identity
asserted_at
valid_until
assertion_status
producing_owner
metadata
~~~

`subject_class` is exactly `HUMAN_NATURAL_PERSON`.
`human_presence_class` is exactly one permitted certified class requiring an
active Human proof event. `assertion_status` at creation is exactly
`AUTHENTICATED_HUMAN_CURRENT`. `proof_control_class` must prove control by the
same canonical credential subject. A device or workload attestation may be
supplemental evidence but cannot supply either HUMAN classification or Human
presence by itself.

Validation requires exact equality among credential subject, proof, receipt,
actor derivation, challenge, trust root, issuer, audience, deployment/runtime/
workspace scopes, time, HIC family, and CHE. A principal classified as
`DEVICE`, `WORKLOAD`, `AGENT`, `SERVICE`, `MODEL`, `PROCESS`, `MACHINE`,
`UNKNOWN`, or any value other than `HUMAN_NATURAL_PERSON` fails closed and no
session is created.

Replay reconstructs the assertion from committed predecessors and never
recontacts an issuer or changes classification. CRO may observe identity,
digest, HUMAN/failed classification result, scope, and time, but never source
personal attributes, proof material, or opaque subject values.

### Proof, receipt, and session binding corrections

Revision 2 replaces Revision 1's free subject references. The finalized
`HumanAuthenticationProofEnvelopeV1` binds
`credential_subject_identity`/`credential_subject_digest` and the exact issuer
assertion identity/digest. `HumanAuthenticationVerificationReceiptV1` binds
that same canonical credential subject and records cryptographic result but
cannot independently declare a different Human classification.

`AuthenticatedHumanSessionV1` replaces `credential_subject_reference` with:

~~~text
credential_subject_identity
credential_subject_digest
human_subject_assertion_identity
human_subject_assertion_digest
actor_identity
subject_class = HUMAN_NATURAL_PERSON
~~~

The session validator revalidates the complete credential subject -> proof ->
receipt -> Human assertion chain. No free string, provider locator, or mutable
external subject reference can support a session.

## Trust Root Authority Lifecycle

### Candidate

`HumanAuthenticationTrustRootV1` is revised as an immutable candidate. Its
identity payload removes Revision 1's `trust_root_status` and
`certification_reference` fields and adds exactly:

~~~text
subject_assertion_profile_identity
subject_assertion_profile_version
issuer_authority_class
candidate_status = CANDIDATE
~~~

It does not contain mutable `ACTIVE`, `SUPERSEDED`, `REVOKED`, or `RETIRED`
status and it does not reference its later Certification. The candidate is
finalized first; a separate CDP Certification then depends on that candidate;
the later transition depends on both. Operational statuses are derived from
transitions and the current head. This direction prevents a candidate <->
Certification identity cycle.

### `HumanAuthenticationTrustRootTransitionIntentV1`

The immutable intent is finalized before any Human decision. Its closed fields
are:

~~~text
artifact_type
artifact_version
trust_root_transition_intent_identity
trust_root_transition_intent_digest
transition_kind
candidate_trust_root_identity
candidate_trust_root_digest
predecessor_active_head_identity
predecessor_active_head_digest
predecessor_trust_root_identity
predecessor_trust_root_digest
candidate_certification_identity
candidate_certification_digest
revocation_evidence_identity
revocation_evidence_digest
rollback_target_head_identity
rollback_target_head_digest
deployment_scope_identity
proof_profile_identity
audience_identity
intended_head_status
intended_effective_at
transition_idempotency_identity
proposing_owner
metadata
~~~

Inapplicable references use the exact canonical null. The intent contains no
Human Authority Act, applied transition, active head, Receipt, Replay, or CRO
reference. The Human act targets this finalized intent identity/digest.

### `HumanAuthenticationTrustRootTransitionV1`

Closed fields:

~~~text
artifact_type
artifact_version
trust_root_transition_identity
trust_root_transition_digest
trust_root_transition_intent_identity
trust_root_transition_intent_digest
transition_kind
candidate_trust_root_identity
candidate_trust_root_digest
predecessor_active_head_identity
predecessor_active_head_digest
predecessor_trust_root_identity
predecessor_trust_root_digest
candidate_certification_identity
candidate_certification_digest
human_authority_act_identity
human_authority_act_digest
revocation_evidence_identity
revocation_evidence_digest
rollback_target_head_identity
rollback_target_head_digest
deployment_scope_identity
proof_profile_identity
audience_identity
intended_head_status
intended_effective_at
transition_idempotency_identity
transition_owner
metadata
~~~

`transition_kind` is exactly `INITIAL_ACTIVATION`, `ROTATION`, `SUPERSESSION`,
`REVOCATION`, `RETIREMENT`, or `ROLLBACK`. Inapplicable references are the
exact canonical null value. Initial activation requires no predecessor head;
every other transition binds the exact current head. Activation, rotation,
supersession, retirement, and rollback require a valid
`CanonicalHumanAuthorityActV1` whose exact target is the finalized transition
intent and whose payload binds candidate/head, scope, and effect. Revocation
requires either that Human act
or one admissible terminal revocation-evidence artifact. Every candidate
activation or rollback requires the exact candidate Certification.

The transition owner is exactly
`CANONICAL_HUMAN_IDENTITY_AUTHENTICATION_OWNER`. It validates and applies the
authority but cannot create, infer, widen, or repair it.

The Human act uses the existing `AUTHORIZATION` authority kind and the sole
CHE. Initial activation occurs before authentication-required Production
Cutover and therefore uses the already certified pre-cutover Human Authority
profile for the exact deployment scope; that profile cannot create a
production authenticated session or production Request. After authentication
cutover, later Human-directed trust transitions require a current
`AuthenticatedHumanSessionV1` and Request-specific binding through the same
sole CHE. This is a temporal bootstrap rule, not a second ingress or production
path.

### `HumanAuthenticationTrustRootActiveHeadV1`

Closed fields:

~~~text
artifact_type
artifact_version
active_head_identity
active_head_digest
predecessor_active_head_identity
predecessor_active_head_digest
applied_transition_identity
applied_transition_digest
applied_revocation_identity
applied_revocation_digest
active_trust_root_identity
active_trust_root_digest
deployment_scope_identity
proof_profile_identity
audience_identity
head_generation
head_status
effective_at
descendant_session_policy
producing_owner
metadata
~~~

`head_status` is `ACTIVE`, `REVOKED`, or `RETIRED`. A tuple may have exactly
one current head and at most one `ACTIVE` root. The head snapshot is immutable;
the revocation references are exact canonical null except for `REVOCATION`.
An owner-local current-head pointer is atomically replaced under one exclusive
transition lock. The owner flushes the complete snapshot, atomically replaces
the pointer, re-reads it, validates identity/digest, predecessor, transition,
generation, and singleton tuple, then emits the receipt. Missing, corrupt,
conflicting, multiply active, or unreadable state fails closed.

### `HumanAuthenticationTrustRootTransitionReceiptV1`

Closed fields:

~~~text
artifact_type
artifact_version
trust_root_transition_receipt_identity
trust_root_transition_receipt_digest
trust_root_transition_intent_identity
trust_root_transition_intent_digest
trust_root_transition_identity
trust_root_transition_digest
predecessor_active_head_identity
predecessor_active_head_digest
committed_active_head_identity
committed_active_head_digest
read_back_digest
commit_result
committed_at
transition_idempotency_identity
producing_owner
metadata
~~~

`commit_result` is exactly `COMMITTED` or `ALREADY_COMMITTED_IDENTICAL`. The
receipt is produced only after read-back. It may not be referenced by the
intent, transition, or head from which it derives.

### Descendant effects

| Transition | Prior root | Existing sessions | Existing bindings | New proof |
|---|---|---|---|---|
| initial activation | none | none authorized | none authorized | permitted under active root |
| rotation/supersession | terminal for new proof | `REAUTHENTICATION_REQUIRED` before next production Request | immediately terminal | only under new root |
| revocation | `REVOKED` | immediately `REVOKED` | immediately `REVOKED` | prohibited |
| retirement | `RETIRED` | immediately terminal | immediately terminal | prohibited |
| rollback | replaced head preserved | all sessions from replaced generation terminal | all bindings from replaced generation terminal | only under exact rollback head after validation |

No head transition reactivates any prior session or binding. Rollback changes
the current trust-root head only; every Human must authenticate anew.
The committed head generation is the immediate authoritative admission
barrier: any descendant carrying an older or terminalized generation fails
closed even if owner-local terminal projection receipts are still being
materialized. Projection delay can never preserve production authority.

## Revocation Model

### `HumanAuthenticationRevocationEvidenceV1`

Closed fields:

~~~text
artifact_type
artifact_version
revocation_evidence_identity
revocation_evidence_digest
evidence_kind
source_authority_owner
source_artifact_identity
source_artifact_digest
target_type
target_identity
target_digest
trust_root_identity
trust_root_digest
deployment_scope_identity
revocation_reason
observed_at
effective_at
evidence_status
producing_owner
metadata
~~~

The producing owner is exactly the authentication owner, which normalizes and
validates one finalized authoritative source. It does not originate the source
authority. Admissible evidence kinds and exact source owners are:

| Evidence kind | Required source authority | Eligible target |
|---|---|---|
| `HUMAN_AUTHORITY_REVOCATION_ACT` | Human Authority through exact `CanonicalHumanAuthorityActV1` | root, credential subject, session |
| `CERTIFIED_ISSUER_CREDENTIAL_REVOCATION` | issuer authority named by active trust root and validated revocation source | credential subject |
| `CERTIFIED_SECURITY_COMPROMISE_ASSERTION` | exact security authority class named by active trust root | root or credential subject |

No log entry, model output, operator note, network condition, configuration
flag, unbound provider response, or implementation choice is admissible.
Session close and deterministic expiry use their own lifecycle transitions;
they are not mislabeled as revocation evidence.

### Target identities

`target_type` is exactly `TRUST_ROOT`, `CREDENTIAL_SUBJECT`, or
`AUTHENTICATED_SESSION`. Each target identity/digest resolves respectively to
`HumanAuthenticationTrustRootV1`, `CanonicalCredentialSubjectIdentityV1`, or
`AuthenticatedHumanSessionV1`. Missing, mutable, mismatched, unknown, or
cross-scope targets fail closed.

### Revocation application

`HumanAuthenticationRevocationV1` binds the evidence artifact, exact target,
current head/generation, reason, effective time, propagation set, transition
idempotency identity, and authentication owner. Application is monotonic and
atomic. Root revocation propagates to all descendant assertions, sessions,
and bindings. Credential-subject revocation propagates to every assertion,
session, and binding for that subject. Session revocation propagates to every
binding for that session. No descendant is deleted; current status becomes
terminal and all source evidence remains immutable.

For a root target, exact ordering is revocation evidence -> trust transition
intent -> optional Human act -> applied trust transition -> root revocation ->
active-head snapshot binding both the transition and revocation -> read-back
receipt. For a credential subject or session target, revocation precedes the
corresponding lifecycle transition/state/receipt. The active-head generation
or revocation epoch supplies the immediate fail-closed barrier, so descendant
projection work cannot create an authorization window.

Replay reconstructs source evidence, revocation, propagation, and terminal
receipts without applying or reversing them. CRO observes only identities,
digests, target type, non-sensitive reason class, times, status, and scope.
CRO cannot submit evidence, revoke, restore, retry, or control propagation.

## Session Lifecycle and Recovery Matrix

### Canonical lifecycle artifacts

Revision 2 adds:

- `HumanAuthenticationSessionCloseV1` — exact close control produced by the
  authentication owner from the CHE-admitted close Request and current actor/
  session binding;
- `HumanAuthenticationLifecycleTransitionV1` — immutable transition intent
  binding exact predecessor, authority basis, intended terminal or advancing
  state, evidence, idempotency, and scope;
- `HumanAuthenticationLifecycleStateV1` — immutable committed status snapshot
  pointing to the applied transition and predecessor state;
- `HumanAuthenticationLifecycleReceiptV1` — post-commit read-back evidence;
  and
- `HumanAuthenticationAdmissionConsumptionReceiptV1` — CHE-owned single-use
  binding-consumption evidence correlated to existing CHE advancement and
  idempotency evidence.

The lifecycle transition closed fields are:

~~~text
artifact_type
artifact_version
lifecycle_transition_identity
lifecycle_transition_digest
subject_type
subject_identity
subject_digest
predecessor_state_identity
predecessor_state_digest
transition_kind
authority_basis_type
authority_artifact_identity
authority_artifact_digest
evidence_identity
evidence_digest
intended_status
attempt_identity
idempotency_identity
continuation_identity
continuation_digest
deployment_scope_identity
runtime_scope_identity
workspace_scope_identity
effective_at
producing_owner
metadata
~~~

The transition contains no successor state, Receipt, Replay, or CRO reference.
The successor state references it. The Receipt references the committed state.

### Exact terminal and state schemas

`HumanAuthenticationSessionCloseV1` has the closed payload:

~~~text
artifact_type
artifact_version
session_close_identity
session_close_digest
che_request_identity
che_request_digest
continuation_identity
continuation_digest
authenticated_session_identity
authenticated_session_digest
human_subject_assertion_identity
human_subject_assertion_digest
actor_identity
close_reason
close_requested_at
idempotency_identity
deployment_scope_identity
runtime_scope_identity
workspace_scope_identity
producing_owner
metadata
~~~

`HumanAuthenticationLifecycleStateV1` has the closed payload:

~~~text
artifact_type
artifact_version
lifecycle_state_identity
lifecycle_state_digest
subject_type
subject_identity
subject_digest
predecessor_state_identity
predecessor_state_digest
applied_transition_identity
applied_transition_digest
state_generation
current_status
revocation_epoch
committed_at
producing_owner
metadata
~~~

`HumanAuthenticationLifecycleReceiptV1` has the closed payload:

~~~text
artifact_type
artifact_version
lifecycle_receipt_identity
lifecycle_receipt_digest
lifecycle_transition_identity
lifecycle_transition_digest
committed_state_identity
committed_state_digest
read_back_digest
commit_result
idempotency_identity
committed_at
producing_owner
metadata
~~~

`HumanAuthenticationAdmissionConsumptionReceiptV1` has the closed payload:

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
che_request_identity
che_request_digest
binding_predecessor_state_identity
binding_predecessor_state_digest
binding_consumed_state_identity
binding_consumed_state_digest
idempotency_identity
consumption_result
consumed_at
producing_owner
metadata
~~~

Receipt `commit_result`/`consumption_result` values are exactly `COMMITTED`,
`ALREADY_COMMITTED_IDENTICAL`, `CONSUMED`, or
`ALREADY_CONSUMED_IDENTICAL` as applicable to their artifact. A Receipt never
references a later owner advancement, Replay, CRO observation, or presentation.

### Closed transition kinds

~~~text
CHALLENGE_ISSUED
CHALLENGE_CONSUMED
CHALLENGE_EXPIRED
CHALLENGE_CANCELLED
CHALLENGE_REPLACED
PROOF_VERIFIED
PROOF_REJECTED
PROOF_REFUSED
SESSION_COMMITTED
SESSION_CLOSED
SESSION_EXPIRED
SESSION_REVOKED
BINDING_ISSUED
BINDING_CONSUMED
BINDING_EXPIRED
BINDING_REVOKED
DELIVERY_UNCERTAIN_RECORDED
~~~

`PROOF_REJECTED` means a complete verifier evaluation returned invalid proof.
`PROOF_REFUSED` means verification did not run because challenge, root, scope,
subject, time, revocation, payload, or authority preconditions failed. Neither
may create a session. `DELIVERY_UNCERTAIN_RECORDED` records presentation or
receipt uncertainty and never changes an authentication subject to success.

### Recovery matrix

| Condition | Authoritative evidence and transition | Retry/idempotency rule | Result |
|---|---|---|---|
| session close | exact CHE close Request -> `HumanAuthenticationSessionCloseV1` -> `SESSION_CLOSED` | same key returns close receipt; conflict fails | terminal; never active again |
| proof rejected | verifier receipt `REJECTED` -> `PROOF_REJECTED` | same proof/challenge returns same rejection | no session |
| proof refused | exact failed precondition -> receipt `REFUSED` -> `PROOF_REFUSED` | retry needs new admissible attempt unless same response requested | no session |
| challenge expiry | committed expiry time -> `CHALLENGE_EXPIRED` | expired challenge cannot be retried | new challenge Request required |
| challenge cancellation | exact CHE control or superseding terminal policy -> `CHALLENGE_CANCELLED` | duplicate returns same receipt | terminal |
| challenge replacement | prior challenge terminalized by `CHALLENGE_REPLACED`; new challenge binds prior transition | same replacement key returns same new challenge | exactly one issued challenge |
| delivery uncertainty | `DELIVERY_UNCERTAIN_RECORDED` without success inference | same Request/key retrieves exact committed response; no new act | status derives only from committed source |
| duplicate retry | same idempotency key and canonical digest | return same committed disposition | no duplicate verification/session |
| conflicting duplicate | same key, different digest or scope | fail closed and record conflict | no advancement |
| crash before verification | no verification receipt exists | exact proof may be resubmitted under same key while challenge remains valid; evaluation starts from committed predecessors | never inferred verified |
| crash after verification before session commit | verified receipt exists, no session Receipt | same key may commit the one deterministic session if all predecessors remain current; otherwise terminal refusal | at most one session |
| crash after session commit | committed lifecycle state exists | read-back reconstructs exact Receipt/Response | no new session |
| binding issuance uncertainty | no binding Receipt means no usable binding | same key may recover one deterministic binding from current session | never inferred issued |
| binding consumption uncertainty | CHE consumption receipt controls | exact Request retry uses existing CHE idempotency/advancement record; absent receipt cannot infer downstream execution | at most one advancement |
| terminal revocation | exact revocation and propagation receipts | duplicates return same terminal result | never reactivated |

All state commits use one exclusive owner transition, atomic replacement of
the exact current-state projection, flush, read-back validation, and a
post-commit Receipt. Orphan source or transition artifacts do not establish
current success. Recovery may finish or reproduce only the same deterministic
transition from committed predecessors; it cannot select a different actor,
scope, proof, session, binding, or outcome.

Replay traverses committed source -> transition -> state -> receipt in order.
It exposes orphans and uncertainty and cannot commit, retry, verify, close,
expire, revoke, or repair. CRO passively observes the same non-secret
identities/statuses and cannot influence recovery.

## CAP Successor Ordering Decision

Revision 2 selects Strategy A.

| Lineage position | Exact Constitutional state |
|---|---|
| active predecessor | `AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED` |
| next proposed successor | `AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_1_HUMAN_AUTHENTICATION_REVISION_2_PROPOSED` |
| proposal predecessor | exact active V1 identity/digest plus G77-02 Revision 1 identity/digest |
| competing G76-07 status | immutable inactive proposal evidence; prohibited from activation against stale V1 after auth successor activation |
| required next Release Decision proposal | Revision 5, rebased on exact activated Human Authentication successor identity/digest |
| composed future successor | Human Authentication baseline plus Release Decision addition through the complete separate CAP lifecycle |

G76-07 is neither deleted nor silently modified. Before Human Authentication
activation it remains inactive competing proposal evidence. Once Human
Authentication activates, V1 is stale for new activation and G76-07 cannot
advance. Revision 5 must expressly supersede Revision 4 as a proposal, bind
the authenticated successor, reassess compatibility, and undergo Impact
Assessment, Human Ratification, Certification, publication, and activation.

No stage may activate both branches, merge them during CDP, or infer a
composed baseline from repository presence. CAP remains the sole mechanism for
the later rebase and successor.

## Production Cutover Compatibility

### Mandatory ordering

~~~text
Human Authentication Constitutional successor activated
-> separate CDP implementation and Certification
-> exact production trust-root candidate certified
-> exact Human-authorized trust-root transition
-> one active trust-root head validated by read-back
-> authentication migration readiness evidence
-> Release Decision successor rebased/activated and implemented as required
-> terminal Production Cutover package binds authentication profile/head
-> release/cutover owner atomically activates authentication-required state
-> every new production Human Request requires current binding
~~~

Production Cutover remains owned by the existing release/cutover
production-status owner. The authentication owner supplies validated status
evidence only. Neither authentication nor a trust-root transition can activate
Production Cutover.

### Migration and rollback

| Condition | Constitutional treatment |
|---|---|
| pre-successor Human session | historical only; never an authenticated production session |
| pre-cutover unauthenticated production session | terminal for new production admission at cutover |
| pending pre-cutover Request | not grandfathered; Human must resubmit through authentication and receive a new Request/binding |
| historical Request/evidence | retained read-only for Replay and passive CRO; no authority restored |
| active session under cutover root | usable only while root, assertion, session, binding scope, time, and revocation epoch remain current |
| Production Cutover rollback | Cutover state follows existing owner; all sessions/bindings created under rolled-back production generation become terminal |
| trust-root rollback | separate Human-authorized trust transition; does not follow Cutover automatically; requires fresh Human authentication |
| later re-cutover | no session revival; every Human reauthenticates under then-current head |

Cutover readiness fails closed if no active trust-root head exists, more than
one head exists, the head/candidate/transition/receipt chain is invalid, the
authentication CDP Certification is absent, migration evidence is incomplete,
or terminal Production Cutover evidence does not bind the exact authentication
profile and head generation.

## Identity Dependency Graph

All artifacts use closed canonical versioned payloads. The identity is a
type-specific namespace plus SHA-256 of the canonical identity payload; the
digest is `sha256:` plus the same SHA-256. Each payload excludes only its own
identity/digest fields. Independently issued Request, Continuation,
idempotency, Human act, and external-source identities are permitted only
under their existing certified owner contracts and must be bound with exact
scope and digest before supporting authority.

~~~text
active Constitutional baseline
  -> certified TrustRoot candidate
      -> TrustRootTransitionIntent
          -> HumanAuthorityAct
              -> TrustRootTransition
                  -> TrustRootActiveHead
                      -> TrustRootTransitionReceipt

issuer source assertion + active TrustRoot
  -> CanonicalCredentialSubjectIdentity

CHE Challenge Request + active TrustRoot
  -> Challenge
      -> CHE Proof Request + ProofEnvelope
          + CanonicalCredentialSubjectIdentity
          -> VerificationReceipt
              -> AuthenticatedHumanSubjectAssertion
                  -> AuthenticatedHumanSession
                      -> AdmissionBinding + independent production Request
                          -> CHE AdmissionConsumptionReceipt

CHE Session Close Request + Session
  -> SessionClose
      -> LifecycleTransition
          -> LifecycleState
              -> LifecycleReceipt

authoritative revocation source + exact target
  -> RevocationEvidence
      -> credential/session Revocation
          -> LifecycleTransition -> LifecycleState -> LifecycleReceipt
      -> root TransitionIntent -> optional HumanAuthorityAct
          -> root Transition -> root Revocation -> TrustRootActiveHead
              -> TrustRootTransitionReceipt

committed owner source/state/receipt
  -> Replay
      -> passive CRO observation
~~~

The production Request does not reference the admission-binding identity; it
is independently finalized and the binding references it as a sidecar.
Therefore Request and binding do not cycle. A transition never references its
successor state or Receipt. A source artifact never references Replay or CRO.
Trust-root and challenge successors reference finalized predecessors only.

Forbidden dependencies include self identity/digest fields in their own hash,
successor-to-predecessor back references, source-to-Receipt references,
source-to-Replay/CRO references, mutable path references as identity, and any
placeholder persisted as evidence. The complete graph is finite and acyclic.

## Reuse Impact Assessment

1. **Which certified Constitutional capabilities are reused?**

   Revision 2 reuses the active Constitution; Human Authority and exact
   `CanonicalHumanAuthorityActV1`; one canonical production HIC family; sole
   CHE; canonical Request, Response, Continuation, owner transition,
   idempotency, delivery, and correlation; G69-18 owner-local Replay and
   passive CRO; G69-19 Production Cutover; complete G70 CAP; G76-06 acyclic
   identity rules; G76-07 as immutable competing proposal evidence; G77-01
   Gate 0B classification; G77-02 Revision 1's bounded authentication core;
   G77-03 blockers; fail-closed validation; and G48 reporting.

2. **Which new Constitutional norms are proposed?**

   Revision 2 proposes authentication-only CHE bootstrap capabilities;
   canonical HUMAN subject and credential-subject identity; deterministic
   actor mapping; candidate/transition/active-head/receipt trust authority;
   closed revocation evidence and propagation; session close and complete
   lifecycle/recovery transitions; Strategy A successor ordering; and exact
   authentication Production Cutover migration/rollback rules. These remain
   one bounded Human-authentication model and introduce no unrelated domain.

3. **Does any certified capability become unreachable?**

   No active capability changes or becomes unreachable because the proposal
   is inactive. If later activated and implemented, existing semantic,
   Governance, Authorization, Worker, Replay, CRO, and Cutover owners remain
   reachable through the same owner chain after exact authenticated CHE
   admission. Unauthenticated production Requests intentionally fail closed.

4. **Does the proposal create a parallel production path?**

   No. Authentication bootstrap and production Requests use the same HIC
   family and the same sole CHE. Authentication control is a bounded owner
   transition, not a second ingress, semantic workflow, or execution route.

5. **Does it decrease or increase the number of production paths?**

   Neither. The active and proposed topology remains exactly one production
   path with zero parallel paths.

# 2. Code Evidence

## Public API

G77-04 adds or changes no runtime API. After a complete CAP lifecycle activates
this successor, a separate CDP generation may propose implementations of only
the defined responsibilities, including conceptually:

~~~text
create_human_authentication_control_request_v1(...)
validate_human_authentication_control_request_v1(...)
create_canonical_credential_subject_identity_v1(...)
create_authenticated_human_subject_assertion_v1(...)
create_human_authentication_trust_root_transition_intent_v1(...)
create_human_authentication_trust_root_transition_v1(...)
activate_human_authentication_trust_root_head_v1(...)
create_human_authentication_revocation_evidence_v1(...)
apply_human_authentication_revocation_v1(...)
create_human_authentication_lifecycle_transition_v1(...)
commit_human_authentication_lifecycle_state_v1(...)
reconstruct_human_authentication_lifecycle_replay_v1(...)
observe_human_authentication_lifecycle_cro_v1(...)
~~~

These are responsibility labels, not implemented functions or authorized
signatures. No constructor, validator, serializer, persistence store, CHE
extension, HIC capability, provider, deployment, migration, or activation API
is introduced by this proposal artifact.

## Orchestration Entry Point

The sole proposed orchestration entry is the existing CHE:

~~~text
Human
-> canonical HIC transports exact authentication-control Request
-> sole CHE validates modality/capability/Continuation/scope
-> exact authentication owner transition
-> authentication owner commits exact evidence or refusal
-> sole CHE validates Response/Continuation lineage
-> same canonical HIC presents mechanically
~~~

After authentication, production admission remains:

~~~text
independently finalized production Request
+ one binding that references that Request
-> same HIC
-> same sole CHE consumes binding exactly once
-> existing owner chain
~~~

## Semantic Reductions

### Bootstrap reduction

~~~text
authentication-control capability in closed set
AND exact sole-CHE admission valid
AND eligible owner exactly authentication owner
-> authentication-only owner transition

otherwise
-> fail closed before owner transition
~~~

### Human-subject reduction

~~~text
cryptographic proof valid
AND issuer assertion subject_class == HUMAN_NATURAL_PERSON
AND credential subject / actor derivation / proof control all equal
-> Human subject assertion eligible

otherwise
-> no Human assertion
-> no authenticated session
~~~

### Trust transition reduction

~~~text
candidate certified
AND transition intent finalized
AND exact transition authority valid
AND predecessor current
AND tuple has one current head
AND atomic commit/read-back valid
-> new active head

otherwise
-> old head unchanged
-> no new proof authority
~~~

### Recovery reduction

~~~text
committed state + valid read-back Receipt
-> exact recorded result may be returned

missing or orphan evidence
-> never infer authentication success
-> retry only exact idempotent transition when still eligible
~~~

### CAP ordering reduction

~~~text
Human Authentication R2 activates from V1
-> G76-07 predecessor becomes stale
-> Release Decision Revision 5 rebase mandatory
-> two V1 successors cannot activate
~~~

## Public Validators

No validator is implemented. A future CDP validator must deterministically
enforce every closed schema and must reject:

- an authentication-control Request that bypasses CHE or names another owner;
- missing, optional-when-required, stale, or mismatched Continuation;
- capability smuggling into semantic or production execution;
- any subject classification other than `HUMAN_NATURAL_PERSON`;
- actor mapping mismatch or device/workload-only evidence;
- uncertified candidate, missing Human transition authority, stale head, or
  multiple active heads;
- undefined revocation source, mutable target, or incomplete propagation;
- session/binding revival, duplicate conflict, or inferred crash success;
- forward, self, or circular identity dependency;
- Production Cutover without exact authentication readiness; and
- activation of two successors from the same V1 predecessor.

## Canonical Data Models

| Model | Exact role | Owner |
|---|---|---|
| authentication-control Request/Response/Continuation | sole-CHE bootstrap and Human presentation lineage | CHE with transport-only HIC |
| `CanonicalCredentialSubjectIdentityV1` | canonical HUMAN credential subject and issuer binding | authentication owner |
| `AuthenticatedHumanSubjectAssertionV1` | exact verified HUMAN/actor assertion | authentication owner |
| `HumanAuthenticationTrustRootV1` | immutable candidate; transition separately requires its later Certification | authentication owner custody |
| `HumanAuthenticationTrustRootTransitionIntentV1` | finalized proposed head change targeted by Human authority | authentication owner |
| `HumanAuthenticationTrustRootTransitionV1` | applied transition binding intent and exact external authority | authentication owner applying external authority |
| `HumanAuthenticationTrustRootActiveHeadV1` | one immutable current-head generation | authentication owner custody |
| `HumanAuthenticationTrustRootTransitionReceiptV1` | post-read-back transition evidence | authentication owner |
| `HumanAuthenticationRevocationEvidenceV1` | normalized authoritative terminal source | authentication owner |
| `HumanAuthenticationRevocationV1` | monotonic target/descendant revocation | authentication owner |
| session/challenge/binding source artifacts | bounded proof and admission lineage | authentication owner |
| lifecycle transition/state/receipt | deterministic advancement and recovery | responsible authentication owner; CHE owns binding consumption receipt |
| Replay | read-only reconstruction | owner-local Replay |
| CRO observation | passive non-secret correlation | passive CRO |

## Deterministic Algorithms

### Artifact derivation

1. Validate the exact closed schema and version.
2. Resolve every already finalized predecessor identity/digest.
3. Reject missing, mutable, forward, self, duplicate-conflicting, or circular
   references.
4. Exclude only the artifact's own identity/digest fields.
5. Canonically serialize all remaining fields.
6. compute SHA-256 once over those bytes.
7. Construct the type namespace identity and `sha256:` digest.
8. Revalidate the completed artifact.
9. Persist only the completed artifact through its exact owner.

### Atomic transition

1. Validate source evidence, authority, current predecessor, scope, and
   idempotency.
2. Construct immutable transition intent without successor references.
3. Acquire one exclusive owner-local transition lock.
4. Revalidate current head/state and singleton constraints.
5. Construct successor state referencing the transition.
6. Flush and atomically replace the exact current-state projection.
7. Re-read and validate the successor state.
8. Emit a Receipt derived from transition and committed state.
9. Return the same Receipt for an exact duplicate; reject conflict.

### Replay and CRO

Replay validates source, transition, state, and Receipt in topological order.
It reports missing/orphan/conflicting evidence and never calls a provider or
changes status. CRO observes the validated Replay result without secret proof
material and without affecting any transition.

## Responsibility Boundaries

| Responsibility | Exact owner | Negative boundary |
|---|---|---|
| express proof/control act | Human | cannot self-certify invalid proof or bypass CHE |
| transport | canonical HIC family | no semantics, verification, owner selection, retry invention, or route creation |
| admit authentication control | sole CHE | no proof decision, trust selection, or Human classification |
| authenticate identity and preserve evidence | authentication owner | no Human decision, semantic interpretation, Authorization, execution, Cutover, or deployment |
| assert Human source status | certified issuer authority class through exact source artifact | cannot issue Human act or production authority |
| authorize trust transitions | Human Authority through exact act; certified terminal source only for closed revocation cases | cannot be inferred by authentication owner |
| activate/custody trust head | authentication owner | applies authority only; cannot create it |
| admit production Request | sole CHE | requires exact current binding; cannot repair failure |
| decide Human meaning | Human Authority and existing semantic owners | authentication supplies attribution only |
| execute production work | existing certified owner chain | unchanged and unreachable from bootstrap capability |
| reconstruct | owner-local Replay | read-only, non-authoritative |
| observe | passive CRO | no control or secret material |
| activate Production Cutover | existing release/cutover production-status owner | authentication cannot activate |
| evolve Constitution | CAP | one exact successor only |
| implement activated norms | CDP | unavailable at proposal stage |

## Repository Evidence

Revision 2 derives only from authenticated Constitutional evidence. G77-02 is
the exact prior proposal. G77-03 supplies the mandatory blockers. G76-06
supplies generic identity rules. G76-07 is immutable competing proposal
evidence. G69-02/03/05 supply the CHE Request, Continuation, idempotency, and
owner-transition model. G69-07 separates authentication evidence from Human
decision authority. G69-13 fixes one HIC family and sole CHE. G69-18 fixes
Replay and CRO. G69-19 fixes Production Cutover ownership. G70 fixes the one-
successor CAP lifecycle.

Historical providers, tests, runtime behavior, configuration, and deployment
state supply no norm and are not used to define the proposal.

# 3. Constitutional Self-Assessment

## Verified

- G77-02, G77-03, G76-06, and G76-07 bytes match their authenticated SHA-256.
- Revision 2 binds the exact Revision 1 and Impact Assessment predecessors.
- Every Human authentication bootstrap Request enters through the sole CHE.
- The three authentication-control capabilities have exact modality, owner,
  Continuation, source, Response, idempotency, duplicate, terminal, and
  negative rules.
- HIC remains transport only and bootstrap cannot enter execution owners.
- The HUMAN subject assertion, credential subject, issuer trust, and actor
  derivation are exact and reject non-Human principals.
- Trust-root candidate, transition authority, current head, atomic commit,
  read-back, lifecycle, rollback, and descendant effects are exact.
- Revocation evidence kinds, source authorities, targets, application,
  propagation, Replay, and CRO rules are closed.
- Session close, proof rejection/refusal, challenge terminal states, delivery
  uncertainty, duplicates, crash points, binding uncertainty, and revocation
  have deterministic fail-closed outcomes.
- Every new artifact follows the G76-06 finite acyclic identity model.
- Strategy A fixes one successor order and requires G76 Release Decision
  Revision 5 to rebase after Human Authentication activation.
- Production Cutover ordering, reauthentication, migration, rollback, and
  historical treatment are exact.
- One HIC family, one CHE, one owner chain, one production path, and zero
  parallel production paths are preserved.
- Human Authority, Replay, CRO, Production Cutover, CAP, and CDP boundaries are
  preserved.
- No implementation, Ratification, Certification, publication, activation,
  deployment, or runtime mutation occurs.

## Not Verified

- Revision 2 has not received its mandatory new G70-03 Impact Assessment.
- No Human Ratification, amendment Certification, publication, or activation
  exists for Revision 2.
- Revision 2 is not active Constitutional law and authorizes no CDP work.
- No G76 Release Decision Revision 5 rebase exists.
- No schema, model, validator, serializer, CHE capability, trust root, proof
  profile, provider, persistence, migration, rollback, deployment, or runtime
  implementation exists.
- No live Human subject, credential, challenge, proof, session, binding,
  revocation, trust transition, Replay, CRO, or Cutover artifact is created.
- No implementation, integration, deployment, crash, or live production test
  is performed because this generation is proposal-only.
- Feasibility of storage primitives, cryptographic profiles, issuer choices,
  privacy controls, process coordination, and external systems remains for
  separately governed CDP and deployment work after activation.
- Existing hook drift, partial conformance, distributed enforcement, dormant
  governance memory, rollback, deployment, and external-system limitations
  remain visible and unchanged.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and required Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | commit, tree, subject, parent, clean start, exact predecessor digests | Git and SHA-256 inspection | `PASS` |
| Revision 1 successor | G77-02 identity/revision/digest and immutable bytes | lineage comparison | `PASS` |
| G77-03 binding | assessment identity/digest/class | lineage comparison | `PASS` |
| proposal-only stage | status fixed; no later CAP acts | scope review | `PASS` |
| blocker classification vocabulary | every mandatory blocker exactly resolved/not resolved | matrix review | `PASS` |
| sole-CHE bootstrap | all three capabilities first enter CHE; blocker `RESOLVED` | topology trace | `PASS` |
| HIC negative capabilities | transport/presentation only; blocker `RESOLVED` | boundary review | `PASS` |
| bootstrap contracts | modality, semantics, owner, Continuation, sources, responses, idempotency, duplicates, terminals, negatives; blocker `RESOLVED` | contract matrix | `PASS` |
| Human-subject correctness | canonical subject artifact, HUMAN class, issuer trust, actor mapping, rejection set; blocker `RESOLVED` | identity/validation review | `PASS` |
| trust-root authority | candidate/intent/Human act/applied transition/head/receipt; blocker `RESOLVED` | lifecycle review | `PASS` |
| one active trust head | exact tuple, atomic pointer replacement, read-back; blocker `RESOLVED` | state-model review | `PASS` |
| revocation authority | closed evidence sources, owner, targets, propagation; blocker `RESOLVED` | model review | `PASS` |
| session lifecycle | complete closed transitions and terminal non-revival; blocker `RESOLVED` | lifecycle matrix | `PASS` |
| retry/crash/uncertainty | exact idempotency and committed-evidence rules; blocker `RESOLVED` | recovery matrix | `PASS` |
| artifact DAG | topological dependency graph and self/forward/cycle prohibition; blocker `RESOLVED` | G76-06 rule comparison | `PASS` |
| Replay completeness | committed source/transition/state/receipt reconstruction; blocker `RESOLVED` | boundary and DAG review | `PASS` |
| CRO boundaries | passive non-secret observation only; blocker `RESOLVED` | negative-capability review | `PASS` |
| CAP successor lineage | Strategy A and mandatory G76 R5 rebase; blocker `RESOLVED` | predecessor/successor review | `PASS` |
| Production Cutover compatibility | prerequisite ordering, no grandfathering, rollback, historical evidence; blocker `RESOLVED` | migration review | `PASS` |
| Human Authority preservation | attribution only and exact external trust authority | semantic comparison | `PASS` |
| topology | 1 HIC / 1 CHE / 1 owner chain / 1 path / 0 parallel | topology trace | `PASS` |
| no implementation/Ratification/Certification/activation | report-only mutation | scope and repository review | `PASS` |
| implementation tests | proposal only | scope review | `NOT_APPLICABLE` |
| whitespace integrity | complete report diff | `git diff --check` equivalent | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- added
  `docs/governance/G77_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_2_HUMAN_AUTHENTICATION_CONSTITUTIONAL_MODEL_V1.md`
  as the sole G77-04 artifact.

No existing file changed.

Unchanged subsystems:

- active Constitution, CAP, CDP, Human Authority, Governance, Production
  Cutover, production status, release, CLIA, HIC, CHE, Conversation, Platform,
  Replay, CRO, Authorization, Workers, runtime, deployment, configuration,
  schema, policy, routing, workflow, and owner chain;
- G77-02, G77-03, G76-06, G76-07, and all preceding artifacts; and
- all code, tests, configuration, credentials, trust roots, sessions,
  providers, and runtime state.

API compatibility:

- No active API, schema, model, validator, serializer, command, profile, route,
  owner, caller, workflow, production, authentication, Ratification,
  Certification, publication, activation, or Constitutional contract changes.

Boundary preservation:

- The proposal grants no Human, authentication, implementation, deployment,
  Ratification, Certification, publication, or activation authority.
- Human Authority semantics remain unchanged.
- The active HIC remains transport only and the active CHE remains sole.
- Replay remains read-only and CRO remains passive.
- G76-07 remains immutable and inactive.
- The active one-HIC-family, one-CHE, one-owner-chain, one-production-path
  topology remains unchanged, with zero parallel production paths.

Unrelated pre-existing changes:

- None observed. The worktree was clean at revision start.

# 6. Certification Verdict

CONSTITUTIONAL_HUMAN_AUTHENTICATION_CAP_PROPOSAL_REVISION_2_ESTABLISHED
