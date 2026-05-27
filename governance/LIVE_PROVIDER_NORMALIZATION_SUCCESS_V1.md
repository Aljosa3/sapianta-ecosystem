# LIVE_PROVIDER_NORMALIZATION_SUCCESS_V1

## Scope

This milestone stabilizes the FIRST successful end-to-end governed cognition
normalization path. Given a valid raw provider response, the live readonly
governed runtime now reliably:

1. captures the raw provider response (provider-agnostic),
2. extracts and validates it into a bounded cognition proposal under strict
   deterministic discipline,
3. routes the bounded proposal through the existing governed cognition
   review, authorization, routing, isolation, and governed return path,
4. surfaces `status=SUCCESS` from the operator CLI.

It is strictly a stabilization milestone: NO new providers, capabilities,
write execution, orchestration, async runtime, retries, autonomous
execution, runtime mutation, provider mutation, agent behavior, or
planning systems are introduced.

It exposes:

- `BoundedExtractionEvidence`
- `extract_bounded_cognition_proposal(...)`
- `reconstruct_bounded_extraction_lineage(...)`
- Deterministic raw provider response fixtures
  (`aigol/runtime/raw_provider_response_fixtures.py`)
- New diagnostic fields on `LiveCognitionRejectionAnalysisEvidence`
  (`bounded_extraction_status`, `bounded_extraction_stage`,
  `bounded_extraction_reason`, `bounded_extraction_evidence_hash`,
  `normalization_failure_type`, `schema_failure_type`)
- A new `extraction_evidence_hash` field on
  `LiveOpenAIRuntimeConnectorEvidence` linking the connector lineage to
  the bounded extraction lineage
- Operator CLI status `SUCCESS` (renamed from `COMPLETED`)
- A new `BOUNDED_EXTRACTION` rejection stage in
  `LiveCognitionRejectionAnalysisEvidence`

## Bounded Extraction Discipline

The bounded extraction layer enforces:

- raw provider output -> bounded JSON extraction -> schema validation
  -> bounded proposal normalization

Strictly one-shot deterministic parsing. The layer:

- rejects empty responses (`EMPTY_RESPONSE`)
- rejects mixed prose + JSON (`MIXED_CONTENT`)
- rejects invalid JSON (`INVALID_JSON`)
- rejects non-object JSON (`NON_JSON_OBJECT`)
- rejects schema-drifted bounded proposals (`MISSING_FIELDS` / `EXTRA_FIELDS`)
- rejects invalid field types (`INVALID_FIELD_TYPE`)
- rejects disallowed proposal types (`INVALID_PROPOSAL_TYPE`)
- rejects unauthorized capability escalations (`UNAUTHORIZED_CAPABILITY`)
- rejects invalid contract references (`INVALID_CONTRACT_REFERENCE`)

No permissive heuristics, repair logic, retries, fuzzy parsing, or
AI-assisted correction are permitted.

Only normalized `BoundedCognitionProposal` artifacts cross this
boundary into governance.

## Deterministic Replay Fixtures

The fixture module
[`aigol/runtime/raw_provider_response_fixtures.py`](../aigol/runtime/raw_provider_response_fixtures.py)
provides append-only deterministic raw provider response strings that
contain only constant literal payloads, no runtime-generated timestamps,
and no network dependency. Required fixtures:

- `valid_bounded_proposal`
- `malformed_json`
- `mixed_prose_and_json`
- `schema_drift`
- `partial_bounded_proposal`
- `invalid_capability_escalation`
- `empty_response`
- `non_json_object`

Each fixture carries an `EXPECTED_OUTCOMES` annotation defining the
deterministic extraction status, stage, and failure classification that
the bounded extraction layer must emit.

## Operator CLI SUCCESS Path

The operator CLI was renamed from `CLI_COMPLETED = "COMPLETED"` to
`CLI_SUCCESS = "SUCCESS"`. When invoked with a valid raw provider response
(via the deterministic fixture set), it now returns:

```
status=SUCCESS
return=operation=inspect_runtime ...
cli_evidence_hash=sha256:...
operator_usage_evidence_hash=sha256:...
activation_evidence_hash=sha256:...
```

The successful path preserves:

- replay lineage continuity (bounded extraction hash, raw provider response hash, connector hash, operator usage hash, CLI hash)
- production isolation continuity (`ISOLATED`)
- governed return continuity (`ACCEPTED`)
- readonly capability containment (`metadata_inspection_provider.inspect_runtime` only)
- deterministic evidence hashing (round-trippable canonical evidence)

No write capability, shell execution, subprocess expansion, filesystem
mutation, or external side effect is introduced.

## Replay-Visible Diagnostics

Diagnostic fields added to the rejection analyzer evidence:

- `bounded_extraction_status` — `NORMALIZED` / `REJECTED` / `ABSENT`
- `bounded_extraction_stage` — extraction pipeline stage that was reached
- `bounded_extraction_reason` — verbatim extraction layer reason
- `bounded_extraction_evidence_hash` — hash link to the extraction lineage
- `normalization_failure_type` — `NONE` / `EMPTY_RESPONSE` / `INVALID_JSON` / `MIXED_CONTENT` / `NON_JSON_OBJECT`
- `schema_failure_type` — `NONE` / `MISSING_FIELDS` / `EXTRA_FIELDS` / `INVALID_FIELD_TYPE` / `INVALID_PROPOSAL_TYPE` / `UNAUTHORIZED_CAPABILITY` / `INVALID_CONTRACT_REFERENCE` / `BOUNDED_PROPOSAL_CONSTRUCTION`

Strictly replay-visible evidence — NO telemetry systems, monitoring
systems, metrics aggregation, or observability platforms are introduced.

## Provider-Agnostic Core Discipline

`aigol.runtime.bounded_extraction_layer`,
`aigol.runtime.raw_provider_response_capture`, and
`aigol.runtime.raw_provider_response_fixtures` are AiGOL core modules
that contain no OpenAI/Anthropic/Claude/GPT identifier. The OpenAI
adapter is the only place that knows about OpenAI's API surface.
Future Claude or local provider adapters can wrap the same bounded
extraction layer without touching AiGOL core.

## Guarantees

- Provider-agnostic cognition normalization
- Deterministic extraction discipline
- Fail-closed normalization
- Replay-visible bounded extraction evidence (lineage + hash)
- Bounded cognition contract preservation
- Operator CLI status=SUCCESS on the successful path

## Non-Goals

- New providers
- New capabilities
- Write execution
- Orchestration
- Async runtime
- Retries
- Autonomous execution
- Runtime mutation
- Provider mutation
- Agent behavior
- Planning systems

## Certification

`LIVE_PROVIDER_NORMALIZATION_SUCCESS_V1` certifies the first successful
real governed cognition normalization path under deterministic bounded
extraction discipline, provider-agnostic AiGOL core, replay-visible
extraction evidence, fail-closed normalization, and bounded cognition
contract preservation — without introducing new providers, new
capabilities, write execution, orchestration, async runtime, retries,
autonomous execution, runtime mutation, or provider mutation.
