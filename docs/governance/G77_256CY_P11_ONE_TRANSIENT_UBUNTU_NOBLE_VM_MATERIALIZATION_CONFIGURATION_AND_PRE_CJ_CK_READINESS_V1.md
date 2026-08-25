# 1. Implementation Summary

Generation: G77-256CY P11 one transient Ubuntu Noble VM materialization,
configuration and pre-CJ CK readiness

Report identity:
`G77_256CY_P11_ONE_TRANSIENT_UBUNTU_NOBLE_VM_MATERIALIZATION_CONFIGURATION_AND_PRE_CJ_CK_READINESS_V1`

Reporting date: 2026-08-25

Mandatory checkpoint:
`ba7435c17b5e6c1fdb880808de8ba6e308e143bc`

Immediate constitutional predecessor:
`G77_256CX_P11_POST_INSTALL_LOCAL_VM_SUBSTRATE_INDEPENDENT_VERIFICATION_ACTUAL_HOST_DELTA_RECONCILIATION_AND_VM_MATERIALIZATION_READINESS_V1`

Governing authority:

```text
CU_A__AUTHORIZE_BOUNDED_PREPARATION_OF_ONE_NEW_DISPOSABLE_LINUX_VM_TO_A_PRE_CJ_CK_READINESS_STATE_ONLY
```

Objective: under the existing CU-A authority, materialize exactly one
transient non-production Ubuntu Noble amd64 VM with QEMU TCG and exactly one
NoCloud seed, configure only the CK/CF D-A environment boundary, independently
verify pre-CJ CK readiness, and stop and tear down before CJ P01.

Scope classifications used throughout this report:

| Classification | Meaning in CY |
|---|---|
| `HUMAN_DECISION` | exact pre-existing CU-A authority; no new Human semantics |
| `FACT` | directly observed Git, host, QEMU, guest-kernel or filesystem state |
| `EVIDENCE` | exact immutable identity, command output or guest serial record supporting a fact |
| `INFERENCE` | bounded conclusion from identified facts, never an authority grant |
| `NOT_EVALUATED` | CJ P01-P12, P11 and later operational behavior not run |
| `NOT_AUTHORIZED` | CJ, P11, E01-E12, P12, production and topology expansion |

Outcome:

```text
MANDATORY_CHECKPOINT = PASS
INITIAL_GIT_STATUS_SHORT = EMPTY
HEAD = ba7435c17b5e6c1fdb880808de8ba6e308e143bc
CX_BYTE_AUTHENTICATION = PASS
MINIMUM_LINEAGE_AUTHENTICATION = PASS__CX_CW_CU_CK_CF
FULL_G77_HISTORY_RECONSTRUCTION = NO

CU_A_BINDING = PASS__EXISTING_AUTHORITY_NOT_EXPANDED
NEW_HUMAN_SEMANTIC_DECISION_REQUIRED = NO
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0

BASE_IMAGE_AUTHENTICATION = PASS
BASE_IMAGE_SHA256_BEFORE = 6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733
BASE_IMAGE_SHA256_AFTER = 6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733
WORKING_QCOW2_OVERLAY_COUNT = 1
NOCLOUD_SEED_COUNT = 1
QEMU_ACCELERATOR = TCG
QEMU_NETWORK_INTERFACE_ARGUMENT = NONE

GUEST_BOOT = PASS
EXACT_THREE_DISTINCT_ROLE_UIDS = PASS
ROLE_UID_PAIRWISE_DISTINCT = YES
SUPERVISOR_NOT_A_ROLE_UID = PASS
CUSTODY_OWNER_IDENTITY = PASS
FIXED_AF_UNIX_ENDPOINT_PREPARED = PASS
PROTECTED_STATE_DIRECTORY = PASS
SO_PEERCRED_CAPABILITY_AVAILABLE = PASS__TWO_LIVE_KERNEL_READS
EXACT_CHECKOUT_READ_ONLY = PASS
PRODUCTION_ROUTE_COUNT = 0
PRE_CJ_CK_READINESS = PASS

GUEST_TEARDOWN = PASS
QEMU_PROCESS_ABSENT_AFTER_SHUTDOWN = PASS
CY_TRANSIENT_MATERIALIZATION_ROOT_ABSENT = PASS
CJ_EXECUTION_COUNT = 0
P11_OPERATIONAL_EXECUTION_COUNT = 0
E01_E12_EXECUTION_COUNT = 0
P12_ENTRY_COUNT = 0
```

Exactly one VM was created and started. The Ubuntu guest reached the serial
console, mounted the exact checkpoint read-only through a local 9p transport,
created the CK-fixed UID/GID contexts `1/1`, `2/2`, and `3/3` under one
non-role UID/GID `0/0` supervisor, and prepared the fixed custody socket and
protected state directory. Two distinct clients connected through the fixed
AF_UNIX endpoint; the custody process read their kernel-supplied PID/UID/GID
values with `SO_PEERCRED`. No AiGOL code, CJ step, P11 operation, evidence
case, P12 step or production route was executed.

