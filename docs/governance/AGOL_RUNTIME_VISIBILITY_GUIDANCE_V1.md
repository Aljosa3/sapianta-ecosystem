# AGOL Runtime Visibility Guidance V1

Status: bounded Product 1 workflow assistance primitive.

AGOL Runtime Visibility Guidance V1 helps detect likely runtime/source divergence
during local Product 1 refinement work. It exists because visible preview files
can be changed correctly while a localhost uvicorn preview continues serving
already-imported in-memory content.

## Purpose

The primitive prepares deterministic, replay-visible restart guidance when
modified files likely affect Product 1 preview output.

It may produce:

- `restart_required_likelihood`;
- `affected_preview_scope`;
- `runtime_visibility_explanation`;
- `recommended_restart_commands`;
- `user_confirmation_required`;
- replay continuity hashes.

## Boundary

This primitive is guidance only.

AGOL may:

- classify modified files that likely affect visible preview output;
- explain why restart may be required;
- prepare bounded restart guidance;
- suggest user-executed restart commands;
- preserve deterministic replay evidence.

AGOL must not:

- restart processes;
- execute shell commands;
- manage daemons;
- own server lifecycle;
- mutate deployment state;
- gain orchestration authority;
- gain runtime control authority.

## Replay Continuity

The primitive preserves:

- `primitive_id`;
- `request_hash`;
- `command_hash`;
- `scope_hash`;
- `deterministic_hash`;
- `replay_lineage`.

Equivalent requests must produce equivalent deterministic guidance outputs.

## User Authority

Restart guidance always requires user confirmation. Suggested commands are
prepared as workflow assistance only and do not authorize AGOL to run them.
