# UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1

Status: Ready

Target verdict:

```text
UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_READY
```

## 1. Purpose

This artifact defines the Universal Bidirectional Translation Runtime.

The runtime sits:

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

The runtime translates in two directions:

```text
Human Natural Language
-> Governance Intent
```

and:

```text
Governance State
-> Human Natural Language
```

The translation runtime is not governance, approval, execution, or authority.

## 2. Constitutional Role

The LLM role is explicitly:

```text
translation only
never authority
never execution
never governance
```

The runtime may:

- translate human language into structured governance intent candidates;
- translate governance state into human-readable explanation;
- identify ambiguity;
- request clarification;
- compare provider translations;
- record evidence.

The runtime may not:

- select authoritative workflow;
- approve execution;
- authorize workers;
- mutate proposals;
- mutate replay;
- override HIRR;
- bypass ACLI;
- bypass domain adapter contracts;
- act as governance.

## 3. Runtime Position

The runtime is above ACLI and below the Human.

```text
Human
-> Translation Runtime
-> ACLI / HIRR / Governance
-> Domains / Products / Workers / Providers
-> Replay
```

It is a communication layer.

ACLI remains the governed interaction layer.

Governance remains authoritative for workflow state.

Human remains authority for approval.

Replay remains source of truth.

## 4. Contract Overview

The runtime has two independent but connected contracts:

1. Human -> Governance Translation Contract.
2. Governance -> Human Translation Contract.

They are independent because translating a human request into governance intent is not the same as explaining governance state back to a human.

They are connected because replay must preserve both directions and allow future learning from repeated translations.

## 5. Human -> Governance Translation Contract

### 5.1 Responsibilities

The Human -> Governance contract translates raw human language into a structured governance-intent candidate.

Responsibilities:

- preserve original human language;
- detect domain candidates;
- detect product candidates;
- detect intent family;
- detect ambiguity;
- detect execution relevance;
- detect approval relevance;
- detect provider relevance;
- detect worker relevance;
- detect missing context;
- produce a governance-intent candidate for ACLI/HIRR.

It may not make the candidate authoritative.

HIRR and ACLI must still decide whether the candidate is accepted, clarified, rejected, or routed.

### 5.2 Inputs

Required inputs:

```text
translation_request_id
human_prompt
session_context
operator_context
available_products
available_domains
available_workflows
created_at
```

Optional inputs:

```text
prior_turns
replay_context
domain_examples
product_examples
provider_translation_candidates
operator_locale
operator_expertise_level
```

### 5.3 Outputs

Required output:

```text
translation_artifact_type
translation_direction=HUMAN_TO_GOVERNANCE
original_human_prompt
governance_intent_candidate
domain_candidates
product_candidates
workflow_candidates
intent_family
confidence
ambiguity_status
clarification_questions
missing_context
execution_relevance
approval_relevance
provider_relevance
worker_relevance
translation_source
deterministic_fallback_used
provider_participation
replay_reference
```

The output is evidence for ACLI/HIRR, not authority.

### 5.4 Mandatory Evidence

Replay must record:

- original prompt;
- normalized prompt;
- translation rules used;
- provider candidates if any;
- comparison result if any;
- confidence;
- ambiguity status;
- clarification questions;
- deterministic fallback status;
- final translation candidate;
- rendered operator-facing clarification if emitted.

### 5.5 Ambiguity Handling

Ambiguity handling must classify:

```text
NO_AMBIGUITY
MINOR_AMBIGUITY
MATERIAL_AMBIGUITY
UNRESOLVED_AMBIGUITY
UNSAFE_AMBIGUITY
```

Rules:

- no ambiguity may proceed as a candidate;
- minor ambiguity may proceed with disclosed assumptions;
- material ambiguity requires clarification;
- unresolved ambiguity fails closed;
- unsafe ambiguity fails closed.

Provider output may identify ambiguity but may not resolve it authoritatively.

### 5.6 Confidence Model

Confidence values:

```text
HIGH
MEDIUM
LOW
GOVERNANCE_ONLY
UNKNOWN
```

Confidence describes translation quality only.

Confidence must never:

- select workflow authoritatively;
- approve execution;
- override HIRR;
- override ACLI;
- alter proposal hash.

### 5.7 Provider Independence

Human -> Governance translation must work deterministically without providers.

Provider-assisted translation may be used only as:

```text
advisory translation candidate
```

Provider-independent output must remain available.

### 5.8 Provider Comparison Compatibility

The contract must support:

```text
Provider A translation candidate
Provider B translation candidate
Provider C translation candidate
-> comparison
-> agreement / disagreement
-> confidence synthesis
-> human-visible ambiguity result
```

Comparison remains non-authoritative.