The VM then unlinked its socket, removed its custody-state root, unmounted the
read-only checkout and powered off. Host-side teardown removed the overlay,
seed, serial capture and complete CY transient root. The signed CW base image
was outside the CY root and remains unchanged.

```text
PROJECT_PROGRESS_ESTIMATE = NON_NUMERIC__ONE_AUTHORIZED_VM_MATERIALIZED_BOOTED_AND_DESTROYED__PRE_CJ_CK_READINESS_PASS__STOPPED_BEFORE_CJ_P01
CY_CONTINUATION_REQUIRES_NEW_HUMAN_CJ_DECISION = YES
```

# 2. Code Evidence

## Exact checkpoint and predecessor authentication

The mandated first commands returned:

```text
$ git status --short
<empty>
$ git rev-parse HEAD
ba7435c17b5e6c1fdb880808de8ba6e308e143bc
```

The checkpoint object is:

| Identity | Value |
|---|---|
| commit | `ba7435c17b5e6c1fdb880808de8ba6e308e143bc` |
| tree | `bb05ccf66507fdc09801ae4a418f043a363a87f9` |
| parent | `3eb2ca32301541233964ee6fbf4c5bdc0b8ae36f` |
| subject | `G77-256CX verify VM substrate and materialization readiness` |
| commit time | `2026-08-25T13:24:19+02:00` |

Its delta adds exactly the immediate predecessor:

```text
A  docs/governance/G77_256CX_P11_POST_INSTALL_LOCAL_VM_SUBSTRATE_INDEPENDENT_VERIFICATION_ACTUAL_HOST_DELTA_RECONCILIATION_AND_VM_MATERIALIZATION_READINESS_V1.md
```

CX authenticates byte-for-byte:

| Property | Value |
|---|---|
| Git blob | `177f9052548fdcc7dd12a9b9c5f18e62c867cf4e` |
| raw SHA-256 | `adb12ca4a9aa7cb8a6f874f4e7fab09405172f21132083c030b7d5adf855cb0a` |
| lines | `939` |
| bytes | `36141` |
| committed/worktree equality | `PASS` |

The authenticated CX frontier and readiness state are:

```text
ACTUAL_VM_SUBSTRATE_EXECUTABLE = YES__QEMU_TCG
VM_MATERIALIZATION_READINESS = READY
NEW_HUMAN_SEMANTIC_DECISION_REQUIRED = NO
CX_AUTHENTICATED_FRONTIER = MATERIALIZE_AND_CONFIGURE_EXACTLY_ONE_TRANSIENT_NON_PRODUCTION_UBUNTU_NOBLE_QCOW2_VM_UNDER_EXISTING_CU_A_USING_QEMU_TCG_AND_CLOUD_LOCALDS_TO_THE_PRE_CJ_CK_READINESS_BOUNDARY_ONLY
CX_AUTHENTICATED_AUTO_CONTINUABLE = YES
```

## Minimum checkpoint-local governing lineage

Only the five directly required governing artifacts were authenticated. G48
was read solely as the reporting-format authority. No broad history search was
performed.

| Artifact | Commit | Git blob | Raw SHA-256 | Lines | Bytes |
|---|---|---|---|---:|---:|
| CX | `ba7435c17b5e6c1fdb880808de8ba6e308e143bc` | `177f9052548fdcc7dd12a9b9c5f18e62c867cf4e` | `adb12ca4a9aa7cb8a6f874f4e7fab09405172f21132083c030b7d5adf855cb0a` | 939 | 36141 |
| CW | `3eb2ca32301541233964ee6fbf4c5bdc0b8ae36f` | `ab44863bef5ee3d808f55c94fcb59e3636ced8ce` | `51b16ae3a1f8bb36160667de0318020cc0597c1ee983e8ff6a4a0041796970a0` | 878 | 33513 |
| CU | `57935457d897ea0138ff79ffb700b8e615ce9828` | `5e793908b33fbd31138127703a5bfba5d5601f58` | `1a087493c1daefcba126002b3ba39aca34fcbd2aedd23b8839875c65536679a0` | 735 | 31794 |
| CK | `b253a62b9e6e832195f30f50b11931c2cd6daaa4` | `10446e7ce4448a3af8d22274efbe09c76fb09bd5` | `cfc92ee9e9f6c98fc429eefeccdb080dd4e85fe3c7ce41f8b62e9ce72981a374` | 846 | 37329 |
| CF | `fbe5bb757a7f2423cb1d9706455e32479a9c3f9a` | `165847c2f61be771117d93269b0cb33c3bc341af` | `cc1ddb5c428ade145977949b8b3bbc42318cd29368f7be7bdb17135084c033b0` | 976 | 41373 |

```text
SESSION_CONTEXT_INHERITED = YES
GIT_CHECKPOINT_HANDOFF_USED = YES
CHECKPOINT_LOCAL_ARTIFACT_COUNT_AUTHENTICATED = 5
FULL_G77_HISTORY_RECONSTRUCTION = NO
AUTHENTICATED_CONTRADICTION_COUNT = 0
```

