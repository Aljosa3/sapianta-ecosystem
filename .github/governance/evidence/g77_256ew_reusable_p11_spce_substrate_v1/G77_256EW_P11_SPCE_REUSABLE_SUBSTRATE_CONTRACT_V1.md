# G77-256EW Reusable P11/SPCE Substrate Contract V1

Status: repository-only certification-preparation contract; not certified and not operational authority.

Version: `1.0.0`

Identity: `P11_SPCE_REUSABLE_SUBSTRATE_V1`

Required baseline: commit `27f0e4a93a1eabb2d048c9196046b0491af8a665`, tree `d85e34df17f9cbe06e07d68ca4b0d12be16c2d61`.

Authority origin: the Human G77-256EW authorization to design, extract, formalize, validate, and prepare a reusable substrate for certification. This contract does not certify the substrate, authorize operational execution, award E05 credit, enter P12, create a production route, or permit automatic continuation.

## 1. Required decomposition

Future bounded P11/E05 generations shall use this separation:

```text
AUTHENTICATED_COMMON_SUBSTRATE
+ VECTOR_SPECIFIC_ADAPTER
+ FRESH_VECTOR_SPECIFIC_EXECUTION_EVIDENCE
```

The common substrate may preserve implementation semantics and validation contracts. It must never manufacture a current Git identity, Human authorization, vector selection, runtime observation, protected effect, denial observation, teardown result, terminal truth, or frontier reduction.

`manifest_is_authority = false` and `auto_continuable = false` are invariant.

## 2. Reused committed mechanisms

EW introduces no second operational P11 stack. The aggregate validator delegates or binds to:

- the EU `P11_ENTRY_DEFINITION_V1` model and read-only semantic evaluator for event and counter semantics;
- the DU canonical continuation-manifest schema and validator;
- the EI exact producer;
- the EB candidate-bound validation receipt schema and validator;
- the EE runtime-consumer binding receipt schema and validator;
- the ER atomic checkpoint writer protocol;
- the ER canonical QEMU argv encoder and hash implementation;
- the existing P11 operational consumer as a bound future integration target, not an EW execution target;
- committed ER teardown evidence as an evidence-supported pattern; and
- the G48 reporting standard.

The EW aggregate validator exists because none of those components owns aggregate substrate validation, blocker state, common/vector separation, base-image custody policy, launch-receipt structure, or prospective counter-source uniqueness. It has no launch, VM, materialization, commissioning, P11, E05, P12, production, retry, or replay function.

## 3. B1 launch and argv receipt contract

The canonical argv bytes and digest shall be produced only by the bound ER canonical argv implementation unless a separately authorized successor supersedes it.

A pre-launch receipt must contain exactly:

- `schema_id`;
- `receipt_kind = PRE_LAUNCH`;
- `launcher_identity`;
- `launcher_sha256`;
- `canonical_argv`;
- `canonical_argv_sha256`;
- `vm_generation_identity`;
- `required_head`;
- `required_tree`;
- `pre_boot_authorization_identity`;
- `pre_boot_authorization_sha256`;
- `pre_boot_authorization_authenticated = true`;
- `sequence`;
- `execution_invoked = false`;
- `exit_status = null`; and
- `receipt_is_authority = false`.

A post-execution receipt has the same exact fields except:

- `receipt_kind = POST_EXECUTION`;
- `execution_invoked = true`; and
- `exit_status` is an integer.

Both receipts must bind the exact same launcher, argv, generation, Git baseline, and pre-boot authorization. The post-execution sequence must be exactly one greater than the pre-launch sequence. Both must be persisted through an authenticated durable checkpoint mechanism. A launcher must refuse execution unless the pre-boot authorization is already authenticated and all receipt bindings match.

EW validates this contract with repository-only fixtures. EW does not implement or invoke a launcher. Exact executed-call-site and exit-status certification therefore remains dependent on a later separately authorized operational observation.

## 4. B2 base-image custody contract

Every future substrate binding must persist:

- `base_image_id`;
- `base_image_sha256`;
- `format`;
- `qemu_img_check_requirement`;
- `read_only_expectation`;
- `overlay_only_mutation_policy`;
- `allowed_path_or_path_class`;
- `custody_version`;
- `change_authority`; and
- `fail_closed_mismatch_policy`.

The V1 policy is:

```text
FORMAT = QCOW2
QEMU_IMG_CHECK_REQUIREMENT = PASS_BEFORE_AND_AFTER_BOUNDED_USE
READ_ONLY_EXPECTATION = TRUE
OVERLAY_ONLY_MUTATION_POLICY = REQUIRED
ALLOWED_PATH_OR_PATH_CLASS = HUMAN_CONFIGURED_ABSOLUTE_REGULAR_NONSYMLINK_PATH_OUTSIDE_GENERATION_TRANSIENT_ROOT
CUSTODY_VERSION = 1.0.0
CHANGE_AUTHORITY = EXPLICIT_HUMAN_AUTHORIZATION_PLUS_NEW_VERSIONED_MANIFEST
FAIL_CLOSED_MISMATCH_POLICY = DENY_MATERIALIZATION_AND_BOOT
```

