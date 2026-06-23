# DEMO_QUICKSTART_V1

Status: Ready

Purpose: Minimal operator-facing quickstart for demonstrating the certified Sapianta workflow.

Target verdict:

```text
DEMO_QUICKSTART_READY
```

## 1. What This Demo Shows

This quickstart demonstrates the certified governance chain:

```text
Human Question
-> HIRR / ACLI
-> OCS Cognition
-> Multi-Provider Comparison
-> Human Review
-> Governed Development Approval
-> Repository Mutation Worker
-> Validation
-> Replay Reconstruction
```

The demo shows that AI cognition can inform governed execution without becoming execution authority.

## 2. What This Demo Does Not Show

This demo does not show:

- unrestricted autonomous agents
- automatic execution from provider output
- production deployment
- compliance guarantees
- broker/API execution
- hidden governance mutation
- autonomous constitutional mutation

## 3. Installation Prerequisites

Required:

- Linux or macOS shell
- Python 3.12 or compatible project Python
- `git`
- `pytest`
- repository checkout of SAPIANTA

Optional:

- `OPENAI_API_KEY` for live OpenAI-backed conversational OCS demos

The certified quickstart path does not require live provider access because the certification scenario uses deterministic provider fixtures.

## 4. Environment Setup

From the repository root:

```bash
python -m pytest --version
python -m aigol.cli.aigol_cli --help
python -m aigol.cli.aigol_cli conversation --help
```

Expected result:

- pytest is available
- the AiGOL CLI prints command help
- `aigol conversation` exposes `--session-id`, `--runtime-root`, and `--workspace`

If live OpenAI-backed OCS is needed:

```bash
export OPENAI_API_KEY="..."
```

Do not commit secrets.

## 5. Startup Commands

Validate the certified unified chain:

```bash
python -m pytest tests/test_cognition_to_governed_execution_certification_v1.py
```

Validate the governed development path:

```bash
python -m pytest tests/test_governed_development_end_to_end_certification_v1.py
```

Validate conversational runtime stability:

```bash
python -m pytest tests/test_conversational*.py
```

Optional interactive ACLI startup:

```bash
python -m aigol.cli.aigol_cli conversation \
  --session-id DEMO-SESSION-001 \
  --created-at 2026-06-23T00:00:00Z \
  --runtime-root runtime/demo_quickstart \
  --workspace .
```

Example interactive prompt:

```text
Add replay validation
```

Expected routing:

```text
DEVELOPMENT_INTENT -> GOVERNED_DEVELOPMENT_WORKFLOW
```

## 6. Canonical Demo Scenario

Use the certified executable scenario:

```bash
python -m pytest tests/test_cognition_to_governed_execution_certification_v1.py -q
```

Scenario summary:

1. Human asks whether replay validation should be added.
2. OCS runs multiple cognition providers.
3. Cognition comparison analyzes agreement and disagreement.
4. Human review bridges cognition into governed development.
5. Governed development approval binds the proposal hash.
6. Governance artifact creation executes.
7. Repository mutation executes through the worker path.
8. Validation runs through the allowlisted runner.
9. Replay reconstruction verifies the chain.
10. Missing approval fails closed without mutation.

## 7. Expected Outputs

Expected pytest result:

```text
2 passed
```

Expected evidence from the unified certification:

- OCS final status is completed
- selected cognition mode is `MULTI_PROVIDER_COMPARISON`
- comparison remains non-authoritative
- human review is recorded
- governed development approval is required
- repository mutation worker is used
- validation command status is completed
- replay reconstruction succeeds
- missing approval produces `FAILED_CLOSED`

Expected safety signals:

- provider authority is false
- comparison authority is false
- worker invocation happens only inside the governed repository mutation path
- approval is not bypassed
- replay remains source of truth

## 8. Replay Locations

The pytest scenario writes replay evidence under pytest temporary directories.

To inspect paths during a run, use verbose pytest:

```bash
python -m pytest tests/test_cognition_to_governed_execution_certification_v1.py -vv
```

Replay roots created by the scenario include:

```text
ocs_cognition/
development_routing/
governed_development/
governed_development/governance_artifact_creation/
governed_development/governed_repository_mutation/
governed_development/governed_repository_mutation/repository_mutation_worker/
governed_development/governed_repository_mutation/validation_command/
```

For an interactive ACLI session, replay evidence is written under the selected runtime root:

```text
runtime/demo_quickstart/DEMO-SESSION-001/TURN-000001/
```

Common subdirectories:

```text
source_router/
conversational_cli_routing/
routing_visibility/
universal_intake/
turn_completion/
```

## 9. Troubleshooting

### `pytest` is missing

Install project test dependencies in the active Python environment.

Minimum check:

```bash
python -m pytest --version
```

### `ModuleNotFoundError: aigol`

Run commands from the repository root.

The repository `pytest.ini` sets `pythonpath` for tests.

### Live OpenAI prompt fails closed

Check:

```bash
echo "$OPENAI_API_KEY"
```

Provider failure is expected to fail closed. It should not authorize execution or mutate governance.

### `FAILED_CLOSED` appears

`FAILED_CLOSED` means the runtime refused to proceed without required evidence, approval, replay integrity, or validation success.

This is a safety behavior, not automatically a demo failure.

For the canonical certification scenario, one test intentionally verifies missing approval fails closed.

### Replay directory already exists

Use a new `--session-id` or remove only demo-generated runtime directories after confirming they are not needed as evidence.

Do not delete governance or certification artifacts.

## 10. Success Criteria

The quickstart is successful when:

- the unified certification test passes
- governed development certification passes
- conversational runtime tests pass
- the operator can explain where cognition stops and human authority begins
- replay evidence locations are known
- fail-closed behavior is visible and understandable

Minimum success command:

```bash
python -m pytest tests/test_cognition_to_governed_execution_certification_v1.py
```

Expected result:

```text
2 passed
```

## 11. Final Verdict

```text
DEMO_QUICKSTART_READY
```
