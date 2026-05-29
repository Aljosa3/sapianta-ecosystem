# First Useful AiGOL V1 Baseline

Status: frozen operational baseline inventory.

## Baseline Runtime Surface

The frozen first useful AiGOL baseline includes these runtime surfaces:

- `aigol/runtime/minimal_operator_entrypoint.py`
- `aigol/runtime/human_prompt_to_governed_readonly_result.py`
- `aigol/runtime/minimal_cognition_to_execution_bridge.py`
- `aigol/runtime/minimal_execution_runtime_prototype.py`
- `aigol/runtime/read_only_capability_attachment.py`
- `aigol/runtime/filesystem_read_only_capability.py`
- `aigol/runtime/governed_result_summary.py`
- `aigol/runtime/replay_summary_command.py`

## Baseline Governance Surface

The frozen baseline is supported by:

- `governance/MINIMAL_OPERATOR_ENTRYPOINT_V1.md`
- `governance/HUMAN_PROMPT_TO_GOVERNED_READONLY_RESULT_V1.md`
- `governance/MINIMAL_COGNITION_TO_EXECUTION_BRIDGE_V1.md`
- `governance/COGNITION_PROPOSAL_TO_EXECUTION_REQUEST_BRIDGE_V1.md`
- `governance/MINIMAL_EXECUTION_RUNTIME_PROTOTYPE_V1.md`
- `governance/FIRST_READ_ONLY_CAPABILITY_ATTACHMENT_V1.md`
- `governance/SECOND_READ_ONLY_CAPABILITY_ATTACHMENT_V1.md`
- `governance/GOVERNED_RESULT_SUMMARY_V1.md`
- `governance/REPLAY_SUMMARY_COMMAND_V1.md`
- `governance/FIRST_USEFUL_AIGOL_USAGE_GUIDE_V1.md`
- `governance/FROZEN_EPOCH_PRESSURE_VALIDATION_V1.md`
- `governance/FIRST_USEFUL_AIGOL_STABILITY_REPORT_V1.md`

## Baseline Validation Surface

The baseline validation surface includes:

- `tests/test_minimal_operator_entrypoint_v1.py`
- `tests/test_human_prompt_to_governed_readonly_result_v1.py`
- `tests/test_minimal_cognition_to_execution_bridge_v1.py`
- `tests/test_minimal_execution_runtime_prototype_v1.py`
- `tests/test_read_only_capability_attachment_v1.py`
- `tests/test_filesystem_read_only_capability_v1.py`
- `tests/test_governed_result_summary_v1.py`
- `tests/test_replay_summary_command_v1.py`
- `tests/test_frozen_epoch_pressure_validation_v1.py`

## Baseline Capability Surface

The frozen baseline allows only:

- read-only runtime inspection
- bounded filesystem read-only inspection for explicitly allowed paths

The baseline excludes:

- mutation
- shell execution
- network execution
- API execution
- orchestration runtime
- agents
- memory
- autonomous continuation

## Baseline Operator Surface

The operator can:

- submit one bounded request
- receive a governed result summary
- inspect replay through a deterministic replay summary
- use replay evidence as the audit source of truth

## Baseline Evolution Rule

Future evolution must treat this baseline as a preservation target.

New work must not weaken:

- proposal-only cognition
- AiGOL governance authority
- authorization-before-execution
- worker execution-only role
- replay centrality
- fail-closed boundaries
- read-only capability discipline
