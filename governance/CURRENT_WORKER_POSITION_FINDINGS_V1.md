# Current Worker Position Findings V1

Status: reconstruction findings.

## Finding 1: Worker Is Already Constitutionally Positioned

Worker is already positioned as execution-only inside the core invariant.

Evidence:

- `FIRST_USEFUL_AIGOL_V1_FREEZE` freezes "Worker executes."
- `REAL_WORKER_ATTACHMENT_MODEL_V1` defines Worker as an execution-only participant.
- `WORKER_ATTACHMENT_BOUNDARY_V1` states Worker receives only authorized execution requests.

## Finding 2: Worker Authority Is Narrow And Explicit

Worker currently possesses execution participation only after AiGOL authorization.

Worker does not possess:

- authorization authority
- governance authority
- replay authority
- proposal authority
- capability expansion authority
- persistence authority

## Finding 3: Worker Relationship To AiGOL Is Defined

AiGOL validates, authorizes, rejects, governs, and records.

Worker executes only the authorized bounded request and returns replay-visible evidence.

## Finding 4: Worker Relationship To LLM Is Defined

LLM does not send executable authority to Worker.

LLM output becomes untrusted proposal input. AiGOL governance stands between proposal and Worker execution.

## Finding 5: Worker Replay Expectations Are Defined

Worker replay mapping is already specified:

- governed execution request
- AiGOL authorization evidence
- worker identity envelope
- capability binding evidence
- worker execution request
- worker result evidence
- worker termination evidence
- governed return linkage

## Finding 6: Worker Replaceability Is Not Yet Canonical

Existing artifacts imply a worker boundary but do not yet canonicalize interchangeable workers, worker pools, worker discovery, or domain-specific workers.

## Finding 7: Worker Registration Is Not Yet Defined

Existing artifacts define attachment and identity fields, but not a registration or discovery process.

## Finding 8: Worker Isolation Is Partially Defined

Worker containment is defined semantically:

- no self-authorization
- no hidden persistence
- no replay mutation
- no continuation after termination

An implemented sandbox or external worker isolation runtime is not yet defined in this Worker-specific layer.
