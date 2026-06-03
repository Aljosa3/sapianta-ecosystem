# AIGOL_LAYER_DEFINITIONS_V1

## Status

Canonical layer definitions.

## Single-Sentence Constitutional Definitions

```text
COGNITION = "Transforms human intent into structured understanding without creating authority."
```

```text
RESOURCE_SELECTION = "Chooses an eligible Resource and explicit active role without invoking, authorizing, or executing it."
```

```text
PPP = "Turns structured intent and selected Resources into proposal, validation, approval, repair, and handoff artifacts without becoming governance or execution."
```

```text
GOVERNANCE = "Determines admissibility, approval, authorization, and certification while preserving constitutional and replay boundaries."
```

```text
EXECUTION = "Performs only explicitly authorized bounded work and returns replay-visible result evidence."
```

## COGNITION

What it is:

An intent-understanding and context-preparation layer.

Purpose:

Transform human prompts into structured, replay-visible understanding.

Authority it has:

- classify intent;
- preserve conversation continuity;
- create task intake evidence;
- assemble context;
- identify ambiguity;
- fail closed.

Authority it does not have:

- select Resources authoritatively;
- produce provider proposals as authority;
- approve;
- authorize;
- dispatch;
- execute;
- mutate governance.

Primary artifacts:

- human prompt artifact;
- intent classification artifact;
- conversation response artifact;
- native development task intake artifact;
- development context assembly artifact.

Previous layer:

```text
Human
```

Next layer:

```text
RESOURCE_SELECTION
```

## RESOURCE_SELECTION

What it is:

A deterministic eligibility and role-selection layer for Providers, Workers, and Hybrid Provider-Workers.

Purpose:

Choose which Resource role may be used by the downstream workflow.

Authority it has:

- evaluate capability compatibility;
- evaluate category compatibility;
- evaluate role compatibility;
- evaluate trust compatibility;
- evaluate authority compatibility;
- emit selected Resource evidence.

Authority it does not have:

- invoke provider;
- invoke Worker;
- dispatch;
- execute;
- approve;
- authorize;
- generate proposal.

Primary artifacts:

- `RESOURCE_SELECTION_ARTIFACT_V1`;
- `RESOURCE_SELECTION_STATUS_V1`;
- `RESOURCE_SELECTION_DIAGNOSTICS_V1`;
- `RESOURCE_PPP_INTEGRATION_ARTIFACT_V1`.

Previous layer:

```text
COGNITION
```

Next layer:

```text
PPP
```

## PPP

What it is:

A proposal production, validation, repair, clarification, approval-surfacing, and implementation handoff pipeline.

Purpose:

Move a structured task from intent and selected Resource evidence into proposal-only implementation handoff artifacts.

Authority it has:

- prepare provider request packets;
- capture provider proposal evidence where permitted;
- validate proposals against contract;
- request repair/retry;
- surface clarification;
- surface approval requirement;
- create implementation handoff artifacts.

Authority it does not have:

- interpret raw human intent independently of Cognition;
- select Resources independently of Resource Selection;
- govern final admissibility;
- authorize implementation;
- invoke Workers;
- dispatch;
- execute;
- mutate governance.

Primary artifacts:

- provider request packet;
- provider response artifact;
- development proposal artifact;
- proposal validation artifact;
- retry artifact;
- clarification or approval-required artifact;
- implementation handoff artifact.

Previous layer:

```text
RESOURCE_SELECTION
```

Next layer:

```text
GOVERNANCE
```

## GOVERNANCE

What it is:

The validation, admissibility, approval, authorization, certification, and boundary enforcement layer.

Purpose:

Determine whether proposal, handoff, lifecycle, or execution artifacts may advance.

Authority it has:

- validate;
- approve;
- reject;
- certify;
- authorize;
- fail closed;
- preserve constitutional constraints.

Authority it does not have:

- act as provider;
- act as Worker;
- execute domain work;
- silently mutate replay;
- bypass human authority.

Primary artifacts:

- governance review artifacts;
- approval artifacts;
- authorization artifacts;
- certification artifacts;
- rejection artifacts;
- fail-closed evidence.

Previous layer:

```text
PPP
```

Next layer:

```text
EXECUTION
```

## EXECUTION

What it is:

The bounded Worker action layer.

Purpose:

Perform authorized, scoped, replay-visible work only after Governance authorization.

Authority it has:

- execute authorized task packet;
- return result evidence;
- terminate;
- fail closed on mismatch.

Authority it does not have:

- propose;
- select Resources;
- approve;
- authorize;
- govern;
- self-dispatch;
- mutate governance;
- mutate replay.

Primary artifacts:

- Worker assignment artifact;
- dispatch artifact;
- Worker invocation artifact;
- execution result artifact;
- termination evidence.

Previous layer:

```text
GOVERNANCE
```

Next layer:

```text
Replay
```

