# Codex Task Execution Protocol V1

Status: canonical Codex task execution protocol.

Parent guidance: `AGENTS.md`

Purpose: define how Codex executes bounded work inside the SAPIANTA constitutional environment.

This protocol does not redesign governance, change runtime behavior, introduce autonomous mutation, introduce deployment automation, or create self-modifying governance. It formalizes task discipline, persistence rules, validation behavior, approval boundaries, and replay-safe lineage expectations.

## 1. Task Intake Semantics

Codex must interpret tasks through the constitutional repository model.

Task intake requires:

- identify the declared goal;
- identify the intended artifact class;
- identify whether the request is documentation, productization, governance evidence, runtime code, tests, or release work;
- identify the likely mutation layer;
- preserve known constitutional semantics;
- prefer bounded interpretation over expansive interpretation.

When task scope is ambiguous, Codex should:

- choose the smallest safe interpretation;
- avoid broad architecture edits;
- avoid runtime changes unless explicitly requested;
- ask for clarification when ambiguity affects governance, runtime, deployment, or irreversible behavior.

Codex must not infer permission to:

- redesign layers;
- change enforcement ordering;
- activate dormant governance;
- introduce execution capability;
- perform deployment;
- create unrestricted autonomy semantics.

## 2. Scope Isolation

Codex should modify only files relevant to the declared task scope.

Scope isolation requires:

- avoid unrelated refactors;
- avoid opportunistic cleanup outside the task;
- preserve user edits and existing dirty worktree changes;
- avoid changing runtime behavior from documentation tasks;
- avoid changing governance semantics from productization tasks;
- keep generated artifacts in the expected repository location.

Architecture drift prevention requires Codex to treat the following as high-sensitivity surfaces:

- `docs/governance/`
- `.github/governance/`
- `runtime/governance/`
- constitutional manifests and finalize evidence;
- product lifecycle governance documents;
- release discipline and demo runtime policy documents.

High-sensitivity does not mean unchangeable. It means changes must remain explicit, scoped, and aligned with constitutional meaning.

## 3. Write and Persistence Discipline

Repository artifacts are real only when persisted to the filesystem at the intended path.

Generated conversational output is not the same as a persisted repository artifact.

Codex must distinguish:

- generated text shown in conversation;
- temporary scratch output;
- persisted files in the repository;
- tracked or untracked git-visible repository artifacts;
- committed release lineage where a commit is explicitly requested.

Persistence expectations:

- create or modify files using repository-safe write operations;
- verify important deliverables exist after writing;
- use `git status` or direct path checks when persistence matters;
- avoid claiming a file exists unless it has been written;
- avoid claiming a repository state is finalized unless evidence files exist.

Governance lesson:

SAPIANTA treats persistence ambiguity as a governance risk. A prior persistence ambiguity showed that generated intent and repository reality can diverge. Therefore, final answers should distinguish what was written, what was validated, what remains uncommitted, and what limitations remain.

Replay-safe artifact expectations:

- deterministic documentation should avoid timestamps unless required;
- governance evidence should use stable identifiers where possible;
- generated manifests should be valid JSON where JSON is required;
- finalization artifacts should preserve known limitations instead of overwriting them.

## 4. Validation Discipline

Codex should prefer bounded deterministic validation.

Validation should match the touched surface:

- documentation-only changes: run `git diff --check`;
- governance conformance changes: run targeted conformance tests and conformance engine where applicable;
- JSON manifest changes: run `python -m json.tool` on generated JSON;
- runtime code changes: run targeted tests for the changed module;
- product UI changes: run the relevant local checks and visual/runtime verification when applicable.

Validation must preserve fail-closed reporting:

- failed validation must be reported;
- skipped validation must be reported;
- missing dependencies must be reported;
- known conformance gaps must remain visible;
- partial completion must not be presented as full completion.

Codex should not broaden validation into unrelated suites when a targeted deterministic check is sufficient, unless the task requires broader validation.

## 5. Approval Gates

Codex must require explicit human approval before:

- destructive operations;
- deleting files or directories;
- resetting, reverting, or force-changing git history;
- deployment actions;
- release-tag creation;
- large mutation scopes;
- modifying runtime behavior from an ambiguous task;
- changing constitutional semantics;
- changing enforcement ordering;
- introducing new execution capability;
- modifying broker/API/network execution surfaces;
- changing stable server runtime state.

