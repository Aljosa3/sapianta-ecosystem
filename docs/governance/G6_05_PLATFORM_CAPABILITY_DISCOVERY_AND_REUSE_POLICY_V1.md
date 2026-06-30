# G6-05 Platform Capability Discovery And Reuse Policy V1

Status: canonical discovery and reuse policy defined.

Final verdict: PLATFORM_CAPABILITY_DISCOVERY_POLICY_READY

## 1. Purpose

G6-05 defines the mandatory Platform Capability Discovery and Reuse Policy for AiGOL.

Before introducing any new subsystem, runtime, facade, provider layer, Worker layer, adapter-owned semantic path, governance mechanism, replay mechanism, or execution pathway, the proposer must first prove that the capability does not already exist in Platform Core or that the existing capability cannot be safely reused, canonicalized, or extended.

This policy is documentation-only. It does not introduce runtime behavior, repository mutation, provider execution, Worker execution, deployment, approval activation, or authorization activation.

## 2. Executive Determination

Generations 3 through 6 repeatedly found that proposed new capabilities already existed as reusable Platform Core components.

The recurring outcome was not "build a new runtime." The recurring outcome was:

```text
discover existing capability -> verify ownership -> reuse unchanged where possible -> canonicalize names where needed -> extend only the missing production surface
```

Platform Capability Discovery is therefore a mandatory first step for all future architecture and implementation work.

## 3. Historical Reuse Pattern

| Area Reviewed | Reuse Outcome | Policy Lesson |
| --- | --- | --- |
| UBTR audits | UBTR already existed as the canonical semantic translation authority, with compatibility layers and extension gaps. | Do not create interface-local translators. Extend canonical UBTR consumers and compatibility retirement paths. |
| UHCL audits | Human communication capability existed across UBTR and shared communication artifacts, then became UHCL specialization work. | Do not let adapters generate reusable explanations or confirmations. Promote shared communication models. |
| PGSP and LGDS audits | LGDS existed as the G4 governed session runtime; PGSP became the broader canonical protocol; no new runtime facade was required. | Prefer public API naming and adapter contracts before adding facade code. |
| Worker Runtime audits | Existing Worker runtime was reusable; the gap was PGSP orchestration and wiring. | Do not duplicate Worker identity, authorization, replay, dispatch, or failure handling. |
| External Provider Platform audits | A broad EPP already existed across provider abstraction, registry, connectors, transport, credential vault, governance, replay, and PGSP provider cognition. | Do not create a new Provider Services architecture when canonicalization and indexing are enough. |
| Natural-language onboarding audits | Provider onboarding already existed as a certified natural-language domain with credential vault, approval, replay, and governance evidence. | Extend lifecycle coverage instead of creating a new onboarding runtime. |

## 4. Mandatory Discovery Workflow

Every proposal for a new subsystem or runtime must complete this workflow before implementation:

1. State the requested capability in neutral Platform Core terms.
2. Search existing governance artifacts for prior audits, certifications, and final verdicts.
3. Search runtime modules and tests for matching capability names, artifacts, entrypoints, replay builders, and certification packages.
4. Identify the current owner of each matching capability.
5. Verify whether the existing owner is canonical, compatibility-only, deprecated, or ambiguous.
6. Map the proposed capability to existing artifacts, APIs, replay evidence, governance checks, and adapter contracts.
7. Classify the outcome as reuse unchanged, canonical naming, thin facade, extension, or new implementation.
8. Document duplication risks.
9. Document governance and replay impact.
10. Validate the audit artifact with `git diff --check`.

No implementation batch may proceed until the discovery result is recorded.

## 5. Decision Tree

```text
New capability proposed
        |
        v
Does a matching capability already exist?
        |
        +-- Yes --> Is ownership canonical and runtime usable?
        |              |
        |              +-- Yes --> Reuse existing API unchanged.
        |              |
        |              +-- Mostly --> Canonicalize naming or document public API.
        |              |
        |              +-- Partially --> Extend existing runtime or contract.
        |
        +-- No --> Does the capability exist under another name?
        |              |
        |              +-- Yes --> Create compatibility mapping or naming policy.
        |              |
        |              +-- No --> Is a broader Platform Core primitive missing?
        |                             |
        |                             +-- Yes --> Propose new canonical primitive.
        |                             |
        |                             +-- No --> Reject or defer proposal.
```

