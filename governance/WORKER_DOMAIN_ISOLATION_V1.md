# WORKER_DOMAIN_ISOLATION_V1

## Status

Certified worker domain isolation model.

## Isolation Principle

Workers remain isolated from providers.

Workers never trust proposals.

Workers only receive governed requests.

Workers never receive raw provider authority.

Workers never receive raw cognition authority.

## Domain Review

| Worker Domain | Isolation Rule |
| --- | --- |
| Filesystem Worker | Must receive authorized bounded file capability only; raw provider text cannot request file action. |
| API Worker | Must receive authorized bounded API capability only; raw provider text cannot call endpoint. |
| Database Worker | Must receive authorized bounded query capability only; raw provider text cannot query or mutate database. |
| Local Tool Worker | Must receive authorized bounded tool invocation only; raw provider text cannot invoke tool. |
| Remote Tool Worker | Must receive authorized bounded remote invocation only; raw provider text cannot call remote system. |
| Future Domain Worker | Must receive domain-reviewed authorized capability only; raw provider text cannot establish domain authority. |

## Isolation Guarantees

Worker isolation requires:

- explicit worker identity
- capability binding
- authorization evidence
- replay lineage
- fail-closed validation
- termination evidence

## Certification

Worker domain isolation is compatible with provider proposals only if
governance and authorization remain between provider and worker.
