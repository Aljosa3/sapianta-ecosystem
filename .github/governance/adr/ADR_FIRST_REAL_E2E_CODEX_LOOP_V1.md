# ADR: FIRST_REAL_E2E_CODEX_LOOP_V1

## Status

Accepted.

## Context

SAPIANTA / AiGOL now has ChatGPT ingress, NL-to-envelope transformation, provider connector artifacts, execution gate authorization, bounded Codex execution, and result return. The next proof is a single governed end-to-end loop that carries one request through those layers without manual internal transfer.

## Decision

Introduce `sapianta_bridge/real_e2e_codex_loop/` as the first real bounded operational Codex E2E loop.

The loop requires explicit human authorization, provider identity `codex_cli`, bounded workspace, bounded timeout, deterministic lineage, and the existing bounded Codex runtime. It permits only `codex run <prepared_task_artifact>`.

## Boundaries

This is not autonomous AI, orchestration, routing, scheduling, fallback, retry, adaptive planning, memory mutation, background work, or unrestricted runtime authority.

## Consequences

Codex output is captured as governed execution evidence, returned through the result return loop, and exposed as a ChatGPT-facing response payload. Any future expansion must preserve these deterministic fail-closed boundaries.
