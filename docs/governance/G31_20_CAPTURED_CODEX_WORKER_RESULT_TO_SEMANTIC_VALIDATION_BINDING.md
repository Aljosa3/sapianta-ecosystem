# G31-20 Captured CODEX Worker Result to Semantic Validation Binding

## Verdict

`G31_SEMANTIC_VALIDATION_IMPLEMENTED_LIVE_EVIDENCE_UNAVAILABLE`

The binding is operational for an in-memory G31-18 capture that still contains
the exact authentic stdout bytes. The retained G31-19B Replay families contain
only hashes, not those bytes, so the live result was not submitted to the
canonical validator. No process was restarted and no validation was fabricated
from hashes alone.

## Canonical owner and contract

The canonical owner remains
`aigol.runtime.worker_result_validation_runtime.validate_worker_result`.
It requires one exact `WORKER_RESULT_CAPTURE_ARTIFACT_V1`, its canonical
four-step capture Replay, validator identity/time, and an unused validation
destination. It returns either:

- `RESULT_VALIDATED` with four existing Replay artifacts; or
- `FAILED_CLOSED` with a truthful failure result.

The reused validation artifact families are:

1. `WORKER_RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1`;
2. `WORKER_RESULT_VALIDATION_CLASSIFICATION_ARTIFACT_V1`;
3. `WORKER_RESULT_VALIDATION_ARTIFACT_V1`;
4. `WORKER_RESULT_VALIDATION_RESULT_ARTIFACT_V1`.

No parallel validator, artifact family, Replay subsystem, authorization
system, approval, or acceptance transition was introduced.

## Binding implementation

The thin Worker-owned entry point is
`validate_captured_codex_worker_result` in
`aigol/runtime/codex_worker_result_to_semantic_validation_binding_runtime.py`.

Before the canonical call it:

- reuses `reconstruct_codex_worker_result_capture_binding`, which reuses the
  complete G31-17B activation and G31-18 capture reconstruction;
- requires the exact in-memory UTF-8 semantic stdout bytes;
- recomputes byte length and SHA-256;
- proves equality with the activation receipt stdout hash, semantic payload,
  Worker-output artifact hash, payload hash, canonical result-capture artifact,
  and capture Replay;
- binds the semantic-output SHA-256 into the canonical validation identity;
- verifies the current repository snapshot through activation reconstruction;
- rejects cross-session destinations, destination reuse, and any prior
  validation attempt for the same capture;
- calls the canonical owner exactly once only after eligibility succeeds.

Stderr and transport diagnostics are never passed as semantic output. Only the
`semantic_output` UTF-8 bytes from the authenticated G31-18 Worker-output
artifact are eligible.

## Complete lineage

The composed reconstruction preserves:

1. contextual request and session;
2. durable repository grounding and current repository snapshot;
3. proposal approval and distinct execution authorization;
4. CODEX Worker selection with `codex-execution`, excluding the cognition
   Provider identity;
5. assignment, dispatch, invocation request, and invocation;
6. G31 execution candidate and governed-execution evidence;
7. third activation review/approval;
8. fixed CODEX request, one process receipt, and three-step activation Replay;
9. exact authentic stdout bytes and receipt stdout hash;
10. semantic Worker-output artifact and its payload hash;
11. canonical four-step `WORKER_RESULT_CAPTURED` Replay;
12. output-hash-bound validation identity and unused destination;
13. canonical result-validation artifact and four-step Replay.

AiCLI performs only orchestration and truthful rendering. Its authority flags
remain:

- `aicli_authorizes = false`;
- `aicli_executes = false`;
- `aicli_owns_replay = false`;
- `aicli_validates = false`;
- `aicli_accepts_result = false`.

No fourth human decision is required because the canonical transition is
deterministic evidence processing.

## Truth table

