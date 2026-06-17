# AIGOL First Live Cognition Provider Manual Execution Command V1

Status: manual execution command specification.

Purpose: identify the exact terminal command for executing `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1` from a keyed operator shell.

This artifact does not execute the command.

It must not be run through the Codex sandbox.

It does not invoke OpenAI by itself.

It does not provision credentials.

It does not print credential values.

## Working Directory

Run from:

```bash
/home/pisarna/work/sapianta
```

## Required Environment Variables

The terminal session must contain:

```text
AIGOL_OPENAI_API_KEY
OPENAI_API_KEY
```

The governed operator entrypoint checks:

```text
AIGOL_OPENAI_API_KEY
```

`OPENAI_API_KEY` is checked as an operator preflight marker only.

Neither value may be printed, committed, logged, hashed, or replayed.

## Prerequisite Checks

The command performs these boolean checks before certification:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_PRESENT=True
```

If either value is missing, the command aborts before certification.

Allowed preflight output:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_PRESENT=True
```

Forbidden output:

```text
credential value
credential hash
authorization header
partial token
```

## Exact Terminal Command

Run this entire command from the keyed terminal session:

```bash
cd /home/pisarna/work/sapianta

python - <<'PY'
from pathlib import Path
import json
import os
import re
import sys

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
    reconstruct_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    instantiate_first_live_provider_dispatch_authorization,
    reconstruct_first_live_provider_dispatch_authorization,
)
from aigol.runtime.first_live_provider_operator_entrypoint import (
    run_first_live_provider_operator_entrypoint,
    reconstruct_first_live_provider_operator_entrypoint_replay,
)
from aigol.runtime.first_live_provider_execution_runtime import (
    reconstruct_first_live_provider_execution_runtime_replay,
)
from aigol.runtime.live_openai_executor import create_governed_live_openai_executor
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable

print("AIGOL_OPENAI_API_KEY_PRESENT=" + str(bool(os.environ.get("AIGOL_OPENAI_API_KEY"))))
print("OPENAI_API_KEY_PRESENT=" + str(bool(os.environ.get("OPENAI_API_KEY"))))

if not os.environ.get("AIGOL_OPENAI_API_KEY"):
    print("ABORTED_BEFORE_CERTIFICATION=AIGOL_OPENAI_API_KEY_MISSING")
    sys.exit(2)

if not os.environ.get("OPENAI_API_KEY"):
    print("ABORTED_BEFORE_CERTIFICATION=OPENAI_API_KEY_MISSING")
    sys.exit(2)

base = Path("runtime/first_live_cognition_provider_certification_v1")
base.mkdir(parents=True, exist_ok=True)

existing = []
for path in base.glob("CERT-*"):
    match = re.fullmatch(r"CERT-(\d{6})", path.name)
    if match:
        existing.append(int(match.group(1)))

cert_number = max(existing, default=0) + 1
cert_id = f"CERT-{cert_number:06d}"
cert_suffix = f"{cert_number:06d}"
root = base / cert_id

activation_dir = root / "activation_package"
dispatch_dir = root / "dispatch_authorization"
execution_dir = root / "execution"
operator_dir = root / "operator_entrypoint"
human_confirmation_dir = root / "human_confirmation"
evidence_dir = root / "evidence_package"
replay_dir = root / "replay_package"
report_dir = root / "certification_report"

created_at = "2026-06-17T00:00:00+00:00"
expires_at = "2026-06-17T01:00:00+00:00"
human_prompt = "Help me decide the safest next step for reviewing an AI-generated customer reply before anyone sends it."

activation = instantiate_first_live_provider_activation_package(
    package_id=f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
    human_request=human_prompt,
    required_capability="reasoning",
    approved_by="human.operator",
    created_at=created_at,
    expires_at=expires_at,
    replay_dir=activation_dir,
)

dispatch = instantiate_first_live_provider_dispatch_authorization(
    dispatch_authorization_id=f"FIRST-LIVE-COGNITION-PROVIDER-DISPATCH-AUTH-{cert_suffix}",
    activation_package_replay_dir=activation_dir,
    replay_dir=dispatch_dir,
    created_at=created_at,
    expires_at=expires_at,
)

operator_result = run_first_live_provider_operator_entrypoint(
    operator_request_id=f"FIRST-LIVE-COGNITION-PROVIDER-OPERATOR-DISPATCH-{cert_suffix}",
    operator_id="human.operator",
    human_request=human_prompt,
    created_at=created_at,
    activation_package_replay_dir=activation_dir,
    dispatch_authorization_replay_dir=dispatch_dir,
    execution_replay_dir=execution_dir,
    operator_replay_dir=operator_dir,
    transport=create_governed_live_openai_executor(),
    confirm_dispatch=True,
    live_transport_enabled=True,
)

activation_replay = reconstruct_first_live_provider_activation_package(activation_dir)
dispatch_replay = reconstruct_first_live_provider_dispatch_authorization(dispatch_dir)
operator_replay = reconstruct_first_live_provider_operator_entrypoint_replay(operator_dir)

execution_replay = None
if (execution_dir / "007_first_live_provider_dispatch_execution_packet.json").exists():
    execution_replay = reconstruct_first_live_provider_execution_runtime_replay(execution_dir)

err = load_json(
    activation_dir / "err_openai_selection" / "000_err_resource_selection_evidence_recorded.json"
)["artifact"]

execution_capture = operator_result.get("execution_capture")
provider_invoked = False
provider_response_received = False
transport_evidence = {}
cognition_artifact = {}

if isinstance(execution_capture, dict):
    transport_evidence = execution_capture.get("transport_evidence_artifact") or {}
    cognition_artifact = execution_capture.get("cognition_artifact") or {}
    provider_invoked = bool(transport_evidence.get("provider_invoked"))
    provider_response_received = execution_capture.get("final_status") == "DISPATCH_EXECUTION_COMPLETED"

human_confirmation_recorded = False
if provider_response_received:
    human_confirmation_dir.mkdir(parents=True, exist_ok=True)
    confirmation = {
        "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_HUMAN_CONFIRMATION_ARTIFACT_V1",
        "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
        "created_at": created_at,
        "provider_response_artifact_hash": transport_evidence.get("response_artifact_hash"),
        "llm_cognition_artifact_hash": cognition_artifact.get("artifact_hash"),
        "human_confirmation_recorded": True,
        "confirmed_as_proposal_only": True,
        "worker_execution_authorized": False,
        "governance_mutation_authorized": False,
        "additional_provider_call_authorized": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "replay_visible": True,
    }
    confirmation["artifact_hash"] = replay_hash(confirmation)
    write_json_immutable(
        human_confirmation_dir / "000_first_live_cognition_provider_human_confirmation.json",
        confirmation,
    )
    human_confirmation_recorded = True

observed = {
    "provider_selected": err.get("selected_resource_id"),
    "provider_selected_type": err.get("selected_resource_type"),
    "provider_invoked": provider_invoked,
    "provider_response_received": provider_response_received,
    "human_confirmation_recorded": human_confirmation_recorded,
    "replay_reconstructed": bool(activation_replay and dispatch_replay and operator_replay),
    "execution_replay_reconstructed": execution_replay is not None,
    "worker_invoked": bool(operator_result.get("worker_invoked")),
    "credential_secret_replayed": bool(operator_result.get("credential_secret_replayed")),
    "authorization_header_replayed": bool(operator_result.get("authorization_header_replayed")),
    "operator_final_status": operator_result.get("final_status"),
    "failure_reason": operator_result.get("failure_reason"),
}

final_verdict = (
    "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"
    if all(
        [
            observed["provider_selected"] == "openai",
            observed["provider_invoked"],
            observed["provider_response_received"],
            observed["human_confirmation_recorded"],
            observed["replay_reconstructed"],
            not observed["worker_invoked"],
        ]
    )
    else "COGNITION_PROVIDER_CERTIFICATION_FAILED"
)

evidence_package = {
    "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_EVIDENCE_PACKAGE_V1",
    "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
    "created_at": created_at,
    "scenario": {
        "proposal_only": True,
        "worker_execution_allowed": False,
    },
    "evidence_references": {
        "activation_package": str(activation_dir),
        "err_resolution": str(activation_dir / "err_openai_selection"),
        "dispatch_authorization": str(dispatch_dir),
        "operator_entrypoint": str(operator_dir),
        "execution": str(execution_dir),
        "human_confirmation": str(human_confirmation_dir),
    },
    "observed": observed,
}
evidence_package["artifact_hash"] = replay_hash(evidence_package)

replay_package = {
    "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_REPLAY_PACKAGE_V1",
    "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
    "created_at": created_at,
    "replay_root": str(root),
    "reconstructed_segments": {
        "activation_package": True,
        "err_resolution": True,
        "dispatch_authorization": True,
        "operator_entrypoint": True,
        "execution_runtime": execution_replay is not None,
        "provider_response": provider_response_received,
        "human_confirmation": human_confirmation_recorded,
    },
    "replay_reconstructed": observed["replay_reconstructed"],
    "observed": observed,
}
replay_package["artifact_hash"] = replay_hash(replay_package)

report = {
    "artifact_type": "FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_REPORT_V1",
    "certification_id": f"FIRST-LIVE-COGNITION-PROVIDER-CERT-{cert_suffix}",
    "governing_artifact": "AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1",
    "created_at": created_at,
    "observed": observed,
    "blocker_analysis": {
        "architecture_blockers": [],
        "governance_blockers": [],
        "runtime_blockers": [] if final_verdict == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED" else [observed["failure_reason"]],
        "dependency_blockers": [],
    },
    "final_verdict": final_verdict,
}
report["artifact_hash"] = replay_hash(report)

evidence_dir.mkdir(parents=True, exist_ok=True)
replay_dir.mkdir(parents=True, exist_ok=True)
report_dir.mkdir(parents=True, exist_ok=True)

write_json_immutable(evidence_dir / "000_first_live_cognition_provider_evidence_package.json", evidence_package)
write_json_immutable(replay_dir / "000_first_live_cognition_provider_replay_package.json", replay_package)
write_json_immutable(report_dir / "000_first_live_cognition_provider_certification_report.json", report)

print("CERT_ROOT=" + str(root))
print("provider_selected=" + str(observed["provider_selected"]))
print("provider_invoked=" + str(observed["provider_invoked"]))
print("provider_response_received=" + str(observed["provider_response_received"]))
print("human_confirmation_recorded=" + str(observed["human_confirmation_recorded"]))
print("replay_reconstructed=" + str(observed["replay_reconstructed"]))
print("FINAL_VERDICT=" + final_verdict)
PY
```

