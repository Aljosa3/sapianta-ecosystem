# AIGOL_WORKER_CAPABILITY_AUDIT_V1

## Status

Worker capability audit completed.

No new worker was implemented. No repair runtime was implemented. No domain creation was performed. No execution behavior or architecture was changed.

## Purpose

Audit the current worker layer after `AIGOL_REAL_HUMAN_DOMAIN_WORKFLOW_ACCEPTANCE_V1` reached:

```text
NEXT_BLOCKING_COMPONENT = CLARIFIED_DOMAIN_INTENT_TO_OCS_OR_EXECUTION_HANDOFF_REVIEW
```

The question for this milestone is whether the current worker layer can perform useful real tasks or whether FreshDomain remains blocked by missing worker capability.

## Worker Registry Discovery

The worker registry state is partial rather than a single canonical production registry.

Discovered worker and worker-family sources:

- `aigol/runtime/worker_runtime.py`: replay-visible generic worker registration and assignment runtime.
- `aigol/runtime/worker_assignment_runtime.py`: dynamic in-memory compatible worker candidate creation from an invocation request.
- `aigol/runtime/domain_and_worker_resolution_registry.py`: deterministic domain and worker-family registry.
- `aigol/workers/filesystem_worker.py`: bounded filesystem create-file worker.
- `aigol/workers/github_worker.py`: bounded GitHub issue draft domain worker.
- `aigol/runtime/replay_inspector_worker.py`: read-only replay inspector worker.
- `aigol/runtime/external_runtime_inspection_worker.py`: read-only external runtime inspection worker.
- `aigol/runtime/capabilities/capability_registry.py`: bounded capability allowlist.

Historical governance evidence also states that the canonical Worker registration process is partial, while worker identity, attachment, invocation, result capture, validation, replay review, and termination boundaries are implemented.

## Worker Classification

| Worker Or Registry Entry | Classification | Declared Capability | Production-Capable |
| --- | --- | --- | --- |
| `FILESYSTEM_CREATE_WORKER` | filesystem worker / proof worker | `CREATE_FILE` under `FILESYSTEM_CREATE_FILE` authorization | No; bounded local artifact creation only |
| `GITHUB_ISSUE_DRAFT_WORKER` | domain worker / external-adjacent draft worker | `CREATE_ISSUE_DRAFT` under `GITHUB_CREATE_ISSUE_DRAFT` authorization | Partial; creates draft artifacts, does not call GitHub or mutate repositories |
| `REPLAY_INSPECTOR_WORKER_V1` | proof/test worker / replay worker | read-only replay inspection scopes | Partial; useful for governance inspection, not business-domain execution |
| `EXTERNAL_RUNTIME_INSPECTION_WORKER` | external/integration worker | read-only runtime metadata inspection | Partial; inspection only |
| `AIGOL-WORKER-{target_worker_family}` | dynamic assignment candidate | request-derived worker role and allowed outputs | No; in-memory compatibility candidate, not a registered concrete capability |
| Domain worker families in `domain_and_worker_resolution_registry.py` | worker-family registry entries | Trading and server-management family metadata | No; family declarations, not executable domain workers |
| Runtime capability registry entries | capability controls | `read_text`, `inspect_json`, `analyze_text`, `mock_write_preview` | No; bounded capability primitives, not domain workers |

## Domain Artifact Capability Check

Required FreshDomain artifacts:

- domain definition artifact;
- domain metadata artifact;
- domain registration artifact;
- governance evidence artifact.

No discovered worker is certified to create the complete governed domain artifact set.

The filesystem worker can create a file, but it has no domain-definition schema, domain-registration authority, governance evidence contract, or FreshDomain-specific replay binding.

The GitHub worker can create a deterministic issue draft artifact, but its scope is GitHub issue draft creation, not governed domain registration.

The replay inspector and external runtime inspection workers are read-only and cannot create domain artifacts.

The dynamic assignment candidate mirrors the requested worker role for compatibility tests; it is not a durable production worker capability and does not define a domain creation contract.

## FreshDomain Continuation Assessment

FreshDomain cannot continue into an existing worker today.

The human workflow correctly reaches:

```text
WORKFLOW_RESUME_READY
Next Governed Workflow Stage: OCS_OR_EXECUTION_HANDOFF_REVIEW
```

However, the current worker layer has no worker whose declared input and output contracts accept clarified generic domain intent and produce governed domain definition, metadata, registration, and evidence artifacts.

## Missing Worker Capability Gaps

Critical:

- `GOVERNED_DOMAIN_ARTIFACT_AUTHORING_AND_REGISTRATION_WORKER_MISSING`

Important:

- no canonical worker capability entry for generic governed domain creation;
- no domain artifact output contract binding clarified intent to domain definition, metadata, registration, and governance evidence;
- canonical worker registry remains partial;
- dynamic in-memory workers are useful for chain compatibility but not production capability evidence.

Technical debt:

- worker metadata exists across multiple local contexts;
- worker capability declarations and executable worker identities are not unified into one canonical portfolio registry;
- a focused CLI worker-assignment acceptance test currently fails because the CLI turn lacks `worker_assignment_status`.

## Validation

Focused worker suites were run:

```text
python -m pytest tests/test_first_real_domain_worker_v1.py tests/test_replay_inspector_worker_v1.py tests/test_external_runtime_inspection_worker_v1.py tests/test_worker_runtime_v1.py tests/test_worker_assignment_runtime_v1.py tests/test_domain_and_worker_resolution_registry_v1.py
```

Result:

```text
86 passed, 1 failed
```

The failing test was:

```text
tests/test_worker_assignment_runtime_v1.py::test_cli_acceptance_flows_reach_worker_assigned
KeyError: 'worker_assignment_status'
```

This failure is recorded as a worker/CLI acceptance signal. It does not change the FreshDomain conclusion because FreshDomain is blocked earlier by the absence of a domain artifact worker capability.

## Recommendation

Minimal next milestone:

```text
AIGOL_GOVERNED_DOMAIN_ARTIFACT_WORKER_FOUNDATION_V1
```

This milestone should define, but not yet broaden authority beyond governance, the worker capability and artifact contracts for:

- clarified domain intent intake;
- domain definition artifact output;
- domain metadata artifact output;
- domain registration artifact output;
- governance evidence artifact output;
- replay lineage binding from clarification resume and OCS or execution handoff review;
- fail-closed rejection of ambiguous domain scope or authority escalation.

## Final Outputs

```text
WORKER_REGISTRY_DISCOVERED = PARTIAL
WORKER_CAPABILITIES_DISCOVERED = TRUE
PROOF_WORKERS_ONLY = FALSE
DOMAIN_CREATION_WORKER_EXISTS = FALSE
FRESHDOMAIN_CAN_CONTINUE_TO_EXISTING_WORKER = FALSE
TOP_WORKER_GAP = GOVERNED_DOMAIN_ARTIFACT_AUTHORING_AND_REGISTRATION_WORKER_MISSING
RECOMMENDED_NEXT_MILESTONE = AIGOL_GOVERNED_DOMAIN_ARTIFACT_WORKER_FOUNDATION_V1
READY_FOR_REAL_DOMAIN_CREATION_EXECUTION = FALSE
```
