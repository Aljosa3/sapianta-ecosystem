# G14-22 Reference Unified Human Interface Implementation V1

Status: reference Unified Human Interface implemented and certified.

Final verdict: REFERENCE_UNIFIED_HUMAN_INTERFACE_CERTIFIED

## 1. Executive Summary

G14-22 implements the first clean reference Unified Human Interface for AiGOL:

```text
aicli
```

The implementation is intentionally minimal. It owns only terminal interaction, conversational presentation, user input, output rendering, and approval collection.

All semantic, project, governance, provider, worker, and Replay responsibilities remain delegated to the certified platform runtime:

```text
Human
-> aicli
-> Platform Core project services
-> PGSP
-> UBTR
-> CSA
-> Platform Core
-> Governance
-> Provider Platform
-> Worker Platform
-> Replay
```

The live validation completed a real reference UHI session through provider invocation, worker execution, result validation, and Replay certification.

Final verdict: REFERENCE_UNIFIED_HUMAN_INTERFACE_CERTIFIED

## 2. Implementation Summary

Implemented artifacts:

| Artifact | Purpose |
| --- | --- |
| `aigol/cli/aicli.py` | Reference UHI CLI module. |
| `aicli` | Repository-local lightweight executable wrapper. |
| `tests/test_g14_22_reference_unified_human_interface_v1.py` | Regression tests for delegation, clarification, scenario coverage, and thin-adapter constraints. |

The reference CLI supports:

- natural development request entry;
- Platform Core owned intent resolution;
- Platform Core owned clarification rendering;
- governed implementation summary rendering;
- `/approve` approval collection;
- `/cancel` pending summary cancellation;
- `/exit` session termination;
- delegation to the certified runtime after approval.

The reference CLI does not implement its own REPL history model, project workspace model, provider selection, worker routing, governance logic, or Replay persistence.

## 3. Responsibility Boundary

| Responsibility | Owner | G14-22 finding |
| --- | --- | --- |
| Terminal input/output | `aicli` | Implemented as interface-local presentation. |
| Human approval collection | `aicli` | Implemented as local approval capture only. |
| Development intent resolution | Platform Core project services | Reused through `resolve_development_intent(...)`. |
| Clarification question production | Platform Core project services | Reused through `guided_development_clarification(...)`. |
| Runtime continuation | Certified Platform Core runtime | Reused through `run_interactive_conversation(...)`. |
| Semantic interpretation | UBTR / certified runtime path | Not implemented in `aicli`. |
| Structured intent | CSA / certified runtime path | Not implemented in `aicli`. |
| Governance authorization | Governance | Not implemented in `aicli`. |
| Provider invocation | Provider Platform | Not implemented in `aicli`. |
| Worker execution | Worker Platform | Not implemented in `aicli`. |
| Replay evidence | Replay | Not implemented in `aicli`. |

Implementation evidence:

```text
aicli_authorizes: False
aicli_executes: False
aicli_owns_replay: False
aicli_owns_workspace: False
aicli_owns_goal_mapping: False
aicli_owns_provider_selection: False
platform_core_services_delegated: True
provider_platform_preserved: True
worker_platform_preserved: True
replay_authority_preserved: True
```

## 4. Interface Behavior

The reference interaction is:

```text
aicli
> Implement governance validation utility.

Governed implementation summary
...
Type /approve to continue, or /cancel to discard.
> /approve
```

After approval, `aicli` delegates to the certified runtime. It does not inspect providers, authorize execution, select workers, or write Replay evidence directly.

Session completion reports:

```text
runtime_status: REFERENCE_UHI_RUNTIME_BOUND
submitted_message_count: 1
approval_count: 1
aicli_authorizes: False
aicli_executes: False
aicli_owns_replay: False
```

## 5. Regression Scenario Matrix

| Scenario | Validation method | Result |
| --- | --- | --- |
| A. New implementation | `Implement governance validation utility.` | Delegates to the common runtime runner after approval. |
| B. Improve existing implementation | `Improve provider availability handling.` | Delegates to the common runtime runner after approval. |
| C. Extend certified capability | `Extend certified replay capability with a summary utility.` | Delegates to the common runtime runner after approval. |
| D. Clarification required | `Improve project.` | Renders Platform Core clarification and does not enter runtime. |
| E. Resume project | `Implement workspace resume support.` | Delegates to the common runtime runner after approval. |
| F. Knowledge reuse | `I want AiGOL Next to support GitHub Actions.` | Platform Core maps the goal and the interface delegates after approval. |
| G. Replay generation | `Implement replay summary utility.` | Delegates to the common runtime runner after approval. |

Finding:

All executable scenarios use the same runtime runner. The clarification scenario performs no execution before a deterministic Platform Core clarification is resolved.

