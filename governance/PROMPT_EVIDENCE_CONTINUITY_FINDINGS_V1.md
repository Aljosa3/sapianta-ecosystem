# PROMPT_EVIDENCE_CONTINUITY_FINDINGS_V1

## Finding 1: Human Prompt Creation Is Replay-Visible

For all 34 failed or non-conversation fourth-epoch outcomes, the original
prompt was created and stored in:

```text
000_human_prompt_artifact.json
```

The artifact contains:

```text
prompt_text
prompt_hash
prompt_id
replay_visible = true
```

## Finding 2: Conversation Runtime Preserves Prompt Text When Entered

For 33 of 34 analyzed outcomes, the conversation response path was entered and
stored the prompt as:

```text
conversation_response/000_provider_assisted_conversation_started.json.artifact.prompt_text
```

The one exception was:

```text
What is Constitutional Memory?
```

which routed to `CONSTITUTIONAL_MEMORY_CONSULTATION` instead of the
conversation response path.

## Finding 3: Provider Receives Prompt Text In Payload Input

For the 29 `human_prompt is required` failures, OpenAI provider requests
included the prompt inside:

```text
request.payload.input
```

The payload contained the minimal context capsule and:

```text
Human prompt:
<original prompt>
```

Therefore the provider had enough text to answer. The failure occurred after
provider response generation, during validation/normalization.

## Finding 4: Structured `human_prompt` Is Lost At The Adapter Envelope Boundary

The provider-assisted classification normalizer expected:

```text
provider_proposal_envelope.request.human_prompt
```

The OpenAI adapter returned the envelope request as an OpenAI API request
record and did not preserve the original structured request fields.

Observed envelope request fields:

```text
provider
model
endpoint
payload
api_key_captured
single_request
streaming
tool_use
function_calling
memory
```

Missing fields:

```text
human_prompt
semantic_task
human_request_reference
allowed_destinations
```

## Finding 5: Replay Serialization Did Not Cause The Loss

Replay artifacts preserve:

- human prompt artifact;
- conversation start artifact;
- OpenAI payload input;
- provider response text;
- validation failure artifact.

The missing value is not absent from all replay. It is absent only from the
structured provider proposal envelope request shape consumed by classification
normalization.

## Finding 6: Prompt Evidence Can Be Reconstructed Without Changing Authority Boundaries

All failed prompts can be reconstructed from replay-visible evidence.

Restoring continuity would not require granting providers routing, execution,
governance, worker, or replay authority. The required change would be evidence
preservation across adapter boundaries, not authority transfer.
