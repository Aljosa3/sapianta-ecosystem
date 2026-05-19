# AGOL_CONSTITUTIONAL_NAMING_FOUNDATION_V1

## Status

Normalization review complete.

Decision: `NORMALIZATION_PARTIAL`

This milestone normalizes constitutional terminology, naming hierarchy, and
governance identity across AGOL / AiGOL / SAPIANTA artifacts after the AGOL
constitutional foundation review.

This milestone is review, normalization, and specification only. It does not
modify runtime behavior, introduce APIs, add orchestration, add workers, expand
execution capability, or introduce semantic autonomy.

## 1. Constitutional Identity

### SAPIANTA

`SAPIANTA` is the constitutional governance substrate and product governance
identity. It names the broader repository system, constitutional governance
model, Product 1 enterprise positioning, audit continuity, replay discipline,
and stable governance infrastructure.

Use `SAPIANTA` when referring to:

- constitutional governance infrastructure;
- Product 1, AI Decision Validator;
- enterprise execution governance positioning;
- repository-wide governance substrate;
- browser companion product identity where existing UI already uses SAPIANTA.

### AGOL

`AGOL` is the governed operational layer family inside the SAPIANTA substrate.
It names operational governance primitives, bridge transport, replay-safe
workflow continuity, runtime visibility, refinement guidance, and governed
transport foundation work.

Use `AGOL` when referring to:

- governed operational layer milestones;
- AGOL Bridge;
- AGOL Bridge Transport Spec;
- AGOL Bridge Runtime Foundation;
- operational continuity, replay, lifecycle, and transport artifacts.

### AiGOL

`AiGOL` is the semantic-direction governance identity within the AGOL family. It
is used when discussing admissible semantic evolution, semantic direction
governance, and the separation between model-native cognition and
system-native governance.

Use `AiGOL` when referring to:

- semantic direction governance;
- admissible semantic evolution;
- governance over LLM-proposed direction;
- the role boundary: LLM cognition may propose, AiGOL may admit, constrain, or
  reject.

Do not use `AiGOL` to imply autonomous cognition, autonomous planning, hidden
orchestration, or execution authority.

### Relationship Hierarchy

The canonical relationship is:

`SAPIANTA` -> constitutional governance substrate
`AGOL` -> governed operational layer family within SAPIANTA
`AiGOL` -> semantic-direction governance identity within AGOL

The execution boundary remains separate:

`ChatGPT / LLMs` -> semantic cognition
`AiGOL / AGOL` -> semantic direction governance, replay, lifecycle, transport
`Codex / workers` -> execution through governed transport only

## 2. Naming Hierarchy

### Constitutional Layer Naming

Use `SAPIANTA` for constitutional architecture, invariants, enforcement
hierarchy, lineage model, stable substrate declarations, and enterprise product
identity.

### Governance Layer Naming

Use `AGOL` for governed operational governance primitives and transport
foundation artifacts. Use `AiGOL` only where semantic direction governance is
the subject.

### Runtime Layer Naming

Use `AGOL_BRIDGE_RUNTIME_*` for filesystem bridge runtime artifacts. Use
`GOVERNED_*_RUNTIME_*` for runtime surfaces that are not specifically AGOL
Bridge filesystem transport, such as browser sidepanel and preview runtime
milestones.

### Observability Layer Naming

Use `GOVERNED_*_OBSERVABILITY_*` for read-only inspection capabilities. Use
`SIDEPANEL` only for Browser Companion UX surfaces that render lifecycle or
runtime output.

### Replay and Certification Naming

Use suffixes that state the evidence type:

- `_REPLAY_CERTIFICATION`
- `_LIFECYCLE_CERTIFICATION`
- `_OBSERVABILITY_CERTIFICATION`
- `_ACCEPTANCE`
- `_BOUNDARIES`
- `_USAGE`

### ADR Numbering Rules

New top-level governance ADRs must replace `ADR-00X` with a stable numeric
identifier before constitutional finalization.

Recommended format:

`ADR-###-SHORT-TITLE.md`

Existing `.github/governance/adr/ADR_*_V1.md` artifacts may keep their historic
underscore naming unless a dedicated migration milestone renames them.

### Finalize Milestone Naming Rules

Use:

`FINALIZE_<MILESTONE_ID>_V<N>.md`
`FINALIZE_<MILESTONE_ID>_V<N>.json`

When the milestone id already includes `_V1`, do not append another version
suffix.

### Evidence Naming Rules

Use:

`<MILESTONE_ID>_<EVIDENCE_TYPE>.json`
`<MILESTONE_ID>_<EVIDENCE_TYPE>.md`

Evidence type must be one of acceptance, certification, replay, lifecycle,
observability, boundaries, usage, or finalize evidence.

## 3. Canonical Terminology

### Canonical Terms

