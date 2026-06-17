# AIGOL Live Provider Environment Trace V1

Status: environment visibility trace.

Purpose: trace the runtime process chain used by `CERT-000004` and determine why `AIGOL_OPENAI_API_KEY` was not visible to the operator entrypoint.

This artifact is review only.

It does not provision credentials.

It does not invoke OpenAI.

It does not modify runtime behavior.

It does not redesign credential boundaries, provider runtime, ERR, replay, or operator entrypoint architecture.

## Observed State

User-observed shell state:

```text
AIGOL_OPENAI_API_KEY present
```

Certification evidence:

```text
provider_selected = openai
credential_available = true
credential_env_present_at_runtime = false
provider_invoked = false
provider_response_received = false
failure_reason = first live provider operator entrypoint failed closed: credential unavailable
```

Key question:

```text
Why can the user shell report AIGOL_OPENAI_API_KEY present while the certification process reports it unavailable?
```

## Reviewed Runtime Surfaces

Reviewed:

- `aigol/runtime/first_live_provider_operator_entrypoint.py`;
- `aigol/runtime/first_live_provider_execution_runtime.py`;
- `aigol/runtime/live_provider_runtime_boundary.py`;
- `aigol/runtime/live_openai_executor.py`;
- `CERT-000004` certification evidence;
- Codex command process environment trace.

## CERT-000004 Execution Path

The certification was executed by a Python process launched through the Codex tool command surface.

The certification script directly called:

```text
instantiate_first_live_provider_activation_package(...)
instantiate_first_live_provider_dispatch_authorization(...)
run_first_live_provider_operator_entrypoint(...)
```

The operator entrypoint directly calls:

```text
run_first_live_provider_execution_runtime(...)
```

The execution runtime directly calls:

```text
run_live_provider_runtime_boundary(...)
```

No AiGOL subprocess is created inside this path.

No AiGOL clean environment is constructed inside this path.

No AiGOL virtualenv activation is performed inside this path.

No AiGOL environment filtering is performed inside this path.

## Process Chain Observed

The local command trace showed:

```text
pid = 2
ppid = 1
executable = /usr/bin/python
AIGOL_OPENAI_API_KEY_PRESENT = false
OPENAI_PROVIDER_CREDENTIAL_PRESENT = false
VIRTUAL_ENV_PRESENT = false
```

Process inspection showed the parent process is:

```text
bwrap ... codex-linux-sandbox ... /home/pisarna/.vscode/extensions/openai.chatgpt-.../codex ...
```

The command process is therefore not an ordinary interactive terminal shell.

It is a Codex sandbox child process launched by the VS Code extension command surface.

The sandbox command uses a shell snapshot:

```text
/home/pisarna/.codex/shell_snapshots/<snapshot>.sh
```

and then runs the requested command under that sandbox.

## Environment Inheritance Trace

Observed inheritance chain:

```text
VS Code / Codex extension process
-> Codex sandbox process
-> shell snapshot loaded by Codex
-> exec_command shell
-> python certification process
-> direct AiGOL operator entrypoint function call
```

Credential lookup happens here:

```text
python certification process
-> run_first_live_provider_operator_entrypoint(...)
-> _verify_credential_available("env:AIGOL_OPENAI_API_KEY")
-> os.environ.get("AIGOL_OPENAI_API_KEY")
```

Observed result:

```text
os.environ.get("AIGOL_OPENAI_API_KEY") = missing
```

## Subprocess Review

AiGOL runtime path:

```text
SUBPROCESS_USED_BY_OPERATOR_ENTRYPOINT = NO
SUBPROCESS_USED_BY_EXECUTION_RUNTIME = NO
SUBPROCESS_USED_BY_LIVE_PROVIDER_BOUNDARY = NO
SUBPROCESS_USED_BY_OPENAI_EXECUTOR = NO
```

The only process launch involved in the certification attempt is outside AiGOL:

```text
Codex tool command launches a Python process.
```

Therefore, the missing credential is not caused by an AiGOL-created subprocess dropping environment variables.

## Clean Environment Review

AiGOL runtime does not create:

```text
env = {}
clean environment
sanitized environment
explicit allowlist environment
```

The operator entrypoint simply reads:

```text
os.environ.get("AIGOL_OPENAI_API_KEY")
```

Therefore, the missing credential is not caused by AiGOL cleaning the environment.

## Virtualenv Review

Observed:

```text
VIRTUAL_ENV_PRESENT = false
python executable = /usr/bin/python
```

No virtualenv activation was observed in the certification command process.

No evidence was found that virtualenv activation changed credential visibility.

Finding:

```text
VIRTUALENV_VISIBILITY_CAUSE = NOT_EVIDENCED
```

## Environment Filtering Or Sanitization Review

AiGOL code:

```text
ENVIRONMENT_FILTERING_BY_AIGOL = NOT_FOUND
```

Codex sandbox:

The sandbox is launched by `bwrap` and loads a Codex shell snapshot before executing commands.

The trace shows explicit environment snapshot and proxy-variable handling by the Codex command surface.

No evidence shows AiGOL filtering `AIGOL_OPENAI_API_KEY`.

The likely environment boundary is:

```text
external user shell
!=
Codex extension sandbox command process
```

If `AIGOL_OPENAI_API_KEY` was exported in a terminal after the Codex extension/sandbox environment was created, or exported in a shell not inherited by the Codex command process, AiGOL will not see it.

## Same Shell Session Review

Observed command process:

```text
Codex sandbox child process
```

Observed environment:

```text
AIGOL_OPENAI_API_KEY_PRESENT = false
```

Therefore:

```text
CERTIFICATION_EXECUTED_FROM_SAME_SHELL_SESSION_AS_USER_PROVISIONING = NOT_EVIDENCED
```

More precise finding:

```text
The certification was executed from the Codex governed command process, not necessarily from the interactive shell where the operator observed AIGOL_OPENAI_API_KEY.
```

## Root Cause Analysis

Root cause:

```text
AIGOL_OPENAI_API_KEY was not present in the environment inherited by the Python process that executed CERT-000004.
```

The likely cause is an environment visibility boundary between:

```text
the user shell where AIGOL_OPENAI_API_KEY was provisioned
```

and:

```text
the Codex sandbox command process that executed the certification
```

Not root cause:

```text
AiGOL operator entrypoint subprocess environment loss
AiGOL execution runtime subprocess environment loss
AiGOL live provider boundary environment sanitization
AiGOL virtualenv activation
ERR provider selection
provider registration
credential secret replay filtering
```

## Why `credential_available = true` Still Appeared

As established by `AIGOL_OPERATOR_ENTRYPOINT_CREDENTIAL_MISMATCH_REVIEW_V1`:

```text
activation_package/003_first_live_provider_credential_availability.json
```

records activation-package availability from a pre-dispatch assertion/default parameter.

It does not prove that the later operator-entrypoint Python process contains:

```text
AIGOL_OPENAI_API_KEY
```

The operator entrypoint is the first actual live process-environment gate.

## Smallest Remediation

Smallest operational remediation:

```text
Provision AIGOL_OPENAI_API_KEY into the exact process environment that launches the Codex certification command.
```

Acceptable approaches:

1. Start or restart the Codex/VS Code session from a shell that already exports `AIGOL_OPENAI_API_KEY`.
2. Configure the IDE or Codex extension launch environment to include `AIGOL_OPENAI_API_KEY`.
3. Execute the certification from a terminal process that directly contains `AIGOL_OPENAI_API_KEY`, using the governed runtime entrypoint and preserving all replay requirements.

The preflight must show only:

```text
AIGOL_OPENAI_API_KEY_PRESENT = true
```

It must not print:

```text
credential value
credential hash
authorization header
partial token
```

## Smallest Evidence Remediation

Add or require a pre-certification environment trace artifact before live dispatch:

```text
LIVE_PROVIDER_ENVIRONMENT_VISIBILITY_TRACE_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `runtime_process_id`;
- `parent_process_id`;
- `python_executable`;
- `launched_by_codex_sandbox`;
- `virtualenv_present`;
- `credential_env_name`;
- `credential_env_present`;
- `credential_value_omitted`;
- `credential_hash_recorded`;
- `authorization_header_replayed`;
- `secret_value_replayed`;
- `replay_visible`;
- `created_at`;
- `artifact_hash`.

Required values:

```text
credential_value_omitted = true
credential_hash_recorded = false
authorization_header_replayed = false
secret_value_replayed = false
```

This is an evidence improvement, not a provider architecture change.

## Certification Rerun Requirement

Before rerunning `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1`, verify in the same command execution context:

```text
AIGOL_OPENAI_API_KEY_PRESENT = true
```

Then execute:

```text
activation package instantiation
-> dispatch authorization instantiation
-> operator entrypoint
-> execution runtime
-> live provider runtime boundary
-> OpenAI executor
```

If the preflight still reports:

```text
AIGOL_OPENAI_API_KEY_PRESENT = false
```

then the live certification must not be expected to invoke the provider.

## Final Verdict

Verdict:

```text
LIVE_PROVIDER_ENVIRONMENT_VISIBILITY_GAP_FOUND
```

Supporting determinations:

```text
CERT_000004_PROCESS_ENV_CONTAINED_AIGOL_OPENAI_API_KEY = NO
OPERATOR_ENTRYPOINT_DIRECTLY_READS_OS_ENVIRON = YES
AIGOL_SUBPROCESS_ENV_LOSS_FOUND = NO
AIGOL_CLEAN_ENV_CREATION_FOUND = NO
AIGOL_ENV_SANITIZATION_FOUND = NO
VIRTUALENV_VISIBILITY_CAUSE_FOUND = NO
SAME_SHELL_SESSION_AS_USER_PROVISIONING_EVIDENCED = NO
LIKELY_GAP = USER_PROVISIONED_SHELL_ENV_NOT_INHERITED_BY_CODEX_SANDBOX_COMMAND_PROCESS
SMALLEST_REMEDIATION = PROVISION_KEY_IN_CODEX_GOVERNED_COMMAND_PROCESS_ENVIRONMENT_OR_RUN_CERTIFICATION_FROM_THE_KEYED_GOVERNED_PROCESS
```
