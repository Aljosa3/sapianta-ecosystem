# AIGOL_LLM_COGNITION_PROVIDER_AUTHORITY_POLICY_V1

## Status

Certified governance policy.

This artifact defines the authority policy for the `COGNITION_PROVIDER` role. It is policy only and does not implement runtime invocation.

## Authority Model

The `COGNITION_PROVIDER` remains non-authoritative.

Required authority flags:

```text
provider_authority = false
approval_authority = false
execution_authority = false
worker_authority = false
governance_authority = false
replay_authority = false
```

Additional preserved boundaries:

```text
implementation_authority = false
domain_creation_authority = false
dispatch_authority = false
memory_mutation_authority = false
policy_override_authority = false
human_authority_replacement = false
```

## Permitted Cognitive Functions

A cognition provider may perform only the following support functions:

- analyze;
- infer;
- compare;
- explain;
- identify uncertainty;
- identify missing information.

These functions are advisory. They do not create AiGOL authority.

## Permitted Artifact Contributions

A cognition provider may contribute candidate material for future governed artifacts:

- findings;
- assumptions;
- alternatives;
- risks;
- uncertainties;
- confidence statements;
- clarification candidates.

Provider-contributed material remains untrusted until AiGOL validates and normalizes it under a later certified runtime.

## Prohibited Authority Claims

A cognition provider output is authority-invalid when it claims or implies:

- approval;
- authorization;
- execution permission;
- implementation permission;
- worker invocation;
- domain creation permission;
- governance mutation;
- replay mutation;
- dispatch control;
- policy override;
- human decision replacement;
- finality over AiGOL decisions.

## Authority Boundary Enforcement Requirements

Future runtimes using this policy must:

- reject missing authority flags;
- reject non-false authority flags;
- reject authority-bearing provider text;
- reject provider output that attempts to mutate governance or replay;
- reject provider output that attempts to authorize execution, implementation, worker invocation, or domain creation;
- mark all accepted cognition-provider output as non-authoritative;
- preserve human review before downstream action.

## Relationship To Existing Provider Model

This policy preserves the existing provider invariant:

- LLM proposes.
- AiGOL governs.
- Worker executes.
- Replay records.

The `COGNITION_PROVIDER` role refines the first line only. The provider may support cognition, but AiGOL remains the governing system and human authority remains the final authority boundary.

## Policy Classification

```text
AIGOL_LLM_COGNITION_PROVIDER_AUTHORITY_POLICY_STATUS = CERTIFIED
```
