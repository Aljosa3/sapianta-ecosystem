# End To End Operator Flow Replay V1

Status: replay evidence model for the first governed read-only operator flow.

## Operator Replay Chain

The operator-level replay chain is:

```text
human_prompt
cognition_proposal
bridge_capture
governed_result
```

## Nested Bridge Replay

The operator flow preserves the existing proposal bridge replay:

```text
contribution
normalized_request
validation
authorization
execution
return
```

## Replay Guarantees

Replay evidence must preserve:

- human prompt capture
- untrusted cognition proposal
- AiGOL validation and authorization evidence
- deterministic read-only worker/capability execution evidence
- governed return evidence
- fail-closed artifacts for rejected flows

Replay reconstruction must fail closed on missing artifacts, ordering mismatch, replay hash mismatch, or artifact hash mismatch.