## Reused CK and CF requirements

No environment architecture was invented. CY directly reused these committed
requirements:

```text
SUPERVISOR = UID_0__GID_0__NON_ROLE
ISSUANCE_PROCESS = UID_1__PRIMARY_GID_1__CLIENT_ACCESS_GID_4
CALLER_PROCESS = UID_2__PRIMARY_GID_2__CLIENT_ACCESS_GID_4
CUSTODY_PROCESS = UID_3__PRIMARY_GID_3
FIXED_PRINCIPAL_BINDINGS = issuance_uid_1__caller_uid_2__custody_uid_3

<fixture-root>/ipc owner=3 group=4 mode=0750
<fixture-root>/ipc/p11_da_disposable_custody_v1.sock owner=3 group=4 mode=0660
<fixture-root>/state owner=3 group=3 mode=0700

FIXED_ENDPOINT_NAME = p11_da_disposable_custody_v1.sock
FIXED_PROTOCOL_IDENTITY = P11_DA_DISPOSABLE_LOCAL_IPC_V1
LOCAL_TRANSPORT = AF_UNIX
PEER_IDENTITY = SO_PEERCRED__KERNEL_SUPPLIED
```

The concrete transient binding was:

```text
FIXTURE_ROOT = /run/g77-p11-da
IPC_DIRECTORY = /run/g77-p11-da/ipc
FIXED_ENDPOINT = /run/g77-p11-da/ipc/p11_da_disposable_custody_v1.sock
PROTECTED_STATE = /run/g77-p11-da/state
CHECKOUT_MOUNT = /mnt/aigol-checkout
```

## Authenticated image and exactly one construction

The already-verified CW image was authenticated before overlay creation and
again after VM teardown:

```text
BASE_IMAGE = /tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img
BASE_IMAGE_BYTES = 624447488
BASE_IMAGE_FORMAT = QCOW2_V3
BASE_IMAGE_VIRTUAL_BYTES = 3758096384
EXPECTED_SHA256 = 6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733
SHA256_BEFORE = 6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733
SHA256_AFTER = 6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733
QEMU_IMG_CHECK_BEFORE = PASS__NO_ERRORS
```

The minimum host construction commands were:

```bash
qemu-img create -f qcow2 -F qcow2 -b /tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img /tmp/g77_256cy.nOtCgO/guest-overlay.qcow2
cloud-localds -N /tmp/g77_256cy.nOtCgO/network-config /tmp/g77_256cy.nOtCgO/nocloud-seed.img /tmp/g77_256cy.nOtCgO/user-data /tmp/g77_256cy.nOtCgO/meta-data
```

Before boot, the overlay was 196,664 bytes, structurally clean, and had the
authenticated base as its sole backing file. The one seed was 391,168 bytes.
The cloud-config parsed as YAML and its embedded Python verifier compiled.

Construction identities before boot:

| Object | Raw SHA-256 |
|---|---|
| meta-data | `aeb4a645470e830345f714bc8dff4ce5a3e31e528601d73af9568480acb3a1b3` |
| network-config | `639b6f419a9ac49312b218e12395dc7e7d623d96202c3315a92dcd19d6fa02ba` |
| user-data | `5f5e99b8ca47522ada4a2b26d9a69b866f1dc89e030ac438ba7aa0f9607c9ba1` |
| working overlay | `6ea4eed169518c646774cfbe2c7b8c00646a9cdead8798f7c94c786c6b6ce8b2` |
| NoCloud seed | `5cd7550af21458f5e1a7dce2f2e5ee075f8f0fa5bd4276f833563b5532eb6859` |

Exactly one QEMU command was issued:

```bash
qemu-system-x86_64 -name g77-256cy-pre-cj -machine pc,accel=tcg -cpu max -smp 2 -m 1536 -nodefaults -no-reboot -display none -monitor none -serial file:/tmp/g77_256cy.nOtCgO/serial.log -drive file=/tmp/g77_256cy.nOtCgO/guest-overlay.qcow2,if=virtio,format=qcow2 -drive file=/tmp/g77_256cy.nOtCgO/nocloud-seed.img,if=virtio,format=raw,readonly=on -device virtio-rng-pci -virtfs local,path=/home/pisarna/work/sapianta,mount_tag=aigol_checkout,security_model=none,readonly=on -nic none
```

`-nodefaults` and `-nic none` prevented creation of a guest network device.
The checkout was exposed only through local read-only 9p; it was not copied.
The serial channel was evidence-only and no interactive login or credential
was used.

## Minimum guest verifier excerpt

The following representative excerpt reproduces the material verifier
configuration. Unrelated serialization and teardown lines are omitted.

