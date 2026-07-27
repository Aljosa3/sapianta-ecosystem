# Generation 32-10B-R01 Repository Regression Runtime Investigation

Status: completed `AUDIT_ONLY` static investigation.

Date: 2026-07-27

Audited constitutional baseline:

- Platform Core Baseline V31;
- Certified Filesystem Adapter Executable Constitutional Contract V1;
- Immutable Constitutional Evidence Manifest V1;
- Automatic Constitutional Validator Kernel V1;
- G32-10B Validator Constitutional Conformance Audit.

Deterministic determination:

`REPOSITORY_REGRESSION_RUNTIME_IS_INEFFICIENT_BUT_CORRECT_EXTERNAL_DUPLICATE_EXECUTION_NOT_VALIDATOR_KERNEL_DRIFT`

No runtime, test, Validator, Replay, Governance, Certification, Provider,
Worker, contract, manifest, configuration, or constitutional artifact was
modified. This document is a static audit record; it does not authorize any
performance change.

## Executive determination

The reported greater-than-one-hour execution is most probably caused by five
independent, overlapping repository regressions executing the same large,
CPU-bound integration suite concurrently. It is not plausibly caused by the
Automatic Constitutional Validator Kernel.

The root `pytest.ini` contains no parallelism setting or launcher. It defines
only two root collection paths, `tests` and `sapianta-domain-credit/tests`.
Static search found no repository code that launches `pytest`; occurrences of
pytest commands in tests are validation metadata or asserted command vectors.
The three reported `python -m pytest -q` processes are consequently separate
external invocations, not child processes started by the Validator or pytest
configuration. The two explicit large subsets add further overlapping work.

Near-100% CPU with continually increasing CPU time is consistent with active
CPU-bound Python work and contention among independent runs; it is not the
signature of a deadlock. A shared progress log can make that contention appear
as stalled output because five processes interleave writes and each must
independently reach the same later, slower tests.

## Runtime execution reconstruction

```text
external validation orchestration
  ├─ pytest -q #1 ─┐
  ├─ pytest -q #2 ─┼─ independent collection of the same root test paths
  ├─ pytest -q #3 ─┤  (no pytest-level deduplication or shared result cache)
  ├─ explicit subset #1 ── overlaps root collection tests
  └─ explicit subset #2 ── overlaps root collection tests
                         │
                         └─ repeated end-to-end, replay reconstruction,
                            serialization/hash, filesystem and subprocess tests
                            on shared CPU and a shared visible progress log
```

The root suite statically contains 1,058 test files and 6,268 declared test
functions; prior collection evidence for the current tree is 6,900 pytest
nodes after parametrization. Running three complete suites already performs
at least three complete discoveries and three complete executions. Any subset
that overlaps a root-suite node performs that node again. Pytest does not
coordinate independent processes or deduplicate their work.

## Validator execution dependency graph

```text
explicit invocation-scoped trust anchors
  └─ authenticated ECC load and schema/hash validation
       └─ one deterministic topological schedule
            ├─ authenticated ICEM load and contract binding validation
            │    └─ one pass over declared evidence, wrappers, Replay refs,
            │       and lineage commitments
            └─ one pass over scheduled requirements
                 └─ one rule evaluation per dependency-satisfied requirement
                      └─ immutable PASS/FAIL result and canonical result hash
```

There is no path from the Validator to pytest, subprocess execution, a test
runner, provider invocation, Worker execution, Replay persistence, Governance,
or Certification. The kernel imports only local validation modules and Python
standard-library facilities for JSON, hashing, dataclasses, and heap ordering.

The certified invocation has 33 requirements and 10 evidence records. The
kernel-focused test module has 14 test nodes. These bounded quantities cannot
account for a repository-wide multi-hour CPU load with five concurrent
processes.

## Complexity assessment

| Subsystem | Static complexity | Assessment |
| --- | --- | --- |
| Scheduler | `O(R + D + Σ d(v) log d(v) + R log R)` for `R` requirements and `D` dependency edges. Each requirement is scheduled once and each edge removed once. | No duplicate scheduling, graph expansion, or exponential behavior. |
| Contract loading | Linear in contract structure, plus canonical sort/serialization cost for hash verification. | One authenticated contract load per validator invocation. |
| Canonical hashing | `O(S)` traversal and encoding for scalar/array structure; object-key ordering adds `O(k log k)` per object with `k` keys. | Correct bounded integrity work. A mapping source is canonicalized and parsed before hash verification, so a supplied in-memory artifact can be serialized more than once; this is a future micro-optimization candidate, not a defect. |
| Rule evaluation | `ALL` visits each child at most once and short-circuits on failure; `EXISTS` and references follow a pointer once; `EQUALS` visits compared JSON values once; `SUBSET_OF` canonicalizes each array element and uses a set. | No quadratic matching or repeated rule loading. Rule nesting is limited to 64. |
| Evidence manifest | One manifest load; one pass over records; one reference-index map; one later pass over declared lineage commitments. Each declared artifact, wrapper, and Replay reference is resolved only at its declared validation point. | Linear in manifest/evidence/lineage size, with canonical-hash cost per authenticated artifact. No repeated contract resolution or recursive expansion. |
| Requirement evaluation | One ordered pass. Dependency status is a dictionary lookup; an unsatisfied dependency prevents that rule from being evaluated. | No accidental re-evaluation. |
| Repository regression | `O(P × T)` for `P` independently launched process suites and `T` work per suite, plus overlap from explicit subsets. Individual end-to-end tests add replay serialization, filesystem and subprocess work. | Dominant observed cost. With the reported five invocations, redundant work is inherent. |

