# AIGOL_FIRST_REAL_USAGE_EPOCH_UX_GAP_ANALYSIS_V1

## Status

UX gap analysis.

## Gap Summary

AiGOL can complete several governed lifecycles, but the CLI still exposes too
much internal machinery and too little operator guidance.

## UX Gap 1: Missing Operator Summary Layer

Current behavior:

The CLI prints internal stage summaries directly.

Needed behavior:

Every operation should begin with a compact result:

```text
Status: TERMINATED
Outcome: Domain bundle created
Domain: MARKETING
Files created: 5
Replay: <path>
Real implementation logic: NOT CREATED
Next inspection: <command>
```

## UX Gap 2: Missing Workspace Readiness Check

Current behavior:

Workspace shape is validated during runtime execution.

Needed behavior:

Before operation:

- detect missing workspace directories;
- display exact missing paths;
- explain whether AiGOL will create them or the operator must prepare them.

## UX Gap 3: Missing Chain Discovery

Current behavior:

Replay inspection works with an exact turn root. Aggregate roots fail closed
when multiple chains exist.

Needed behavior:

- list latest sessions and turns;
- select latest deterministically;
- allow `show-chain <chain_id>` from aggregate root;
- show the exact command for deeper inspection.

## UX Gap 4: Missing Operator-Safe Vocabulary

Current behavior:

Internal governance terms are correct but can sound like real execution.

Needed behavior:

Use a two-layer display:

- operator outcome language;
- optional internal lifecycle language.

The default view should not make placeholder worker invocation sound like an
external worker executed real implementation logic.

## UX Gap 5: Missing Clarification Continuation UX

Current behavior:

Clarification and request-modification states are recorded but do not provide a
strong next-step surface.

Needed behavior:

- show expected answer format;
- preserve prior context visibly;
- offer examples of valid clarification responses;
- keep the pending clarification discoverable.

## UX Gap 6: Missing OCS Operator Surface

Current behavior:

OCS is certified but not directly visible in ordinary operator usage.

Needed behavior:

- show OCS summary when OCS is involved;
- expose context, cognition, ambiguity, semantic resolution, and PPP candidates
  without requiring artifact-file knowledge;
- keep authority boundaries visible.

## UX Gap 7: Missing Replay-Derived Intent Workflow Surface

Current behavior:

Replay-derived intent exists as runtime capability, but the operator usage
epoch did not expose a direct CLI workflow from observed replay history into
candidate improvement intent.

Needed behavior:

- inspect replay for improvement candidates;
- show candidate evidence;
- ask for human decision before any downstream handoff;
- preserve proposal-only boundary.

## UX Gap 8: Missing Domain Registry Feedback

Current behavior:

Unknown or multi-domain prompts can fail through provider fallback messages.

Needed behavior:

- list registered domains;
- identify unknown names;
- identify multiple requested domains;
- explain whether one operation can contain multiple domains.