```python
EXPECTED_HEAD = "ba7435c17b5e6c1fdb880808de8ba6e308e143bc"
CHECKOUT = Path("/mnt/aigol-checkout")
FIXTURE_ROOT = Path("/run/g77-p11-da")
IPC_DIR = FIXTURE_ROOT / "ipc"
STATE_DIR = FIXTURE_ROOT / "state"
ENDPOINT = IPC_DIR / "p11_da_disposable_custody_v1.sock"
PEERCRED = struct.Struct("3i")
ROLE_BINDINGS = {
    "issuance": {"uid": 1, "gid": 1, "groups": [4]},
    "caller": {"uid": 2, "gid": 2, "groups": [4]},
    "custody": {"uid": 3, "gid": 3, "groups": []},
}

subprocess.run([
    "mount", "-t", "9p", "-o", "trans=virtio,version=9p2000.L,ro",
    "aigol_checkout", str(CHECKOUT)
], check=True, timeout=60)

FIXTURE_ROOT.mkdir(mode=0o755)
IPC_DIR.mkdir(mode=0o750)
STATE_DIR.mkdir(mode=0o700)
os.chown(FIXTURE_ROOT, 0, 0)
os.chown(IPC_DIR, 3, 4)
os.chmod(IPC_DIR, 0o750)
os.chown(STATE_DIR, 3, 3)
os.chmod(STATE_DIR, 0o700)

raw = connection.getsockopt(
    socket.SOL_SOCKET, socket.SO_PEERCRED, PEERCRED.size
)
pid, uid, gid = PEERCRED.unpack(raw)
```

The two client children dropped supplementary groups and identities before
connecting: issuance used UID/GID `1/1` plus group `4`; caller used `2/2` plus
group `4`. The custody server used UID/GID `3/3` with no supplementary group.
The supervisor remained UID/GID `0/0` and was not included in the role map.

## Independent guest evidence

The guest reached Ubuntu `24.04.4 LTS`. Its final cloud-init stage began at
guest uptime 230.32 seconds; readiness evidence was emitted at uptime 231.75
seconds and poweroff completed at uptime 247.118781 seconds.

The exact serial readiness record was:

```json
{
  "checkout_head": "ba7435c17b5e6c1fdb880808de8ba6e308e143bc",
  "checkout_ref": "refs/heads/master",
  "checkout_mount": {
    "mount_line": "aigol_checkout /mnt/aigol-checkout 9p ro,relatime,access=client,trans=virtio 0 0",
    "mount_read_only_option": true,
    "statvfs_read_only": true
  },
  "supervisor": {"pid": 918, "uid": 0, "gid": 0, "non_role": true},
  "client_processes": [
    {"ack": "OK", "label": "issuance", "pid": 925, "uid": 1, "gid": 1, "groups": [4]},
    {"ack": "OK", "label": "caller", "pid": 926, "uid": 2, "gid": 2, "groups": [4]}
  ],
  "custody_server": {"pid": 924, "uid": 3, "gid": 3, "groups": []},
  "kernel_peer_credentials": [
    {"label": "issuance", "pid": 925, "uid": 1, "gid": 1},
    {"label": "caller", "pid": 926, "uid": 2, "gid": 2}
  ],
  "role_uid_count": 3,
  "role_gid_count": 3,
  "pairwise_distinct_role_uid_comparisons": 3,
  "so_peercred_constant": 17,
  "so_peercred_live_reads": 2,
  "fixture_root": {"path": "/run/g77-p11-da", "uid": 0, "gid": 0, "mode": "0755"},
  "ipc_directory": {"path": "/run/g77-p11-da/ipc", "uid": 3, "gid": 4, "mode": "0750"},
  "fixed_endpoint": {"path": "/run/g77-p11-da/ipc/p11_da_disposable_custody_v1.sock", "uid": 3, "gid": 4, "mode": "0660", "is_socket": true},
  "protected_state": {"path": "/run/g77-p11-da/state", "uid": 3, "gid": 3, "mode": "0700"},
  "interfaces": ["lo"],
  "production_route_count": 0,
  "production_routes": [],
  "status": "PASS"
}
```

Both issuance and caller independently received:

```text
STATE_TRAVERSAL_DENIED = TRUE
ENDPOINT_UNLINK_DENIED = TRUE
ENDPOINT_RENAME_DENIED = TRUE
```

The guest had no network interface other than `lo`. Its default image
`systemd-networkd-wait-online` unit timed out because no NIC existed; cloud-init
then continued normally. That package-default timeout is consistent with, and
does not weaken, the independently recorded zero-route and loopback-only
facts. No package was installed or updated in the guest.

The final guest teardown record was:

```json
{
  "checkout_unmounted": true,
  "endpoint_absent": true,
  "errors": [],
  "fixture_root_absent": true,
  "status": "PASS"
}
```

## Host-side final evidence and counters

Before host deletion, the post-boot objects were:

| Object | Bytes | Raw SHA-256 | Validation |
|---|---:|---|---|
| working overlay | 22740992 | `dd5542a1eb316344164e825082eee6dc103b4ffd6616eef4a14c505ccd21c5d2` | `qemu-img check`: no errors |
| NoCloud seed | 391168 | `5cd7550af21458f5e1a7dce2f2e5ee075f8f0fa5bd4276f833563b5532eb6859` | exactly one seed |
| serial evidence | 107723 | `ed82a6fc2d9d767590066bb8e5c8cf1a6055ec8505e89faff2861979fcaaa2f8` | 1202 lines; readiness and teardown markers complete |