The historical ER base-image SHA-256 may be recorded as reference evidence, but an external transient `/tmp` path is not a conforming versioned custody boundary. EW does not read, alter, relocate, or certify the shared base image.

## 5. B3 common raw-evidence profile

The common profile and vector delta are independently reducible.

`COMMON_REQUIRED_EVIDENCE` contains only:

- exact generation and Git baseline identities;
- explicit Human authorization and one-shot budget identities;
- DU, EB, and EE results and bound artifact identities;
- materialization identity for base, overlay, seed, checkout, and no-NIC state;
- authenticated pre-boot authorization;
- exact pre-launch and post-execution receipt bindings;
- commissioning disposition;
- per-request boundary, gate, authorization, start, entry, invocation, effect, and denial evidence;
- independently derived prospective counters;
- guest and host teardown dispositions;
- terminal manifest binding;
- P12 and production-route zero boundaries; and
- checkpoint, continuation, and fail-closed states.

`VECTOR_SPECIFIC_REQUIRED_EVIDENCE` contains only:

- selected E05 vector identity;
- vector-specific preconditions;
- vector-specific expected result;
- vector-specific protected effect;
- vector-specific denial or effect proof;
- fresh execution evidence identity; and
- vector-specific frontier-reduction disposition.

A common-profile result must be reportable as `PASS` or `FAIL` even when the vector delta is `FAIL`, and conversely. Neither result implies the other. Full generation acceptance requires both plus separately authorized fresh execution evidence.

## 6. B4 aggregate manifest

`G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json` is the single aggregate machine-readable substrate manifest. It must:

- bind exact committed component paths and SHA-256 identities;
- classify components only as `CERTIFIED`, `EVIDENCE_SUPPORTED`, `REQUIRES_HARDENING`, or `VECTOR_SPECIFIC`;
- embed the V1 launch receipt, custody, common-profile, vector-delta, and counter-binding contracts;
- preserve known limitations and blocker states;
- carry an authenticated inner hash;
- declare `manifest_is_authority = false`; and
- declare `auto_continuable = false`.

## 7. B5 certification boundary

The present Human authorization permits preparation, not a new certification power. The aggregate substrate may become constitutionally certified only after a separate Human decision that names:

- the exact manifest outer and inner SHA-256 identities;
- the exact component set and versions;
- the certification scope and exclusions;
- the accepted residual operational-evidence requirements;
- supersession and revocation rules;
- mandatory per-generation applicability checks; and
- the rule that vector-specific authorization, execution evidence, protected effects, denials, teardown, and credit are always fresh.

Until then, `REUSABLE_P11_SPCE_EXECUTION_SUBSTRATE` cannot be labeled certified.

## 8. B6 prospective counter producer/consumer contract

The canonical prospective counters are:

```text
BOUNDARY_REQUEST_COUNT
PRE_ATTEMPT_DENIAL_COUNT
P11_ENTRY_COUNT
P11_OPERATIONAL_INVOCATION_COUNT
PROTECTED_EFFECT_COUNT
SECOND_PROTECTED_EFFECT_COUNT
```

`DENIAL_COUNT` means the canonical `PRE_ATTEMPT_DENIAL_COUNT`; no second denial-counter dialect is created.

Each counter must have one distinct durable source binding. Multiple counter names may not alias one aggregate source field. Observed counters must equal the independent reduction of the exact EU event records. Historical aggregate semantics must be explicitly marked historical and must never be submitted as prospective conformance.

The following must fail closed:

- a denied request increments `P11_ENTRY_COUNT`;
- a denied request increments `P11_OPERATIONAL_INVOCATION_COUNT`;
- denied reuse manufactures a second protected effect;
- invocation occurs without admitted entry;
- protected effect occurs without invocation;
- entry occurs without all required gates and authorization;
- multiple counters alias one aggregate source field; and
- historical aggregate semantics are presented as prospective semantics.

EW validates the contract and these negatives without modifying the historical ER harness or the operational consumer. Future operational producers and consumers must explicitly adopt this contract before their evidence can claim prospective conformance.

## 9. Fail-closed and non-authority rules

The substrate must fail closed on:

- baseline, component hash, schema, inner hash, or cross-binding mismatch;
- unknown classification or blocker state;
- missing current Human authorization;
- missing or mismatched DU, EB, or EE evidence;
- missing pre-boot authorization;
- launch-receipt mismatch;
- base-image custody mismatch;
- common-profile or vector-delta failure;
- counter-source aliasing or semantic mismatch;
- missing teardown or terminal truth; or
- any attempt to inherit operational result or credit.

No reusable artifact may authorize execution, automatic retry, repair-and-continue, P12 entry, production routing, credit, commit, push, or autonomous continuation.

## 10. Freeze boundary after EW

Repository-only contract extraction can close the common raw-evidence profile and aggregate-manifest definition. It cannot by itself prove an executed launcher call site, place the shared base image into versioned custody, originate Human certification authority, or prove that an operational producer/consumer has adopted the prospective counter contract.

The expected truthful EW decision is therefore partial unless later validation discovers a defect requiring a stricter result.
