# Constitutional Evidence Reporting Standard V1

Status: CANONICAL IMPLEMENTATION REPORTING STANDARD

Version: V1

Generation: G48-00

Authority: Development Governance

Constitutional position: L3 governed reporting artifact

Compatibility baseline: G0-G47

## A. Purpose and Scope

This standard defines the mandatory evidence-reporting form for every future
major SAPIANTA implementation generation. It standardizes how implementation
claims are connected to code evidence, validation evidence, repository
mutations, and one explicit certification verdict.

This standard is a reporting requirement. It does not:

- create runtime behavior;
- certify an implementation by itself;
- replace the Constitution, Governance, Human Authority, Authorization,
  Replay, validation owners, or Certification;
- alter any implementation contract;
- authorize repository mutation; or
- convert an unverified claim into constitutional evidence.

The terms `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`,
`SHOULD NOT`, and `MAY` are normative. Descriptive text marked
**Informational** does not create a requirement.

## B. Normative Reporting Rules

### B.1 Exact top-level structure

An implementation report MUST contain exactly these six top-level sections,
in this order and with these titles:

1. `Implementation Summary`
2. `Code Evidence`
3. `Constitutional Self-Assessment`
4. `Validation Matrix`
5. `Repository Mutation Summary`
6. `Certification Verdict`

No appendix, evidence annex, notes section, or other top-level report section
is permitted. Supporting detail MAY appear as subsections inside the
applicable mandatory section.

Report identity, generation, baseline, implementation-contract references,
and reporting date MUST be recorded inside Section 1. They MUST NOT be used to
create an additional report section.

### B.2 Evidence discipline

Every material implementation claim MUST be:

- demonstrated by a code excerpt, immutable artifact, or exact repository
  reference;
- connected to a validation activity or explicitly marked `NOT_VERIFIED`;
- represented in the Validation Matrix; and
- reflected in the final verdict.

Representative excerpts MUST reproduce implementation text exactly. An
excerpt MAY omit unrelated lines when the omission is declared immediately
before or after the excerpt. An excerpt SHOULD remain below approximately 100
lines. Line references alone MAY supplement an excerpt but MUST NOT replace
all code evidence for a runtime implementation.

Assertions based only on intent, architecture prose, or a successful command
exit are not sufficient evidence for an unexercised constitutional
requirement.

### B.3 Validation result vocabulary

The Validation Matrix MUST use one of these result labels:

- `PASS`: the stated validation completed and demonstrated the requirement;
- `FAIL`: the validation completed and disproved the requirement;
- `PARTIAL`: only a declared subset of the requirement was demonstrated;
- `NOT_RUN`: the required or relevant validation was not executed;
- `BLOCKED`: the validation could not complete because of a declared blocker;
- `NOT_APPLICABLE`: the requirement does not apply, with justification.

`PARTIAL`, `NOT_RUN`, and `BLOCKED` MUST also appear under `Not Verified` in
Section 3 when they leave a constitutional requirement undemonstrated.

### B.4 Certification discipline

Section 6 MUST contain exactly one verdict token selected from the verdicts
authorized by the governing generation or certification contract.

The verdict MUST be the final substantive content of the report. A certifying
verdict MUST NOT be returned when a mandatory acceptance criterion is
`FAIL`, `NOT_RUN`, or `BLOCKED`. A `PARTIAL` result permits certification only
when the governing contract explicitly permits partial verification and the
remaining limitation is declared under `Not Verified`.

When no certifying verdict is justified, the report MUST use the applicable
blocked, incomplete, requires-repair, or requires-revision verdict. Reporting
must fail closed rather than inventing a verdict.

## C. Mandatory Section Responsibilities

| Section | Required contents | Explicit non-responsibility |
|---|---|---|
| 1. Implementation Summary | Objective, bounded scope, implementation-contract and baseline references, modified modules, intentionally unchanged modules, preserved boundaries | Does not prove implementation correctness |
| 2. Code Evidence | Public API, orchestration entry point, semantic reductions, public validators, canonical data models, deterministic algorithms, and responsibility boundaries | Does not replace execution or validation evidence |
| 3. Constitutional Self-Assessment | Separate `Verified` and `Not Verified` lists; exercised invariants, contracts, fail-closed paths, and every missing demonstration | Does not silently infer untested conformance |
| 4. Validation Matrix | One row for every constitutional requirement, with Requirement, Evidence, Validation, and Result | Does not omit requirements because validation was unavailable |
| 5. Repository Mutation Summary | Modified files, unchanged subsystems, API compatibility, boundary preservation, and unrelated pre-existing changes when present | Does not claim ownership of unrelated changes |
| 6. Certification Verdict | Exactly one authorized verdict consistent with Sections 3 and 4 | Does not grant authority beyond the governing certification contract |

