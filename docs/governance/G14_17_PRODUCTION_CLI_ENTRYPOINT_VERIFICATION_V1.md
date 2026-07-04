# G14-17 Production CLI Entrypoint Verification V1

Status: production CLI entrypoint partially confirmed; production executable unavailable in audit environment.

Final verdict: PRODUCTION_CLI_ENTRYPOINT_PARTIALLY_CONFIRMED

## 1. Executive Summary

G14-17 audited whether the production command:

```text
aigol next
```

invokes the same runtime as the repository module command:

```text
python -m aigol.cli.aigol_cli next
```

The audit found that the repository module entrypoint is present, imports from the current workspace, and enters the certified AiGOL Next runtime binding path.

The production executable could not be verified because `aigol` is not installed or visible on `PATH` in this workspace.

Root cause classification:

```text
PATH_CONFIGURATION_DIFFERENCE
```

This classification is based on direct executable resolution evidence, not inference:

- `command -v aigol` returned no executable;
- `type -a aigol` returned `aigol: not found`;
- Python `shutil.which("aigol")` returned `None`;
- no repository-level `pyproject.toml`, `setup.cfg`, or `setup.py` defines a current production console script in the repository root.

The repository module path was revalidated through a live interactive session. It entered native runtime binding, but failed closed at provider availability:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_PARTIALLY_BOUND
runtime_entered: True
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
```

Therefore, the original manual discrepancy cannot be certified as a Platform Core defect or runtime entrypoint defect from this environment. The production command cannot be compared until the production `aigol` executable is installed or its resolved path is provided.

## 2. Executable Resolution Report

Audit commands:

```text
command -v aigol
type -a aigol
python -c "import shutil; print(shutil.which('aigol'))"
```

Observed results:

```text
command -v aigol: no output
type -a aigol: /bin/bash: line 1: type: aigol: not found
shutil.which("aigol"): None
```

Finding:

```text
The production `aigol` executable is not available to the audit shell.
```

Operational impact:

- the installed executable location cannot be inspected;
- symbolic links cannot be traced;
- wrapper scripts cannot be inspected;
- installed package metadata cannot be compared to the workspace module;
- runtime equivalence for the literal production command cannot be fully certified.

## 3. PATH Analysis

The active Python interpreter for the repository module audit was:

```text
/usr/bin/python
```

The imported module paths were:

```text
/home/pisarna/work/sapianta/aigol/__init__.py
/home/pisarna/work/sapianta/aigol/cli/aigol_cli.py
```

This confirms that:

- `python -m aigol.cli.aigol_cli next` uses the workspace source tree;
- the current shell does not resolve `aigol` to any production wrapper;
- a human terminal that does resolve `aigol` may be using a different shell, virtual environment, installed package, alias, or wrapper not present here.

## 4. Packaging Analysis

Repository-root packaging files were not present:

```text
pyproject.toml: not present at repository root
setup.cfg: not present at repository root
setup.py: not present at repository root
```

The repository contains package manifests in subprojects:

```text
./sapianta-domain-credit/pyproject.toml
./sapianta_system/pyproject.toml
./sapianta-domain-trading/pyproject.toml
```

No root-level console script definition was found for production `aigol`.

Finding:

```text
The repository module path is canonical for the current workspace audit, but the production executable packaging path is not represented by an installed root-level console entrypoint in this environment.
```

## 5. Entrypoint Comparison

### 5.1 Production Command

Command:

```text
aigol next
```

Verification status:

```text
not executable in this workspace
```

The audit cannot determine:

- executable path;
- interpreter path;
- wrapper script body;
- installed package version;
- module invoked;
- whether it points to current workspace code.

### 5.2 Repository Module Command

Command:

```text
python -m aigol.cli.aigol_cli next
```

Verification status:

```text
executable and auditable
```

Implementation evidence:

```text
aigol/cli/aigol_cli.py::main
```

When the command is invoked as a real interactive TTY and no subcommand, prompt, or JSON flag is present, `main()` calls:

```text
run_acli_next_persistent_conversational_session(...)
```

with:

```text
turn_runner=_run_acli_next_runtime_bound_session
guided_development_workflow=True
```

## 6. Repository Module Call Graph

The repository module path is:

```text
python -m aigol.cli.aigol_cli next
-> aigol.cli.aigol_cli::main
-> _should_run_persistent_acli_next(args)
-> run_acli_next_persistent_conversational_session(...)
-> /send
-> governed implementation summary
-> /approve
-> submit_turn(...)
-> _run_acli_next_runtime_bound_session(...)
-> run_acli_next_conversational_session(...)
-> is_native_development_prompt(...)
-> run_interactive_conversation(...)
-> conversational CLI routing
-> NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
-> post-context continuation
-> Provider Platform
```

Approval handling evidence:

```text
aigol/acli_next/conversational.py
```

The `/approve` branch calls:

```text
submit_turn(
    session_id=conversation_id,
    prompts=[pending_summary["refined_message"]],
    created_at=created_at,
    replay_dir=replay_dir,
    workspace=workspace,
)
```

In the CLI module entry path, `submit_turn` is `_run_acli_next_runtime_bound_session`.

## 7. Runtime Binding Analysis

The runtime binding function is:

```text
aigol/cli/aigol_cli.py::_run_acli_next_runtime_bound_session
```

It returns:

```text
AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

