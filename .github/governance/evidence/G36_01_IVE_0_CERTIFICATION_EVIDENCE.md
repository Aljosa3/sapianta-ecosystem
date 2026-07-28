# G36-01 IVE-0 Certification Evidence

Status: CERTIFIED

Version: 1.0.0

Date: 2026-07-28

Scope: deterministic constitutional impact classification and validation
recommendation only

## Evidence Claim

G36-01:

- consumes only canonical normalized-change artifacts;
- reuses G27 impact and planning when their certified ingress domain applies;
- uses an additive exact-path component inventory outside that domain;
- fails closed on ambiguous or unsupported component mappings;
- produces deterministic component, classification, recommendation, and
  reasoning hashes;
- records immutable replay-visible evidence;
- requires downstream exact-candidate Human Approval;
- synthesizes no command and expands no validation allowlist;
- executes no validation;
- invokes no Authorization, Worker, Provider, AiCLI, or execution gate; and
- modifies no Replay semantic or execution-spine owner.

## Evidence Surface

| Artifact | SHA-256 |
| --- | --- |
| IVE-0 runtime | `cfd0982759a8b76a39943bb841b7dba8e70b4ac78ff37d6995fbd12f619280d1` |
| IVE-0 deterministic suite | `ce93079f5a1305f8da39778a920fcdfd80ef7b177e0474ec0264c9b98186a8ee` |
| IVE-0 architecture and integration report | `bc82c0094f30eb1c0b1cd776a5fd90b55f6682d03f1f4620c9407685ca3df3c3` |
| IVE-0 Governance report | `6efa0f1fca8e9606bac93f2ef974006cf943206f3934ca934602a9a114876a77` |

## Verification Results

| Verification | Result |
| --- | --- |
| Complete IVE-0 suite | 9 passed in 0.14s |
| Focused constitutional compatibility suite | 72 passed in 1.48s |
| Changed Python compilation | PASS |
| Diff whitespace/error check | PASS |
| Governance conformance engine | PARTIALLY_CONFORMANT; 18 passed; 2 failed; 0 critical violations |
| Deterministic identical-input plan hash | PASS |
| Exact component-type coverage | PASS |
| Replay reconstruction and lineage | PASS |
| Tamper detection | PASS |
| Invalid-source fail-closed behavior | PASS |
| Human Approval requirement | PASS |
| Validation executed by IVE-0 | NO |
| Authorization invoked by IVE-0 | NO |
| Worker or Provider invoked by IVE-0 | NO |
| Repository mutation authorized | NO |

## Runtime Evidence Family

Each IVE-0 invocation writes:

```text
000_intelligent_validation_plan_recorded.json
```

Eligible G27 composition additionally writes and hash-binds:

```text
impact/000_platform_change_impact_recorded.json
validation_plan/000_platform_validation_plan_recorded.json
```

The IVE artifact binds normalized source, G27 lineage when applicable, affected
components, overall classification, validation recommendation, Human Approval
requirement, constitutional reasoning, authority flags, and deterministic
hashes.

## Known Baseline Condition

The Governance conformance engine continues to expose the known repository hook
drift: the root hook is absent and the nested-system hook lacks two governance
tokens. There are zero critical violations. G36-01 neither changes nor hides
this pre-existing partial-conformance state.

The repository-wide pytest suite was not executed. Certification is explicitly
bounded to the complete new suite and the affected compatibility surfaces.

## Verdict

```text
IVE_0_CONSTITUTIONALLY_CERTIFIED
```
