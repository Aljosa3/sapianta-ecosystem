# G4-07 Platform Session Protocol Naming Audit V1

Status: PLATFORM SESSION PROTOCOL NAMING AUDIT COMPLETE

Final verdict: CANONICAL_NAME_RECOMMENDED

## 1. Objective

This audit determines whether `LGDS`, Live Governed Development Session, is the
right canonical name for the protocol currently emerging from G4-02, G4-04, and
G4-05.

The purpose is to avoid locking Platform Core into an overly narrow protocol
name before Web, REST, Voice, Mobile, Product, governance, replay, diagnostic,
and domain-specific workflows begin using the same interaction pattern.

This is a naming and architectural audit only. It does not modify runtime code,
tests, ACLI, UBTR, CSA, OCS, Governance, UHCL, Replay, Provider Services,
Worker Services, approval, authorization, deployment, or mutation behavior.

## 2. Protocol Purpose Assessment

The layer currently represented as:

```text
Human
-> Interface Adapter
-> ???
-> UBTR
-> CSA
-> OCS
-> Governance
-> UHCL
-> Replay
-> Execution Intent
```

is not merely an AiGOL self-development protocol.

It is the Platform Core session protocol that accepts an interface-captured human
interaction, preserves adapter-only boundaries, routes into canonical semantic
translation, binds structured intent, preserves governance and replay evidence,
returns reusable human communication, captures human response classes, and
prepares advisory or governed execution intent.

The current G4 implementation proves this protocol first for governed natural
language development because Generation 4 is focused on replacing the
ChatGPT/Codex copy-paste development workflow. The underlying shape is broader
than development.

## 3. Required Questions

### 1. Is the protocol intended only for AiGOL self-development?

No. AiGOL self-development is the first certified use case, not the long-term
limit of the protocol.

The protocol should eventually govern every Platform Core interaction that
starts from a human/interface request and must pass through canonical semantics,
governance, UHCL communication, replay evidence, and bounded execution intent.

### 2. Should future interactions use the same protocol?

Yes, where the interaction is a governed Platform Core interaction.

Future users of the same protocol should include:

- Product workflows;
- business processes;
- medical workflows;
- energy workflows;
- administration;
- diagnostics;
- replay review;
- governance review;
- domain-specific governed workflows;
- future interface adapters such as Web, REST, Voice, and Mobile.

Each domain may have its own product, policy, provider, worker, or evidence
specialization, but the session protocol should remain shared.

### 3. Does the word Development become too restrictive?

Yes. `Development` is accurate for the Generation 4 proving path, but too narrow
for the canonical Platform Core protocol.

Using `Development` in the canonical protocol name would create future pressure
to rename or fork the protocol when non-development workflows become first-class
users. That would conflict with the no-duplication principle established in
Generation 4.

### 4. What broader concept should the canonical protocol represent?

The canonical protocol should represent governed platform sessions.

It should not be named for a single domain such as development, Product 1,
medical workflows, diagnostics, administration, or replay review. It should name
the shared Platform Core session boundary between interface adapters and
canonical Platform Core services.

Recommended canonical concept:

`Platform Governed Session Protocol`

Recommended short name:

`PGSP`

Acceptable descriptive expansion:

`Governed Platform Session Protocol`

Rejected as canonical:

- `Live Governed Development Session`, because it is development-specific;
- `Governed Intent Protocol`, because it overemphasizes intent and undernames
  session, communication, response, governance, and replay continuity;
- `Governed Interaction Protocol`, because it is plausible but less explicit
  about Platform Core session boundaries;
- `Governed Workflow Session`, because it risks conflating the session protocol
  with downstream workflow execution.

### 5. Should LGDS remain canonical, specialized, or implementation-only?

LGDS should not become the canonical Platform Core protocol name.

LGDS should remain one of the following:

- a specialization of PGSP for governed development sessions; or
- the current implementation name for the G4 development proving path.

LGDS may remain useful in G4 lineage because it accurately describes the first
live development session path. It should not own the universal interface-adapter
to Platform Core session contract.

### 6. Interface Adapter, Platform Session Protocol, and Platform Services

These concepts must remain distinct:

| Concept | Owns | Does not own |
| --- | --- | --- |
| Interface Adapter | Modality capture, rendering, response capture, local session interaction, adapter-specific formatting. | Semantic translation, reusable communication, governance policy, replay reconstruction, provider logic, worker logic, execution authority. |
| Platform Session Protocol | The neutral session boundary that accepts adapter-captured interaction, binds it into UBTR/CSA/OCS/Governance/UHCL/Replay, preserves human response lineage, and prepares bounded execution intent. | Provider execution, worker execution, repository mutation, deployment, approval creation, authorization creation, interface-specific UI. |
| Platform Services | Reusable UBTR, CSA, OCS, Governance, UHCL, Replay, Provider Services, Worker Services, Product services, validation, and evidence capabilities. | Interface ownership or adapter-specific presentation. |

The Platform Session Protocol uses Platform Services. It does not replace them.
Interface adapters call the Platform Session Protocol. They do not own it.

## 4. Naming Analysis

