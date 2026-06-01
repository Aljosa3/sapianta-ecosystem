# FIRST_REAL_WORKFLOW_DISCOVERY_ADR_V1

## Decision

Adopt AiGOL first for bounded governance-file creation and replay verification workflows.

Prioritize replay/operator reporting before expanding providers or workers.

## Context

AiGOL MVP is operational through:

- `aigol run-governed`;
- replay operation inspection;
- replay verification;
- bounded filesystem create-file execution.

Weekly usage showed successful replay is valuable, but aggregate operational visibility remains manual.

## Decision Rationale

The strongest current workflows are those where AiGOL can provide:

- useful execution;
- clear authorization scope;
- replay-visible evidence;
- high-quality human explanation;
- trust based on reconstructable replay.

New governance artifacts, ADR skeletons, usage logs, and evidence stubs fit this profile.

## Rejected Priorities

### Provider Expansion

Rejected for now.

External provider reliability was not measured in weekly usage.

### Worker Expansion First

Rejected for now.

The only observed repeated worker demand is create-file and replay verification/reporting.

### Orchestration Or Planning

Rejected.

No observed workflow requires orchestration, planning, reflection, or autonomous dispatch.

## Consequences

AiGOL should move from architecture-building to real workflow adoption.

The next implementation, if any, should improve replay/operator reporting so that workflow explanations become easier and more trustworthy.
