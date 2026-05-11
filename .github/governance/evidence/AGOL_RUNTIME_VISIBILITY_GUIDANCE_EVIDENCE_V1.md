# AGOL Runtime Visibility Guidance Evidence V1

Status: replay-visible evidence for bounded Product 1 runtime visibility
guidance.

## Artifacts

- `docs/governance/AGOL_RUNTIME_VISIBILITY_GUIDANCE_V1.md`
- `runtime/governance/agol_runtime_visibility_guidance.py`
- `tests/test_agol_runtime_visibility_guidance.py`
- `.github/governance/evidence/AGOL_RUNTIME_VISIBILITY_GUIDANCE_EVIDENCE_V1.md`

## Capability Added

AGOL can now detect likely Product 1 preview visibility divergence when changed
files affect local preview output and uvicorn may be serving already-imported
content without reload.

The helper produces deterministic guidance for:

- restart likelihood;
- affected preview scope;
- runtime visibility explanation;
- recommended user-executed restart commands;
- user confirmation requirement;
- replay continuity hashes.

## Boundary Preservation

The primitive does not:

- start servers;
- stop servers;
- restart processes;
- execute shell commands;
- manage daemon lifecycle;
- mutate runtime behavior;
- mutate deployment state;
- grant orchestration authority.

## Replay Fields

The implementation preserves:

- `primitive_id`;
- `request_hash`;
- `command_hash`;
- `scope_hash`;
- `deterministic_hash`;
- `replay_lineage`.

## Validation

Required validation:

```bash
pytest tests/test_agol_runtime_visibility_guidance.py
python -m py_compile runtime/governance/agol_runtime_visibility_guidance.py
git diff --check
```