## Expected CERT Root Location

The command writes to the next available root:

```text
runtime/first_live_cognition_provider_certification_v1/CERT-00000N/
```

For example, if `CERT-000004` is the latest existing root, expected next root is:

```text
runtime/first_live_cognition_provider_certification_v1/CERT-000005/
```

## Expected Output Artifacts

Evidence package:

```text
<CERT_ROOT>/evidence_package/000_first_live_cognition_provider_evidence_package.json
```

Replay package:

```text
<CERT_ROOT>/replay_package/000_first_live_cognition_provider_replay_package.json
```

Certification report:

```text
<CERT_ROOT>/certification_report/000_first_live_cognition_provider_certification_report.json
```

Additional expected replay roots:

```text
<CERT_ROOT>/activation_package/
<CERT_ROOT>/dispatch_authorization/
<CERT_ROOT>/operator_entrypoint/
<CERT_ROOT>/execution/
<CERT_ROOT>/human_confirmation/
```

## Expected Success Markers

Successful terminal markers:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_PRESENT=True
CERT_ROOT=runtime/first_live_cognition_provider_certification_v1/CERT-00000N
provider_selected=openai
provider_invoked=True
provider_response_received=True
human_confirmation_recorded=True
replay_reconstructed=True
FINAL_VERDICT=FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED
```

## Expected Failure Markers

Preflight failure markers:

```text
ABORTED_BEFORE_CERTIFICATION=AIGOL_OPENAI_API_KEY_MISSING
ABORTED_BEFORE_CERTIFICATION=OPENAI_API_KEY_MISSING
```

Certification failure markers:

```text
provider_selected=openai
provider_invoked=False
provider_response_received=False
FINAL_VERDICT=COGNITION_PROVIDER_CERTIFICATION_FAILED
```

Failure details must be read from:

```text
<CERT_ROOT>/certification_report/000_first_live_cognition_provider_certification_report.json
<CERT_ROOT>/operator_entrypoint/001_first_live_provider_operator_dispatch_result.json
<CERT_ROOT>/execution/007_first_live_provider_dispatch_execution_packet.json
```

depending on the failure gate reached.

## Final Verdict

Verdict:

```text
MANUAL_EXECUTION_COMMAND_IDENTIFIED
```
