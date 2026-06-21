# AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1

Status: defined.

Purpose: eliminate recurring operator-side credential visibility failures by defining a deterministic, secret-free operator environment bootstrap compatible with `AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1`.

Final verdict:

```text
OPERATOR_ENVIRONMENT_BOOTSTRAP_DEFINED
```

## 1. Scope

This artifact defines the operator-side startup procedure for exposing approved provider credential references to the governed AiGOL process environment.

It reviews:

- `OPENAI_API_KEY` handling;
- `AIGOL_OPENAI_API_KEY` handling;
- provider credential registry expectations;
- dependency failure runtime expectations;
- operator workflow requirements.

This artifact does not:

- store credential values;
- create a secret manager;
- redesign ERR;
- redesign provider runtime;
- add runtime fallback behavior;
- authorize provider invocation;
- change replay semantics.

## 2. Governing Facts

`AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1` defines the canonical OpenAI credential reference as:

```text
provider_id = openai
credential_reference = env:AIGOL_OPENAI_API_KEY
```

`OPENAI_API_KEY` is a provider-native/operator alias. It may be useful for local tooling, SDK diagnostics, or operator habits, but it is not the canonical AiGOL governed credential reference.

The first live cognition provider certification entrypoint expects both presence markers for current certification visibility:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
OPENAI_API_KEY_PRESENT=True
```

The governed execution path fails closed if `AIGOL_OPENAI_API_KEY` is absent from the Python process environment that launches the certification or provider runtime.

## 3. Root Problem

The recurring failure pattern is:

```text
OPENAI_API_KEY_PRESENT=True
AIGOL_OPENAI_API_KEY_PRESENT=False
```

This means the operator shell can see a provider-native credential alias, but the governed AiGOL credential reference is not present.

The earlier environment trace established that a second failure mode also exists:

```text
credential exists in one shell
!=
credential exists in the process launching AiGOL
```

For example, an IDE, Codex sandbox, terminal tab, or subprocess may have been started before credential export occurred.

## 4. Canonical Operator Bootstrap Location

The canonical operator bootstrap file is:

```text
$HOME/.config/aigol/operator-bootstrap.sh
```

Required properties:

- local to the operator account;
- outside the repository;
- outside replay artifacts;
- outside governance artifacts;
- not committed to git;
- readable only by the operator where local policy allows;
- sourced before running governed AiGOL certification or live-provider commands.

Recommended file permissions:

```text
0600
```

The bootstrap file may contain either:

1. secret-free propagation from already-provisioned provider-native variables into canonical `AIGOL_*` variables; or
2. organization-approved local secret loading commands managed outside AiGOL.

AiGOL governance artifacts must never include the resulting secret values.

## 5. Canonical Bootstrap Template

The recommended secret-free bootstrap template is:

```sh
# ~/.config/aigol/operator-bootstrap.sh
# AiGOL operator environment bootstrap.
# Do not enable shell tracing while sourcing this file.

set +x

if [ -z "${AIGOL_OPENAI_API_KEY:-}" ] && [ -n "${OPENAI_API_KEY:-}" ]; then
  export AIGOL_OPENAI_API_KEY="$OPENAI_API_KEY"
fi

