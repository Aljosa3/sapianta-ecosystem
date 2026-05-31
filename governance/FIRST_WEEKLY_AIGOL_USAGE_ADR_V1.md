# FIRST_WEEKLY_AIGOL_USAGE_ADR_V1

## Decision

The next major development priority should be replay/operator usage visibility, not provider expansion, worker expansion, or authorization expansion.

## Context

`OPERATOR_EXPERIENCE_HARDENING_V1` made AiGOL easier to operate by adding default operation ids and operation replay lookup.

This milestone used AiGOL repeatedly to observe actual needs.

## Evidence

15 operator attempts were performed:

- 12 successful governed operations;
- 3 fail-closed invalid attempts;
- 0 unexpected failures;
- 12 successful replay chains;
- 72 successful replay files;
- 0 invalid fail-case files created.

## Rationale

Successful operation replay is already useful. The operator can inspect a known operation id and see proposal, authorization, worker, and outcome evidence.

The remaining pain is weekly operational visibility:

- operation counting is manual;
- success/failure rates are manual;
- early fail-closed attempts are not full replay chains;
- there is no operation-level ledger or recent-operation index.

## Rejected Next Priorities

### New Worker

Rejected for now.

Observed usage requested only filesystem create-file.

### New Provider

Rejected for now.

The weekly run did not measure external provider reliability.

### Authorization Expansion

Rejected.

Authorization friction was low and the existing model worked.

### Orchestration

Rejected.

No evidence supports orchestration, planning, reflection, or autonomous dispatch.

## Decision

Proceed next with replay/operator usage visibility hardening.

Architecture expansion remains deferred until operational evidence requires it.
