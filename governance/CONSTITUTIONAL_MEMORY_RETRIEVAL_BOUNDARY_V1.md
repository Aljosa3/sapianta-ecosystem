# Constitutional Memory Retrieval Boundary V1

Status: retrieval trigger and scope boundary.

## Retrieval Trigger Model

| Requesting Entity | Classification | Evidence |
| --- | --- | --- |
| Human | `ALLOWED` | Human authority may request review or explanation, but retrieval remains reference-only. |
| Operator | `ALLOWED` | Operator-triggered retrieval is the recommended first runtime access shape. |
| AiGOL Governance | `ALLOWED` | Governance may consult memory as reference evidence for review. |
| Runtime validation step | `CONDITIONAL` | Allowed only inside explicit governance-mediated validation and replay-visible consultation. |
| Provider | `FORBIDDEN` | Provider is proposal source only; provider-triggered memory access risks implicit authority. |
| Worker | `FORBIDDEN` | Worker executes only authorized requests; worker-triggered memory access risks execution-role expansion. |
| Autonomous background process | `FORBIDDEN` | Hidden retrieval violates replay visibility and reference-only constraints. |

## Retrieval Scope Model

| Memory Scope | Classification | Evidence |
| --- | --- | --- |
| Constitutional invariants | `RETRIEVABLE` | Core constitutional source. |
| Authority invariants | `RETRIEVABLE` | Required for preserving authority separation. |
| Freeze manifests | `RETRIEVABLE` | Canonical baseline memory. |
| Baseline guarantees | `RETRIEVABLE` | Canonical preservation targets. |
| Certifications | `RETRIEVABLE` | Supporting validation evidence. |
| Acceptance evidence | `RETRIEVABLE` | Supporting milestone evidence. |
| Governance reviews | `RETRIEVABLE` | Reconstruction and readiness evidence. |
| Operational baselines | `RETRIEVABLE` | Frozen operational reference. |
| Replay lineage | `CONDITIONAL` | May be retrieved as evidence view, not canonical override. |
| `.runtime/` evidence | `CONDITIONAL` | May be retrieved only as operational evidence. |
| Derived summaries | `CONDITIONAL` | May support operator understanding, not authority. |
| Hidden runtime state | `OUT_OF_SCOPE` | Not Constitutional Memory. |
| Provider memory | `OUT_OF_SCOPE` | Provider remains proposal source only. |
| Worker memory | `OUT_OF_SCOPE` | Worker remains execution-only. |

## Boundary Rule

Retrieval is admissible only when the request, scope, and output all remain replay-visible and reference-only.

