# G35-12 Canonical Condensation G31 Input-Binding Certification Evidence

Status: STANDALONE BINDING CERTIFIED — G31 INTEGRATION NOT CERTIFIED
Version: 1.0.0
Date: 2026-07-28
Scope: approved condensation to future G31 preflight eligibility only

## Evidence Claim

The G35-12 runtime:

- consumes only a completely reconstructable G35-11 Replay chain;
- requires deterministic validation PASS and exact explicit APPROVE;
- rejects rejection, ambiguity, missing authority, and cross-chain reuse;
- reconstructs exact Model D fields without transformation;
- binds UTF-8 bytes, Unicode-code-point counts, content hashes, artifact
  versions, and Replay identities;
- emits a stable immutable preflight input tuple;
- writes no Replay and creates no second Replay authority;
- does not import or invoke G31 or any execution subsystem;
- creates no execution authorization; and
- remains dormant and unregistered.

## Evidence Surface

| Artifact | SHA-256 |
| --- | --- |
| Dedicated G31 input-binding runtime | `ffd9f8508120596ee96df058c79cd0f8e11050006077a1b7956f8e1e52518009` |
| Deterministic G35-12 test suite | `4dcc9d7d9ea022309e015d4568c7e99ce04134d3cf054b3a38801623f30d26b3` |

Governance report:

- `docs/governance/G35_12_CANONICAL_CONDENSATION_DEDICATED_G31_INPUT_BINDING_RUNTIME.md`

## Verification Results

| Verification | Result |
| --- | --- |
| Dedicated deterministic binding suite | 35 passed in 1.65s |
| Complete G35-10/G35-11/G35-12 chain suite | 90 passed in 2.25s |
| Unchanged-boundary compatibility suite | 111 passed in 145.95s |
| Target Python compilation | PASS |
| Diff whitespace/error check | PASS |
| Validation PASS required | YES |
| Exact explicit approval required | YES |
| Rejection can bind | NO |
| Model D exact equality proven | YES |
| Post-approval transformation accepted | NO |
| Preflight input tuple deterministic | YES |
| G31 imported or invoked | NO |
| Existing runtime/schema modified | NO |
| Execution authority created | NO |
| Replay written by binding | NO |
| Capability registered or reachable | NO |

## Model D Evidence

The artifact contains separate semantic fields proving:

```text
approved_projection
    == approved_projection_prefix + approved_synthesis_body

g31_function_argument
    == approved_synthesis_body

g31_final_measured_request
    == approved_projection

authorized_task
    == approved_synthesis_body
```

Every value has a strict UTF-8 content hash, UTF-8 byte count, and Unicode
code-point count. Source, proposal, validation, review, decision, approval, and
Replay commitments are repeated and cross-validated.

## Replay and Authority Evidence

The input-binding runtime invokes only the existing approved condensation
Replay reconstruction. It does not persist or alter Replay. Its artifact means
only `ELIGIBLE_FOR_G31_PREFLIGHT`; `g31_preflight_invoked`,
`g31_preflight_passed`, every execution authority, Worker/Provider activity,
mutation, and registration remain false.

## Known Boundary

This evidence does not certify invocation of G31, input-mode orchestration,
AiCLI or Human Interface integration, CODEX activation, authorization, Worker
execution, or capability registration. Those remain future separately
authorized work.

## Verdict

```text
CANONICAL_CONDENSATION_DEDICATED_G31_INPUT_BINDING_RUNTIME_CERTIFIED
```
