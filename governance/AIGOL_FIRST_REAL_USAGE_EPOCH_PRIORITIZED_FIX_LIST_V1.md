# AIGOL_FIRST_REAL_USAGE_EPOCH_PRIORITIZED_FIX_LIST_V1

## Status

Prioritized fix list.

## Priority 1: Compact Operator Summary

Problem:

Successful operations print too much internal lifecycle detail.

Fix:

Default conversation output should show compact result, created artifacts,
replay path, authority boundaries, and next inspection command.

Priority: highest.

## Priority 2: Replay Inspection From Aggregate Root

Problem:

`show-latest-chain` and `show-chain` fail from a multi-session runtime root.

Fix:

Resolve latest chain deterministically or show candidate chains with exact
commands.

Priority: highest.

## Priority 3: Workspace Preflight Path Details

Problem:

Missing workspace directories produce an opaque fail-closed reason.

Fix:

Name exact missing paths and required workspace layout.

Priority: high.

## Priority 4: Registry-Aware Unknown And Multi-Domain Feedback

Problem:

Unknown domain and multi-domain prompts surface as provider clarification
fallback failures.

Fix:

Render registry failure or multi-domain ambiguity directly.

Priority: high.

## Priority 5: Human Decision Continuation Guidance

Problem:

`REQUEST_MODIFICATION` records clarification state but does not tell the
operator what to do next.

Fix:

Show next-step instructions and preserve pending modification context.

Priority: high.

## Priority 6: Authority Vocabulary Cleanup

Problem:

Execution and worker lifecycle terms sound like real external execution even
when the lifecycle remains governed and bounded.

Fix:

Use operator-safe labels before internal lifecycle terms.

Priority: medium-high.

## Priority 7: OCS Operator Inspection Surface

Problem:

OCS is certified but not naturally visible in CLI usage.

Fix:

Expose existing OCS chain summaries through conversation output or inspection
commands.

Priority: medium.

## Priority 8: Replay-Derived Intent Operator Workflow

Problem:

Replay-derived improvement intent is not reachable as a normal operator
workflow during this epoch.

Fix:

Add an operator command or route that selects replay scope, runs existing
replay-derived intent generation, and displays proposal-only candidates.

Priority: medium.

## Priority 9: Pending State Discovery

Problem:

Operators need to know which approvals, modifications, or clarifications are
pending.

Fix:

Add or improve pending-state inspection for conversation sessions.

Priority: medium.

