# MINIMAL_HUMAN_PROMPT_INTERFACE_V1

## Status

`MINIMAL_HUMAN_PROMPT_INTERFACE_STATUS = READY`

## Purpose

This milestone implements the first direct Human Prompt Interface for AiGOL.

It replaces the first manual transport step:

```text
Human
↓
ChatGPT
↓
Prompt
↓
Copy/Paste
```

with:

```text
Human
↓
AiGOL Prompt Interface
```

## Runtime Surface

Implemented:

```text
aigol/runtime/minimal_human_prompt_interface.py
```

CLI surface:

```text
python -m aigol.cli.aigol_cli prompt submit \
  --prompt "Explain how AiGOL preserves replay."
```

## Governed Flow

The implemented minimal flow is:

```text
Human Prompt
↓
Human Prompt Artifact
↓
Intent Classification
↓
Intent Routing Attachment
↓
Prompt Lineage
↓
Replay
```

This enters the existing cognition path through intent classification and routing evidence.

It does not activate provider, worker, authorization, execution, memory retrieval, orchestration, planning, or autonomous dispatch.

## Replay Evidence

Replay reconstructs:

- prompt id;
- prompt text;
- prompt hash;
- timestamp;
- intent classification;
- routing decision;
- prompt lineage.

## Observed Smoke Evidence

Command:

```text
python -m aigol.cli.aigol_cli prompt submit \
  --prompt "Explain how AiGOL preserves replay." \
  --runtime-root /tmp/aigol_prompt_interface_runtime
```

Result:

```text
prompt_status = HUMAN_PROMPT_ACCEPTED
classification_destination = CONVERSATION
routing_destination = CONVERSATION
cognition_path_entered = True
provider_invoked = False
worker_invoked = False
execution_requested = False
```

## Boundary

This milestone does not introduce:

- new provider;
- new worker;
- new authorization model;
- new replay model;
- orchestration;
- planning;
- autonomous dispatch.

## Final Classification

```text
MINIMAL_HUMAN_PROMPT_INTERFACE_STATUS = READY
```
