# 1. Implementation Summary

Generation: G77-256CK

Report identity:
`G77_256CK_P11_COMPLIANT_THREE_DISTINCT_UID_EXECUTION_ENVIRONMENT_REQUIREMENTS_AND_MINIMUM_PROVISIONING_HANDOFF_V1`

Reporting date: 2026-08-24

Mandatory committed checkpoint:
`a7f388523357840bd6ee57c5e4749624fcf27e63`

Constitutional baseline: committed G77-256CJ and its checkpoint-local
CI/CH/CG/CF/CE/CD lineage.

Implementation contracts: committed D-A Category D contract, CD evidence
plan, CF construction-only substrate, CI bounded operational authorization,
CH mandatory preconditions, and CJ fail-closed commissioning result.

Objective:

Determine the minimum compliant isolated execution-environment and operator
provisioning handoff needed to repeat the already-authorized CJ commissioning
with exactly three genuinely distinct OS UID role principals, without changing
the selected D-A architecture or tracked AiGOL source.

Outcome:

```text
MANDATORY_HEAD_AUTHENTICATION = PASS__EXACT
INITIAL_GIT_STATUS_SHORT = EMPTY__CLEAN
CJ_ARTIFACT_BYTE_AUTHENTICATION = PASS
CJ_DIRECT_PARENT_CI = PASS__EXACT
CI_CH_CG_CF_CE_CD_FIRST_PARENT_LINEAGE = PASS__EXACT
CJ_COMMITTED_VERDICT = FAIL_CLOSED__P01_NOT_PROVEN
THREE_DISTINCT_UID_REQUIREMENT = FIXED__NOT_REINTERPRETED
MINIMUM_COMPLIANT_MECHANISM = EPHEMERAL_LINUX_USER_NAMESPACE_WITH_FUNCTIONAL_SUBORDINATE_UID_GID_MAPPING
COMPLIANT_ALTERNATIVES = ROOTFUL_EPHEMERAL_CONTAINER__DISPOSABLE_LINUX_VM__TEMPORARY_LOCKED_HOST_ACCOUNTS
TRACKED_AIGOL_SOURCE_CHANGE_REQUIRED = NO
D_A_ARCHITECTURE_CHANGE_REQUIRED = NO
PRIVILEGED_PROVISIONING_PERFORMED = NO
CJ_COMMISSIONING_REPEATED = NO
P01_P12_EXECUTION_COUNT = 0
P11_OPERATIONAL_INVOCATION_COUNT = 0
E01_E12_EXECUTION_COUNT = 0
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0
AUTO_CONTINUABLE = NO
```

The minimum recommended mechanism is a short-lived Linux user, mount, PID,
IPC, UTS and network namespace created outside the current restricted Codex
runner. The operator account must have functional `newuidmap` and `newgidmap`
helpers and assigned subordinate UID/GID ranges. The namespace maps the
operator to namespace UID/GID `0` solely as a non-role provisioner and maps
three different subordinate kernel UIDs to role UIDs `1`, `2`, and `3`.

The three D-A role principals remain exactly:

| Namespace UID | Fixed role | Permitted constitutional effect |
|---|---|---|
| `1` | `HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL` | no authority origin by OS identity; only the separately exact Human act may carry authority |
| `2` | `P11_ORCHESTRATION_CALLER_PRINCIPAL` | bounded caller identity only |
| `3` | `AUTHORITY_CUSTODY_PROCESS_PRINCIPAL` | fixed endpoint and owner-state custody only |

Namespace UID `0` is not a fourth D-A principal. It is an ephemeral
provisioning supervisor, is absent from `FixedPrincipalBindings`, is rejected
for every custody operation, cannot originate authority, and exists only to
create, observe and tear down the disposable boundary.

Implementation scope:

- authenticate the exact committed baseline;
- define deterministic host, namespace, filesystem, AF_UNIX, `SO_PEERCRED`,
  process-launch and teardown requirements;
- compare only mechanisms that preserve the fixed D-A composition;
- specify one minimum operator handoff; and
- create this governance artifact.

Created repository path:

- `docs/governance/G77_256CK_P11_COMPLIANT_THREE_DISTINCT_UID_EXECUTION_ENVIRONMENT_REQUIREMENTS_AND_MINIMUM_PROVISIONING_HANDOFF_V1.md`.

Modified modules:

- none.

Intentionally unchanged modules:

- all four committed CF implementation/test paths;
- canonical CHE and Human Authority Act contracts;
- canonical Replay and RuntimeLedger;
- Category C and P10 `[X,Y,BO]`;
- runtime, production, P11, P12 and deployment topology; and
- every committed governance artifact.

Architectural boundaries preserved:

- exactly three role UIDs, not three labels or processes sharing one UID;
- one fixed AF_UNIX custody endpoint and one protected owner-state store;
- kernel-supplied credentials, never request-supplied identity;
- canonical CF/CHE/Human Authority/Replay/RuntimeLedger reuse;
- zero production route, zero fallback and zero parallel path;
- no operational act, P11 invocation or E01-E12 execution; and
- operator-controlled provisioning values are bound before CJ and are not
  request fields.

# 2. Code Evidence

## Mandatory checkpoint and committed artifact authentication

The two mandated commands were the first repository assessment commands:

```text
$ git rev-parse HEAD
a7f388523357840bd6ee57c5e4749624fcf27e63

$ git status --short
<empty>
```

Exact HEAD object identity:

