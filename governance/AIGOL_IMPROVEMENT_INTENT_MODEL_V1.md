# AIGOL_IMPROVEMENT_INTENT_MODEL_V1

## Status

Foundation model.

## Definition

An Improvement Intent is a structured request to evaluate whether an improvement proposal should be produced.

It is an intent artifact, not a proposal artifact.

## Artifact

Future runtime artifact:

```text
IMPROVEMENT_INTENT_ARTIFACT_V1
```

## Required Fields

```text
artifact_type
improvement_intent_version
improvement_intent_id
intent_source
canonical_chain_id
gap_reference
gap_hash
source_replay_reference
source_replay_hash
affected_layer
affected_domain
affected_worker_family
improvement_class
intent_summary
evidence_summary
constraints
known_gaps
assumptions
confidence
human_review_required
high_risk_domain
ppp_eligible
created_at
replay_visible
artifact_hash
```

## Intent Sources

Allowed sources:

```text
HUMAN_PROMPT
REPLAY_GAP_DETECTION
GOVERNANCE_REVIEW
WORKER_EVIDENCE_REVIEW
PROVIDER_ASSISTED_NON_AUTHORITATIVE
COMBINED_EVIDENCE
```

Provider-assisted sources may contribute text only.

They may not create authority.

## Improvement Classes

Improvement classes:

```text
RUNTIME_HARDENING
CONTEXT_ASSEMBLY_HARDENING
RESOURCE_SELECTION_HARDENING
PPP_CONTRACT_HARDENING
GOVERNANCE_REVIEW
WORKER_FOUNDATION
WORKER_RUNTIME
DOMAIN_MODEL
OPERATOR_WORKFLOW
REPLAY_RECONSTRUCTION
TEST_FIXTURE
DOCUMENTATION_OR_CERTIFICATION
```

## PPP Eligibility

An Improvement Intent is PPP-eligible only when:

- source evidence is replay-visible;
- source hashes are valid;
- chain continuity is preserved;
- affected scope is explicit;
- constraints are explicit;
- high-risk status is declared;
- human review requirement is declared;
- no execution authority is requested.

## Required False Authority Flags

Future artifacts must preserve:

```text
proposal_created = false
proposal_approved = false
implementation_authorized = false
implementation_applied = false
execution_requested = false
dispatch_requested = false
worker_invoked = false
provider_authority = false
worker_authority = false
governance_authority = false
self_modification_authority = false
replay_mutated = false
governance_mutated = false
```

## Cognition Interaction

Cognition may consume `IMPROVEMENT_INTENT_ARTIFACT_V1` as structured intent.

Cognition may:

- classify intent;
- assemble context;
- identify missing context;
- request clarification.

Cognition may not:

- approve;
- select resources;
- create proposals directly;
- execute.

## PPP Interaction

PPP may consume improvement intent after Cognition and Resource Selection.

PPP may:

- request provider proposal production;
- validate proposal contracts;
- trigger repair or retry;
- surface clarification or approval requirements;
- create implementation handoff artifacts.

PPP may not:

- approve;
- authorize;
- execute;
- mutate governance;
- mutate replay.

## Non-Goals

Improvement Intent does not replace:

- `IMPROVEMENT_PROPOSAL_ARTIFACT_V1`;
- `IMPROVEMENT_REVIEW_ARTIFACT_V1`;
- approval artifacts;
- implementation artifacts;
- execution artifacts.
