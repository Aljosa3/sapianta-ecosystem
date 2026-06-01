# SECOND_REAL_CONVERSATIONAL_USAGE_FINDINGS_V1

## Findings Summary

AiGOL can now answer a narrow set of direct project/governance questions through
`aigol prompt submit`.

The system is not yet broadly conversational.

## Can AiGOL Answer Project Questions?

Classification: `PARTIAL`

Successful:

- identity questions;
- simple replay explanation;
- simple governance explanation.

Unsuccessful:

- recent progress;
- current status;
- component-specific questions;
- last-operation evidence;
- trust/explanation questions.

## Can AiGOL Explain Governance?

Classification: `PARTIAL_HIGH`

It answered direct governance explanation prompts well.

It failed on more specific authority and worker-isolation governance prompts
because deterministic response validation over-blocked text containing
authority-related terms.

## Can AiGOL Summarize Progress?

Classification: `LOW`

Progress prompts failed without provider assistance.

No current runtime summary was consulted.

## Can AiGOL Explain Replay?

Classification: `PARTIAL_HIGH`

Direct replay explanation succeeded.

Replay-ledger or last-operation replay questions failed because prompt-to-replay
operation routing is not integrated.

## Can AiGOL Explain Failures?

Classification: `LOW`

Failure-related prompts failed closed or required provider assistance.

The CLI reports fail-closed status, but not a rich human explanation.

## Can AiGOL Answer Without Provider?

Classification: `YES_BUT_NARROW`

Successful answers were all self-resolution responses.

Observed successful response rate:

```text
6 / 50 = 12%
```

## When Is Provider Required?

Provider is currently required for:

- natural-language paraphrases outside deterministic markers;
- Slovenian prompts;
- recent progress summaries;
- replay history questions;
- component-specific explanations;
- unsupported prompt explanation.

Because no live provider was available during the epoch, these failed closed.

## When Are Responses Poor?

Responses are poor or unavailable when:

- prompt classification fails;
- provider fallback is unavailable;
- self-resolution lacks domain coverage;
- response validation blocks safe authority-related explanatory text;
- the prompt asks for replay/history context not connected to conversation.

## Most Important Finding

The next bottleneck is not the prompt-to-response pipe.

That pipe now exists.

The next bottleneck is answer coverage:

- deterministic self-resolution knowledge is too small;
- provider fallback is operationally unavailable in this run;
- replay-backed explanation is not connected to conversation prompts.
