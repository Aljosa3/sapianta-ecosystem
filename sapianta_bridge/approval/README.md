# Human Approval Queue v1

This package provides the first immutable governance approval boundary between advisory reflection and any future execution authority.

Approval converts reflection proposals into pending approval artifacts, then records explicit approved or rejected governance decisions. It does not execute tasks, invoke Codex, enqueue transport work, mutate replay logs, or modify reflection artifacts.

## Architecture

- `approval_queue.py`: enqueue advisory proposals and record approve/reject decisions.
- `approval_models.py`: fail-closed approval and decision validation.
- `approval_storage.py`: append-only storage lifecycle.
- `approval_reader.py`: read-only approval and decision history.
- `governance_decisions.py`: immutable decision evidence.
- `approval_cli.py`: bounded CLI for inspection and human decisions.

## Governance Boundary

The lifecycle is:

```text
reflection proposal -> pending/ -> approved/ or rejected/ -> decisions/
```

Every approval artifact preserves source reflection and task lineage. Every decision artifact sets `execution_authority_granted` to `false` in v1.

## CLI

```bash
python -m sapianta_bridge.approval.approval_cli pending
python -m sapianta_bridge.approval.approval_cli approved
python -m sapianta_bridge.approval.approval_cli rejected
python -m sapianta_bridge.approval.approval_cli approve --approval-id APPROVAL-...
python -m sapianta_bridge.approval.approval_cli reject --approval-id APPROVAL-...
python -m sapianta_bridge.approval.approval_cli task --task-id TASK-001
```

Approve and reject commands create governance decision evidence only. They do not trigger execution, create tasks, invoke Codex, or bypass reflection.

## Replay-Safe Lineage

Approval artifacts are deterministic and lineage-bound to reflection IDs and task IDs. Duplicate approvals for the same reflection proposal are blocked fail-closed.

## Why Approval Is Separate From Execution

Reflection remains advisory. Approval records human governance decisions. Future execution layers must still pass through separate protocol, transport, and governance boundaries. Approval v1 introduces explicit decision evidence, not autonomy.
