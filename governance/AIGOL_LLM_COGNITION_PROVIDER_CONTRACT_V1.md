# AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1

## Status

Certified governance contract.

This artifact defines the constitutional role contract for `COGNITION_PROVIDER` before any LLM provider may participate in OCS cognition. It does not implement provider invocation, runtime execution, OpenAI calls, multi-provider support, cognition artifact production, or changes to certified OCS cognition behavior.

## Purpose

AiGOL may later attach LLM providers to OCS cognition only under a bounded, replay-visible, non-authoritative role.

The preserved invariant is:

- LLM proposes.
- AiGOL governs.
- Worker executes.
- Replay records.

## Role Definition

Role:

`COGNITION_PROVIDER`

Role class:

External non-authoritative cognition participant.

Purpose:

- analyze;
- infer;
- compare;
- explain;
- identify uncertainty;
- identify missing information.

The `COGNITION_PROVIDER` may provide cognition support to AiGOL. It may not become AiGOL cognition authority.

## Distinction From PROPOSAL_PROVIDER

`PROPOSAL_PROVIDER`:

- produces bounded proposals for downstream governed review;
- may support development proposal production;
- is proposal-source oriented.

`COGNITION_PROVIDER`:

- produces bounded cognition assistance for OCS review;
- may support analysis, inference, comparison, explanation, uncertainty detection, and missing-information detection;
- is cognition-support oriented.

Shared constraints:

- both roles are non-authoritative;
- both roles produce untrusted external output;
- both roles require AiGOL validation before downstream use;
- neither role may approve, authorize, execute, govern, mutate replay, invoke workers, or create domains.

## Allowed Outputs

A `COGNITION_PROVIDER` may emit only bounded cognition-support output:

- findings;
- assumptions;
- alternatives;
- risks;
- uncertainties;
- confidence statements;
- clarification candidates.

Allowed outputs remain candidate material. They do not become approvals, authorizations, execution instructions, governance decisions, replay entries, domain creation decisions, or implementation decisions by provider action.

## Prohibited Outputs

A `COGNITION_PROVIDER` output must be rejected or fail closed when it contains, claims, or attempts:

- approvals;
- authorizations;
- governance mutations;
- replay mutations;
- worker invocation;
- execution authorization;
- domain creation authorization;
- implementation authorization;
- dispatch instructions;
- approval bypass;
- human authority replacement;
- governance policy override;
- replay reconstruction override;
- self-authorization;
- provider authority escalation.

## Required Provider Contract Fields

Any future cognition-provider registration must include:

- provider identity;
- provider role: `COGNITION_PROVIDER`;
- provider contract version;
- approved scope;
- credential policy reference when credentials are required;
- authority flags;
- allowed output classes;
- prohibited output classes;
- fail-closed conditions;
- replay binding requirements;
- human approval requirements;
- lineage requirements.

## Required Invocation Preconditions

Before any future runtime may invoke a `COGNITION_PROVIDER`, all of the following must be true:

- provider is registered;
- provider is approved for the `COGNITION_PROVIDER` role;
- provider contract is present;
- provider authority flags are all false;
- request is permitted by the cognition provider necessity policy;
- human approval requirements are satisfied when required;
- request contains replay-visible lineage references;
- request contains no governance-prohibited instruction;
- request preserves OCS deterministic context hash references.

This contract does not implement these checks. It defines the governance contract that future runtimes must enforce.

## Response Acceptance Preconditions

A future runtime may accept cognition-provider output only when:

- output is normalized into allowed output classes;
- output contains no authority-bearing claim;
- output preserves provider identity and metadata;
- output preserves request and context lineage;
- output can be replay reconstructed;
- output is explicitly marked non-authoritative;
- output remains subject to AiGOL validation and human review.

## Fail-Closed Conditions

Provider cognition must fail closed when:

- provider is not approved;
- provider is not registered;
- provider contract is missing;
- provider role is not `COGNITION_PROVIDER`;
- provider authority flags are missing or not false;
- provider response exceeds the authority boundary;
- cognition request violates governance policy;
- lineage references are missing;
- replay binding cannot be reconstructed;
- response cannot be normalized into allowed output classes;
- response attempts approval, authorization, execution, worker invocation, domain creation, implementation, governance mutation, or replay mutation.

## Replay Requirements

Future cognition-provider use must be replay-visible and reconstructable.

Minimum replay references:

- originating human request;
- OCS context artifact reference;
- OCS context hash;
- provider contract version;
- provider identity;
- provider request hash;
- provider response hash;
- response normalization result;
- fail-closed decision if rejected;
- human review reference when applicable.

## Human Authority Preservation

The `COGNITION_PROVIDER` may support human decision making. It may not replace human authority.

Human authority remains required for:

- approval;
- rejection;
- downstream action;
- implementation;
- domain creation;
- execution authorization;
- governance changes.

## Certified Contract Statement

`COGNITION_PROVIDER` is a non-authoritative external cognition-support role. It may analyze, infer, compare, explain, identify uncertainty, and identify missing information. It may emit findings, assumptions, alternatives, risks, uncertainties, confidence statements, and clarification candidates. It may not approve, authorize, execute, invoke workers, create domains, authorize implementation, mutate governance, mutate replay, or bypass human authority.

This contract safely enables future implementation of `AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_V1` without introducing provider authority.
