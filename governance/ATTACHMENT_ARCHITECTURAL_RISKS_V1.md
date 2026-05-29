# Attachment Architectural Risks V1

Status: analysis-only risk record.

## Risk Principle

Real attachment is safe only if it preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## LLM Attachment Risks

### Proposal Becomes Instruction

Risk: external LLM output may be treated as authoritative instruction instead of untrusted proposal input.

Required control: normalize and validate through AiGOL before execution request creation.

### Provider Identity Ambiguity

Risk: model output without deterministic provider identity weakens replay lineage.

Required control: fail closed on missing provider id, response id, model id, invocation id, or response hash.

### Hidden Continuation

Risk: live inference can invite retries, streaming continuation, multi-turn carryover, or implicit memory.

Required control: first attachment must be single-shot, replay-scoped, non-streaming, non-retrying, and non-persistent.

### Capability Drift

Risk: model output may request unsupported or mutating capabilities.

Required control: proposal bridge must continue to reject unsupported capabilities and forbidden intent.

## Worker Attachment Risks

### Worker Self-Authorization

Risk: a worker adapter may decide it is authorized to execute.

Required control: worker invocation must require AiGOL authorization evidence and must reject self-authorization.

### Capability Expansion by Binding

Risk: attaching a real worker may accidentally introduce new execution power.

Required control: first worker attachment must bind only existing read-only capabilities.

### Hidden Worker State

Risk: a worker may persist hidden state across runs.

Required control: worker replay scope and termination state must be explicit; hidden persistence fails closed.

### Replay Contamination

Risk: worker results may not map cleanly to replay lineage.

Required control: every worker input, boundary decision, output, and termination state must be replay-visible.

## Shared Risks

### Constitutional Baseline Drift

Risk: attachment work may reinterpret the freeze baseline as permission to expand.

Required control: attachment milestones must preserve `FIRST_USEFUL_AIGOL_V1` and explicitly certify non-expansion.

### Authority Separation Erosion

Risk: LLM or worker attachment may blur proposer, governor, executor, and recorder roles.

Required control: attachment records must keep roles explicit and reject role ambiguity.

### Replay Centrality Weakening

Risk: summaries or provider/worker logs may be treated as replay substitutes.

Required control: replay remains the source of truth; summaries and logs remain views or evidence inputs.

### Overengineering Pressure

Risk: real attachment may attract orchestration, agents, routing, retries, memory, or async coordination.

Required control: first real attachments should be single-provider, single-worker, single-flow, bounded, synchronous where practical, and fail-closed.
