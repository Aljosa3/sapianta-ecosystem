# SAPIANTA Product Lifecycle Architecture v1

## Document Role

This document defines the local development, governed source, stable demo, and future production lifecycle model for Product 1.

This is documentation and workflow foundation only. It does not redesign the ecosystem foundation, move repositories, activate runtime governance, modify runtime logic, or change protected governance/runtime semantics.

## Product 1

Product 1 is the AI Decision Validator.

Primary product focus:
- EU AI Act execution governance
- enterprise demo UX
- audit UX
- replay UX
- explainability UX
- unknown-decision governance
- stable demo release workflow

## Lifecycle Layers

### Local Innovation Layer

The local PC workspace at `~/work/sapianta` is the Local Innovation Layer.

This layer is used for:
- productization experiments
- enterprise demo UX development
- audit viewer iteration
- replay visualization iteration
- explainability UX exploration
- unknown-decision governance UX design
- local validation before source promotion

Local work may be experimental, but it must preserve deterministic semantics, governance-first architecture, replay safety, and audit lineage integrity.

### Governed Source Layer

GitHub is the Governed Source Layer.

GitHub acts as the governed release registry for stable source states. Work is pushed only after local validation and human review of the intended state.

The governed source layer records:
- stable checkpoints
- reviewed feature branches
- optional demo release branches
- release notes
- source lineage for demo updates

### Stable Demo Runtime

The Hetzner server is the Stable Demo Runtime.

The demo server is a controlled showcase node, not a live experimentation node. It should receive updates only after a stable checkpoint exists in the governed source layer.

The demo server is used for:
- enterprise demonstrations
- stable Product 1 showcase flows
- audit viewer demonstrations
- replay demonstrations
- Swagger/API documentation checks
- controlled validation after server pull and service restart

### Production Runtime

The Production Runtime is a future strict deterministic runtime.

Production is not activated by this lifecycle document. Future production runtime work must preserve deterministic behavior, governance approval requirements, replay safety, audit lineage, and strict separation from demo experimentation.

## Branch Model

The branch model is:
- `main` or `master`: stable governed demo runtime source
- `feature/*`: experimental productization work
- `release/*`: optional demo release branches for controlled showcase checkpoints

Feature branches are the normal place for Product 1 iteration. `main` or `master` should represent a stable state suitable for the governed demo runtime. `release/*` branches may be used when a demo checkpoint needs additional isolation.

## Deployment Flow

The Product 1 lifecycle flow is:

```text
LOCAL DEV
  -> FEATURE BRANCH
  -> LOCAL VALIDATION
  -> COMMIT
  -> GITHUB PUSH
  -> RELEASE DECISION
  -> SERVER PULL
  -> DEMO VALIDATION
```

Server updates are intentionally downstream of local validation, commit, GitHub push, and release decision. The server should not be used as the place where Product 1 experiments are discovered.

## Demo vs Production Semantics

Demo semantics:
- controlled showcase runtime
- stable enough for enterprise walkthroughs
- may include productized UX and demo-oriented flows
- must not imply autonomous governance activation
- must not imply production enforcement
- must preserve audit and replay narrative integrity

Production semantics:
- future strict deterministic runtime
- requires explicit human-approved architecture and operational readiness
- requires governed activation review
- requires deterministic execution guarantees
- requires production-grade audit lineage and replay safety
- remains separate from demo workflow

## EU AI Act Positioning

Product 1 positions SAPIANTA as an execution governance and evidence layer for AI decision systems.

The EU AI Act positioning should emphasize:
- decision validation before or around operational use
- auditability of decision outcomes
- explainability evidence for enterprise review
- replayable governance evidence
- operational risk framing
- human approval where governance coverage is unknown

This positioning is product and demo narrative. It does not itself create legal compliance, production enforcement, or automated regulatory certification.

## AI Decision Validator Positioning

The AI Decision Validator is the first product expression of the governed SAPIANTA architecture.

It should demonstrate:
- decision intake
- policy and governance evaluation
- audit evidence
- replay evidence
- explainability evidence
- unknown-decision detection
- human-reviewed governance extension paths

The enterprise demo should make the validation journey legible, credible, and repeatable.

## Unknown-Decision Governance

Unknown-decision governance handles cases where an incoming decision cannot be fully evaluated by existing governance coverage.

Required semantics:
- coverage unknown
- governance gap detected
- proposal generation
- human approval required
- dormant validation state
- activation review

Unknown decisions must not silently become accepted decisions. They should enter a dormant validation state until a human-reviewed governance extension and activation review resolve the gap.

The proposal generation step may produce candidate governance coverage, but generated proposals are not active governance. Human approval is required before any activation path.

## Replay Governance: AI Flight Recorder

Replay governance is positioned as the AI Flight Recorder for Product 1.

It should preserve and present:
- decision inputs
- validation path
- policy and governance context
- audit events
- explainability outputs
- unknown-decision handling
- human approval lineage where applicable

The AI Flight Recorder framing should make audit and replay understandable to enterprise reviewers without weakening deterministic replay semantics.

## Demo Server Rule

The demo server is a controlled showcase node, not a live experimentation node.

All demo server updates must follow the lifecycle flow:

```text
LOCAL DEV -> FEATURE BRANCH -> LOCAL VALIDATION -> COMMIT -> GITHUB PUSH -> RELEASE DECISION -> SERVER PULL -> DEMO VALIDATION
```

No live experimentation, unreviewed runtime modification, or foundation redesign should happen on the demo server.
