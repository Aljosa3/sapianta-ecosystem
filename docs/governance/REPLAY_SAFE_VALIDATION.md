# Replay-Safe Validation

Status: constitutional governance finalization artifact.

## Replay-Safe Validation Model

Replay-safe validation means that governance evidence can be inspected, hashed, compared, and certified without mutating runtime state or rewriting evidence history.

The conformance system follows this model by:

- reading files only;
- using deterministic rule definitions;
- producing sorted deterministic report output;
- preserving known drift as evidence;
- avoiding runtime repair or mutation.

## Replay-Critical Artifacts

Replay-critical artifacts include:

- constitutional specification documents;
- canonical layer model;
- constitutional invariants;
- enforcement hierarchy;
- lineage model;
- conformance report JSON;
- conformance evidence markdown;
- Layer 0 freeze manifest;
- replay engine and chain verifier code;
- finalized envelopes and hashes where domain-specific components produce them.

## Replay Evidence Chain

The finalization evidence chain is:

1. governance audit documents;
2. constitutional specification documents;
3. conformance engine rules and models;
4. conformance report;
5. finalization manifest;
6. milestone certification;
7. validation commands.

This chain is replay-safe because validation reads evidence and reports status without modifying runtime behavior.

## Replay Assumptions

Replay-safe validation assumes:

- file contents are available at the referenced paths;
- deterministic serialization remains stable;
- conformance rules remain explicit;
- evidence files are not silently rewritten;
- runtime checks are evaluated as evidence surfaces, not executed as repairs.

## Replay Limitations

Replay-safe validation does not prove:

- full formal semantic equivalence of every runtime path;
- shell hook execution behavior beyond token/evidence checks;
- production-grade rollback behavior;
- cross-repository enforcement uniformity;
- legal or regulatory compliance.

These limitations are part of the finalization evidence and must remain visible.

