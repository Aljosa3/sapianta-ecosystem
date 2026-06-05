# AIGOL_REAL_IMPLEMENTATION_GENERATION_RECOMMENDED_PATH_V1

## Status

Review-only recommended implementation path.

## Recommended Path

### 1. Contract Milestone

Create:

```text
AIGOL_REAL_IMPLEMENTATION_GENERATION_CONTRACT_V1
```

Define:

- implementation-generation boundary;
- provider implementation request model;
- provider implementation response model;
- implementation content artifact model;
- generated test artifact model;
- validation artifact model;
- human approval scopes;
- filesystem mutation authorization model;
- certification evidence model.

### 2. OCS Candidate Selection Runtime

Create a replay-visible runtime for selecting, rejecting, or requesting
modification to OCS-generated PPP candidates.

This must not invoke PPP or providers.

### 3. Approved OCS-To-PPP Invocation Bridge

Create an approval-gated bridge from selected OCS candidate to PPP/proposal
production.

This must preserve proposal-only boundaries.

### 4. Provider Implementation Request Runtime

Create a new provider boundary distinct from proposal production.

This runtime should request implementation content only after:

- validated implementation handoff;
- explicit human provider-invocation approval;
- exact target manifest constraints;
- replay-visible context and proposal lineage.

### 5. Implementation Content Contract Runtime

Validate normalized provider implementation content before any validation or
application step.

The runtime should fail closed on:

- unknown paths;
- path traversal;
- missing content hashes;
- ambiguous operations;
- unauthorized file types;
- authority-bearing content;
- hidden execution, dispatch, or governance claims.

### 6. Generated Code And Test Validation Runtime

Validate generated code and generated tests in a bounded, replay-visible
validation stage.

Minimum validation:

- parse/syntax checks;
- test collection;
- targeted tests;
- forbidden capability scan;
- dependency policy check;
- governance invariant scan;
- deterministic validation result hash.

### 7. Human Implementation Content Review Runtime

Present generated content, validation results, risks, paths, and diffs for
human decision.

Supported decisions:

- approve application;
- reject;
- request modification.

### 8. Real Implementation Application Runtime

Only after explicit content-acceptance approval, apply generated content with
exact authorized file operations.

Initial scope should be create-only for a tightly bounded target.

Update semantics should be a separate milestone.

### 9. Post-Application Certification Runtime

Verify:

- final file hashes;
- validation evidence;
- replay reconstruction;
- approval lineage;
- mutation authorization;
- post-application test results;
- governance review result.

Then emit final certification JSON.

## Recommended Next Milestone

```text
AIGOL_REAL_IMPLEMENTATION_GENERATION_CONTRACT_V1
```

## Recommended First Runtime After Contract

```text
AIGOL_OCS_CANDIDATE_SELECTION_RUNTIME_V1
```

Rationale:

The first unsafe transition is not file mutation. It is choosing which OCS
candidate may proceed toward PPP and provider activity. Candidate selection
must be replay-visible before provider implementation generation is designed.

