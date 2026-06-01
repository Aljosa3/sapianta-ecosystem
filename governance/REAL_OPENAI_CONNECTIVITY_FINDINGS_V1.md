# Real OpenAI Connectivity Findings V1

Status: findings from factual proof-of-connectivity review.

## Findings

1. `OPENAI_API_KEY` is present in the runtime environment.

   Evidence: local environment check returned `OPENAI_API_KEY_PRESENT=TRUE` and `OPENAI_API_KEY_LENGTH=164`. The key value was not printed or persisted.

2. The API key originates from the process environment.

   Evidence: `aigol/provider/providers/openai_provider.py` defines `OPENAI_API_KEY_ENV = "OPENAI_API_KEY"` and `_resolve_api_key(...)` reads `os.environ.get(OPENAI_API_KEY_ENV)` when no explicit key is injected.

3. AiGOL can initialize the OpenAI provider adapter.

   Evidence: live proof run constructed `OpenAIProviderAdapter(timeout_seconds=20)` and registered `openai_provider_metadata()` in `ProviderRegistry`.

4. AiGOL sent a real OpenAI provider request.

   Evidence: live replay recorded endpoint `https://api.openai.com/v1/responses`, model `gpt-5.1`, `stream=false`, and the proof prompt payload. The adapter default client performs an HTTP POST to that endpoint.

5. AiGOL received a real OpenAI provider response.

   Evidence: replay recorded raw response id `resp_02aefc54f17190e6006a1d499ad4dc819cbfde31d6905b008f`, raw response object `response`, status `completed`, resolved model `gpt-5.1-2025-11-13`, and total token usage `61`.

6. AiGOL recorded replay-visible evidence.

   Evidence: replay files were written under `/tmp/real_openai_connectivity_sfnhm8np`:

   - `000_provider_proposal_created.json`
   - `001_provider_proposal_returned.json`

7. AiGOL reconstructed the interaction from replay.

   Evidence: `reconstruct_provider_attachment_replay(...)` returned `provider_invoked=true` and `replay_artifact_count=2`.

8. The proof run is distinguishable from test doubles.

   Evidence: no injected client was passed to `OpenAIProviderAdapter`; the adapter therefore used `OpenAIHTTPClient`. The observed replay includes live OpenAI response metadata that is absent from static fake-client tests.

## Boundary Finding

A first non-escalated sandbox attempt failed closed with:

```text
failure_reason = OpenAI provider unavailable
provider_invoked = false
```

That attempt is not used as connectivity proof. It is retained only as evidence that restricted network conditions fail closed.

