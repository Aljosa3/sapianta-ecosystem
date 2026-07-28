# G35-13 Canonical Governed Development Condensation Entry Integration

Status: IMPLEMENTED — CERTIFICATION CANDIDATE  
Version: 1.0.0  
Date: 2026-07-28  
Authority: Common Human Interface runtime-entry sequencing  
Dependencies: G35-05, G35-08, G35-09, G35-10, G35-11, G35-12  
Scope: request-entry integration through unchanged G31 preflight only

## 1. Result

Generation 35-13 connects the certified Canonical Condensation stack to the
existing common Human Interface runtime entry:

```text
exact source request
        |
        +-- final length <= 240 --> historical G31 preflight branch
        |
        `-- final length > 240
                   |
                   v
        selected proposal inputs
                   |
                   v
        proposal -> deterministic validation -> Phase 1 Replay
                   |
                   v
        exact human review -> explicit APPROVE or REJECT
                   |
                   v
        Phase 2 Replay -> dedicated Model D input binding
                   |
                   v
        unchanged G31 preflight(B)
```

The integration terminates after the early G31 preflight. It does not activate
a Worker, invoke a Provider, create execution authorization, reach an execution
gate, or mutate the repository.

## 2. Change Surface

Modified runtime:

- `aigol/runtime/human_interface_runtime_entry_service.py`

Added:

- `tests/test_g35_13_canonical_condensation_entry_integration.py`;
- this governance report; and
- G35-13 certification evidence.

Not modified:

- `aigol/runtime/codex_worker_activation_binding_runtime.py`;
- any G31 decision, activation, handoff, result, or task-outcome owner;
- AiCLI transport;
- Authorization;
- Worker or Provider contracts;
- execution-gate contracts;
- condensation proposal, validation, review, decision, Replay, or dedicated
  input-binding runtimes;
- Replay constitutional invariants; and
- capability registry or configuration.

This is the minimum entry-owner change authorized by the certified ownership
model. It creates no tenth owner.

## 3. Deterministic Mode Selection

The common entry uses the existing G31 constants:

```text
P = "runtime validation: "
M = 240 Unicode code points
```

It evaluates:

```text
len(P + exact_entry_prompt) > M
```

No alternate bound, tokenizer, byte count, configuration lookup, or inferred
meaning participates in mode selection.

For a request within the bound:

- proposal inputs are prohibited;
- the historical preflight call and response branch remain in use; and
- no condensation field is added.

For an over-bound request without selected proposal inputs:

- the historical preflight still fails closed for compatibility;
- the entry result explicitly reports that condensation is required; and
- no proposal, approval, binding, Worker, Provider, authorization, or mutation
  occurs.

For an over-bound request with selected proposal inputs:

- the condensation path is selected;
- there is no direct-mode fallback after selection; and
- every later failure is terminal for that transition.

## 4. Proposal Input Boundary

The entry accepts one typed `canonical_condensation_proposal_inputs` object.
Its field set is closed. The exact original request, workspace, and session are
not accepted from that object; they are bound by the common entry itself.

The caller supplies the already selected:

- original request identity;
- clarification evidence and completion truth;
- completed objective identity and text;
- project, invocation, and chain identities;
- semantic commitments;
- material source requirements;
- exact requirement mappings;
- proposed bounded synthesis body;
- unresolved ambiguity list; and
- optional certified proposal-method evidence.

The common entry does not infer, summarize, repair, truncate, normalize, or
approve these values. The G35-10 proposal owner constructs the immutable
artifact, and the G35-10 deterministic validator evaluates it against the
entry-bound source, workspace, session, and objective hashes.

## 5. Replay Lifecycle

Before human review, common entry records the existing three-event Phase 1
family:

1. source lineage;
2. canonical proposal; and
3. deterministic validation.

A validation result other than `PASS` returns
`CANONICAL_CONDENSATION_VALIDATION_FAILED_CLOSED` with no pending human
decision and no G31 call.

After PASS, common entry creates the exact G35-11 review and exposes the
distinct pending action:

```text
G31_CANONICAL_CONDENSATION_DECISION
valid values: APPROVE, REJECT
```

The action name uses the existing common-entry transition envelope; it does
not make condensation approval a G31 execution decision.

An exact decision records the existing two-event review/decision extension.
Replay remains owned by the existing condensation Replay runtime. Common entry
only selects deterministic directories and retains references.

## 6. Human Authority Continuity

The review renders:

- exact source request;
- canonical proposal;
- deterministic validation result;
- exact prefix `P`;
- exact synthesis body `B`;
- exact final projection `F = P + B`;
- hashes, byte counts, code-point counts, and Replay identity; and
- the warning that approval grants no execution authority.

The decision must be exact `APPROVE` or `REJECT`, and the deciding actor must
be the actor to whom the review was presented. Lowercase, aliases, retry,
fallback, and alternate decision values fail closed.

Rejection records immutable decision Replay and terminates without creating an
input binding or invoking G31.

## 7. Dedicated Binding and Unchanged G31

Approval does not directly choose a string for G31. Common entry asks the
certified G35-12 owner to reconstruct Phase 2 Replay and return its immutable
Model D binding.

Common entry passes only:

```text
binding["g31_function_argument"] == B
```

to:

```text
worker_activation.preflight_codex_worker_synthesis(B)
```

The G31 function remains unchanged and constructs:

```text
final_synthesized_request == P + B == F
```

The entry then records a non-authoritative continuity capture requiring exact
equality for:

- raw request;
- canonical prefix;
- final request;
- raw, prefix, and final code-point counts;
- maximum count;
- counting contract; and
- final request SHA-256.

Any mismatch raises a fail-closed error. The continuity capture does not amend
the immutable G35-12 binding, whose preflight flags correctly describe its
pre-invocation state.

## 8. State and Substitution Protection

Continuation requires equality among:

- retained entry review and pending review;
- retained proposal and reviewed proposal;
- retained validation and reviewed validation;
- retained Phase 1 Replay location and reviewed Replay reference;
- retained original request and reviewed source;
- current session and proposal session; and
- current workspace and proposal workspace.

The existing proposal, validation, review, decision, Replay, and binding
validators independently reconstruct their identities. Re-hashing or replacing
only the outer application state cannot authorize substituted content.

## 9. Authority Assessment

Condensation approval remains semantic-representation approval only.

At successful G31 preflight return:

```text
semantic_representation_approved: true
execution_authorized: false
worker_invoked: false
provider_invoked: false
repository_mutated: false
```

No existing implementation approval, grounded execution decision, CODEX
activation decision, result review, content acceptance, or mutation decision
is removed, merged, inferred, or satisfied by this transition.

## 10. Compatibility Assessment

Short direct requests retain the historical branch and emit no condensation
fields. Historical over-bound requests without a proposal continue to produce
the unchanged G31 `SYNTHESIS_PREFLIGHT_FAILED_CLOSED` capture with zero human
approvals and no runtime execution.

The implementation changes no G31 or downstream source file. Targeted
compatibility confirms:

- direct 220/240 boundary behavior;
- historical 221+ failure behavior;
- G31 activation and prompt fidelity;
- common-entry transition behavior;
- Human Interface transport neutrality;
- Replay reconstruction;
- governance conformance and failure semantics; and
- no Worker, Provider, authorization, or mutation leakage.

The reference AiCLI continues to transport existing common-entry
presentations and exact actions. It is not made a proposal producer. A caller
that has no authenticated selected proposal inputs remains on the compatible
fail-closed over-bound path; the Human Interface is never permitted to invent
condensation semantics.

## 11. Validation Summary

The certification evidence records the exact commands and results. The scoped
validation includes:

- complete G35-10 through G35-13 suite;
- focused G31 preflight, activation, prompt-fidelity, and common-entry suite;
- core Human Interface compatibility suite;
- Replay compatibility suite;
- governance compatibility suite;
- governance conformance engine;
- target Python compilation; and
- `git diff --check`.

The governance conformance engine remains deterministically
`PARTIALLY_CONFORMANT` because of the repository's already documented hook
drift. It reports zero critical violations. G35-13 neither changes nor hides
that baseline condition.

Target compilation passes for the modified entry service, the G35-10 through
G35-13 runtime chain, the unchanged G31 preflight owner, and the new test
module. Repository-wide `compileall` additionally discovers five intentionally
malformed generated files under
`sapianta_system/runtime/development/quarantine/`. Those pre-existing,
unmodified negative fixtures fail parsing by design; they are not imported by
the integrated path and are retained visibly rather than rewritten by this
generation.

## 12. Certification Determination

The integrated path proves:

```text
over-bound exact source
-> deterministic PASS
-> exact explicit APPROVE
-> immutable approved Replay reconstruction
-> certified dedicated Model D binding
-> unchanged G31 preflight(B)
-> exact F equality
```

No G31 or downstream constitutional behavior changes.

```text
CANONICAL_CONDENSATION_ENTRY_INTEGRATION_CERTIFIED
```
