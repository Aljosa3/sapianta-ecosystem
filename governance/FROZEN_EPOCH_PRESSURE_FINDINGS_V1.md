# Frozen Epoch Pressure Findings V1

Status: findings from first useful AiGOL pressure validation.

## Findings

### Finding 1: Malformed Operator Requests Fail Closed

Malformed human requests are rejected before execution. No capability is invoked.

### Finding 2: Unsupported Capabilities Fail Closed

Unsupported capability requests are rejected without creating new capability authority.

### Finding 3: Authorization Failure Remains Replay-Visible

Denied authorization produces a rejected governed result and replay summary with `FAILED_CLOSED` authorization status.

### Finding 4: Invalid Cognition Proposal Structures Fail Closed

Malformed proposal inputs do not become execution requests.

### Finding 5: Replay Corruption Is Detected

Tampered replay artifacts are rejected during replay summary reconstruction.

### Finding 6: Replay Ordering Violations Are Detected

Replay step ordering changes are detected and fail closed.

### Finding 7: Repeated Successful Runs Remain Isolated

Repeated successful runs preserve distinct flow identifiers and verified replay summaries.

### Finding 8: Repeated Failed Runs Remain Stable

Repeated failed runs preserve rejection status, fail-closed semantics, and verified replay summaries.

### Finding 9: Replay Reconstruction Is Stable Under Repeated Reads

Repeated replay summary reads return stable summary hashes.

### Finding 10: Filesystem Boundary Pressure Fails Closed

Forbidden filesystem paths are rejected while replay remains visible and verified.

## Conclusion

The frozen epoch pressure validation supports declaring the first useful AiGOL stable enough for completion review.
