# AIGOL_CANONICAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_ACLI_ENTRY_FIX_V1

## Status

Canonical ACLI routing entry fix implemented and regression covered.

No worker was implemented. No worker invocation was implemented. No execution authorization runtime behavior was changed. No repair runtime or retry behavior was implemented.

## Purpose

Register `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` in the canonical conversational router so reviewed domain approval and authorization-entry prompts do not fall through to `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`.

## Defect

`AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` was only reachable through interactive pre-routing for a subset of approval prompts. The canonical conversational router did not recognize the stage, and the approval-entry detector did not accept:

```text
Authorize FreshDomain domain artifact request.
```

This allowed operator continuation prompts to route to the provider-assisted fallback and fail closed.

## Implementation

The fix adds:

- canonical workflow registration for `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW`;
- canonical prompt routing for reviewed domain approval and authorization-entry prompts;
- support for `Authorize <Domain> domain artifact request`;
- CLI routing visibility alignment with the canonical stage name;
- regression coverage for direct router behavior and interactive ACLI binding.

Supported prompts:

```text
Approve FreshDomain for domain artifact creation.
Approve reviewed FreshDomain workflow.
Continue FreshDomain to authorization.
Authorize FreshDomain domain artifact request.
```

## Binding

The canonical route is bound to the existing approval-entry path:

```text
AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
-> domain_handoff_review_approval_binding_runtime
-> DOMAIN_APPROVAL_BINDING_ARTIFACT_V1
-> DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1
-> DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1
```

The runtime remains bounded. It creates authorization-entry evidence and execution-ready continuation evidence, but does not invoke authorization, workers, execution, repair, or retry behavior.

## Governance Boundaries

Preserved:

- provider fallback prevention for certified prompts;
- fail-closed behavior for unsupported approval prompts;
- replay-visible routing decisions;
- replay-visible approval binding;
- no provider invocation;
- no worker invocation;
- no execution start;
- no domain creation.

## Validation

Executed:

```bash
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_domain_handoff_review_approval_binding_runtime_v1.py
```

Result:

```text
41 passed
```

Additional validation:

```bash
python -m json.tool AIGOL_CANONICAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_ACLI_ENTRY_FIX_ACCEPTANCE_EVIDENCE.json
python -m json.tool AIGOL_CANONICAL_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_ACLI_ENTRY_FIX_CERTIFICATION.json
git diff --check
```

## Final Outputs

```text
CANONICAL_ACLI_ENTRY_REGISTERED = TRUE
AUTHORIZE_PROMPT_SUPPORTED = TRUE
DEFAULT_PROVIDER_FALLBACK_PREVENTED = TRUE
AUTHORIZATION_ENTRY_REACHABLE_FROM_ACLI = TRUE
REPLAY_CONTINUITY_PRESERVED = TRUE
READY_FOR_REAL_AUTHORIZATION_ENTRY_ACCEPTANCE = TRUE
```
