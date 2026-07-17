# G31-18 CODEX Transport to Semantic Worker Result Capture Binding

Status: implemented and deterministically validated.

Date: 2026-07-17

Verdict class:

`G31_CODEX_RESULT_CAPTURE_IMPLEMENTED_LIVE_SUCCESS_UNPROVEN`

## Canonical owner and bounded caller

The Worker-owned bridge is
`aigol.runtime.codex_transport_to_worker_result_capture_binding_runtime`.
Its public entry point `capture_successful_codex_worker_result` is the only new
caller of the existing canonical owner
`aigol.runtime.worker_result_capture_runtime.capture_worker_result`.

AiCLI invokes this bridge immediately after the existing third activation
decision. It asks for no fourth decision and remains presentation and
orchestration only. `aicli_authorizes`, `aicli_executes`, `aicli_owns_replay`,
and `aicli_accepts_result` all remain false.

## Transport-to-semantic binding

G31-18 accepts only one `EXECUTION_ACCEPTED` G31-17B activation. A narrow
helper extracted in the G31-17B owner revalidates the complete contextual
request, grounding, first and second decisions, execution authorization,
CODEX Worker selection, assignment, dispatch, invocation, execution candidate,
G31-16B evidence, third approval, fixed execution request, activation Replay,
receipt, repository snapshot, and role-separated `CODEX -> codex-execution`
identity.

G31-17B now records compatible extension fields inside its existing third
Replay wrapper: process-start count, exact workspace, fixed process-request
identity, response Replay identity, and matching pre/post repository snapshots.
Its three-step ordering, artifact families, approval semantics, and activation
behavior remain unchanged.

The bridge reconstructs the fixed request and recomputes the existing Codex
receipt from the supplied dispatch. It requires:

- exactly one process start;
- `codex exec <bounded_prompt>` and no other arguments;
- `shell=False`;
- the exact approved workspace and 30-second timeout;
- `EXECUTION_ACCEPTED`, return code zero, and no timeout;
- valid adapter command/consumer validation;
- authentic non-empty stdout strictly below the 4,096-character and byte
  capture bounds;
- SHA-256 equality between exact UTF-8 stdout bytes and the receipt;
- current repository grounding and exact post-activation repository snapshot;
- no Provider authority or repository mutation.

Stderr remains transport diagnostic evidence. It is hashed in the receipt but
is never copied into the semantic-output field.

The bridge constructs one lineage envelope required by the existing Worker
output contract. Its payload contains the exact stdout text and bytes/hash,
receipt identity/hash lineage, activation Replay identity/hash, and fixed
process-request identity/hash. Identity, invocation, authorization, allowed
output, and operation fields are derived from the reconstructed invocation;
semantic text is neither repaired nor synthesized.

The canonical four-step result-capture Replay stores the Worker-output and
payload hashes using only existing artifact families:

1. `000_result_capture_evidence_recorded.json`;
2. `001_result_capture_classification_recorded.json`;
3. `002_result_capture_artifact_recorded.json`;
4. `003_result_capture_result_recorded.json`.

No new canonical result artifact or parallel Replay subsystem was introduced.
The canonical family intentionally stores semantic payload hashes rather than
duplicating raw payload bytes. G31-18 reconstruction therefore requires the
supplied bounded output artifact and proves that its artifact/payload hashes
equal the canonical Replay.

## Authority and ownership matrix

| Boundary | Owner | Authority granted |
|---|---|---|
| Third process decision | existing G31-17B approval | one fixed process only |
| Fixed process request and receipt | existing Codex adapter | bounded transport only |
| G31 transport verification | G31-17B owner/helper | validation only |
| Worker-output envelope | G31-18 Worker bridge | exact transport-to-lineage binding |
| Result capture | existing `capture_worker_result` | capture only |
| Result validation | existing later runtime | not entered |
| Human review/acceptance | existing later boundary | not entered |
| Mutation, commit, deploy, release | separate later authorities | not granted |

No Provider connector, new approval, new authorization token, or execution
process is created by G31-18. Repeated capture cannot start another process.

## Success and failure truth table

| Transport outcome | Semantic capture | Validation | Acceptance | Mutation |
|---|---:|---:|---:|---:|
| Authentic success, return code zero, bounded non-empty stdout | yes, once | no | no | no |
| `EXECUTION_FAILURE` or non-zero exit | no | no | no | no |
| Timeout | no | no | no | no |
| Empty output | no | no | no | no |
| Output at capture limit or otherwise truncated | no | no | no | no |
| Receipt/output/hash/request substitution | no | no | no | no |
| Incomplete, reordered, cross-session, or changed Replay | no | no | no | no |
| Duplicate destination, receipt reuse, or repeated capture | no | no | no | no |
| Repository drift | no | no | no | no |
| CODEX-to-Provider identity substitution | no | no | no | no |

