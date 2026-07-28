# G35-12 Canonical Condensation Dedicated G31 Input-Binding Runtime

Status: IMPLEMENTED — STANDALONE AND DORMANT
Version: 1.0.0
Date: 2026-07-28
Authority: Approved condensation to future G31 preflight eligibility boundary
Dependencies: G35-05, G35-08, G35-09, G35-10, G35-11
Scope: deterministic input binding only

## 1. Result

Generation 35-12 implements the dedicated, read-only boundary between an
explicitly approved Canonical Condensation Replay chain and a future invocation
of the unchanged G31 preflight:

```text
approved five-event condensation Replay
                   |
                   v
deterministic reconstruction and exact validation
                   |
                   v
immutable G31 input-binding result
                   |
                   v
future unchanged G31 preflight (not invoked here)
```

The runtime remains dormant and unregistered. It imports no G31 preflight,
AiCLI, Human Interface entry, generic CODEX, Authorization, Worker, Provider,
execution-gate, handoff, task-outcome, or capability-registry runtime.

## 2. Runtime Surface

Created:

- `aigol/runtime/canonical_governed_development_condensation_g31_input_binding_runtime.py`;
- `tests/test_g35_12_canonical_condensation_g31_input_binding_runtime.py`;
- this governance report; and
- G35-12 certification evidence.

Modified:

- no existing runtime module;
- no existing test;
- no G31 preflight or activation module;
- no entry point;
- no generic schema;
- no Replay implementation;
- no capability registry; and
- no configuration.

## 3. Required Approved Input Chain

The runtime accepts one input: the immutable G35-11 five-event Replay
directory. It reconstructs through the existing condensation Replay reader:

1. original source lineage;
2. canonical condensation proposal;
3. deterministic validation;
4. exact human-review presentation; and
5. explicit human decision.

Binding requires all of the following:

- complete and correctly ordered Replay;
- valid wrapper and artifact hashes;
- supported artifact, schema, validator, and Replay versions;
- deterministic validation status `PASS`;
- exact decision `APPROVE`;
- `explicit_human_action: true`;
- semantic-representation approval;
- an immutable approved-projection artifact; and
- exact equality across source, proposal, validation, review, decision,
  approved projection, and Replay commitments.

A Phase 1-only chain, missing review, missing decision, malformed decision,
explicit rejection, incomplete reconstruction, or substituted chain raises a
fail-closed error and returns no partial binding.

## 4. Canonical Binding Artifact

The content-addressed artifact is:

```text
CANONICAL_CONDENSATION_G31_INPUT_BINDING_V1
```

with schema:

```text
CANONICAL_CONDENSATION_G31_INPUT_BINDING_SCHEMA_V1
schema_version: 1.0.0
runtime_version: 1.0.0
binding_model: MODEL_D
binding_status: ELIGIBLE_FOR_G31_PREFLIGHT
```

`binding_hash` is the canonical JSON Replay hash of the complete artifact
excluding `binding_id` and `binding_hash`. `binding_id` is derived from that
hash. No timestamp, mutable registry lookup, or execution result participates
in the identity.

The binding meaning is strictly:

```text
This exact approved condensation is eligible to be presented
to the unchanged G31 preflight.
```

Eligibility is not a preflight PASS or execution authorization.

## 5. Exact Model D Reconstruction

The runtime reconstructs the G35-09 Model D fields independently:

| Semantic role | Exact value |
| --- | --- |
| `original_source_request` | Immutable original human request |
| `approved_projection_prefix` | Exact approved `runtime validation: ` prefix |
| `approved_synthesis_body` | Exact approved unprefixed body `B` |
| `approved_projection` | Exact approved `P + B` |
| `g31_function_argument` | Exact `B` |
| `g31_final_measured_request` | Exact `P + B` |
| `authorized_task` | Exact `B` |

The fields remain distinct even where their string values are byte-identical.
The binding requires:

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

The complete measured request must remain within the unchanged 240
Unicode-code-point limit. This check does not invoke or replace G31 preflight.

## 6. Exactness and Commitment Model

Each source, prefix, body, projection, G31 argument, measured request, and
authorized-task role carries:

- exact string value;
- strict UTF-8 SHA-256 commitment;
- UTF-8 byte count;
- Python Unicode-code-point count;
- `UTF-8_STRICT` encoding contract; and
- `PYTHON_UNICODE_CODE_POINTS` counting contract.

The runtime performs no `strip()`, case conversion, newline rewriting,
whitespace rewriting, Unicode normalization, fallback encoding, truncation, or
semantic reconstruction.

The binding also repeats and verifies:

- original request and source-bundle hashes;
- proposal hash;
- validation hash;
- review hash;
- human-decision hash;
- approved-projection artifact hash;
- prefix, body, and complete-projection hashes;
- Phase 1 Replay family hash;
- approved-chain Replay extension hash;
- extension-record hashes; and
- every applicable artifact/schema/runtime version.

Re-hashing a modified outer binding cannot legitimize changed content because
validation reconstructs the expected artifact independently from immutable
Replay and requires complete equality.

## 7. Early and Activation Preflight Tuple

The binding exposes:

```text
CANONICAL_CONDENSATION_G31_PREFLIGHT_INPUT_TUPLE_V1
```

The tuple contains only the constitutionally compared input values and their
commitments:

- exact future `g31_function_argument`;
- exact future `g31_final_measured_request`;
- strict UTF-8 hashes and byte counts;
- Unicode-code-point counts;
- encoding and counting contracts; and
- binding schema ID/version.

`preflight_input_tuple_hash` commits to this exact object. Future early and
activation checks can compare this tuple without requiring unrelated complete
runtime captures to be equal.

## 8. Replay Ownership

The binding runtime is a Replay consumer only:

- it invokes the existing G35-11 reconstruction function;
- it writes no Replay record;
- it changes no Replay history;
- it creates no alternate Replay format; and
- the same approved Replay reconstructs the same binding and tuple.

`replay_written` is always false. Replay family and extension hashes remain
inputs to the binding identity.

## 9. Fail-Closed Behavior

The runtime returns no binding for:

- missing source, proposal, validation, review, decision, or approval;
- validation other than PASS;
- rejection or malformed/ambiguous decision;
- a conflicting extra decision event;
- missing, reordered, corrupt, incomplete, or unsupported Replay events;
- unsupported artifact, schema, validator, or runtime version;
- source, proposal, validation, review, decision, approval, or Replay
  commitment mismatch;
- approval reused for another source, proposal, review, or Replay chain;
- prefix, body, projection, or concatenation mismatch;
- leading/trailing whitespace or newline changes;
- `strip()`-equivalent substitution;
- Unicode normalization changes;
- UTF-8 byte, code-point, or hash mismatch;
- G31 argument, measured-request, or authorized-task role drift;
- changed preflight tuple; or
- a changed authority boundary.

All failures occur before G31, CODEX, Authorization, Worker, Provider,
execution-gate, handoff, deployment, task-outcome, or mutation activity.

## 10. Authority Boundary

The artifact truth flags state:

```text
g31_input_binding_created: true
eligible_for_g31_preflight: true
g31_preflight_invoked: false
g31_preflight_passed: false
codex_synthesis_authorized: false
authorization_created: false
execution_authorized: false
worker_invoked: false
provider_invoked: false
repository_mutated: false
capability_registered: false
replay_written: false
```

The required `authorized_task` field names the exact future G31 semantic task
value. It is not an execution-authorization artifact and grants no current
authority.

## 11. Validation Evidence

Dedicated G35-12 suite:

```text
python -m pytest -q \
  tests/test_g35_12_canonical_condensation_g31_input_binding_runtime.py

35 passed in 1.65s
```

Complete condensation chain:

```text
python -m pytest -q \
  tests/test_g35_10_canonical_condensation_runtime_phase1.py \
  tests/test_g35_11_canonical_condensation_human_review_and_decision_runtime.py \
  tests/test_g35_12_canonical_condensation_g31_input_binding_runtime.py

90 passed in 2.25s
```

Scoped unchanged-boundary compatibility:

```text
111 passed in 145.95s
```

That suite covered existing G31 preflight, activation, transport, CODEX prompt
fidelity, common Human Interface entry, constitutional Replay, governance
conformance, execution authorization, Worker runtime, Provider runtime, and
execution-gate binding/validation.

Target Python compilation and `git diff --check` passed. This is scoped
compatibility evidence, not a complete repository regression.

## 12. Remaining Boundary

This generation does not:

- invoke G31;
- connect the binding to G31;
- modify G31 preflight or activation;
- select direct versus condensation input mode;
- add Human Interface or AiCLI orchestration;
- create CODEX or execution authorization;
- alter downstream schemas;
- register the capability; or
- perform execution.

A future separately authorized integration must consume exactly
`g31_function_argument`, compare the certified preflight tuple, and preserve
all unchanged G31 behavior.

## 13. Verdict

```text
CANONICAL_CONDENSATION_DEDICATED_G31_INPUT_BINDING_RUNTIME_CERTIFIED
```

This verdict certifies only the standalone dedicated binding. It grants no
integration, registration, preflight PASS, authorization, execution, or
mutation authority.
