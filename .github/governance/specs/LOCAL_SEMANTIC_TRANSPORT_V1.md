# LOCAL_SEMANTIC_TRANSPORT_V1

## Status

Draft transport specification.

## Purpose

This specification defines the first non-copy/paste governed semantic transport
between ChatGPT / Claude semantic proposals and the AiGOL operational cockpit.

This is local semantic transport design only. It is not provider execution,
Codex dispatch, orchestration, autonomous continuation, approval automation,
ChatGPT API integration, or durable production transport.

## Operational Flow

The target flow is:

ChatGPT / Claude semantic proposal
-> local transport artifact
-> AiGOL proposal ingestion
-> deterministic validation
-> continuity cockpit rendering

The transport improves over manual copy/paste by making the semantic proposal a
bounded local artifact with deterministic identity and replay-safe inspection.

## Recommended Transport Path

Recommended for v1: `local file-drop semantic_proposal.json`.

The operator exports or saves a semantic proposal as a local JSON artifact, then
explicitly imports that artifact into the Browser Companion sidepanel. The
sidepanel validates the artifact deterministically before rendering continuity
cockpit output.

Rationale:

- preserves explicit user-visible transfer;
- avoids ChatGPT / Claude API coupling;
- avoids browser extension background channels;
- creates a tangible proposal artifact for hashing and replay reference;
- supports deterministic schema validation;
- keeps provider dispatch, approval, and execution outside the transport;
- keeps durable production persistence deferred.

## Rejected Or Deferred Transport Paths

### Localhost POST endpoint

Deferred.

Reason: a localhost POST endpoint could be valid later, but it introduces a
network-facing ingestion surface and requires additional localhost boundary,
CSRF, origin, and replay-write review. It is not needed for first transport
proof.

### Browser extension import endpoint

Deferred.

Reason: an extension import endpoint risks hidden background behavior or
implicit page coupling unless carefully specified. The current sidepanel should
remain explicit and operator-driven.

### Clipboard-assisted explicit import

Allowed as transitional UX, but not recommended as the canonical v1 transport.

Reason: clipboard assistance reduces typing friction but remains close to
copy/paste and provides weaker artifact identity than a file-drop JSON object.
It may be used only when the operator explicitly pastes or selects content.

## Transport Artifact Schema

The local artifact filename should be `semantic_proposal.json`.

Required JSON fields:

- `transport_artifact_id`
- `artifact_version`
- `created_by`
- `created_at`
- `source_model_family`
- `human_request`
- `semantic_intent`
- `proposed_mode`
- `risk_class`
- `authority_boundary_statement`
- `semantic_boundary_statement`
- `requested_action_type`
- `lineage_ref`
- `replay_identity`
- `artifact_hash`

Allowed `proposed_mode` values:

- `READ_ONLY`
- `REVIEW_ONLY`
- `DEMO_ONLY`

Rejected `proposed_mode` values:

- `EXECUTE`
- `AUTO_EXECUTE`
- `AUTONOMOUS`
- `PROVIDER_RUNTIME`
- `ORCHESTRATION`

## Deterministic Serialization

The artifact must be serialized as canonical JSON before hashing:

- stable key ordering;
- UTF-8 encoding;
- no implicit timestamps added during import;
- no hidden fields added during import;
- `artifact_hash` computed over canonical artifact content excluding
  `artifact_hash` itself.

If the hash is absent or invalid, ingestion must fail closed or render a blocked
validation result. Hash repair is not permitted in v1.

## AiGOL Proposal Ingestion

AiGOL proposal ingestion may:

- read an explicitly selected local artifact;
- parse JSON deterministically;
- validate required fields;
- validate bounded mode;
- validate authority boundary language;
- compute or verify replay-safe identity;
- render accepted proposals in the continuity cockpit;
- render rejected proposals as blocked validation evidence.

AiGOL proposal ingestion must not:

- discover files automatically;
- watch directories;
- call providers;
- dispatch execution;
- approve actions;
- create lifecycle transitions;
- rewrite replay;
- repair artifact hashes;
- persist artifacts durably without a separate milestone.

## Authority Boundaries

The local semantic transport preserves:

- ChatGPT / Claude = semantic cognition only;
- AiGOL / AGOL = proposal admissibility, validation, continuity, replay, and
  boundary visibility;
- Codex / providers = not invoked by this transport;
- sidepanel = read-only cockpit rendering.

Successful import means only that the proposal is admissible for cockpit
visibility. It is not approval, dispatch, execution, or continuation authority.

## Replay Guarantees

The transport must support replay-safe references:

- stable `transport_artifact_id`;
- stable `lineage_ref`;
- stable `replay_identity`;
- deterministic `artifact_hash`;
- explicit import event visibility;
- read-only artifact inspection.

The transport must not rewrite, repair, delete, or infer replay records. Any
future durable replay write must be separately specified.

## Lifecycle Guarantees

The v1 local semantic transport does not create execution lifecycle transitions.

Allowed visibility states:

- `IMPORTED_FOR_REVIEW`
- `VALIDATED_FOR_COCKPIT`
- `BLOCKED`

These are proposal-ingestion visibility states only. They are not task dispatch
states and must not be confused with `APPROVED`, `DISPATCHED`, `EXECUTING`, or
`RETURNED`.

## Cockpit Rendering Guarantees

The cockpit may render:

- proposal validation status;
- semantic proposal artifact;
- human request;
- semantic intent;
- proposed mode;
- risk class;
- authority boundary;
- semantic boundary;
- continuity status;
- replay visibility;
- lifecycle visibility;
- lineage visibility;
- findings, risks, and recommendations.

Rendering remains deterministic, read-only, in-memory, sidepanel-local, and
non-authoritative.

## Security Risks

Risks to control:

- malformed JSON or oversized artifacts;
- unsafe modes disguised as bounded review;
- authority boundary statements that imply execution or continuation;
- model-provided content claiming approval;
- artifact hash mismatch;
- path traversal if file import later reads filesystem paths;
- localhost endpoint exposure if POST transport is added later;
- hidden background import if extension endpoint is added later;
- operator confusion between semantic proposal and governed approval.

## Governance Guarantees

The transport must preserve:

- explicit user-visible transfer;
- deterministic proposal validation;
- replay-safe artifact identity;
- no provider calls;
- no dispatch;
- no approval;
- no execution;
- no orchestration;
- no hidden persistence;
- no autonomous continuation;
- no semantic authority expansion.

## Recommended Implementation Sequence

1. Create a review-only fixture for `semantic_proposal.json`.
2. Define deterministic hash validation for proposal artifacts.
3. Add explicit sidepanel file selection for local JSON import.
4. Reuse existing semantic proposal validation rules.
5. Render accepted artifacts through the existing continuity cockpit.
6. Render rejected artifacts as blocked validation evidence.
7. Add tests proving no provider, dispatch, approval, execution, orchestration,
   durable persistence, replay mutation, or lifecycle mutation paths are
   introduced.
8. Review before considering localhost POST or browser extension import
   endpoint variants.
