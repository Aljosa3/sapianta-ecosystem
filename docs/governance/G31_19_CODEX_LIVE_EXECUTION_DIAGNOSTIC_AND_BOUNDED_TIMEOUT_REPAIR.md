# G31-19 CODEX Live Execution Diagnostic and Bounded Timeout Repair

## Verdict

`G31_CODEX_LIVE_EXECUTION_FAILURE_CAUSE_IDENTIFIED_FIX_REQUIRED`

Baseline commit:
`f1c0347927ab91240c0d20a71988a3455545c997`

Nested `sapianta_system` adapter baseline:
`5e541bbaa63d584c3de1d21ed622339fed2ca325`

The current remaining live failure classification is exactly
`CODEX_EXECUTION_TIMEOUT`. The one post-diagnostic confirmation reached a real
authenticated CODEX task, but the approved 30-second process boundary expired
before stdout was produced. The bounded correction to 60 seconds is
implemented and deterministically validated, but the allowed confirmation
attempt was consumed before that second cause was known. Live success and
semantic Worker result capture therefore remain unproven.

The diagnostic attempt also identified and separated the earlier first
barrier: `CODEX_WORKSPACE_OR_PERMISSION_FAILURE`. In the default tool sandbox,
`/home/pisarna/.codex/state_5.sqlite` was read-only, so the in-process CODEX
app-server could not initialize. Explicit authority for the distinct
confirmation removed that environment barrier without copying, exposing, or
persisting credentials.

## Read-only prerequisites

- executable: `/home/pisarna/.vscode/extensions/openai.chatgpt-26.707.41301-linux-x64/bin/linux-x86_64/codex`;
- mode: `0755`, regular executable file;
- version: `codex-cli 0.144.0-alpha.4`;
- fixed arguments supported: `codex exec [PROMPT]`;
- authentication status: `Logged in using ChatGPT`;
- disposable workspace: readable, writable, searchable, and grounded to the
  two approved fixture source files;
- outer process contract: `codex exec <bounded_prompt>`, `shell=False`, one
  process, no retry, no Provider.

The non-fatal CLI warning about PATH-alias creation was observed separately
from both failure causes. No configuration value, credential, token, private
environment value, or unredacted prompt is recorded in this report. The prompt
is represented by SHA-256
`312ab4289c1e8f1f0b9aa7fdf312601f46242107a0237f2632f2a63ac97a1858`.

## Diagnostic receipt

Retained Replay:
`/tmp/g31-19-diagnostic-Rzikbo/runtime/G31-19-DIAGNOSTIC/CODEX-WORKER-ACTIVATION-f7001ee1408545f6`

- receipt status: `EXECUTION_FAILURE`;
- receipt id: `CODEX-EXECUTION-RECEIPT-3afce3a2b8300e63bc0bd241`;
- wrapper Replay hash:
  `sha256:cef83531499a3c294aa77f1905e146f7a0c2a4238dad47d7ff8bece086f4dc8c`;
- return code: `1`;
- timed out: `false`;
- duration: `0.060581` seconds;
- exception type/message: empty because the child process started and itself
  returned the failure;
- stdout: 0 bytes, not truncated,
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- stderr: 919 bytes, not truncated,
  `d59cab84877e123e43a1f9a593b385f42e308e89a1fafebbfca04489979602f1`;
- bounded cause: the CODEX state database reported `attempt to write a readonly
  database`, followed by app-server initialization failure with `Read-only file
  system (os error 30)`;
- shell: `false`; timeout: 30 seconds; process-start count: 1;
- approval count: 3; Provider invoked: false; retry: false;
- repository snapshot before/after:
  `sha256:a42e51fe32c5f5752a987e7d5080580c4ce5113c560b78c89ed52f3bf3854ba2`;
- semantic result captured: false; repository mutated: false.

The diagnostic Replay preserved enough bounded evidence to classify the
failure without another reproduction.

## Confirmation receipt

Retained Replay:
`/tmp/g31-19-confirmation-5XCClR/runtime/G31-19-CONFIRMATION/CODEX-WORKER-ACTIVATION-1bf7e5b6db37b250`

- receipt status: `EXECUTION_TIMEOUT`;
- receipt id: `CODEX-EXECUTION-RECEIPT-4b4be52c4efc3f95db4edfd1`;
- wrapper Replay hash:
  `sha256:295f5c0bc92268e46f7efc86821b062e428cb297e155309be5a6209d9203854a`;
- return code: `124`;
- timed out: `true`;
- duration: `30.016309` seconds;
- exception: `TimeoutExpired`, `process exceeded the bounded execution
  timeout`;
- stdout: 0 bytes, not truncated,
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- stderr: 3,715 bytes / 3,713 characters, not truncated,
  `0af63b0fde647b204d0430e4e01387e0bad647db0f0a9a6b47eb45d5eebf8deb`;
- bounded excerpt proved CODEX initialized, entered the exact disposable
  workspace, and performed read-only inspection before timeout;
- shell: `false`; approved timeout: 30 seconds; process-start count: 1;
- approval count: 3; Provider invoked: false; retry: false;
- repository snapshot before/after:
  `sha256:5f3b6cd79f01369ea52d483f5bafbea536ecad7ff140ca39b44ffdc159cc193c`;
- source file hashes remained
  `3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75`
  and
  `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4`;
- authentic semantic output: false; result-capture Replay: absent;
- validation, acceptance, mutation, commit, deployment, and release: false.

This attempt was the distinct post-diagnostic confirmation, not an automatic
retry. No further live process was started after it exposed the timeout.

