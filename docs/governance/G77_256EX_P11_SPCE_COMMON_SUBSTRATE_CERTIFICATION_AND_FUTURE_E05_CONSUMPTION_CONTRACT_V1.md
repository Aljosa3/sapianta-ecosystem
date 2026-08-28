# G77-256EX P11/SPCE Common Substrate Certification and Future E05 Consumption Contract V1

Status: Human-authorized constitutional certification with explicit fresh operational and vector-specific exclusions.

Certification identity: `P11_SPCE_CERTIFIED_COMMON_SUBSTRATE_V1`

Certification version: `1.0.0`

Source manifest: `.github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json`

Source manifest outer SHA-256: `42744ccb19767a9f90ed909f3d99b05622053fd00e97886d8a331bcadfe8675c`

Source manifest inner SHA-256: `affea45b58f265c094a921b65932d9f9d69c95e6fe4d4359af07432482f6660f`

Source HEAD: `8295ddd2f2639e7130eaecf2520b6d0d8174f8c7`

Source tree: `db309e74925ea0a47365285d2a0a88316c742ddc`

## 1. Human certification decision

The Human G77-256EX authorization is sufficient for a bounded constitutional certification decision over the exact committed EW manifest scope because:

- Human Authority retains final constitutional authority;
- Layer 3 may review and certify when certification is governed and evidence-backed;
- the authorization expressly permits repository-only certification of components whose committed evidence is sufficient;
- the exact EW manifest, component bytes, limitations, tests, lineage, and exclusions are authenticated; and
- the decision does not invent execution, credit, P12, production, or autonomous authority.

The decision is:

```text
FREEZE_DECISION = CERTIFIED_COMMON_SUBSTRATE_WITH_EXPLICIT_FRESH_OPERATIONAL_BOUNDARIES
REUSABLE_P11_SPCE_EXECUTION_SUBSTRATE = CONSTITUTIONALLY_CERTIFIED__COMMON_REPOSITORY_SUBSTRATE_ONLY__FRESH_OPERATIONAL_AND_VECTOR_BOUNDARIES_EXCLUDED
```

This certification is an admissibility and reuse decision for the exact common repository substrate. It is not an operational result.

## 2. What is certified

The following exact common mechanisms, contracts, and proof obligations are certified within their declared version and freshness boundaries:

1. Git-bound baseline identity verification semantics; each generation still supplies a fresh HEAD and tree.
2. EI canonical producer semantics; each generation still authenticates current producer bytes and output.
3. DU canonical manifest schema and four-gate validation within the existing DU certification scope.
4. EB exact-candidate binding interface; every candidate still requires a fresh receipt.
5. EE runtime-consumer binding interface; every runtime projection still requires a fresh receipt.
6. Canonical continuation-manifest model; exact content and lineage remain generation-bound.
7. Atomic checkpoint durability protocol: file fsync, atomic replace, directory fsync, self-hash, duplicate-key rejection, sentinel rejection, and independent reread.
8. Phase-A authentication checkpoint semantics; current identities remain generation-bound.
9. Materialization identity model; actual base, overlay, seed, checkout, and materialization observations remain fresh.
10. Pre-boot authorization model; authorization identity and state remain fresh and non-replayable.
11. No-NIC construction requirement; actual QEMU argv and network absence remain fresh operational evidence.
12. One-VM/one-boot budget rule; actual counters remain fresh evidence.
13. P01-P12 commissioning evidence structure; actual commissioning result remains fresh.
14. Common raw-evidence profile and its independent separation from vector-specific evidence.
15. Guest teardown requirements; actual completion remains fresh.
16. Host teardown requirements; actual targets and completion remain fresh.
17. Repository-only SPCE reconstruction and continuation protocol, excluding cross-LLM certification and operational replay.
18. EU prospective P11 entry and counter semantics as a version-bound common semantic contract.
19. EW B2 repository custody contract, including the additional EX backing-chain and mutation rules in section 5.
20. EW B6 repository producer/consumer evidence contract and its eight negative regressions.
21. G48 V1 reporting structure as a version-bound common reporting obligation.

The 22-component legacy matrix counts only its original 22 entries. Within that matrix, 17 are certified, zero remain merely evidence-supported, two require hardening through fresh operational evidence, and three remain vector-specific.

## 3. What is not certified

This certification expressly excludes:

- an actual QEMU launch or the exact argv passed at an actual execution boundary;
- a post-execution exit-status observation;
- physical custody, availability, integrity, or immutability of any current base-image file;
- any current overlay, seed, checkout, VM, boot, commissioning, invocation, effect, denial, or teardown result;
- operational adoption of the prospective P11 counter producer/consumer contract;
- any vector identity, vector precondition, vector oracle, protected effect, or denial proof;
- any E05 result or credit, including CONSUMED;
- P12 entry or production routing;
- cross-LLM continuation readiness or CLREC constitutional certification;
- automatic continuation; and
- any component hash, schema, contract, or semantic successor not explicitly certified by this identity.