The exact `/tmp/g77_256cy.nOtCgO` root was then removed. Final checks found no
QEMU process and no CY transient root. The CW base image remained present with
the exact authenticated SHA-256.

```text
VM_CREATION_COUNT = 1
VM_START_COUNT = 1
VM_BOOT_COUNT = 1
VM_TEARDOWN_COUNT = 1

ROLE_UID_COUNT = 3
PAIRWISE_DISTINCT_ROLE_UID_COUNT = 3
ROLE_GID_COUNT = 3
LIVE_SO_PEERCRED_READ_COUNT = 2

PRODUCTION_ROUTE_COUNT = 0

CJ_EXECUTION_COUNT = 0
P11_OPERATIONAL_EXECUTION_COUNT = 0
E01_E12_EXECUTION_COUNT = 0
P12_ENTRY_COUNT = 0

NEW_AUTHORITY_PATH_COUNT = 0
NEW_PRODUCTION_PATH_COUNT = 0
NEW_PARALLEL_AUTHORITY_PATH_COUNT = 0
NEW_PARALLEL_PRODUCTION_PATH_COUNT = 0
NEW_REPLAY_RUNTIMELEDGER_PATH_COUNT = 0
NEW_EVIDENCE_PRODUCTION_PATH_COUNT = 0
NEW_PERMANENT_EVIDENCE_SUBSYSTEM_COUNT = 0

MACHINE_COMPLETED_HUMAN_SEMANTICS = 0
```

# 3. Constitutional Self-Assessment

## Verified

- `HEAD` exactly matched the mandatory checkpoint and the initial worktree and
  index were clean.
- CX authenticated byte-for-byte as the immediate constitutional predecessor.
- CW, CU, CK and CF authenticated as the minimum directly required lineage.
- CU-A already supplied the complete Human semantic authority for one
  pre-CJ disposable VM; no new semantic decision was supplied or generated.
- the official Noble base image matched the CW signed-manifest digest before
  construction and after teardown and remained unchanged;
- exactly one overlay and one NoCloud seed were constructed;
- exactly one QEMU TCG VM was started and exactly one Ubuntu guest booted;
- QEMU exposed no guest NIC and the guest observed only `lo` and zero
  non-loopback routes;
- the exact checkpoint was mounted through local 9p with both the mount `ro`
  option and the kernel read-only filesystem flag;
- the guest used one non-role UID/GID `0/0` supervisor and exactly three
  genuine, pairwise-distinct kernel UID/GID role contexts `1/1`, `2/2`, and
  `3/3`;
- issuance and caller had only client-access GID `4` in addition to their
  primary GIDs; custody had no supplementary groups;
- the fixed endpoint was a real AF_UNIX socket owned `3:4` with mode `0660`;
- the endpoint parent was owned `3:4` with mode `0750` and denied unlink and
  rename to both client roles;
- protected state was owned `3:3` with mode `0700` and denied traversal to
  both client roles;
- the custody process executed two live `SO_PEERCRED` reads and observed the
  exact issuance and caller kernel PID/UID/GID values;
- guest teardown removed the socket, fixture root and checkout mount;
- host teardown removed the QEMU process, overlay, seed, serial log, cloud-init
  inputs and complete CY transient root;
- no tracked AiGOL runtime, source, test or prior governance artifact changed;
- no CF or D-A semantic or architecture change occurred;
- no CJ, P11, E01-E12, P12 or production action occurred; and
- no authority, production, parallel, Replay/RuntimeLedger, evidence-production
  or permanent-evidence path was created.

## Not Verified

- `NOT_EVALUATED`: CJ P01-P12 commissioning against a newly authorized
  materialization is not evaluated by CY.
- `NOT_EVALUATED`: P11 operational behavior and E01-E12 evidence generation
  remain unexecuted.
- `NOT_EVALUATED`: P12 entry, production routing and deployment remain
  unexecuted.
- `NOT_AUTHORIZED`: CY does not grant CJ authority even though CK environment
  readiness passed.
- `NOT_AUTHORIZED`: CY does not grant access, observation or operational
  authority beyond the transient OS-level readiness probes recorded here.
- `NOT_VERIFIED`: the destroyed guest cannot itself be reused; a future
  authorized CJ generation must independently rematerialize and reverify the
  same bounded recipe rather than trusting this report as live state.

## Constitutional health and topology