## 6. Real Runtime Evidence

Live reference UHI command:

```text
./aicli --session-id G14-22-REFERENCE-UHI-REAL-2 --runtime-root /tmp/aigol_g14_22_reference_uhi_real_2 --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Submitted request:

```text
Implement governance validation utility.
```

Human approval:

```text
/approve
```

Runtime output:

```text
runtime_status: REFERENCE_UHI_RUNTIME_BOUND
governance_authorization_reached: True
provider_invocation_reached: True
worker_execution_reached: True
replay_certification_reached: True
runtime_replay_reference: /tmp/aigol_g14_22_reference_uhi_real_2/G14-22-REFERENCE-UHI-REAL-2/TURN-000001
```

Evidence root:

```text
/tmp/aigol_g14_22_reference_uhi_real_2/G14-22-REFERENCE-UHI-REAL-2/TURN-000001
```

## 7. Provider Evidence

Provider proposal production evidence:

```text
post_context_continuation/conversation_ppp_routing/provider_proposal_production/003_provider_proposal_production_returned.json
```

Observed values:

```text
provider_id: openai
production_status: PROVIDER_PROPOSAL_PRODUCED
provider_invocation_status: PROVIDER_INVOKED
failure_reason: null
provider_authority: false
worker_created: false
```

Finding:

Provider Platform remained the invocation boundary. The provider was not authoritative and did not execute work.

## 8. Governance Evidence

Governance authorization evidence:

```text
certified_development_continuation/execution_authorization/002_authorization_artifact_recorded.json
```

Observed values:

```text
authorization_status: EXECUTION_AUTHORIZED
authorizing_actor: AIGOL_GOVERNANCE
execution_started: false
worker_assigned: false
worker_dispatched: false
worker_invoked: false
replay_visible: true
```

Finding:

`aicli` collected human approval, but Governance retained authorization authority.

## 9. Worker Evidence

Worker invocation evidence:

```text
certified_development_continuation/worker_lifecycle_continuation/worker_invocation/002_invocation_artifact_recorded.json
```

Observed values:

```text
worker_id: AIGOL-WORKER-CLAUDE-EXTERNAL
worker_family: CLAUDE_EXTERNAL
worker_role: CLAUDE_CODE (WORKER_ROLE)
invocation_status: WORKER_INVOKED
worker_invoked: true
invoked_by: AIGOL_GOVERNANCE
replay_visible: true
```

Finding:

Worker execution remained Worker Platform owned and Governance invoked.

## 10. Replay Evidence

Replay certification evidence:

```text
certified_development_continuation/worker_lifecycle_continuation/replay_certification/000_replay_certification_artifact_recorded.json
```

Observed values:

```text
certification_status: REPLAY_CERTIFICATION_COMPLETED
certification_decision: CERTIFIED_FOR_CLOSED_IMPROVEMENT_LOOP
replay_lineage_preserved: true
deterministic_certification_preserved: true
fail_closed_preserved: true
failure_reason: null
```

Finding:

Replay remained canonical and preserved full execution evidence.

## 11. Architecture Compliance

G14-22 preserves the Unified Human Interface architecture.

Confirmed invariants:

- `aicli` is a thin interface adapter.
- `aicli` does not perform semantic interpretation.
- `aicli` does not implement development intent classification.
- `aicli` does not own project guidance, goal mapping, workspace logic, or knowledge reuse.
- `aicli` does not select providers.
- `aicli` does not authorize.
- `aicli` does not execute workers.
- `aicli` does not generate Replay evidence.
- Platform Core services remain reusable by Web, Android, Voice, REST, Desktop, and future interfaces.

No responsibility migration was detected.

## 12. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/cli/aicli.py tests/test_g14_22_reference_unified_human_interface_v1.py
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py -q
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_19_development_intent_resolution_unification_v1.py tests/test_openai_provider_failure_diagnostics_v1.py -q
./aicli --session-id G14-22-REFERENCE-UHI-REAL-2 --runtime-root /tmp/aigol_g14_22_reference_uhi_real_2 --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
git diff --check
```

Validation result:

```text
py_compile: clean
pytest: 5 passed
relevant pytest suites: 12 passed
real runtime: REFERENCE_UHI_RUNTIME_BOUND
provider invocation: reached
worker execution: reached
Replay certification: reached
git diff --check: clean
```

## 13. Final Determination

The reference Unified Human Interface is implemented and validated.

`aicli` provides a clean baseline for future Web, Android, Voice, REST, Desktop, and other Unified Human Interfaces because it contains only presentation and approval collection logic while delegating all certified platform responsibilities to Platform Core and the governed runtime.

Final verdict: REFERENCE_UNIFIED_HUMAN_INTERFACE_CERTIFIED
