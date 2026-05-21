# REAL_OPERATOR_USAGE_AND_FRICTION_COLLECTION_V1

## Status

Operational proving report.

Practical usability decision: `USABLE_WITH_SIMPLIFICATION_REQUIRED`

## Purpose

This proving exercise collects operator usability and friction evidence for the
current governed bridge runtime after canonical Python result artifact
export/import.

This milestone validates whether the existing operational bridge helps an
operator understand, inspect, and trust the governed flow:

Human
-> semantic proposal
-> governed transport
-> governed task package
-> mocked Codex result
-> result validation
-> governed return

This is not a new bridge architecture layer, orchestration runtime, provider
execution path, localhost server, hidden listener, durable replay backend, or
new transport protocol.

## Reviewed Runtime Surface

Reviewed existing capabilities:

- minimal end-to-end bridge runtime;
- canonical result artifact export/import;
- Browser Companion sidepanel lifecycle rendering;
- governed chat return flow;
- replay event visibility;
- explicit non-authority labels;
- mock-only Codex result visibility.

## Method

The proving method is structured operator review against the implemented
surface. It evaluates visible lifecycle rows, canonical artifact labels,
governed return wording, replay event IDs, import/export steps, and authority
boundary visibility.

This is not browser automation and does not create new runtime behavior.

## 1. Operator Flow Clarity

Assessment: `MOSTLY_CLEAR`.

The operator can follow the high-level lifecycle:

- human request;
- semantic proposal;
- governed transport;
- task package;
- mocked Codex result;
- result validation;
- governed return.

The compact lifecycle panel and governed chat return make the flow visible
without forcing immediate raw JSON inspection.

Friction found:

- The same flow is represented in several places: lifecycle panel, event stream,
  result card, governed return, canonical artifact status, and audit evidence.
- Operators may wonder which panel is the "main answer."
- The canonical artifact import improves runtime truth, but "artifact export"
  remains a technical concept that may need a simple operator sentence.

Recommended simplification:

- Treat the governed chat return as the main operator-facing result.
- Treat lifecycle rows as supporting evidence.
- Keep raw artifact inspection behind audit evidence.

## 2. Governance Overload

Assessment: `MODERATE_OVERLOAD`.

Authority separation is clear, but there are many repeated labels:

- no execution;
- no provider calls;
- no approval;
- no dispatch;
- no orchestration;
- semantic transport only;
- mock Codex only;
- session-local replay only.

The repetition protects safety, but it increases scanning cost.

Overload findings:

- First-time operators may read the cockpit as an audit document rather than a
  live operational result.
- Governance terms remain dense even after simplification.
- `CERTIFIED_FOR_CONTINUITY_INGESTION`, `CONTINUITY_VISIBLE`, and
  `HASH_VERIFIED` are precise but still require interpretation.

Recommended simplification:

- Keep one first-level authority statement.
- Move repeated non-authority evidence into expandable detail.
- Prefer one compact state line: `Review-only, hash verified, mock-only, no
  execution`.

## 3. Replay Readability

Assessment: `USEFUL_BUT_NOISY`.

Replay event IDs are useful for traceability and deterministic proof, but they
are not operator-friendly as first-level information.

Replay findings:

- `replay_event_id` values help audit review.
- Operators may not know whether replay is durable, append-only session
  visibility, or a backend ledger.
- Replay IDs can distract from the lifecycle outcome.
- Session-local replay labels reduce durable persistence confusion, but the
  word "replay" still carries ledger expectations.

Recommended simplification:

- Show first-level replay as `Replay: visible in this session`.
- Move raw replay IDs behind a "details" expansion.
- Keep one visible reminder that replay is session-local and not durable.

## 4. Governed Return Quality

Assessment: `GOOD`.

The governed return is compact enough to paste back into a chat or use as the
operator-facing result.

Strengths:

- It includes accepted or rejected status.
- It includes a reason.
- It includes replay visibility.
- It includes the next recommended step.
- It includes the non-authority reminder.