### 5.9 Deterministic Fallbacks

Fallbacks:

- deterministic phrase and schema translation;
- clarification request;
- fail-closed response;
- known-domain example matching;
- product/domain unavailable response.

Fallback must be replay-visible.

### 5.10 Replay Requirements

Replay must include:

```text
translation_direction
original_prompt_hash
translation_candidate
confidence
ambiguity_status
provider_participation
provider_comparison
deterministic_fallback
clarification_questions
handoff_to_hirr
handoff_to_acli
```

### 5.11 Certification Requirements

Certification scenarios:

1. Clear development request.
2. Clear product request.
3. Clear domain request.
4. Ambiguous request.
5. Unsafe approval-bypass request.
6. Provider unavailable.
7. Provider disagreement.
8. Deterministic fallback.
9. Replay reconstruction.
10. HIRR rejects translation candidate.

## 6. Governance -> Human Translation Contract

### 6.1 Responsibilities

The Governance -> Human contract translates governance state into human-readable language.

Responsibilities:

- explain selected workflow;
- explain proposal;
- explain approval requirement;
- explain what will happen;
- explain what will not happen;
- explain execution result;
- explain validation result;
- explain replay evidence;
- explain provider participation;
- explain fail-closed outcomes;
- expose authoritative versus advisory boundaries.

It may not modify governance state.

### 6.2 Inputs

Required inputs:

```text
translation_request_id
governance_state
workflow_state
proposal_state
approval_state
execution_state
validation_state
replay_state
created_at
```

Optional inputs:

```text
domain_context
product_context
provider_explanation_candidates
operator_expertise_level
operator_locale
prior_confusion_evidence
```

### 6.3 Outputs

Required output:

```text
translation_artifact_type
translation_direction=GOVERNANCE_TO_HUMAN
authoritative_state_reference
human_summary
what_i_understood
what_will_happen
what_will_not_happen
approval_explanation
next_action
replay_visibility
explanation_transparency
confidence
completeness
fallback_status
provider_participation
rendered_operator_view
rendered_operator_view_hash
```

### 6.4 Mandatory Evidence

Replay must record:

- authoritative governance state;
- source state hashes;
- deterministic explanation;
- provider request if any;
- provider response if any;
- provider comparison if any;
- fallback status;
- rendered human view;
- rendered view hash;
- explanation confidence;
- explanation completeness.

### 6.5 Ambiguity Handling

Ambiguity may occur when:

- governance state is incomplete;
- replay evidence is missing;
- workflow state is failed-closed;
- provider explanation disagrees with deterministic explanation;
- operator asks for an explanation without a reference.

Handling:

- explain known state;
- identify missing evidence;
- ask for replay or proposal reference;
- fail closed when authoritative state cannot be verified.

### 6.6 Confidence Model

Confidence values:

```text
HIGH
MEDIUM
LOW
GOVERNANCE_ONLY
UNKNOWN
```

Confidence describes only the quality of the explanation.

It does not describe governance correctness.

### 6.7 Provider Independence

Governance -> Human translation must work deterministically.

Provider-assisted explanation is optional.

Provider failure must fall back to deterministic explanation.

### 6.8 Provider Comparison Compatibility

The contract supports multi-provider explanation:

```text
deterministic explanation
-> provider explanation candidates
-> comparison
-> disagreement disclosure
-> human-readable explanation
```

Disagreement must be visible.

Comparison may not change governance state.

### 6.9 Deterministic Fallbacks

Fallbacks:

- deterministic explanation;
- replay-state summary;
- missing-evidence explanation;
- fail-closed explanation;
- request for replay reference.

### 6.10 Replay Requirements

Replay must include:

```text
translation_direction
authoritative_state_hash
deterministic_explanation_hash
provider_request_hash
provider_response_hash
rendered_operator_view_hash
confidence
completeness
fallback_reason
provider_participation
comparison_result
```

### 6.11 Certification Requirements

Certification scenarios:

1. Proposal explanation.
2. Approval explanation.
3. Execution explanation.
4. Validation explanation.
5. Replay explanation.
6. Provider-assisted explanation.
7. Provider unavailable fallback.
8. Provider disagreement disclosure.
9. Missing replay reference.
10. Failed-closed state explanation.

## 7. Integration With Universal ACLI

Universal ACLI remains the interaction authority.

Translation runtime integrates by:

```text
Human prompt
-> translation candidate
-> HIRR
-> ACLI workflow routing
```

and:

```text
ACLI state
-> translation runtime
-> operator explanation
```

ACLI may use translation evidence but does not delegate authority to translation.

## 8. Integration With Universal Product Contract

Products may provide:

- product vocabulary;
- product examples;
- product workflow labels;
- product operator wording;
- product replay labels.

