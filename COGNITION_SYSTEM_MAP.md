# Cognition System Map

Status: analysis-only topology artifact.

Purpose: map the emergent bounded cognition topology across AiGOL / SAPIANTA.

This artifact does not add runtime behavior, orchestration, autonomous cognition, execution authority, or hidden adaptation.

## High-Level Cognition Topology

```text
Human Authority
  -> constitutional governance
  -> semantic ingress / intent normalization
  -> admissibility and authority checks
  -> replay identity and lineage binding
  -> approval / dispatch boundary states
  -> bounded execution continuity
  -> governed return evidence
  -> replay verification and institutional memory
  -> advisory reflection / future proposal candidates
```

This topology is not a loop of autonomous action. It is a chain of governed judgments with explicit stop points.

## Governance Cognition Graph

```text
[Human Authority]
    |
    v
[L0 System Constitution]
    | constrains
    v
[L1 Canonical Artifact Definitions]
    | stabilizes
    v
[L2 Decision Spine]
    | routes proposals through
    v
[L3 Governance System]
    | certifies / blocks / escalates
    v
[L4 Research / Refinement System]
    | may propose only inside bounded scope
    v
[Execution Layer]
    | may act only through governed, deterministic, ledgered boundaries
    v
[Replay / Ledger / Evidence Memory]
```

Interpretation:

- L0/L1 provide constitutional and schema memory.
- L2 is the restricted decision substrate.
- L3 governs certification and admissibility.
- L4 is where bounded experimentation and proposal generation can exist.
- Execution is downstream and cannot self-authorize.

## Bounded Cognition Lifecycle

```text
Untrusted semantic input
  -> canonical ingress artifact
  -> import validation
  -> semantic proposal candidate
  -> semantic contract candidate
  -> acceptance gate
  -> governed task package preview
  -> human approval gate
  -> governed handoff package preview
  -> explicit dispatch authorization
  -> controlled execution continuity preview
  -> controlled execution handoff
  -> bounded Codex provider
  -> governed return artifact
  -> append-only ledger
  -> replay verification
```

Boundary facts:

- semantic input is not authority;
- approval is not dispatch;
- dispatch authorization is not execution;
- continuity preview is not execution;
- execution is single-path and single-provider;
- governed return persistence is append-only evidence, not self-modifying memory.

## Constitutional Reasoning Diagram

```text
Conflict or request appears
  -> replay safety first
  -> Layer 0 constraints
  -> Layer 1 artifact stability
  -> protected path / trust boundary
  -> mutation authorization
  -> promotion classification
  -> governance review
  -> certification / strict validation
  -> research/product evolution only if lower layers permit
```

This is the system's institutional reasoning order. It decides what has precedence before any action is considered.

## Semantic Cognition Flow

```text
Human text / ChatGPT-style output
  -> deterministic normalized intent
  -> authority boundary flags
  -> provenance and replay identity
  -> hash verification
  -> semantic proposal candidate
  -> semantic contract
  -> ambiguity list
  -> forbidden operations
  -> expected artifacts and tests
```

Key source surfaces:

- `sapianta_bridge/nl_envelope/intent_classifier.py`
- `agol_bridge/chatgpt_ingress/chatgpt_ingress_artifact.py`
- `agol_bridge/chatgpt_ingress/chatgpt_ingress_validator.py`
- `agol_bridge/semantic_contract/semantic_contract_synthesis.py`
- `sapianta_bridge/protocol/validator.py`

## Memory And Replay Topology

```text
Replay identity
  -> request hash
  -> command hash
  -> scope hash
  -> artifact hash
  -> lineage references
  -> governed return hash
  -> append-only ledger line
  -> evidence bundle
  -> replay verification result
```

Evidence stores:

- `.runtime/aigol/ledger/governed_returns.jsonl`
- `.runtime/aigol/evidence/<replay_identity>/`
- `.github/governance/evidence/`
- `.github/governance/finalize/`
- `runtime/*_evidence/`
- `runtime/governance/master/`

Memory semantics:

- replay is read-only;
- ledger is append-only;
- governance memory is dormant unless separately activated;
- missing lineage blocks or weakens authority;
- failed executions are preserved, not hidden.

## Reflection And Advisory Topology

```text
Replay evidence
  -> execution summary
  -> lifecycle transition history
  -> capability delta
  -> governance risk classification
  -> advisory proposal
  -> human approval queue
  -> explicit decision artifact
```

Key source surfaces:

- `sapianta_bridge/reflection/reflection_engine.py`
- `sapianta_bridge/reflection/capability_delta.py`
- `sapianta_bridge/reflection/governance_risk.py`
- `sapianta_bridge/reflection/advisory_proposals.py`
- `sapianta_bridge/approval/approval_queue.py`
- `sapianta_bridge/approval/governance_decisions.py`

