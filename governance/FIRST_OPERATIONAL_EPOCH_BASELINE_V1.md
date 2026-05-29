# First Operational Epoch Baseline V1

Status: frozen baseline declaration.

## Baseline Architecture

The first operational AiGOL epoch baseline consists of:

- `aigol/runtime/human_prompt_to_governed_readonly_result.py`
- `aigol/runtime/minimal_cognition_to_execution_bridge.py`
- `aigol/runtime/minimal_execution_runtime_prototype.py`
- `aigol/runtime/read_only_capability_attachment.py`
- `aigol/runtime/filesystem_read_only_capability.py`

## Baseline Governance Evidence

Baseline governance evidence includes:

- `governance/HUMAN_PROMPT_TO_GOVERNED_READONLY_RESULT_V1.md`
- `governance/END_TO_END_OPERATOR_FLOW_REPLAY_V1.md`
- `governance/GOVERNED_READONLY_RESULT_GUARANTEES_V1.md`
- `governance/COGNITION_PROPOSAL_TO_EXECUTION_REQUEST_BRIDGE_V1.md`
- `governance/PROPOSAL_BRIDGE_RUNTIME_CONSISTENCY_REVIEW_V1.md`
- `governance/FIRST_OPERATOR_RUNTIME_REVIEW_V1.md`
- `governance/OPERATOR_RUNTIME_FINDINGS_V1.md`
- `governance/RUNTIME_SIMPLIFICATION_RECOMMENDATIONS_V1.md`

## Baseline Capability Scope

The baseline capability scope is frozen to:

- runtime metadata inspection
- allowlisted filesystem read-only inspection

No write, delete, move, shell, network, API, orchestration, agent, or autonomous capability is part of this baseline.

## Baseline Replay Scope

The baseline replay scope includes:

- operator-level replay
- bridge-level replay
- capability-level replay
- prototype lifecycle replay

Replay remains the source of operational evidence.

## Baseline Evolution Rule

Future evolution must preserve:

- proposal-only cognition
- AiGOL governance authority
- explicit authorization
- execution-only worker role
- replay centrality
- read-only boundary guarantees
- fail-closed ambiguity handling

Capability expansion must not be treated as implied by this freeze.