If any required input for a section is unavailable, the report MUST preserve
the section, state the missing input, classify affected requirements as
`NOT_VERIFIED`, and fail closed in Section 6 where certification depends on
that input.

## D. Mandatory Report Format

The following is the reusable canonical template. Text in angle brackets is a
required substitution. Optional detail must remain nested inside one of these
six sections.

```markdown
# 1. Implementation Summary

Generation: <generation>

Report identity: <stable report identity>

Constitutional baseline: <baseline>

Implementation contracts: <authoritative contracts>

Objective:

<objective>

Implementation scope:

- <implemented responsibility>

Modified modules:

- <path and responsibility>

Intentionally unchanged modules:

- <subsystem and reason>

Architectural boundaries preserved:

- <boundary and evidence reference>

# 2. Code Evidence

## Public API

<exact representative excerpt and repository reference>

## Orchestration Entry Point

<exact representative excerpt and repository reference>

## Semantic Reductions

<exact representative excerpt and repository reference>

## Public Validators

<exact representative excerpt and repository reference>

## Canonical Data Models

<exact representative excerpt and repository reference>

## Deterministic Algorithms

<exact representative excerpt and repository reference>

## Responsibility Boundaries

<exact representative excerpt or authoritative boundary evidence>

# 3. Constitutional Self-Assessment

## Verified

- <requirement, contract, invariant, or fail-closed behavior demonstrated>

## Not Verified

- <requirement not demonstrated and why>

If no item remains unverified, state:

- None identified within the authorized scope and executed validation.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| <constitutional requirement> | <code/artifact/reference> | <command or deterministic review> | <PASS/FAIL/PARTIAL/NOT_RUN/BLOCKED/NOT_APPLICABLE> |

# 5. Repository Mutation Summary

Modified files:

- <path and bounded change>

Unchanged subsystems:

- <subsystem>

API compatibility:

- <compatibility result and evidence>

Boundary preservation:

- <boundary result and evidence>

Unrelated pre-existing changes:

- <path, or "None observed">

# 6. Certification Verdict

<EXACTLY_ONE_AUTHORIZED_VERDICT_TOKEN>
```

This format is mandatory for future major implementation reports. A
generation MAY add more detailed subsections only under the six required
sections. It MUST NOT rename, reorder, merge, or add top-level sections.

## E. Completed Example: G47-01C-R02

The following completed report applies the mandatory format to the
G47-01C-R02 localized repair. It records the actual code and validation
limitations and does not reinterpret the historical verdict.

````markdown
# 1. Implementation Summary

Generation: G47-01C-R02

Report identity: G47_01C_R02_CONSTITUTIONAL_REPAIR_REPORT_V1

Constitutional baseline: G47-01A, G47-01B, G47-01C, and the authoritative
G47-01C-R01 review

Implementation contracts: G47-00B Final Canonical Implementation Contract and
G47-01C-R02 Validator Context and Evidence Authority repair authorization

Objective:

Remove the proven context-free semantic-validator bypasses, require
authoritative evidence context, detect overlapping contradictory claims from
one authoritative owner, and correct stale runtime documentation.

Implementation scope:

- mandatory upstream context for Need Assessment, Governance disposition, and
  planning-eligibility public validation;
- exact supported evidence-type enforcement;
- authoritative owner, architectural owner, certification scope,
  compatibility scope, supersession scope, source reference, and source hash
  validation;
- overlap-aware authority conflict rejection; and
- documentation alignment.

Modified modules:

- `aigol/runtime/constitutional_development_governance_orchestration.py`:
  localized constitutional validator and evidence-authority repair.

Intentionally unchanged modules:

- Planner, Replay, Approval, Authorization, PCBV31, AiCLI, Workers, Providers,
  serialization, hashing, reconstruction, bundle layout, and public API.

Architectural boundaries preserved:

- the runtime validates but does not plan, approve, authorize, execute, or
  persist Replay;
- bundle serialization, hashing, reconstruction, and layout were unchanged;
- the repair changed one runtime module only.

# 2. Code Evidence

## Public API and Orchestration Entry Point

Repository reference:
`aigol/runtime/constitutional_development_governance_orchestration.py`.

```python
def orchestrate_constitutional_development_governance(
    *,
    bundle_id: str,
    task_intake: DevelopmentGovernanceTaskIntake,
    cdd_classification: DevelopmentGovernanceCDDClassification,
    evidence_snapshot: DevelopmentGovernanceEvidenceSnapshot,
    need_assessment: DevelopmentGovernanceNeedAssessment,
    governance_disposition: DevelopmentGovernanceDisposition,
    planning_eligibility: DevelopmentGovernancePlanningEligibility,
) -> ConstitutionalDevelopmentGovernanceBundle:
```

