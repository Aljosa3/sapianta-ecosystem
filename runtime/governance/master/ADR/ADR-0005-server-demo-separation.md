# ADR-0005: Server/Demo Separation

## STATUS

Accepted.

## CONTEXT

SAPIANTA currently needs product-facing progress for AI Decision Validator while preserving a stable dormant governance foundation. Combining server/demo work with governance activation would create ambiguity about whether UI and product flows imply runtime enforcement.

The market-facing product is AI Decision Validator, and the near-term focus is demo clarity, audit viewer experience, cinematic landing page, EU AI Act positioning, and enterprise demo flow.

ACTIVE has no runtime meaning.

## DECISION

Keep the server/demo branch intentionally separated from dormant governance foundation work. Server/demo changes may improve product presentation and user experience, but they must not imply governance activation, runtime enforcement, policy execution, or Decision Spine changes.

Governance remains dormant, replay-safe, and observational only.

## CONSEQUENCES

Product work can proceed without destabilizing governance architecture. Future runtime-safe activation remains a separate phase requiring explicit ADRs, milestone summaries, tests, and human approval.

## NON-GOALS

- Runtime governance activation through demo work
- Enforcement activation through UI
- Policy engine changes
- Decision Spine changes
- Automatic git execution
