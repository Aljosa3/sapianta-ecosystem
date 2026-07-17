# G31-19B CODEX 60-Second Live Execution and Result-Capture Confirmation

## Verdict

`G31_CODEX_LIVE_EXECUTION_AND_RESULT_CAPTURE_OPERATIONAL`

Parent baseline:
`71c03c1d774e12e28027519804aba5f9a8bb89df`

Nested `sapianta_system` baseline:
`31522024b38bc08a60ea2152122bc2b399e1235e`

One disposable live confirmation completed through the existing G31 authority
path. No Provider, retry, fallback, additional process, repository mutation,
semantic validation, acceptance, commit, deployment, or release occurred.

## Retained evidence

Workspace:
`/tmp/g31-60-confirmation-l0j6uv/workspace`

Runtime:
`/tmp/g31-60-confirmation-l0j6uv/runtime/G31-60-CONFIRMATION`

The activation and result-capture Replay families remain present and
reconstruct deterministically.

### Activation Replay

- artifacts: 3;
- Replay hash:
  `sha256:146b55e245e7a7a4d48e06d7d8dd75610a2bdc745f62d0eeae6d0f45fcac9dcb`;
- receipt:
  `CODEX-EXECUTION-RECEIPT-cf7bec9f0d6a1d167506e0c1`;
- review hash:
  `sha256:c64a7a572f0e132e6f92378d38d7416f60b544acdc7e3862e9ddb26693125bc5`;
- approval hash:
  `sha256:cfb7b347eae7b2a83bcdebee25d49184a03d5454723dcbea6b1fb2495958c897`;
- request identity:
  `688fe5e619db459a9ce58824f66fea18752cebbdc96e7b09607387eb7cb0ed94`;
- response identity:
  `5a552c819a1f992c05d02381f7a45e9ee65c579e71d0abc76a9002f1bfdd2ffc`.

### Transport truth

- human decisions: exactly 3;
- process-start count: exactly 1;
- command: fixed `codex exec <bounded_prompt>`;
- outer shell: false;
- approved timeout: 60 seconds;
- status: `EXECUTION_ACCEPTED`;
- return code: 0;
- timed out: false;
- duration: 18.106489 seconds;
- stdout: 2,473 bytes, untruncated;
- stdout SHA-256:
  `a51d1e81b5fef9ec7b44b6cc2206b493a26746c3dedd152c223f38db59c92292`;
- stderr: 4,612 bytes, bounded/truncated transport evidence;
- stderr SHA-256:
  `1fbf8e7238a7fbf017708ca3f576986ef9feaeb545c6b94931cf600f0019ffa1`;
- Provider invoked: false;
- retry/fallback/additional process: false.

No prompt, credential, private environment value, complete stderr, or raw
semantic output is persisted in this report.

### Result-capture Replay

- canonical status: `WORKER_RESULT_CAPTURED`;
- artifacts: 4;
- Replay hash:
  `sha256:970f06d81cf2ab19f790e9cf3d975e59ae5ad4cbdadbe26172b4e5045dfadf0e`;
- Worker-output hash:
  `sha256:7e4797554cad7354fc727b9f8a70b8dc38f4ff48dfdd738ab8f05d5ebebac1a4`;
- Worker-output payload hash:
  `sha256:2c346c62e6639dbe48ee47b86f3e84a5a66e0e4cca7f9c67f6c46139725a7739`;
- captured Worker: `CODEX`, `codex-execution` execution identity,
  `GOAL_FAITHFUL_IMPLEMENTATION_WORKER` role;
- result validated: false;
- result accepted: false;
- repository mutated: false.

The disposable repository snapshot remained
`sha256:5f3b6cd79f01369ea52d483f5bafbea536ecad7ff140ca39b44ffdc159cc193c`.
Its two source hashes remained:

- `aigol/runtime/human_interface.py`:
  `3692fbc6d8f9f76f5afbc65e8c5f46aa4fbae6f36849ba005293ba7b0ad89a75`;
- `tests/test_human_interface.py`:
  `6cb9728c57aa10f995cb6dcb1508c0e8ddb5897a94b4f7895872db47c7a743d4`.

## Validation handoff limitation

The retained activation Replay stores the stdout hash but not the exact stdout
bytes. The canonical result-capture Replay stores the Worker-output and payload
hashes but not the semantic Worker-output artifact body. The exact 2,473 bytes
were available in memory during G31-18 and were authenticated then, but are not
recoverable from either retained Replay family.

Therefore a later semantic-validation transition must not validate this live
capture from hashes alone. No new CODEX process may be started to recreate it.
The next binding may validate in-memory G31-18 captures where the exact bytes
remain available, while reporting this retained live validation as unavailable.

## Protected-state continuity

All nine protected parent paths retained their initial SHA-256 values before
and after live confirmation. They were not modified, restored, deleted,
staged, or included in any commit. The parent and nested source repositories
were not mutated by the live process.