Friction found:

- Rejection reasons may still be technical.
- Accepted return can be mistaken for approval if the non-authority reminder is
  removed.
- Next steps are useful but generic.

Recommended simplification:

- Keep the governed return as the primary operator output.
- Add rejection-specific next-step wording in a future usability pass.
- Never separate accepted status from the no-execution reminder.

## 5. Operator Friction

Assessment: `MANUAL_BUT_ACCEPTABLE_FOR_PROVING`.

Current flow is intentionally explicit:

- generate or export result artifact;
- select file in sidepanel;
- import canonical result;
- inspect lifecycle and governed return.

Friction findings:

- Manual file handoff is understandable but not smooth.
- There are many controls in the same sidepanel, including older runtime
  controls that may confuse a bridge operator.
- Artifact terminology may feel technical.
- Import/export requires the operator to understand canonical source of truth.

Recommended simplification:

- Keep the explicit file handoff for now.
- Group bridge-specific controls separately from older preview/runtime controls.
- Rename or caption artifact import as "Import Python bridge result" for
  operator clarity while preserving artifact terminology in detail.

## 6. Trust And Safety Perception

Assessment: `STRONG_WITH_DENSITY_RISK`.

The cockpit makes the safety boundary visible:

- no real execution;
- mock Codex only;
- no provider calls;
- canonical Python result artifact;
- non-authoritative continuity semantics.

Trust findings:

- Operators should understand that Codex is mocked only.
- Canonical artifact import helps reduce "two runtime truths" confusion.
- Hash verification is visible as integrity-only.
- The system is safe, but the number of labels may make it feel heavier than
  the task being reviewed.

Recommended simplification:

- Keep `NO REAL EXECUTION / MOCK CODEX ONLY` as first-level text.
- Keep `CANONICAL PYTHON RESULT ARTIFACT` visible when imported.
- Avoid adding more trust labels unless they replace existing duplicated text.

## Friction Findings

- Manual artifact handoff is clear but slower than a direct bridge.
- The cockpit still contains too many adjacent controls for an operator focused
  only on the bridge flow.
- Replay IDs are audit-useful but noisy in compact operator view.
- Artifact terminology may slow non-technical operators.
- Rejection repair guidance is still generic.

## Overload Findings

- Non-authority labels are repeated across several panels.
- Replay, lifecycle, continuity, and artifact views overlap conceptually.
- Operators may need guidance on which panel is primary.
- Raw audit evidence remains necessary, but should stay out of the default
  operator path.

## Lifecycle Clarity Findings

- The full lifecycle is visible and mostly understandable.
- The mocked Codex boundary is clear.
- Canonical artifact import improves trust in Python as source of truth.
- The lifecycle should not gain additional first-level rows.

## Replay Usability Findings

- Replay supports audit confidence.
- Replay event IDs are too detailed for first-pass operator review.
- Session-local replay should be phrased in plain language.
- Durable replay backend expectations must continue to be explicitly rejected.

## Operator Trust Findings

- No-real-execution clarity is strong.
- Mock Codex visibility is strong.
- Hash verification as integrity-only is clear enough when the label remains
  visible.
- Accepted bridge lifecycle still needs the attached non-authority reminder.

## Recommended Operational Priorities

1. Make the governed return the primary operator answer.
2. Keep lifecycle visible as compact supporting evidence.
3. Move replay IDs and raw artifact JSON deeper by default.
4. Group bridge-specific controls away from older runtime controls.
5. Add rejection-specific operator repair hints.
6. Avoid new governance abstractions until real operator friction is lower.

## Practical Recommendation

Recommended next practical milestone:
`BRIDGE_OPERATOR_SURFACE_SIMPLIFICATION_V1`.

Scope should be rendering-only and operator-first:

- no new runtime behavior;
- no new transport protocol;
- no endpoint;
- no provider execution;
- no orchestration;
- no durable replay backend.

The goal should be to make the bridge feel like one clear governed operator
result with expandable evidence, not a large audit document.
