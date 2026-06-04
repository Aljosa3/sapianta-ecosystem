# AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_REVIEW_V1

## Status

Review-only pre-OCS operator experience assessment.

No runtime mutation, implementation change, replay mutation, or OCS activation is
authorized by this artifact.

`AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_STATUS = PARTIAL_WITH_BLOCKING_UX_GAPS`

## Review Scope

Reviewed surfaces:

- `aigol/runtime/conversation_to_ppp_handoff_execution.py`;
- `aigol/runtime/implementation_approval_resume.py`;
- `aigol/runtime/improvement_approval_runtime.py`;
- `aigol/cli/aigol_cli.py`;
- `aigol/cli/commands/chain_inspection.py`;
- `aigol/runtime/unified_replay_reconstruction_runtime.py`;
- `aigol/runtime/conversation_native_development_intent_routing.py`;
- `aigol/runtime/domain_bundle_registry_runtime.py`;
- approval resume and chain inspection tests.

## Findings

### HUMAN_APPROVAL_REQUIRED Lifecycle

The lifecycle correctly preserves human authority for high-risk Trading
improvement requests. `conversation_to_ppp_handoff_execution` records a
proposal-only handoff packet and terminates at `HUMAN_APPROVAL_REQUIRED` before
implementation handoff creation.

The approval packet is replay-visible and includes context, registry,
provider-policy, proposal, validation, and approval request artifacts.

Primary gap: the operator-facing summary shows that approval is required, but
does not expose a complete decision menu or explain replay consequences for
approval, rejection, or modification.

### Approval Resume Runtime

`implementation_approval_resume` validates approval request hash, proposal
lineage, chain id, scope, expiration, and replay packet integrity before
resuming into implementation handoff creation.

Primary gap: the resume runtime supports only `APPROVED` human implementation
approval artifacts. Rejection and modification request paths fail closed as
missing or invalid approval instead of becoming first-class replay-valid
terminal decisions.

### show-latest-chain Runtime

The chain inspection command uses unified replay reconstruction and returns
operator-visible fail-closed summaries when reconstruction fails.

Primary gap: inspection is read-only with respect to source replay, but it still
writes inspection reports under the report root. Before OCS transition, the CLI
should make that evidence-write behavior explicit in help text and operator
summaries.

### Replay Inspection Behavior

Replay inspection preserves source replay immutability and fail-closes on
missing replay roots, corrupted reconstruction reports, or missing evidence.

Primary gap: failure feedback is technically correct but not diagnostic enough
for an operator. It does not consistently distinguish missing replay root,
missing chain id, ambiguous latest chain, corrupted wrapper hash, and missing
expected lifecycle stage in human-facing language.

### Unknown Domain Handling

Unknown domain handling is deterministic and fail-closed. Native development
intent routing only routes known catalog patterns, and registry-backed domain
bundle lookup fail-closes on unknown bundle identity.

Primary gap: unknown or unsupported domain prompts fail through generic
classification or registry messages. The operator is not shown a supported
domain list, a registry resolution summary, or an explicit "not currently
factory-resolvable" explanation.

### Human-Facing CLI Interaction

The interactive conversation CLI can preserve pending approval across the
session and accepts a literal `approve` turn to resume the chain.

Primary gap: the interaction is under-specified for humans. There is no explicit
prompt such as "approve/reject/request changes/show packet", no command to
inspect the pending approval packet inline, and no accidental approval guard
beyond the exact pending-chain validation performed by the runtime.

## Replay Impact

Current replay behavior is structurally safe:

- high-risk approval-required state is replay-visible;
- approval resume is lineage-checked;
- chain inspection is fail-closed;
- source replay is not mutated by inspection;
- unknown domain resolution fails closed.

However, OCS transition would amplify operator ambiguity unless approval
choices, rejection/modification artifacts, and registry feedback become
first-class CLI behaviors.

## Final Classification

AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_STATUS = PARTIAL_WITH_BLOCKING_UX_GAPS