| Candidate name | Strength | Weakness | Recommendation |
| --- | --- | --- | --- |
| `Live Governed Development Session` / `LGDS` | Accurate for G4-05 live ACLI development path. | Too narrow for Product, governance, replay, diagnostics, administration, medical, energy, and business workflows. | Keep as specialization/current lineage name only. |
| `Platform Governed Session Protocol` / `PGSP` | Names the Platform Core boundary, governance, session continuity, and protocol nature. | New acronym requires documentation. | Recommended canonical name. |
| `Governed Platform Session Protocol` | Similar to PGSP, slightly more grammatical as prose. | Acronym ordering less direct if shortened as GPSP. | Acceptable expansion, not preferred short name. |
| `Governed Interaction Protocol` | Broad and adapter-neutral. | Could be confused with interface interaction only, not full session/replay/governance continuity. | Not canonical. |
| `Governed Intent Protocol` | Emphasizes UBTR/CSA intent path. | Too narrow; undernames UHCL, replay, response capture, and session continuity. | Not canonical. |
| `Governed Workflow Session` | Works for domain workflows. | Risks conflating session protocol with downstream workflow execution. | Not canonical. |
| `Universal Governed Session Protocol` | Broad and future-facing. | `Universal` can sound stronger than current certified scope. | Possible future descriptor, not current canonical name. |

## 5. Long-Term Scalability Assessment

The canonical name must scale across:

- multiple interface adapters;
- multiple product domains;
- advisory-only and executable future sessions;
- human confirmation and clarification loops;
- governance and replay review workflows;
- provider-assisted cognition where OCS owns orchestration;
- worker execution readiness where Worker Services own execution lifecycle;
- Product 1 and future products as Platform Core consumers.

`LGDS` does not scale cleanly because `Development` will be false or misleading
for many future interactions.

`PGSP` scales because it names the stable architectural position rather than the
first use case.

## 6. Architectural Terminology Review

Recommended terminology:

- `Platform Governed Session Protocol`: canonical neutral protocol.
- `LGDS`: governed development specialization of PGSP.
- `ACLI live session entrypoint`: ACLI adapter entrypoint into PGSP/LGDS.
- `G4-04 session runtime`: current implementation substrate for the first PGSP
  proving path.
- `G4-02 scaffold`: current protocol engine substrate for the governed loop.
- `Interface Adapter`: modality-specific capture/render/response layer.
- `Platform Services`: UBTR, CSA, OCS, Governance, UHCL, Replay, Provider
  Services, Worker Services, Product services, and validation/evidence
  capabilities.

Avoid:

- using `LGDS` as the universal protocol name;
- calling ACLI the session protocol;
- calling UBTR the session protocol;
- calling Provider or Worker Services session owners;
- creating product-specific session protocols when PGSP can be specialized.

## 7. Recommendation

Canonical name recommendation:

`Platform Governed Session Protocol`

Canonical short name:

`PGSP`

Rationale:

- captures the architectural role of the `???` layer;
- remains interface-neutral;
- remains domain-neutral;
- preserves LGDS as the development specialization;
- avoids future renaming when Product, governance, replay, diagnostics, medical,
  energy, administration, or business workflows use the same session pattern;
- prevents a new runtime from being justified by naming ambiguity;
- aligns with Generation 4 no-duplication and adapter-only principles.

## 8. Migration Impact

No runtime migration is required by this audit.

Recommended future naming migration should be additive only:

- keep existing G4-02, G4-04, and G4-05 artifact names for lineage;
- add PGSP facade documentation and optional facade artifacts in a later batch;
- document LGDS as a PGSP specialization;
- avoid renaming existing replay artifacts in place;
- avoid changing existing hashes or replay reconstruction behavior.

## 9. Compatibility Impact

Compatibility impact is low if the next batch is facade-only.

Required compatibility constraints:

- existing G4-04 calls remain valid;
- existing G4-05 ACLI entrypoint remains valid;
- existing replay artifacts remain reconstructable;
- existing LGDS audit remains historically valid as a development-session reuse
  audit;
- new PGSP terminology must not imply provider execution, worker execution,
  approval creation, authorization creation, repository mutation, deployment, or
  autonomous continuation.

## 10. Roadmap Impact

The G4-06 recommended batch should be renamed before implementation.

Replace:

`G4_07_LGDS_CANONICAL_FACADE_AND_NAMING_ALIGNMENT_V1`

with:

`G4_08_PGSP_CANONICAL_FACADE_AND_LGDS_SPECIALIZATION_ALIGNMENT_V1`

The numbering advances because this G4-07 audit consumes the G4-07 slot.

Recommended scope for the next implementation batch:

- define PGSP as the neutral Platform Core session protocol facade;
- define LGDS as the governed development specialization of PGSP;
- delegate to the existing G4-04 session runtime;
- keep G4-05 as the ACLI live adapter over the development specialization;
- add no new translation, communication, governance, replay, provider, worker,
  approval, authorization, mutation, or deployment behavior;
- validate with `git diff --check` and targeted facade tests only.

## 11. Final Determination

The protocol currently called LGDS is broader than development. It represents
the Platform Core governed session boundary between interface adapters and
canonical Platform Services.

`Development` is not sufficiently general for the canonical protocol name.

LGDS should remain as the current governed development specialization and G4
lineage label. The canonical long-term protocol name should be:

`Platform Governed Session Protocol (PGSP)`

Final verdict: CANONICAL_NAME_RECOMMENDED
