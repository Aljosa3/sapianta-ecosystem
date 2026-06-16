# AIGOL_ERR_V0

Status: experimental implementation milestone.

Purpose: prove that AiGOL can locate an external cognition provider or execution worker through a passive resource registry instead of hardcoded OCS routing.

## Architecture Summary

AIGOL_ERR_V0 introduces a minimal External Resource Registry runtime.

The registry supports only:

- resource registration;
- lookup by `resource_id`;
- lookup by declared capability;
- `ACTIVE` / `INACTIVE` status filtering;
- replay-visible evidence when OCS selects a resource through ERR.

Supported resource types are limited to:

- `COGNITION_PROVIDER`
- `EXECUTION_WORKER`

ERR does not execute, invoke, route, rank, optimize, schedule, authorize, govern, or mutate replay history.

Boundary invariant:

```text
Human = authority layer
OCS = orchestration layer
Providers = cognition only
Workers = execution only
ERR = passive resource metadata plus selection evidence
```

Providers may not invoke workers. Workers may not invoke providers. ERR may not invoke either.

## Minimal Schema

Each resource contains:

- `resource_id`
- `resource_type`
- `capabilities`
- `status`

No marketplace fields, ranking fields, cost fields, latency fields, lifecycle machinery, provider comparison fields, or autonomous discovery fields are included.

## Test Resources

ERR_V0 includes test-only defaults:

- `mock_provider`
  - type: `COGNITION_PROVIDER`
  - capability: `reasoning`
  - status: `ACTIVE`

- `mock_filesystem_worker`
  - type: `EXECUTION_WORKER`
  - capability: `file_write`
  - status: `ACTIVE`

No external API calls are made. No real provider or worker is invoked.

## Required Demonstration Workflow

The demonstration workflow is:

```text
Human Intent
-> HIRR output
-> required_capability = reasoning
-> ERR capability lookup
-> mock_provider selected
-> replay evidence recorded
```

This proves only that OCS can locate a provider through ERR without hardcoding a provider reference into OCS.

## Replay Evidence

`select_resource_for_capability(...)` records append-only replay evidence:

- `000_err_resource_selection_evidence_recorded.json`
- `001_err_resource_selection_returned.json`

The replay evidence records:

- selected resource id;
- selected resource type;
- required capability;
- active match ids;
- registry hash;
- optional human intent and HIRR output;
- boundary flags showing no provider invocation, worker invocation, orchestration, governance mutation, or replay mutation.

## Remaining Gaps

ERR_V0 intentionally does not implement:

- marketplace behavior;
- ranking;
- cost or latency optimization;
- dynamic routing;
- ELL runtime;
- attachment lifecycle;
- provider comparison;
- autonomous discovery;
- domain integrations;
- advanced governance.

## ELL Recommendation

ERR_V0 covers the immediate architectural question: OCS can discover a provider or worker by capability without hardcoded resource references.

ELL should not be implemented as a separate runtime layer yet. The next decision should be deferred until ERR_V0 is exercised against a real OCS call site. If future work needs execution lifecycle semantics, attachment state, streaming, provider invocation, or cross-resource coordination, that may justify a separate ELL. At this milestone, ELL would be premature and would risk duplicating or bypassing ERR's passive registry boundary.