## Smallest bounded corrections

1. The existing canonical CODEX dispatch now retains duration, exception
   classification and bounded message, original character/byte lengths, and
   truncation flags. These diagnostics are copied into the existing receipt
   and execution evidence; no new artifact family exists.
2. The G31 activation timeout is now a finite 60 seconds. Thirty seconds
   allowed initialization and repository inspection but no final transport
   output. Sixty seconds is the smallest conventional bounded increment and
   remains below the existing adapter validator maximum of 120 seconds.
3. The exact 60-second value is visible in the third activation review and is
   bound into the review hash, human approval, CODEX execution request,
   dispatch/receipt metadata, and activation Replay. Substitution to 30 seconds
   at approval, request, or receipt reconstruction fails closed.
4. Measured duration remains evidence but is excluded from deterministic
   response and read-only observability identities. All command, timeout,
   status, output, hashes, exception classification, and truncation facts
   remain identity- or Replay-bound.

No Provider path, parallel adapter, new authorization system, fourth approval,
retry, fallback, semantic validation, result acceptance, or mutation authority
was introduced.

## Truth table

| Fact | Prior live report | Diagnostic | Confirmation | Corrected contract |
|---|---:|---:|---:|---:|
| third human decisions | 3 | 3 | 3 | 3 required |
| process starts | 1 | 1 | 1 | exactly 1 |
| fixed `codex exec` / `shell=False` | true | true | true | required |
| environment state writable | unknown | false | true | operator authority required |
| timeout | 30s | 30s | 30s | 60s, bound |
| transport accepted | false | false | false | unproven |
| timeout observed | unreported | false | true | fail closed |
| stdout present / untruncated | false | false | false | required for capture |
| semantic result captured | false | false | false | unproven |
| Provider / retry / extra process | false | false | false | prohibited |
| validated / accepted / mutated | false | false | false | prohibited |

## Protected-path continuity

Every protected path was hashed before and after each focused, live,
regression, governance, and complete-suite phase. All final hashes equal the
initial hashes:

| Protected path | Initial and final SHA-256 |
|---|---|
| `diagnostic_evidence.json` | `881710ee8c0166769c83ec94e25a67961746a4613ec5206180c945e84b2a3283` |
| `governed_return.json` | `1d73d6d78572de9f689e3e5e1b16b97332af6164cf458c13f5858ca70ed0a0c9` |
| `lineage.json` | `c5f6adff859182c28441fe4ea5fd3b361a94845130863a677eed3d45ccdd3c5e` |
| `provider_stderr.txt` | `0a2a0a25196af82e2dcbe1865d128df82b471515813352dbceaf0425f5be6f9f` |
| `provider_stdout.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `governed_returns.jsonl` | `bfa09ec044db2cfda7df97b236a826d4684e62a839a472202d8e5abda6c09c60` |
| `WORKER_INVOCATION_ARTIFACT_V1` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `WORKER_INVOKED` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `invocation` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The complete suite ran in a disposable repository copy because the main-tree
suite is known to write default runtime evidence. No protected path was
modified, reverted, deleted, staged, or included in the task surface.

## Validation

- focused adapter/G31-17B/G31-18 after timeout repair: 31 passed;
- observability plus focused adapter/G31 after identity correction: 37 passed;
- G31-10 through G31-18 regression: 104 passed;
- Worker lifecycle, invocation, result-capture, and validation regression: 115
  passed;
- governance tests: 5 passed;
- governance engine: `PARTIALLY_CONFORMANT`, 18 passed, two known hook-drift
  findings, zero critical violations, deterministic/fail-closed/read-only;
- targeted `py_compile`: passed;
- `git diff --check`: passed;
- first disposable full-suite audit exposed one duration-identity regression:
  6,414 passed, 5 skipped, 1 failed;
- corrected complete disposable suite: 6,415 passed, 5 skipped in 362.84
  seconds.

## Changed surface and size

Production changes are 82 inserted and 11 removed lines across the existing
owners: 78/10 in five nested `sapianta_system` adapter/observability files and
4/1 in the parent G31 activation binding. Tests add 123 lines across two
existing modules. This 221-line report is the only new file.

- `sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_dispatch.py`;
- `sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_evidence.py`;
- `sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_receipt.py`;
- `sapianta_system/runtime/codex_execution_adapter/governed_codex_execution_replay.py`;
- `sapianta_system/runtime/execution_observability/governed_execution_observability_request.py`;
- `aigol/runtime/codex_worker_activation_binding_runtime.py`;
- `tests/test_governed_codex_execution_adapter.py`;
- `tests/test_g31_17b_governed_execution_to_codex_worker_activation_binding.py`;
- this report.

No AiCLI, G31-18 bridge, canonical result-capture owner, semantic validator,
acceptance owner, or mutation owner changed.

## Remaining gap, estimate, and next state

The 60-second contract has no live receipt yet. A future separately authorized
attempt must use a writable existing CODEX state/configuration, exactly three
human decisions, one process, no retry, and the same disposable grounding. It
must reach `EXECUTION_ACCEPTED` with nonempty untruncated stdout before G31-18
may call the canonical `capture_worker_result` owner.

Evidence-scoped whole-project progress is estimated at **89.6%**. The
conversational governed-development path remains **99.9%** complete as a
planning indicator, not production-readiness or conformance certification.

Recommended next state:
`G31_CODEX_60_SECOND_LIVE_EXECUTION_AND_RESULT_CAPTURE_CONFIRMATION_REQUIRED`.
