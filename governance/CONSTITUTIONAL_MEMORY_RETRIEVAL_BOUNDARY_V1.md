# Constitutional Memory Retrieval Boundary V1

Status: retrieval boundary review.

## Recommended Retrieval Trigger

First implementation review should prefer:

```text
operator-triggered retrieval
```

and:

```text
governance-mediated retrieval
```

This preserves explicit intent and avoids hidden memory consultation.

## Trigger Classification

| Trigger | Classification | Rationale |
| --- | --- | --- |
| Manual reading | `RECOMMENDED` | Already safe and current. |
| Operator-triggered | `RECOMMENDED` | Explicit, auditable, bounded. |
| Governance-triggered | `RECOMMENDED_WITH_SCOPE` | Useful for review and validation if replay-visible. |
| Runtime-triggered | `CONDITIONAL` | Acceptable only inside an explicit governance step. |
| Provider-triggered | `OUT_OF_SCOPE` | Risks granting proposal source implicit memory access. |
| Worker-triggered | `OUT_OF_SCOPE` | Risks granting execution participant implicit memory access. |
| Autonomous retrieval | `FORBIDDEN` | Violates reference-only and no hidden continuation expectations. |

## Retrieval Scope Classification

| Memory Layer | Retrieval Classification |
| --- | --- |
| Constitutional invariants | `RETRIEVABLE` |
| Authority invariants | `RETRIEVABLE` |
| Canonical replay language | `RETRIEVABLE` |
| Freeze manifests | `RETRIEVABLE` |
| Baseline guarantees | `RETRIEVABLE` |
| Certifications | `RETRIEVABLE` |
| Acceptance evidence | `RETRIEVABLE` |
| Governance reviews | `RETRIEVABLE` |
| Operational baselines | `RETRIEVABLE` |
| Replay lineage | `CONDITIONAL` |
| `.runtime/` evidence | `CONDITIONAL` |
| Derived summaries | `CONDITIONAL` |
| Hidden runtime state | `OUT_OF_SCOPE` |
| Provider conversation memory | `OUT_OF_SCOPE` |
| Worker memory | `OUT_OF_SCOPE` |

## Conditional Retrieval Rule

Replay lineage, `.runtime/` evidence, and derived summaries may be retrieved only as evidence views and must not supersede canonical sources.