Historical ER/ES/EN/EO/EP/EQ evidence remains immutable and cannot be presented as fresh proof.

## 4. B1 exact prospective launch-evidence mechanism

B1 remains `OPEN__OPERATIONAL_EVIDENCE_REQUIRED`.

The certified prospective mechanism is:

```text
CANONICAL_QEMU_VECTOR
-> AUTHENTICATED_PRE_BOOT_AUTHORIZATION
-> BOUND_LAUNCHER_IDENTITY
-> ATOMIC_PRE_LAUNCH_RECEIPT
-> EXACT_SUBPROCESS_ARGV_ARGUMENT
-> ATOMIC_POST_EXECUTION_RECEIPT
-> EXIT_STATUS_AND_RECEIPT_PAIR_VALIDATION
```

The future launcher must accept the canonical vector as its only argv source. Immediately before the execution boundary it must persist a pre-launch receipt containing the exact canonical argv representation and digest. The same exact immutable vector object or canonical bytes must supply the subprocess argument. After process return it must persist a post-execution receipt binding the same launcher, vector, VM generation, Git identity, pre-boot authorization, and the integer exit status.

Acceptance requires:

```text
DECLARED_VECTOR_SHA256
= PRE_LAUNCH_RECEIPT_ARGV_SHA256
= EXECUTION_BOUNDARY_ARGV_SHA256
= POST_EXECUTION_RECEIPT_ARGV_SHA256
```

Repository design certification does not close the missing operational observation.

## 5. B2 repository custody certification

B2 repository contract state is `CLOSED__CERTIFIED`; physical custody evidence remains `OPEN__OPERATIONAL_EVIDENCE_REQUIRED`.

The certified repository contract is:

```text
BASE_IMAGE_IDENTITY = VERSIONED_STABLE_ID_PLUS_SHA256
BASE_IMAGE_SHA256 = EXACT_LOWERCASE_SHA256
BASE_IMAGE_FORMAT = QCOW2
BACKING_CHAIN_RULE = EXACTLY_ONE_READ_ONLY_CERTIFIED_BASE__NO_TRANSITIVE_OR_UNDECLARED_BACKING_FILE
READ_ONLY_EXPECTATION = TRUE
PRE_EXECUTION_INTEGRITY_CHECK = SHA256_PLUS_QEMU_IMG_CHECK_PASS
POST_EXECUTION_INTEGRITY_CHECK = SAME_SHA256_PLUS_QEMU_IMG_CHECK_PASS
QEMU_IMG_CHECK_REQUIREMENT = PASS_BEFORE_AND_AFTER_BOUNDED_USE
CUSTODY_BOUNDARY = HUMAN_CONFIGURED_ABSOLUTE_REGULAR_NONSYMLINK_PATH_OUTSIDE_GENERATION_TRANSIENT_ROOT
VERSIONING_RULE = IDENTITY_OR_BYTES_CHANGE_REQUIRES_NEW_VERSION_AND_HUMAN_REAUTHORIZATION
MUTATION_PROHIBITION = BASE_IMAGE_MUST_NEVER_BE_WRITTEN__ALL_GUEST_MUTATION_IS_OVERLAY_ONLY
```

An overlay must bind the exact certified base-image identity and SHA-256. Rebase, backing-chain substitution, base-image format change, path-class violation, pre/post hash mismatch, failed `qemu-img check`, or direct base-image write intent fails closed before execution or credit.

No physical base image is certified by EX.

## 6. B3 and B4 reauthentication

B3 remains `CLOSED__CERTIFIED`: the EW common raw-evidence field set and vector-specific field set are disjoint, versioned, and independently validated.

B4 remains `CLOSED__CERTIFIED_CANONICAL_IDENTITY`: the exact EW manifest outer and inner hashes are the canonical reusable-substrate source identity. EX does not create a successor manifest family.

Every future consumer must:

1. authenticate this certification identity and the EW manifest outer and inner hashes;
2. run the bound EW validator against the exact manifest;
3. authenticate all required component hashes and compatibility;
4. reject invalidation triggers before reuse;
5. import only the certified common proof obligations;
6. create a small vector-specific delta;
7. obtain every generation-bound and fresh operational proof; and
8. reduce credit fail closed.

## 7. B5 authority closure

B5 is `CLOSED__HUMAN_AUTHORITY_EXERCISED_BY_EX` for certification version `1.0.0` and the exact source manifest only.

This decision cannot be generalized into autonomous certification power. A successor version, changed scope, new component bytes, or changed exclusions requires a new governed Human certification decision.

## 8. B6 repository and operational split

B6 repository binding is `CLOSED__CERTIFIED`. B6 operational binding remains `OPEN__OPERATIONAL_EVIDENCE_REQUIRED`.

The only canonical prospective counter model is:

```text
BOUNDARY_REQUEST_COUNT
PRE_ATTEMPT_DENIAL_COUNT
P11_ENTRY_COUNT
P11_OPERATIONAL_INVOCATION_COUNT
PROTECTED_EFFECT_COUNT
SECOND_PROTECTED_EFFECT_COUNT
```

