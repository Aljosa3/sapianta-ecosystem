# AIGOL Runtime Evidence Retention Policy V1

Status: runtime evidence retention policy.

Purpose: determine which AiGOL runtime evidence artifacts should be committed to git, retained outside git, or excluded as transient execution traces.

This artifact is policy guidance only.

It does not redesign replay.

It does not redesign certification.

It does not change runtime behavior.

It does not weaken audit requirements.

It does not authorize deletion of existing evidence.

It does not silently reclassify unresolved evidence as certified.

## Decision Question

Runtime evidence artifacts may include:

- replay evidence;
- certification evidence;
- runtime traces;
- worker execution outputs;
- provider diagnostics;
- audit packages;
- ledger files;
- temporary workspaces;
- local execution byproducts.

The policy question is whether these artifacts should be:

```text
1. committed to git
2. partially committed
3. excluded from git
```

## Current Repository Signals

Current `.gitignore` already excludes operational runtime artifacts:

```text
.runtime/aigol/evidence/
.runtime/aigol/ledger/
```

The repository also contains governance artifacts under:

```text
docs/governance/
```

and many runtime-generated evidence roots under:

```text
runtime/*_evidence
runtime/acli_*
runtime/worker_execution_evidence
```

Interpretation:

The repository already distinguishes between:

- durable governance artifacts;
- operational runtime evidence;
- transient local execution output.

This policy formalizes that distinction.

## Evidence Classes

### Class A: Governance Certification Artifacts

Examples:

```text
docs/governance/AIGOL_*_V1.md
docs/product_lifecycle/*_V1.md
```

Retention policy:

```text
COMMIT
```

Rationale:

- small;
- human-readable;
- governance-native;
- durable;
- suitable for review;
- captures final verdicts, criteria, and known limitations.

### Class B: Certification Summary Packages

Examples:

```text
certification_report.json
evidence_package.json
scorecard.json
delta_analysis.json
campaign_manifest.json
```

Retention policy:

```text
COMMIT SELECTIVELY
```

Commit only when the package is:

- deterministic;
- compact;
- scrubbed of secrets;
- explicitly referenced by a governance artifact;
- necessary to substantiate a certification claim;
- stable enough to survive clone/review without local runtime dependencies.

Do not commit if the file contains:

- absolute local paths that are not needed for replay review;
- provider stdout with environment-specific binaries;
- secrets, credentials, tokens, or user-sensitive data;
- large raw transcripts;
- redundant per-step runtime traces already summarized elsewhere.

### Class C: Replay Step Evidence

Examples:

```text
000_*_recorded.json
001_*_returned.json
worker replay steps
authorization replay steps
ERR selection replay steps
```

Retention policy:

```text
PARTIAL RETENTION
```

Commit replay step evidence only for:

- canonical certification baselines;
- release-candidate evidence packs;
- externally reviewable audit snapshots;
- regression fixtures intentionally used by tests;
- legally or contractually required audit evidence.

Otherwise retain outside git.

Rationale:

Replay step evidence is valuable, but committing every step from every local empirical run causes:

- repository growth;
- noisy diffs;
- environment-specific churn;
- accidental retention of sensitive prompt material;
- confusion between certified baselines and exploratory traces.

### Class D: Runtime Traces

Examples:

```text
session_runtime/
turn_completion/
runtime_progress/
source_router/
multiline_prompt_capture/
operator output logs
provider stdout/stderr
```

Retention policy:

```text
EXTERNAL OR IGNORED
```

Runtime traces should not be committed by default.

They may be archived externally if they support a certification package.

### Class E: Worker Output Artifacts

Examples:

```text
workspace/user_session_proof.txt
workspace/worker_execution_evidence.txt
generated proof files
temporary mutation outputs
```

Retention policy:

```text
EXTERNAL OR FIXTURE-ONLY
```

Commit only if the output is an intentionally curated fixture or a tiny canonical proof artifact required by a governance baseline.

Otherwise keep outside git.

### Class F: Operational Ledgers

Examples:

```text
.runtime/aigol/ledger/governed_returns.jsonl
runtime operation ledgers
local execution counters
```

Retention policy:

```text
EXTERNAL RETENTION
```

Operational ledgers are append-heavy and environment-specific.

They should not be treated as source artifacts unless promoted into a curated release evidence snapshot.

### Class G: Secret-Bearing or Sensitive Evidence

Examples:

```text
credentials
API keys
tokens
provider raw payloads containing private content
customer data
personal data
commercially sensitive prompts
```

Retention policy:

```text
NEVER COMMIT
```

Sensitive evidence must be redacted, hashed, or externally retained under an access-controlled evidence store.

## Recommended Policy

Recommended verdict:

```text
PARTIAL_RETENTION
```

AiGOL should commit:

- governance artifacts;
- compact certification reports;
- compact evidence manifests;
- compact scorecards;
- delta analyses;
- intentionally curated regression fixtures.

AiGOL should not commit by default:

- full runtime traces;
- local session directories;
- raw provider stdout/stderr;
- operational ledgers;
- temporary workspaces;
- bulky replay trees;
- exploratory evidence runs;
- secret-bearing evidence.

## Retention Strategy

Use three retention tiers.

### Tier 1: Git-Retained Governance Evidence

Location:

```text
docs/governance/
.github/governance/evidence/
.github/governance/manifests/
tests/fixtures/ only when intentionally curated
```

Contents:

- policy artifacts;
- certification criteria;
- final verdicts;
- compact certification reports;
- stable regression fixtures.

Retention:

```text
long-term in git
```

### Tier 2: External Certification Evidence Archive

