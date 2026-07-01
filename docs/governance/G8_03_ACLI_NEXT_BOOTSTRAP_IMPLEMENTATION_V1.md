# G8-03 ACLI Next Bootstrap Implementation V1

Status: ACLI Next bootstrap implemented.

Final verdict: ACLI_NEXT_BOOTSTRAP_IMPLEMENTED

## 1. Implementation Summary

This milestone implements the first ACLI Next runtime bootstrap.

Implemented:

- `aigol/acli_next/` runtime package;
- `aigol next session` legacy CLI shim;
- session bootstrap artifact;
- PGSP invocation artifact;
- completion summary artifact;
- UHCL-compatible terminal rendering through the existing CLI renderer path;
- targeted ACLI Next bootstrap tests.

The implementation remains:

- non-mutating;
- replay-visible;
- fail-closed;
- compatible with legacy ACLI;
- thin over certified Platform Core.

## 2. Files Changed

Runtime files:

- `aigol/acli_next/__init__.py`
- `aigol/acli_next/entrypoint.py`
- `aigol/cli/aigol_cli.py`

Tests:

- `tests/test_g8_acli_next_bootstrap.py`

Governance:

- `docs/governance/G8_03_ACLI_NEXT_BOOTSTRAP_IMPLEMENTATION_V1.md`

## 3. Runtime Structure

The new package is intentionally small:

| Module | Purpose |
| --- | --- |
| `aigol/acli_next/__init__.py` | Exposes the bootstrap runtime API. |
| `aigol/acli_next/entrypoint.py` | Starts ACLI Next session, delegates to existing PGSP lineage, records replay-visible artifacts, renders summary. |

The legacy CLI registers:

```text
aigol next session
```

The CLI shim delegates to `aigol.acli_next.run_acli_next_session(...)`.

## 4. PGSP Integration

ACLI Next bootstrap delegates to the certified live governed session route:

```text
run_g4_live_acli_governed_development_session_entrypoint(...)
```

This preserves:

- PGSP lineage;
- UBTR ownership;
- CSA ownership;
- OCS ownership;
- Governance ownership;
- Replay ownership;
- UHCL communication ownership.

ACLI Next does not duplicate PGSP internals.

## 5. Replay And Session Handling

ACLI Next records three bootstrap artifacts:

1. `000_acli_next_session_created.json`
2. `001_pgsp_invocation_recorded.json`
3. `002_acli_next_completion_recorded.json`

The delegated PGSP/G4 live session writes its own replay evidence under:

```text
<acli_next_replay_dir>/pgsp_session
```

Replay-visible fields include:

- session id;
- turn id;
- operator request hash;
- operator response hash;
- PGSP replay reference;
- PGSP replay hash;
- non-mutation flags;
- completion status.

## 6. Governance Impact

Governance boundaries are preserved.

ACLI Next:

- captures human input;
- invokes PGSP;
- renders advisory summary;
- records replay-visible confirmation state.

ACLI Next does not:

- certify governance;
- approve work;
- authorize execution;
- invoke Workers directly;
- invoke providers directly;
- mutate repositories.

## 7. Replay Impact

Replay boundaries are preserved.

ACLI Next:

- creates bootstrap replay artifacts;
- references PGSP replay evidence;
- fails closed if PGSP replay reference is missing;
- records non-mutation status explicitly.

ACLI Next does not:

- reconstruct replay independently;
- mutate replay history;
- synthesize replay evidence;
- treat documentation-only evidence as runtime evidence.

## 8. Non-Mutation Guarantees

The bootstrap result requires the delegated PGSP result to report:

- `provider_invoked: False`;
- `worker_invoked: False`;
- `approval_created: False`;
- `authorization_created: False`;
- `execution_authorized: False`;
- `repository_mutated: False`;
- `deployment_performed: False`.

If any of these values are not false, ACLI Next fails closed.

## 9. Deferred Functionality

Deferred:

- Git operations;
- repository mutation;
- deployment;
- write-capable Workers;
- autonomous provider selection;
- provider execution outside certified PGSP/EPP paths;
- machine-readable canonical lookup consumption;
- mutating Worker authorization.

## 10. Rollback Impact

Rollback is low-impact.

The implementation is side-by-side:

- removing `aigol/acli_next/` removes the new runtime package;
- removing the `next` CLI parser branch restores legacy CLI behavior;
- existing ACLI commands and replay artifacts remain compatible;
- no Platform Core ownership or runtime semantics are changed.

## 11. Validation Results

Validation commands:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py
```

Validation status: passed.

Validation evidence:

```text
git diff --check
```

Result: clean.

```text
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/cli/aigol_cli.py
```

Result: passed.

```text
python -m pytest tests/test_g8_acli_next_bootstrap.py
```

Result: 3 passed.

## 12. Final Determination

The ACLI Next bootstrap runtime is implemented.

It provides the first non-mutating, replay-visible, PGSP-backed ACLI Next session entrypoint while preserving certified Platform Core authority boundaries.

Final verdict: ACLI_NEXT_BOOTSTRAP_IMPLEMENTED
