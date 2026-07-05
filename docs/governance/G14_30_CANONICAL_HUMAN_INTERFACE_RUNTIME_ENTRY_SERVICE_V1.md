# G14-30 Canonical Human Interface Runtime Entry Service V1

Status: canonical Human Interface runtime entry implemented.

Final verdict: CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_CERTIFIED

## 1. Executive Summary

G14-30 removes the remaining historical divergence between the reference Unified Human Interface and ACLI Next runtime entry paths.

The implementation introduces one canonical Platform Core runtime entry service:

```text
aigol/runtime/human_interface_runtime_entry_service.py
```

Both current Human Interfaces now delegate into this service:

* `aicli`
* `aigol next`

The service receives composed human requests, restores Platform Core project context, performs Development Intent Resolution through existing Platform Core services, enters the certified governed runtime when admissible, and records replay-visible workspace state.

Human Interface adapters remain thin. They collect input, render output, and collect approval only.

## 2. Canonical Runtime Entry

The canonical runtime path is now:

```text
Human
    |
Human Interface Adapter
    |
Canonical Human Interface Runtime Entry Service
    |
Platform Core Project Services
    |
Development Intent Resolution
    |
PGSP / UBTR / CSA
    |
Platform Core
    |
Governance
    |
Provider Platform
    |
Worker Platform
    |
Replay
```

The Human Interface Runtime Entry Service is implemented as:

```text
run_human_interface_runtime_entry(...)
```

The service is interface-independent. Future Web, Android, iOS, Voice, REST, Desktop, and other Human Interfaces can provide composed requests and delegate into the same entry service without copying runtime logic.

## 3. Updated Call Graph

### 3.1 Reference UHI (`aicli`)

```text
./aicli
    |
run_reference_uhi_session(...)
    |
/approve
    |
run_human_interface_runtime_entry(...)
    |
prepare_unified_human_interface_project_context(...)
    |
run_interactive_conversation(...)
    |
record_unified_human_interface_workspace_state(...)
```

`aicli` no longer owns a private `_run_certified_runtime(...)` wrapper.

### 3.2 ACLI Next

```text
python -m aigol.cli.aigol_cli next
    |
_run_acli_next_runtime_bound_session(...)
    |
run_human_interface_runtime_entry(...)
    |
prepare_unified_human_interface_project_context(...)
    |
run_interactive_conversation(...)
    |
record_unified_human_interface_workspace_state(...)
```

`aigol next` preserves its presentation layer but no longer implements its own runtime-entry branch for Project Services, prompt selection, conversation execution, or workspace recording.

## 4. Responsibility Matrix

| Capability | Owner | G14-30 Status |
| --- | --- | --- |
| Terminal input and output | Human Interface adapter | Preserved |
| Multi-line composition | `aicli` adapter | Preserved as UI-only |
| ACLI Next presentation | ACLI Next adapter | Preserved as presentation-only |
| Project Workspace restoration | Platform Core Project Services | Centralized through runtime entry |
| Project Guidance | Platform Core Project Services | Centralized through runtime entry |
| Knowledge Reuse | Platform Core Project Services | Centralized through runtime entry |
| Development Intent Resolution | Platform Core Project Services | Centralized through runtime entry |
| Runtime binding | Canonical Human Interface Runtime Entry Service | Shared by all interfaces |
| Governed runtime execution | Platform Core / OCS | Preserved |
| Authorization | Governance | Preserved |
| Provider invocation | Provider Platform | Preserved |
| Worker execution | Worker Platform | Preserved |
| Replay evidence | Replay / Platform Core services | Preserved |

## 5. Implementation Evidence

Implementation evidence:

* `aigol/runtime/human_interface_runtime_entry_service.py` defines the canonical runtime entry service and status model.
* `aigol/cli/aicli.py` delegates approved requests into `run_human_interface_runtime_entry(...)`.
* `aigol/cli/aigol_cli.py` delegates ACLI Next runtime-bound sessions into `run_human_interface_runtime_entry(...)`.
* The historical `aicli` `_run_certified_runtime(...)` wrapper was removed.
* The historical ACLI Next local runtime prompt, runtime turn extraction, and workspace-recording branch were removed from `_run_acli_next_runtime_bound_session(...)`.

Regression evidence:

* `tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py`
* `tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py`
* `tests/test_g14_22_reference_unified_human_interface_v1.py`

## 6. Runtime Evidence

Focused automated runtime validation confirmed:

* the canonical entry service produces `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND`;
* `aicli` reaches the canonical entry service after `/approve`;
* `aigol next` reaches the same canonical entry service;
* both interfaces use the same operator context:

```text
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY
```

The canonical entry service produces replay-visible Project Services and workspace state artifacts for each interface.

Real interactive validation was also performed with the same natural-language request:

```text
Add GitHub Actions support.
```

The `aicli` path was executed through:

```text
./aicli
```

The ACLI Next path was executed through:

```text
python -m aigol.cli.aigol_cli next --prompt "Add GitHub Actions support."
```

Both real executions reached the canonical runtime entry and produced equivalent post-context continuation evidence:

| Interface | Runtime Entry | Continuation Status | Failure Classification |
| --- | --- | --- | --- |
| `aicli` | `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY` | `FAILED_CLOSED` | `PROVIDER_AVAILABILITY` |
| `aigol next` | `CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY` | `FAILED_CLOSED` | `PROVIDER_AVAILABILITY` |

The shared downstream failure was:

```text
OpenAI provider unavailable
```

This confirms runtime-entry equivalence while preserving the existing fail-closed Provider Platform behavior. Provider availability remains an operational dependency outside the G14-30 runtime-entry unification.

## 7. Replay Evidence

The service records replay-visible evidence for:

* Platform Core Project Services context;
* Development Intent Resolution;
* runtime prompts;
* runtime entry status;
* governed runtime progress;
* Project Workspace state.

Replay remains owned by the certified runtime and Platform Core services. Human Interface adapters do not generate independent runtime replay evidence.

## 8. Architectural Compliance

G14-30 preserves all certified ownership boundaries:

* Human Interfaces remain thin adapters.
* Platform Core remains the orchestration authority.
* Project Workspace, Project Guidance, Knowledge Reuse, and Development Intent Resolution remain Platform Core services.
* Governance remains the authorization authority.
* Provider Platform remains the provider invocation authority.
* Worker Platform remains the execution authority.
* Replay remains the evidence authority.

No new authority layer was introduced.

## 9. Validation

Performed:

```text
python -m py_compile aigol/runtime/human_interface_runtime_entry_service.py aigol/cli/aicli.py aigol/cli/aigol_cli.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py

python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py -q

python -m pytest tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py -q

git diff --check
```

Result:

```text
13 passed
5 passed
git diff --check passed
```

Additional validation is recorded in the final implementation report for this milestone.

## 10. Certification Summary

The canonical Human Interface Runtime Entry Service is implemented and shared by current Human Interfaces.

The certified runtime entry is now reusable by future Web, Android, iOS, Voice, REST, Desktop, and other Human Interfaces without introducing interface-specific runtime orchestration.

Final verdict:

```text
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_CERTIFIED
```
