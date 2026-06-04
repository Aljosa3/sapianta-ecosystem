# AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_GAP_ANALYSIS_V1

## Status

Review-only gap analysis.

## Gap 1: Approval Choice Surface

Current behavior:

- pending approval is resumed only by a literal `approve` conversation turn;
- no explicit operator menu is shown;
- no inline command exposes the approval packet before decision.

Required capability:

- deterministic choices for approve, reject, request modification, inspect
  packet, and exit;
- replay-visible operator decision selection;
- confirmation language that names the target chain and approval scope.

## Gap 2: Reject Path

Current behavior:

- approval resume accepts only `APPROVED`;
- rejection is available in a separate improvement approval runtime but not in
  implementation approval resume for conversation-to-implementation handoff;
- CLI rejection of a pending implementation approval is not first-class.

Required capability:

- human implementation rejection artifact;
- replay-visible terminal rejection outcome;
- no downstream implementation handoff after rejection;
- operator summary explaining that the chain closed without mutation.

## Gap 3: Modification Request Path

Current behavior:

- requested changes cannot be recorded as a bounded continuation of the pending
  approval packet;
- modification currently behaves like missing/invalid approval.

Required capability:

- human modification request artifact;
- replay-visible requested-change rationale;
- deterministic return to proposal/context revision without execution,
  dispatch, or hidden mutation.

## Gap 4: Replay Inspection Diagnostics

Current behavior:

- chain inspection fail-closes safely;
- source replay is not mutated;
- report artifacts are written under a report root.

Required capability:

- explicit operator-facing distinction between source replay and inspection
  report evidence;
- clearer failure classes for missing root, missing chain, ambiguous latest
  chain, corrupted hash, and incomplete lifecycle evidence.

## Gap 5: Registry Resolution Feedback

Current behavior:

- unknown domains fail closed through classification or registry errors;
- supported factory domains are not shown to the operator when resolution fails.

Required capability:

- registry resolution summary in CLI output;
- supported domain list for unknown domain prompts;
- explicit fail-closed reason when a domain is known but not executable for the
  requested lifecycle.

## Gap 6: OCS Transition Readiness

Current behavior:

- approval and replay primitives are governance-preserving;
- operator experience still depends on implicit command knowledge.

Required capability:

- pre-OCS operator decision protocol;
- deterministic pending approval inspection;
- replay-visible rejection and modification outcomes;
- robust chain inspection UX suitable for non-developer operators.
