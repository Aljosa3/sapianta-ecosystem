# AIGOL_ARCHITECTURE_LEGEND_V1

Status: WORKING LEGEND
Scope: Core architecture terms currently used in AiGOL implementation, governance artifacts, and certified architectural decisions.

---

# 1. HUMAN LAYER

## Human

Authority layer of AiGOL.

Responsibilities:

* defines intent
* approves actions when required
* remains final authority

Constitutional invariant:

```text
Human = authority layer
```

---

# 2. INTERFACE LAYER

## ACLI

AiGOL Conversational Language Interface

Purpose:

Primary human entry point into AiGOL.

Responsibilities:

* accept natural language input
* provide conversational interaction
* route human intent into AiGOL workflows

Flow:

```text
Human
↓
ACLI
```

---

## HIRR

Human Intent Resolution Ready

Purpose:

Resolve human intent without requiring knowledge of internal architecture.

Responsibilities:

* intent understanding
* clarification-first behavior
* workflow target identification
* workflow refinement
* fail-closed ambiguity handling

Flow:

```text
Human
↓
ACLI
↓
HIRR
```

Status:

```text
CERTIFIED
```

---

# 3. ORCHESTRATION LAYER

## OCS

Orchestration & Cognition System

Purpose:

Central orchestration layer of AiGOL.

Responsibilities:

* workflow coordination
* cognition orchestration
* governance enforcement
* context assembly
* provider selection
* worker authorization

Constitutional invariant:

```text
OCS governs.
```

Flow:

```text
HIRR
↓
OCS
```

---

## PPP

Proposal Processing Pipeline

Purpose:

Standardized processing of proposals before execution.

Responsibilities:

* proposal intake
* validation
* governance checks
* approval handling
* workflow progression

PPP processes:

* human proposals
* replay-derived proposals
* future improvement proposals

---

# 4. RESOURCE INFRASTRUCTURE

## ERR

External Resource Registry

Purpose:

Canonical registry of external resources.

Responsibilities:

* resource registration
* resource lookup
* capability lookup
* resource status tracking

ERR does NOT:

* execute resources
* invoke providers
* invoke workers
* perform orchestration

Current implementation:

```text
ERR_V0
```

---

## ERR_V0

External Resource Registry Version 0

Purpose:

Minimal proof-of-concept registry.

Capabilities:

* registration
* lookup by id
* capability search
* ACTIVE filtering
* replay-visible selection evidence

Supported resource types:

```text
COGNITION_PROVIDER
EXECUTION_WORKER
```

---

## Capability

A capability represents something a resource can do.

Examples:

```text
reasoning
file_write
```

AiGOL prefers:

```text
capability lookup
```

instead of:

```text
hardcoded resource references
```

---

## Resource

Generic term for:

```text
provider
worker
service
```

---

# 5. COGNITION LAYER

## LLM

Large Language Model

Examples:

* OpenAI
* Claude
* Gemini
* Mistral

Constitutional role:

```text
LLM = cognition source
```

LLM is NOT:

```text
authority
governance
execution
approval
```

---

## Cognition Provider

Provider capable of producing cognition.

Examples:

```text
OpenAI
Claude
Gemini
```

Responsibilities:

* findings
* assumptions
* alternatives
* risks
* uncertainties
* confidence

Provider output:

```text
Cognition Artifact
```

---

## Cognition Artifact

Standardized cognition result returned by a provider.

Purpose:

Normalize provider output into replay-visible artifacts.

---

# 6. EXECUTION LAYER

## Worker

Execution component.

Purpose:

Perform actions approved by AiGOL.

Examples:

* Filesystem Worker
* GitHub Worker
* Email Worker
* Calendar Worker
* Trading Worker

Constitutional invariant:

```text
Worker executes.
```

Workers do NOT:

```text
govern
approve
authorize
invoke providers
```

---

## Execution

Actual mutation or action performed by workers.

Examples:

```text
write file
send email
commit code
place trade
```

---

# 7. GOVERNANCE LAYER

## Governance

Purpose:

Protect architectural integrity and authority boundaries.

Responsibilities:

* approval enforcement
* policy enforcement
* authorization control
* mutation boundaries

Constitutional invariant:

```text
AiGOL governs.
```

---

## ADR

Architecture Decision Record

Purpose:

Permanent record of architectural decisions.

Used for:

* architectural certification
* governance evidence
* milestone decisions

---

# 8. REPLAY LAYER

## Replay

Purpose:

Immutable audit trail of system activity.

Responsibilities:

* record decisions
* record selections
* record executions
* support reconstruction

Constitutional invariant:

```text
Replay records.
```

---

## Replay Evidence

Replay-visible artifact proving that an event occurred.

Examples:

```text
resource selection
provider selection
execution result
approval record
```

---

# 9. CORE CONSTITUTIONAL INVARIANTS

```text
Human = authority layer

OCS = orchestration layer

LLM = cognition layer

Worker = execution layer

LLM proposes.

AiGOL governs.

Worker executes.

Replay records.
```

---

# 10. CURRENT HIGH-LEVEL FLOW

```text
Human
↓
ACLI
↓
HIRR
↓
OCS
 ↓
 ├─ Governance
 ├─ PPP
 ├─ Replay
 └─ ERR
        ↓
        ├─ Providers
        └─ Workers
```

---

Version:

```text
AIGOL_ARCHITECTURE_LEGEND_V1
```
