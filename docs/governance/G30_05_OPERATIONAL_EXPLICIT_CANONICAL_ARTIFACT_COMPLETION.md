# G30-05 Operational Explicit Canonical Artifact Completion

Status: implemented and bounded.

## Purpose

G30-05 demonstrates the first complete operational AiCLI workflow in which a
user receives a Generation 29 clarification and then supplies an existing,
compatible canonical artifact through certified explicit artifact ingress.

The lifecycle uses the certified Platform Core, G29, G28, Platform Knowledge,
Canonical Presentation, Replay, and Governance responsibilities unchanged.

## Deterministic integration finding

G30-04 already persisted the clarification owner, canonical semantic slot,
originating Project Objective, session identity, and route lineage. G29-08
already accepted opaque artifact references and composed validated artifacts
with G29-06.

One bounded representation defect remained: when a supplied artifact fulfilled
the open `input_artifact_family` slot, G29 correctly completed instead of
returning another clarification envelope. The operational turn validator
interpreted the absence of that new envelope as semantic-slot substitution.

G30-05 preserves the originating semantic-slot identity on the completion turn.
No classifier, selector, route, lifecycle stage, registry, or authority changed.

## Operational lifecycle

```text
User request
  -> AiCLI opaque transport
  -> Platform Core Project Services
  -> G29 input_artifact_family clarification
  -> Replay-backed session suspension
  -> user resumes the same session with --artifact-reference
  -> G29-08 explicit canonical artifact ingress
  -> G29-06 selection and canonical input binding
  -> Platform Knowledge
  -> G29-04 invocation lifecycle
  -> unchanged G28 certified capability invocation
  -> Canonical Platform Presentation
  -> Replay reconstruction
```

The completion turn retains `OPERATIONAL_CLARIFICATION_REPLY`, the original
clarification owner, `input_artifact_family`, and the original Project
Objective. Project Objective inference is not restarted.

## Terminal validation

The operational validation used two real repository-local `./aicli` commands
with the same session and runtime root.

The first command submitted:

```text
Analyze Platform Capability Composition Coverage.
Audit only.
```

AiCLI rendered the existing G29 clarification and closed with
`REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT`.

The second command supplied a
`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1` Replay wrapper
using `--artifact-reference`. The unchanged lifecycle returned:

```text
work_type: AUDIT_ONLY
binding_status: GOVERNED_READ_ONLY_WORK_BOUND
presentation_status: PRESENTATION_READY
The selected certified Platform capability completed successfully.
provider_invoked: False
worker_invoked: False
repository_mutated: False
```

## Replay continuity

Replay reconstruction verifies three connected chains:

1. the G30-04 operational clarification origin and completion turn;
2. G29-08 received, resolved, and downstream-linked ingress artifacts;
3. G29-06 selection, Platform Knowledge, G29-04, G28, and canonical
   presentation lineage.

The ingress reconstruction requires its downstream route hash to equal the
completed G29-06 route hash. The operational completion turn retains the
originating clarification-envelope hash and semantic slot.

## Fail-closed behavior

A canonical artifact whose immutable wrapper or artifact body is modified is
rejected by existing G29-08 validation. The result remains read-only and
records `GOVERNED_READ_ONLY_WORK_FAILED_CLOSED`; no semantic route, Provider,
Worker, or repository mutation is reached.

## Authority boundaries

- AiCLI transports the user message and opaque reference only.
- Platform Core validates the resumed session and clarification owner.
- G29 owns semantic selection, canonical input compatibility, and lifecycle.
- G28 owns certified capability invocation.
- Canonical Presentation owns the terminal-ready result.
- Replay owns reconstruction and tamper detection.
- Human Interface, Worker, and Provider authority remain unchanged.

## Validation evidence

Deterministic validation completed on 2026-07-15:

- focused G30-05 completion and invalid-artifact tests: 3 passed;
- combined G28, G29, G30-04, and G30-05 regression selection: 84 passed;
- Replay reconstruction and governance selection: 17 passed;
- full repository suite: 6,144 passed and 4 skipped;
- `py_compile` and `git diff --check`: passed.

The read-only governance conformance engine remains
`PARTIALLY_CONFORMANT`: 18 checks pass, two pre-existing hook-conformance
checks fail, and there are no critical violations. G30-05 does not alter or
conceal that known hook drift.

## Remaining operational limitations

- The canonical artifact must already exist as a valid immutable Replay
  wrapper inside an ingress-allowed root.
- AiCLI resumes artifact completion through a second `submit` invocation; it
  does not yet offer an in-process command for attaching a reference.
- A failed artifact submission produces a fail-closed result. Retrying requires
  a new governed request rather than silently replacing the rejected artifact.

These limitations preserve explicit ingress and fail-closed semantics.

## Reusable pattern

Future operational artifact completion should preserve this sequence:

1. suspend on the owner-authored canonical semantic slot;
2. persist the immutable owner/session/objective envelope;
3. accept only an explicit opaque reference on resume;
4. validate and snapshot through existing ingress;
5. return the artifact to the same owner and slot;
6. reconstruct ingress, route, invocation, presentation, and operational turn.

No natural-language reply should be converted into a canonical artifact by the
Human Interface.