- `SAPIANTA constitutional governance substrate`
- `AGOL governed operational layer`
- `AiGOL semantic direction governance`
- `AGOL Bridge`
- `AGOL Bridge Transport Spec v1`
- `AGOL Bridge Runtime Foundation`
- `Governed Browser Sidepanel Runtime`
- `governed transport`
- `replay-safe transport`
- `append-only replay log`
- `lifecycle transition`
- `approval-gated dispatch`
- `quarantine`
- `fail-closed`
- `bounded in-memory continuity`
- `localhost-only interaction`
- `explicit confirmation`
- `read-only observability`

### Deprecated or Discouraged Terms

These terms are not banned historically, but should not be used for new
architecture decisions:

- `full autonomous semantic runtime`
- `autonomous semantic operating system`
- `semantic autonomy engine`
- `unrestricted autonomous AI`
- `self-evolving governance`
- `hidden orchestration`
- `automatic execution authority`
- `ChatGPT execution authority`

## 4. Artifact Consistency Review

### ADR Names

Top-level governance ADRs currently use placeholder numbering:

- `ADR-00X-AGOL-BRIDGE-PIVOT.md`
- `ADR-00X-SEMANTIC-DIRECTION-GOVERNANCE.md`

These are semantically aligned but numerically incomplete. Future governance
finalization should assign stable ADR numbers.

### Finalize Milestone Names

Finalize milestone names are aligned with existing repo convention:

- `FINALIZE_AGOL_BRIDGE_RUNTIME_FOUNDATION_V1.*`
- `FINALIZE_GOVERNED_BROWSER_SIDEPANEL_RUNTIME_V1.*`

### Runtime Evidence Names

Runtime evidence is aligned when it uses milestone id plus evidence type:

- `AGOL_BRIDGE_RUNTIME_FOUNDATION_*`
- `GOVERNED_BROWSER_SIDEPANEL_RUNTIME_V1_ACCEPTANCE`
- `BROWSER_COMPANION_SIDEPANEL_*`

The sidepanel evidence contains both `BROWSER_COMPANION_SIDEPANEL_*` and
`GOVERNED_BROWSER_SIDEPANEL_RUNTIME_V1_*` families. This is acceptable as a
transition, but future evidence should prefer the finalized milestone id.

### Governance Artifact Names

Existing historical governance artifacts use `AGOL_*`, `GOVERNED_*`, and
`SAPIANTA_*` prefixes. This review does not rename them. It defines future
guidance so new artifacts choose the narrowest accurate identity.

### Sidepanel Terminology

Use `Governed Browser Sidepanel Runtime` for the finalized milestone. Use
`Browser Companion sidepanel` for the UX surface. Do not imply browser autonomy
or hidden browser state.

### Bridge Terminology

Use `AGOL Bridge` for governed filesystem transport and replay lifecycle
substrate. Do not use bridge terminology to imply semantic reasoning or worker
orchestration.

## 5. Draft vs Canonical Status

### Draft

`Draft` means the artifact is usable for implementation guidance but remains
open to bounded correction before canonical freeze.

### Finalized

`Finalized` means a milestone has been accepted and certified against its stated
scope. Finalization certifies that milestone, not necessarily every referenced
specification as constitutional canon.

### Canonical

`Canonical` means the artifact is the governing reference for future work within
its scope. Changes require explicit governance review and preservation of
lineage.

### Constitutional

`Constitutional` means the artifact constrains repository interpretation and
must not be silently reinterpreted, bypassed, or mutated by ordinary feature
work.

### AGOL Bridge Transport Spec v1 Status

`AGOL_BRIDGE_TRANSPORT_SPEC_V1.md` remains `Draft v1` after this review.

Decision: the spec is a `Draft Foundation Spec` that has been implemented and
finalized through `AGOL_BRIDGE_RUNTIME_FOUNDATION_V1`, but it is not yet a
canonical constitutional artifact. A follow-up milestone should either freeze it
as `Canonical Foundation Spec v1` or issue a corrected v1.1 before canonical
designation.

## Normalization Decision

Decision: `NORMALIZATION_PARTIAL`

The identity model and naming hierarchy are stable enough for future work. Full
normalization is partial because existing historical artifacts still contain
mixed naming and placeholder ADR numbering.

## Remaining Ambiguities

1. Stable numeric ADR ids have not yet been assigned to the top-level governance
   ADRs.
2. Historical artifacts mix `AGOL`, `AiGOL`, `AIGOL`, and `SAPIANTA` in ways
   that should not be rewritten without a dedicated migration plan.
3. The transport spec remains Draft while the runtime foundation is finalized.
4. Some Browser Companion sidepanel evidence uses pre-finalization naming.

## Recommended Follow-Up

Create a bounded artifact indexing milestone that:

- assigns stable ADR numbers;
- records alias mappings for AGOL, AiGOL, AIGOL, and SAPIANTA;
- decides whether AGOL Bridge Transport Spec v1 becomes canonical;
- defines whether historical artifact renaming is prohibited, optional, or
  required only through migration manifests.
