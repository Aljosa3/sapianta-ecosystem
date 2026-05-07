# SAPIANTA Trading Domain Current Status

## Status

Trading is dormant and partially implemented.

It is currently:
- validation-only
- simulation-oriented
- replay-oriented
- contract-backed
- governance-bound
- not live
- not autonomous
- not production-active

## Implemented Foundations

### Standalone Trading Package

`sapianta-domain-trading/` contains:
- proposal model
- policy evaluator
- advisory builder
- decision envelope builder
- ledger recorder
- replay verifier
- provenance helper
- IBKR socket connectivity check
- constitutional flow tests
- replay tests
- ledger replay tests

### Governance Artifacts

`sapianta_system/governance/domains/trading/` contains:
- `TRADING_DOMAIN_INTENT_v0.1.md`
- `TRADING_EVENT_REGISTRY_v0.1.json`
- `TRADING_DECISION_CONTRACT_v0.1.json`
- `TRADING_INTENT_CONTRACT_v0.1.json`
- `TRADING_DECISION_TO_INTENT_SPEC_v0.1.md`
- `TRADING_RANKING_CONFIGURATION_v0.1.md`
- `STRATEGY_EVOLUTION_FRAMEWORK_v0.1.md`

### Runtime Validation And Simulation

`sapianta_system/runtime/` contains:
- `runtime/domains/trading/decision_to_intent.py`
- `runtime/modules/trading_validation/validator.py`
- `runtime/modules/trading_validation/policy.py`
- `runtime/modules/trading_validation/trading_policy.py`
- `runtime/modules/trading_validation/correlation_penalty.py`
- `runtime/trading/rolling_sim_v0_1.py`
- `runtime/trading/ranking_engine.py`
- `runtime/trading/scoring_components.py`
- `runtime/trading/config_loader.py`
- `runtime/trading/deterministic_utils.py`

### Tests

Trading tests exist for:
- governance contract loading and validation
- event registry validation
- decision-to-intent runtime determinism
- replay determinism
- trading validation hash determinism
- structural validation
- policy hash order independence
- standalone constitutional flow

## Partially Implemented Or Inconsistent Areas

- Standalone package replay has side effects because envelope building records to the ledger.
- Standalone package scripts appear stale relative to current function signatures.
- Standalone `trading/` data source, indicators, and pipeline files are empty while tests reference expected functions.
- Production trading runner exists but uses random simulated prices and is not runtime-safe activation.
- Strategy promotion and production strategy files exist in `sapianta_system/runtime/production/`, but they are not sufficient production governance.

## Conceptual Or Governance-Only Areas

- strategy evolution framework
- ranking configuration as domain governance
- execution path from trading intent to execution
- promotion of strategies into operational domains
- domain orchestration with risk/compliance domains

## Must Remain Dormant

- live broker execution
- order routing
- production trading runner
- strategy promotion to production
- autonomous strategy evolution into live trading
- runtime market data ingestion for live decisioning
- any path that bypasses Decision Spine, policy validation, approval, ledger, or governance review

## Current Maturity

Maturity: LEVEL 2

Trading has deterministic foundations and tests, but not controlled runtime integration.