| Identity | Value |
|---|---|
| commit | `a7f388523357840bd6ee57c5e4749624fcf27e63` |
| tree | `f9e6f3e531c772cc0664b699c8d1aac7d9f55c10` |
| parent | `7894e508f6f7f168467f1f8bbae4a020bbc9f8f1` |
| subject | `G77-256CJ fail closed P11 preflight at P01` |
| commit time | `2026-08-24T16:24:37+02:00` |

The commit delta contains exactly one path:

```text
A  docs/governance/G77_256CJ_AUTHORIZED_DISPOSABLE_OS_MATERIALIZATION_AND_CH_P01_P12_PREFLIGHT_COMMISSIONING_USING_COMMITTED_CF_V1.md
```

Committed CJ artifact identity:

| Identity | Value |
|---|---|
| Git blob | `93b5c70969905d5f7784c12d278abd530bd848d0` |
| raw SHA-256 | `a19f5701e471194abd3561ad932b2025c78c39fb4230e0ee74ff366c0a6f1a9e` |
| bytes | `38816` |
| committed/worktree equality | `PASS__CLEAN_CHECKOUT` |

The authenticated committed CJ conclusion is:

```text
CH_P01_P12_PREFLIGHT = FAIL_CLOSED
FIRST_FAILED_PRECONDITION = P01__EXACT_THREE_DISTINCT_OS_PRINCIPALS_NOT_PROVEN
AUTO_CONTINUABLE = NO
```

## Checkpoint-local lineage authentication

The exact first-parent chain read was limited to eight commits:

```text
CJ a7f388523357840bd6ee57c5e4749624fcf27e63
 -> CI 7894e508f6f7f168467f1f8bbae4a020bbc9f8f1
 -> CH 606b0d1907fc4712af06fb033cf1999fe6b42105
 -> CG bccbb46a65ebc0de7a0c421e4c871b8487d3bb0c
 -> CF fbe5bb757a7f2423cb1d9706455e32479a9c3f9a
 -> CE ad644a03a54d6c12ecadc05f67eade432a3ab014
 -> CD 9154de15a4da10855b2b490a8f7eea7fddbcb5ed
 -> CC e50344417f7e5cdf5a8aa5ec20b43559feffa3ed
```

CE is preserved because it is the actual committed intermediary between CF
and CD. Omitting it would falsely collapse the lineage.

| Artifact | Commit | Git blob | Raw SHA-256 | Bytes |
|---|---|---|---|---:|
| CI | `7894e508f6f7f168467f1f8bbae4a020bbc9f8f1` | `9122a036075a4b7744162af4810a5782815228f3` | `0e92504b4c9e3416f2c9ac36d5086e0439248b41aac20190ee2834061ef58dbe` | 39394 |
| CH | `606b0d1907fc4712af06fb033cf1999fe6b42105` | `81771f1673d84ece78b0717edb99f8b4aaa2bfb6` | `d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce` | 46396 |
| CG | `bccbb46a65ebc0de7a0c421e4c871b8487d3bb0c` | `eb7fb510530a470567d87a0043a37394116935a5` | `ea02817baa1d28de78edc968d2962a116d5d9eddefbb5ab340b5d0f8de88acaa` | 39967 |
| CF | `fbe5bb757a7f2423cb1d9706455e32479a9c3f9a` | `165847c2f61be771117d93269b0cb33c3bc341af` | `cc1ddb5c428ade145977949b8b3bbc42318cd29368f7be7bdb17135084c033b0` | 41373 |
| CE | `ad644a03a54d6c12ecadc05f67eade432a3ab014` | `0fecc21ea623bd9d38a97315477d84bb782911ff` | `7de4cba5ff7aaefd1f5dcd26ea49000d411188edb02957b6d104a8ee9df706f8` | 40026 |
| CD | `9154de15a4da10855b2b490a8f7eea7fddbcb5ed` | `af571dcc903c4609dc3eda958ac1f420cf0c92aa` | `666162ed94c5b291c1694230cbdc2ea040ba2165817f3c325fe2979fe993b670` | 64845 |

```text
CHECKPOINT_LOCAL_LINEAGE_AUTHENTICATION = PASS
AUTHENTICATION_MISMATCH_COUNT = 0
FULL_G77_HISTORY_RECONSTRUCTION = NO
```

## Fixed three-principal and peer-credential contract

The following representative excerpt is exact committed CF text from
`tests/p11_da_custody_process_v1.py`; unrelated definitions are omitted:

```python
@dataclass(frozen=True, slots=True)
class FixedPrincipalBindings:
    issuance_uid: int
    caller_uid: int
    custody_uid: int

    def __post_init__(self) -> None:
        values = (self.issuance_uid, self.caller_uid, self.custody_uid)
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in values
        ):
            _fail("principal UID bindings must be non-negative integers")
        if len(set(values)) != ROLE_COUNT:
            _fail("all three P11 D-A principal UID bindings must be distinct")

    def uid_for(self, role: PrincipalRole) -> int:
        return {
            PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL: self.issuance_uid,
            PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL: self.caller_uid,
            PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL: self.custody_uid,
        }[role]
```

Kernel credential acquisition is also fixed by committed CF:

```python
def read_kernel_peer_credentials(connection: socket.socket) -> PeerCredentials:
    """Read Linux kernel-supplied peer credentials; never trust request data."""

    if not isinstance(connection, socket.socket) or connection.family != socket.AF_UNIX:
        _fail("P11 D-A custody requires a Unix-domain socket")
    raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, _PEER_CREDENTIALS.size)
    pid, uid, gid = _PEER_CREDENTIALS.unpack(raw)
    return PeerCredentials(pid=pid, uid=uid, gid=gid)
```

