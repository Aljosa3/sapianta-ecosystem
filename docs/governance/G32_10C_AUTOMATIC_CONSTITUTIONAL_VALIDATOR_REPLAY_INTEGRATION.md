# Generation 32-10C: Automatic Constitutional Validator Replay Integration

Status: IMPLEMENTED — REPLAY-OWNED, CONSTITUTIONALLY NEUTRAL  
Date: 2026-07-27  
Scope: First executable connection from ECC and Evidence Manifest validation to Platform Replay

## 1. Purpose and Boundary

This integration makes an already-complete immutable Automatic Constitutional
Validator result visible to Platform Replay. It does not alter validation
semantics, Replay semantics, Governance, Certification, authorization, Worker
selection, Provider invocation, or execution.

The Validator remains read-only. It does not import, invoke, or write Replay.
A caller explicitly submits the immutable `ConstitutionalValidationResult` to
the Replay-owned recording function after validation has completed.

## 2. Execution Lifecycle

```text
ECC executable contract + immutable Evidence Manifest + evidence inputs
        |
        v
Automatic Constitutional Validator Kernel
        |  immutable ConstitutionalValidationResult
        v
Platform Replay record_constitutional_validator_result(...)
        |  one immutable replay wrapper
        v
Platform Replay reconstruct_constitutional_validator_replay(...)
```

The boundary is intentionally one-way. Validation has no Replay write path;
Replay only records and later verifies the completed result.

## 3. Replay Event and Ordering

The isolated replay stream has exactly one ordered step:

| Index | File | Step | Event |
| --- | --- | --- | --- |
| 0 | `000_constitutional_validator_result_recorded.json` | `constitutional_validator_result_recorded` | `CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED` |

The event artifact type is `CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1`; its
service version is `AUTOMATIC_CONSTITUTIONAL_VALIDATOR_REPLAY_V1`. Both the
event and its immutable wrapper carry independently verified transport hashes.
An existing or non-empty target replay directory fails closed, preventing a
second recording from being appended or substituted.

## 4. Result Model, Identity, and Lineage

The canonical replay result model contains:

- Validator identity and version.
- ECC contract ID, version, and contract hash.
- Evidence Manifest ID, version, and manifest hash.
- Validation, invocation, session, and chain identifiers.
- Overall outcome, scheduled requirements, rule counts, and failure codes.
- The complete immutable Validator result and its canonical `result_hash`.

`validator_execution_id` is deterministically derived from Validator identity,
the ECC and Manifest hashes, the Validator invocation identities, and the
Validator result hash. `replay_identity` is deterministically derived from the
execution identity plus the ECC, Manifest, and result hashes.

`recorded_at` is a Replay-event field provided by the caller. It is excluded
from the canonical Validator-result model and derived identities, so it does
not alter validation determinism.

## 5. Reconstruction and Fail-Closed Verification

Reconstruction verifies, before returning any result:

1. Exact replay index, step, schema, and owner.
2. Wrapper and event transport hashes.
3. The immutable Validator result structure and canonical `result_hash`.
4. Deterministic execution and Replay identities.
5. Summary counts, failure codes, and ECC/Manifest lineage bindings.
6. Explicit lifecycle-boundary flags.

It then returns the original Validator result together with the ECC and
Evidence Manifest identity bindings. Tampered results, hashes, ordering,
identities, summaries, or lineage bindings fail closed.

## 6. Constitutional and Authority Impact

This is Replay recording only. The recorded event explicitly states:

- `replay_owner = PLATFORM_CORE_REPLAY`
- `replay_visible = true`
- `validator_replay_persisted = false`
- `governance_assessed = false`
- `certification_performed = false`
- `authorization_created = false`
- `worker_assigned = false`
- `provider_invoked = false`
- `execution_requested = false`

The `validator_replay_persisted` value remains false because the Validator did
not persist anything; Platform Replay owns persistence. Replay visibility
therefore creates no authority, approval, certification, or execution effect.

## 7. Compatibility and Demonstration

The integration is a new, isolated replay artifact type and does not change
existing replay streams or wrappers. Existing historical replay reconstruction
continues to use its own versions and step sequences.

The end-to-end integration test validates the certified Filesystem Adapter ECC
fixture, records the resulting immutable Validator outcome through Platform
Replay, reconstructs it, and verifies the ECC and Evidence Manifest hashes,
PASS outcome, and absence of Governance or Certification action.

## 8. Static Validation

The implementation is covered by focused Replay unit tests, the existing
Validator kernel suite, and the certified-fixture integration test. Validation
also checks that the Validator package has no dependency on this Replay module.

No Governance, Certification, policy, authorization, Worker, capability, or
constitutional artifact was modified by this integration.
