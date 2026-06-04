# AIGOL_OCS_BOUNDARY_CONTRACT_V1

## Status

Contract model.

## Boundary Definition

OCS is a bounded cognition and context assembly layer.

It answers:

```text
What governed context is relevant, normalized, and safe to hand to the next
proposal or task-intake stage?
```

It does not answer:

```text
May this operation execute?
```

Execution permission remains with the existing governed authorization,
approval, replay review, and worker execution substrate.

## Allowed Position

OCS may sit after conversation, replay inspection, approval evidence, domain
registry resolution, provider proposal evidence, or worker result evidence.

OCS may sit before:

- native development task intake;
- Resource Selection;
- PPP;
- provider proposal production;
- clarification;
- approval-required surfacing.

OCS may not sit after authorization as a hidden execution modifier.

## Read Authority

OCS may read only replay-visible, governance-visible, or explicitly referenced
source artifacts.

Permitted read classes:

- current operator request and session metadata;
- conversation turn artifacts;
- replay reconstruction and chain inspection outputs;
- domain registry and domain bundle registry entries;
- domain foundation artifacts and certifications;
- human approval, rejection, and modification request artifacts;
- provider necessity classifications;
- validated provider proposal artifacts;
- worker assignment, invocation, result, and validation artifacts;
- governed termination artifacts;
- known gap and limitation artifacts.

## Forbidden Reads

OCS must not read:

- secrets, credentials, tokens, or private environment values;
- hidden provider messages not recorded as governed artifacts;
- filesystem content outside explicit governed references;
- live worker process memory;
- broker, exchange, deployment, or production API state;
- mutable runtime scratch state as authority-bearing context;
- hidden vector memory or unstated long-term memory;
- unvalidated generated files as canonical context;
- personal or regulated data unless a future governed artifact explicitly
  authorizes and scopes that read.

## Write Boundary

This contract does not authorize writes.

A future OCS runtime may write only explicitly defined OCS evidence artifacts
that are append-only, replay-visible, and non-authority-bearing.

OCS must never write directly to:

- source replay;
- constitutional governance artifacts;
- runtime implementation files;
- domain foundation artifacts;
- executable bundle outputs;
- worker outputs;
- deployment targets.

## Failure Boundary

OCS must fail closed when:

- required context is missing;
- an input reference is invalid;
- an input hash does not match;
- a context source is ambiguous;
- a domain is ambiguous;
- an approval state is ambiguous;
- a provider or worker role is ambiguous;
- context would require forbidden reads;
- an output would carry prohibited authority;
- a terminated operation is referenced as resumable.

## Human Authority Boundary

OCS may recommend a safe next governed handoff.

OCS may not approve that handoff, approve downstream execution, or infer human
approval from conversation content.