The verifier accepts exactly one role whose fixed UID and operation match:

```python
        matching = tuple(
            role
            for role in PrincipalRole
            if self._bindings.uid_for(role) == peer.uid
            and operation in ROLE_DESCRIPTORS[role].allowed_operations
        )
        if len(matching) != 1:
            _fail("peer is not authorized for the fixed custody operation")
        return matching[0]
```

These excerpts prove that three processes with one UID, group-only separation,
role labels and application assertions cannot satisfy the committed contract.

## Fixed endpoint and closed request surface

Committed CF fixes the local protocol and endpoint name and excludes all
custody-selection fields:

```python
FIXED_ENDPOINT_NAME = "p11_da_disposable_custody_v1.sock"
FIXED_PROTOCOL_IDENTITY = "P11_DA_DISPOSABLE_LOCAL_IPC_V1"

FORBIDDEN_REQUEST_SELECTION_FIELDS = frozenset(
    {
        "principal",
        "endpoint",
        "credential",
        "resolver",
        "store",
        "owner_state",
        "custody_path",
    }
)
```

The fixture root is a pre-bound provisioning input, not a request field:

```python
    def endpoint_under_fixture_root(self, fixture_root: Path) -> Path:
        if not isinstance(fixture_root, Path) or not fixture_root.is_absolute():
            _fail("disposable fixture root must be an absolute Path")
        return fixture_root / self.endpoint_name
```

Therefore the operator must bind one absolute fixture root in a pre-run
manifest. Neither issuance nor caller request bytes may select or replace it.

## Owner-state and one-use requirements

Committed CF permits only the following state transitions:

```python
ALLOWED_OWNER_STATE_TRANSITIONS = frozenset(
    {
        (OwnerStateName.AVAILABLE, OwnerStateName.CLAIMED),
        (OwnerStateName.AVAILABLE, OwnerStateName.REVOKED),
        (OwnerStateName.AVAILABLE, OwnerStateName.SUPERSEDED),
        (OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED),
        (OwnerStateName.CLAIMED, OwnerStateName.CONSUMED),
        (OwnerStateName.CLAIMED, OwnerStateName.RECONCILIATION_REQUIRED),
        (OwnerStateName.RECONCILIATION_REQUIRED, OwnerStateName.CONSUMED),
    }
)
```

The exact D3 transaction remains one invocation, zero retry, one output and
zero production route:

```python
        if (
            self.invocations_per_claim != 1
            or self.maximum_duration_ns != 10_000_000_000
            or self.automatic_retry_count != 0
            or self.output_record_count != 1
            or self.production_route_count != 0
        ):
            _fail("D3 transaction constants are invalid")
```

Environment provisioning supplies filesystem and process isolation only. It
does not change any owner-state transition or transaction constant.

## Minimum compliant environment requirements

The operator-provided environment must satisfy this complete conjunction
before CJ is repeated:

| Dimension | Minimum deterministic requirement | Required proof during repeated CJ |
|---|---|---|
| kernel | Linux with AF_UNIX and `SO_PEERCRED` | interpreter socket constants and live kernel credential reads |
| UID mapping | namespace UIDs `1`, `2`, `3` map to three different host kernel UIDs | `/proc/self/uid_map`; role-process `/proc/<pid>/status`; three different `id -u` values |
| GID mapping | role GIDs and one client-access GID are mapped without UID substitution | `/proc/self/gid_map`; process group captures |
| supervisor | namespace UID `0`, excluded from role bindings and every allowed operation | mismatch denials for supervisor credentials |
| process separation | one issuance process as UID `1`, one caller process as UID `2`, one custody process as UID `3` | PID/UID/GID identities and live role-operation matrix |
| checkout | exact clean commit `a7f388...` mounted/readable without write authority from role processes | HEAD/status plus mount/path permissions |
| fixture root | one operator-created absolute realpath on a private local POSIX filesystem | realpath, device, inode, owner and mode |
| endpoint directory | UID `3` owned; client-access group; mode `0750`; issuance/caller have search but no directory write | stat plus unlink/rename/replacement denial |
| AF_UNIX socket | exact CF name; UID `3` owner; client-access group; mode `0660` | stat, peer connections and fixed-path equality |
| protected store | separate UID/GID `3` directory; mode `0700`; no issuance/caller traversal or replacement | stat plus open/unlink/rename denials from UIDs `1` and `2` |
| filesystem semantics | local atomic rename/create, stable inode metadata and process-restart survival until disposal | construction-safe atomic claim/bind/exhaust observations |
| request isolation | payload cannot contain principal, endpoint, credential, resolver, store, owner-state or custody-path selectors | closed-field rejection and zero-selection-effect observations |
| network | private network namespace with no production interface/route required by the run | namespace identity and zero production routing |
| lifecycle | one supervisor with `--kill-child=SIGKILL`; no persistent namespace bind mounts or daemon | child inventory before/after teardown |
| disposal | stop processes, unlink socket, remove transient store/root, terminate namespaces and verify absence | exact removal observations and retained minimum hashes only |

The client-access GID is an ACL mechanism only. It does not identify a D-A
principal and cannot replace the three distinct UID bindings.

## Mechanism comparison

