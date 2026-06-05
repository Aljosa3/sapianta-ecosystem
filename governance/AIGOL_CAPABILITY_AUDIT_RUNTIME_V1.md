# AIGOL_CAPABILITY_AUDIT_RUNTIME_V1

## Status

Runtime implementation certification.

```text
AIGOL_CAPABILITY_AUDIT_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Convert the manual capability audit into a repeatable runtime.

The runtime scans local repository evidence and regenerates:

- `governance/AIGOL_CAPABILITY_AUDIT_V2.md`
- `governance/AIGOL_CAPABILITY_MATRIX_V2.json`
- `governance/AIGOL_ROADMAP_POST_AUDIT_V2.md`

## Runtime Scope

Scanned directories:

- `governance/`
- `aigol/runtime/`
- `tests/`

The runtime does not scan external services, network resources, package registries, or deployment targets.

## Classification Rules

Statuses:

- `CERTIFIED`
- `IMPLEMENTED`
- `PARTIAL`
- `NOT_STARTED`

Classification semantics:

- `CERTIFIED`: certification evidence is detected.
- `IMPLEMENTED`: runtime implementation and tests are detected without certification evidence.
- `PARTIAL`: local governance, runtime, test, or replay evidence exists but stronger criteria are not met.
- `NOT_STARTED`: explicit missing or planned capability is preserved as a missing capability.

`CERTIFIED` is never assigned without certification evidence.

## Runtime Implementation

Runtime file:

```text
aigol/runtime/capability_audit_runtime.py
```

Primary functions:

- `detect_capabilities`
- `build_capability_matrix`
- `classify_capability`
- `render_audit_document`
- `render_roadmap_document`
- `run_capability_audit`

CLI entrypoint:

```bash
python -m aigol.runtime.capability_audit_runtime /home/pisarna/work/sapianta
```

## Generated V2 Artifacts

The certified runtime generated:

- `governance/AIGOL_CAPABILITY_AUDIT_V2.md`
- `governance/AIGOL_CAPABILITY_MATRIX_V2.json`
- `governance/AIGOL_ROADMAP_POST_AUDIT_V2.md`

## Authority Boundaries

This runtime is audit-only.

It does not:

- authorize implementation;
- authorize execution;
- authorize dispatch;
- invoke providers;
- invoke workers;
- mutate governance semantics;
- upgrade partial evidence into full conformance;
- hide missing capabilities.

## Certification Evidence

Certification artifact:

```text
governance/AIGOL_CAPABILITY_AUDIT_RUNTIME_V1_CERTIFICATION.json
```

Test file:

```text
tests/test_capability_audit_runtime_v1.py
```

Certified test coverage:

- detection of capabilities;
- evidence file detection;
- `CERTIFIED` classification;
- `IMPLEMENTED` classification;
- `PARTIAL` classification;
- `NOT_STARTED` classification;
- V2 audit generation;
- V2 matrix generation;
- V2 roadmap generation;
- certified classification requiring certification evidence.

## Success Criteria

AiGOL can re-run its own capability audit after every milestone by executing:

```bash
python -m aigol.runtime.capability_audit_runtime /home/pisarna/work/sapianta
```