No `O(n²)`, `O(n³)`, exponential, recursive-amplification, or repeated graph
traversal defect was found in the Validator path. The only intentional
recursion is bounded rule validation/evaluation.

## Dominant hotspot identification

**Primary hotspot: duplicated whole-repository execution, multiplied by
integration-heavy tests.**

The test tree statically includes 59 calls to `aicli.run_reference_uhi_session`,
1,070 replay-reconstruction calls, and subprocess usage in 34 test files.
These operations construct and verify full governance/replay chains, serialize
and hash artifacts, traverse test workspaces, and sometimes create bounded
child processes. For example, the G31 worker-dispatch test invokes the full
reference UHI session for its success, seven substitution, five nested
substitution, duplicate, and boundary cases; each invocation performs a
complete governed lifecycle before exercising a stage-local assertion.

This architecture is correct and intentionally evidence-rich, but expensive
when repeatedly executed. The single explicit fixed sleep test cannot explain
the observation: it contains only a two-second timeout scenario and a
ten-second post-marker scenario that is configured with a one-second timeout;
sleeping would also not explain sustained near-100% CPU.

The exact test node at the reported 40% point cannot be proven from static
sources alone because the process command lines, collection order, duration
output, and complete shared log were not supplied. A dynamic duration profile
would be required to name that node. This limitation does not change the
root-cause classification: the external duplication alone guarantees redundant
full-suite work.

## Classification

| Question | Determination |
| --- | --- |
| Is multiple full-suite execution expected from repository configuration? | No. The repository defines collection topology, not a multi-process pytest launcher. |
| Is repeated repository-wide validation occurring? | Yes, as a direct consequence of the reported three independent root invocations; explicit subsets may overlap them. |
| Is the behavior correct? | The individual test executions remain semantically correct. |
| Is the behavior efficient? | No. It is externally duplicated and CPU-contentious. |
| Is it architecturally suspicious? | The external execution plan is operationally suspicious; the Validator architecture is not. |
| Is a Validator defect likely? | No. Static structure and bounded input cardinality rule it out as the dominant source. |
| Is a deadlock evidenced? | No. Continued CPU accrual and progress are inconsistent with that conclusion. |

## Constitutional impact assessment

There is no constitutional drift. The Validator remains a bounded,
deterministic, read-only evaluation capability under invocation-scoped Platform
Core trust anchors. It introduces no parallel trust model and does not execute
tests, mutate evidence, persist Replay, assess Governance, certify,
authorize, assign, dispatch, invoke, or execute.

The bottleneck is outside constitutional decision authority: it is redundant
validation orchestration. Any future performance work must preserve isolated
test evidence, fail-closed behavior, replay integrity, deterministic output,
and the existing external ownership of Governance and Certification.

## Recommendations (not implemented)

### Immediate correctness and operational integrity

- Do not treat the five concurrent outputs as five independent confirmations;
  they overlap and do not add independent coverage.
- Stop or allow completion of redundant runs only under the operator's existing
  process-control authority. Preserve their logs as operational evidence.
- Before relying on a regression result, record one exact command, process
  identity, start/end time, exit code, collected-node count, and immutable log
  reference. This is an evidence-discipline recommendation, not a request to
  change the Validator.

### Future performance improvements

- Run one root regression at a time; run a focused subset only when it is
  disjoint from that root regression or replaces it by declared policy.
- On a separate authorized performance-investigation task, collect pytest
  duration data to identify the exact late-suite nodes rather than infer them
  from progress percentages.
- Consider marking or grouping expensive end-to-end/replay lifecycle tests so
  a focused change can select the affected validation layer without losing
  release-level full regression coverage.
- Consider cache-free, immutable per-invocation canonicalization reuse only if
  a later benchmark demonstrates that hashing dominates. Any such change must
  retain byte-identical canonical hashes and fail-closed semantics.

### Deferred architectural enhancements

- Define a governed validation-orchestration record that prevents accidental
  duplicate root-suite launches while retaining human authority to request an
  intentional independent rerun.
- Define a replay-safe shard manifest only if parallel validation is later
  authorized. It must declare mutually exclusive test-node ranges, immutable
  per-shard logs, deterministic aggregation, and no shared mutable runtime
  target.

No recommendation is an immediate code correction. No optimization,
concurrency mechanism, cache, test change, or runtime modification is
authorized by this audit.

## Validation performed

Only read-only static inspection was performed:

- pytest configuration and collection topology;
- repository search for pytest launchers and Validator references;
- Validator source dependency, scheduler, loader, canonicalization, and rule
  evaluator inspection;
- static test-tree counts and inspection of representative integration tests.

No pytest execution, profiling, benchmark, patch, configuration change, or
commit was performed for this investigation.