Successful final truth is:

```text
worker_process_started = true
subprocess_invoked = true
transport_receipt_successful = true
authentic_worker_output_present = true
semantic_worker_result_captured = true
provider_invoked = false
additional_worker_process_started = false
result_validated = false
result_accepted = false
repository_mutated = false
commit_created = false
deployed = false
released = false
```

Every failed transport preserves false semantic capture, validation,
acceptance, and repository mutation. Failed eligibility is decided before the
canonical capture owner is called and creates no semantic-capture Replay.

## One-time and fail-closed evidence

The bridge rejects an existing destination before calling the canonical owner.
It scans same-session canonical capture Replay for the exact semantic payload
hash, which binds receipt, activation Replay, process request, and output bytes.
The same receipt therefore cannot be captured at another destination, even
with a repeated caller request. Canonical output and payload hashes are
reconstructed after success.

Focused tests cover injected success, failure/non-zero status, timeout, empty
output, bounded-output truncation, stdout and receipt hash substitution,
approval/candidate/Worker/Provider substitution, activation Replay tampering,
cross-session paths, duplicate destination, receipt reuse, repeated capture,
repository drift outside the grounded target list, canonical call counts, and
separation of validation, acceptance, and mutation.

## Validation

- G31-18 focused module: 13 passed.
- G31-10 through G31-17B regression: 89 passed.
- Worker lifecycle, activation, result-capture, and result-validation group:
  111 passed.
- Governance tests: 5 passed. Governance engine: `PARTIALLY_CONFORMANT`, 18
  passed, two known hook-drift findings, zero critical violations;
  deterministic, fail-closed, and read-only.
- Complete repository suite: 6,412 passed, 4 skipped, 0 failed in 345.69
  seconds.
- Targeted `py_compile` and final `git diff --check`: passed.

One disposable PTY proof used exactly the existing three `/approve` decisions
and started one real `codex exec` process. It returned `EXECUTION_FAILURE`, as
in G31-17B's live proof. G31-18 reported `FAILED_CLOSED`, did not call canonical
semantic capture, created no result-capture Replay, performed no retry, and did
not fabricate output. The fixed receipt preserved `process_start_count = 1`,
`semantic_worker_result_captured = false`, and `repository_mutated = false`.
Source hashes remained
`3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75`
and `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4`
before and after. The disposable workspace and Replay were removed. No other
live process was attempted, so live semantic-capture success remains unproven.

The requested complete suite exposed a pre-existing test-isolation defect: it
temporarily appended 69 records to the protected default
`.runtime/aigol/ledger/governed_returns.jsonl` and refreshed its associated
CHATGPT ingress evidence despite the G31-18 tests themselves using disposable
roots. The original 158-line ledger prefix matched the hash captured before
testing, and its last original canonical record regenerated all five evidence
files with their exact captured hashes. Those six protected files were restored
byte-for-byte to the pre-test dirty state. The three protected root markers
remained empty and unchanged throughout. No protected path is included in the
G31-18 changed surface or commit commands.

## Changed surface and size

Expected G31-18 surface:

- `aigol/runtime/codex_transport_to_worker_result_capture_binding_runtime.py`;
- narrow compatible extraction in
  `aigol/runtime/codex_worker_activation_binding_runtime.py`;
- minimal continuation in `aigol/cli/aicli.py`;
- `tests/test_g31_18_codex_transport_to_worker_result_capture_binding.py`;
- this governance report.

Production additions are 445 physical lines: 322 in the thin bridge, 107 in
the G31-17B helper/receipt extension, and 16 in AiCLI. This is 193 lines and
approximately 30% smaller than G31-17B's 638 production additions, but exceeds
400 by 45 lines. The excess is the explicit request/receipt recomputation,
repository snapshot continuity, canonical four-step reconstruction, and
success/failure truth separation needed to prevent transport diagnostics or a
failed receipt from becoming semantic output. No parallel architecture was
added.

## Explicit stop boundary and progress

G31-18 stops immediately after `WORKER_RESULT_CAPTURED`. It does not call a
semantic validator, review or accept a result, apply output, mutate the
repository, create a commit, deploy, or release. G31-16B
`WORKER_EXECUTION_COMPLETED` remains pre-process governance evidence and is
never used as Worker output.

Evidence-scoped no-copy/paste conversational governed development is estimated
at **99.9%** and whole-project progress at **89.5%**. These are planning
indicators, not production-readiness or full-conformance certification.

## Recommended next state

`G31_CAPTURED_CODEX_WORKER_RESULT_TO_SEMANTIC_VALIDATION_AUDIT_REQUIRED`
