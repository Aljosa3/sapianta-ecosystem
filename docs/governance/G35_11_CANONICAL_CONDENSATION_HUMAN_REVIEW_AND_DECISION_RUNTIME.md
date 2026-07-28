# G35-11 Canonical Condensation Human Review and Decision Runtime

Status: IMPLEMENTED — STANDALONE AND DORMANT
Version: 1.0.0
Date: 2026-07-28
Authority: Human semantic-representation decision boundary
Dependencies: G35-05, G35-08, G35-09, G35-10
Scope: exact review presentation, explicit decision, and Replay extension only

## 1. Result

Generation 35-11 implements the standalone human-review and human-decision
boundary for Canonical Governed Development Condensation:

```text
immutable source
      |
      v
immutable proposal
      |
      v
deterministic PASS validation
      |
      v
exact human-review presentation
      |
      v
explicit APPROVE or REJECT decision
```

The capability remains dormant and unregistered. It creates no G31 input,
CODEX synthesis request, authorization, Worker or Provider activity, execution
gate state, task-outcome state, deployment authority, or repository mutation.

## 2. Runtime Surface

Added:

- `aigol/runtime/canonical_governed_development_condensation_human_review_runtime.py`;
- `aigol/runtime/canonical_governed_development_condensation_human_decision_runtime.py`;
- `tests/test_g35_11_canonical_condensation_human_review_and_decision_runtime.py`;
- this report; and
- Phase 2 certification evidence.

Extended:

- `aigol/runtime/canonical_governed_development_condensation_replay.py`.

No production entry point, generic CODEX schema, authorization schema, Worker
contract, Provider contract, execution-gate contract, task-outcome contract,
or capability registry was changed.

## 3. Exact Human Review Presentation

The review artifact is:

```text
CANONICAL_CONDENSATION_HUMAN_REVIEW_PRESENTATION_V1
```

Creation requires:

1. an immutable G35-10 proposal;
2. its exact deterministic validation result;
3. validation status `PASS`;
4. supported validator version `1.0.0`;
5. successful reconstruction of the referenced Phase 1 Replay;
6. exact equality between supplied and replayed proposal and validation; and
7. an exact human actor and presentation time.

The review artifact embeds rather than merely summarizes:

- the exact original source request and raw content commitment;
- the complete proposal artifact and proposal commitment;
- the complete validation artifact, result, version, ID, and commitment;
- exact Model D prefix `P`;
- exact proposed synthesis body `B`;
- exact complete projection `F = P + B`;
- UTF-8 byte counts and content commitments for `P`, `B`, and `F`;
- Unicode-code-point counts for `P`, `B`, and `F`;
- the complete projection commitment;
- the Phase 1 Replay family, record hashes, family hash, and location;
- the only valid outcomes, `APPROVE` and `REJECT`; and
- the explicit no-execution warning.

The rendering function emits the exact source text, canonical JSON proposal,
canonical JSON validation, and exact Model D strings and commitments. It does
not reconstruct a replacement value for presentation.

The review identity and hash cover every displayed field. Any content,
commitment, actor, time, warning, Replay reference, or authority-boundary
change creates an identity failure or reconstruction mismatch.

## 4. Explicit Human Decision

The decision artifact is:

```text
CANONICAL_CONDENSATION_HUMAN_DECISION_V1
```

The runtime accepts exactly:

```text
APPROVE
REJECT
```

It performs no trimming, case conversion, alias resolution, defaulting,
timeout interpretation, or continuation inference. Values such as `APPROVED`,
`approve`, `YES`, an empty value, a padded value, or an ambiguous phrase fail
closed.

The deciding actor must be the actor named in the exact review presentation.
The decision binds:

- source-request and source-bundle commitments;
- proposal and validation commitments;
- review ID and commitment;
- Phase 1 Replay family hash;
- exact `P`, `B`, and `F`;
- their content commitments and the projection commitment;
- exact decision actor and time;
- decision schema and scope; and
- deterministic decision ID and hash.

### 4.1 Approval

`APPROVE` creates one immutable nested artifact:

```text
CANONICAL_CONDENSATION_APPROVED_PROJECTION_V1
```

It contains the exact reviewed `P`, `B`, and `F`, byte and code-point counts,
content hashes, proposal/validation/review commitments, and Phase 1 Replay
family hash. Its own artifact hash is deterministic.

Its only meaning is:

```text
The exact reviewed condensation projection is approved as a faithful
governed representation of the source request.
```

It does not authorize G31 admission, CODEX synthesis, execution, handoff,
Worker or Provider activity, mutation, deployment, or any execution gate.

### 4.2 Rejection

`REJECT` records the exact reviewed subject and sets:

```text
approved_projection: null
approved_projection_artifact_hash: null
approved_projection_created: false
semantic_representation_approved: false
rejection_final_for_review: true
```

A rejection therefore cannot be interpreted as an approved projection.