if [ -z "${AIGOL_ANTHROPIC_API_KEY:-}" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  export AIGOL_ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
fi

if [ -z "${AIGOL_GEMINI_API_KEY:-}" ] && [ -n "${GEMINI_API_KEY:-}" ]; then
  export AIGOL_GEMINI_API_KEY="$GEMINI_API_KEY"
fi

if [ -z "${AIGOL_MISTRAL_API_KEY:-}" ] && [ -n "${MISTRAL_API_KEY:-}" ]; then
  export AIGOL_MISTRAL_API_KEY="$MISTRAL_API_KEY"
fi
```

Canonical rule:

```text
AIGOL_* credential variables win.
Provider-native aliases may populate AIGOL_* variables only when the canonical variable is absent.
```

This is an operator bootstrap rule, not a runtime fallback rule.

## 6. Shell Startup Integration

For interactive Bash shells, source the bootstrap file from:

```text
$HOME/.bashrc
```

Recommended snippet:

```sh
if [ -r "$HOME/.config/aigol/operator-bootstrap.sh" ]; then
  . "$HOME/.config/aigol/operator-bootstrap.sh"
fi
```

For login-shell-only environments, source the same file from:

```text
$HOME/.profile
```

For Zsh environments, source the same file from:

```text
$HOME/.zshrc
```

For IDE or Codex-launched processes, the operator must ensure one of the following:

1. start the IDE from a shell that has already sourced the bootstrap;
2. configure the IDE launch environment to source or inherit the bootstrap;
3. run live certification from a terminal session that has directly sourced the bootstrap.

An already-running IDE or sandbox process must not be assumed to inherit credentials exported later in a separate shell.

## 7. Provider Credential Propagation Strategy

Provider credential propagation is defined as a pre-runtime operator responsibility.

Initial mappings:

| provider_id | canonical AiGOL variable | accepted operator alias for bootstrap | runtime credential reference |
| --- | --- | --- | --- |
| `openai` | `AIGOL_OPENAI_API_KEY` | `OPENAI_API_KEY` | `env:AIGOL_OPENAI_API_KEY` |
| `claude` | `AIGOL_ANTHROPIC_API_KEY` | `ANTHROPIC_API_KEY` | `env:AIGOL_ANTHROPIC_API_KEY` |
| `gemini` | `AIGOL_GEMINI_API_KEY` | `GEMINI_API_KEY` | `env:AIGOL_GEMINI_API_KEY` |
| `mistral` | `AIGOL_MISTRAL_API_KEY` | `MISTRAL_API_KEY` | `env:AIGOL_MISTRAL_API_KEY` |

Rules:

- the provider credential registry defines canonical references;
- bootstrap may copy from provider-native aliases into canonical references;
- runtime checks canonical AiGOL references;
- dependency failures report canonical references;
- replay records only secret-free presence and diagnostic metadata.

## 8. Replay-Safe Diagnostics

Operator bootstrap diagnostics may record:

```json
{
  "artifact_type": "OPERATOR_ENVIRONMENT_BOOTSTRAP_DIAGNOSTIC_V1",
  "provider_id": "openai",
  "canonical_credential_reference": "env:AIGOL_OPENAI_API_KEY",
  "canonical_credential_present": true,
  "provider_native_alias": "env:OPENAI_API_KEY",
  "provider_native_alias_present": true,
  "bootstrap_file_reference": "$HOME/.config/aigol/operator-bootstrap.sh",
  "bootstrap_file_present": true,
  "credential_value_recorded": false,
  "credential_hash_recorded": false,
  "authorization_header_recorded": false,
  "replay_safe": true
}
```

Diagnostics must never record:

- credential values;
- credential hashes;
- partial tokens;
- authorization headers;
- request payload contents;
- secret-manager returned values.

## 9. Dependency Failure Runtime Integration

If a canonical credential reference is missing after bootstrap, the dependency failure runtime classification is:

```text
MISSING_CREDENTIAL
```

Operator-facing message:

```text
OpenAI cognition cannot run because env:AIGOL_OPENAI_API_KEY is unavailable in the governed process environment.
```

Impact:

```text
Provider execution is stopped before invocation.
No worker execution occurs.
No live provider request is attempted.
```

Remediation:

```text
Source $HOME/.config/aigol/operator-bootstrap.sh in the exact shell or launch environment that will run AiGOL, then verify credential presence without printing the value.
```

Retry guidance:

```text
After the verification command reports AIGOL_OPENAI_API_KEY_PRESENT=True, rerun the governed certification or provider invocation entrypoint.
```

## 10. Operator Verification Command

From the repository root:

```text
/home/pisarna/work/sapianta
```

Run:

```sh
. "$HOME/.config/aigol/operator-bootstrap.sh"
python - <<'PY'
import os
import sys

checks = {
    "AIGOL_OPENAI_API_KEY_PRESENT": bool(os.environ.get("AIGOL_OPENAI_API_KEY")),
    "OPENAI_API_KEY_PRESENT": bool(os.environ.get("OPENAI_API_KEY")),
    "AIGOL_ANTHROPIC_API_KEY_PRESENT": bool(os.environ.get("AIGOL_ANTHROPIC_API_KEY")),
    "AIGOL_GEMINI_API_KEY_PRESENT": bool(os.environ.get("AIGOL_GEMINI_API_KEY")),
    "AIGOL_MISTRAL_API_KEY_PRESENT": bool(os.environ.get("AIGOL_MISTRAL_API_KEY")),
}

for name, present in checks.items():
    print(f"{name}={present}")

sys.exit(0 if checks["AIGOL_OPENAI_API_KEY_PRESENT"] else 1)
PY
```

Expected OpenAI certification prerequisite:

```text
AIGOL_OPENAI_API_KEY_PRESENT=True
```

For the current first live cognition-provider certification, expected additional marker:

```text
OPENAI_API_KEY_PRESENT=True
```

No command in this procedure prints credential values.

## 11. Live Certification Command After Bootstrap

After verification succeeds, the operator may run:

```sh
python -m aigol.runtime.first_live_cognition_provider_certification
```

Expected success markers:

```text
provider_selected=openai
provider_invoked=True
provider_response_received=True
human_confirmation_recorded=True
replay_reconstructed=True
FINAL_VERDICT=FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED
```

Expected bootstrap failure markers:

```text
ABORTED_BEFORE_CERTIFICATION=AIGOL_OPENAI_API_KEY_MISSING
ABORTED_BEFORE_CERTIFICATION=OPENAI_API_KEY_MISSING
```

## 12. Future Provider Onboarding Procedure

For every future provider:

1. Add or confirm a secret-free entry in `AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1`.
2. Define exactly one canonical `AIGOL_*` credential reference.
3. Define approved provider-native alias names for operator bootstrap only.
4. Add a propagation rule to the local operator bootstrap template.
5. Add a replay-safe presence diagnostic field.
6. Add dependency failure classification for missing canonical credential reference.
7. Add an operator verification marker.
8. Certify missing-credential fail-closed behavior.
9. Certify live provider invocation only after the canonical credential marker is present.

Provider onboarding must not require replaying, hashing, storing, or printing credential values.

## 13. Pass Criteria

`AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1` is satisfied when:

- the operator has a single canonical bootstrap file location;
- shell startup sources the bootstrap before AiGOL commands run;
- `OPENAI_API_KEY` can deterministically propagate to `AIGOL_OPENAI_API_KEY`;
- canonical `AIGOL_*` variables remain authoritative;
- diagnostics show presence booleans only;
- dependency failure reports missing canonical references without exposing secrets;
- future provider onboarding follows the provider credential registry.

## 14. Failure Criteria

The bootstrap is not sufficient if:

- provider credentials are stored in the repository;
- credential values appear in replay;
- credential hashes appear in replay;
- runtime silently falls back to provider-native aliases;
- IDE-launched processes cannot be verified before certification;
- operators must infer which process environment is authoritative;
- future providers require ad hoc credential naming outside the registry.

## 15. Remaining Operational Caution

This artifact defines the bootstrap procedure. It cannot force an already-running parent process to inherit environment changes made later in a different shell.

If verification fails inside Codex or an IDE but succeeds in an external terminal, the operator must run certification from the verified terminal or restart the IDE/Codex host from a bootstrapped shell.

## 16. Final Verdict

The smallest governance-preserving solution is a local, secret-free operator bootstrap convention that propagates provider-native aliases into canonical `AIGOL_*` credential references before AiGOL runtime begins.

```text
OPERATOR_ENVIRONMENT_BOOTSTRAP_DEFINED
```
