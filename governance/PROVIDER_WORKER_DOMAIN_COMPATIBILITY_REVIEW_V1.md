# PROVIDER_WORKER_DOMAIN_COMPATIBILITY_REVIEW_V1

## Status

Governance-only architectural review.

No provider runtime, worker runtime, schemas, replay, cognition, governance,
coordinators, orchestration, or domain routing are modified by this review.

## Review Question

Before provider and worker attachment proceeds, should AiGOL introduce minimal
domain metadata to avoid future architectural friction?

Candidate metadata:

- `domain`
- `capability`
- `resource_type`

## Findings Summary

Minimal domain metadata is not constitutionally required for the next single
provider or worker attachment.

It is a low-cost architectural investment before large-scale provider and
worker expansion.

The recommended position is:

```text
ARCHITECTURAL_RECOMMENDATION = ADD_MINIMAL_METADATA_NOW
```

This recommendation is metadata-only. The fields must be descriptive,
replay-visible, deterministic, and non-authoritative.

They must not introduce:

- execution authority
- autonomous coordination
- hidden state
- dynamic routing authority
- governance authority transfer

## Metadata Necessity Matrix

| Surface | Metadata | Status | Evidence | Finding |
| --- | --- | --- | --- | --- |
| Provider | domain | OPTIONAL_NOW | `FIRST_REAL_PROVIDER_ATTACHMENT_V1` attaches OpenAI as proposal-only without domain. `CROSS_DOMAIN_READINESS_REVIEW_V1` identifies missing domain ontology as high-severity future gap. | Not required for a single provider, but useful before multiple provider categories appear. |
| Provider | capability | OPTIONAL_NOW | Provider runtime already records provider_id, provider_type, provider_version, and status. Capability classes exist in `CAPABILITY_CLASS_MODEL_V1`. | Useful for later provider capability mapping, but not needed for first provider attachment. |
| Provider | resource_type | OPTIONAL_NOW | Provider is already identified as external proposal producer in `MINIMAL_PROVIDER_ATTACHMENT_RUNTIME_V1`. | Useful to distinguish LLM, search, email, local model, and future sources without changing authority. |
| Worker | domain | OPTIONAL_NOW | `FIRST_EXTERNAL_WORKER_ATTACHMENT_V1` defines a read-only inspection worker. `WORKER_TAXONOMY_ANALYSIS_V1` says domain-specific workers are not defined. | Not required for one worker; useful before domain-specific workers such as trading, email, or analytics. |
| Worker | capability | REQUIRED_NOW | Worker execution is already constrained by capability classes and authorization mapping. | Capability metadata should be present before worker expansion because workers are execution participants. |
| Worker | resource_type | OPTIONAL_NOW | Worker identity and worker_type already exist; no generalized resource abstraction exists. | Useful for future resource indexing and replay, but can remain descriptive. |

## Provider Readiness

Status: OPTIONAL_NOW

Providers should eventually expose:

- domain
- capability
- resource_type

Evidence:

- `MINIMAL_PROVIDER_ATTACHMENT_RUNTIME_V1` currently records provider_id,
  provider_type, provider_version, and provider_status.
- `FIRST_REAL_PROVIDER_ATTACHMENT_V1` proves OpenAI can attach without domain,
  capability, or resource_type metadata.
- `PROVIDER_SUBSTITUTABILITY_REVIEW_V1` finds provider identity and boundary
  semantics mostly complete, while provider ecosystem semantics remain partial.
- `CROSS_DOMAIN_READINESS_REVIEW_V1` identifies missing domain ontology,
  capability-to-domain binding, and resource abstraction as future gaps.

Finding:

Provider metadata is sufficient for first attachment. Minimal domain metadata is
not a blocker, but adding it before many providers exist will reduce future
migration friction.

## Worker Readiness

Status: OPTIONAL_NOW, with capability treated as REQUIRED_NOW before worker
expansion.

Workers should eventually expose:

- domain
- capability
- resource_type

Evidence:

- `FIRST_EXTERNAL_WORKER_ATTACHMENT_V1` proves one read-only inspection worker
  can attach without a full domain model.
- `WORKER_ECOSYSTEM_READINESS_REVIEW_V1` classifies worker ecosystem status as
  `PARTIALLY_DEFINED`.