| Mechanism | D-A compatibility | Minimum conditions | Assessment |
|---|---|---|---|
| rootless user namespace | preserves one host and one kernel while creating distinct mapped UIDs | functional `newuidmap`/`newgidmap`, subordinate ranges, permitted user/net/mount/PID namespaces | `RECOMMENDED__MINIMUM` |
| rootful ephemeral container | preserves D-A if all three in-container UIDs map distinctly and AF_UNIX remains local | read-only checkout, no network, private scratch, no UID collapse, full disposal | `COMPLIANT_ALTERNATIVE` |
| disposable Linux VM | naturally supplies three accounts and full kernel isolation | clean image, no production network, exact checkpoint, deterministic destruction | `COMPLIANT_ALTERNATIVE__LARGER_SURFACE` |
| temporary locked host accounts | genuine host UIDs and direct SO_PEERCRED | privileged operator, no-login accounts, protected paths, complete account/path cleanup | `COMPLIANT_BUT_BROADER_HOST_MUTATION` |
| three processes with one UID | peer UID is identical | none can cure identity collapse | `REJECTED` |
| three groups with one UID | CF authenticates UID, not group-as-principal | group may only grant endpoint access | `REJECTED_AS_PRINCIPAL_SUBSTITUTE` |
| three role labels/application identities | request/application data is not kernel identity | prohibited by CF trust boundary | `REJECTED` |
| containers whose UIDs collapse to one host/kernel credential | SO_PEERCRED cannot prove three distinct principals at the relevant boundary | requires corrected distinct mappings | `REJECTED` |
| separate authority/custody service or new ledger | changes selected architecture/topology | prohibited | `REJECTED` |

The rootless user-namespace mechanism is minimal because it requires no host
account creation, no VM image, no permanent service and no tracked repository
change. It is compliant only after live mapping and credential proof; source
inspection or subordinate-ID configuration alone is insufficient.

## Exact minimum operator provisioning handoff

### Host prerequisites

The Human/operator must provide a Linux execution session outside the current
restricted Codex runner with all of these material facts:

```text
UNSHARE = PRESENT
NEWUIDMAP = PRESENT__FUNCTIONAL_SETUID_OR_EQUIVALENT_PRIVILEGED_HELPER
NEWGIDMAP = PRESENT__FUNCTIONAL_SETUID_OR_EQUIVALENT_PRIVILEGED_HELPER
SETPRIV = PRESENT
UNPRIVILEGED_USER_NAMESPACE = PERMITTED
SUBORDINATE_UID_COUNT = AT_LEAST_4__MAP_ROOT_HOLE_LEAVES_UIDS_1_2_3
SUBORDINATE_GID_COUNT = AT_LEAST_5__MAP_ROOT_HOLE_LEAVES_GIDS_1_2_3_4
AF_UNIX = PRESENT
SO_PEERCRED = PRESENT
PRIVATE_MOUNT_NAMESPACE = AVAILABLE
PRIVATE_PID_NAMESPACE = AVAILABLE
PRIVATE_NETWORK_NAMESPACE = AVAILABLE
CHECKOUT_HEAD = a7f388523357840bd6ee57c5e4749624fcf27e63
CHECKOUT_STATUS_SHORT = EMPTY
```

`NoNewPrivs` or an equivalent policy must not block the mapping helpers. A
configured `/etc/subuid` or `/etc/subgid` range without functional helpers is
not sufficient; CJ already demonstrated that failure mode.

### Required mapping and role binding

The resulting namespace maps must contain at least:

```text
NAMESPACE_UID_0 -> OPERATOR_HOST_UID              # non-role supervisor
NAMESPACE_UID_1 -> FIRST_DISTINCT_SUBORDINATE_UID # issuance
NAMESPACE_UID_2 -> SECOND_DISTINCT_SUBORDINATE_UID # caller
NAMESPACE_UID_3 -> THIRD_DISTINCT_SUBORDINATE_UID # custody
```

Role launch credentials are fixed before any request:

```text
ISSUANCE_PROCESS = UID_1__PRIMARY_GID_1__CLIENT_ACCESS_GID_4
CALLER_PROCESS = UID_2__PRIMARY_GID_2__CLIENT_ACCESS_GID_4
CUSTODY_PROCESS = UID_3__PRIMARY_GID_3
FIXED_PRINCIPAL_BINDINGS = issuance_uid_1__caller_uid_2__custody_uid_3
```

The supervisor creates exactly one fixture root. Within it:

```text
<fixture-root>/ipc   owner=3 group=4 mode=0750
<fixture-root>/ipc/p11_da_disposable_custody_v1.sock owner=3 group=4 mode=0660
<fixture-root>/state owner=3 group=3 mode=0700
```

The parent and `ipc` directory are not writable by UIDs `1` or `2`, so those
roles cannot unlink, rename or replace the fixed endpoint. The state directory
is not searchable by either role. Symlinked roots, shared production paths,
network filesystems with uncertain ownership/atomicity, and caller-provided
paths are rejected.

### Minimum namespace-launch command template

After the operator has supplied and independently hashed a reviewed ephemeral
commissioning entrypoint, the minimum outer launch form is:

```bash
unshare \
  --user --map-auto --map-root-user \
  --mount --propagation private \
  --pid --fork --mount-proc --kill-child=SIGKILL \
  --ipc --uts --net \
  -- /ABSOLUTE/OPERATOR_OWNED/READ_ONLY/CJ_COMMISSIONING_ENTRY
```

The single absolute path is an operator material binding, not an architectural
choice and not request data. Before execution, the handoff must record its raw
SHA-256, owner, mode and realpath. The entrypoint must mount or expose the exact
checkout read-only to role processes, create only disposable scratch paths,
bind role UIDs `1/2/3`, run only CJ P01-P12, and tear down without entering P11
or E01-E12.