The constitutionally relevant validation sequence is:

```python
    evidence = validate_development_governance_evidence_snapshot(
        evidence_snapshot,
        expected_cdd_id=cdd.cdd_id,
        expected_baseline=cdd.baseline_reference,
    )
    need = validate_need_assessment(
        need_assessment,
        task_intake=intake,
        cdd_classification=cdd,
        evidence_snapshot=evidence,
    )
    disposition = validate_development_governance_disposition(
        governance_disposition,
        task_intake=intake,
        cdd_classification=cdd,
        evidence_snapshot=evidence,
        need_assessment=need,
    )
    eligibility = validate_planning_eligibility(
        planning_eligibility,
        need_assessment=need,
        governance_disposition=disposition,
    )
```

## Semantic Reductions and Public Validators

Need Assessment fails closed without its complete upstream context:

```python
    if (
        task_intake is None
        or cdd_classification is None
        or evidence_snapshot is None
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Need Assessment semantic validation requires complete context"
        )
```

Governance disposition fails closed without its complete upstream context:

```python
    if (
        task_intake is None
        or cdd_classification is None
        or evidence_snapshot is None
        or need_assessment is None
    ):
        raise DevelopmentGovernanceRuntimeError(
            "Governance disposition validation requires complete context"
        )
```

Planning eligibility fails closed without both upstream reductions:

```python
    if need_assessment is None or governance_disposition is None:
        raise DevelopmentGovernanceRuntimeError(
            "planning eligibility validation requires complete context"
        )
    expected_eligible = (
        governance_disposition.governance_disposition
        == "BOUNDED_PLANNING_PERMITTED"
    )
```

## Canonical Data Models

The bundle remains immutable and reference-only:

```python
@dataclass(frozen=True, slots=True)
class ConstitutionalDevelopmentGovernanceBundle:
    """Immutable canonical bundle containing ordered references and hashes."""

    artifact_type: str
    runtime_version: str
    bundle_id: str
    bundle_identity: str
    baseline_reference: str
    stage_order: tuple[str, ...]
    stage_references: tuple[DevelopmentGovernanceStageReference, ...]
    bundle_hash: str
```

## Deterministic Algorithms

The supported evidence-type contract is exact rather than regex-based:

```python
SUPPORTED_EVIDENCE_VERSION = "V1"
_SUPPORTED_EVIDENCE_TYPE_CONTRACTS = {
    "DEVELOPMENT_GOVERNANCE_EVIDENCE_V1": {
        "artifact_version": SUPPORTED_EVIDENCE_VERSION,
        "authority_registry_version": (
            PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
        ),
        "source_reference_binding": "CERTIFICATION_EVIDENCE",
        "content_hash_binding": "AUTHORITATIVE_SOURCE_BYTES",
        "compatibility_scope_binding": "CDD_BASELINE",
        "supersession_binding": "CERTIFICATION_RECORD",
    },
}
```

Overlapping contradictory claims from the same authoritative owner fail
closed:

```python
def _register_authoritative_claim(
    claims_by_authority: dict[
        tuple[str, str, str],
        list[DevelopmentGovernanceEvidenceReference],
    ],
    artifact: DevelopmentGovernanceEvidenceReference,
) -> None:
    authority_key = (
        artifact.subject_id,
        artifact.claim_type,
        artifact.canonical_owner,
    )
    prior_claims = claims_by_authority.setdefault(authority_key, [])
    for prior in prior_claims:
        if (
            prior.claim_value != artifact.claim_value
            and _authoritative_claim_scopes_overlap(prior, artifact)
        ):
            raise DevelopmentGovernanceRuntimeError(
                "one authoritative owner supplied overlapping conflicting evidence"
            )
    prior_claims.append(artifact)
```

## Responsibility Boundaries

The module contract states:

```python
"""Constitutional Development Governance runtime through G47-01C-R02.

This module realizes the immutable runtime structure, canonical stage order,
and deterministic constitutional semantics frozen by the G47-00B
implementation contract.  It validates evidence, evaluates Need Assessment
predicates without priority, reduces Governance disposition, and validates
planning eligibility.  It canonically serializes, hashes, validates, and
reconstructs the reference-only Governance bundle.  It does not integrate a
planner, persist Replay, or reconstruct a Replay protocol.
```

The excerpt ends before the closing module documentation delimiter; no
implementation text inside the excerpt was altered.

# 3. Constitutional Self-Assessment

## Verified

- all three public semantic validators reject absent mandatory upstream
  context;
- evidence artifact types are accepted only through the exact V1 contract;
- evidence ownership and scope are checked against the authoritative platform
  capability certification registry;
- the authoritative source reference must exist and its SHA-256 must match;
- contradictory authoritative claims with overlapping or unbounded scopes
  fail closed;
