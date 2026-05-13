# Governance Worktree Hygiene v1

This package establishes deterministic governance worktree hygiene for replay-safe AGOL development.

Governance lineage is canonical system memory. Transient runtime artifacts are execution residue. Execution residue must not become canonical governance evidence.

## Artifact Classes

- `CANONICAL_GOVERNANCE_ARTIFACT`: ADRs, governance manifests, replay evidence, deterministic evidence, policy evidence, and architecture evidence.
- `TRANSIENT_RUNTIME_ARTIFACT`: `__pycache__`, `*.pyc`, `*.pyo`, runtime temp files, generated runtime noise, transient logs, and replay cache noise.
- `UNKNOWN_ARTIFACT`: anything uncertain. Unknown artifacts fail closed and require explicit classification.

## Replay Pollution Risks

Compiled caches, runtime logs, generated execution outputs, and temporary files can make replay lineage non-minimal, non-reproducible, and harder to certify. They are not governance evidence.

## Gitignore Hygiene

The root `.gitignore` must include:

```text
__pycache__/
*.pyc
.pytest_cache/
*.pyo
```

These rules prevent future untracked cache artifacts from entering canonical lineage. They do not rewrite history or remove already tracked files.

## Fail-Closed Enforcement

The worktree validator does not delete files, rewrite history, mutate tags, or clean the repo automatically. It classifies artifacts and blocks transient or unknown candidates from governance lineage until reviewed.

## Relationship To Replay Integrity

Replay-safe governance infrastructure requires deterministic artifact hygiene. This layer preserves canonical lineage integrity without changing protocol, transport, reflection, approval, policy, stabilization, or architecture semantics.