Location:

```text
external evidence store
release artifact bundle
object storage
artifact registry
signed archive
```

Contents:

- full replay packages;
- session runtime traces;
- raw certification runs;
- worker output artifacts;
- provider diagnostics after redaction;
- hash manifests tying archive contents to git-retained summaries.

Retention:

```text
long-term outside git
```

Required metadata:

```text
archive_id
created_at
source_commit
governing_artifact
certification_status
artifact_count
root_hash
redaction_status
retention_class
access_policy
```

### Tier 3: Local Transient Runtime Evidence

Location:

```text
runtime/
.runtime/
temporary workspaces
local operator runtime roots
```

Contents:

- local empirical runs;
- scratch evidence;
- failed packaging attempts;
- generated runtime traces;
- local ledgers.

Retention:

```text
short-term local retention
```

Disposition:

- keep while actively debugging;
- promote summaries to Tier 1 if certification-relevant;
- export full package to Tier 2 if audit-relevant;
- otherwise exclude from git and allow cleanup under an explicit cleanup procedure.

## Git Strategy

### Commit By Default

Commit:

```text
docs/governance/AIGOL_*_V1.md
docs/product_lifecycle/*_V1.md
compact certification summaries
curated scorecards
curated manifests
small deterministic test fixtures
```

### Do Not Commit By Default

Do not commit:

```text
runtime/acli_*/
runtime/*_evidence/
.runtime/aigol/evidence/
.runtime/aigol/ledger/
session_runtime/
workspace/
provider_stdout.txt
provider_stderr.txt
raw prompts with sensitive content
raw provider responses
```

### Promote Only Through Review

A runtime evidence file may be committed only if a reviewer confirms:

```text
evidence_is_required_for_certification = true
file_is_compact = true
file_is_deterministic = true
file_contains_no_secrets = true
file_contains_no_unnecessary_local_paths = true
file_is_referenced_by_governance_artifact = true
```

### Recommended Ignore Expansion

Current `.gitignore` already excludes `.runtime/aigol/evidence/` and `.runtime/aigol/ledger/`.

Recommended future ignore policy:

```text
runtime/acli_*/
runtime/*_evidence/
runtime/**/session_runtime/
runtime/**/workspace/
```

Exception:

Curated evidence fixtures may be placed in a dedicated governed path:

```text
docs/governance/evidence/
tests/fixtures/governance/
```

and committed intentionally.

## Archival Strategy

Archive full certification evidence outside git when:

- a certification verdict depends on it;
- an enterprise audit requires it;
- replay reconstruction must be reproducible later;
- the evidence is too large or noisy for git;
- raw traces contain environment-specific values.

External archive requirements:

```text
content-addressed storage
root hash
manifest hash
source git commit
governing artifact reference
certification report reference
redaction report
access control
retention period
destruction policy
```

Recommended archive package layout:

```text
archive_manifest.json
certification_report.json
evidence_package.json
replay_package.json
redaction_report.json
hash_manifest.json
session_runtime/
worker_replay/
authorization_replay/
err_replay/
result_artifacts/
```

Git-retained governance artifacts should reference:

```text
archive_id
root_hash
certification_status
minimal evidence summary
known limitations
```

## Audit Requirements

Auditability requires:

- stable governance summaries in git;
- deterministic replay hashes;
- clear evidence lineage;
- explicit known gaps;
- reproducible archive references;
- no hidden mutation;
- no secret retention in git.

Auditability does not require committing every runtime trace to source control.

For long-term enterprise review, a compact git summary plus externally retained full replay archive is stronger than an unbounded repository full of local runtime traces.

## Repository Growth Risk

Committing all runtime evidence would create:

- rapid repository growth;
- slow clones;
- noisy reviews;
- merge conflicts in append-only ledgers;
- accidental tracking of local machine paths;
- accidental tracking of provider version churn;
- accidental tracking of sensitive prompt data;
- blurred distinction between certified evidence and exploratory evidence.

This would reduce maintainability and increase governance risk.

## Maintainability Requirements

Runtime evidence must remain:

- classifiable;
- hashable;
- referencable;
- reconstructable;
- redaction-aware;
- promotion-controlled;
- separable from source code.

The source repository should remain the durable governance and implementation registry, not the default storage backend for every local runtime event.

## Decision Matrix

| Evidence Type | Git | External Archive | Local Only |
| --- | --- | --- | --- |
| Governance policy artifacts | Yes | Optional | No |
| Certification reports | Selective | Yes | Optional |
| Evidence packages | Selective | Yes | Optional |
| Replay packages | Selective summary only | Yes | Optional |
| Full session runtime traces | No by default | Yes if certification-relevant | Yes |
| Worker outputs | Fixture-only | Yes if certification-relevant | Yes |
| Provider stdout/stderr | No by default | Redacted only | Yes |
| Operational ledgers | No by default | Snapshot only | Yes |
| Secret-bearing artifacts | Never | Controlled redacted/hash only | Minimize |

## Final Policy

AiGOL should adopt:

```text
PARTIAL_RETENTION
```

This means:

```text
Commit governance artifacts and compact certification summaries.
Archive full replay/certification evidence externally when audit-relevant.
Keep raw runtime traces and local operational ledgers out of git by default.
Promote only curated, deterministic, non-sensitive evidence into git through explicit governance review.
```

## Final Verdict

```text
PARTIAL_RETENTION
```

Reason:

Committing all runtime evidence would harm repository maintainability and increase leakage/noise risk. Excluding all runtime evidence would weaken certification auditability. Partial retention preserves governance continuity while keeping full replay evidence available through controlled external archives.
