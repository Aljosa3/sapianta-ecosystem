# SAPIANTA Trading Domain System State

## Document Role

This is an inspection-only architectural state reconstruction for the dormant Trading domain.

It is documentation-only. It does not activate trading, create runtime integration, modify policy logic, modify the Decision Spine, or expand governance.

## Current Status

Trading is a latent future capability domain with partially implemented deterministic foundations.

Current classification:
- dormant
- validation-oriented
- replay/simulation-oriented
- partially implemented
- not production-active
- not autonomous
- not an AI trading bot

Most accurate framing:
Trading is a governance proving domain, replay-safe validation environment, and deterministic policy experimentation layer.

## Evidence Summary

Concrete Trading artifacts exist in multiple places:

- `sapianta-domain-trading/`
- `sapianta_system/governance/domains/trading/`
- `sapianta_system/runtime/domains/trading/`
- `sapianta_system/runtime/modules/trading_validation/`
- `sapianta_system/runtime/trading/`
- `sapianta_system/tests/domains/trading/`
- `sapianta_system/tests/runtime/trading/`
- `sapianta_system/tests/runtime/trading_validation/`
- `sapianta_system/scripts/validation/validate_trading_*.py`

These artifacts support deterministic contracts, policy validation, decision-to-intent mapping, replay tests, rolling simulation, ranking configuration, and governance validation.

## What Actually Exists

Implemented foundations:
- immutable trading decision proposal model in `sapianta-domain-trading/src/sapianta_domain_trading/proposal.py`
- deterministic policy evaluation in `sapianta-domain-trading/src/sapianta_domain_trading/policy.py`
- advisory wrapper in `sapianta-domain-trading/src/sapianta_domain_trading/advisory.py`
- decision envelope builder in `sapianta-domain-trading/src/sapianta_domain_trading/envelope.py`
- append-only ledger and replay verification in `sapianta-domain-trading/src/sapianta_domain_trading/ledger.py`
- replay pipeline in `sapianta-domain-trading/src/sapianta_domain_trading/replay.py`
- provenance graph helper in `sapianta-domain-trading/src/sapianta_domain_trading/provenance.py`
- IBKR connectivity check only in `sapianta-domain-trading/src/sapianta_domain_trading/ibkr/ibkr_connection.py`
- trading event registry and contracts under `sapianta_system/governance/domains/trading/`
- deterministic decision-to-intent transformer in `sapianta_system/runtime/domains/trading/decision_to_intent.py`
- trading validation contract and validator under `sapianta_system/runtime/modules/trading_validation/`
- rolling simulation, ranking engine, scoring components, config loader, and deterministic utilities under `sapianta_system/runtime/trading/`
- governance-level validation scripts under `sapianta_system/scripts/validation/`
- domain and runtime tests for contracts, replay determinism, and validation

## Current Maturity Level

Maturity: LEVEL 2

Reason:
Trading has deterministic validation, contracts, tests, replay/simulation foundations, policy hashing, ranking configuration, and domain-specific runtime scaffolding. It is beyond conceptual documentation.

Trading is not LEVEL 3 because runtime-safe activation, production orchestration, live execution governance, operational safety boundaries, market-data authority, broker execution approval, and deployment semantics are not established.

## Important Caveats

- `sapianta-domain-trading` replay currently rebuilds envelopes through a path that records to the ledger, so replay is not cleanly side-effect-free.
- `sapianta_system/runtime/production/trading_runner.py` exists but uses simulated random prices and should be treated as dormant/unsafe for production activation.
- `sapianta-domain-trading/scripts/check_determinism.py` and `check_hash_reproducibility.py` appear inconsistent with the current proposal/advisory/envelope function signatures.
- Trading submodules `data_source.py`, `indicators.py`, and `pipeline.py` under `sapianta-domain-trading/src/sapianta_domain_trading/trading/` are empty while tests reference them.
- IBKR support is connectivity-only. It is not broker integration, order routing, or execution authorization.

## Current Product/Architecture Position

Trading should remain a deterministic policy experimentation and validation domain. It must not be presented as a production trading system, an autonomous execution system, or an AI trading bot.