- `WORKER_TAXONOMY_ANALYSIS_V1` finds capability taxonomy partial and
  domain-specific workers undefined.
- `CAPABILITY_CLASS_MODEL_V1` defines capability classes and fail-closed
  requirements.

Finding:

Worker capability metadata matters earlier than provider metadata because
workers are execution participants. Domain and resource_type remain descriptive
and optional for the next single worker, but should be introduced before
large-scale worker expansion.

## Replay Impact Assessment

Status: PARTIAL

Replay currently reconstructs provider identity, provider response, worker
evidence, cognition state, intent, memory consultation, citation bundles, and
single-domain operational evidence.

Replay would benefit from:

- domain visibility
- capability visibility
- resource visibility

Without these fields, future replay could still reconstruct what happened
component-by-component, but cross-domain analysis would become harder because
domain grouping and resource relationships would need to be inferred from
provider_id, worker_id, request text, or external governance documents.

Finding:

Replay does not require these fields for current operation, but future
cross-domain replay will need them or an equivalent domain-resource index.

## Cognition Compatibility

Status: BENEFICIAL

Future cognition layers will likely require:

- domain awareness
- capability awareness
- resource awareness

Evidence:

- `COGNITION_FOUNDATION_FREEZE_V1` freezes cognition as non-authoritative.
- `INTENT_ROUTING_MODEL_V1` defines destinations but not domain routing.
- `CROSS_DOMAIN_READINESS_REVIEW_V1` finds future domain coordination feasible
  with gaps.

Finding:

Cognition can continue without metadata today. Future domain reasoning,
synergy proposals, and dependency awareness will eventually require descriptive
metadata or a separate domain registry.

## Cross-Domain Compatibility

| Field | Classification | Evidence | Finding |
| --- | --- | --- | --- |
| domain | CRITICAL | Cross-domain review identifies missing domain ontology as HIGH severity. | Domain identity is essential for multi-domain reasoning and replay grouping. |
| capability | CRITICAL | Capability classes are already canonical and worker execution depends on capability boundaries. | Capability is the safest bridge between current governance and future domain coordination. |
| resource_type | USEFUL | Providers, workers, capabilities, and artifacts are identifiable but not generalized as resources. | Resource type improves future compatibility but can remain coarse and descriptive. |

## Technical Debt Comparison

### Option A: Add Metadata Now

Migration effort:

- Low, if metadata is optional and descriptive.

Replay impact:

- Positive, if fields are replay-visible and non-authoritative.

Governance impact:

- Low, if fields do not authorize, route, execute, or govern.

Future compatibility:

- High. Early metadata prevents later backfill across many providers and
  workers.

Risk:

- Over-specifying domain values before a canonical ontology exists.

Mitigation:

- Use minimal coarse fields and mark them descriptive only.

### Option B: Add Metadata Later

Migration effort:

- Low now, high later after many providers/workers exist.

Replay impact:

- Later replay may need inferred domain/resource lineage or versioned schema
  reconciliation.

Governance impact:

- Later governance reviews must separate historical records with missing
  metadata from newer records with metadata.

Future compatibility:

- Reduced. Cross-domain analysis becomes harder if many attachments lack
  domain/capability/resource descriptors.

Risk:

- Technical debt accumulates silently as attachments multiply.

## Final Scores

`PROVIDER_COMPATIBILITY_SCORE`: `78`

`WORKER_COMPATIBILITY_SCORE`: `72`

`FUTURE_COORDINATION_COMPATIBILITY_SCORE`: `84`

## Final Recommendation

`ARCHITECTURAL_RECOMMENDATION`: `ADD_MINIMAL_METADATA_NOW`

## Go / No-Go Decision

GO for provider and worker attachment if metadata is treated as optional,
descriptive, replay-visible, and non-authoritative.

GO for adding minimal metadata before large-scale provider/worker expansion.

NO-GO for using metadata as routing authority, execution authority,
authorization authority, governance authority, or autonomous coordination.

## Direct Answer

Adding `domain`, `capability`, and `resource_type` before expansion is a
low-cost architectural investment that reduces future redesign pressure.

The fields are not required for the next single provider or worker attachment.

They should be added before dozens of providers or workers exist.