Authority rule:

- reflection may advise;
- advisory proposals require human approval;
- reflection cannot execute automatically.

## Refinement Cognition Topology

```text
Operator feedback / refinement history
  -> adaptive intent awareness
  -> perceptual mismatch detection
  -> visual continuity memory
  -> convergence-aware refinement
  -> recommendation / prompt augmentation
  -> no mutation unless separately requested and governed
```

Key source surfaces:

- `runtime/governance/agol_adaptive_intent.py`
- `runtime/governance/agol_refinement_guidance.py`
- `runtime/governance/agol_visual_continuity_memory.py`
- `runtime/governance/agol_convergence_aware_refinement.py`

This is one of the clearest proto-cognitive clusters: it detects stagnation, user dissatisfaction, stabilized preferences, convergence, and mutation pressure, but it denies autonomous learning and runtime authority.

## Execution Boundary Topology

```text
READY_FOR_HUMAN_APPROVAL
  -> HUMAN_APPROVAL_GATE_V1
  -> APPROVED_FOR_GOVERNED_HANDOFF
  -> GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1
  -> READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION
  -> EXPLICIT_DISPATCH_AUTHORIZATION_V1
  -> DISPATCH_AUTHORIZED
  -> CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1
  -> READY_FOR_CONTROLLED_EXECUTION_HANDOFF
  -> CONTROLLED_EXECUTION_HANDOFF_V1
  -> BOUNDED_CODEX_CLI_PROVIDER
```

Explicit distinctions:

- human approval != dispatch authorization;
- dispatch authorization != execution;
- continuity preview != provider invocation;
- provider invocation remains single-provider and bounded;
- retries, routing, orchestration, and autonomous continuation remain false.

## Institutional Memory Topology

```text
Milestone
  -> ADR / governance doc
  -> evidence artifact
  -> finalization artifact
  -> boundary guarantees
  -> lineage report
  -> continuity report
  -> future interpretation constraint
```

Representative roots:

- `.github/governance/adr/`
- `.github/governance/evidence/`
- `.github/governance/finalize/`
- `runtime/finalization_evidence/`
- `runtime/governance/master/`
- `docs/governance_audit/`

This is long-term institutional memory. It records what the system is allowed to remember about its own evolution.

## CAL / CCS / Bounded Learning Topology

```text
Capability gap / development need
  -> deterministic task proposal
  -> governance gate
  -> mutation guard
  -> architecture guardian
  -> tests
  -> CCS certification
  -> registry / evidence
  -> possible future promotion
```

Current status:

- CAL and CCS are present as scaffolding and documented acceleration foundations.
- They are not safe to treat as active autonomous adaptive governance.
- Self-promotion, autonomous production activation, and governance mutation remain forbidden.

## Product 1 Cognition Interpretation

Product 1, AI Decision Validator, can be interpreted as the enterprise-facing expression of this bounded cognition layer:

```text
AI proposal
  -> governance interpretation
  -> admissibility check
  -> authority boundary
  -> evidence and replay
  -> decision visibility
  -> fail-closed recommendation
```

The product value is not "an AI that thinks freely." The value is institutional reasoning about whether AI execution should be trusted, blocked, escalated, or bounded.

## Emergent Cognition Map

```text
                        [Human Authority]
                               |
                               v
                    [Constitutional Governance]
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
[Semantic Interpretation]                    [Governance Memory]
        |                                             |
        v                                             v
[Admissibility / Authority Checks]       [Replay / Lineage / Freeze]
        |                                             |
        +----------------------+----------------------+
                               |
                               v
                  [Boundary State Machine]
                               |
          +--------------------+--------------------+
          |                                         |
          v                                         v
[Advisory Reflection]                    [Execution Governance]
          |                                         |
          v                                         v
[Human Review / Proposal]        [Bounded Single-Provider Handoff]
                                                    |
                                                    v
                                      [Governed Return Continuity]
                                                    |
                                                    v
                                      [Ledger / Evidence / Verify]
```

## System-Level Inference

The repository already has the shape of a bounded cognition operating system:

- constitutional law;
- semantic perception;
- admissibility judgment;
- working memory through replay identity;
- long-term memory through governance artifacts;
- meta-cognition through reflection;
- action gating through approval and dispatch;
- result memory through governed returns;
- institutional oversight through human authority.

What is missing is not the substrate. What is missing is consolidation into an explicit cognition layer with a registry, state envelope, and read-only observability over the cognitive lifecycle.
