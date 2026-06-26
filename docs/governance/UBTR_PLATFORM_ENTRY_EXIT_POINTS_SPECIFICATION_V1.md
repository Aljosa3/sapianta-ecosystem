# UBTR Platform Entry And Exit Points Specification V1

Status: Generation 2 platform boundary specification.

This artifact defines which platform entry points and exit points must pass
through the Universal Bidirectional Translation Runtime.

It does not implement runtime code.
It does not modify Platform Core.
It does not redesign Governance, Replay, OCS, HIRR, approval, workers, or
providers.

## 1. Purpose

Generation 2 defines UBTR as the canonical semantic authority for human-facing
translation.

This specification freezes the platform boundary:

- every human-facing input that requires semantic interpretation must enter
  through UBTR;
- every human-facing output that explains governance state must exit through
  UBTR;
- internal Platform Core traffic that already uses the Canonical Semantic
  Artifact must not be re-translated unnecessarily.

The goal is consistent semantic handling across ACLI, graphical interfaces,
APIs, chat channels, voice channels, and future conversational surfaces.

## 2. Boundary Principle

UBTR is mandatory at human semantic boundaries.

UBTR is not mandatory for internal machine-to-machine traffic that already uses
canonical platform artifacts.

```text
Human Channel
  |
  v
UBTR Entry Processing
  |
  v
Canonical Semantic Artifact
  |
  v
Platform Core
  |
  v
UBTR Exit Processing
  |
  v
Human Channel
```

## 3. Mandatory UBTR Entry Points

UBTR is mandatory for any channel where a human supplies natural language,
semi-structured intent, clarification, approval explanation request, rejection
reason, modification request, or review comment.

Mandatory human-facing entry channels:

- ACLI;
- Web UI;
- Desktop UI;
- Mobile UI;
- REST API when accepting human-authored text or intent payloads;
- MCP interfaces when exposing human-authored prompts or tool requests;
- Voice interfaces;
- Email interfaces;
- Chat interfaces such as Slack, Teams, Discord, or similar;
- future conversational channels.

## 4. Mandatory UBTR Exit Points

UBTR is mandatory for any channel where Platform Core state is rendered back to
a human in natural language or operator-facing terms.

Mandatory human-facing exit content:

- routing summaries;
- proposal explanations;
- approval requests;
- rejection summaries;
- modification-request summaries;
- validation summaries;
- replay summaries;
- fail-closed explanations;
- provider cognition summaries;
- worker result summaries;
- hardening or certification summaries shown to operators;
- governance state explanations;
- recovery and resume explanations.

## 5. Channel Matrix

| Channel | UBTR Mandatory | Entry Processing | Exit Processing | Replay Implications | Authentication Boundary | Governance Boundary |
| --- | --- | --- | --- | --- | --- | --- |
| ACLI | Yes | Normalize operator input, approvals, rejections, clarification, modification requests. | Render proposal, approval, execution, validation, replay, and fail-closed explanations. | Record translation artifacts, semantic lineage, rendered output reference. | Local operator identity or session identity must be bound before governed action. | UBTR translates; ACLI/HIRR/workflows govern downstream behavior. |
| Web UI | Yes | Normalize form text, chat text, guided intent fields, comments, approval reasons. | Render human-readable governance state, approval prompts, replay views, errors. | Record channel, UI action reference, translation lineage. | Web session and user role verified before governance action. | UI cannot bypass UBTR for semantic intent. |
| Desktop UI | Yes | Normalize desktop prompts, local file intent descriptions, approval decisions. | Render local operator summaries and replay references. | Record device/session metadata where allowed and semantic artifact lineage. | Desktop identity or local authenticated user boundary. | Desktop UI remains presentation layer only. |
| Mobile UI | Yes | Normalize short-form text, voice-to-text output, taps that carry semantic choices. | Render compact explanations and approval prompts. | Record mobile channel and semantic artifact references. | Mobile identity, device session, and role boundary. | Mobile UI cannot reduce approval requirements. |
| REST API | Conditional mandatory | Mandatory when API accepts human-authored natural language or intent payloads. Not required for canonical artifact submission. | Mandatory when returning human-readable summaries. Not required for machine canonical payloads. | Record source payload type and whether UBTR was applied or bypassed because payload was already canonical. | API authentication, token, tenant, and role boundary. | API must not provide direct execution authority through text fields. |
| MCP interfaces | Conditional mandatory | Mandatory for human-authored prompts, tool requests, and natural language task descriptions. Not required for internal canonical artifact exchange. | Mandatory for human-readable tool result explanations. | Record MCP server/tool identity, semantic artifact, and translation lineage. | MCP client/server identity and tool permission boundary. | MCP tools remain governed consumers, not semantic authorities. |
| Voice interfaces | Yes | Convert speech transcript to normalized semantic input; preserve transcript reference. | Render or synthesize human-facing explanation from UBTR projection. | Record transcript hash, channel, confidence, and semantic artifact. | Speaker/session identity must be established before governed action. | Voice confidence cannot become approval confidence. |
| Email interfaces | Yes | Normalize email body, subject, reply context, approval language, rejection language. | Render reply explanations, approval instructions, replay links. | Record message id/reference, normalized input, semantic lineage. | Sender identity and authorization must be verified separately. | Email wording cannot bypass approval boundary. |
| Chat interfaces | Yes | Normalize chat messages, slash-command text, threaded clarifications, approvals. | Render concise explanations and replay references into channel. | Record channel id/reference, thread reference, semantic artifact. | Workspace, user, role, and channel authorization boundary. | Chat commands remain human-facing semantic inputs. |
| Future conversational channels | Yes by default | Apply UBTR unless the channel exchanges only canonical artifacts. | Apply UBTR for human-readable output. | Record channel adapter identity and semantic lineage. | Must define identity before governed use. | Must preserve governance and replay boundaries. |