Inside the namespace, role processes must be launched with kernel credentials
equivalent to these fixed forms:

```bash
setpriv --reuid=1 --regid=1 --groups=4 --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs --pdeathsig=SIGKILL -- <issuance-role-command>
setpriv --reuid=2 --regid=2 --groups=4 --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs --pdeathsig=SIGKILL -- <caller-role-command>
setpriv --reuid=3 --regid=3 --clear-groups --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs --pdeathsig=SIGKILL -- <custody-role-command>
```

The bracketed commands are CJ-owned commissioning roles, not new services and
not authorized here. They may be instantiated only in the repeated CJ
generation. CK does not create or execute them.

### Required pre-CJ handoff manifest

Before repeated CJ begins, the operator must hand over one immutable manifest
containing exactly these classes of facts:

```text
schema_identity
expected_repository_head
repository_status_short
host_kernel_identity
unshare_newuidmap_newgidmap_setpriv_identities_and_hashes
uid_map_bytes_and_hash
gid_map_bytes_and_hash
supervisor_pid_uid_gid_and_non_role_declaration
issuance_pid_uid_gid_and_role
caller_pid_uid_gid_and_role
custody_pid_uid_gid_and_role
fixture_root_realpath_device_inode_owner_mode
endpoint_parent_realpath_device_inode_owner_mode
fixed_endpoint_expected_realpath
protected_store_realpath_device_inode_owner_mode
checkout_realpath_mount_identity_and_read_only_status
network_namespace_identity_and_zero_production_route_declaration
entrypoint_realpath_owner_mode_sha256
teardown_command_identity_and_expected_absence_checks
```

The manifest contains no Human act and grants no authority. Repeated CJ must
independently verify every fact rather than trusting the declaration alone.

### Deterministic teardown contract

The operator entrypoint must register teardown before starting any role:

1. stop issuance and caller processes;
2. stop and wait for the custody process;
3. verify no role or child process remains;
4. unlink the AF_UNIX socket and verify absence;
5. dispose transient owner-state and scratch data only after binding required
   commissioning observation hashes;
6. remove endpoint/state directories and the fixture root;
7. terminate the namespace supervisor so `--kill-child=SIGKILL` closes any
   missed descendant;
8. verify there are no persistent namespace bind mounts, host accounts,
   sockets, processes or stores; and
9. retain only the G48 commissioning report and minimum immutable identities.

Teardown failure is a CJ fail-closed result. It cannot trigger repair, retry,
P11, E01-E12 or autonomous continuation.

# 3. Constitutional Self-Assessment

## Verified

- mandatory HEAD equals the requested checkpoint;
- initial worktree and index are clean;
- the committed CJ artifact authenticates byte-for-byte;
- CJ directly parents CI, and the required CI/CH/CG/CF/CE/CD lineage is exact;
- committed CJ failed at P01 because no authorized three-UID mechanism was
  available, not because D-A required redesign;
- CF already accepts three fixed distinct UIDs and kernel `SO_PEERCRED`;
- the rootless user-namespace mapping supplies three distinct inner UIDs and
  three distinct outer kernel UIDs without host-account creation;
- endpoint, store, ACL and teardown requirements can be provisioned outside
  request data and without tracked AiGOL changes;
- compliant container, VM and host-account alternatives preserve D-A only if
  they demonstrate the same fixed properties;
- all identity substitutes and parallel paths are explicitly rejected; and
- no provisioning, commissioning, P11 or E01-E12 action occurred in CK.

## Not Verified

- no operator-provided environment has yet satisfied the handoff;
- functional `newuidmap`/`newgidmap` outside the restricted runner is not yet
  demonstrated;
- no live three-UID process set was created;
- no live endpoint/store ownership or replacement denial was tested;
- no live per-operation `SO_PEERCRED` role binding was tested;
- deterministic teardown was specified but not executed;
- P01-P12 remain unexecuted in CK; and
- no operational Human Authority Act exists or was requested.

These are deliberate provisioning/commissioning gaps. They do not invalidate
the environment specification, but they keep CJ and the first evidence attempt
closed until a separate operator handoff and repeated CJ prove them.

## PROJECT_PROGRESS_ESTIMATE

```text
PROJECT_PROGRESS_ESTIMATE = NON_CERTIFIED_ORIENTATIONAL__CJ_FAILURE_AUTHENTICATED__MINIMUM_COMPLIANT_ENVIRONMENT_SPECIFIED__PROVISIONING_PENDING__CJ_REPEAT_PENDING__P11_AND_E01_E12_ZERO
```

## CONSTITUTIONAL_HEALTH_EVIDENCE

| Dimension | Evidence | Status |
|---|---|---|
| checkpoint integrity | exact commit/tree/parent/status | `PASS` |
| CJ byte integrity | Git blob plus raw SHA-256 | `PASS` |
| lineage continuity | eight checkpoint-local first-parent commits | `PASS` |
| Human semantics | three-principal D-A fixed unchanged | `PASS__ZERO_MACHINE_COMPLETION` |
| architecture preservation | CF fixed bindings/AF_UNIX/SO_PEERCRED reused | `PASS` |
| environment feasibility | rootless namespace and three alternatives specified | `PASS__CONDITIONAL_ON_LIVE_PROOF` |
| actual provisioning | prohibited and not performed | `NOT_RUN__EXPECTED` |
| actual commissioning | prohibited and not performed | `NOT_RUN__EXPECTED` |
| production isolation | no production action/path | `PASS` |
| topology | every requested new-path counter zero | `PASS` |

