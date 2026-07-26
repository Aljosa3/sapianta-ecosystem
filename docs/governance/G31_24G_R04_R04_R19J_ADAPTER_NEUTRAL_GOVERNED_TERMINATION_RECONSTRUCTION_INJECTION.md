# Generation 31-24G-R04-R04-R19J Adapter-Neutral Governed Termination Reconstruction Injection

Status: completed constitutional implementation.

Date: 2026-07-26

Deterministic verdict:

`G31_ADAPTER_NEUTRAL_GOVERNED_TERMINATION_RECONSTRUCTION_INJECTION_IMPLEMENTED`

Exactly one next state:

`G31_24G_R04_R04_R19K_ADAPTER_NEUTRAL_GOVERNED_TERMINATION_RECONSTRUCTION_OPERATIONAL_READINESS_AUDIT_REQUIRED`

## Certified baseline and scope

G0-G30 and the accepted Generation 31 baseline through R19I are treated as
constitutionally closed. The implementation baseline is commit
`dc419ff54cb399b2a7cedc82bd46639914f84083`, whose subject is
`G31 R19H: implement stable invocation-scoped schema-aware Replay Review reconstruction compatibility`.

R19I identified one blocker:

`G31_R19H_GENERIC_GOVERNED_TERMINATION_HARDWIRES_FILESYSTEM_SPECIFIC_RECONSTRUCTION_ADAPTER`

R19J changes only how the existing Governed Termination owner receives its
Replay Review reconstruction dependency. No Replay artifact, Authorization
format, Worker format, review semantic, termination semantic, or
certification boundary changes.

## Implementation

`governed_termination_runtime` now defines one non-authoritative dependency:

```text
ReplayReviewReconstructor
```

The dependency is accepted as a per-call keyword by:

- Replay Review discovery for termination;
- governed termination creation; and
- governed termination Replay reconstruction.

The same invocation-supplied reconstructor is propagated into duplicate
termination detection and every nested Replay Review lineage check. It is
never stored.

When the dependency is omitted, all public entries default to the unchanged
generic `reconstruct_post_execution_replay_review`. Historical generic
behavior therefore remains the default.

The Governed Termination owner no longer imports the Filesystem Replace
Worker schema-aware resolver. A caller handling certified Filesystem lineage
may supply the stable R19H reconstructor for that invocation. The injected
function supplies authentication only; Governed Termination continues to
own admission, termination classification, termination artifacts, its
four-event Replay, and its fail-closed result.

The call boundary rejects:

- a non-callable dependency;
- dependency exceptions;
- unsupported immutable lineage; and
- a reconstruction result that is not a JSON object.

Existing owner-specific lineage and hash checks then authenticate the
reconstructed Replay Review before any termination event is written.

## Constitutional assessment

| Property | R19J assessment |
| --- | --- |
| Generic default | Unchanged generic Replay Review reconstruction |
| Adapter-specific compatibility | Supplied explicitly per invocation |
| Adapter dependency in generic termination | Removed |
| Mutable global or registry | None |
| Context manager or routing state | None |
| Replay Review ownership | Unchanged |
| Authorization ownership | Unchanged |
| Termination ownership | Unchanged |
| Replay ownership and formats | Unchanged |
| Certification ownership | Unchanged |
| Replay determinism | Preserved by the selected per-call reconstructor and existing hash checks |
| Unsupported lineage | Fails closed |

The repair is adapter-neutral and non-authoritative. Additional certified
Replay Review reconstructors can use the same call boundary without
changing the generic Governed Termination owner.

## Focused and regression evidence

Focused R19J tests prove:

1. the Filesystem schema-aware reconstructor can be supplied independently
   to termination creation and later reconstruction;
2. each call invokes only its supplied reconstructor;
3. unsupported immutable lineage fails closed before termination;
4. an invalid dependency is normalized to a fail-closed result;
5. the generic reconstructor remains the default; and
6. no Filesystem import, registry, context manager, lock, or module-global
   routing state exists in the generic termination module.

Validation before the complete suite:

- focused R19J tests: `4 passed`;
- affected R19E, R19H, Replay Review, Governed Termination, and bridge
  regressions: `81 passed`;
- complete Generation 31 R04 transition group: `284 passed`;
- governance and protected-evidence regressions: `12 passed`;
- targeted `py_compile`: passed;
- parent `git diff --check`: passed; and
- all nested repository `git diff --check` checks: passed.

One preliminary governance command named repository test paths that do not
exist. Pytest collected and executed zero tests in that command. The command
selection was corrected to the canonical governance and protected-evidence
modules, which passed `12` tests.

## Complete repository suite

The complete repository suite was executed exactly once:

```text
6857 passed, 4 skipped in 4480.16s (1:14:40)
```

No failure occurred. No repair or repaired-node validation was required, and
the complete suite was not executed a second time.

## Integrity and mutation boundaries

The implementation does not write Replay Review artifacts, Authorization
artifacts, Worker artifacts, or certification evidence. The only runtime
writes remain the pre-existing Governed Termination owner's four immutable
Replay events after successful lineage authentication.

Final `py_compile` passed for every changed Python module and test. Parent
`git diff --check`, staged `git diff --cached --check`, and all three nested
repository `git diff --check` checks passed. The staging area is empty.

The nested repositories are clean at:

- `sapianta-domain-credit`:
  `8615e1e290471a67e4e764c6ab2138340bc7936f`;
- `sapianta_system`:
  `3183bab71f8f30397c0309dd2e6d846d14a11f66`; and
- `sapianta-domain-trading`:
  `d3038dc4ba36ffbaee9161172b4c852e8e6acbda`.

The protected hashes equal the accepted R19H baseline:

| Protected path | SHA-256 |
| --- | --- |
| `diagnostic_evidence.json` | `21546ed151c165c6364aa914d892c34b117ef1ab664ae09d8e2c2a5327bcc8df` |
| `governed_return.json` | `ee57877ceea7d85bd9e3bb29aca64f3637384a7346a5b6a4c4f922c87cb2bcf7` |
| `lineage.json` | `8c47abb9a7c238c9f527e54dd88aa304edbca03b97ea630a4907b4ef139b3a08` |
| `provider_stderr.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `provider_stdout.txt` | `f2fec907b48e7162211f26bbe94352d40f4f6c4380ab3aa4256d072b7c602f30` |
| `governed_returns.jsonl` | `71b085174a274b870617c21810d9a496421985675ae0945f4b56bd3afe7b1118` |

No protected file or nested repository changed. No file was staged or
committed automatically.
