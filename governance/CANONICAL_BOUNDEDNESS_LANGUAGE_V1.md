# Canonical Boundedness Language V1

Status: boundedness vocabulary canonicalization only.

## Canonical Definition

Boundedness is the constitutional constraint that limits scope, authority, persistence, lifecycle progression, and interpretation.

Boundedness prevents capability drift.

## Canonical Terms

### Bounded

Bounded means explicit in scope, limited in authority, replay-visible, and constrained by termination or fail-closed rules.

### Fail-Closed

Fail-closed means ambiguity, invalid transition, lineage corruption, authority drift, hidden continuation, or unverifiable evidence causes deterministic rejection or terminal failure.

Fail-closed does not mean repair, retry, inference, or autonomous recovery.

### Isolation

Isolation means separation between scopes that must not contaminate one another.

Canonical isolation examples:

- constitutional substrate versus runtime userspace
- session replay scope versus other session replay scopes
- identity continuity versus hidden persistence
- orchestration concept versus execution coordination

### Containment

Containment means bounded runtime or semantic participation cannot escape its declared scope.

Containment prohibits authority leakage, hidden state transfer, and cross-boundary mutation.

### Termination

Termination is explicit closure of a bounded lifecycle or interaction.

Termination must be replay-visible, deterministic, final, and non-persistent.

### Non-Persistence

Non-persistence means no hidden runtime, cognition, orchestration, or identity state survives beyond its explicit bounded scope.

## Canonical Rule

When a layer uses the term bounded, it must preserve:

- explicit scope
- replay visibility
- authority separation
- fail-closed ambiguity handling
- no hidden continuation
- explicit termination where lifecycle is present

