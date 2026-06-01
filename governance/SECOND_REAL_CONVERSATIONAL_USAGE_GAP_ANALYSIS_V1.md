# SECOND_REAL_CONVERSATIONAL_USAGE_GAP_ANALYSIS_V1

## Gap Matrix

| Gap | Severity | Evidence | Impact |
| --- | --- | --- | --- |
| Provider unavailable for real prompt fallback | High | 10 prompts reached `OpenAI provider unavailable`; many others failed provider-assisted classification | Natural language coverage remains low |
| Deterministic self-resolution coverage too narrow | High | Only 6 of 50 prompts answered | AiGOL cannot yet answer common project questions |
| Prompt-to-replay question routing missing | High | Last operation, replay ledger, replay report, and failure prompts failed | AiGOL cannot answer operational evidence questions conversationally |
| Component explanation coverage missing | Medium | Provider-assisted intent classification, conversation runtime, Constitutional Memory explanation prompts failed | Project self-explanation remains incomplete |
| Response validator over-blocks authority terminology | Medium | Authority and worker isolation prompts failed despite being safe explanatory questions | Governance explanations are blocked by coarse text checks |
| Failure explanations too thin | Medium | Failures show terse internal reasons | Operator does not receive high-quality explanation of what failed |
| Unsupported prompt explanations missing | Medium | Flight, browser, poem, and file creation prompts fail without helpful response | Safe behavior exists but user guidance is weak |
| Multilingual deterministic coverage missing | Medium | Slovenian prompts failed without provider | Non-English usage requires provider or deterministic multilingual rules |

## Authority Impact

No observed gap requires authority expansion.

All next steps can preserve:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Replay Impact

Replay quality is medium:

- replay roots are created;
- prompt, classification, routing, and conversation evidence are persisted;
- operator output does not yet summarize replay evidence well.

## Provider Impact

Provider fallback exists architecturally but was not useful operationally in
this epoch because no live provider response was available.

## Worker Impact

Worker execution remained isolated.

No worker expansion is justified by this epoch.
