# AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_RECOMMENDED_FIX_ORDER_V1

## Status

Review-only recommended fix order.

## Fix Order

1. Certify a pending approval inspection command.

   The operator should be able to inspect approval scope, target domain,
   proposal summary, planned artifacts, known gaps, and replay references before
   deciding.

2. Add first-class rejection.

   Implement a human implementation rejection artifact and terminal replay
   outcome. Rejection must not create an implementation handoff, execution
   authorization, dispatch, invocation, or executable bundle.

3. Add first-class modification request.

   Implement a human modification request artifact with bounded requested
   changes and replay-visible continuation state. It should return to proposal
   revision rather than bypassing validation.

4. Improve approval CLI menu.

   Show deterministic choices when approval is pending:
   `approve`, `reject`, `request changes`, `show approval`, and `exit`.

5. Improve replay inspection diagnostics.

   Split operator failure messages into missing root, missing chain, ambiguous
   latest chain, corruption, and incomplete lifecycle classes.

6. Improve registry resolution feedback.

   On unknown or unsupported domain prompts, show supported registry domains,
   executable status, and the exact fail-closed reason.

7. Re-run pre-OCS operator acceptance validation.

   Validate approve, reject, request changes, missing replay root, unknown
   domain, known unsupported domain, and show-latest-chain failure paths.

## Recommended Next Milestone

`AIGOL_PRE_OCS_APPROVAL_DECISION_PROTOCOL_V1`

This milestone should implement the operator decision protocol before any OCS
transition work begins.
