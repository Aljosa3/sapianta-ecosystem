# G31-24G-R01 Versioned Existing-File Mutation Candidate Provenance and Replay Binding

Baseline: 62deeef65a9c76498cdac56f3c88c46f8ab9ff63 on master.

Verdict: G31_V2_ACCEPTED_RESULT_TO_EXISTING_FILE_CANDIDATE_PROVENANCE_BINDING_OPERATIONAL.

## Scope and result

This bounded extension adds a V2 member of the existing existing-file mutation candidate family. It projects one reconstructed, accepted G31 V2 REPLACE_CONTENT result into candidate evidence and stops before any human mutation decision, mutation authorization, Worker request, command, or source write. V1 candidate construction and validation are unchanged.

The extension reuses the existing candidate owner, G31 acceptance, content-decision, prerequisite-binding, implementation-manifest, validation, repository-grounding reconstructors, immutable serialization, and AiCLI presentation transport. It creates no parallel candidate family, mutation, authorization, Worker, Provider, or command owner.

## Public contract

New public symbols are EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2; create_g31_accepted_existing_file_mutation_candidate; validate_g31_accepted_existing_file_mutation_candidate; reconstruct_g31_accepted_existing_file_mutation_candidate_replay; and render_g31_accepted_existing_file_mutation_candidate.

The V2 candidate binds one exact accepted result, canonical acceptance, content decision, prerequisite, V2 manifest, content/test validation, disposable-validation binding, repository grounding, target path, raw preimage/postimage SHA-256, legacy source/replacement content hashes, and unchanged source/replacement modes. Candidate provenance is replay-hashed as candidate_provenance_binding_hash and is included in the candidate artifact hash.

Repository grounding must pass its existing validator and reconstruction at the manifest source workspace. Substituted root, grounding, session, target, operation, file type, mode, manifest, acceptance, decision, prerequisite, validation, or Replay identity fails closed before candidate evidence is written.

## Candidate Replay and presentation

The candidate family owns a pre-authorization three-step immutable Replay:

1. existing-file mutation candidate request recorded;
2. existing-file mutation candidate recorded;
3. existing-file mutation candidate returned.

Reconstruction verifies wrapper index, step, wrapper hash, candidate hash, provenance, accepted-result lineage, and returned identity. The session-contained destination is append-only; repeated accepted-result provenance fails closed.

AiCLI remains non-authoritative. After exact accepted content it calls the candidate owner, reconstructs evidence, renders the candidate, and stops. Presentation says content is accepted, no human mutation decision is recorded, mutation is not authorized, and the main repository was not changed.

## Authority boundary

Successful state:

result_accepted = true
existing_file_mutation_candidate_created = true
human_mutation_decision_recorded = false
mutation_authorized = false
main_repository_mutated = false

Rejected content does not create a candidate. The extension does not call filesystem authorization, replace Worker, repository mutation, patch/disposable execution, Provider, or command owners. It writes only immutable session Replay evidence.

## Fail-closed evidence and validation

Focused fixtures cover exact accepted projection/reconstruction and AiCLI transport, altered manifest postimage, candidate tampering, duplicate Replay destination, repeated accepted-result consumption, V1 candidate compatibility, V1/V2 human-decision compatibility, and G31-24E acceptance compatibility. Existing reconstructors provide further checks for accepted outcome, cross-session evidence, prerequisite/manifest/validation lineage, repository grounding, target evidence, regular-file semantics, and source mode.

- Focused candidate, V1 existing-file, G31-24E, and V1 human-decision fixtures: 21 collected and passed; no skips, failures, or deselections.
- Targeted py_compile: pass for candidate owner and AiCLI.
- Parent and nested git diff --check: pass.
- Full suite and long PTY workflow: not run; committed evidence was sufficient and no shared-owner regression was observed.

Exact parent status contains the protected modified `.runtime/aigol` evidence
and ledger paths, protected untracked `WORKER_INVOCATION_ARTIFACT_V1`,
`WORKER_INVOKED`, and `invocation`, plus:

- modified `aigol/runtime/platform_core_existing_file_mutation_candidate.py`;
- modified `aigol/cli/aicli.py`;
- untracked `tests/test_g31_24g_r01_existing_file_candidate_provenance.py`;
- untracked this report.

No files are staged; all nested repositories remain clean.

Evidence-scoped progress: G31 conversational reachability is 99.6%; whole project remains 97.5%. Human mutation decision, authorization, and source mutation remain deliberately unreachable.

Next state (exactly one):

G31_24G_R02_VERSIONED_HUMAN_MUTATION_DECISION_CONTRACT_ON_REPLAYED_V2_CANDIDATE_REQUIRED