Governance-sensitive changes require explicit scope confirmation when the request does not clearly authorize them.

Approval absence is not approval.

## 6. Governance Escalation

Codex should escalate rather than silently interpret when:

- constitutional meanings conflict;
- replay semantics are unclear;
- mutation scope crosses protected boundaries;
- task intent implies runtime behavior change but is not explicit;
- release or deployment consequences are possible;
- governance evidence is missing;
- conformance status would be hidden or weakened;
- Product 1 positioning could drift toward unrestricted autonomy or AGI framing.

Escalation may mean:

- ask the user a focused clarification question;
- document an unresolved limitation;
- mark the task partially complete;
- refuse to make a forbidden mutation;
- stop before destructive or deployment actions.

Escalation is a governance-preserving behavior, not a failure.

## 7. Commit Semantics

Codex should not commit unless the user asks for a commit.

When commits are requested, commit messages should preserve governance meaning continuity.

Commit semantics should identify:

- artifact class;
- milestone or protocol name;
- governance scope;
- validation performed;
- known limitations when relevant.

Governance-oriented commit examples:

- `docs(governance): add Codex task execution protocol v1`
- `governance: update conformance evidence for hook drift`
- `product: refine enterprise demo audit narrative`

Finalize commits should preserve:

- finalized scope;
- evidence references;
- conformance status;
- replay-safe lineage.

Stable substrate commits should avoid implying unrestricted finality. Stable means constitutionally bounded and replay-safe, not frozen forever.

## 8. Failure Semantics

Codex must favor explicit honesty over simulated completion.

When work cannot be completed, Codex should report:

- what was completed;
- what failed;
- what was not attempted;
- why validation failed or was skipped;
- which files were affected;
- known limitations;
- unresolved ambiguity;
- whether runtime behavior was changed.

Codex must not:

- hide failing tests;
- claim validation passed when it did not run;
- imply artifacts were persisted when they were only drafted;
- erase known conformance gaps;
- silently downgrade constitutional requirements.

## 9. Replay-Safe Task Lineage

Replay-safe task lineage is a governance requirement.

The canonical lineage model is:

task -> generation -> validation -> evidence -> commit -> tag -> release lineage

Not every task reaches every stage. The active stage must remain clear.

For ordinary Codex tasks:

- task: user request and scope;
- generation: files created or modified;
- validation: checks run and results;
- evidence: docs, manifests, reports, or test outputs;
- commit: only if user requests;
- tag: only if user requests and release discipline allows;
- release lineage: only through governed release flow.

Lineage continuity requires:

- preserve affected file paths;
- preserve validation status;
- preserve known gaps;
- avoid silent mutation of evidence;
- avoid undocumented release or deployment actions.

## 10. Governance-Native Self-Building Philosophy

SAPIANTA self-building is:

- bounded;
- governance-native;
- replay-aware;
- constitutionally constrained;
- lineage-preserving;
- enterprise-positioned.

The system must not drift toward:

- unrestricted autonomous mutation;
- recursive uncontrolled self-modification;
- governance bypass autonomy;
- self-modifying constitutional logic;
- unrestricted agent execution.

The goal is bounded constitutional evolution.

Codex may assist with evolution only when evolution preserves the constitutional substrate, replay guarantees, mutation boundaries, and release discipline.

## 11. Codex Behavioral Principles

Codex should:

- preserve constitutional framing;
- preserve governance semantics;
- preserve replay-safe terminology;
- preserve enterprise positioning;
- preserve deterministic semantics;
- preserve audit continuity;
- keep non-goals explicit;
- keep scope boundaries visible.

Codex should not:

- introduce hype framing;
- introduce AGI narratives;
- introduce singularity framing;
- introduce unrestricted autonomy semantics;
- silently reinterpret governance;
- hide known limitations;
- bypass release discipline;
- simulate completion.

## 12. Completion Checklist

Before final response, Codex should verify:

- requested artifacts exist;
- touched files are limited to task scope;
- required validation was run or skipped with explanation;
- JSON artifacts are valid when created;
- `git diff --check` passes for touched surfaces when feasible;
- no runtime behavior changed unless explicitly requested;
- known limitations are preserved;
- final response states what was done and what was validated.

## 13. Core Rule

Task execution must preserve the constitution before optimizing for speed, breadth, or convenience.

Codex-assisted development in SAPIANTA is not unrestricted autonomous execution.

It is governance-preserving bounded development with replay-safe task lineage.

