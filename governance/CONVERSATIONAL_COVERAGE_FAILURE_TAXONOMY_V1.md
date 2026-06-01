# Conversational Coverage Failure Taxonomy V1

Status: failure taxonomy from the 50-prompt epoch.

## Taxonomy

| Failure category | Cases | Count | Percent of failures | Evidence |
| --- | --- | ---: | ---: | --- |
| Intent classification provider-unavailable | 6-10, 16-18, 23-26, 28-34, 37-40, 43-49 | 30 | 68.2% | `response_failure = provider-assisted conversation failed closed: OpenAI provider unavailable` |
| Provider activation unavailable | 11-15, 20, 22, 27, 35, 50 | 10 | 22.7% | `provider_event = FAILED_CLOSED`, `provider_invoked = false`, `provider_failure = OpenAI provider unavailable` |
| Response validation over-block | 5, 41, 42 | 3 | 6.8% | `conversation response validation failed closed: authority-bearing response` |
| Non-conversation intent | 36 | 1 | 2.3% | Classified as `CONSTITUTIONAL_MEMORY_CONSULTATION`; prompt-to-conversation rejected it as not conversation intent |

## Prompt Category Outcomes

| Prompt category | Cases | Outcome |
| --- | --- | --- |
| Simple AiGOL identity | 1, 2 | Succeeded |
| Simple replay explanation | 3, 21 | Succeeded |
| Simple governance explanation | 4, 19 | Succeeded |
| Operational/component explanation | 11-14, 38-40 | Failed: provider unavailable or intent classification provider-unavailable |
| Progress/current status/history | 15-17, 20, 35, 45, 46 | Failed: provider unavailable or intent classification provider-unavailable |
| Replay ledger/last result evidence | 33, 34, 44 | Failed: intent classification provider-unavailable |
| Multilingual/Slovenian | 8, 47-50 | Failed: provider unavailable or intent classification provider-unavailable |
| Ambiguous/minimal prompts | 26, 27 | Failed: intent classification provider-unavailable or provider activation unavailable |
| Unsupported action/generation prompts | 28-32 | Failed closed before provider response |
| Authority/worker isolation explanations | 5, 41, 42 | Failed: response validation over-block |
| Constitutional Memory | 36, 37 | One non-conversation classification; one intent classification provider-unavailable |

## Per-Question Evidence Answers

### Classified Successfully

20 prompts classified successfully at the prompt level.

Destinations:

- `CONVERSATION`: 19
- `CONSTITUTIONAL_MEMORY_CONSULTATION`: 1

### Classified Unsuccessfully

30 prompts failed prompt-level classification.

### Routed Successfully

20 prompts routed successfully.

Destinations:

- `CONVERSATION`: 19
- `CONSTITUTIONAL_MEMORY_CONSULTATION`: 1

### Routed Unsuccessfully

30 prompts had failed routing because classification failed.

### Invoked Provider

0 prompts actually invoked the provider during the epoch.

10 prompts created provider proposal artifacts, but those artifacts were `FAILED_CLOSED` with `provider_invoked = false`.

### Received Provider Response

0 prompts received a provider response during the epoch.

### Failed Before Provider Response

44 failed prompts failed before provider response.

