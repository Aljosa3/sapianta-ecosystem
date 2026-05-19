# ADR-00X - Semantic Direction Governance

# Status

Accepted

# Context

AGOL Bridge Pivot establishes AGOL as a governed execution bridge rather than a full autonomous semantic operating system. AGOL Bridge Transport Spec v1 prioritizes replay-safe transport, lifecycle state, approval boundaries, and deterministic result return.

This creates a necessary architectural distinction: semantic cognition and semantic governance are not the same responsibility.

LLMs can generate semantic possibilities, alternatives, interpretations, task framings, and candidate directions. AGOL does not need to own full semantic cognition in order to govern the admissibility of those directions.

# Decision

AiGOL will govern semantic direction rather than implement full semantic cognition.

The role boundaries are:

- ChatGPT / LLMs = semantic cognition.
- AiGOL = semantic direction governance.
- Codex / workers = execution.

LLMs remain the evolving cognition layer. AiGOL evaluates whether a proposed semantic direction is admissible under governance constraints, replay requirements, approval boundaries, mutation limits, and execution safety rules.

This separates semantic cognition from semantic governance. AiGOL does not need to infer every domain meaning internally. It must determine whether a proposed direction may proceed, must be constrained, must require approval, or must fail closed.

# Architectural Principle

LLMs generate semantic possibilities.
AiGOL governs admissible semantic evolution.

# Rationale

Owning full semantic cognition would increase complexity, duplicate model-native reasoning capability, and pull AiGOL toward autonomous semantic infrastructure. Governing semantic direction preserves the governance-first architecture while allowing cognition models to evolve independently.

This model keeps reasoning model-native and governance system-native. It also supports model-agnostic evolution because AiGOL governs admissibility boundaries rather than depending on one provider, model, or embedded semantic inference engine.

# Governance Alignment

Semantic Direction Governance aligns with:

- fail-closed execution;
- replay-safe task transfer;
- deterministic governance checks;
- bounded lifecycle transitions;
- explicit approval boundaries;
- AGOL Bridge Pivot;
- AGOL Bridge Transport Spec v1.

AiGOL may accept, constrain, quarantine, or reject semantic direction. It does not silently convert model output into execution authority.

# Consequences

Positive consequences:

- clearer separation of cognition, governance, and execution;
- reduced need for a domain inference runtime in v1;
- model-agnostic compatibility;
- preservation of replay and approval boundaries;
- less architectural pressure toward autonomous planning.

Negative consequences:

- semantic replay remains incomplete where model reasoning is non-deterministic;
- domain interpretation remains dependent on the cognition layer;
- deeper semantic governance may require future bounded specifications.

# Non-Goals

This ADR does not introduce:

- semantic autonomy engine;
- domain inference runtime;
- autonomous planning;
- hidden orchestration;
- runtime implementation;
- APIs;
- execution expansion.

# Decision Boundary

Semantic cognition may propose.

Semantic direction governance may admit, constrain, or reject.

Execution may proceed only through governed transport, replay evidence, lifecycle controls, and explicit approval boundaries.
