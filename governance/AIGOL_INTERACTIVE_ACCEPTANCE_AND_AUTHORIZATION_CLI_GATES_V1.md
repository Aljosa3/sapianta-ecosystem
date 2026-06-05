# AIGOL_INTERACTIVE_ACCEPTANCE_AND_AUTHORIZATION_CLI_GATES_V1

## Status

Interactive acceptance and authorization CLI gates certified.

## Final Classification

```text
AIGOL_INTERACTIVE_ACCEPTANCE_AND_AUTHORIZATION_CLI_GATES_STATUS = CERTIFIED
```

## Purpose

This milestone replaces synthetic acceptance evidence in the first real
implementation generation epoch with a replay-visible operator checkpoint.

The provider proposes only. AiGOL validates, summarizes, pauses for operator
decision, and proceeds to mutation authorization only after explicit approval.

## CLI Surface

Interactive command:

```text
python -m aigol.cli.aigol_cli implementation real-epoch \
  --request "Create a provider generated implementation candidate requiring interactive approval." \
  --runtime-root /tmp/aigol_interactive_gates_approve_replay \
  --workspace /tmp/aigol_interactive_gates_approve_workspace \
  --created-at 2026-06-05T22:00:00Z \
  --actor-id human.operator
```

Automation and test command:

```text
python -m aigol.cli.aigol_cli implementation real-epoch \
  --request "Create a provider generated implementation candidate requiring interactive approval." \
  --runtime-root /tmp/aigol_interactive_gates_approve_replay \
  --workspace /tmp/aigol_interactive_gates_approve_workspace \
  --created-at 2026-06-05T22:00:00Z \
  --actor-id human.operator \
  --decision APPROVE \
  --decision-reason "Validated paths and hashes; approve CREATE_ONLY mutation."
```

## Checkpoint Display

Before filesystem mutation authorization, the CLI displays:

- request summary;
- generated implementation summary;
- manifest summary;
- affected paths;
- allowed choices: `APPROVE`, `REJECT`, `ABORT`.

## Operator Decisions

### APPROVE

Observed status:

```text
epoch_status: REAL_EPOCH_CERTIFIED
interactive_operator_decision_hash: sha256:d1641b2d5d87e043fc333f24c7902692606c93f092c9f8f1c565bca2f8421523
implementation_certification_hash: sha256:05fddb220df6849cdff9e524012df3b8bcb2afbddbb923661b08bcf2973636c2
materialization_without_approval: false
```

`APPROVE` creates acceptance evidence, permits filesystem mutation
authorization, materializes only authorized `CREATE_ONLY` files, and certifies
the implementation.

### REJECT

Observed status:

```text
epoch_status: REAL_EPOCH_REJECTED_FAILED_CLOSED
interactive_operator_decision_hash: sha256:9be9fcf74a6854d6d2a297a48c994d02ae46a7cc2296604ef5a295ed31a8a43e
workspace_files: 0
```

`REJECT` fails closed after recording the operator decision. No filesystem
mutation authorization artifact is created and no materialization occurs.

### ABORT

Observed status:

```text
epoch_status: REAL_EPOCH_ABORTED
interactive_operator_decision_hash: sha256:090a419f0f7a7dda7980f46a24a192640317abd3d21eb0aca646c33b5b71e302
workspace_files: 0
```

`ABORT` terminates without authorization. No filesystem mutation authorization
artifact is created and no materialization occurs.

## Replay Evidence

The checkpoint records:

- operator decision;
- timestamp;
- actor id;
- decision reason;
- checkpoint hash;
- request summary;
- implementation summary;
- manifest summary;
- affected paths.

The decision artifact is persisted as:

```text
007_interactive_operator_decision_artifact.json
```

In approved runs, the replay inspection report records:

```text
authorization_without_approval: false
materialization_without_approval: false
```

## Validation

Validation performed:

```text
python -m pytest tests/test_interactive_acceptance_and_authorization_cli_gates_v1.py
python -m pytest tests/test_first_real_implementation_generation_epoch_v1.py
python -m pytest tests/test_first_real_epoch_provider_worker.py
git diff --check
```

Additional downstream lifecycle validation remains covered by:

```text
python -m pytest tests/test_implementation_certification_runtime_v1.py
python -m pytest tests/test_filesystem_mutation_runtime_v1.py
python -m pytest tests/test_filesystem_mutation_authorization_runtime_v1.py
python -m pytest tests/test_generated_content_acceptance_runtime_v1.py
python -m pytest tests/test_generated_test_validation_runtime_v1.py
python -m pytest tests/test_generated_content_validation_runtime_v1.py
python -m pytest tests/test_implementation_manifest_runtime_v1.py
```

## Certification Judgment

The flow is fully replay-visible and fail-closed:

```text
Human
-> Provider Proposal
-> Validation
-> Interactive Approval
-> Authorization
-> Materialization
-> Certification
```

No materialization occurs without operator approval.
