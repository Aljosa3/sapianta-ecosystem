# AGOL_CONSTITUTIONAL_LINEAGE_NORMALIZATION_V1

## Status

Lineage normalization complete.

Stabilization status: `CONSTITUTIONAL_LINEAGE_STABLE`

This milestone stabilizes constitutional lineage semantics after:

- AGOL Constitutional Foundation Review
- AGOL Constitutional Naming Foundation Review
- AGOL Bridge Runtime Foundation Finalization
- Governed Browser Sidepanel Runtime Finalization

This milestone is normalization, governance stabilization, constitutional
alignment, and lineage clarification only. It does not modify runtime behavior,
add APIs, expand execution authority, add orchestration, add workers, add
semantic autonomy, or implement replay visualization.

## 1. ADR Numbering Normalization

### Canonical ADR Numbering Strategy

Future top-level governance ADRs must use stable numeric identifiers:

`ADR-###-SHORT-TITLE.md`

The numeric identifier must be assigned once and must not be reused for a
different decision. Short titles may clarify the decision but must not become
the only stable identity.

Existing historical ADRs under `.github/governance/adr/ADR_*_V1.md` remain
historically valid. They are lineage artifacts and must not be renamed without a
dedicated migration manifest.

### Stable Numbering Allocation Rules

1. Allocate the next available numeric id in a monotonic sequence for new
   top-level governance ADRs.
2. Do not reuse numbers after withdrawal, replacement, or supersession.
3. Record supersession through an alias or migration manifest rather than
   rewriting historical references.
4. Preserve the original filename in replay and audit evidence.
5. If a placeholder ADR becomes canonical, assign a stable number and record the
   placeholder as an alias.

### Placeholder ADR Migration Policy

`ADR-00X-*` files are acceptable as transitional review artifacts but must not
be promoted to constitutional status without stable numbering or an alias
manifest.

Placeholder ids remain historically valid after migration. They may be cited as
aliases, but new references should prefer the stable numeric id after assignment.

### Replay-Safe ADR Reference Policy

Replay-safe references must include one of:

- canonical numeric ADR id;
- original historical filename;
- migration manifest id;
- alias mapping id.

Do not silently rewrite references in existing evidence. New evidence may add a
canonical reference while preserving the historical reference that existed at
the time of creation.

## 2. Canonical Naming Freeze

### SAPIANTA

Canonical meaning: constitutional governance substrate and product governance
identity.

Use for constitutional architecture, invariants, enforcement hierarchy, lineage
model, stable substrate declarations, Product 1 positioning, enterprise
governance evidence, and browser companion product identity where already
established.

### AGOL

Canonical meaning: governed operational layer family within SAPIANTA.

Use for governed operational primitives, AGOL Bridge, transport foundation,
runtime continuity, replay-safe workflow, lifecycle, refinement guidance, and
operational governance milestones.

### AiGOL

Canonical meaning: semantic-direction governance identity within AGOL.

Use only for admissible semantic evolution, semantic direction governance, and
the separation between model-native cognition and system-native governance.

Do not use AiGOL to imply autonomous cognition, hidden orchestration,
autonomous planning, or execution authority.

### Browser Companion

Canonical meaning: browser UX surface for explicit local governed interaction.

Use `Browser Companion` for the extension-level product surface and `Governed
Browser Sidepanel Runtime` for the finalized persistent sidepanel milestone.

### AGOL Bridge

Canonical meaning: deterministic governed transport and lifecycle substrate.

Use for filesystem package movement, schema validation, approval-gated dispatch,
append-only replay, lifecycle transitions, quarantine, and result package
return.

### Governance Runtime

Canonical meaning: governed runtime surfaces that enforce bounded,
confirmation-preserving, replay-visible interaction. Do not use this term to
imply autonomous runtime authority.

### Replay Artifacts

Canonical meaning: append-only or certification artifacts that preserve
historical reference, content hashes, lifecycle transitions, and audit
continuity.

### Lifecycle Artifacts

Canonical meaning: artifacts that declare or record bounded state transitions,
approval gates, dispatch boundaries, return state, finalization, quarantine, and
failure.

### Observability Artifacts

Canonical meaning: read-only inspection artifacts and surfaces. Observability
must not trigger execution or mutate governance state.

## 3. Historical Alias Mapping Policy

Historical naming drift is handled through replay-safe alias mappings, not
automatic renaming.

Historical artifact renaming is prohibited unless a dedicated migration
manifest is created before the rename and the old reference remains resolvable
through alias mapping.

Alias mapping semantics:

- alias mappings must preserve old name, new name, artifact class, migration
  reason, and effective date;
- alias mappings must be append-only governance artifacts;
- alias mappings must not delete or invalidate original references;
- alias mappings must distinguish historical aliases from preferred canonical
  names.

Migration manifest semantics:

- a migration manifest is required before any historical artifact rename;
- the manifest must list old path, new path, migration reason, affected
  references, replay impact, and rollback guidance;
- the manifest must certify that audit continuity and deterministic historical
  references are preserved.

