# Proposal Bridge Terminology Findings V1

Status: terminology review for proposal-only bridge consistency.

## Finding Summary

The reviewed runtime and governance artifacts preserve the proposal-only invariant behaviorally. They do not state that an LLM executes directly.

However, earlier milestone wording uses transitional terms such as:

- cognition-to-execution bridge
- cognition execution request
- cognition execution authorization

These terms are acceptable as historical artifact names but should be interpreted constitutionally as:

- cognition proposal to governed execution request
- proposal-derived execution request
- AiGOL-governed authorization

## Canonical Terminology

Prefer:

- cognition proposal
- untrusted proposal input
- proposal-to-execution-request bridge
- governed execution request
- deterministic worker execution
- AiGOL-governed authorization

Avoid in future artifacts:

- cognition executes
- LLM executes
- direct cognition-to-execution
- autonomous LLM execution
- LLM-driven execution

## Runtime Naming Assessment

Runtime function and file names retain historical milestone terms for continuity:

- `minimal_cognition_to_execution_bridge.py`
- `execute_cognition_to_execution_bridge`
- `execute_authorized_cognition_request`

These names do not grant execution authority to cognition. The implementation still requires:

- untrusted input capture
- deterministic normalization
- validation
- explicit authorization
- deterministic worker/capability execution
- replay-visible result capture

## Recommendation

Future governance and runtime-facing documentation should describe the bridge as a proposal-to-execution-request bridge.

Runtime renaming is not recommended inside this review milestone because it would create churn without changing authority semantics.

## Terminology Certification

The reviewed bridge must be read as:

```text
LLM proposal -> AiGOL validation and authorization -> worker execution -> replay evidence
```

It must not be read as:

```text
LLM execution
```