## 5. No Post-Decision Transformation

The decision is reconstructed from the complete immutable review artifact.
Approval copies the exact reviewed strings and counts without normalization.
The validator recomputes the decision artifact and requires exact equality.

Consequently, changing whitespace, applying `strip()`, replacing the prefix,
rewriting the body, changing the complete projection, altering UTF-8 or
code-point commitments, or substituting another review fails closed even when
the attacker recomputes the outer artifact identity.

## 6. Replay Extension

G35-11 uses the existing G35-10 Replay owner. It does not create a second
Replay authority.

The extension contract is:

```text
CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_REVIEW_DECISION_EXTENSION_V1
```

The five-event chain is:

1. `condensation_source_lineage_recorded`;
2. `condensation_proposal_recorded`;
3. `condensation_validation_recorded`;
4. `condensation_human_review_presented`; and
5. `condensation_human_decision_recorded`.

The first three wrappers are copied unchanged from the immutable Phase 1
Replay. Their content and replay hashes remain identical. The two new wrappers
are chained from the Phase 1 tail and bind the Phase 1 family hash.

This versioned extension preserves both requirements:

- the original three-record Phase 1 family remains independently readable and
  immutable; and
- the Phase 2 reader reconstructs the complete source-through-decision chain
  under one Replay implementation and authority.

Reconstruction verifies exact file membership, Phase 1 wrapper hashes,
Phase 1 causal order, Phase 2 wrapper field sets, extension version, index,
event order, previous-record hashes, time continuity, authority boundaries,
review identity, decision identity, and all cross-record commitments.

For approval it returns the exact approved Model D projection. For rejection
it returns no approved projection.

The append-only writer refuses a non-empty destination. One review chain
therefore cannot receive a second or conflicting decision in its Replay
location. An approval cannot replace an immutable rejection; a new source
proposal, review, and Replay chain are required.

## 7. Fail-Closed Coverage

The runtime fails closed for:

- missing source, proposal, validation, or review evidence;
- validation status other than PASS;
- unsupported or forged validation version/evidence;
- source, proposal, validation, review, or Replay commitment mismatch;
- modified prefix, body, or complete projection;
- `F != P + B`;
- UTF-8 byte, Unicode-code-point, or content-hash mismatch;
- transformed, stripped, normalized, or rewritten approval content;
- decision actor mismatch;
- malformed, partial, aliased, implicit, or ambiguous decisions;
- decision-to-review substitution;
- unsupported review or decision schema versions;
- missing, extra, reordered, or corrupt Replay events;
- Replay wrapper, chain, or reconstruction mismatch;
- duplicate/conflicting decision persistence; and
- an attempted approval replacing an immutable rejection.

Every failure occurs before G31, Authorization, Worker, Provider, execution
gate, CODEX, handoff, deployment, or mutation activity.

## 8. Compatibility

The following remain unchanged:

- G31 synthesis preflight and input binding;
- AiCLI transports;
- common Human Interface runtime entry;
- CODEX Worker activation and generic CODEX contracts;
- generic handoff contracts;
- grounded execution authorization;
- execution-gate authorization;
- Worker and Provider contracts;
- task-outcome review;
- capability certification registry; and
- all existing V1 artifact schemas.

Static import tests confirm that the Phase 2 modules do not import downstream
entry, input-binding, CODEX, Authorization, Worker, Provider, execution-gate,
task-outcome, or registry modules.

## 9. Validation Evidence

Phase 2:

```text
python -m pytest -q \
  tests/test_g35_11_canonical_condensation_human_review_and_decision_runtime.py

31 passed in 0.72s
```

Combined Phase 1 and Phase 2:

```text
python -m pytest -q \
  tests/test_g35_10_canonical_condensation_runtime_phase1.py \
  tests/test_g35_11_canonical_condensation_human_review_and_decision_runtime.py

55 passed in 0.72s
```

Scoped unchanged-boundary compatibility:

```text
111 passed in 147.05s
```

That suite covered existing G31 preflight, activation, transport, CODEX prompt
fidelity, common Human Interface entry, constitutional Replay, governance
conformance, execution authorization, Worker runtime, Provider runtime, and
execution-gate binding/validation.

Target Python compilation and `git diff --check` also passed. This was a
focused compatibility run, not the complete repository regression.

## 10. Remaining Boundary

This generation does not implement:

- G31 input binding;
- approved-condensation mode selection;
- preflight equality binding;
- Human Interface orchestration;
- CODEX activation;
- capability registration; or
- any execution path.

An approved projection remains dormant evidence. It cannot be consumed until a
future separately authorized G31 input-binding generation is implemented and
certified.

## 11. Verdict

```text
CANONICAL_CONDENSATION_HUMAN_REVIEW_AND_DECISION_RUNTIME_CERTIFIED
```

This verdict certifies only the standalone Phase 2 review-and-decision
boundary. It grants no integration, registration, authorization, execution, or
mutation authority.
