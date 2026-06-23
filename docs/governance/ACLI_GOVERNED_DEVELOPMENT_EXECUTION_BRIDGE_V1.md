# ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE_V1

Status: Implemented

Purpose: Close the no-copy-paste development gap by bridging ACLI governed development workflow selection into proposal generation, explicit approval capture, governed execution, validation, and replay.

## 1. Bridge Design

The bridge implements the operator-facing flow:

```text
Human
-> ACLI
-> Development Intent
-> Proposal Generation
-> Approval Capture
-> Governed Development Workflow
-> Repository Mutation
-> Validation
-> Replay
```

The bridge is intentionally two-turn:

1. A natural development prompt produces a replay-visible governed development proposal and stops.
2. A subsequent `APPROVE`, `REJECT`, or `REQUEST_MODIFICATION` turn records the human decision.

Only `APPROVE` is converted into a governed development approval artifact. Repository mutation is impossible before that approval artifact exists.

## 2. Runtime Integration

Implemented runtime module:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
```

The module provides:

- `propose_acli_governed_development_execution`
- `approve_and_execute_acli_governed_development`
- `render_acli_governed_development_bridge_summary`

The bridge composes existing certified runtimes:

- conversational routing
- universal intake
- governed development workflow runtime
- governance artifact creation runtime
- governed repository mutation runtime
- repository mutation worker runtime
- validation command runner runtime
- governed development replay reconstruction

## 3. Exact Code Changes

Modified:

```text
aigol/cli/aigol_cli.py
```

Changes:

- imports the bridge runtime;
- tracks an in-session pending governed development proposal;
- treats pending governed development approval as a stateful pre-routing gate;
- routes `GOVERNED_DEVELOPMENT_WORKFLOW` selection into proposal generation;
- maps human `APPROVE` into governed development `APPROVED`;
- invokes the certified governed development workflow only after approval;
- records turn summaries exposing mutation, worker, validation, replay, and approval status.

Created:

```text
aigol/runtime/acli_governed_development_execution_bridge.py
tests/test_acli_governed_development_execution_bridge_v1.py
```

## 4. Proposal Generation

The proposal stage derives bounded artifacts from:

- ACLI prompt id;
- original human prompt;
- conversational routing decision;
- workflow selection;
- universal intake artifact;
- repository workspace root.

Generated proposal includes:

- one governance artifact creation proposal under `docs/governance/`;
- one repository mutation proposal outside forbidden governance/replay prefixes;
- `git diff --check` validation plan;
- replay references and hashes;
- explicit human approval requirement;
- mutation-before-approval disabled.

## 5. Approval Capture

Approval remains explicit.

Accepted operator decisions:

- `APPROVE`
- `REJECT`
- `REQUEST_MODIFICATION`

Only `APPROVE` creates a governed development approval artifact with:

- top-level proposal hash binding;
- governance artifact component hash binding;
- repository mutation component hash binding;
- human authority preserved;
- approval bypass set to false.

Rejected or modification-requested proposals do not mutate the repository.

## 6. Execution

After approval, the bridge invokes:

```text
execute_governed_development_workflow(...)
```

The workflow then executes:

```text
Governance Artifact Creation
-> Governed Repository Mutation
-> Validation
-> Replay Reconstruction
```

The repository mutation remains delegated to the existing repository mutation worker path.

## 7. Preserved Protections

The implementation preserves:

- fail-closed behavior;
- explicit approval boundary;
- repository mutation worker protections;
- replay lineage;
- proposal hash binding;
- validation allowlists;
- provider non-authority;
- no mutation before approval.

## 8. Tests

Added focused tests:

```text
tests/test_acli_governed_development_execution_bridge_v1.py
```

Covered scenarios:

- `Add replay validation` followed by `APPROVE` executes through ACLI and mutates via the governed workflow;
- `Add replay validation` followed by `REJECT` records rejection and does not mutate;
- `Add replay validation` followed by `exit` leaves approval pending and does not mutate.

The test uses the real `run_interactive_conversation(...)` path instead of manually assembling governed development artifacts.

## 9. Validation Plan

Required validation:

```bash
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
python -m pytest tests/test_governed_development_end_to_end_certification_v1.py -q
python -m pytest tests/test_conversational_cli_runtime_v1.py -q
python -m pytest tests/test_cognition_to_governed_execution_certification_v1.py -q
python -m py_compile aigol/runtime/acli_governed_development_execution_bridge.py aigol/cli/aigol_cli.py
git diff --check
```

## 10. Certification Conditions

`NO_COPY_PASTE_DEVELOPMENT_READY` requires:

- ACLI accepts natural language development intent;
- ACLI routes to `GOVERNED_DEVELOPMENT_WORKFLOW`;
- ACLI generates a governed proposal without external artifact assembly;
- ACLI captures explicit approval;
- approved execution invokes the certified governed development workflow;
- repository mutation executes through worker protections;
- validation succeeds through allowlisted command execution;
- replay evidence is persisted and reconstructable;
- rejection and missing approval do not mutate the repository.

## 11. Final Verdict

```text
NO_COPY_PASTE_DEVELOPMENT_READY
```
