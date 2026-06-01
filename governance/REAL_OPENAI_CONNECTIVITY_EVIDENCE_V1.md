# Real OpenAI Connectivity Evidence V1

Status: replay-safe evidence record.

## Evidence Matrix

| Claim | Status | Explicit source |
| --- | --- | --- |
| `OPENAI_API_KEY_PRESENT` | `TRUE` | Environment probe: `OPENAI_API_KEY_PRESENT=TRUE`, `OPENAI_API_KEY_LENGTH=164`. |
| API key origin | `TRUE` | Source: `aigol/provider/providers/openai_provider.py`, `OPENAI_API_KEY_ENV = "OPENAI_API_KEY"` and `_resolve_api_key(...)`. |
| `OPENAI_PROVIDER_INITIALIZED` | `TRUE` | Live proof run: `OpenAIProviderAdapter(timeout_seconds=20)`, `openai_provider_metadata()`, `ProviderRegistry.register_provider(...)`. |
| `REAL_REQUEST_SENT` | `TRUE` | Replay created artifact: endpoint `https://api.openai.com/v1/responses`, model `gpt-5.1`, prompt payload, `single_request=true`, `streaming=false`. |
| `REAL_RESPONSE_RECEIVED` | `TRUE` | Replay created artifact: raw response id `resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f`, object `response`, status `completed`, usage `61` total tokens. |
| `REPLAY_RECORDED` | `TRUE` | Replay files in `/tmp/real_openai_connectivity_sfnhm8np`, replay indexes `0` and `1`, replay hashes present. |
| `REPLAY_RECONSTRUCTABLE` | `TRUE` | Reconstruction output: `reconstruct_provider_invoked=true`, `reconstruct_replay_artifact_count=2`. |

## Live Request Evidence

Replay-created request excerpt:

```json
{
  "provider": "openai",
  "endpoint": "https://api.openai.com/v1/responses",
  "model": "gpt-5.1",
  "payload": {
    "input": "For connectivity proof, reply with one short sentence that includes SAPIANTA_OPENAI_CONNECTIVITY_PROOF.",
    "model": "gpt-5.1",
    "stream": false
  },
  "api_key_captured": false,
  "single_request": true,
  "streaming": false,
  "tool_use": false,
  "function_calling": false,
  "memory": false
}
```

## Live Response Evidence

Replay-created response excerpt:

```json
{
  "provider": "openai",
  "provider_version": "openai-responses-v1",
  "model": "gpt-5.1",
  "raw_response_hash": "sha256:492da3c498308e821b4d51f1051070a5384bbcaa5377e1f0631069072c8ee92a",
  "raw_response": {
    "id": "resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f",
    "object": "response",
    "status": "completed",
    "model": "gpt-5.1-2025-11-13",
    "usage": {
      "input_tokens": 27,
      "output_tokens": 34,
      "total_tokens": 61
    }
  },
  "response_text_present": true,
  "streaming": false,
  "tool_use": false,
  "function_calling": false,
  "memory": false
}
```

## Replay Evidence

Created artifact:

```json
{
  "replay_step": "provider_proposal_created",
  "replay_index": 0,
  "replay_hash": "sha256:20856303d499cdeca670c318d28d958c4cb28af992cc32ab9b4acd0c4164d470",
  "artifact_hash": "sha256:045b3c03655441d7da15c8b32c68748963e71460009cb82fe3ce5ffe1a155557",
  "proposal_hash": "sha256:08e2fa75977f035182242578df5408ade0748906f05ce42c4dc0522c6b1a7c44",
  "provider_invoked": true
}
```

Returned artifact:

```json
{
  "replay_step": "provider_proposal_returned",
  "replay_index": 1,
  "replay_hash": "sha256:c0c4bbf988d912a8fe6fbf3389b580613c76865fe103f8c710896edaf33318cd",
  "artifact_hash": "sha256:c060b25e3da07a7d460fce7d373f8a25ad4f4a5bfb2270b1b24d49fc1c0fa83c",
  "created_hash": "sha256:045b3c03655441d7da15c8b32c68748963e71460009cb82fe3ce5ffe1a155557",
  "proposal_hash": "sha256:08e2fa75977f035182242578df5408ade0748906f05ce42c4dc0522c6b1a7c44",
  "provider_invoked": true,
  "failure_reason": null
}
```

## Non-Proof Evidence

Existing tests use injected fake clients and stubs. Those tests prove adapter behavior, fail-closed behavior, and replay behavior, but they are not used as proof of real OpenAI communication.

