# Real OpenAI Connectivity Proof V1

Status: factual proof-of-connectivity review.

Final classification:

```text
REAL_OPENAI_CONNECTIVITY_STATUS = READY
```

## Scope

This proof certifies only observable OpenAI API connectivity for AiGOL.

It does not certify provider architecture, governance redesign, provider normalization quality, fallback behavior, autonomous execution, or broader runtime readiness.

## Live Proof Run

Proof command executed the existing AiGOL OpenAI provider adapter through the existing provider attachment runtime:

```text
OpenAIProviderAdapter(timeout_seconds=20)
run_provider_attachment(provider_id="openai", ...)
reconstruct_provider_attachment_replay(...)
```

The run used the adapter default HTTP client. No fake client, mock provider, stub, or static response was injected.

Replay directory:

```text
/tmp/real_openai_connectivity_sfnhm8np
```

Observed result:

```json
{
  "api_key_captured": false,
  "event_type": "PROVIDER_PROPOSAL_CREATED",
  "failure_reason": null,
  "model": "gpt-5.1",
  "provider_id": "openai",
  "provider_invoked": true,
  "provider_version": "openai-responses-v1",
  "raw_response_id": "resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f",
  "raw_response_hash": "sha256:492da3c498308e821b4d51f1051070a5384bbcaa5377e1f0631069072c8ee92a",
  "reconstruct_provider_invoked": true,
  "reconstruct_replay_artifact_count": 2,
  "response_text_present": true
}
```

## Required Evidence Status

| Evidence item | Status | Evidence |
| --- | --- | --- |
| `OPENAI_API_KEY_PRESENT` | `TRUE` | Local environment check returned `OPENAI_API_KEY_PRESENT=TRUE` and `OPENAI_API_KEY_LENGTH=164`. Adapter source resolves `OPENAI_API_KEY` from the process environment. |
| `OPENAI_PROVIDER_INITIALIZED` | `TRUE` | Live proof run initialized `OpenAIProviderAdapter(timeout_seconds=20)` and registered `openai_provider_metadata()`. Successful replay recorded `provider_id=openai`, `provider_version=openai-responses-v1`, `provider_status=AVAILABLE`. |
| `REAL_REQUEST_SENT` | `TRUE` | Replay artifact `000_provider_proposal_created.json` recorded endpoint `https://api.openai.com/v1/responses`, model `gpt-5.1`, `stream=false`, and the proof prompt payload. |
| `REAL_RESPONSE_RECEIVED` | `TRUE` | Replay artifact recorded raw OpenAI response id `resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f`, object `response`, status `completed`, model `gpt-5.1-2025-11-13`, usage `61` total tokens, and `raw_response_hash`. |
| `REPLAY_RECORDED` | `TRUE` | Replay files `000_provider_proposal_created.json` and `001_provider_proposal_returned.json` were written with replay hashes and artifact hashes. |
| `REPLAY_RECONSTRUCTABLE` | `TRUE` | `reconstruct_provider_attachment_replay(...)` returned `provider_invoked=true` and `replay_artifact_count=2`. |

## Distinguishability From Simulation

The proof interaction is distinguishable from mocks, simulations, fake providers, test doubles, and static responses because:

- the adapter was constructed without an injected `client`;
- the adapter source defaults to `OpenAIHTTPClient`;
- `OpenAIHTTPClient` performs a POST to `https://api.openai.com/v1/responses`;
- the replay contains an OpenAI response id beginning with `resp_`;
- the replay contains OpenAI response metadata including `object=response`, `status=completed`, dated resolved model `gpt-5.1-2025-11-13`, billing metadata, and token usage;
- the replay records `api_key_captured=false`, so the secret was not persisted.

## Fail-Closed Result

All required proof items are present.

Therefore:

```text
REAL_OPENAI_CONNECTIVITY_STATUS = READY
```

