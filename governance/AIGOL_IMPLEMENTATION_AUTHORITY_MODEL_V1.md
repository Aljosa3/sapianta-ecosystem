# AIGOL_IMPLEMENTATION_AUTHORITY_MODEL_V1

## Status

Contract-only authority model.

## Authority Principles

1. Human operator retains final implementation authority.
2. Provider output is content evidence, not authority.
3. AiGOL may validate and reject but may not self-authorize.
4. OCS may generate bounded cognition and PPP candidates only.
5. PPP and proposal artifacts may not authorize implementation.
6. Implementation handoff is not implementation authorization.
7. Execution readiness is not execution authorization.
8. Filesystem mutation requires exact mutation authorization.
9. Replay verifies authority lineage but does not grant authority.
10. Approval scopes are single-purpose and non-transferable.

## Authorized Actors

| Actor | May Authorize Implementation Creation | Notes |
| --- | --- | --- |
| Human operator | Yes | Only through explicit replay-visible approval artifacts. |
| AiGOL runtime | No | May validate, fail closed, and prepare evidence only. |
| OCS | No | May generate proposal-only PPP candidates. |
| PPP | No | May route and prepare proposal evidence only. |
| Provider | No | May return generated content after authorization; cannot approve it. |
| Worker | No | May produce bounded results only when governed; cannot authorize mutation. |
| Replay | No | May reconstruct and verify lineage only. |

## Required Approval Gates

### Gate 1: Candidate Selection Authorization

Purpose:

Select one OCS/PPP/implementation handoff candidate for downstream processing.

Required artifact:

```text
IMPLEMENTATION_CANDIDATE_SELECTION_AUTHORIZATION_V1
```

Must bind:

- candidate reference and hash;
- operator identity;
- decision timestamp;
- selected scope;
- selected target domain/resource/worker;
- explicit non-authorization of provider invocation and mutation.

### Gate 2: Provider Implementation Generation Authorization

Purpose:

Authorize an approved provider to generate implementation content.

Required artifact:

```text
PROVIDER_IMPLEMENTATION_GENERATION_AUTHORIZATION_V1
```

Must bind:

- selected candidate reference and hash;
- implementation handoff reference and hash;
- provider id and version;
- provider adapter reference;
- target manifest constraints;
- allowed file paths and operation modes;
- maximum file count;
- allowed artifact types;
- forbidden capabilities;
- explicit non-authorization of filesystem mutation.

### Gate 3: Generated Content Acceptance Authorization

Purpose:

Human operator accepts generated content after validation.

Required artifact:

```text
IMPLEMENTATION_CONTENT_ACCEPTANCE_AUTHORIZATION_V1
```

Must bind:

- implementation manifest reference and hash;
- provider response reference and hash;
- code validation reference and hash;
- test validation reference and hash;
- rendered diff or content review hash;
- operator decision;
- explicit accept, reject, or request-modification outcome;
- explicit non-authorization of mutation unless Gate 4 is separately present.

### Gate 4: Filesystem Mutation Authorization

Purpose:

Authorize applying exact validated and accepted content to the workspace.

Required artifact:

```text
IMPLEMENTATION_FILESYSTEM_MUTATION_AUTHORIZATION_V1
```

Must bind:

- content acceptance authorization reference and hash;
- implementation manifest reference and hash;
- exact file entries;
- exact operation type per file;
- exact target path per file;
- exact content hash per file;
- preflight target state per file;
- validation references and hashes;
- canonical chain id;
- workspace root;
- mutation mode;
- no authority transfer.

## Approval Non-Reuse Rule

An approval from one gate cannot satisfy any other gate.

Examples:

- candidate selection does not authorize provider invocation;
- provider generation authorization does not authorize content acceptance;
- content acceptance does not authorize filesystem mutation;
- filesystem mutation authorization does not authorize execution;
- execution request authorization does not authorize implementation mutation.

## Forbidden Authority Claims

Generated content, provider responses, proposals, tests, manifests, and
validation artifacts must not claim:

- execution authority;
- dispatch authority;
- worker invocation authority;
- provider authority;
- governance mutation authority;
- replay mutation authority;
- automatic approval;
- automatic implementation;
- authority transfer.

## Fail-Closed Authority Conditions

The lifecycle must fail closed when:

- any required approval is absent;
- approval scope mismatches;
- approval hash mismatches;
- provider id mismatches;
- manifest hash mismatches;
- generated content requests unauthorized paths;
- generated content requests forbidden operations;
- tests are missing or unbound;
- validation fails;
- mutation target state differs from authorization;
- replay reconstruction fails.