Lineage preservation guarantees:

- replay continuity takes precedence over tidy naming;
- audit references must remain deterministic;
- historical filenames remain valid evidence references;
- canonical aliases may be added, but historical references must not be erased.

## 4. Draft / Finalized / Canonical / Constitutional States

### Draft

Draft means the artifact is usable for bounded implementation or review guidance
but remains open to correction before canonical freeze.

Mutation constraints: edits are allowed when they preserve stated scope and
lineage.

Replay implication: draft references are valid historical references but should
not be treated as immutable constitutional authority.

### Finalized

Finalized means a milestone has been accepted and certified against its stated
scope.

Mutation constraints: ordinary edits are not allowed; changes require a follow-up
milestone or superseding finalization artifact.

Replay implication: finalized artifacts are stable evidence for that milestone.

### Canonical

Canonical means the artifact is the governing reference for future work within
its declared scope.

Promotion rule: an artifact may become canonical only after explicit review,
stable identity, and lineage-preserving reference policy.

Mutation constraints: changes require governance review, versioning, or
supersession.

Replay implication: canonical artifacts may be used as primary references, but
older historical references remain valid through lineage and alias mapping.

### Constitutional

Constitutional means the artifact constrains repository interpretation and must
not be silently reinterpreted, bypassed, or mutated by ordinary feature work.

Promotion rule: constitutional promotion requires canonical status, explicit
constitutional scope, mutation boundary declaration, and replay-preserving
finalization.

Mutation constraints: mutation is forbidden except through explicit
constitutional governance process.

Replay implication: constitutional references are stable controls for future
review and conformance.

## 5. Constitutional Layer Clarification

### Semantic Cognition Layer

ChatGPT / LLMs generate semantic possibilities, candidate meanings, task
framings, and proposed directions. This layer does not grant execution
authority.

### Semantic Direction Governance Layer

AiGOL / AGOL governs whether proposed semantic direction is admissible,
constrained, approval-gated, quarantined, or rejected under governance
constraints.

### Execution Layer

Codex / workers execute only through governed transport and bounded runtime
authority. Execution does not bypass AGOL Bridge lifecycle, approval, replay, and
quarantine semantics.

### Observability Layer

Observability surfaces inspect lifecycle state, runtime responses, result
packages, and replay-visible evidence. Observability is read-only and does not
trigger execution.

### Replay Layer

Replay artifacts preserve deterministic historical references, append-only
records, content hashes, lifecycle transitions, certification evidence, and
audit continuity.

### Lifecycle Layer

Lifecycle artifacts constrain transitions between created, normalized, waiting,
approved, dispatched, executing, returned, validated, finalized, quarantined,
and failed states.

## Confirmed Constitutional Separation

- ChatGPT / LLMs = semantic cognition
- AiGOL / AGOL = semantic direction governance
- Codex / workers = execution through governed transport only

## Canonical Terms

- `SAPIANTA constitutional governance substrate`
- `AGOL governed operational layer`
- `AiGOL semantic direction governance`
- `Browser Companion`
- `Governed Browser Sidepanel Runtime`
- `AGOL Bridge`
- `governed transport`
- `replay-safe reference`
- `append-only replay log`
- `migration manifest`
- `replay-safe alias mapping`
- `lifecycle transition`
- `approval-gated dispatch`
- `quarantine`
- `fail-closed`
- `read-only observability`
- `bounded continuity`

## Deprecated Terms

The following terms are deprecated for future architectural claims:

- `full autonomous semantic runtime`
- `autonomous semantic operating system`
- `semantic autonomy engine`
- `worker mesh`
- `unrestricted autonomous AI`
- `self-evolving governance`
- `hidden orchestration`
- `automatic execution authority`
- `ChatGPT execution authority`
- `silent artifact rename`

## Alias Terms

The following aliases remain historically valid:

- `AIGOL` -> `AiGOL`
- `AGOL Bridge Runtime v0.1` -> `AGOL Bridge Runtime Foundation v1`
- `Browser Companion sidepanel` -> `Governed Browser Sidepanel Runtime`
- `SAPIANTA Companion` -> `Browser Companion`
- `ADR-00X-AGOL-BRIDGE-PIVOT` -> pending stable numeric ADR alias
- `ADR-00X-SEMANTIC-DIRECTION-GOVERNANCE` -> pending stable numeric ADR alias

## Ambiguities Remaining

1. Stable numeric ADR ids are still pending for top-level governance ADRs.
2. Historical references still include AGOL, AiGOL, and AIGOL variants.
3. AGOL Bridge Transport Spec v1 remains a Draft Foundation Spec until a
   canonical promotion milestone is completed.
4. Existing evidence contains transitional sidepanel naming that should remain
   historically valid.

## Recommended Next Step

Create an append-only alias registry and ADR numbering manifest. The manifest
should assign stable numeric ids to placeholder ADRs, preserve historical
filenames as aliases, and define whether AGOL Bridge Transport Spec v1 is
promoted to canonical status or superseded by a corrected version.