## SHADOW_AUTOMATION_STATE

```text
SHADOW_AUTOMATION_STATE = UNCHANGED__ISOLATED__NOT_INVOKED
SHADOW_INVOCATION_COUNT = 0
SHADOW_EVIDENCE_USED = NO
SHADOW_AUTHORITY_EFFECT = ZERO
```

## CONSTITUTIONAL_FRONTIER_DISTANCE

```text
FRONTIER_BEFORE = CJ_FAIL_CLOSED_AT_P01__COMPLIANT_THREE_UID_HOST_REQUIRED
FRONTIER_AFTER = MINIMUM_ROOTLESS_USER_NAMESPACE_HANDOFF_SPECIFIED__NOT_PROVISIONED
DISTANCE_TO_CJ_REPEAT = HUMAN_OPERATOR_PROVIDES_AND_BINDS_ONE_COMPLIANT_EPHEMERAL_ENVIRONMENT
DISTANCE_TO_P11 = CJ_PASS_12_OF_12__THEN_SEPARATE_EXACT_ONE_USE_OPERATIONAL_ACT
DISTANCE_TO_E01_E12 = NOT_ENTERED
AUTO_CONTINUABLE = NO
```

## GOVERNANCE_EFFICIENCE

```text
GOVERNANCE_EFFICIENCE = POSITIVE__EXACT_CJ_REUSE__EIGHT_COMMIT_LOCAL_LINEAGE__CF_SOURCE_REUSE__ONE_ENVIRONMENT_SPECIFICATION__ZERO_PROVISIONING__ZERO_COMMISSIONING__ONE_REPORT
GOVERNANCE_EFFICIENCY_EQUIVALENT = GOVERNANCE_EFFICIENCE
FULL_HISTORY_RECONSTRUCTION = NO
```

## COGNITION_ASSISTED_HANDOFF

```text
COGNITION_ASSISTED_HANDOFF = REQUIRED__HUMAN_OPERATOR_MUST_SUPPLY_FUNCTIONAL_MAPPING_HELPERS_SUBORDINATE_RANGES_AND_ISOLATED_NAMESPACE_ENTRYPOINT
HUMAN_SEMANTIC_DECISION_REQUIRED = NO__D_A_AND_THREE_UID_REQUIREMENT_ALREADY_FIXED
HUMAN_OR_OPERATOR_MATERIAL_ACTION_REQUIRED = YES__PRIVILEGED_OR_HOST_LEVEL_ENVIRONMENT_PROVISIONING
AUTO_CONTINUABLE = NO
```

## AIGOL_CODEX_WORK_SHARE

| Actor | Work | Constitutional semantic authority |
|---|---|---|
| Human Constitutional Authority | selected D-A and authorized bounded CJ scope | `100_PERCENT` |
| committed CF | fixed construction-only mechanics | `0_PERCENT` |
| Codex | authenticated evidence, derived environment conditions and wrote handoff | `0_PERCENT` |
| Human/operator | future host provisioning and custody of material facts | material execution authority only |

## OVERENGINEERING_RISK

```text
OVERENGINEERING_RISK = LOW_FOR_ROOTLESS_USER_NAMESPACE__MEDIUM_FOR_HOST_ACCOUNTS_OR_CONTAINER__HIGHER_FOR_VM
RISK_IF_GROUP_OR_LABEL_SUBSTITUTES_FOR_UID = CRITICAL
RISK_IF_CONTAINER_UIDS_COLLAPSE = CRITICAL
RISK_IF_ENDPOINT_PARENT_IS_ROLE_WRITABLE = CRITICAL
RISK_IF_REQUEST_SELECTS_CUSTODY = CRITICAL
RISK_IF_NEW_TRACKED_SUBSYSTEM_IS_ADDED = CRITICAL
```

## COGNITION_PROVENANCE

| Provenance | Content | Authority effect |
|---|---|---|
| `EXACT_HUMAN_AUTHORITY` | D-A, three principals and bounded CJ authorization | sole semantic authority |
| `AUTHENTICATED_GIT_EVIDENCE` | CJ/CI/CH/CG/CF/CE/CD identities and bytes | baseline identity only |
| `COMMITTED_CF_SOURCE` | bindings, AF_UNIX, SO_PEERCRED, state and D3 constants | implementation evidence only |
| `LOCAL_UTIL_LINUX_MANUAL` | exact `unshare --map-auto --map-root-user` behavior | host mechanism evidence only |
| `CODEX_CLASSIFICATION` | minimum mechanism comparison and handoff | zero authority effect |
| `MACHINE_COMPLETED_HUMAN_SEMANTICS` | none | zero |

## CANDIDATE_CAPABILITY / SHADOW_DESIGN_TARGET

```text
CANDIDATE_CAPABILITY = DISPOSABLE_P11_D_A_THREE_UID_COMMISSIONING_ENVIRONMENT
CANDIDATE_CAPABILITY_STATE = REQUIREMENTS_DEFINED__NOT_PROVISIONED__NOT_COMMISSIONED
SHADOW_DESIGN_TARGET = NONE_IN_SCOPE
PRODUCTION_CAPABILITY = NOT_CREATED
```

## CONSTITUTIONAL_CONTINUATION_PROGRESS

