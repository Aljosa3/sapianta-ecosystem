# AIGOL_REPLAY_INSPECTION_RECOMMENDED_FIX_ORDER_V1

## Status

Review-only recommended fix order.

## Fix Order

1. Define `AIGOL_REPLAY_INSPECTION_OPERATOR_CONTRACT_V1`.

   Specify pure inspection, optional persistence, repeatability, diagnostics,
   and source replay immutability.

2. Add pure reconstruction mode.

   Refactor unified replay reconstruction so report construction can occur
   without `_persist_report`.

3. Make `show-*` commands pure by default.

   Default operator inspection should not write report artifacts.

4. Add explicit persisted report mode.

   Add an intentional flag or separate command for persisted evidence creation.
   Require unique report id or certified idempotent reuse.

5. Improve collision diagnostics.

   Replace low-level append-only filename output with operator-facing guidance
   when persisted report collision occurs.

6. Add regression tests.

   Include repeated `show-latest-chain`, repeated `show-chain`, pure no-write,
   persisted report, and report collision diagnostic tests.

7. Re-certify chain inspection for OCS.

   Certify only after repeatability and read/persist separation are validated.

## Recommended Next Milestone

`AIGOL_REPLAY_INSPECTION_READ_ONLY_REPEATABILITY_V1`

This should be completed before OCS transition.