- the public function signatures and bundle layout remain compatible;
- Planner, Replay, Approval, Authorization, PCBV31, AiCLI, Worker, Provider,
  serialization, hashing, and reconstruction responsibilities remain outside
  the repair;
- focused registry and governance-conformance tests passed; and
- Python compilation and `git diff --check` passed.

## Not Verified

- full repository regression was not completed: it was interrupted at
  approximately 40 percent after no failures had appeared because the
  remaining G31 cases were long-running;
- repository-wide governance conformance was not demonstrated as fully
  conformant: the conformance engine remained `PARTIALLY_CONFORMANT` with zero
  critical violations and two already-visible hook-drift findings; and
- the focused validation used existing suites and deterministic probes; no new
  test module was added.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Public semantic validators require complete context | Context guards in `validate_need_assessment`, `validate_development_governance_disposition`, and `validate_planning_eligibility` | Focused negative probes for absent context | PASS |
| Evidence types use an exact supported contract | `_SUPPORTED_EVIDENCE_TYPE_CONTRACTS` and `_validate_evidence_reference` | Supported and unsupported artifact-type probes | PASS |
| Evidence context is authoritative | `_validate_authoritative_evidence_context` registry, scope, source, and hash checks | Positive authoritative fixture and negative mismatch probes | PASS |
| Overlapping contradictory authority fails closed | `_register_authoritative_claim` and `_authoritative_claim_scopes_overlap` | Overlapping and disjoint claim probes | PASS |
| Runtime documentation identifies the completed R02 boundary | Module documentation names G47-01C-R02 and its implemented and deferred responsibilities | Static documentation review | PASS |
| Public API and bundle layout remain unchanged | Existing public signatures and frozen bundle dataclass | Static API comparison and focused compatibility tests | PASS |
| Forbidden subsystem boundaries remain unchanged | One-file commit mutation inventory | `git show --stat` and architectural diff review | PASS |
| Focused constitutional compatibility | Registry and governance conformance test selection | 11 focused tests | PASS |
| Python source compiles | Repaired runtime module | Python compilation | PASS |
| Patch is whitespace-clean | Repository diff | `git diff --check` | PASS |
| Full repository regression | Repository test suite | Interrupted near 40 percent with no observed failures | NOT_RUN |
| Full governance conformance | Governance conformance report | Zero critical violations; two known hook-drift findings | PARTIAL |

# 5. Repository Mutation Summary

Modified files:

- `aigol/runtime/constitutional_development_governance_orchestration.py`:
  149 insertions and 40 deletions in the localized R02 repair commit.

Unchanged subsystems:

- Planner;
- Replay;
- Approval;
- Authorization;
- PCBV31;
- AiCLI;
- Worker;
- Provider;
- serialization;
- hashing;
- reconstruction; and
- bundle layout.

API compatibility:

- public runtime signatures were preserved;
- mandatory context parameters retained their existing optional-call shape but
  now fail closed when omitted, as authorized by R02.

Boundary preservation:

- validation gained no planning, approval, authorization, execution, or Replay
  ownership;
- the canonical bundle remained immutable and reference-only.

Unrelated pre-existing changes:

- None observed in the R02 commit.

# 6. Certification Verdict

G47_01C_CONSTITUTIONALLY_CERTIFIED
````

## F. Cross-Reference and Authority Boundaries

This standard MUST be applied together with, and does not replace:

| Authority or artifact | Relationship to this standard |
|---|---|
| Constitution and Stable Constitutional Substrate | Define higher-order meaning and immutable boundaries |
| `CONSTITUTIONAL_DEVELOPMENT_POLICY_V1.md` | Governs classification, necessity, planning, approval, authorization, implementation, validation, evidence, and certification ordering |
| Applicable generation contract | Defines the authorized scope, acceptance criteria, required validation, and permitted verdict tokens |
| Replay policies | Govern constitutional recording and reconstruction; a report only references their evidence |
| Authorization contracts | Govern mutation or execution authority; a report cannot authorize either |
| Validation policies and owners | Define validation semantics; a report records outcomes without replacing them |
| Certification policies and owners | Determine certification authority; a report exposes the resulting verdict |

## G. Repository and Governance Impact

Adoption requires this single governance documentation artifact.

No changes are required to:

- the Constitution;
- the Stable Constitutional Substrate;
- constitutional protocol families;
- PCBV31;
- Planner;
- Replay;
- Governance authority;
- Authorization;
- AiCLI;
- Workers;
- Providers; or
- runtime behavior.

The standard formalizes evidence disclosure for future implementation reports.
It does not change the meaning or certification state of G47-01C-R02 or any
other historical generation.

Implementation readiness is complete when this document is present,
structurally verified, and repository formatting validation passes.