```text
CONSTITUTIONAL_HEALTH = PASS__CY_SCOPE_ONLY__PRE_CJ_CK_READINESS_DEMONSTRATED__NO_AUTHORITY_EXPANSION
CONSTITUTIONAL_HEALTH_EVIDENCE = EXACT_CHECKPOINT__AUTHENTICATED_LINEAGE__SIGNED_IMAGE_DIGEST__ONE_VM_BOOT__THREE_KERNEL_UIDS__LIVE_SO_PEERCRED__FIXED_CUSTODY_PERMISSIONS__READ_ONLY_CHECKOUT__ZERO_ROUTE__COMPLETE_TEARDOWN

SHADOW_AUTOMATION_STATE = UNCHANGED__ISOLATED__NOT_INVOKED
SHADOW_INVOCATION_COUNT = 0
SHADOW_DESIGN_TARGET = NONE_IN_CY_SCOPE

CONSTITUTIONAL_FRONTIER_DISTANCE = PRE_CJ_CK_READINESS_PASSED__ONE_SEPARATE_HUMAN_CJ_AUTHORIZATION_DECISION_REMAINS
CONSTITUTIONAL_FRONTIER_DISTANCe = PRE_CJ_CK_READINESS_PASSED__ONE_SEPARATE_HUMAN_CJ_AUTHORIZATION_DECISION_REMAINS
DISTANCE_TO_CJ_P01 = ONE_EXPLICIT_HUMAN_CJ_AUTHORIZATION
DISTANCE_TO_P11 = NOT_ASSESSED__CJ_NOT_AUTHORIZED_OR_EXECUTED

GOVERNANCE_EFFICIENCE = POSITIVE__FIVE_ARTIFACT_CHECKPOINT_LOCAL_REUSE__ONE_VM__ONE_OVERLAY__ONE_SEED__ONE_BOOT__ONE_TEARDOWN__NO_RETRY_OR_HISTORY_RECONSTRUCTION
COGNITION_ASSISTED_HANDOFF = PASS__CK_CF_REQUIREMENTS_TRANSLATED_TO_ONE_DETERMINISTIC_VM_RECIPE_AND_ONE_CJ_AUTHORIZATION_FRONTIER
OVERENGINEERING_RISK = LOW__QEMU_TCG__ONE_BASE__ONE_OVERLAY__ONE_SEED__NO_NIC__NO_LIBVIRT_GUI_DAEMON_OR_ORCHESTRATOR
RISK_IF_READINESS_IS_TREATED_AS_CJ_OR_P11_AUTHORITY = CRITICAL
RISK_IF_DESTROYED_GUEST_STATE_IS_TREATED_AS_LIVE = CRITICAL

CANDIDATE_CAPABILITY = DISPOSABLE_P11_D_A_THREE_UID_PRE_CJ_ENVIRONMENT
CANDIDATE_CAPABILITY_STATE = PRE_CJ_CK_READINESS_DEMONSTRATED__GUEST_DESTROYED__CJ_NOT_AUTHORIZED
CONSTITUTIONAL_CONTINUATION_PROGRESS = CU_A_REUSED__CX_READY_REUSED__ONE_NOBLE_VM_MATERIALIZED__CK_CF_BOUNDARY_DEMONSTRATED__ALL_TRANSIENT_STATE_DESTROYED__STOPPED_BEFORE_CJ_P01

CK_REUSE_SUFFICIENT = YES
CF_D_A_REUSE_SUFFICIENT = YES
TRACKED_AIGOL_SOURCE_CHANGE_REQUIRED = NO
D_A_ARCHITECTURE_CHANGE_REQUIRED = NO
OPERATIONAL_TOPOLOGY_CHANGE = NONE__TRANSIENT_PRE_CJ_VM_DESTROYED
```

## AIGOL_CODEX_WORK_SHARE

| Actor | Work performed | Constitutional semantic authority |
|---|---|---|
| Human Constitutional Authority | exact CU-A authorization inherited unchanged | `100_PERCENT` |
| AiGOL/Git/QEMU/cloud-init mechanics | object hashing, one VM lifecycle and deterministic OS probes | `0_PERCENT` |
| Codex cognition | minimum requirement reduction, verifier construction, evidence classification and report | `0_PERCENT` |
| guest Linux kernel | PID/UID/GID and AF_UNIX `SO_PEERCRED` material facts | `0_PERCENT` |

## COGNITION_PROVENANCE

| Provenance | Content | Authority effect |
|---|---|---|
| `HUMAN_DECISION` | exact inherited CU-A token | sole scope authority |
| `AUTHENTICATED_GIT_EVIDENCE` | checkpoint, CX and minimum CW/CU/CK/CF bytes | lineage evidence only |
| `SIGNED_IMAGE_EVIDENCE` | exact CW Noble image SHA-256 | supply identity only |
| `HOST_EXECUTION_EVIDENCE` | QEMU command, overlay/seed identities and teardown absence | implementation facts only |
| `GUEST_KERNEL_EVIDENCE` | UIDs, GIDs, permissions, AF_UNIX and `SO_PEERCRED` | readiness facts only |
| `CODEX_INFERENCE` | conjunction classification and next-frontier reduction | no Human semantic authority |
| `MACHINE_COMPLETED_HUMAN_SEMANTICS` | none | zero |

## Token benchmark

Only exposed telemetry is reported. No unavailable usage value is inferred.

