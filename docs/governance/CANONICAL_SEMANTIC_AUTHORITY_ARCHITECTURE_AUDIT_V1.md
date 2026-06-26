# CANONICAL_SEMANTIC_AUTHORITY_ARCHITECTURE_AUDIT_V1

## 1. Audit Purpose

This artifact determines which architectural component is intended to own canonical semantic interpretation within AiGOL Platform Core.

This is an architecture audit only.

No runtime behavior, routing, governance, replay, providers, workers, or tests were modified.

Important terminology boundary:

```text
semantic authority = canonical ownership of translation semantics
governance authority = authority to route, approve, execute, mutate, or certify
```

The semantic owner may translate meaning into structured candidates, but it does not become governance authority.

## 2. Repository Evidence

### 2.1 Universal Bidirectional Translation Runtime

Primary artifact:

- `docs/governance/UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1.md`

Runtime position:

```text
Human
-> Universal Bidirectional Translation Runtime
-> Universal ACLI
```

and:

```text
Universal ACLI / Governance State
-> Universal Bidirectional Translation Runtime
-> Human
```

Stated purpose:

- translate human language into structured governance-intent candidates;
- translate governance state into human-readable explanation;
- identify ambiguity;
- request clarification;
- compare provider translations;
- record evidence.

Stated non-authority:

- may not select authoritative workflow;
- may not approve execution;
- may not authorize workers;
- may not mutate proposals;
- may not mutate replay;
- may not override HIRR;
- may not bypass ACLI.

### 2.2 Universal Translation Runtime Integration

Primary artifact:

- `docs/governance/UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1.md`

Runtime module:

- `aigol/runtime/universal_translation_runtime_integration.py`

The integration artifact states:

```text
UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1 integrates the Universal Translation Runtime as the canonical translation layer for AiGOL.
```

It also states the current operational ACLI routing path:

```text
human_prompt
-> translate_human_to_governance
-> _classify_workflow
-> workflow selection
```

This proves that Universal Translation is intended to be canonical translation evidence, while the current implementation remains in compatibility mode for routing behavior.

### 2.3 Human -> Governance Translation Runtime

Primary artifact:

- `docs/governance/HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1.md`

Runtime module:

- `aigol/runtime/human_to_governance_translation_runtime.py`

Implemented responsibility:

- normalize a human request;
- detect action;
- detect domain;
- extract entities;
- detect ambiguity;
- assign confidence;
- populate governance translation payload;
- emit replay-visible Universal Translation Artifact.

It produces translation candidates, not execution authority.

### 2.4 Governance -> Human Translation Runtime

Primary artifact:

- `docs/governance/GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1.md`

Runtime module:

- `aigol/runtime/governance_to_human_translation_runtime.py`

Implemented responsibility:

- translate governance state into human-readable payload;
- summarize proposals, approval, worker status, validation, replay, and ERR;
- preserve authoritative references;
- emit replay-visible Universal Translation Artifact.

It explains governance state, but does not approve, execute, or mutate.

### 2.5 Human-Friendly ACLI Explanation Layer

Primary artifact:

- `docs/governance/HUMAN_FRIENDLY_ACLI_EXPLANATION_LAYER_V1.md`

Runtime module:

- `aigol/runtime/acli_human_friendly_explanation_runtime.py`

Stated responsibility:

- explain what ACLI understood;
- explain what will happen;
- explain what will not happen;
- explain approval requirements;
- explain what to type next;
- explain replay visibility.

Stated boundary:

```text
It must not classify intent, select workflows, override workflow selection, approve execution, trigger providers, invoke workers, mutate repository state, mutate governance artifacts, or bypass fail-closed checks.
```

Therefore, it is not the canonical semantic interpreter. It is an operator-facing explanation layer over already-created artifacts.

### 2.6 LLM-Assisted Explanation Layer

Primary artifact:

- `docs/governance/ACLI_LLM_ASSISTED_EXPLANATION_LAYER_V1.md`

Runtime module:

- `aigol/runtime/acli_llm_assisted_explanation_runtime.py`

Stated responsibility:

- optionally improve human-facing explanation of technical runtime state;
- paraphrase technical state;
- explain terminology;
- summarize why approval is required;
- improve readability.

Stated boundary:

```text
The purpose is not to make LLMs part of routing, governance, approval, execution, validation, or replay authority.
```

Provider output may not:

- classify intent;
- select workflows;
- alter routing confidence;
- approve proposals;
- authorize execution;
- create worker requests;
- invoke workers;
- modify repository state;
- modify governance artifacts;
- modify deterministic replay history.

Therefore, the LLM-assisted explanation layer is not the canonical semantic interpreter. It is optional advisory explanation after ACLI state already exists.

### 2.7 Explanation Provider Contract

Primary artifact:

- `docs/governance/ACLI_EXPLANATION_PROVIDER_CONTRACT_V1.md`

The contract states:

```text
Explanation providers may help produce human-facing explanations of technical ACLI runtime state.
They do not participate in governance authority, workflow authority, approval authority, execution authority, validation authority, or replay authority.
```

Provider output must never select workflows or change HIRR classification.

This confirms explanation providers are not semantic authority for workflow input.

### 2.8 Semantic Contract / MOC Layer

Primary evidence:

- `schemas/semantic_contract.schema.json`
- `docs/governance/cognition/MOC_V1_SPEC.md`
- `docs/governance/cognition/MOC_V1_SEQUENCE_FLOW.md`
- `aigol/moc/contract_validation.py`
- `aigol/moc/advisory_contract_generation.py`
- `browser_companion/sidepanel.html`
- `browser_companion/sidepanel.js`

MOC flow:

```text
Human Intent
-> Intent Normalization
-> Governance Retrieval
-> Semantic Contract
-> Advisory Proposal
-> Human Approval
-> Worker Task
-> Governed Return
```

The semantic contract model predates or parallels Universal Translation. It is bounded and advisory, but repository evidence does not show it as the canonical Universal ACLI semantic authority.

### 2.9 Absent Concepts

Search found no repository references for:

- `GIR`
- `ExecutionIntentPackage`

These do not appear to be active architectural candidates for semantic authority in the current repository.

## 3. Historical Timeline

### Stage 1: Semantic Contract / MOC

The early semantic architecture uses a semantic contract to bound intent into advisory governance evidence.

Problem solved:

- make human intent structured and bounded;
- preserve advisory-only cognition;
- connect intent to proposals and approval.

Primary scope:

- cognition protocol;
- browser companion / MOC flows;
- advisory semantic contract validation.

### Stage 2: ACLI / HIRR Deterministic Routing

ACLI and HIRR developed deterministic marker-based interpretation for operational routing.

Problem solved:

- get real operator prompts into certified workflows;
- preserve fail-closed behavior;
- avoid provider dependency;
- maintain deterministic replay.

Primary scope:

- workflow selection;
- clarification;
- governed development;
- domain routing;
- OCS routing;
- lifecycle continuation.

### Stage 3: Human-Friendly Explanation Layer

Human-friendly explanation was introduced after routing and governed development began working.

Problem solved:

- operators could not understand technical ACLI state;
- proposal/approval/replay status needed plain-language explanation.

Primary scope:

- operator UX;
- deterministic explanation;
- replay-visible explanation artifacts.

Not intended for:

- semantic interpretation before routing;
- workflow selection.

### Stage 4: LLM-Assisted Explanation Layer

LLM-assisted explanation was introduced as an optional readability layer over deterministic state.

Problem solved:

- deterministic explanation may be too rigid or technical;
- providers can improve wording without authority.

Primary scope:

- optional operator-facing explanation;
- provider-assisted paraphrase;
- deterministic fallback.

Not intended for:

- HIRR;
- routing;
- workflow input;
- approval;
- execution.

### Stage 5: Universal Bidirectional Translation Runtime

Universal Bidirectional Translation was introduced as the general Human <-> Governance translation architecture.

Problem solved:

- normalize human language before governance;
- explain governance state back to humans;
- preserve provider-independent translation;
- support deterministic fallback, ambiguity handling, replay evidence, and replay-derived learning.

Primary scope:

- canonical translation between human language and governance-intent candidates;
- governance-state-to-human explanation;
- multilingual translation and normalization;
- replay evidence for both directions.

### Stage 6: Universal Translation Integration

UTR integration added replay-visible translation evidence to ACLI routing and explanation paths.

Problem solved:

- make translation replay-visible before HIRR-compatible routing;
- provide compatibility layer without breaking existing certified local classifiers.

Primary scope:

- additive translation evidence;
- integration wrapper;
- compatibility-mode migration.

Remaining gap:

- workflow selection still consumes local semantic markers rather than canonical translated intent.

## 4. Concept Comparison Matrix

| Concept | Same As UTR? | Complementary? | Evolutionary Stage? | Competing Architecture? | Intended Role |
| --- | --- | --- | --- | --- | --- |
| Semantic Contract / MOC | No | Yes | Earlier/parallel | Not currently canonical for ACLI | Advisory semantic contract evidence |
| Human-Friendly ACLI Explanation | No | Yes | Later UX layer | No | Deterministic operator explanation after routing |
| LLM-Assisted Explanation Layer | No | Yes | Later UX augmentation | No | Optional provider-assisted explanation of runtime state |
| Explanation Provider Contract | No | Yes | Provider contract for UX | No | Bound provider explanation behavior |
| Universal Bidirectional Translation Runtime | Yes, architecture-level UTR | N/A | Current canonical translation architecture | No | Human <-> Governance translation |
| Universal Translation Runtime Integration | Implementation/integration of UTR | Yes | Migration layer | No | Add translation evidence before routing/explanation |

Conclusion:

The explanation layers and UTR are complementary, not competing. The Universal Bidirectional Translation Runtime owns translation semantics. Explanation layers render already-known state to operators.

## 5. Responsibility Matrix

| Responsibility | Intended Owner |
| --- | --- |
| Canonical semantic interpretation | Universal Bidirectional Translation Runtime |
| Human -> governance intent candidate | Human -> Governance Translation Runtime |
| Governance state -> human-readable explanation | Governance -> Human Translation Runtime |
| Workflow input normalization | Universal Bidirectional Translation Runtime, consumed by HIRR/ACLI after migration |
| Authoritative workflow selection | ACLI / HIRR / Governance, not UTR |
| Replay explanation | Governance -> Human Translation Runtime plus ACLI explanation layers |
| Human-readable proposal/approval explanation | Human-Friendly ACLI Explanation Layer |
| Optional provider-assisted readability | LLM-Assisted Explanation Layer |
| Multilingual normalization | Universal Bidirectional Translation Runtime |
| Provider translation escalation | Adaptive Translation Escalation Runtime |
| Replay-derived deterministic rule promotion | Replay-Derived Translation Learning Runtime through governed improvement workflow |
| Worker authorization | Governance / approval / worker runtimes, not UTR |

## 6. Ownership Analysis

### 6.1 Canonical Semantic Interpretation

Intended owner:

```text
Universal Bidirectional Translation Runtime
```

Reason:

- it is explicitly positioned between Human and ACLI;
- it translates human natural language into governance-intent candidates;
- it owns ambiguity handling and confidence;
- it supports provider independence, deterministic fallback, multilingual translation, replay evidence, and replay-derived learning.

### 6.2 Workflow Input

Intended owner of semantic input:

```text
Universal Bidirectional Translation Runtime
```

Authoritative selector:

```text
ACLI / HIRR / Governance
```

Meaning:

UTR should supply canonical translated intent as input. ACLI/HIRR should remain responsible for authoritative workflow selection and fail-closed governance behavior.

### 6.3 Replay Explanation

Intended owner:

```text
Governance -> Human Translation Runtime
```

Complementary renderers:

- Human-Friendly ACLI Explanation Layer;
- LLM-Assisted Explanation Layer.

### 6.4 Human-Readable Explanation

Intended owner:

```text
Human-Friendly ACLI Explanation Layer
```

Optional augmentation:

```text
LLM-Assisted Explanation Layer
```

These are downstream of routing and workflow state. They do not own canonical semantic interpretation.

### 6.5 Multilingual Normalization

Intended owner:

```text
Universal Bidirectional Translation Runtime
```

Current implementation reality:

Multilingual handling is partly duplicated in local ACLI/HIRR marker lists, including Slovenian phrases.

## 7. Overlap Analysis

### 7.1 UTR vs Universal Bidirectional Translation Runtime

These are not competing concepts.

`Universal Translation Runtime` is the shorthand/integration naming used for the implemented runtime stack.

`Universal Bidirectional Translation Runtime` is the architecture-level concept defining both directions:

- Human -> Governance;
- Governance -> Human.

### 7.2 UTR vs LLM-Assisted Explanation Layer

These are complementary.

UTR owns translation semantics and structured governance-intent candidates.

LLM-assisted explanation owns optional human-facing paraphrase of already-authoritative ACLI state.

The LLM-assisted explanation layer explicitly cannot classify intent or select workflows.

### 7.3 UTR vs Human-Friendly Explanation Layer

These are complementary.

Human-friendly explanation uses runtime state to explain what happened or what will happen. It does not determine semantic meaning before routing.

### 7.4 UTR vs Semantic Contract / MOC

These are related but distinct.

MOC semantic contracts are advisory governance artifacts used in cognition flows. UTR is broader and applies to Universal ACLI and domain/product integration.

MOC may remain a domain/protocol-specific semantic artifact consumer, but it is not the canonical Universal ACLI semantic authority.

## 8. Drift Analysis

### 8.1 Ownership Divergence

Ownership diverged when UTR was integrated in additive compatibility mode:

```text
translate_human_to_governance
-> record translation evidence
-> _classify_workflow(human_prompt)
```

This preserved certified routing behavior but left semantic interpretation in ACLI/HIRR marker systems.

### 8.2 Duplicated Responsibilities

Duplicated responsibility exists in:

- action detection;
- domain detection;
- governance artifact detection;
- proposal-only detection;
- clarification need detection;
- execution/no-execution detection;
- multilingual phrase handling;
- provider relevance detection;
- operator explanation construction.

### 8.3 Current Proposal-Only Alignment

The current proposal-only implementation does not fully align with intended ownership.

Current implementation:

```text
ACLI-local _proposal_only_ocs_escalation(normalized)
```

Intended semantic ownership:

```text
Universal Bidirectional Translation Runtime
-> canonical governance-intent candidate
-> ACLI/HIRR workflow selection
```

Therefore, proposal-only routing is a temporary compatibility implementation, not the final canonical architecture.

### 8.4 Authoritative Architecture

The authoritative architecture for semantic translation should be:

```text
Universal Bidirectional Translation Runtime
```

The authoritative architecture for governance decisions remains:

```text
ACLI / Governance / HIRR / approval runtimes
```

This distinction preserves the constitutional boundary:

```text
translation proposes meaning
governance decides admissibility
human approves
workers execute
replay records
```

## 9. Recommendations

Architecture-only recommendations:

1. Treat `Universal Bidirectional Translation Runtime` as the canonical semantic translation architecture.
2. Treat `Universal Translation Runtime` as the implemented shorthand/runtime stack for that architecture.
3. Treat human-friendly and LLM-assisted explanation layers as downstream explanation renderers, not semantic authorities.
4. Treat MOC Semantic Contract as an adjacent advisory contract system, not the Universal ACLI semantic authority.
5. Document the current ACLI/HIRR marker systems as compatibility-layer semantic fallbacks.
6. Future migration should move selected semantic ownership from local markers into canonical translated intent fields while preserving ACLI/HIRR as authoritative workflow selectors.
7. Future audits should distinguish:
   - canonical semantic translation ownership;
   - authoritative workflow selection;
   - operator-facing explanation.

No implementation changes are recommended by this audit.

## 10. Non-Goals

This audit does not:

- redesign UTR;
- redesign HIRR;
- redesign ACLI routing;
- change proposal-only routing;
- change OCS cognition;
- change PPP;
- change worker authorization;
- change replay semantics;
- change provider behavior;
- modify runtime code;
- modify tests.

## 11. Final Verdict

UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_IS_CANONICAL_AUTHORITY
