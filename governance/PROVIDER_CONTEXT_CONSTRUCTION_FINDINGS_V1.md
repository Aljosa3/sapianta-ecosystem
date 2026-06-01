# Provider Context Construction Findings V1

Status: measured findings.

## Finding 1: OpenAI Receives Only Extracted Prompt Text

`OpenAIProviderAdapter.generate_proposal(...)` calls `_extract_prompt(request)` and then `_create_openai_payload(model=self.model, prompt=prompt)`.

`_extract_prompt(...)` accepts only:

- string request;
- `request["prompt"]`;
- `request["human_prompt"]`;
- `request["request"]`.

All other request fields are dropped before the OpenAI API call.

## Finding 2: AiGOL Builds More Context Than It Sends

Conversation response provider requests include:

- `semantic_task`;
- `prompt_id`;
- `human_prompt`;
- `intent_destination`;
- `self_resolution_status`;
- `self_resolution_reason`;
- `provider_authority`;
- `response_authority`;
- `execution_authority`.

Provider-assisted intent classification requests include:

- `semantic_task`;
- `human_prompt`;
- `human_request_reference`;
- `allowed_destinations`;
- `deterministic_classification_status`;
- `deterministic_failure_reason`;
- `provider_authority`;
- `routing_authority`;
- `execution_authority`.

These fields are replay-visible in provider attachment artifacts, but only `human_prompt` is transformed into OpenAI `payload.input`.

## Finding 3: Provider-Side AiGOL Context Is Missing

The OpenAI payload does not include:

- AiGOL identity;
- governance purpose;
- replay purpose;
- constitutional constraints;
- provider role;
- worker authority boundaries;
- project/domain context;
- expected answer contract;
- distinction between generic provider boundaries and AiGOL provider boundaries.

## Finding 4: Prompt Text Survives Fully

The human prompt itself survives fully into the provider prompt.

Example from the operator-supplied Platform Log:

```text
Human Prompt = Explain provider boundaries.
Provider Prompt = Explain provider boundaries.
```

This is `FULL_CONTEXT` for the literal prompt string, but `MINIMAL_CONTEXT` for the task.

## Finding 5: Poor Provider Answers Can Be Caused By Context Loss

For `Explain provider boundaries.`, the provider cannot know from the prompt alone whether the intended domain is:

- healthcare provider boundaries;
- professional services provider boundaries;
- cloud provider boundaries;
- AiGOL proposal-only LLM provider boundaries.

The operator-supplied Platform Log response about professional/healthcare provider boundaries is therefore consistent with missing AiGOL context, not provider malfunction.

## Finding 6: Context Construction Was Not The Measured Second-Epoch Bottleneck

The second 50-prompt epoch recorded zero actual provider invocations and zero provider responses.

Therefore, context construction cannot be certified as the primary measured bottleneck for that epoch.

It is a separate, now-visible bottleneck for post-connectivity provider answer quality.

