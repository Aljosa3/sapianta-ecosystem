# Optional Gaps V1

Status: useful later, not required for first useful AiGOL.

## Optional Gap 1: Additional Read-Only Capabilities

More read-only capabilities may be useful later, but they should not block first operation.

Examples:

- config inspection
- structured JSON inspection
- repository metadata inspection

These should wait until the frozen read-only flow has a stable operator invocation and replay summary.

## Optional Gap 2: Rich Replay Browser

A replay browser could help review evidence, but first useful AiGOL only needs deterministic replay summaries.

Avoid before first useful:

- semantic search
- adaptive indexing
- query engines
- graph navigation

## Optional Gap 3: Domain Templates

Domain-specific prompt templates may improve usability, but they are not necessary for the first useful operator path.

Examples:

- governance artifact inspection template
- source file inspection template
- runtime metadata inspection template

## Optional Gap 4: Human-Friendly Report Export

Markdown or JSON report export can wait until the basic governed result format is stable.

## Optional Gap 5: Capability Catalog UI

A UI showing available capabilities may be useful later. For now, a small text list or CLI help is enough.

## Optional Gap 6: Provider Variation

Provider abstraction and multiple LLM providers are not required for first useful AiGOL. The current priority is governance-preserving local usefulness, not provider breadth.