New runtime implementation is permitted only after the audit proves all of the following:

- no existing runtime provides the capability;
- no existing runtime can be safely extended without violating ownership;
- no canonical naming, public API, or thin facade can expose the capability;
- replay evidence requirements cannot be satisfied by current replay models;
- governance checkpoints cannot be satisfied by current governance mechanisms;
- the new runtime has a clearly bounded owner and does not duplicate Platform Services.

## 6. Reuse Decision Criteria

Reuse existing capability unchanged when:

- the existing runtime already satisfies the requested behavior;
- ownership matches the certified architecture;
- replay evidence exists and reconstructs;
- governance evidence exists and remains admissible;
- adapters can call or render the existing public API;
- no authority transfer or mutation boundary change is required.

Canonicalize naming when:

- the capability exists under a narrower or historical name;
- the runtime is correct but the long-term architectural term is broader;
- future adapters need a stable term;
- documentation can resolve the mismatch without runtime code.

Use a lightweight facade only when:

- multiple adapters need one import surface;
- the facade delegates to existing runtimes;
- the facade does not own semantic interpretation, governance, replay, provider execution, Worker execution, approval, authorization, or mutation;
- documentation alone has become insufficient for compatibility.

Extend existing capability when:

- the current runtime covers the seed or certification case but not the full production surface;
- the missing feature belongs to the same owner;
- extension can preserve existing artifacts and replay compatibility;
- tests can prove no authority drift.

Create a new implementation only when:

- the capability is genuinely absent;
- the capability has no safe existing owner;
- extension would distort or overburden an existing layer;
- the new owner and boundaries are constitutionally clear;
- replay and governance evidence can be defined before runtime activation.

## 7. Canonicalization Criteria

Canonicalization is preferred over implementation when the problem is one of naming, discoverability, or adapter access.

Canonicalization may include:

- architecture index documents;
- public API contracts;
- compatibility maps;
- ownership matrices;
- naming migration recommendations;
- certification criteria;
- adapter invocation contracts.

Canonicalization must not:

- rename runtime modules prematurely;
- move ownership between layers;
- hide compatibility layers;
- claim production readiness without evidence;
- create new authority paths.

## 8. Extension Criteria

Extension is justified when existing capability is real but incomplete.

Valid extension examples:

- UBTR consumer migration beyond compatibility paths;
- UHCL communication level expansion over existing evidence;
- PGSP adapter contract expansion without a new runtime;
- PGSP orchestration over existing Worker runtime;
- EPP lifecycle coverage over the existing provider onboarding domain;
- provider replacement and retirement scenarios over the credential vault.

Invalid extension examples:

- adding provider selection to UBTR;
- adding semantic interpretation to ACLI;
- adding reusable explanation generation to adapters;
- adding Worker authorization checks outside the certified Worker boundary;
- adding provider governance authority to providers;
- adding replay mutation outside Replay ownership.

## 9. Ownership Implications

Discovery must preserve ownership before it optimizes implementation speed.

| Capability Type | Canonical Owner | Discovery Rule |
| --- | --- | --- |
| Human input capture | Interface Adapter | Adapter may capture and render only. |
| Semantic translation | UBTR | Search UBTR before creating translation logic anywhere else. |
| Canonical intent | CSA | Reuse CSA artifacts before adding domain-specific intent shapes. |
| Session protocol | PGSP | Future adapters call PGSP, not bespoke session protocols. |
| Orchestration | OCS | Reuse OCS proposal and orchestration paths before adding flow logic elsewhere. |
| Human communication | UHCL | Reuse UHCL before writing explanations in adapters or services. |
| Provider integration | EPP / Provider Services | Reuse EPP registry, credential, connector, transport, governance, and replay surfaces. |
| Worker execution | Worker Services | Reuse Worker identity, authorization, dispatch, replay, failure, and post-execution review. |
| Governance checkpoints | Governance | Governance owns admissibility and authority boundaries. |
| Replay reconstruction | Replay | Replay owns reconstruction and continuity evidence. |

If discovery finds that a proposed capability would move one of these responsibilities, the proposal must be rejected or rewritten.

## 10. Governance Implications

The discovery policy is a governance control.

It prevents:

