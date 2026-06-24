# SAPIANTA_DEMO_RUNBOOK_V1

Status: Ready

Purpose: Operator-facing runbook for reproducing the certified ACLI governed development workflow.

Target verdict:

```text
SAPIANTA_DEMO_RUNBOOK_READY
```

## 1. What This Demo Proves

This runbook demonstrates the certified no-copy-paste ACLI development path:

```text
Human Prompt
-> HIRR
-> Workflow Selection
-> Proposal
-> Approval
-> Execution
-> Repository Mutation
-> Validation
-> Replay
```

The demo proves that a normal operator prompt can enter ACLI, resolve to governed development, require explicit approval, mutate the repository only through the governed worker path, run validation, and preserve replay evidence.

## 2. What This Demo Does Not Prove

This demo does not claim:

- unrestricted autonomous development
- automatic execution without human approval
- production deployment readiness
- complete compliance certification
- hidden governance mutation
- autonomous constitutional mutation

LLM proposes. AiGOL governs. Worker executes. Replay records.

## 3. Prerequisites

Required:

- Linux or macOS shell
- Python project environment
- `git`
- `pytest`
- local checkout of the SAPIANTA repository

Recommended:

- clean working branch or disposable evaluation branch
- terminal large enough to inspect multiline ACLI output

Not required for the certified ACLI development path:

- live OpenAI provider access
- external ChatGPT or Codex copy/paste loop
- production server access

## 4. Environment Preparation

Run from the repository root:

```bash
python -m pytest --version
python -m aigol.cli.aigol_cli --help
python -m aigol.cli.aigol_cli conversation --help
git status --short
```

Expected result:

- pytest is available
- AiGOL CLI help renders successfully
- `conversation` command exposes `--session-id`, `--runtime-root`, `--workspace`
- operator understands any pre-existing working tree changes before starting

Do not commit secrets or paste credentials into ACLI.

## 5. Startup Sequence

Start an ACLI conversation from the repository root:

```bash
python -m aigol.cli.aigol_cli conversation \
  --session-id SAPIANTA-DEMO-001 \
  --created-at 2026-06-24T00:00:00Z \
  --runtime-root runtime/sapianta_demo_runbook_v1 \
  --workspace .
```

Use a unique `--session-id` for each demo run. If replay directories already exist, choose a new session id rather than overwriting evidence.

## 6. Canonical Demo Scenario

At the ACLI prompt, enter:

```text
Add replay validation
```

Expected first-turn flow:

```text
ROUTING DECISION
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
```

Optional routing smoke test for governance-artifact-only intent:

```text
Add governance artifact TEST_ACLI_BRIDGE_V1 documenting that ACLI execution bridge was successfully tested.
```

That prompt should route to a certified governance artifact creation path. The canonical full demo uses `Add replay validation` because it exercises proposal generation, approval capture, repository mutation, validation, and replay through the governed development bridge.

Expected proposal output includes:

```text
Governed Development Proposal
approval_required: true
approval_boundary: explicit human APPROVE required before mutation
mutation_performed: false
worker_invoked: false
validation_executed: false
next_action: APPROVE, REJECT, or REQUEST_MODIFICATION
```

No repository mutation should occur before approval.

## 7. Approval Flow

Review the proposal id, proposal hash, target paths, replay reference, and approval boundary.

To approve, enter:

```text
APPROVE
```

Expected approval-turn routing output:

```text
ROUTING DECISION
workflow: GOVERNED_DEVELOPMENT_WORKFLOW
confidence: HIGH
matched:
- governed-development-pending-approval
- APPROVE
reason:
Stateful governed development approval decision detected; continuing the pending proposal without rerouting.
```

The approval turn must not display:

```text
ROUTING FAILED CLOSED
```

Expected execution output includes:

```text
Governed Development Execution
bridge_status: EXECUTION_COMPLETED
approval_decision: APPROVED
approval_bypassed: false
proposal_hash: sha256:...
approval_hash: sha256:...
mutation_performed: true
worker_invoked: true
validation_executed: true
workflow_execution_status: GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
worker_protections_preserved: true
validation_allowlists_preserved: true
replay_lineage_preserved: true
```

Exit the session after completion:

```text
exit
```

## 8. Expected Repository Changes

The governed development workflow creates bounded demo artifacts with generated names.

Expected path families:

```text
docs/governance/ACLI_GOVERNED_DEVELOPMENT_*_V1.md
aigol/runtime/acli_governed_development_*.py
```

Inspect changes:

```bash
git status --short
git diff -- docs/governance aigol/runtime
```

The exact generated suffix is replay-derived and may differ between sessions.

## 9. Validation Inspection

Run whitespace validation:

```bash
git diff --check
```

Run the focused certification regression:

```bash
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
```

Optional broader routing validation:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_human_execution_intent_detection_v1.py -q
```

Expected result:

- `git diff --check` passes
- focused bridge tests pass
- conversational routing tests pass when run

## 10. Replay Inspection

Interactive replay evidence is written under:

```text
runtime/sapianta_demo_runbook_v1/SAPIANTA-DEMO-001/
```

Expected turn directories:

```text
TURN-000001/
TURN-000002/
```

Key replay locations:

```text
TURN-000001/conversational_cli_routing/
TURN-000001/routing_visibility/
TURN-000001/universal_intake/
TURN-000001/acli_governed_development_execution_bridge/
TURN-000002/routing_visibility/
TURN-000002/universal_intake/
TURN-000002/acli_governed_development_execution_bridge/
TURN-000002/acli_governed_development_execution_bridge/governed_development_workflow/
```

Inspect replay files:

```bash
find runtime/sapianta_demo_runbook_v1/SAPIANTA-DEMO-001 -maxdepth 4 -type f | sort
```

Replay evidence should show:

- original human prompt captured
- routing visibility recorded
- proposal persisted
- approval persisted
- repository mutation execution recorded
- validation command recorded
- governed development outcome recorded
- replay reconstruction references present

## 11. Troubleshooting

### Prompt Routes To Clarification

If ACLI asks clarification questions, the prompt did not deterministically match a certified governed workflow. Use the canonical prompt in this runbook and retry with a new session id.

### `ROUTING FAILED CLOSED` Appears On Approval

This is not expected for a valid pending governed development approval. Confirm that the previous turn produced a `Governed Development Proposal` and that the approval token is exactly:

```text
APPROVE
```

Then run:

```bash
python -m pytest tests/test_acli_governed_development_execution_bridge_v1.py -q
```

### Replay Directory Already Exists

Use a fresh session id:

```text
SAPIANTA-DEMO-002
```

Do not delete replay evidence that must be retained for audit.

### Validation Fails

Treat validation failure as fail-closed evidence. Do not claim demo success until `git diff --check` and the focused bridge test pass.

### Working Tree Has Existing Changes

Record the pre-demo `git status --short` output. Existing changes do not invalidate the demo, but the operator must distinguish pre-existing changes from ACLI-generated changes.

## 12. Success Criteria

The demo is successful when:

- ACLI starts through `python -m aigol.cli.aigol_cli conversation`
- a natural language prompt reaches a certified governed workflow
- ACLI renders a proposal before mutation
- mutation does not occur before `APPROVE`
- approval turn does not show misleading routing failure
- execution completes through the governed development workflow
- repository mutation occurs through the worker path
- validation passes
- replay evidence is persisted under the selected runtime root
- operator can inspect repository changes and replay locations

## 13. Final Verdict

```text
SAPIANTA_DEMO_RUNBOOK_READY
```
