# G5-04 Provider Cognition To OCS Decision Proposal Alignment V1

Status: certified alignment.

Final verdict: PROVIDER_TO_OCS_ALIGNMENT_READY

## 1. Purpose

G5-04 defines the canonical transformation from replay-visible provider cognition evidence into an OCS-owned decision proposal.

This is an alignment and certification milestone only. It does not introduce runtime changes, provider authority, worker execution, repository mutation, deployment, approval activation, authorization activation, retry, or fallback.

The core rule is:

```text
Provider cognition may inform an OCS proposal.
Provider cognition may not become an OCS proposal by authority transfer.
```

OCS owns the decision proposal. Provider Services own bounded cognition evidence only.

## 2. Reviewed Baseline

Reviewed certified components:

- G5-02 bounded read-only provider cognition runtime;
- G5-03 live PGSP provider cognition entrypoint and UHCL review;
- G4-02 governed development loop scaffold OCS proposal artifact;
- G4-04 governed self-development session ownership model;
- G3-04 provider-services roadmap under OCS governance;
- universal proposal interface constraints.

Relevant existing invariants:

- provider output remains cognition evidence only;
- OCS owns advisory proposal generation;
- Governance owns authority checkpoints;
- UHCL owns reusable communication;
- Replay owns reconstruction evidence;
- adapters render and capture interaction only;
- provider confidence is never authority.

## 3. Transformation Model

The canonical transformation is:

```text
PGSP session context
-> provider cognition evidence
-> provider post-execution review
-> UHCL provider cognition review
-> OCS evidence intake
-> OCS-owned proposal synthesis
-> governance checkpoint
-> UHCL proposal review
-> human confirmation boundary
-> replay reconstruction
```

Provider cognition is an input evidence source. OCS performs the proposal synthesis step.

The OCS proposal may reference provider cognition hashes, summaries, risks, assumptions, and review status, but it must independently record the OCS decision structure, proposal status, recommended next step, alternatives, assumptions, risks, validation plan, replay plan, and non-authority flags.

## 4. Information Classification

| Information | Treatment | Owner After Transformation |
| --- | --- | --- |
| Provider identity reference | Copied by reference/hash only. | Provider Services / Replay |
| Credential reference | Copied by reference/hash only; secret material never copied. | Provider Services |
| Provider request hash | Copied as source evidence. | Replay |
| Provider response hash | Copied as source evidence. | Replay |
| Provider output text | May be summarized or cited as provider evidence; not authoritative. | Provider Services |
| Provider risk observations | May be derived into OCS risks with source binding. | OCS |
| Provider assumptions | May be derived into OCS assumptions with source binding. | OCS |
| Provider recommendations | May be considered, but OCS must restate any accepted recommendation as OCS-owned proposal content. | OCS |
| Provider confidence | Remains provider evidence only; never copied as authority. | Provider Services |
| UHCL provider review status | Copied by reference/hash and rendered as communication evidence. | UHCL / Replay |
| Human review response class | Copied as interaction evidence; does not authorize execution. | PGSP / UHCL |
| OCS proposal summary | Derived by OCS. | OCS |
| OCS recommended next step | Derived by OCS. | OCS |
| OCS alternatives | Derived by OCS. | OCS |
| OCS proposal hash | Created by OCS proposal artifact. | OCS / Replay |

## 5. OCS Proposal Requirements

An OCS proposal derived from provider cognition must include:

- `proposal_id`;
- `ocs_owner = OCS`;
- PGSP session reference;
- CSA or semantic intent reference when available;
- provider cognition evidence references and hashes;
- UHCL review reference and hash;
- proposal summary;
- recommended next step;
- alternatives;
- assumptions;
- risks;
- validation plan;
- replay plan;
- governance checkpoint reference;
- `proposal_only = true` until later execution milestones explicitly certify otherwise;
- non-authority flags for provider, worker, approval, authorization, mutation, and deployment.

For domain proposal compatibility, the OCS proposal should also map to the universal proposal interface:

- intent summary;
- target objects;
- expected changes;
- what will happen;
- what will not happen;
- approval reason;
- risk classification;
- validation plan;
- replay plan;
- proposal hash.

## 6. Ownership Matrix

| Capability | Canonical Owner | Boundary |
| --- | --- | --- |
| Live session context | PGSP | Session ownership only. |
| Provider identity | Provider Services | Identity and credential boundaries only. |
| Provider cognition execution | G5-02 provider cognition runtime | Read-only cognition evidence only. |
| Live provider cognition routing | G5-03 PGSP entrypoint | Routing and capture only. |
| Provider output | Provider Services | Non-authoritative evidence. |
| Evidence intake | OCS | Intake does not imply acceptance. |
| Proposal synthesis | OCS | OCS-owned decision proposal only. |
| Governance checkpoint | Governance | Authority boundary verification only. |
| Human communication | UHCL | Review and explanation only. |
| Human confirmation capture | Interface adapter / PGSP | Confirmation evidence only until approval/authorization are certified. |
| Replay reconstruction | Replay | Evidence continuity only. |
| Worker execution | Worker Services | Out of scope for G5-04. |
| Repository mutation | Governed mutation runtime | Out of scope for G5-04. |

