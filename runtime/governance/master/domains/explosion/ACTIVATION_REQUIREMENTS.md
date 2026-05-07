# SAPIANTA Explosion Domain Activation Requirements

## Activation Status

Explosion activation is NOT APPROVED and NOT IMPLEMENTED.

Explosion must remain dormant until explicit governance artifacts define what the domain is and what it is allowed to do.

## Requirements Before Explosion Activation

### Domain Definition Requirements

- explicit Explosion domain intent document
- explicit domain boundary document
- explicit non-goals and forbidden paths
- domain event registry if events are needed
- artifact schema for acceleration outputs
- formal relation to CAL, CCS, ASF, GAD, and sandbox layers

### Governance Requirements

- explicit activation ADR
- explicit autonomy level transition review
- human authority model
- promotion gate compatibility
- artifact lineage requirements
- replay-safety review
- rollback and halt semantics
- proof that autonomy cannot self-increase

### Runtime Safety Requirements

- isolated sandbox namespace
- no production write authority
- no governance write authority
- no Decision Spine mutation
- no policy engine mutation
- no runtime integration without approval
- deterministic scheduling if loops are introduced
- deterministic artifact ordering
- fail-closed execution guard
- mutation guard and architecture guardian enforcement

### Validation Requirements

- deterministic test suite
- replay validation
- artifact lineage validation
- sandbox containment tests
- approval gate tests
- no hidden control flow tests
- no autonomous deployment tests
- no policy mutation tests

## Requirements Before Autonomous Optimization

- explicit scope limits
- max iteration limits
- baseline lock
- behavior drift detection
- deterministic ranking criteria
- no candidate self-promotion
- approval-gated promotion only
- incident artifact on failure

## Requirements Before Runtime Execution

Explosion should not receive runtime execution authority without:
- new ADR
- domain contract
- runtime boundary spec
- governance review
- replay-safety validation
- human approval

## Activation Blockers

- no formal Explosion domain exists
- no Explosion contract exists
- no Explosion event registry exists
- no Explosion test suite exists
- adjacent research/evolution code includes randomness and timestamps
- activation semantics are not defined
- production boundaries are not proven

## Required Current State

Explosion remains dormant, experimental, and governance-dependent.
