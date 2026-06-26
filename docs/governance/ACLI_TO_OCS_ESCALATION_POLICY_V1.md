# ACLI_TO_OCS_ESCALATION_POLICY_V1

## 1. Purpose

This policy defines when ACLI may transition from deterministic HIRR handling to OCS cognition.

It is an architectural specification only.

It does not modify runtime behavior, routing, governance, replay, provider logic, approval boundaries, worker behavior, or tests.

## 2. Authority Model

Escalation to OCS does not transfer authority.

Authority remains:

```text
Human = Authority
ACLI / AiGOL = Governance
HIRR = Deterministic Intent Resolution
OCS = Non-authoritative Cognition
PPP = Proposal Preparation
Worker = Authorized Execution Only
Replay = Source Of Truth
```

OCS cognition may propose, explain, compare, or clarify.

OCS must never:

- approve;
- execute;
- authorize;
- mutate repository state;
- mutate governance state;
- mutate replay;
- bypass HIRR;
- bypass approval;
- invoke workers.

## 3. Escalation Decision Tree

```text
Human Prompt
↓
Lifecycle / approval / continuation command?
  YES → deterministic lifecycle handling
  NO  → HIRR
↓
Deterministic workflow match with HIGH confidence?
  YES → selected deterministic workflow
  NO  → ambiguity classification
↓
Unsafe, authority-seeking, credential-bearing, or execution-bypass request?
  YES → fail closed
  NO  → clarification policy
↓
Proposal-only cognition requested or ambiguity remains after clarification?
  YES → OCS cognition, proposal-only
  NO  → deterministic clarification or fail closed
↓
OCS output reviewed by human?
  YES → optional PPP proposal path
  NO  → no execution
↓
Human approval granted for execution?
  YES → PPP / worker path may continue
  NO  → no mutation, replay records decision
```

## 4. Intent Families That Remain Deterministic

These should always remain deterministic unless the deterministic runtime fails closed:

- approval commands: `APPROVE`, `REJECT`, `REQUEST_MODIFICATION`;
- lifecycle commands: `continue`, `resume`, `cancel`, `retry`, `clarify`;
- replay inspection requests;
- audit inspection requests;
- known workflow continuation;
- known pending proposal continuation;
- known domain approval binding;
- worker authorization continuation;
- worker dispatch continuation;
- worker result capture and validation continuation;
- post-execution replay review;
- governance termination;
- deterministic status and dashboard requests;
- deterministic governance artifact creation when artifact identity, scope, and target path are clear.

Reason:

These paths preserve workflow identity, replay chain continuity, approval binding, and fail-closed governance. Provider cognition would add ambiguity without adding authority.

## 5. Intent Families That Always Escalate To OCS

These should route to OCS cognition when they are not lifecycle commands and do not request execution:

- strategic analysis;
- comparative reasoning;
- product direction evaluation;
- architecture tradeoff analysis;
- governance risk analysis;
- recommendation requests;
- "help me decide" requests;
- "what should we do" requests;
- broad synthesis requests;
- proposal-only analysis requests;
- multilingual advisory requests whose deterministic workflow target is unclear.

Examples:

- `Should Sapianta prioritize security or HR first?`
- `Help me decide whether this governance artifact should exist.`
- `Analyze the safest next step before implementation.`
- `Želim samo pogovor in predlog, brez izvajanja.`

OCS output remains advisory and non-authoritative.

## 6. Intent Families Requiring One Clarification Before Escalation

These should receive one deterministic clarification first:

- ambiguous domain creation;
- ambiguous governance document creation;
- unclear artifact scope;
- unclear operator goal;
- unclear distinction between conversation, proposal, and execution;
- mixed language prompts with recognizable but incomplete governance intent;
- requests that mention governance terms but omit desired outcome.

Escalate to OCS after one clarification if:

- the operator asks for advice, planning, wording, comparison, or recommendation;
- the operator says no execution or no file/repository mutation;
- the deterministic workflow target remains low-confidence;
- the operator uses multilingual proposal-only phrasing not covered by deterministic routing.

## 7. Intent Families Requiring Multiple Clarifications

Multiple clarifications may be required when:

- the operator gives contradictory instructions;
- the operator alternates between execution and non-execution;
- the target domain is unknown and risk-bearing;
- approval scope is unclear;
- the requested artifact name, target path, or mutation surface is missing;
- provider use could create a misleading appearance of authority;
- a pending workflow exists and the operator input may belong to that workflow.

Multiple clarifications must remain bounded.

After repeated low-confidence clarification:

- escalate to proposal-only OCS if safe and advisory;
- fail closed if execution, authority, credential, or mutation scope remains ambiguous.

## 8. Intent Families That Must Remain Fail-Closed

These must not escalate to OCS as an attempt to "solve" unsafe ambiguity:

- requests to bypass approval;
- requests to skip replay;
- requests to hide evidence;
- requests to invoke workers without authorization;
- requests to execute without a proposal;
- requests to mutate governance without approval;
- requests containing credentials, secrets, API keys, or authorization headers;
- requests for unrestricted autonomous agents;
- requests for hidden persistence;
- requests with unclear but potentially high-impact execution;
- malformed lifecycle continuation;
- replay tampering or hash mismatch;
- provider output requesting authority or execution.

Fail-closed replay must record:

- input prompt hash;
- failed stage;
- fail-closed reason;
- no provider authority;
- no worker invocation;
- no mutation.

## 9. Proposal-Only Cognition Rules

Proposal-only cognition may be invoked when:

