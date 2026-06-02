# AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_REPLAY_MODEL_V1

## Status

Review-only replay model.

## Replay Purpose

Development context assembly replay must allow an operator to reconstruct:

- which intake artifact was used;
- which context artifacts were selected;
- which context was missing;
- which context was ambiguous;
- which constraints were preserved;
- whether provider use was required, optional, or prohibited;
- why assembly succeeded or failed closed.

## Replay Steps

Recommended replay steps:

```text
000_development_context_assembly_started.json
001_development_context_artifacts_resolved.json
002_development_context_assembly_validated.json
003_development_context_assembly_recorded.json
004_development_context_assembly_returned.json
```

## Mandatory Replay Fields

Every replay wrapper must preserve:

- replay index;
- replay step;
- event type;
- artifact;
- replay hash.

Every assembly artifact must preserve:

- context assembly id;
- intake reference;
- intake hash;
- artifact references;
- artifact hashes;
- context status;
- provider necessity classification;
- failure reason if any;
- no-authority flags;
- artifact hash.

## Hash Requirements

Context hash must include:

- intake hash;
- ordered artifact references;
- ordered artifact hashes;
- required category list;
- missing context list;
- ambiguous context list;
- known gaps;
- provider necessity classification;
- context status.

Changing any referenced artifact or missing-context result must change the context hash.

## Missing Context Replay

Missing context must be recorded as data, not hidden in prose.

Each missing context entry should include:

- category;
- expected artifact id or pattern;
- required or advisory classification;
- fail-closed impact;
- reason missing.

## Ambiguous Context Replay

Each ambiguous context entry should include:

- category;
- candidate references;
- ambiguity reason;
- fail-closed impact.

## Provider Replay

Context assembly does not invoke providers.

If future proposal generation uses a provider, provider replay must reference the context assembly artifact hash. The provider must not become a source of context truth.

## Reconstruction

Reconstruction must fail closed on:

- missing replay step;
- replay ordering mismatch;
- wrapper hash mismatch;
- artifact hash mismatch;
- intake hash mismatch;
- artifact reference hash mismatch;
- context status/reference mismatch.

## Replay Visibility Classification

Development context assembly replay visibility:

```text
MANDATORY
```