- duplicate authority paths;
- adapter-owned semantics;
- provider-owned execution authority;
- Worker runtime duplication;
- unreviewed governance bypass;
- replay fragmentation;
- hidden mutation paths;
- premature production claims;
- architecture drift through convenience facades.

Every discovery audit must state:

- whether the capability already exists;
- whether it is canonical, partial, or under another name;
- whether reuse, canonicalization, extension, facade, or new implementation is recommended;
- what governance evidence already exists;
- what governance evidence is missing;
- what replay continuity exists;
- what replay continuity is missing.

## 11. Implementation Policy

Implementation batches must follow this order:

1. Discovery audit.
2. Ownership verification.
3. Replay and governance assessment.
4. Reuse decision.
5. Canonical API or naming document if needed.
6. Runtime extension only if the audit proves it is required.
7. Targeted tests for changed runtime behavior.
8. Full validation when execution behavior changes.

Runtime code must not be introduced merely to make a concept easier to name.

Runtime code may be introduced only when documentation, indexing, compatibility aliases, or existing entrypoints cannot satisfy the certified need.

## 12. Certification Policy

A capability discovery audit is certification-ready when it includes:

- scope and non-goals;
- reviewed components;
- existing capability inventory;
- capability mapping;
- ownership matrix;
- replay assessment;
- governance assessment;
- duplication risk assessment;
- reuse, canonicalization, facade, extension, or new-runtime recommendation;
- validation result.

Allowed final verdict patterns:

- `*_REUSE_CONFIRMED`
- `*_EXISTING_API_SUFFICIENT`
- `*_LIGHTWEIGHT_FACADE_RECOMMENDED`
- `*_EXTENSION_REQUIRED`
- `*_CANONICAL_READY`
- `*_RESTRUCTURING_REQUIRED`
- `*_NEW_RUNTIME_REQUIRED`

Verdicts must be specific to the capability under review and must not hide partial readiness.

## 13. Required Evidence Sources

At minimum, discovery must inspect:

- current and prior governance documents;
- runtime modules;
- tests;
- replay reconstruction functions;
- public API indexes;
- adapter contracts;
- credential and authorization boundaries where relevant;
- ownership declarations;
- final verdicts from related milestones.

For documentation-only discovery, `git diff --check` is the minimum validation.

For runtime changes following discovery, validation must match the touched surface and include targeted tests. Full pytest is required when execution, replay, governance, PGSP, provider, Worker, or adapter behavior changes.

## 14. Duplication Risk Checklist

Before implementation, answer:

- Would this duplicate UBTR translation?
- Would this duplicate UHCL communication?
- Would this duplicate PGSP session protocol?
- Would this duplicate OCS orchestration?
- Would this duplicate Provider Services or EPP?
- Would this duplicate Worker runtime?
- Would this duplicate credential vault behavior?
- Would this duplicate governance checks?
- Would this duplicate replay reconstruction?
- Would this make an adapter own reusable Platform Core logic?

If any answer is yes, implementation must stop until reuse or extension is resolved.

## 15. Compatibility Impact

This policy preserves compatibility by requiring:

- existing runtime names to remain valid unless a migration is explicitly certified;
- compatibility aliases to be documented before code movement;
- current replay artifacts to remain reconstructable;
- adapter contracts to consume Platform Core rather than duplicate it;
- production claims to reflect actual certification state.

## 16. Roadmap Impact

Future milestones should start with capability discovery unless they are explicitly scoped as extensions of a previously audited capability.

Recommended standing milestone pattern:

1. `*_EXISTING_CAPABILITY_REUSE_AUDIT_V1`
2. `*_CANONICAL_PUBLIC_API_OR_NAMING_V1`
3. `*_CONTRACT_AND_CERTIFICATION_CRITERIA_V1`
4. `*_MINIMAL_RUNTIME_EXTENSION_V1`
5. `*_LIVE_ENTRYPOINT_OR_PRODUCTION_CERTIFICATION_V1`

This keeps AiGOL evolution bounded, replay-safe, and constitutionally aligned.

## 17. Final Determination

Platform Capability Discovery is now a mandatory policy gate before new subsystem or runtime implementation.

The correct default posture is reuse before redesign, canonicalize before facade, facade before runtime, and extension before new implementation.

Final verdict: PLATFORM_CAPABILITY_DISCOVERY_POLICY_READY