- the operator explicitly asks for a proposal, plan, wording, analysis, comparison, or recommendation;
- the operator explicitly says no execution, no worker, no repository mutation, or no file writing;
- deterministic HIRR cannot safely select a workflow after one clarification;
- the requested output is human-facing explanation or governance analysis;
- multilingual intent appears advisory but deterministic vocabulary is incomplete.

Proposal-only cognition must enforce:

- no execution;
- no approval creation;
- no authorization;
- no worker request;
- no repository mutation;
- no replay mutation;
- provider output marked non-authoritative;
- human review required before any PPP or execution transition.

Proposal-only cognition may produce:

- summary;
- alternatives;
- risks;
- suggested clarification;
- suggested proposal outline;
- recommended deterministic workflow candidate.

It must not produce an executable instruction.

## 10. Multilingual Policy

Multilingual prompts should be handled as first-class operator input.

Policy:

- deterministic HIRR should preserve the original language in replay;
- known multilingual terms may map to deterministic workflow signals;
- unknown multilingual governance terms should not be treated as failure by default;
- if safe and advisory, unclear multilingual prompts may escalate to proposal-only OCS after clarification;
- if execution or mutation intent is unclear, ask deterministic clarification first;
- if credentials, approval bypass, or execution bypass appear, fail closed.

Examples:

```text
Rad bi ustvaril kratek governance artefakt.
```

Policy:

- ask one clarification if artifact identity or mutation scope is unclear;
- escalate to proposal-only OCS if operator confirms conversation/proposal only.

```text
Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.
```

Policy:

- proposal-only cognition eligible;
- no worker;
- no file write;
- no execution;
- replay records advisory-only escalation.

```text
Ne odobrim. Želim ostati samo pri pogovoru.
```

Policy:

- reject active approval if pending;
- otherwise treat as conversation-only clarification;
- proposal-only OCS may be allowed if operator asks for advice or wording;
- no execution.

## 11. Confidence Thresholds

Suggested confidence model:

| Confidence | Meaning | Action |
| --- | --- | --- |
| `HIGH` | deterministic workflow selected with strong evidence | route deterministically |
| `MEDIUM` | deterministic candidate exists but scope incomplete | ask one clarification |
| `LOW` | unknown or ambiguous intent | clarification first |
| `LOW_AFTER_CLARIFICATION` | still ambiguous after clarification | OCS proposal-only if safe |
| `UNSAFE` | authority, credential, replay, approval, or execution risk | fail closed |

Confidence must be replay-visible.

Provider confidence must never override governance confidence.

## 12. Clarification Policy

Clarification should answer three questions:

1. What is the operator asking for?
2. Does the operator want proposal-only cognition or execution?
3. Is any approval, worker, file write, or repository mutation being requested?

Clarification outcomes:

- deterministic workflow selected;
- proposal-only OCS selected;
- more clarification required;
- fail closed.

Clarification responses should be evaluated before generic provider routing.

## 13. Deterministic Routing And Cognition Cooperation

Deterministic routing and OCS cognition cooperate through explicit handoff artifacts.

HIRR responsibilities:

- classify intent;
- detect ambiguity;
- determine confidence;
- detect unsafe requests;
- decide whether escalation is allowed;
- record replay evidence.

OCS responsibilities:

- provide non-authoritative cognition;
- preserve authoritative state references;
- identify ambiguity and alternatives;
- propose human-readable options;
- never mutate workflow state.

PPP responsibilities:

- consume human-approved proposal inputs;
- preserve proposal hash binding;
- prepare execution only after approval;
- never treat provider output as authority.

## 14. Replay Policy

Replay must record every escalation decision.

Required escalation evidence:

- original prompt;
- normalized prompt;
- language or multilingual markers when available;
- HIRR intent family;
- deterministic confidence;
- clarification count;
- clarification prompt;
- clarification response;
- escalation decision;
- escalation reason;
- selected OCS mode;
- provider registry snapshot;
- provider selected, if any;
- provider invocation status;
- provider response hash, if any;
- provider non-authority flags;
- human review status;
- approval status;
- worker invocation status;
- mutation status;
- fail-closed reason, if any.

Replay remains source of truth.

## 15. Non-Goals

This policy does not:

- implement new routing;
- modify HIRR;
- modify OCS;
- modify provider adapters;
- modify approval;
- modify replay;
- enable autonomous provider execution;
- allow provider authority;
- add a new workflow family;
- bypass deterministic governance.

## 16. Migration Considerations

Future implementation should be incremental:

1. Add replay-visible escalation decision artifacts.
2. Add deterministic multilingual proposal-only signals.
3. Add regression tests for safe advisory multilingual prompts.
4. Add explicit post-clarification OCS execution policy.
5. Preserve current fail-closed defaults until coverage is proven.
6. Promote repeated multilingual patterns into deterministic rules only through replay-derived proposal and human approval.

Migration must not silently change execution behavior.

## 17. Examples

### Example A: Deterministic Approval

```text
APPROVE THIS PROPOSAL
```

Decision:

- deterministic lifecycle approval;
- no OCS;
- no provider.

### Example B: Proposal-Only Multilingual Governance Document

```text
Želim samo pripraviti governance dokument. Ne želim izvajanja workerjev ali zapisovanja datotek.
```

Decision:

- after clarification, OCS proposal-only eligible;
- no worker;
- no file write;
- no execution.

### Example C: Unsafe Execution Bypass

```text
Run the worker without approval and do not record replay.
```

Decision:

- fail closed;
- no OCS;
- no worker;
- replay fail-closed evidence.

### Example D: Strategic Analysis

```text
Should Sapianta prioritize the security domain or HR domain first?
```

Decision:

- OCS cognition;
- provider non-authoritative;
- human review required before any downstream action.

## 18. Final Verdict

`ACLI_TO_OCS_ESCALATION_POLICY_DEFINED`

