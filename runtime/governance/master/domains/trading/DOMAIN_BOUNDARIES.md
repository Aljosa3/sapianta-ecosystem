# SAPIANTA Trading Domain Boundaries

## Boundary Statement

Trading is a domain-specific validation and simulation environment. It must not become a live trading system without explicit governance approval.

Trading must not be framed as an AI trading bot.

## Allowed Current Scope

- deterministic proposal construction
- policy validation
- advisory generation
- decision envelope construction
- contract validation
- replay verification
- ledger integrity inspection
- deterministic simulation
- ranking configuration research
- paper-only future experiments

## Forbidden Current Scope

- live trading
- autonomous execution
- broker order routing
- portfolio management
- self-promoting strategy changes
- runtime market ingestion mandate
- production deployment
- policy bypass
- Decision Spine mutation
- policy engine mutation
- autonomous strategy-to-execution path

## Domain Separation

Trading may reference domain-specific inputs, policies, and simulation artifacts.

Trading must remain separated from:
- governance rule mutation
- policy engine mutation
- Decision Spine mutation
- broker execution authority
- autonomous research promotion authority
- production deployment authority

## Dangerous Activation Areas

- `sapianta_system/runtime/production/trading_runner.py`
- `sapianta_system/runtime/production/strategy_promotion_engine.py`
- `sapianta-domain-trading/src/sapianta_domain_trading/ibkr/`
- strategy evolution to production paths
- any ledger write occurring during replay

These areas require review before use as any activated runtime path.

## Boundary Preservation Rule

Any future Trading change that introduces execution, broker access, live data authority, strategy promotion, or production deployment must be treated as a structural domain change requiring ADR, milestone, validation, replay-safety review, and human approval.
