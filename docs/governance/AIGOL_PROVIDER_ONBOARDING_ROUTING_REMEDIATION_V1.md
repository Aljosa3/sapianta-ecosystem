# AIGOL_PROVIDER_ONBOARDING_ROUTING_REMEDIATION_V1

Status: implemented and executable.

## Goal

Connect the certified Provider Onboarding Domain into live ACLI routing so normal operator prompts such as `Dodaj Gemini.` no longer fall through to generic clarification or compliance-domain clarification.

## Remediation Scope

The remediation adds a deterministic ACLI workflow route:

```text
PROVIDER_ONBOARDING_DOMAIN
```

The route detects:

- `Dodaj Claude`
- `Dodaj Gemini`
- `Dodaj Mistral`
- `Želim uporabljati Claude`
- `Onemogoči Claude`

## Preserved Boundaries

The route only selects the certified provider onboarding domain. It does not:

- invoke providers;
- invoke workers;
- authorize execution;
- bypass human approval;
- bypass replay.

Provider onboarding actions remain governed by the Provider Onboarding Domain and Provider Credential Vault lifecycle controls.

## Certification

Required validation:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_acli_dogfood_live_operator_certification_v1.py
python -m py_compile aigol/runtime/conversational_cli_runtime.py
python -m aigol.runtime.acli_dogfood_live_operator_certification_v1
git diff --check
```

## Final Verdict

The remediation is successful when `AIGOL_ACLI_DOGFOOD_LIVE_OPERATOR_CERTIFICATION_V1` returns:

```text
ACLI_LIVE_OPERATOR_READY
```