only when:

```text
not any(is_native_development_prompt(prompt) for prompt in prompts)
```

When native development is detected, it invokes:

```text
run_interactive_conversation(...)
```

with:

```text
auto_continue=True
operator_context=AIGOL_NEXT_RUNTIME_BINDING
```

The repository module validation reached this runtime binding path.

## 8. Runtime Comparison

### 8.1 Production Command Runtime

The production command could not be executed:

```text
aigol: not found
```

Runtime equivalence for the production executable remains unverified.

### 8.2 Repository Module Runtime

Validation command:

```text
python -m aigol.cli.aigol_cli next \
  --session-id G14-17-REPO-MODULE \
  --runtime-root /tmp/aigol_g14_17_repo_module \
  --workspace /home/pisarna/work/sapianta \
  --created-at 2026-07-04T00:00:00Z
```

Interactive input:

```text
Implement a native validation helper for replay evidence summaries.
/send
/approve
exit
```

Observed output:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_PARTIALLY_BOUND
runtime_entered: True
governance_authorization_reached: False
provider_invocation_reached: False
worker_execution_reached: False
replay_certification_reached: False
manual_chatgpt_codex_transfer_required: True
```

Important distinction:

```text
The repository module did not return AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED.
```

It entered runtime binding and failed closed later due to provider availability.

## 9. Runtime Evidence

Runtime evidence root:

```text
/tmp/aigol_g14_17_repo_module/G14-17-REPO-MODULE
```

Workflow selection evidence:

```text
TURN-000001/conversational_cli_routing/001_conversational_workflow_selection_recorded.json
workflow_id: NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION
routing_status: WORKFLOW_SELECTED
matched_terms: task-completion, native, development
```

Provider continuation evidence:

```text
TURN-000001/post_context_continuation/001_post_context_continuation_returned.json
continuation_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
operational_failure_classification: PROVIDER_AVAILABILITY
provider_resilience_status: PROVIDER_UNAVAILABLE_FAIL_CLOSED
```

Provider proposal evidence:

```text
TURN-000001/post_context_continuation/conversation_ppp_routing/provider_proposal_production/003_provider_proposal_production_returned.json
provider_id: openai
provider_invocation_status: PROVIDER_NOT_INVOKED
production_status: FAILED_CLOSED
failure_reason: OpenAI provider unavailable
```

Turn completion evidence:

```text
TURN-000001/turn_completion/001_result_delivered.json
status: FAILED_CLOSED
result_delivered: true
replay_visible: true
```

## 10. Root Cause Analysis

Root cause classification:

```text
PATH_CONFIGURATION_DIFFERENCE
```

Evidence:

- no `aigol` executable is present on `PATH`;
- the production command cannot be executed in this environment;
- the repository module imports from the workspace and enters runtime binding;
- the repository module no longer reproduces the observed `AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED` state for the tested implementation prompt;
- the repository module currently fails closed at provider availability rather than at runtime binding.

The audit does not prove:

- stale production installation;
- entrypoint divergence;
- packaging divergence;
- implementation defect in Platform Core;
- implementation defect in AiGOL Next runtime binding.

Those classifications require access to the actual production executable path.

## 11. Production Readiness Assessment

Repository module readiness:

```text
partially ready; runtime binding is reached, provider availability blocks full execution in this audit environment
```

Production executable readiness:

```text
not fully confirmable; executable unavailable on PATH
```

Required operational closure:

1. Install or expose the production `aigol` executable in the same environment used for acceptance.
2. Record:

```text
command -v aigol
type -a aigol
head -n 40 "$(command -v aigol)"
python -c "import shutil; print(shutil.which('aigol'))"
```

3. Confirm whether the executable invokes:

```text
aigol.cli.aigol_cli:main
```

4. Run the same interactive scenario through both entrypoints.

No Platform Core redesign is indicated.

## 12. Certification Summary

The production CLI entrypoint cannot be fully certified because the production executable is not present in this audit environment.

The repository module entrypoint is auditable and enters the certified runtime binding path.

The observed manual failure mode:

```text
AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED
```

is not reproduced by the repository module in this audit.

The current repository module failure mode is:

```text
PROVIDER_AVAILABILITY
```

Final verdict: PRODUCTION_CLI_ENTRYPOINT_PARTIALLY_CONFIRMED

## 13. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PRODUCTION_CLI_ENTRYPOINT_PARTIALLY_CONFIRMED
