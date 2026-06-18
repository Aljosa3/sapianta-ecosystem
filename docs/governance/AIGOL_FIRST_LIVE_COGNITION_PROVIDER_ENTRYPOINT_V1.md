# AIGOL First Live Cognition Provider Entrypoint V1

Status: implemented runtime entrypoint.

Purpose: convert the manual first live cognition-provider certification command into a permanent single-command Python module entrypoint.

This milestone does not change behavior.

It does not change governance.

It does not change replay semantics.

It does not change certification logic.

It does not introduce provider routing, retry, fallback, worker invocation, governance mutation, replay mutation, or credential disclosure.

## Runtime Entrypoint

Module:

```text
aigol.runtime.first_live_cognition_provider_certification
```

Command:

```bash
python -m aigol.runtime.first_live_cognition_provider_certification
```

Required working directory:

```text
/home/pisarna/work/sapianta
```

Required environment markers:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_PRESENT=True
```

The module checks environment presence only. It does not print credential values.

## Preserved Certification Path

The entrypoint performs the same bounded sequence as `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_MANUAL_EXECUTION_COMMAND_V1`:

```text
activation package instantiation
-> dispatch authorization instantiation
-> operator entrypoint
-> execution runtime
-> live provider runtime boundary
-> OpenAI executor
-> human confirmation artifact if provider response is received
-> evidence package
-> replay package
-> certification report
```

## Output Markers

Expected success markers:

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

Expected preflight failure markers:

```text
ABORTED_BEFORE_CERTIFICATION=AIGOL_OPENAI_API_KEY_MISSING
ABORTED_BEFORE_CERTIFICATION=OPENAI_API_KEY_MISSING
```

Expected certification failure marker:

```text
FINAL_VERDICT=COGNITION_PROVIDER_CERTIFICATION_FAILED
```

## Evidence Locations

The entrypoint writes to the next available root:

```text
runtime/first_live_cognition_provider_certification_v1/CERT-00000N/
```

Summary artifacts:

```text
<CERT_ROOT>/evidence_package/000_first_live_cognition_provider_evidence_package.json
<CERT_ROOT>/replay_package/000_first_live_cognition_provider_replay_package.json
<CERT_ROOT>/certification_report/000_first_live_cognition_provider_certification_report.json
```

## Validation

Focused validation:

```text
python -m pytest tests/test_first_live_cognition_provider_certification_entrypoint_v1.py tests/test_first_live_provider_operator_entrypoint_v1.py tests/test_first_live_provider_execution_runtime_v1.py tests/test_live_provider_runtime_boundary_v1.py
30 passed
```

Validated:

- single-command entrypoint invokes the existing governed sequence;
- success path records provider selection, invocation, response, human confirmation, and replay reconstruction;
- missing credential aborts before certification;
- CLI output markers are stable;
- secret material is not replayed;
- existing operator, execution, and live provider boundary tests remain passing.

## Final Verdict

Verdict:

```text
FIRST_LIVE_COGNITION_PROVIDER_ENTRYPOINT_IMPLEMENTED
```
