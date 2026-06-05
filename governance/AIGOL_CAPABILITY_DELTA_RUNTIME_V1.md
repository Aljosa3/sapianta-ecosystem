# AIGOL_CAPABILITY_DELTA_RUNTIME_V1

## Status

Runtime implementation certification.

```text
AIGOL_CAPABILITY_DELTA_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Measure capability progress between audits.

The runtime compares:

- `governance/AIGOL_CAPABILITY_MATRIX_V1.json`
- `governance/AIGOL_CAPABILITY_MATRIX_V2.json`

and generates:

- `governance/AIGOL_CAPABILITY_DELTA_REPORT_V1.md`
- `governance/AIGOL_CAPABILITY_DELTA_V1.json`

## Runtime Scope

The runtime computes:

- added capabilities;
- removed capabilities;
- status changes;
- maturity changes;
- layer score deltas;
- `CERTIFIED` delta;
- `IMPLEMENTED` delta;
- `PARTIAL` delta;
- `NOT_STARTED` delta;
- top improvements;
- top regressions;
- recommended next milestone.

## Layer Normalization

The runtime reports layer deltas using:

- `L1 Governance`
- `L2 Cognition`
- `L3 Provider/Worker`
- `L4 Execution`
- `L5 Implementation`
- `L6 Domain Runtime`
- `L7 Marketplace`

Compatibility aliases:

- `L2 Cognition (OCS)` -> `L2 Cognition`
- `L5 Implementation Generation` -> `L5 Implementation`
- `L7 Marketplace / Ecosystem` -> `L7 Marketplace`

## Runtime Implementation

Runtime file:

```text
aigol/runtime/capability_delta_runtime.py
```

Primary functions:

- `compute_capability_delta`
- `render_delta_report`
- `run_capability_delta`
- `recommended_next_milestone`

CLI entrypoint:

```bash
python -m aigol.runtime.capability_delta_runtime governance/AIGOL_CAPABILITY_MATRIX_V1.json governance/AIGOL_CAPABILITY_MATRIX_V2.json governance
```

## Generated Delta Summary

Generated status deltas:

| Status | Delta |
| --- | ---: |
| `CERTIFIED` | +350 |
| `IMPLEMENTED` | +8 |
| `PARTIAL` | +1398 |
| `NOT_STARTED` | +0 |

Generated capability movement:

- added capabilities: 1784;
- removed capabilities: 28;
- status changes: 10;
- total capability delta: +1756.

Generated layer score deltas:

| Layer | Delta |
| --- | ---: |
| L1 Governance | -38 |
| L2 Cognition | -26 |
| L3 Provider/Worker | -22 |
| L4 Execution | -24 |
| L5 Implementation | +10 |
| L6 Domain Runtime | +2 |
| L7 Marketplace | +9 |

## Interpretive Boundary

The delta compares a manual V1 capability matrix with a runtime-generated V2 capability matrix.

Some added, removed, and regressed entries reflect audit granularity changes rather than runtime degradation. The runtime preserves those signals because schema/granularity drift is itself audit-relevant.

## Authority Boundaries

This runtime is comparison-only.

It does not:

- change capability status;
- certify capabilities by itself;
- hide regressions;
- mutate governance semantics;
- authorize implementation;
- authorize execution;
- invoke providers;
- invoke workers.

## Certification Evidence

Certification artifact:

```text
governance/AIGOL_CAPABILITY_DELTA_RUNTIME_V1_CERTIFICATION.json
```

Test file:

```text
tests/test_capability_delta_runtime_v1.py
```

Certified test coverage:

- added capability detection;
- removed capability detection;
- status improvement detection;
- status regression detection;
- status-count deltas;
- maturity changes;
- layer score deltas;
- layer alias normalization;
- report generation;
- JSON delta generation.

## Recommended Next Milestone

```text
AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1
```

Reason:

The first delta compares manual and automated audit schemas and surfaces regressions that require governance review before interpreting all deltas as product progress or product regression.