| Outcome | Captured | Validation performed | Canonical status | Validated | Replay | Accepted/mutated |
|---|---:|---:|---|---:|---:|---:|
| Eligible exact bytes | true | true | `RESULT_VALIDATED` | true | 4 artifacts | false |
| Canonical invalid outcome | true | true | `FAILED_CLOSED` | false | truthful failure evidence | false |
| Missing/substituted bytes | true | false | bridge `FAILED_CLOSED` | false | none | false |
| Receipt/Replay/identity tamper | true | false | bridge `FAILED_CLOSED` | false | none | false |
| Failed/empty/truncated transport | false | false | bridge `FAILED_CLOSED` | false | none | false |
| Reused capture/destination | true | false | bridge `FAILED_CLOSED` | false | none | false |

Every outcome keeps Provider invocation, additional process start, acceptance,
repository mutation, commit, deployment, and release false.

## Retained G31-19B live-result outcome

Both retained Replay families still reconstruct:

- activation: 3 artifacts,
  `sha256:146b55e245e7a7a4d48e06d7d8dd75610a2bdc745f62d0eeae6d0f45fcac9dcb`;
- capture: 4 artifacts, `WORKER_RESULT_CAPTURED`,
  `sha256:970f06d81cf2ab19f790e9cf3d975e59ae5ad4cbdadbe26172b4e5045dfadf0e`;
- Worker-output hash:
  `sha256:7e4797554cad7354fc727b9f8a70b8dc38f4ff48dfdd738ab8f05d5ebebac1a4`.

However, neither retained Replay stores the exact 2,473 stdout bytes. The
activation Replay retains `stdout_hash`; the capture Replay retains the payload
and Worker-output hashes. Hashes cannot reconstruct bytes and are insufficient
under the explicit validation rule.

Retained live validation therefore records:

- validation status: `NOT_PERFORMED_EXACT_BYTES_UNAVAILABLE`;
- validation artifact identity: none;
- validation Replay artifact count/hash: none;
- canonical validation call count: 0;
- response semantic-contract satisfaction: unproven, not misreported valid or
  invalid;
- new `codex exec` process count: 0.

The retained runtime contains no `CODEX-WORKER-RESULT-VALIDATION-*`
destination. No new process was started to recreate output.

## Fail-closed coverage

Focused tests cover:

- valid captured CODEX output and exactly one canonical call;
- canonical invalid outcome without false success;
- missing exact output bytes;
- stdout and Worker-output hash substitution;
- receipt and capture-Replay tampering;
- cross-session destination;
- duplicate destination and repeated capture use;
- Provider-role substitution and changed candidate;
- repository drift;
- failed, empty, and truncated transports;
- no additional Worker process;
- separation from acceptance and mutation;
- AiCLI valid and invalid rendering with three decisions.

## Validation results

- focused G31-20 module: 14 passed;
- Worker activation/capture/validation group: 71 passed;
- G31-10 through G31-20: 118 passed;
- governance tests: 5 passed;
- governance engine: `PARTIALLY_CONFORMANT`, 18 passed, two known hook-drift
  findings, zero critical violations, deterministic/fail-closed/read-only;
- targeted `py_compile`: passed;
- parent and nested `git diff --check`: passed;
- complete disposable suite: 6,429 passed, 5 skipped in 422.44 seconds.

## Protected-state continuity

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

All hashes matched before and after every phase. The complete suite ran from a
disposable copy to avoid known default-runtime writes.

## Size, progress, and next state

Production additions are 337 physical lines: a 317-line binding and 20 AiCLI
lines. This is below 400 and approximately 24% smaller than G31-18's 445-line
production surface. The new bridge itself is slightly smaller than the
G31-18 bridge while adding exact-byte and validation reconstruction.

Evidence-scoped whole-project progress is estimated at **90.0%**. The
conversational governed-development path is **99.95%** complete as a planning
indicator, not production-readiness or conformance certification.

Recommended next state:
`G31_SEMANTIC_WORKER_OUTPUT_DURABLE_BYTE_RETENTION_AUDIT_REQUIRED`.
