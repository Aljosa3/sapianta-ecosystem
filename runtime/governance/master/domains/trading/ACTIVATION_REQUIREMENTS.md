# SAPIANTA Trading Domain Activation Requirements

## Activation Status

Trading activation is NOT APPROVED and NOT IMPLEMENTED.

Trading must remain dormant until the requirements below exist and are human-approved.

## Requirements Before Trading Activation

### Governance Requirements

- explicit Trading activation ADR
- explicit runtime-safe activation milestone
- updated architecture boundary review
- approval semantics for trading intent and execution request
- human approval model for any broker-facing action
- deterministic rollback and halt semantics
- clear authority boundaries between research, validation, policy, and execution

### Runtime Safety Requirements

- side-effect-free replay path
- validated execution boundary for trading
- fail-closed broker boundary
- deterministic market data snapshot model
- deterministic clock/time handling
- order routing isolation
- no random market data in activated paths
- no live execution without explicit approval artifact
- immutable decision envelope before execution
- ledger write only after approved decision stage

### Validation Requirements

- full trading test suite passing
- contract validators passing
- replay determinism passing
- ledger chain verification passing
- policy hash stability passing
- decision-to-intent determinism passing
- simulation reproducibility passing
- stale standalone scripts reconciled or marked obsolete
- empty trading pipeline modules implemented or tests removed through explicit milestone

### Operational Requirements

- paper-trading-only first activation stage
- dry-run broker adapter before live adapter
- account/risk limits externalized and hash-bound
- kill switch and loss-limit semantics
- audit viewer support for trading envelopes
- deployment isolation
- monitored execution logs

## Requirements Before Autonomous Optimization

- promotion gate must classify and validate strategy changes
- strategy artifacts must be hash-bound and versioned
- evaluation datasets must be deterministic and snapshot-bound
- no strategy may self-promote
- no strategy may change risk controls
- no strategy may bypass policy validation
- promotion must require human approval for operational use

## Requirements Before Runtime Execution

- Decision Spine integration review
- policy engine compatibility review
- execution authorization review
- broker boundary review
- replay-safety review
- explicit human approval

## Activation Blockers

- production runner is not safe for live use
- broker support is connectivity-only
- replay path has side effects in the standalone package
- some referenced standalone trading modules are empty
- operational safety layer is incomplete
- deployment semantics are undefined

## Required Current State

Trading remains dormant, validation-only, and simulation-oriented.
