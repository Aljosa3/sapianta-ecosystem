# G8-05 ACLI Next Read-Only Worker Handoff V1

Status: ACLI Next read-only Worker handoff implemented.

Final verdict: ACLI_NEXT_READONLY_WORKER_HANDOFF_IMPLEMENTED

## 1. Executive Summary

G8-05 extends the G8-04 ACLI Next interactive session runtime with a certified read-only Worker handoff after explicit human confirmation.

The implementation supports:

- deterministic Worker capability lookup;
- governance authorization check for confirmed advisory sessions;
- replay-visible Worker request artifacts;
- replay-visible Worker result artifacts;
- structured completion summaries;
- fail-closed behavior when confirmation, authority, capability, or replay evidence is missing.

The handoff remains bounded to read-only summaries over existing ACLI Next interactive replay metadata. It does not introduce repository mutation, Git operations, deployment, write-capable Workers, provider calls, autonomous Worker selection, or a new orchestration layer.

## 2. Implemented Runtime Surface

Files added:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/readonly_worker.py` | Read-only Worker handoff runtime over completed ACLI Next interactive sessions. |
| `tests/test_g8_acli_next_readonly_worker_handoff.py` | Targeted tests for confirmed handoff, missing confirmation, unsupported capability, and CLI routing. |
| `docs/governance/G8_05_ACLI_NEXT_READONLY_WORKER_HANDOFF_V1.md` | Governance implementation record. |

Files updated:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/__init__.py` | Exposes G8-05 read-only Worker handoff APIs. |
| `aigol/cli/aigol_cli.py` | Adds `aigol next readonly-worker` and renders handoff summaries. |

## 3. Runtime Entry Point

The new CLI route is:

```text
aigol next readonly-worker
```

The command reuses the G8-04 interactive turn model:

```text
--turn "human request=>human response"
```

After the interactive session completes, ACLI Next performs the read-only Worker handoff only when:

- the interactive session completed successfully;
- the final canonical response class is `CONFIRMATION`;
- interactive replay evidence exists;
- the requested Worker capability is allowlisted;
- the handoff remains read-only;
- no provider, mutation, deployment, approval, or execution authorization is created.

## 4. Supported Read-Only Capabilities

G8-05 defines a deterministic allowlist:

| Capability | Worker ID | Scope |
| --- | --- | --- |
| `replay_inspection` | `ACLI_NEXT_REPLAY_INSPECTION_WORKER` | Summarizes ACLI Next replay references and turn continuity. |
| `validation_summary` | `ACLI_NEXT_VALIDATION_SUMMARY_WORKER` | Summarizes validation evidence already present in ACLI Next replay metadata. |
| `canonical_mapping_lookup` | `ACLI_NEXT_CANONICAL_MAPPING_LOOKUP_WORKER` | Summarizes canonical response-class mappings in the interactive turn history. |

Unsupported capabilities fail closed before a Worker request artifact is produced.

## 5. Governance Authorization Check

The governance check is documentation-backed and runtime-visible. It does not create execution authorization.

Authorization requires:

| Check | Required State |
| --- | --- |
| Interactive session status | `ACLI_NEXT_INTERACTIVE_COMPLETED` |
| Final response class | `CONFIRMATION` |
| Replay evidence | `replay_reference` and `replay_hash` present |
| Provider invocation | `False` |
| Prior Worker invocation | `False` |
| Approval creation | `False` |
| Authorization creation | `False` |
| Execution authorization | `False` |
| Repository mutation | `False` |
| Deployment | `False` |

The authorization artifact status is:

```text
AUTHORIZED_READONLY_WORKER
```

This status authorizes only the bounded read-only summary handoff. It does not authorize mutation, execution, dispatch, deployment, or provider use.

## 6. Replay Integration

G8-05 records:

| Artifact | Purpose |
| --- | --- |
| `000_acli_next_readonly_worker_request.json` | Captures Worker capability, governance authorization hash, and interactive replay reference. |
| `001_acli_next_readonly_worker_result.json` | Captures read-only Worker result summary and non-mutation flags. |
| `002_acli_next_readonly_worker_completion.json` | Captures final handoff summary, result hash, replay reference, and authority flags. |

The handoff references the G8-04 interactive replay directory and hash. It does not reconstruct or mutate Replay.

## 7. Authority Analysis

G8-05 preserves Platform Core boundaries:

| Authority | Preservation |
| --- | --- |
| PGSP | Interactive session still routes through G8-04 and G8-03 PGSP delegation. |
| UBTR | Not duplicated; semantic translation remains behind PGSP. |
| OCS | Not duplicated; proposal and orchestration remain behind PGSP. |
| Governance | Provides the authorization boundary; ACLI Next only records the check. |
| Replay | Remains evidence reconstruction authority; G8-05 records append-only artifacts. |
| Worker Platform | Read-only Worker handoff is bounded and explicit; no write-capable Worker path is introduced. |
| EPP | Not invoked. |
| ACLI Next | Captures, checks, delegates to read-only summary, records, and renders. |

## 8. Fail-Closed Behavior

The handoff fails closed when:

- the interactive session is incomplete;
- human confirmation is missing;
- replay evidence is missing;
- the requested Worker capability is unsupported;
- prior provider invocation is detected;
- prior Worker invocation is detected before handoff;
- approval or execution authorization is present;
- repository mutation or deployment is present;
- the Worker result is not read-only or replay-visible.

## 9. Deferred Functionality

Deferred beyond G8-05:

- write-capable Workers;
- repository status via Git command execution;
- Git commits;
- patch application;
- deployment;
- autonomous Worker selection;
- autonomous provider selection;
- long-running Worker authorization reuse.

These require separate certification before adoption.

## 10. Validation Strategy

Required validation:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/acli_next/readonly_worker.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py
```

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/acli_next/readonly_worker.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py
```

Validation result: clean. Targeted pytest result: 10 passed.

## 11. Completion Criteria

Completion criteria:

| Criterion | Status |
| --- | --- |
| Read-only Worker handoff exists. | Complete |
| Handoff reuses G8-04 interactive runtime. | Complete |
| Worker capability lookup is deterministic. | Complete |
| Governance authorization check is enforced. | Complete |
| Worker request is replay-visible. | Complete |
| Worker result is replay-visible. | Complete |
| Missing confirmation fails closed. | Complete |
| Unsupported capability fails closed. | Complete |
| No repository mutation occurs. | Complete |
| No Git operation is introduced. | Complete |
| No provider invocation is introduced. | Complete |
| No write-capable Worker is introduced. | Complete |

## 12. Final Determination

G8-05 implements the ACLI Next read-only Worker handoff milestone.

The implementation allows a confirmed interactive advisory session to request bounded read-only Worker summaries while preserving governance, replay, and non-mutation boundaries.

Final verdict: ACLI_NEXT_READONLY_WORKER_HANDOFF_IMPLEMENTED