```text
TOKEN_BENCHMARK = OBSERVABLE_VALUES_ONLY
SESSION_OR_THREAD_ID = NOT_EXPOSED
CONTEXT_START_USED = NOT_EXPOSED
CONTEXT_END_USED = NOT_EXPOSED
CONTEXT_USED_DELTA = NOT_EXPOSED
CONTEXT_COMPACTION_COUNT = 1__OBSERVED
SEVEN_DAY_LIMIT_START = NOT_EXPOSED
SEVEN_DAY_LIMIT_END = NOT_EXPOSED
SEVEN_DAY_LIMIT_DELTA = NOT_EXPOSED
WORKED_TIME = NOT_EXPOSED__GUEST_UPTIME_TO_POWEROFF_247_118781_SECONDS_OBSERVED
FULL_HISTORY_RECONSTRUCTION = NO
COGNITION_FALLBACK_COUNT = 0
PROMPT_CONTEXT_REUSE_RATIO = HIGH__QUALITATIVE__CX_CW_CU_CK_CF_DIRECT_REUSE
CHECKPOINT_AUTHENTICATION_COST = LOW__QUALITATIVE
CONTEXT_REUSE_COST = LOW__QUALITATIVE
HUMAN_MACHINE_SEMANTIC_BOUNDARY_REASONING_COST = MEDIUM__QUALITATIVE
VM_MATERIALIZATION_AND_VERIFICATION_COST = DOMINANT__QUALITATIVE
ARTIFACT_GENERATION_COST = MEDIUM__QUALITATIVE
```

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Ponovno se uporabijo CU-A Human authorization, CW signed Ubuntu image,
   CX-verified QEMU TCG and `cloud-localds`, CK three-UID environment contract
   ter CF fixed AF_UNIX/`SO_PEERCRED` D-A trust boundary. Canonical CHE, Human
   Authority Act, Replay in RuntimeLedger ostanejo nespremenjeni in niso
   operativno invoked.

2. **Katere nove zmogljivosti, če sploh, nastanejo?** Nastane samo dokaz, da
   en disposable VM recipe materialno doseže pre-CJ CK readiness. VM in vsi
   njegovi transient artifacts so odstranjeni; ne nastane trajna runtime ali
   production zmogljivost.

3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Nobena
   obstoječa certificirana zmogljivost ni spremenjena ali odstranjena.

4. **Ali implementacija ustvarja vzporedni tok?** Ne. VM je enkraten pre-CJ
   test boundary pod obstoječim CF/D-A modelom, brez druge authority, custody,
   Replay ali production poti.

5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne. VM je bil
   zagnan z `-nic none`, guest je imel samo `lo`, production-route count je
   nič in production-path delta ostane nič.

```text
NEW_AUTHORITY_PATH_COUNT = 0
NEW_PRODUCTION_PATH_COUNT = 0
NEW_PARALLEL_AUTHORITY_PATH_COUNT = 0
NEW_PARALLEL_PRODUCTION_PATH_COUNT = 0
NEW_REPLAY_RUNTIMELEDGER_PATH_COUNT = 0
NEW_EVIDENCE_PRODUCTION_PATH_COUNT = 0
NEW_PERMANENT_EVIDENCE_SUBSYSTEM_COUNT = 0
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0
```

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| mandatory clean checkpoint | exact first command outputs | status and HEAD equality | `PASS` |
| CX immediate predecessor | blob, SHA-256, lines and bytes | committed/worktree byte equality | `PASS` |
| minimum lineage | CW/CU/CK/CF identities | checkpoint-local Git/hash audit | `PASS` |
| CU-A reuse without expansion | exact inherited token and exclusions | authority-scope comparison | `PASS` |
| authenticated base unchanged | same signed SHA-256 before and after | raw hash plus `qemu-img check` | `PASS` |
| exactly one overlay | one QCOW2 child with sole authenticated backing file | file count and backing-chain inspection | `PASS` |
| exactly one NoCloud seed | one seed image and one QEMU seed drive | file and command audit | `PASS` |
| embedded configuration validity | YAML parse and Python compile | pre-boot static validation | `PASS` |
| exactly one VM/start/boot | one QEMU command, one Noble serial boot | process/session and serial audit | `PASS` |
| QEMU TCG | exact `accel=tcg` command | command and executable version | `PASS` |
| zero guest NIC | `-nodefaults -nic none`; guest `interfaces=[lo]` | command plus guest kernel inspection | `PASS` |
| zero production route | empty guest non-loopback route list | `/proc/net/route` inspection | `PASS` |
| non-role supervisor | PID 918 UID/GID 0/0, excluded from bindings | guest kernel identity capture | `PASS` |
| exactly three role UIDs | UIDs 1, 2 and 3 | child and custody kernel identity capture | `PASS` |
| pairwise UID distinction | three of three unequal pairs | deterministic comparison | `PASS` |
| exact role GIDs/groups | 1/1+4, 2/2+4, 3/3+none | process identity capture | `PASS` |
| fixed endpoint path | exact CF filename under fixed absolute root | guest path equality | `PASS` |
| endpoint type/ownership/mode | AF_UNIX, `3:4`, `0660` | guest `stat` | `PASS` |
| endpoint parent protection | `3:4`, `0750` | `stat`; two unlink/rename denials | `PASS` |
| protected state | `3:3`, `0700` | `stat`; two traversal denials | `PASS` |
| live `SO_PEERCRED` | two kernel reads for PID/UID/GID 925/1/1 and 926/2/2 | AF_UNIX server `getsockopt` | `PASS` |
| exact checkout identity | ref `master`; exact expected HEAD | guest read of read-only mounted `.git` | `PASS` |
| checkout read-only | mount option and kernel filesystem flag both read-only | `/proc/mounts` plus `statvfs` | `PASS` |
| no writable second checkout | one read-only 9p exposure; no copy operation | QEMU/config audit | `PASS` |
| no guest package install | no package command in cloud-config | exact configuration audit | `PASS` |
| no libvirt/GUI/manager layer | direct QEMU only | command/config audit | `PASS` |
| guest teardown | mount/socket/root absence; zero errors | final guest serial record | `PASS` |
| host teardown | no QEMU process and CY root absent | post-run process/path audit | `PASS` |
| tracked source preservation | report is sole repository delta | Git status/path audit | `PASS` |
| CF/D-A preservation | no source or semantic change | path and requirement comparison | `PASS` |
| CJ P01-P12 | outside CY authority | not run | `NOT_RUN` |
| P11 operational execution | outside CY authority | not run | `NOT_RUN` |
| E01-E12 | outside CY authority | not run | `NOT_RUN` |
| P12 entry | outside CY authority | not run | `NOT_RUN` |
| production deployment | prohibited and absent | topology audit | `NOT_APPLICABLE` |
| topology deltas | every required delta counter zero | source, process, route and path audit | `PASS` |
| machine-completed Human semantics | none | semantic provenance audit | `PASS` |

