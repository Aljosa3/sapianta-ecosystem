# HUMAN_PROMPT_REPLAY_MODEL_V1

## Replay Principle

The Human Prompt must be replay-visible before downstream action occurs.

## Required Prompt Replay Fields

A future prompt replay record should include:

- prompt id;
- prompt text hash;
- prompt timestamp;
- operator context;
- intent classification reference;
- routing reference;
- provider requirement decision;
- downstream proposal id if applicable;
- downstream authorization id if applicable;
- downstream operation id if applicable;
- explanation id or explanation hash if applicable.

## Replay Links

The Human Prompt should link to:

```text
Human Prompt Artifact
↓
Intent Classification Artifact
↓
Routing Artifact
↓
Provider Proposal Envelope
↓
Authorization Artifact
↓
Worker Replay
↓
Replay Verification
↓
Replay-Backed Explanation
```

Only the relevant branch should exist for a given prompt.

## Explanation Linkage

Replay-backed explanations should cite:

- prompt id;
- operation id;
- proposal id;
- authorization id;
- worker id;
- verification status;
- supporting replay files.

## Fail-Closed Replay Rules

Fail closed on:

- missing prompt artifact;
- ambiguous prompt without clarification;
- missing intent artifact;
- missing routing evidence;
- missing downstream replay;
- verification failure.

No Human Prompt path should silently bypass replay.
