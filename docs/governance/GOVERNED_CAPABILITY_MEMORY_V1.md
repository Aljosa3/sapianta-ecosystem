# Governed Capability Memory V1

Status: canonical bounded capability memory model.

Parent guidance:
- `AGENTS.md`
- `CODEX_TASK_EXECUTION_PROTOCOL_V1.md`
- `LLM_ROLE_AND_BOUNDARY_MODEL_V1.md`
- `STABLE_SUBSTRATE_DECLARATION_V1.md`
- `CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md`

Purpose: formalize governance-approved bounded operational capabilities for Codex-assisted development.

This milestone does not introduce unrestricted agent autonomy, autonomous deployment, daemon orchestration, unrestricted shell execution, self-authorizing runtime mutation, persistent background execution, or production automation.

## Core Principle

The purpose is not maximum autonomy.

The purpose is maximum governed bounded capability.

Capability memory exists to make approved operational affordances explicit, scope-locked, replay-visible, revocable, and escalation-aware.

## Capability Memory Model

Each governed capability must define:

- capability ID
- allowed scope
- forbidden scope
- approval semantics
- replay visibility
- revocation semantics
- escalation conditions
- lifecycle semantics
- lineage references

Capability approvals are governance artifacts. They must not be treated as implicit authority to expand scope.

## First Capability

Capability ID:

`LOCALHOST_PREVIEW_RUNTIME_V1`

Allowed scope:

- temporary localhost preview execution
- uvicorn preview runtime
- host limited to `127.0.0.1`
- port scoped to the approved registry value
- lifecycle limited to `start -> validate -> stop`
- visual validation support
- bounded UX verification

Forbidden scope:

- deployment
- systemd changes
- daemon persistence
- firewall changes
- remote or public binding
- background permanent services
- autonomous runtime orchestration
- production runtime mutation
- unrestricted shell execution
- arbitrary subprocess execution

## Approval Semantics

Approval is scoped to the exact capability definition.

Approval does not imply:

- deployment authority
- production authority
- background service authority
- port expansion authority
- public network exposure
- arbitrary command execution
- persistent runtime orchestration

Approval absence is not approval.

## Replay Visibility

Capability evaluations should produce deterministic, replay-visible evidence:

- stable capability ID
- stable allowed scope
- stable decision status
- stable escalation reason
- deterministic evaluation hash
- visible revocation state

Replay-visible capability memory supports governance lineage without creating autonomous execution authority.

## Revocation Semantics

Capabilities must be revocable.

When revoked:

- all future requests for the capability must be rejected;
- revocation must remain visible in registry state;
- historical approvals must not be rewritten;
- revocation must not mutate past evidence.

Revocation is a governance boundary, not a runtime repair loop.

## Escalation Rules

Renewed approval is required if:

- port changes;
- host changes;
- runtime becomes persistent;
- deployment semantics appear;
- background execution appears;
- mutation scope expands;
- public network exposure appears;
- lifecycle changes;
- runtime engine changes.

The model favors explicit escalation over silent capability expansion.

## Implementation Boundary

Minimal deterministic implementation artifacts:

- `runtime/governance/capability_models.py`
- `runtime/governance/capability_registry.py`

These files do not start servers, execute shell commands, deploy software, create daemons, schedule work, or mutate runtime state. They only define and evaluate bounded capability scope.

## Product 1 Relationship

`LOCALHOST_PREVIEW_RUNTIME_V1` exists to support bounded Product 1 UX verification:

- homepage refinement preview;
- audit UX review;
- replay evidence visibility review;
- enterprise demo visual validation.

It does not create deployment authority.

## Constitutional Position

Governed capability memory is below constitutional governance.

It must preserve:

- constitutional governance;
- replay-safe lineage;
- explicit approval semantics;
- bounded execution discipline;
- revocable trust boundaries;
- Product 1 release discipline.

Capability memory must not become unrestricted autonomous execution.