## 7. Replay Implications

The transformation must be replay-visible across both evidence and proposal layers.

Required replay bindings:

- PGSP session replay reference;
- G5-03 live entrypoint replay reference and hash;
- nested G5-02 provider cognition replay reference and hash;
- provider request envelope hash;
- provider response or error envelope hash;
- provider participation evidence hash;
- G5-02 post-execution review hash;
- G5-03 UHCL provider review hash;
- OCS proposal artifact hash;
- governance checkpoint hash;
- UHCL proposal review hash when proposal communication is generated;
- human confirmation artifact hash when a response is captured.

Replay reconstruction must fail closed if:

- provider evidence hash continuity is broken;
- provider output appears without provider replay evidence;
- OCS proposal fields are copied without source evidence binding;
- provider authority flags appear;
- proposal authority flags appear before approval and authorization certification;
- worker, mutation, deployment, retry, or fallback evidence appears in a G5-04 transformation path.

## 8. Governance Implications

Governance must verify:

- provider cognition is read-only and cognition-only;
- provider identity and credential boundaries remain intact;
- provider output is marked non-authoritative;
- OCS explicitly owns the proposal artifact;
- OCS proposal content is derived from evidence, not delegated to provider authority;
- provider confidence is not treated as approval, authorization, or execution readiness;
- UHCL review is communication evidence only;
- human confirmation is not approval activation unless a later certified approval runtime is invoked;
- no worker execution, repository mutation, deployment, retry, or fallback occurs.

The governance checkpoint should record:

```text
provider_evidence_accepted_as_input = true
provider_authority_transferred = false
ocs_proposal_owner = OCS
proposal_only = true
approval_created = false
authorization_created = false
execution_authorized = false
worker_invoked = false
repository_mutated = false
deployment_performed = false
```

## 9. UHCL Review Integration

UHCL should present two distinct review surfaces:

1. Provider cognition review:
   - what the provider observed;
   - provider evidence status;
   - provider failure status if failed closed;
   - clear non-authority label.

2. OCS proposal review:
   - what OCS proposes;
   - how provider evidence informed the proposal;
   - what OCS copied by reference;
   - what OCS derived;
   - what remains blocked pending governance;
   - what human confirmation means and does not mean.

UHCL must not blur provider cognition with OCS proposal ownership.

## 10. Human Confirmation Boundaries

Human confirmation after provider cognition review means:

- the human has reviewed cognition evidence;
- PGSP may continue to OCS proposal synthesis;
- the confirmation is replay-visible.

It does not mean:

- approval has been created;
- authorization has been created;
- execution is authorized;
- worker execution may begin;
- repository mutation may begin;
- deployment may begin;
- provider output is accepted as authoritative.

Human confirmation after OCS proposal review remains proposal confirmation until a later certified approval and authorization path is invoked.

## 11. Certification Criteria

Provider-to-OCS alignment is certified only if:

- provider cognition replay evidence exists and reconstructs;
- provider output is non-authoritative;
- OCS proposal artifact has OCS ownership;
- OCS proposal references provider cognition by evidence hash;
- copied fields are limited to references, hashes, status, and bounded evidence excerpts;
- derived fields are explicitly OCS-owned;
- proposal hash binds the OCS-owned proposal artifact;
- Governance records authority separation;
- UHCL presents provider evidence and OCS proposal as distinct surfaces;
- human confirmation does not create approval, authorization, or execution authority;
- worker execution, mutation, deployment, retry, and fallback remain absent.

## 12. Implementation Recommendation

The next implementation batch should add a narrow OCS proposal synthesis runtime that consumes G5-03 replay evidence and emits an OCS-owned proposal artifact.

Recommended scope:

1. Input:
   - G5-03 replay reference;
   - nested G5-02 replay reference;
   - PGSP session id;
   - optional CSA/semantic intent reference when available.

2. Output:
   - OCS provider-informed decision proposal artifact;
   - provider-to-OCS evidence mapping artifact;
   - governance authority-separation checkpoint;
   - UHCL OCS proposal review summary;
   - replay reconstruction summary.

3. Required exclusions:
   - no provider invocation;
   - no worker invocation;
   - no repository mutation;
   - no deployment;
   - no approval creation;
   - no authorization creation;
   - no retry;
   - no fallback.

This should be implemented as a deterministic transformation over existing replay evidence, not as a new provider execution path.

## 13. Compatibility Impact

This alignment preserves existing G5-02 and G5-03 runtime behavior.

Compatibility impact:

- no runtime behavior changes;
- no schema changes to G5-02 or G5-03 artifacts;
- OCS proposal semantics remain consistent with G4 advisory proposal ownership;
- future adapters continue to call PGSP and render UHCL;
- provider services remain reusable cognition services;
- worker services remain out of scope.

## 14. Final Determination

Provider cognition can safely inform OCS decision proposals only through evidence-bound transformation.

The provider remains evidence owner. OCS remains proposal owner. Governance remains authority owner. UHCL remains communication owner. Replay remains reconstruction owner.

Final verdict: PROVIDER_TO_OCS_ALIGNMENT_READY