## 6. Entry Processing Requirements

Every UBTR entry point must:

- preserve the original human input reference;
- normalize natural language without authorizing execution;
- produce or reference a Canonical Semantic Artifact;
- identify ambiguity and confidence;
- preserve channel identity;
- preserve authentication context reference;
- preserve replay lineage;
- fail closed when semantic input cannot be safely represented;
- avoid worker invocation;
- avoid provider invocation except through governed OCS escalation;
- avoid approval inference from natural language unless the approval runtime
  explicitly accepts the command under a valid pending proposal.

Entry processing must not:

- bypass HIRR or workflow routing decisions;
- bypass governance constraints;
- bypass approval boundaries;
- treat channel-specific UI controls as execution authority without governance;
- silently rewrite human intent.

## 7. Exit Processing Requirements

Every UBTR exit point must:

- render governance state in human-readable form;
- preserve the authoritative technical state reference;
- distinguish deterministic explanation from provider-assisted explanation;
- identify what will happen and what will not happen;
- identify whether approval is required;
- identify replay reference or expected replay availability;
- preserve non-authoritative explanation status;
- avoid technical noise unless placed in a diagnostic section;
- fail closed when the output cannot be linked to authoritative state.

Exit processing must not:

- create new governance decisions;
- approve, reject, or modify workflow state;
- hide fail-closed reasons;
- claim execution occurred when replay does not prove it;
- claim provider output is authoritative.

## 8. Semantic Normalization Rules

Semantic normalization must be channel-independent.

The same human intent should produce the same canonical semantic meaning whether
it arrives through ACLI, Web UI, email, chat, voice, or API.

Channel adapters may add metadata, such as:

- channel type;
- session id;
- message id;
- thread id;
- device id;
- transcript confidence;
- user role reference;
- authentication reference.

Channel adapters may not add semantic authority.

## 9. Replay Implications

Replay must record enough evidence to reconstruct:

- channel of origin;
- original human input reference;
- normalized semantic input;
- Canonical Semantic Artifact reference;
- authentication context reference, where available;
- escalation decisions, if any;
- human-readable output projection;
- approval or rejection command interpretation;
- fail-closed reason, if any.

Replay remains the source of truth.
UBTR entry and exit artifacts are replay evidence, not replay authority.

## 10. Authentication Boundary

Authentication is not owned by UBTR.

Each channel must establish identity and authorization before governed action is
allowed.

UBTR may carry authentication context references inside semantic artifacts, but
UBTR must not:

- authenticate users;
- authorize users;
- infer user authority from language;
- elevate privileges;
- bypass channel-specific access control.

Authentication ownership remains with the platform identity and access boundary
for the channel.

## 11. Governance Boundary

Governance is not owned by UBTR.

UBTR may translate human intent into canonical semantic form.
Governance determines whether the downstream action is admissible.

Governance boundary rules:

- semantic clarity does not imply governance admissibility;
- provider confidence does not imply governance admissibility;
- approval wording does not bypass approval model constraints;
- channel convenience does not weaken governance requirements;
- replay lineage must exist for governed actions.

## 12. Interactions That Should Not Pass Through UBTR

The following interactions should not pass through UBTR unless they include
human-facing semantic content:

- binary file transfer;
- blob upload or download;
- internal worker-to-worker communication;
- internal Platform Core communication already using the Canonical Semantic
  Artifact;
- replay storage internals;
- cryptographic hash verification;
- validation runner internal output consumed only by machines;
- provider transport internals;
- database replication;
- metrics aggregation that does not contain human-authored semantic input;
- static asset serving;
- health checks;
- authentication token exchange;
- low-level protocol handshakes.

If these interactions produce human-facing summaries, the summaries must pass
through UBTR exit processing.

## 13. Conditional UBTR Bypass

UBTR may be bypassed only when all of the following are true:

- the payload is already a valid Canonical Semantic Artifact or other
  replay-verified canonical platform artifact;
- no human natural language interpretation is required;
- no human-readable output is being generated;
- replay can reconstruct why UBTR was not applied;
- the receiving component is authorized to consume the canonical artifact.

Bypass must be explicit, replay-visible, and deterministic.

## 14. Future Channel Onboarding Rules

Every future channel must define:

- channel identity;
- human input types;
- human output types;
- authentication boundary;
- governance boundary;
- replay evidence fields;
- UBTR entry processing;
- UBTR exit processing;
- conditions for canonical-artifact bypass;
- failure handling.

Default rule:

If a human can type, speak, click, select, approve, reject, clarify, or request
something that affects governance state, the channel must pass through UBTR.

## 15. Implementation Constraints

Future implementation must:

- preserve deterministic semantic artifacts;
- preserve replay lineage;
- preserve authentication references without making UBTR an identity provider;
- preserve governance boundaries;
- preserve approval boundaries;
- keep channel adapters thin;
- make UBTR behavior channel-independent;
- fail closed on malformed semantic inputs;
- fail closed on missing replay references for governed actions.

Future implementation must not:

- allow channels to interpret human intent independently after migration;
- allow UI-specific shortcuts to bypass UBTR;
- allow API payloads to smuggle execution authority through natural language;
- allow voice confidence to become semantic authority;
- allow chat commands to bypass governed approval;
- require UBTR for raw binary or internal canonical-artifact traffic.

## 16. Final Verdict

UBTR_PLATFORM_ENTRY_EXIT_POINTS_FROZEN