`DENIAL_COUNT` means `PRE_ATTEMPT_DENIAL_COUNT`; `INVOCATION_COUNT` means `P11_OPERATIONAL_INVOCATION_COUNT`. No aliasing counter dialect is created.

Every future operational producer must emit the exact EU event fields and distinct durable source bindings. The consumer must independently reduce events through the certified EU semantics and reject any observed counter mismatch. The EW negative matrix remains mandatory.

```text
REQUEST != ENTRY != INVOCATION != EFFECT
PRE_ATTEMPT_DENIAL => ENTRY_INCREMENT_0
```

Operational closure requires one separately authorized fresh generation whose producer and consumer evidence demonstrates adoption without counter aliasing or historical aggregation.

## 9. Reusable proof classes

### A. Permanent reusable proof within the constitutional baseline

- evidence and a manifest are not authority;
- repository-only hardening cannot award operational credit;
- historical operational evidence cannot serve as fresh evidence;
- vector-specific truth cannot be inherited; and
- unknown or mismatched constitutional state fails closed.

### B. Version-bound reusable proof

- EU P11 semantics and counter model;
- DU schema and validator;
- EI producer semantics;
- EB and EE interfaces;
- checkpoint durability protocol;
- Phase-A, materialization, and pre-boot evidence models;
- QEMU argv canonicalization algorithm;
- no-NIC rule;
- common raw-evidence profile;
- common teardown requirements;
- B2 repository custody contract;
- B6 repository counter contract;
- SPCE repository continuation requirements; and
- G48 V1 structure.

### C. Generation-bound proof

- current HEAD, tree, component hashes, and compatibility;
- Human authorization and execution budget;
- candidate, runtime, DU, EB, and EE receipts;
- current base-image custody receipt;
- current materialization and pre-boot state;
- current launcher identity; and
- terminal teardown and manifest identities.

### D. Vector-specific proof

- selected unsatisfied E05 vector;
- vector preconditions and oracle;
- expected protected effect or denial;
- vector adapter; and
- vector-specific frontier-reduction predicates.

### E. Fresh operational proof

- actual pre/post launch receipts and exit status;
- base-image pre/post integrity and backing-chain observation;
- commissioning result;
- P11 event and counter evidence;
- actual invocation, protected effect, or denial;
- guest and host teardown; and
- terminal result and credit reduction.

Reuse preserves assurance because version/hash/compatibility checks remain mandatory and all stateful or outcome-bearing facts stay generation-bound, vector-specific, or fresh.

## 10. Future E05 generation contract

Every remaining E05 generation must follow:

```text
AUTHENTICATE_CERTIFIED_SUBSTRATE
-> SELECT_ONE_UNSATISFIED_VECTOR
-> GENERATE_VECTOR_DELTA
-> SATISFY_REQUIRED_FRESHNESS
-> MATERIALIZE_IF_SEPARATELY_AUTHORIZED
-> EXECUTE_ONCE_IF_SEPARATELY_AUTHORIZED
-> REDUCE_FRONTIER_FAIL_CLOSED
-> TEARDOWN
-> SEAL
```

It must not regenerate common substrate artifacts merely to obtain a new generation name. It may create only the vector adapter and the generation-bound or fresh evidence required by sections 9C-9E.

Before the first future execution using this certification, the generation must implement and validate the B1 receipts, obtain the B2 physical custody receipt, and demonstrate B6 operational producer/consumer adoption. Those are fresh acceptance gates, not reasons to duplicate the common substrate.

## 11. Invalidation, revocation, and successor rule

Certification is invalid for reuse when any of these occurs:

- `SUBSTRATE_VERSION_CHANGE`;
- `CONSTITUTION_CHANGE` affecting scope or meaning;
- `HASH_MISMATCH` for the certificate, source manifest, validator, or required component;
- `SEMANTIC_MODEL_CHANGE`;
- `BASE_IMAGE_IDENTITY_CHANGE` outside a separately certified custody version;
- `LAUNCHER_CHANGE` outside the certified receipt contract;
- `RAW_SCHEMA_CHANGE`;
- `DU_EB_EE_CONTRACT_CHANGE`;
- `CHECKPOINT_PROTOCOL_CHANGE`;
- `G48_VERSION_CHANGE` affecting reporting obligations;
- discovered contradictory evidence or a failed mandatory regression;
- certification revocation by Human Authority; or
- attempt to use an excluded operational or vector-specific result as inherited proof.

Invalidation fails closed and requires governed reauthentication or a new certification version. A successor must name the superseded certificate and preserve immutable historical evidence.

## 12. Non-authority boundary

This certification creates no E05 credit, VM, boot, operational invocation, P12 entry, production route, automatic continuation, cross-LLM certification, or CLREC certification.

```text
E05_BEFORE = 5/18
E05_AFTER = 5/18
E05_REMAINING = 13
CONSUMED = UNSATISFIED
AUTO_CONTINUABLE = NO
```
