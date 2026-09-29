# S2 WRONG_SCOPE one-shot terminal report

The one authorized operation ended without WRONG_SCOPE acceptance. E05 remains 12/18.

The fresh S2 host authority was created and consumed exactly once. Final native host admission and LY reobservation passed; LT authenticated one reservation, one child invocation and a terminal status. QEMU/FM exited 0 after guest poweroff, while the guest serial log reports harness exit 1 and `RuntimeError: runtime P11 is not the committed JM implementation`. QEMU success therefore does not establish guest acceptance.

The rejection occurred in ER.load_authenticated_fresh_operation_context before raw evidence initialization, guest authority checks and the scope comparator. No raw guest record, execution seal or teardown seal was produced. Missing counters are not synthesized. The guest powered down and no matching S2 QEMU process remains. Spent runtime state is retained without reset.

The S1 preservation hashes and S2 sealed subject remain unchanged. No production source was changed; no retry, replay or repair occurred. The exact authority, invocation, LT journal, pre/post receipts and serial log are retained with SHA-256 bindings. Terminal reduction contains the complete counter and frontier report.

Next boundary: independent Human review of this terminal outcome. This approval authorizes no further attempt or repair.
