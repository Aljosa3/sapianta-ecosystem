# AIGOL_OCS_OUTPUT_MODEL_V1

## Status

Contract model.

## Output Principle

OCS output is proposal-supporting and context-bearing.

OCS output is not authority-bearing.

## Allowed Outputs

OCS may produce:

- read-only analysis artifacts;
- OCS context assembly artifacts;
- governed task-intake candidate artifacts;
- proposal-only PPP handoff artifacts;
- bounded improvement-intent routing artifacts;
- clarification request artifacts;
- no-op or fail-closed status artifacts.

Allowed outputs must include:

- source context reference;
- context hash;
- output type;
- authority flags;
- downstream target;
- known gaps;
- validation scope;
- terminal status.

## Forbidden Outputs

OCS must not produce:

- execution authorization;
- dispatch requests;
- worker invocation requests;
- provider invocation authority;
- executable bundle mutation authorization;
- governance mutation;
- replay mutation;
- domain creation authorization;
- broker or exchange action;
- deployment action;
- approval resume without human decision;
- terminal operation resurrection;
- claims of completed implementation;
- claims of completed OCS certification.

## Output Authority Flags

Every future OCS output artifact must include explicit authority flags.

Required values:

```text
authorizes_execution = false
authorizes_dispatch = false
authorizes_worker_invocation = false
authorizes_provider_invocation = false
authorizes_governance_mutation = false
authorizes_replay_mutation = false
authorizes_domain_creation = false
authorizes_human_approval = false
```

## Output Fail-Closed Rules

OCS output must fail closed when:

- context hash is absent;
- downstream target is ambiguous;
- output type is not allowed;
- authority flags are missing;
- authority flags claim prohibited authority;
- known gaps are omitted;
- approval state is required but unavailable;
- domain or worker resolution is ambiguous;
- provider necessity cannot be determined;
- replay reconstruction cannot validate the context reference.

## Operator-Facing Output

Operator-facing output must distinguish:

- what OCS read;
- what OCS rejected;
- what OCS recommends next;
- what OCS cannot authorize;
- whether human approval is required;
- what remains uncertified.
