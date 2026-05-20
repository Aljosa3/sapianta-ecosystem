# SEMANTIC_PROPOSAL_FIXTURE_CERTIFICATION_V1

## Status

Draft certification specification.

## Purpose

This specification defines the first certified semantic proposal fixture model
for AiGOL governed semantic transport. It establishes a canonical local
`semantic_proposal.json` structure that can be validated, inspected, and routed
into continuity cockpit rendering without creating execution authority.

This is a governance-safe cognition artifact definition only. It is not provider
dispatch, execution runtime, localhost ingress, orchestration, durable
persistence, or ChatGPT API integration.

## Canonical Proposal Structure

The canonical field order is:

1. `transport_artifact_id`
2. `artifact_version`
3. `proposal_id`
4. `lineage_id`
5. `created_by`
6. `created_at`
7. `source_model_family`
8. `human_request`
9. `semantic_intent`
10. `proposed_mode`
11. `risk_class`
12. `authority_boundary_statement`
13. `semantic_boundary_statement`
14. `requested_action_type`
15. `lineage_ref`
16. `replay_identity`
17. `certification`
18. `artifact_hash`

All fields are required for a certified fixture. The proposal may include values
that are operator-authored, model-authored, or human-mediated, but import remains
explicit and local.

## Deterministic Serialization

Canonical serialization expectations:

- JSON object only;
- UTF-8 encoding;
- stable key ordering for hash calculation;
- compact JSON separators for hash calculation;
- no implicit import timestamp;
- no hidden fields added during import;
- `artifact_hash` excluded from canonical hash input;
- hash algorithm: SHA-256;
- hash format: `sha256:<hex>`.

The fixture file preserves readable ordering for review while defining the hash
over canonical sorted JSON. Hash repair is not permitted during ingestion.

## Proposal Identity

`proposal_id` identifies the semantic proposal as a governed cognition artifact.
It is deterministic and replay-safe for the fixture.

`lineage_id` identifies the semantic continuity lineage that the proposal enters.
It does not approve continuation and does not authorize dispatch.

`transport_artifact_id` identifies the local transport artifact. It is distinct
from `proposal_id` so file transport, proposal semantics, and continuity lineage
remain separable.

`replay_identity` provides a replay-safe reference for cockpit visibility. It is
not a durable replay write and does not mutate replay records.

## Authority Boundary Semantics

The authority boundary statement must explicitly preserve:

- ChatGPT / Claude / LLMs provide semantic cognition only;
- AiGOL / AGOL governs admissibility, continuity, replay, lifecycle visibility,
  and boundary interpretation;
- Codex / providers are not invoked by the fixture;
- sidepanel rendering is read-only and non-authoritative;
- certification is not approval, dispatch, execution, or continuation.

## Semantic Boundary Semantics

The semantic boundary statement must explicitly state that semantic reasoning is
model-native, non-deterministic, and non-authoritative. The proposal can provide
semantic direction for governance review, but AiGOL decides only whether the
direction is admissible for governed continuity ingestion.

## Certification Semantics

`VALID` means the proposal is structurally parseable and satisfies required
field validation.

`CERTIFIED_FOR_CONTINUITY_INGESTION` means the proposal is:

- structurally valid;
- authority bounded;
- replay-safe;
- continuity-safe;
- non-executable;
- non-orchestrating;
- fit for read-only cockpit continuity rendering.

Certification does not mean:

- approved;
- executable;
- dispatchable;
- autonomous;
- authoritative;
- eligible for provider calls;
- eligible for lifecycle mutation;
- eligible for replay mutation.

## Fixture Requirements

`.github/governance/fixtures/semantic_proposal_v1.json` must:

- use the canonical field order above;
- include explicit authority boundaries;
- include explicit semantic boundaries;
- include lineage references;
- include replay-safe identity references;
- use `READ_ONLY`, `REVIEW_ONLY`, or `DEMO_ONLY`;
- reject `EXECUTE`, `AUTO_EXECUTE`, `AUTONOMOUS`, `PROVIDER_RUNTIME`, and
  `ORCHESTRATION`;
- remain suitable for continuity ingestion only.

## Review Requirements

The accompanying review certifies:

- deterministic structure;
- replay-safe semantics;
- authority separation;
- continuity-safe ingestion semantics;
- no hidden execution semantics;
- no orchestration semantics;
- no continuation authority.

## Governance Guarantees

This fixture certification preserves:

- explicit local import;
- deterministic artifact identity;
- replay-safe semantic proposal references;
- read-only cockpit rendering;
- no provider dispatch;
- no execution runtime;
- no localhost ingress;
- no orchestration;
- no durable persistence;
- no ChatGPT API integration;
- no approval automation;
- no autonomous continuation.

## Recommended Next Implementation

Use this fixture as the canonical positive test artifact for
`SEMANTIC_PROPOSAL_FILE_IMPORT_V1`, then add hash verification as a separate
bounded validator step after review.