# 5. Repository Mutation Summary

Created exactly one tracked file:

- CREATE
  `docs/governance/G77_256CY_P11_ONE_TRANSIENT_UBUNTU_NOBLE_VM_MATERIALIZATION_CONFIGURATION_AND_PRE_CJ_CK_READINESS_V1.md`
  — this G48 governance artifact only.

No other repository file was created or modified. In particular, CY did not
modify:

- tracked AiGOL runtime, source or test code;
- CF source, tests or semantics;
- D-A architecture;
- canonical CHE or Human Authority Act;
- Replay or RuntimeLedger;
- production or shadow topology;
- CX, CW, CU, CK or any prior governance report; or
- the authenticated CW base image.

Transient, removed after validation:

```text
TRANSIENT_ROOT = /tmp/g77_256cy.nOtCgO
REMOVED_OVERLAY_COUNT = 1
REMOVED_NOCLOUD_SEED_COUNT = 1
REMOVED_SERIAL_LOG_COUNT = 1
REMOVED_CLOUD_INIT_INPUT_COUNT = 3
TRANSIENT_ROOT_ABSENT_AFTER_TEARDOWN = YES
QEMU_PROCESS_COUNT_AFTER_TEARDOWN = 0
```

```text
TRACKED_SOURCE_MUTATION_COUNT = 0
MODIFIED_CF_PATH_COUNT = 0
MODIFIED_RUNTIME_SOURCE_COUNT = 0
MODIFIED_TEST_COUNT = 0
MODIFIED_PRIOR_GOVERNANCE_ARTIFACT_COUNT = 0
CREATED_GOVERNANCE_ARTIFACT_COUNT = 1
STAGED_FILE_COUNT = 0
COMMIT_CREATED = NO
PUSH_PERFORMED = NO
```

Recommended Human Git commands, intentionally not executed:

```bash
git add -- docs/governance/G77_256CY_P11_ONE_TRANSIENT_UBUNTU_NOBLE_VM_MATERIALIZATION_CONFIGURATION_AND_PRE_CJ_CK_READINESS_V1.md
git commit -m "G77-256CY prove transient VM pre-CJ CK readiness"
```

# 6. Certification Verdict

```text
PRE_CJ_CK_READINESS = PASS
CJ_READINESS = NOT_EVALUATED
CJ_AUTHORIZATION = NOT_GRANTED
CJ_EXECUTION_COUNT = 0
P11_OPERATIONAL_EXECUTION_COUNT = 0
E01_E12_EXECUTION_COUNT = 0
P12_ENTRY_COUNT = 0
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0

EXACT_NEXT_CONSTITUTIONAL_FRONTIER = HUMAN_DECIDE_WHETHER_TO_AUTHORIZE_ONE_BOUNDED_CJ_P01_P12_COMMISSIONING_GENERATION_USING_THE_VERIFIED_CY_VM_RECIPE_WITHOUT_ENTERING_P11
AUTO_CONTINUABLE = NO
```

`PRE_CJ_CK_READINESS__PASS`
