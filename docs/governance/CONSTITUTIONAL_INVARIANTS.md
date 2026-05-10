# Constitutional Invariants

Status: canonical constitutional specification.

Constitutional invariants define what must not be violated by runtime behavior, generated development work, domain proposals, governance docs, or future architecture evolution.

## Replay Invariants

Replay must be read-only.

Replay verification must not:
- mutate ledgers;
- mutate commands;
- mutate fills;
- mutate finalized envelopes;
- mutate governance evidence;
- append replay-generated state;
- silently repair divergence.

Replay evidence must remain:
- deterministic;
- hash-verifiable;
- canonically serialized where implemented;
- comparable across repeated evaluation.

Replay ambiguity must fail closed or escalate according to the active governance context.

## Layer Invariants

Layer 0 must remain immutable.

Layer 0 includes:
- constitutional architecture rules;
- deterministic guarantees;
- kernel freeze boundaries;
- system integrity constraints.

Layer 1 must remain immutable.

Layer 1 includes:
- canonical artifact definitions;
- envelope and ledger schemas;
- replay identity surfaces;
- stable audit structures.

Layer 2 must remain restricted.

Layer 2 may not be changed by ordinary autonomous development without governance review.

Layer 3 must remain governed.

Layer 3 may review, certify, block, or route proposals, but must not silently rewrite constitutional authority.

Layer 4 must remain bounded.

Layer 4 may evolve inside allowed development and research scopes, but cannot override higher layers.

## Mutation Boundary Invariants

Protected domains must reject unauthorized mutation. Protected evidence includes:

- governance and constitution paths;
- replay paths;
- kernel paths;
- ledger paths;
- safety paths;
- Layer 2 decision paths;
- canonical trusted scopes;
- finalized audit records.

Autonomous systems must not:
- mutate immutable layers;
- infer missing constitutional state;
- bypass certification;
- bypass replay verification;
- activate dormant governance memory;
- promote experimental work to canonical authority without governed evidence.

## Fail-Closed Invariants

The system must fail closed when:

- a protected path is targeted;
- artifact type is missing for certification;
- generated code is invalid;
- strict tests fail;
- replay hashes diverge;
- proposal intent is ambiguous;
- governance scope is unclear;
- constitutional precedence is unresolved;
- domain lock authorization is missing;
- execution semantics are ambiguous.

Fail-closed may mean block, reject, escalate, quarantine, or mark invalid depending on the specific component.

## Deterministic Invariants

Where the system claims replay or constitutional determinism, it must use:

- stable hashes;
- stable ordering;
- canonical serialization;
- deterministic decision records;
- deterministic classification;
- explicit evidence chains.

Known operational exceptions exist in development-only surfaces, such as wall-clock process guards and timestamped approval placeholders. These must not be treated as constitutional replay evidence.

## Certification Invariants

Certification must depend on evidence, not assertion.

Observed certification dependencies include:

- ArchitectureGuardian validation;
- strict generated tests;
- artifact registry classification;
- replay chain verification;
- constitutional digest or export hash verification in domain flows;
- proposal and envelope certification hashes.

Missing certification evidence must not be silently synthesized.

## Execution Boundary Invariants

Execution proposal review is not execution.

The constitutional execution boundary currently supports:

- deterministic proposal review;
- replay-safe proposal certification;
- canonical execution envelopes;
- offline fake paper command execution in the domain-specific offline model.

It does not support:

- broker connectivity;
- live trading;
- production execution;
- autonomous trading;
- market data dependence;
- order placement;
- hidden execution scheduling.

## Governance Memory Invariants

Governance memory under `runtime/governance/master` is dormant, observational, and documentation-first.

It must not be interpreted as:

- runtime governance activation;
- active policy enforcement;
- Decision Spine mutation;
- automatic approval validation;
- governance arbitration.