The translation runtime may use these as translation context.

Products may not redefine translation authority.

Product-specific translation must still satisfy this runtime contract.

## 9. Integration With Universal Domain Adapter Contract

Domains may provide:

- domain vocabulary;
- domain intent examples;
- domain clarification questions;
- domain risk labels;
- domain explanation snippets.

The translation runtime may use domain adapters as context providers.

Domain adapters remain responsible for domain-specific intent validation.

Translation does not replace the domain adapter.

## 10. Integration With Worker Contracts

Workers may receive translated bounded execution requests only after:

- ACLI selected workflow;
- proposal was created;
- human approved;
- authorization was created.

Translation runtime may produce worker-readable summaries, but those summaries are not authorization.

Worker contract remains authoritative for execution bounds.

## 11. Integration With Cognition Contracts

Cognition providers may assist translation.

Provider roles:

- translation candidate provider;
- explanation provider;
- ambiguity detector;
- comparison participant.

Provider output remains:

```text
advisory
non-authoritative
replay-visible
fallback-safe
```

## 12. Integration With Replay

Replay records both directions:

```text
Human -> Governance translation evidence
Governance -> Human translation evidence
```

Replay must support reconstruction of:

- input;
- translation;
- confidence;
- ambiguity;
- provider participation;
- fallback;
- ACLI handoff;
- rendered operator view.

Replay is the source of truth for translation evidence.

## 13. Integration With ERR

ERR may be used to resolve translation providers or translation-related resources by capability.

ERR role:

```text
passive metadata lookup and replay-visible selection evidence
```

ERR may not:

- invoke translation provider;
- select authoritative translation;
- approve;
- execute;
- mutate replay;
- become governance.

If ERR cannot resolve a required translation resource, the runtime must use deterministic fallback or fail closed.

## 14. Certification Matrix

| Area | Human -> Governance | Governance -> Human |
| --- | --- | --- |
| Deterministic operation | Required | Required |
| Provider independence | Required | Required |
| Provider comparison compatibility | Required | Required |
| Ambiguity handling | Required | Required |
| Confidence model | Required | Required |
| Replay evidence | Required | Required |
| Fallback | Required | Required |
| Handoff to ACLI | Required | Not applicable |
| Rendered operator view | Optional | Required |

## 15. Replay-Derived Learning Roadmap

The runtime may learn from replay only through governed improvement.

Roadmap:

```text
Replay evidence
-> repeated translation pattern detected
-> translation improvement candidate
-> improvement proposal
-> human review
-> human approval
-> deterministic translation rule implementation
-> validation
-> certification
-> future runtime use
```

Rules:

- replay-derived patterns are evidence only;
- repeated patterns do not automatically change translation;
- provider suggestions do not automatically become deterministic rules;
- human approval is required before promotion;
- promoted rules must be versioned;
- prior replay must remain reconstructable.

Examples of promotable patterns:

- repeated natural-language phrase mapped to the same domain intent;
- repeated operator confusion about a workflow status;
- repeated provider explanation improvement accepted by humans;
- repeated replay review wording converted into deterministic explanation text.

## 16. Versioning

Translation runtime versions:

```text
UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_V1
HUMAN_TO_GOVERNANCE_TRANSLATION_CONTRACT_V1
GOVERNANCE_TO_HUMAN_TRANSLATION_CONTRACT_V1
```

Version increments required when:

- confidence model changes;
- replay schema changes;
- provider comparison semantics change;
- deterministic fallback semantics change;
- ACLI handoff fields change;
- rendered operator view schema changes;
- replay-derived learning promotion process changes.

## 17. Acceptance Checklist

- [ ] Human -> Governance translation contract defined.
- [ ] Governance -> Human translation contract defined.
- [ ] LLM role restricted to translation only.
- [ ] Provider independence defined.
- [ ] Provider comparison compatibility defined.
- [ ] Deterministic fallbacks defined.
- [ ] Ambiguity handling defined.
- [ ] Confidence model defined.
- [ ] Replay requirements defined.
- [ ] ACLI integration defined.
- [ ] Product contract integration defined.
- [ ] Domain adapter integration defined.
- [ ] Worker contract integration defined.
- [ ] Cognition contract integration defined.
- [ ] ERR integration defined.
- [ ] Replay-derived learning roadmap defined.
- [ ] Certification requirements defined.

## 18. Final Verdict

```text
UNIVERSAL_BIDIRECTIONAL_TRANSLATION_RUNTIME_READY
```

The Universal Bidirectional Translation Runtime provides a non-authoritative translation layer between Human and ACLI. It translates human language into governance-intent candidates and governance state into human language while preserving ACLI authority, human approval, worker boundaries, provider non-authority, replay evidence, and deterministic fallback.