```text
CONSTITUTIONAL_CONTINUATION_PROGRESS = CJ_FAIL_CLOSED_AUTHENTICATED__MINIMUM_COMPLIANT_USER_NAMESPACE_REQUIREMENTS_DEFINED__ALTERNATIVES_BOUNDED__OPERATOR_HANDOFF_DEFINED__ZERO_PROVISIONING__ZERO_CJ_REPEAT__ZERO_P11_E01_E12__ONE_FRONTIER
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0
```

## PROMPT_CONTEXT_REUSE_RATIO

```text
PROMPT_CONTEXT_REUSE_RATIO = HIGH__DIRECT_CJ_AND_CHECKPOINT_LOCAL_LINEAGE_REUSE
PRIMARY_CHECKPOINT_READ_COUNT = 1
CJ_ARTIFACT_READ_COUNT = 1
CHECKPOINT_LOCAL_COMMIT_READ_COUNT = 8
FULL_G77_HISTORY_RECONSTRUCTION = NO
```

## TOKEN_BENCHMARK

Only observable telemetry is reported.

```text
CONTEXT_START_USED = NOT_EXPOSED
CONTEXT_END_USED = NOT_EXPOSED
CONTEXT_COMPACTION_COUNT = 0__OBSERVED_IN_CK_GENERATION
WALL_CLOCK_DURATION = COMPLETE_GENERATION_NOT_EXACTLY_OBSERVABLE
FILES_READ_COUNT = NOT_EXACTLY_OBSERVABLE
DOMINANT_COST_SOURCE = ENVIRONMENT_TRUST_BOUNDARY_AND_PROVISIONING_COGNITION
TOKEN_OPTIMIZATION_AFFECTED_SAFETY = NO
```

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Ponovno se uporabijo committed CF fixed role bindings, AF_UNIX and
   `SO_PEERCRED` mechanics, canonical Human Authority Act and CHE validators,
   canonical serialization, Replay and RuntimeLedger, owner-state vocabulary,
   D3 phases and zero-effect observation surfaces.

2. **Katere nove zmogljivosti nastanejo?** V CK ne nastane runtime
   zmogljivost. Nastaneta samo environment requirement specification in
   operator provisioning handoff. Future materialization bi ustvarila
   disposable namespace, tri UID contexts, en endpoint in en protected store.

3. **Ali katera obstoječa capability postane nedosegljiva?** Ne. Nobena
   obstoječa ali certificirana capability se ne spremeni.

4. **Ali je nastal vzporedni tok?** Ne. Handoff uporablja isti CF/CHE/Replay/
   RuntimeLedger tok in ne definira druge authority ali custody poti.

5. **Ali se production-path count spremeni?** Ne. Ostane nespremenjen;
   namespace ima zahtevani zero production route.

6. **Ali nastane nov authority path?** Ne. OS UID avtentikacija ne ustvarja
   Human authority. UID `0` supervisor ni role principal in je zavrnjen pri
   vseh custody operacijah.

7. **Ali nastane nov Replay/RuntimeLedger/evidence-production path?** Ne.
   Future CJ commissioning lahko uporabi le obstoječi canonical path;
   construction observations niso satisfying E01-E12 evidence.

8. **Ali CF substrate ostaja odstranljiv brez spremembe production/runtime
   jedra?** Da. Namespace, endpoint, store in procesi so transient; checkout
   ostane read-only in tracked delta ostane nič.

9. **Ali predlagani delta konvergira proti obstoječemu jedru?** Da. Dodaja le
   material OS isolation okoli committed CF in neposredno uporablja njegove
   fixed bindings ter canonical reuse adapterje.

10. **Kaj je najmanjši nujni provisioning delta?** Zagotoviti funkcionalna
    `newuidmap`/`newgidmap`, subordinate ranges, operator-owned reviewed
    entrypoint in en ephemeral `unshare --map-auto --map-root-user` environment
    z UID `1/2/3`, fixed endpoint/store ownership in deterministic teardown.

## Exact topology and execution counters

```text
TRACKED_SOURCE_MUTATION_COUNT = 0
MODIFIED_CF_PATH_COUNT = 0
MODIFIED_RUNTIME_PATH_COUNT = 0
MODIFIED_TEST_PATH_COUNT = 0
CREATED_GOVERNANCE_ARTIFACT_COUNT = 1

PRIVILEGED_PROVISIONING_COMMAND_COUNT = 0
OS_PRINCIPAL_CONTEXT_CREATED_COUNT = 0
USER_NAMESPACE_CREATED_COUNT = 0
CONTAINER_CREATED_COUNT = 0
VM_CREATED_COUNT = 0
HOST_ACCOUNT_CREATED_COUNT = 0
ENDPOINT_CREATED_COUNT = 0
PROTECTED_STORE_CREATED_COUNT = 0

CJ_COMMISSIONING_EXECUTION_COUNT = 0
P01_P12_EXECUTION_COUNT = 0
OPERATIONAL_HUMAN_AUTHORITY_ACT_CREATED_COUNT = 0
OPERATIONAL_HUMAN_AUTHORITY_ACT_CONSUMED_COUNT = 0
P11_OPERATIONAL_INVOCATION_COUNT = 0
P12_ENTRY_COUNT = 0
E01_E12_EXECUTION_COUNT = 0
SATISFYING_EVIDENCE_CREATED_COUNT = 0

NEW_AUTHORITY_PATH_COUNT = 0
NEW_PRODUCTION_PATH_COUNT = 0
NEW_PARALLEL_AUTHORITY_PATH_COUNT = 0
NEW_PARALLEL_PRODUCTION_PATH_COUNT = 0
NEW_REPLAY_RUNTIMELEDGER_PATH_COUNT = 0
NEW_EVIDENCE_PRODUCTION_PATH_COUNT = 0
NEW_PERMANENT_EVIDENCE_SUBSYSTEM_COUNT = 0
MACHINE_COMPLETED_HUMAN_SEMANTICS = 0

STAGED_FILE_COUNT = 0
COMMIT_CREATED = NO
PUSH_PERFORMED = NO
```

## Exactly one next constitutional frontier

```text
EXACT_NEXT_CONSTITUTIONAL_FRONTIER = HUMAN_OPERATOR_PROVISION_AND_BIND_ONE_EPHEMERAL_LINUX_USER_NAMESPACE_WITH_FUNCTIONAL_SUBORDINATE_UID_GID_MAPPING__THREE_DISTINCT_ROLE_UIDS__FIXED_CUSTODY_ENDPOINT__PROTECTED_STORE__READ_ONLY_EXACT_CHECKOUT__THEN_REPEAT_AUTHORIZED_CJ_P01_P12_COMMISSIONING_ONLY
FRONTIER_COUNT = 1
FRONTIER_STATUS = IDENTIFIED__NOT_ENTERED
AUTO_CONTINUABLE = NO
```

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| mandatory HEAD | exact `git rev-parse HEAD` | direct command before assessment | `PASS` |
| mandatory clean status | exact empty `git status --short` | direct command before assessment | `PASS` |
| committed CJ bytes | blob, SHA-256 and size | Git object/read-only hash audit | `PASS` |
| CJ verdict | committed exact fields | direct artifact audit | `PASS` |
| CI/CH/CG/CF/CE/CD lineage | eight first-parent commits and artifact blobs | checkpoint-local Git audit | `PASS` |
| exactly three UIDs fixed | CF `FixedPrincipalBindings` | exact source review | `PASS` |
| kernel peer identity fixed | CF `SO_PEERCRED` implementation | exact source review | `PASS` |
| request cannot select custody | closed request fields | exact source review | `PASS` |
| fixed endpoint | exact endpoint/protocol constants | exact source review | `PASS` |
| protected store requirements | owner/mode/traversal/replacement conjunction | POSIX trust-boundary assessment | `PASS` |
| atomic owner state | CF state and D3 invariants plus filesystem requirements | exact source/environment assessment | `PASS` |
| rootless user namespace feasibility | local util-linux semantics and CJ diagnosed missing helpers | mechanism comparison | `PASS` |
| container alternative | distinct non-collapsed UIDs and same SO_PEERCRED boundary required | bounded architecture assessment | `PASS` |
| VM alternative | three Linux accounts and exact isolated checkout | bounded architecture assessment | `PASS` |
| temporary host-account alternative | genuine UIDs with broader reversible host mutation | bounded architecture assessment | `PASS` |
| same-UID processes rejected | identical peer UID | trust-boundary assessment | `PASS` |
| group/label substitutes rejected | CF UID match and forbidden request identity | trust-boundary assessment | `PASS` |
| tracked source change unnecessary | committed CF accepts pre-bound UIDs/root | source/topology assessment | `PASS` |
| actual privileged provisioning | prohibited in CK | not executed | `NOT_RUN` |
| actual P01-P12 | prohibited in CK | not executed | `NOT_RUN` |
| actual P11/E01-E12 | prohibited in CK | counter audit | `NOT_RUN` |
| topology preservation | all requested counters zero | repository/scope audit | `PASS` |
| machine Human semantics | no missing value filled | provenance audit | `PASS` |
| one next frontier | one exact frontier string | deterministic count | `PASS` |

# 5. Repository Mutation Summary

Created path:

- `docs/governance/G77_256CK_P11_COMPLIANT_THREE_DISTINCT_UID_EXECUTION_ENVIRONMENT_REQUIREMENTS_AND_MINIMUM_PROVISIONING_HANDOFF_V1.md` — this report only.

Modified existing paths:

- none.

Unchanged subsystems:

- CF S1-S7 source and tests;
- canonical CHE, Human Authority Act, Replay and RuntimeLedger;
- Category C and P10;
- runtime, shadow, P11, P12 and production; and
- every prior governance artifact.

API compatibility:

- unchanged; no executable API or configuration changed.

Boundary preservation:

- no authority, production, Replay/RuntimeLedger, evidence-production or
  permanent subsystem path was created.

Unrelated pre-existing changes:

- none observed; mandatory initial status was clean.

Tests executed:

- no repository tests;
- no CF construction tests;
- no P01-P12 commissioning;
- no P11 or E01-E12 execution; and
- read-only Git, exact-source and local mechanism-documentation audits only.

Final exact `git status --short`, report line/byte count and raw SHA-256 are
reported after final byte validation because embedding a file's own hash is
self-referential.

Recommended Human commit commands, intentionally not executed:

```bash
git add -- docs/governance/G77_256CK_P11_COMPLIANT_THREE_DISTINCT_UID_EXECUTION_ENVIRONMENT_REQUIREMENTS_AND_MINIMUM_PROVISIONING_HANDOFF_V1.md
git commit -m "G77-256CK define minimum compliant P11 three-UID environment"
```

# 6. Certification Verdict

`P11_CK_MINIMUM_COMPLIANT_ENVIRONMENT_REQUIREMENTS_DEFINED__NO_D_A_ARCHITECTURE_OR_TRACKED_SOURCE_CHANGE_REQUIRED__PROVISIONING_NOT_PERFORMED`
