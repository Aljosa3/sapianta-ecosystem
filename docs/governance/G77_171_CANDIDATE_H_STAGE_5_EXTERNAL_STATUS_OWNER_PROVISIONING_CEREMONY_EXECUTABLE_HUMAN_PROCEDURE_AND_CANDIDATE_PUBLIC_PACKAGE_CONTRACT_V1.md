# 1. Implementation Summary

Generation: G77-171

Report identity:
`G77_171_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_PROVISIONING_CEREMONY_EXECUTABLE_HUMAN_PROCEDURE_AND_CANDIDATE_PUBLIC_PACKAGE_CONTRACT_V1`

Reporting date: 2026-08-12

Assessment kind:
`EXTERNAL_STATUS_OWNER_PROVISIONING_CEREMONY_EXECUTABLE_HUMAN_PROCEDURE_AND_CANDIDATE_PUBLIC_PACKAGE_CONTRACT`

Constitutional baseline: branch `master`, committed G77-170 HEAD
`6b2c742630730e2ee3fa0b82b3bb040552cb26a0`, tree
`ada643cf2798174ed7890f4eabc6cca55f81245d`, parent
`b37a0345c091f98241e7ca472af654622762393d`, subject
`G77-170 define external owner provisioning protocol`.

The parent is committed G77-169, whose HEAD is
`b37a0345c091f98241e7ca472af654622762393d`, tree
`7797e7e4ebe9253f772d774600bb1bf28a78983f`, parent
`1b807da8c357d8559c3366f9a6f5c4a442165525`, and subject
`G77-169 authorize external owner anchor provisioning`. G77-170 immediately
follows G77-169. The initial worktree was clean. G77-170 and every predecessor
were treated as immutable evidence and were not modified or repaired.

Implementation contracts: G77-171 procedure-and-contract mandate; G48-00;
G77-131 exact external owner/domain; G77-150 operation identity; G77-152
successor status version and token; G77-155 R5 authenticated exact-owner
operation-address read-back; G77-156 exact address, outcome records, and
receipt contract; G77-157 A-BA hostile obligations; G77-158 through G77-165
runtime/source/technology frontier; G77-163 one-source, pre-caller, frozen,
restart, and no-fallback binding; G77-166 D1-D4 decision boundary; G77-167
human decision support; G77-168 human constitutional D1-D4 decision; G77-169
bounded initial-anchor provisioning authority; G77-170 human external-owner
action requirement and eight-obligation protocol; committed CJ1/SHA-256; and
all unchanged Candidate H, Group SVT, Group R, Replay, CRO, CLIA, Human,
constituent, Certification, BEGIN, root, currentness, deployment, activation,
and production boundaries.

Authenticated evidence:

| Evidence | SHA-256 |
|---|---|
| G77-171 mandate | `b6f3a605a0c59374591f988027b020fdc26edb61ea32191ce84889ab56bb8378` |
| G48-00 | `16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb` |
| G77-131 | `dfa6835f7b17c678b6937958c2b941cf0a7c4e7d067377c5538bf24da7dc38f8` |
| G77-150 | `bb2d94a5c9eeb140bb9dd90c2a78ad530e1e65b43f8edbb6f5af2944f235f4b1` |
| G77-152 | `53f1d2cc6a7f70935973ca2e74146f128201665ca7fa57f9494a4b9a5c3d053b` |
| G77-155 | `57a050ba3e8bc98ff11a22b20fbfa0734ef4828964a6fed81106f2e9917b801e` |
| G77-156 | `3ccc8e6dc94c71d3a4997ea7a16e0191659989a8579f5440737cfffc6ea69c4d` |
| G77-157 | `24886bc30cceb6a90ffada0d2b96e1f7bc09731d1d7b55149c2c9ebc96f3c9ea` |
| G77-158 | `cfa4f0cabff2de801a563e5f991413e2160c5ace4c89904ed3d2a1614e257304` |
| G77-159 | `138f24bf146ae1f2cda85a76adc233d83f164cbe7fa428fc6823fb919cb9c9b2` |
| G77-160 | `f4eab37b9b51a8b955e6a96c0b8ee2658a5757e8d5ed78ca1a894adda5eda487` |
| G77-161 | `cdeeee8a7bdf3c32786af1e70c396a1417f6317ea95fde93a6ebd8611b4d12ed` |
| G77-162 | `f6d8a98f60da76fe5844d225e3a11ba659c8c517f6e594679ca6ff4899613611` |
| G77-163 | `0de27da84483b430234a4cffcbd527c0eef9141f50dc282a8f01e97660d92e8d` |
| G77-164 | `26c0ea3028445f165fbb1bc340102288cae3b48b1059fe9a9c847b9c9550e382` |
| G77-165 | `ce6e86198fdc7851fa1fd5f3346089fd720684d6826236e6cecc79ffb886d804` |
| G77-166 | `b75735ece71179ae77945baf60ba1dc0ce9a61378e0ff69581b267cf4e395783` |
| G77-167 | `70a34623eb2a27f71f0f03ccbcdbda61c43ac438d212fab8641cb93bd8c2c3ef` |
| G77-168 | `d55ad7adbda3c08a4e781c54c509001e4add984e07d4e30c6f0838b4227ba0ed` |
| G77-169 | `05b556a987b62405bdad5fa89bcbcb86c8286e967a2e960cc89ac2b380e3ea86` |
| committed G77-170 | `6af6d591cf745a668671b51c670344d6caacd2b7e3a330cff8e2c3f186b5f9ab` |
| committed CJ1 | `8442f2c84b4bb95935f6a7c38e3ff12e54a8fd154f17e1bcc0c368831e00f0a3` |

The sole G77-169-to-G77-170 mutation is the committed G77-170 governance
artifact. The `aigol/runtime`, `runtime`, `agol_bridge`, and
`sapianta_bridge` subtree identities remain unchanged at, respectively,
`bbc1e7e5b55535b7b776db0010e683397aeb3ff2`,
`7f3802a0c4f4603818617a67815e1b259e9a9c80`,
`3a2919bf6a1b9a808c5f02f95097c3ba0060b6f0`, and
`52098f1317fc123ca024feac7d8898dc949aac05`.

Informational technical sources, not constitutional authority:

- RFC 8032 defines Ed25519 signing and verification semantics;
- RFC 8410 defines Ed25519 SubjectPublicKeyInfo encoding and algorithm OID
  `1.3.101.112`; and
- OpenSSL 3.0 documentation defines `genpkey`, `pkey -pubout`, and
  `pkeyutl -rawin` EdDSA behavior. The installed inspection-only environment
  reports OpenSSL `3.0.13`; help inspection generated no material.

Objective:

Compile the G77-170 human external-owner protocol into one deterministic,
safe, human-executable procedure and one exact public candidate-package and
challenge-response contract, without executing the ceremony, creating
cryptographic material, admitting an anchor, or changing G77-165 readiness.

Assessment result:

```text
EXTERNAL_OWNER_PROVISIONING_CEREMONY_READY_FOR_HUMAN_EXECUTION
```

This is procedure readiness only. It does not assert that a key, package,
proof, D3 admission, generation-1 lineage, or independently certified anchor
exists.

G77-170 is reconstructed exactly:

```text
HUMAN_EXTERNAL_OWNER_PROVISIONING_ACTION_REQUIRED

G77_170_B01_ADMISSIBLE_EXTERNAL_OWNER_PUBLIC_VERIFICATION_MATERIAL_AND_AUTHENTICATED_PRIVATE_CONTROL_EVIDENCE_NOT_SUPPLIED
```

The eight obligations remain: generate one candidate inside the exact owner
boundary; use no SAPIANTA/repository boundary; retain every secret; return one
public candidate; supply detached private-control proof; bind all exact
identifiers; exclude prohibited material; and permit deterministic subsequent
verification. G77-171 compiles those obligations but neither satisfies nor
bypasses B01.

Technology decision:

```text
SIGNATURE_MECHANISM = ED25519_RFC8032
PUBLIC_REPRESENTATION = SUBJECT_PUBLIC_KEY_INFO_DER_RFC8410
PUBLIC_REPRESENTATION_TEXT_TRANSPORT = BASE64_RFC4648_PADDED
PUBLIC_KEY_ALGORITHM_OID = 1.3.101.112
PRIVATE_KEY_CONTAINER_FOR_PROCEDURE = ENCRYPTED_PKCS8_PEM_OWNER_LOCAL_ONLY
COMMAND_PROFILE = OPENSSL_3_X
GENERIC_CA_AUTHORITY = NONE
```

Ed25519 is the minimum single mechanism: it supplies detached challenge
signatures, has a deterministic standards-defined public-key representation,
requires no per-key public parameters, supports a stable exact identity, is
available in the inspected OpenSSL 3.x interface, permits public-only export,
supports protected software or future non-exportable owner implementations,
and requires no CA or trust service. RFC 8410 SPKI DER preserves the algorithm
identifier with the public bytes and can later be embedded in an owner-
controlled certificate without making generic CA validity the D3 authority.

The exact anchor formula is:

```text
ANCHOR_DOMAIN = UTF8("G77_171_EXTERNAL_STATUS_OWNER_ED25519_SPKI_ANCHOR_V1")
ANCHOR_PREIMAGE = ANCHOR_DOMAIN || 0x00 || EXACT_SPKI_DER_BYTES
ANCHOR_HEX = lowercase_hex(SHA256(ANCHOR_PREIMAGE))
ANCHOR_DIGEST = "sha256:" || ANCHOR_HEX
ANCHOR_IDENTITY =
  "external-status-owner-authentication-anchor-v1:" || ANCHOR_HEX
```

Only `ANCHOR_IDENTITY` is the active identity. `ANCHOR_DIGEST` is its digest
pair, not an alias or alternate anchor. Certificate fingerprints, raw-key
hashes, URLs, filenames, labels, and provider identifiers are not active
identities.

The exact challenge and package contracts are frozen in Section 2. No actual
nonce, key, signature, package, or proof is created.

Current state remains:

```text
CONCRETE_ANCHOR = ABSENT_OR_NOT_AUTHENTICATED
ANCHOR_ADMISSION_STATUS = UNADMITTED
ACTUAL_ANCHOR_LINEAGE_CARDINALITY = 0
ACTUAL_ACTIVE_ANCHOR_CARDINALITY = 0
G77_165_RERUN_READINESS = NOT_READY
```

Modified modules: none.

Created artifact: this procedure-and-contract governance artifact only.

Intentionally unchanged modules: G77-170 and every predecessor; runtime;
tests; APIs; models; serializers; validators; persistence; readers;
orchestration; TLS; keys; certificates; signatures; randomness; credentials;
endpoints; DNS; services; deployment; Candidate H; Group SVT; Group R;
Replay; CRO; CLIA; external owner state; Stage-5 effects; Human;
constituent; Certification; BEGIN; root; currentness; activation; and
production.

# 2. Code Evidence

## Public API

No runtime API, key API, proof API, reader API, client, endpoint, transport,
callback, configuration type, key store, trust store, registry, validator,
exception, Result family, constructor, class, function, method, or package
export is created or modified.

The governance-facing procedure has exactly two public-only return phases:

```text
PHASE 1:
  external-status-owner-anchor-candidate-package-v1.cj1

PHASE 2, only after a verifier returns one fresh challenge:
  external-status-owner-anchor-control-proof-v1.cj1
```

The challenge itself is verifier-created public evidence:

```text
external-status-owner-anchor-control-challenge-v1.cj1
```

No other file is part of the contract. The exact SPKI DER bytes and detached
signature bytes are transported inside CJ1 as standard RFC 4648 base64 with
required `=` padding and no whitespace. This creates one deterministic text
package, eliminates mutable public URLs and opaque sidecar files, and retains
the exact binary values.

Public package submission is not admission. The only possible progression is:

```text
candidate package
-> syntactic and secret-exclusion screening
-> verifier-created fresh challenge
-> owner detached proof
-> proof verification and owner-association evidence
-> future Human Constitutional D3 admission
-> future independent certification
```

## Orchestration Entry Point

No ceremony, key generation, challenge generation, signing, TLS, reader,
bootstrap, or runtime orchestration is executed.

### Exact human external-owner ceremony

The following commands are normative procedure text for a human operator.
They must be executed only inside an access-controlled system accountable to
the exact G77-131 external owner, outside every SAPIANTA repository,
worktree, runtime, bootstrap, Codex, developer-workstation, CI, or shared
temporary boundary. The operator must first replace the two absolute example
paths with owner-controlled paths. Neither path may be inside or beneath a Git
worktree. The return directory is public-only; the ceremony directory is
secret.

Prerequisites:

```text
OpenSSL major version 3
Python 3 standard library
owner-exclusive encrypted storage for CEREMONY_DIR
separate public-only RETURN_DIR
interactive passphrase entry over an owner-controlled console
no shell tracing, session recording, clipboard capture, or command logging
```

Environment and path gate:

```bash
set -eu
set +x
umask 077

CEREMONY_DIR='/ABSOLUTE/OWNER-CONTROLLED/SECRET-STORAGE/g77-171-generation-1'
RETURN_DIR='/ABSOLUTE/OWNER-CONTROLLED/PUBLIC-EXPORT/g77-171-generation-1'

case "$CEREMONY_DIR:$RETURN_DIR" in
  *'/home/pisarna/work/sapianta'*|*'/home/pisarna/.codex'*|*'/workspace/'*)
    echo 'PROHIBITED_PATH' >&2
    exit 1
    ;;
esac

test "${CEREMONY_DIR#/}" != "$CEREMONY_DIR"
test "${RETURN_DIR#/}" != "$RETURN_DIR"
test "$CEREMONY_DIR" != "$RETURN_DIR"

install -d -m 0700 "$CEREMONY_DIR"
install -d -m 0700 "$RETURN_DIR"

if git -C "$CEREMONY_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'CEREMONY_DIRECTORY_IS_INSIDE_GIT' >&2
  exit 1
fi
if git -C "$RETURN_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'RETURN_DIRECTORY_IS_INSIDE_GIT' >&2
  exit 1
fi

test "$(stat -c '%a' "$CEREMONY_DIR")" = '700'
test "$(openssl version | awk '{print $2}' | cut -d. -f1)" = '3'
test ! -e "$CEREMONY_DIR/owner-anchor-private.pem"
test ! -e "$RETURN_DIR/external-status-owner-anchor-candidate-package-v1.cj1"
```

The hard-coded path exclusions are a minimum guard, not proof of owner
authority. Before proceeding, the human operator must independently verify
that both resolved paths are controlled by the external owner and are outside
all repository, backup, sync, telemetry, indexing, and shared-service paths.

Generate exactly one encrypted owner-local private key and export exactly one
public SPKI DER value:

```bash
cd "$CEREMONY_DIR"
umask 077

openssl genpkey \
  -algorithm ED25519 \
  -aes-256-cbc \
  -out owner-anchor-private.pem

chmod 0600 owner-anchor-private.pem
test "$(stat -c '%a' owner-anchor-private.pem)" = '600'

openssl pkey \
  -in owner-anchor-private.pem \
  -pubout \
  -outform DER \
  -out owner-anchor-public.spki.der

openssl pkey \
  -pubin \
  -inform DER \
  -in owner-anchor-public.spki.der \
  -pubcheck \
  -noout

chmod 0400 owner-anchor-private.pem
chmod 0444 owner-anchor-public.spki.der
```

Both OpenSSL private-key reads prompt for the passphrase through the owner-
controlled console. The passphrase must not be supplied through a command
argument, environment variable, file in the return directory, repository,
shell history, or provider/API credential. The encrypted PKCS#8 PEM remains
private material despite encryption and must never leave `CEREMONY_DIR`.

Construct the exact public candidate package. This script reads public bytes
only and writes only the one public CJ1 file:

```bash
export G77_171_PUBLIC_SPKI="$CEREMONY_DIR/owner-anchor-public.spki.der"
export G77_171_PUBLIC_PACKAGE="$RETURN_DIR/external-status-owner-anchor-candidate-package-v1.cj1"

python3 - <<'PY'
import base64
import hashlib
import json
import os
from pathlib import Path

spki = Path(os.environ["G77_171_PUBLIC_SPKI"]).read_bytes()
if len(spki) != 44:
    raise SystemExit("UNEXPECTED_ED25519_SPKI_DER_LENGTH")
if spki[:12].hex() != "302a300506032b6570032100":
    raise SystemExit("NOT_STRICT_RFC8410_ED25519_SPKI_DER")

domain = b"G77_171_EXTERNAL_STATUS_OWNER_ED25519_SPKI_ANCHOR_V1"
anchor_hex = hashlib.sha256(domain + b"\x00" + spki).hexdigest()
anchor_digest = "sha256:" + anchor_hex
anchor_identity = (
    "external-status-owner-authentication-anchor-v1:" + anchor_hex
)

core = {
    "active_anchor_cardinality_after_admission": 1,
    "algorithm": "ED25519_RFC8032",
    "anchor_digest": anchor_digest,
    "anchor_generation": 1,
    "anchor_identity": anchor_identity,
    "anchor_lineage_cardinality_after_admission": 1,
    "anchor_predecessor": None,
    "artifact_type": "ExternalStatusOwnerAnchorCandidatePackageV1",
    "artifact_version": "V1",
    "ceremony_declaration": {
        "candidate_count": 1,
        "ceremony_type": "EXTERNAL_OWNER_CONTROLLED_INITIAL_ANCHOR_PROVISIONING",
        "private_key_control": "EXTERNAL_OWNER_ONLY",
        "private_key_exported": False,
        "private_material_returned": False,
        "sapianta_private_key_access": False,
    },
    "contract_version": "G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CANDIDATE_PACKAGE_V1",
    "domain_owner_identity": "external-disposition-domain-owner-v1:5555555555555555555555555555555555555555555555555555555555555555",
    "durable_terminal_history_role": "EXACT_OWNER_DURABLE_TERMINAL_HISTORY_ROLE_G77_155_G77_156",
    "extra_authority": "NONE",
    "owner_operation_address_namespace": "external-status-owner-operation-address-v1",
    "public_key_algorithm_oid": "1.3.101.112",
    "public_key_encoding": "SUBJECT_PUBLIC_KEY_INFO_DER_RFC8410",
    "public_key_spki_der_base64": base64.b64encode(spki).decode("ascii"),
    "status_linearization_contract_digest": "sha256:2cd4f630cbfc27eb31ddca9e7f7fa6f42227a4fe362cba076ad4b4d8f5ebce68",
    "status_linearization_contract_identity": "external-status-linearization-contract-v1:2cd4f630cbfc27eb31ddca9e7f7fa6f42227a4fe362cba076ad4b4d8f5ebce68",
    "verification_parameters": "NONE",
}

def cj1(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

package_digest = "sha256:" + hashlib.sha256(cj1(core)).hexdigest()
package = dict(core)
package["package_integrity_digest"] = package_digest
Path(os.environ["G77_171_PUBLIC_PACKAGE"]).write_bytes(cj1(package))
PY

chmod 0444 "$G77_171_PUBLIC_PACKAGE"
```

The restricted data types in this script are strings, integers, booleans,
null, objects, and no arrays requiring caller order; the emitted sorted,
compact UTF-8 JSON is CJ1 for this exact schema. No newline is appended.

Perform local public-only checks:

```bash
test -s "$G77_171_PUBLIC_PACKAGE"
test "$(find "$RETURN_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1
test "$(find "$RETURN_DIR" -mindepth 1 -maxdepth 1 -type f -printf '%f\n')" = \
  'external-status-owner-anchor-candidate-package-v1.cj1'

python3 -m json.tool "$G77_171_PUBLIC_PACKAGE" >/dev/null

if grep -aE -i \
  '(BEGIN[[:space:]]+(ENCRYPTED[[:space:]]+)?PRIVATE[[:space:]]+KEY|recovery_secret|passphrase|password|api[_-]?key|client[_-]?secret|device_control_credential)' \
  "$G77_171_PUBLIC_PACKAGE"; then
  echo 'PROHIBITED_SECRET_MARKER' >&2
  exit 1
fi
```

The required public declarations `private_key_control`,
`private_key_exported`, and `private_material_returned` are not secret fields;
their exact names and fail-closed values are enforced by the schema-aware
inspection defined below. The marker scan is only a first screen and cannot
establish admission or absence of encoded secrets.

Return only the one candidate CJ1 file through an authenticated public-
evidence channel. Do not return `owner-anchor-public.spki.der` separately;
its exact bytes already occur once in the package. Never return
`owner-anchor-private.pem`, its passphrase, backups, terminal transcripts, or
the ceremony directory.

### Later challenge-response procedure

After a future verifier sends the exact CJ1 challenge defined below, the
owner places that public challenge in `CEREMONY_DIR` as
`anchor-control-challenge-v1.cj1`, verifies its package identity, D3 scope,
generation, predecessor, extra-authority, nonce format, and CJ1 digest, and
creates a new empty owner-controlled public-only proof return directory that
is distinct from the phase-1 `RETURN_DIR`. The operator then runs:

```bash
cd "$CEREMONY_DIR"
umask 077

PROOF_RETURN_DIR='/ABSOLUTE/OWNER-CONTROLLED/PUBLIC-EXPORT/g77-171-generation-1-proof'
test "$PROOF_RETURN_DIR" != "$RETURN_DIR"
case "$PROOF_RETURN_DIR" in
  *'/home/pisarna/work/sapianta'*|*'/home/pisarna/.codex'*|*'/workspace/'*)
    echo 'PROHIBITED_PROOF_RETURN_PATH' >&2
    exit 1
    ;;
esac
install -d -m 0700 "$PROOF_RETURN_DIR"
if git -C "$PROOF_RETURN_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo 'PROOF_RETURN_DIRECTORY_IS_INSIDE_GIT' >&2
  exit 1
fi
test "$(find "$PROOF_RETURN_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 0

openssl pkeyutl \
  -sign \
  -rawin \
  -inkey owner-anchor-private.pem \
  -in anchor-control-challenge-v1.cj1 \
  -out anchor-control-signature.bin

chmod 0444 anchor-control-signature.bin
test "$(stat -c '%s' anchor-control-signature.bin)" -eq 64
```

The operator then uses the proof-package construction algorithm in
`Deterministic Algorithms` to embed the 64 signature bytes as padded RFC 4648
base64 in the one public proof CJ1 file. The binary signature sidecar stays
inside the ceremony directory and is not returned. After a successful public
return and backup according to owner policy, the owner should remove the
working signature sidecar and received challenge from the secret directory;
the private key remains under owner lifecycle controls.

## Semantic Reductions

### Authority and blocker reconstruction

G77-168 selects an owner-controlled public-key or certificate identity for a
remote independent owner, exact four-target D3 binding, and explicit
versioned D4 transitions. G77-169 authorizes only external-owner private
control plus future public verification. G77-170 correctly stops because no
owner package or authenticated control proof exists.

```text
G77_170_B01 remains open
G77_171 compiles procedure and bytes only
procedure readiness != ceremony execution
ceremony execution != owner association admission
control proof != D3 admission
D3 admission != independent certification
```

G77-171 does not make the current Codex environment the owner and does not
authorize Codex to execute the normative human commands.

### Technology decision assessment

| Criterion | Ed25519 + RFC 8410 SPKI DER finding |
|---|---|
| G77-168 D2 compatibility | owner-controlled public-key identity directly fits selected class |
| detached challenge proof | RFC 8032 Ed25519 signs exact challenge bytes |
| deterministic public representation | strict 44-byte RFC 8410 SPKI DER with absent parameters |
| stable equality identity | domain-separated SHA-256 over exact DER |
| mature availability | standardized RFCs and OpenSSL 3.x support |
| non-secret export | SPKI contains public key and algorithm identifier only |
| non-exportable compatibility | Ed25519 can be implemented behind owner-controlled providers/devices later; this procedure uses encrypted owner-local PKCS#8 |
| future TLS/service compatibility | Ed25519 keys can participate in RFC 8410 certificate structures; no TLS or CA authority is selected here |
| replayability | exact DER, CJ1, challenge bytes, and signature are retained |
| rotation suitability | one stable identity per explicit D4 generation |
| dependency surface | OpenSSL 3.x plus Python standard library; no CA/provider service |
| generic CA substitution | explicitly absent and prohibited |

Ed25519 is a bounded technical mechanism, not a new constitutional decision:
G77-168 already selects owner-controlled public-key/certificate identity and
G77-169 authorizes the owner to provision one. Algorithm selection changes
neither the owner nor D3 scope, D4 authority, outcome authority, currentness,
or production topology.

### Exact candidate-package contract

The candidate package has one semantic core and one derived integrity field.
Unknown, omitted, duplicate, or additional keys are prohibited.

| Core field | Exact type/value rule |
|---|---|
| `active_anchor_cardinality_after_admission` | integer `1` |
| `algorithm` | string `ED25519_RFC8032` |
| `anchor_digest` | exact derived `sha256:<64 lowercase hex>` |
| `anchor_generation` | integer `1` |
| `anchor_identity` | exact derived identity prefix plus same hex |
| `anchor_lineage_cardinality_after_admission` | integer `1` |
| `anchor_predecessor` | JSON null |
| `artifact_type` | `ExternalStatusOwnerAnchorCandidatePackageV1` |
| `artifact_version` | `V1` |
| `ceremony_declaration` | exact six-key object produced by procedure |
| `contract_version` | `G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CANDIDATE_PACKAGE_V1` |
| `domain_owner_identity` | exact G77-131 owner identity |
| `durable_terminal_history_role` | `EXACT_OWNER_DURABLE_TERMINAL_HISTORY_ROLE_G77_155_G77_156` |
| `extra_authority` | `NONE` |
| `owner_operation_address_namespace` | `external-status-owner-operation-address-v1` |
| `public_key_algorithm_oid` | `1.3.101.112` |
| `public_key_encoding` | `SUBJECT_PUBLIC_KEY_INFO_DER_RFC8410` |
| `public_key_spki_der_base64` | padded RFC 4648 base64, no whitespace; decodes to exact strict 44-byte SPKI DER |
| `status_linearization_contract_digest` | exact G77-131 digest |
| `status_linearization_contract_identity` | exact G77-131 identity |
| `verification_parameters` | `NONE` |

The derived final field is:

```text
PACKAGE_CORE_BYTES = UTF8(CJ1(core object above))
PACKAGE_INTEGRITY_DIGEST =
  "sha256:" || lowercase_hex(SHA256(PACKAGE_CORE_BYTES))
```

The final package is the core plus exact key
`package_integrity_digest = PACKAGE_INTEGRITY_DIGEST`, encoded as UTF-8 CJ1
with no BOM and no trailing newline. The integrity digest detects accidental
change; it does not prove owner origin or private control.

The package intentionally contains no challenge or signature. Those do not
exist until a verifier has screened this candidate and created a fresh
challenge. This avoids signing a reusable self-chosen statement and preserves
the verifier freshness boundary.

### Exact challenge contract

The future verifier creates one 32-byte challenge nonce using its approved
cryptographic random source. G77-171 creates no nonce. The nonce is encoded
as exactly 64 lowercase hexadecimal characters. A challenge identity may be
used once only for one candidate package and one certification attempt.

Challenge core fields:

| Field | Exact type/value rule |
|---|---|
| `anchor_digest` | exact candidate anchor digest |
| `anchor_generation` | integer `1` |
| `anchor_identity` | exact candidate anchor identity |
| `anchor_predecessor` | JSON null |
| `artifact_type` | `ExternalStatusOwnerAnchorControlChallengeV1` |
| `artifact_version` | `V1` |
| `candidate_package_integrity_digest` | exact candidate package digest |
| `challenge_nonce_hex` | exactly 64 lowercase hexadecimal characters |
| `contract_version` | `G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CONTROL_CHALLENGE_V1` |
| `domain_owner_identity` | exact G77-131 owner identity |
| `durable_terminal_history_role` | exact role token from candidate |
| `extra_authority` | `NONE` |
| `owner_operation_address_namespace` | exact G77-156 namespace prefix |
| `protocol_domain` | `G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CONTROL_CHALLENGE_V1` |
| `status_linearization_contract_digest` | exact G77-131 digest |
| `status_linearization_contract_identity` | exact G77-131 identity |

Challenge derivation:

```text
CHALLENGE_CORE_BYTES = UTF8(CJ1(challenge core))
CHALLENGE_HEX = lowercase_hex(SHA256(CHALLENGE_CORE_BYTES))
CHALLENGE_DIGEST = "sha256:" || CHALLENGE_HEX
CHALLENGE_IDENTITY =
  "external-status-owner-anchor-control-challenge-v1:" || CHALLENGE_HEX
```

The final challenge object is the core plus exact keys
`challenge_digest` and `challenge_identity`, encoded as UTF-8 CJ1 with no BOM
and no trailing newline. These exact final bytes are the Ed25519 message.

The domain token, candidate package digest, anchor pair, all four D3 targets,
generation 1, predecessor null, extra authority NONE, and fresh nonce are
therefore cryptographically bound by the detached signature. A timestamp,
hostname, endpoint, filename, caller identity, or mutable registry is neither
required nor authoritative.

### Exact proof-package contract

After signing the exact final challenge bytes, the owner constructs a proof
core with these fields:

| Field | Exact type/value rule |
|---|---|
| `algorithm` | `ED25519_RFC8032` |
| `anchor_digest` | exact candidate anchor digest |
| `anchor_identity` | exact candidate anchor identity |
| `artifact_type` | `ExternalStatusOwnerAnchorControlProofV1` |
| `artifact_version` | `V1` |
| `candidate_package_integrity_digest` | exact candidate package digest |
| `challenge_digest` | exact challenge digest |
| `challenge_identity` | exact challenge identity |
| `contract_version` | `G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CONTROL_PROOF_V1` |
| `detached_signature_base64` | padded RFC 4648 base64 of exactly 64 signature bytes, no whitespace |
| `signature_encoding` | `BASE64_RFC4648_PADDED` |

Proof derivation:

```text
PROOF_CORE_BYTES = UTF8(CJ1(proof core))
PROOF_INTEGRITY_DIGEST =
  "sha256:" || lowercase_hex(SHA256(PROOF_CORE_BYTES))
```

The final proof object is the core plus
`proof_integrity_digest = PROOF_INTEGRITY_DIGEST`, encoded as UTF-8 CJ1 with
no BOM and no newline. The verifier decodes the public SPKI and detached
signature and verifies:

```bash
openssl pkeyutl \
  -verify \
  -rawin \
  -pubin \
  -keyform DER \
  -inkey candidate-public.spki.der \
  -in external-status-owner-anchor-control-challenge-v1.cj1 \
  -sigfile candidate-signature.bin
```

This command is future public verification, not executed in G77-171. A valid
signature proves control of the corresponding private capability for the
exact challenge. It does not by itself prove that the controller is the exact
G77-131 owner; ceremony authentication and Human Constitutional admission
remain mandatory.

### Anchor identity and comparison rule

The public SPKI parser must accept exactly:

```text
DER length = 44 bytes
hex prefix = 302a300506032b6570032100
algorithm OID = 1.3.101.112
AlgorithmIdentifier parameters = absent
subjectPublicKey BIT STRING unused bits = 0
public key payload length = 32 bytes
no trailing bytes
```

Canonical comparison is byte equality of the decoded exact SPKI DER plus
string equality of the recomputed identity/digest pair. Re-encoded PEM,
certificate fingerprints, raw 32-byte keys, JWK thumbprints, provider labels,
or equivalent mathematical points are not accepted as alternate active
identities. A future certificate may authenticate a service using this key,
but generic certificate or CA validity cannot replace the admitted SPKI DER
identity and exact D3 binding.

### Secret-handling and deterministic screening

The public return directory may contain only the expected CJ1 filename for
the current phase. Before any copy into governance evidence, a verifier must:

1. enumerate every directory entry without following symlinks;
2. reject directories, devices, sockets, links, archives, keystores, or
   unexpected binary/opaque files;
3. enforce exact filename and regular-file type;
4. parse strict UTF-8 JSON and reject duplicate/unknown/missing fields;
5. require byte equality with re-encoded CJ1;
6. reject PEM private-key markers and known secret/container field names;
7. decode only the declared base64 public/signature field with strict
   validation;
8. enforce exact SPKI/signature length and structure;
9. recompute every digest and identity; and
10. require independent ceremony/authority certification.

The schema-aware forbidden key-name set is:

```text
private_key
privateKey
d
p
q
dp
dq
qi
oth
seed
recovery_secret
private_backup
private_wrap
passphrase
password
pin
api_key
client_secret
device_control_credential
```

Private JWK parameters `d`, RSA private parameters, encrypted PKCS#8/PEM,
PKCS#12, JKS, seed/recovery data, credentials, and device-control material are
prohibited even if encrypted or base64-encoded. Allowed base64 fields decode
only to strict 44-byte Ed25519 SPKI DER in phase 1 or strict 64-byte Ed25519
signature in phase 2. Any additional base64 or opaque field fails closed.

Text scanning alone cannot prove absence of secrets or owner authority. It is
a syntactic screen followed by strict decoding, semantic field constraints,
digest verification, ceremony evidence, and independent certification.

### D3/D4 preparation

The candidate, challenge, and proof contracts preserve:

```text
generation = 1
predecessor = NONE/null
lineage cardinality after admission = 1
active anchor cardinality after admission = 1
extra authority = NONE
```

They bind the exact G77-131 owner, exact G77-131 contract pair, exact G77-156
address namespace, and exact durable terminal-history role. The package is a
proposal; it does not perform concrete D3 admission or create D4 generation
1. The actual cardinalities remain zero until future Human admission and
independent certification.

No mutable latest lookup, fallback key, alternate candidate, simultaneous
identity representation, second lineage, or owner replacement is admitted.

### Independent certification preparation

A subsequent certification generation must independently:

| Certification requirement | Exact validation |
|---|---|
| parsing | strict filename, UTF-8, CJ1, schema, type, and no unknown fields |
| public representation | decode padded base64; strict 44-byte RFC 8410 Ed25519 SPKI DER |
| anchor identity | recompute domain-separated SHA-256 pair exactly |
| package integrity | recompute SHA-256 over exact CJ1 core |
| challenge freshness | verify 32-byte verifier nonce was generated for this attempt and never used before |
| challenge binding | recompute identity and compare package, anchor, D3, generation, predecessor, and extra-authority fields |
| private control | verify 64-byte Ed25519 signature over exact final challenge CJ1 bytes |
| ceremony declaration | authenticate the ceremony record independently of its self-declaration |
| exact owner association | obtain Human Constitutional admission that the proven controller is the exact G77-131 owner |
| D3 scope | equality of all four targets and extra authority NONE |
| D4 initial state | generation 1, predecessor NONE, one proposed lineage, one proposed active anchor |
| secret exclusion | strict allowlist, schema, marker, decoded-length, container, and provenance inspection |
| replayability | retain exact candidate, challenge, proof, identity formulas, and certification evidence |
| no fallback | verify no alternate key, URL, registry, discovery, or fallback field/path |
| authority conservation | key authenticates existing owner; no second owner/outcome authority |

Certification must reject if the operator's ceremony declaration is the only
owner-association evidence. It must independently authenticate the ceremony
as controlled by the exact external owner. Successful signature verification
alone proves key control, not constitutional owner identity.

### Hostile-case matrix

| Hostile case | Required result | Exact reason |
|---|---|---|
| operator runs ceremony inside repository | `FAIL_CLOSED` | repository is outside owner private boundary |
| Codex executes key generation | `FAIL_CLOSED` | Codex has no owner private authority |
| SAPIANTA executes key generation | `FAIL_CLOSED` | creates prohibited SAPIANTA proof authority |
| private key copied into candidate package | `FAIL_CLOSED` | public-only package and owner secrecy fail |
| encrypted private key treated as safe public evidence | `FAIL_CLOSED` | encryption does not make private material public |
| private JWK submitted | `FAIL_CLOSED` | private parameter `d` and related fields are prohibited |
| generic provider credential submitted | `FAIL_CLOSED` | access credential is not public anchor evidence |
| Human Founder key reused | `FAIL_CLOSED` | different owner, authority role, and scope |
| multiple public candidates submitted | `FAIL_CLOSED` | exact candidate cardinality must equal one |
| ambiguous public encoding | `FAIL_CLOSED` | only strict RFC 8410 SPKI DER is accepted |
| unsupported algorithm | `FAIL_CLOSED` | exact mechanism is Ed25519 RFC 8032 only |
| mutable external URL replaces exact bytes | `FAIL_CLOSED` | replay and equality require embedded exact DER |
| generic CA trust substitutes for D3 | `FAIL_CLOSED` | CA validity is not exact owner/scope admission |
| self-signed declaration treated as owner association | `FAIL_CLOSED` | proof control and constitutional association are separate |
| challenge omits or changes D3 scope | `FAIL_CLOSED` | signature must bind all four exact targets |
| reused or stale challenge accepted | `FAIL_CLOSED` | nonce/challenge identity is single-use per attempt |
| generation differs from 1 | `FAIL_CLOSED` | initial D4 generation is exact |
| predecessor differs from NONE/null | `FAIL_CLOSED` | initial anchor has no predecessor |
| extra authority differs from NONE | `FAIL_CLOSED` | D3 cannot grant broader authority |
| fallback key included | `FAIL_CLOSED` | one active candidate and no fallback are mandatory |
| latest-key lookup introduced | `FAIL_CLOSED` | mutable discovery violates explicit D4 lineage |

### G77-165 readiness

No human ceremony was executed and no owner package or proof was returned.
Therefore:

```text
PROVISIONING_PROCEDURE_READINESS = READY_FOR_HUMAN_EXECUTION
PROVISIONING_EXECUTION_STATUS = NOT_EXECUTED
ANCHOR_ADMISSION_STATUS = UNADMITTED
D3_ADMISSION_STATUS = UNADMITTED
D4_GENERATION_1_STATUS = NOT_INITIALIZED
INDEPENDENT_CERTIFICATION_STATUS = NOT_RUN__NO_CANDIDATE
G77_165_RERUN_READINESS = NOT_READY
G77_165_RERUN_EXECUTED = false
```

## Public Validators

No public validator is implemented. The exact future verifier contract is
fully specified, but G77-171 has no candidate bytes on which to execute it.

Reusable certified mechanics are bounded to CJ1, SHA-256, UTF-8, strict
schema, identity/digest equality, generation, pair, and predecessor checks.
OpenSSL supplies the future public cryptographic parse and Ed25519 verification
mechanics; it does not supply constitutional owner or D3 authority.

Future validation order is fail closed:

```text
allowlisted regular file
-> strict UTF-8 and JSON parse with duplicate rejection
-> exact schema and types
-> exact CJ1 byte equality
-> secret/container screen
-> strict padded base64 decode
-> strict RFC 8410 SPKI structure
-> anchor pair recomputation
-> package integrity recomputation
-> challenge identity/freshness/scope recomputation
-> proof integrity recomputation
-> Ed25519 detached signature verification
-> external ceremony authentication
-> Human owner/D3 admission
-> independent certification
```

Any failure stops admission. No post-state resemblance, TLS success, generic
certificate validation, hostname, location, possession, or configuration can
repair a failed step.

## Canonical Data Models

G77-171 freezes a governance return-package contract, not a runtime canonical
family. It creates no model, schema registry entry, canonical evidence family,
Result family, key object, certificate object, D3 admission object, or D4
lineage object.

```text
FUTURE_ANCHOR_AND_D3_BINDING_EVIDENCE_CLASS =
  A_EXISTING_GOVERNANCE_ARTIFACT_ONLY

NEW_CANONICAL_EVIDENCE_FAMILY_COUNT = 0
NEW_RESULT_FAMILY_COUNT = 0
DUPLICATE_ACTIVE_ANCHOR_IDENTITY_COUNT = 0
```

The candidate, challenge, and proof schemas are exact non-secret evidence
contracts for a future governance artifact. Their existence as prose does not
materialize an instance. Only the SPKI-derived `ANCHOR_IDENTITY` is the future
active anchor identity; its digest is the paired integrity value.

Actual material counts remain:

```text
PRIVATE_KEY_MATERIAL_CREATED_OR_RECEIVED_COUNT = 0
RANDOMNESS_GENERATED_COUNT = 0
PUBLIC_VERIFICATION_MATERIAL_RECEIVED_COUNT = 0
SIGNATURE_CREATED_OR_RECEIVED_COUNT = 0
CANDIDATE_PACKAGE_INSTANCE_COUNT = 0
CHALLENGE_INSTANCE_COUNT = 0
PROOF_PACKAGE_INSTANCE_COUNT = 0
ADMITTED_ANCHOR_COUNT = 0
ANCHOR_LINEAGE_COUNT = 0
ACTIVE_ANCHOR_COUNT = 0
```

## Deterministic Algorithms

Executed G77-171 gate:

```text
authenticate branch, HEAD, tree, parent, subject, and clean worktree
-> verify committed G77-170 immediately follows committed G77-169
-> authenticate mandate, G48, G77-131, G77-150, G77-152, G77-155 through
   G77-170, and committed CJ1 hashes
-> reconstruct G77-168 D1-D4
-> reconstruct G77-169 external-owner-only provisioning authority
-> reconstruct G77-170 B01 and eight obligations
-> verify no concrete anchor or private material appeared
-> verify G77-165 remains NOT_READY
-> compare one minimum technical mechanism against required responsibility
-> select Ed25519 plus exact RFC 8410 SPKI DER public representation
-> freeze one anchor identity/digest formula
-> freeze one CJ1 candidate package
-> freeze one future verifier-created CJ1 challenge
-> freeze one CJ1 detached-proof package
-> define owner-only commands and deterministic secret screening
-> define subsequent independent certification obligations
-> STOP before ceremony, randomness, key, signature, admission, or rerun
```

Exact proof-package construction after a real challenge, executed inside the
owner ceremony boundary after the OpenSSL signing command:

```bash
export G77_171_CHALLENGE="$CEREMONY_DIR/anchor-control-challenge-v1.cj1"
export G77_171_SIGNATURE="$CEREMONY_DIR/anchor-control-signature.bin"
export G77_171_PROOF="$PROOF_RETURN_DIR/external-status-owner-anchor-control-proof-v1.cj1"

python3 - <<'PY'
import base64
import hashlib
import json
import os
from pathlib import Path

def no_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_JSON_KEY")
        value[key] = item
    return value

def cj1(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

challenge_bytes = Path(os.environ["G77_171_CHALLENGE"]).read_bytes()
challenge = json.loads(
    challenge_bytes.decode("utf-8"),
    object_pairs_hook=no_duplicates,
)
if cj1(challenge) != challenge_bytes:
    raise SystemExit("CHALLENGE_NOT_EXACT_CJ1")

signature = Path(os.environ["G77_171_SIGNATURE"]).read_bytes()
if len(signature) != 64:
    raise SystemExit("INVALID_ED25519_SIGNATURE_LENGTH")

proof_core = {
    "algorithm": "ED25519_RFC8032",
    "anchor_digest": challenge["anchor_digest"],
    "anchor_identity": challenge["anchor_identity"],
    "artifact_type": "ExternalStatusOwnerAnchorControlProofV1",
    "artifact_version": "V1",
    "candidate_package_integrity_digest": challenge["candidate_package_integrity_digest"],
    "challenge_digest": challenge["challenge_digest"],
    "challenge_identity": challenge["challenge_identity"],
    "contract_version": "G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CONTROL_PROOF_V1",
    "detached_signature_base64": base64.b64encode(signature).decode("ascii"),
    "signature_encoding": "BASE64_RFC4648_PADDED",
}
proof_digest = "sha256:" + hashlib.sha256(cj1(proof_core)).hexdigest()
proof = dict(proof_core)
proof["proof_integrity_digest"] = proof_digest
Path(os.environ["G77_171_PROOF"]).write_bytes(cj1(proof))
PY

chmod 0444 "$G77_171_PROOF"
test "$(find "$PROOF_RETURN_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1
test "$(find "$PROOF_RETURN_DIR" -mindepth 1 -maxdepth 1 -type f -printf '%f\n')" = \
  'external-status-owner-anchor-control-proof-v1.cj1'
```

This algorithm is not executed in G77-171. The future implementation must
use the committed CJ1 serializer or independently demonstrate exact byte
equivalence; pseudocode cannot override CJ1.

## Responsibility Boundaries

- exact G77-131 external owner: sole outcome authority and sole permitted
  controller/operator of the human private-key ceremony;
- human external-owner operator: executes the commands only inside the
  authenticated owner boundary and returns public-only evidence;
- G77-171 procedure: deterministic mechanics and schemas only, with no
  private, owner, admission, or production authority;
- future verifier: creates a fresh challenge and mechanically verifies public
  bytes and proof, without acquiring owner authority;
- Human Constitutional Authority: later admits the authenticated controller-
  to-owner relationship and exact D3 scope, but does not control the key;
- independent Certification: later verifies exact bytes, proof, ceremony,
  scope, initial lineage, secret exclusion, replay, and authority conservation;
- SAPIANTA bootstrap/runtime: future admitted-public verification only, never
  ceremony execution, selection, trust creation, rotation, or fallback;
- Codex/developer/repository/Git: procedure authorship only, never owner
  private authority;
- caller: exact operation-address query input only, never anchor input;
- generic CA/provider/registry/environment: no exact owner authority;
- external owner history: sole durable terminal-outcome evidence source;
- external vector pointer/history: sole currentness source; and
- Human, constituent, BEGIN, root, deployment, activation, production,
  Replay, CRO, and CLIA boundaries: unchanged.

Actual G77-171 topology:

```text
NEW_BOUNDED_RUNTIME_CAPABILITY_COUNT = 0
NEW_READER_PATH_COUNT = 0
NEW_AUTHORITY_COUNT = 0
NEW_CRYPTO_AUTHORITY_COUNT = 0
NEW_OUTCOME_AUTHORITY_COUNT = 0
NEW_PERSISTENCE_FAMILY_COUNT = 0
NEW_VALIDATOR_FAMILY_COUNT = 0
NEW_RESULT_FAMILY_COUNT = 0
NEW_CURRENTNESS_SOURCE_COUNT = 0
NEW_CANONICAL_EVIDENCE_FAMILY_COUNT = 0

NEW_CRYPTOGRAPHIC_MECHANICS_MATERIALIZED_COUNT = 0
NEW_PROCEDURE_CONTRACT_COUNT = 1

AUTHORITY_PATHS = 1 -> 1
PRODUCTION_PATHS = 1 -> 1
PARALLEL_PATHS = 0 -> 0
```

# 3. Constitutional Self-Assessment

## Verified

- committed G77-170 HEAD/tree/parent/subject, its immediate G77-169 lineage,
  clean initial worktree, mandate hash, controlling predecessor hashes, and
  committed CJ1 hash were authenticated;
- G77-168 D1-D4, G77-169 authority, G77-170 B01, and the eight-obligation
  human protocol were reconstructed without reinterpretation;
- no admitted concrete anchor, private material, key/certificate file, or
  executable TLS verification path appeared;
- G77-165 remains `NOT_READY`;
- Ed25519 plus strict RFC 8410 SPKI DER was selected as one bounded mechanism
  without CA, provider, alias, owner, D3, or outcome-authority creation;
- exact OpenSSL 3.x owner-only commands, secret paths, permissions, public
  export, return files, and later signing procedure were defined;
- one exact public candidate package, verifier challenge, proof package,
  anchor identity formula, integrity formulas, and comparison rule were
  frozen;
- challenge bytes bind the candidate, anchor, exact D3 scope, generation 1,
  predecessor NONE, extra authority NONE, and a future fresh nonce;
- deterministic schema-aware secret screening and independent certification
  obligations were defined;
- all required hostile cases fail closed;
- no ceremony, randomness, key, certificate, signature, challenge, package,
  anchor, D3 admission, lineage, certification, runtime, or rerun was created;
- all authority, topology, currentness, persistence, canonical-family, and
  Result-family counts remain conserved; and
- all G77-170 observations were retained without promotion.

## Not Verified

- the human ceremony has not been executed inside an authenticated external-
  owner-controlled boundary;
- no OpenSSL command in the normative procedure has been run against real
  owner material;
- no private/public key relationship, public candidate package, verifier
  challenge, detached signature, or proof package exists;
- no owner-control proof, ceremony authentication, controller-to-owner
  association, Human D3 admission, D4 generation-1 lineage, or independent
  certification has been verified;
- secret screening has not been exercised against a returned package and
  cannot establish secret absence or authority from prose alone;
- hardware/non-exportable provider behavior, live rotation, revocation,
  expiry, compromise, TLS, reader, bootstrap, concurrency, deployment, and
  production behavior remain unexercised;
- G77-170 B01 remains open, anchor status remains `UNADMITTED`, and G77-165
  rerun readiness remains `NOT_READY`; and
- Group R implementation, Stage-5 effects, activation, BEGIN, and root
  mutation remain outside scope and unverified.

## Constitutional Health Evidence

| Dimension | Evidence | Status |
|---|---|---|
| baseline authenticity | committed HEAD/tree/parent/subject and hashes | `PASS` |
| predecessor immutability | sole new untracked G77-171 artifact | `PASS` |
| G77-170 boundary preservation | procedure only; blocker remains open | `PASS` |
| owner authority uniqueness | exact G77-131 owner remains sole outcome authority | `PASS` |
| private-key authority separation | owner-only commands and secret directory | `PASS_SEMANTIC` |
| technology-selection boundedness | one Ed25519/SPKI mechanism, no CA/provider authority | `PASS` |
| public representation determinism | strict 44-byte RFC 8410 DER | `PASS_CONTRACT` |
| anchor identity determinism | exact domain-separated SHA-256 formula | `PASS_CONTRACT` |
| challenge determinism | exact CJ1 core/full formula plus future fresh nonce | `PASS_CONTRACT` |
| candidate-package determinism | exact CJ1 schema and digest | `PASS_CONTRACT` |
| D3 scope preservation | all four exact targets plus extra authority NONE | `PASS` |
| D4 generation-1 preservation | generation 1/predecessor NONE/cardinalities one | `PASS` |
| secret exclusion | deterministic screen defined; no material created | `PASS_SCOPE` |
| bootstrap separation | no bootstrap selection/trust mechanics | `PASS` |
| caller separation | no caller anchor input | `PASS` |
| crypto-authority conservation | zero new crypto authority | `PASS` |
| outcome-authority conservation | zero new; one existing owner | `PASS` |
| currentness conservation | external vector history remains sole source | `PASS` |
| persistence conservation | no persistence family | `PASS` |
| canonical-family conservation | existing governance evidence only | `PASS` |
| Result-family conservation | no Result family | `PASS` |
| no-fallback preservation | one candidate, no URL/latest/fallback | `PASS` |
| topology stability | 1->1 / 1->1 / 0->0 | `PASS` |
| provisioning procedure readiness | exact commands and contracts | `PASS` |
| anchor admission status | no candidate returned | `BLOCKED` |
| G77-165 rerun readiness | correctly remains not ready | `PASS_BOUNDARY` |
| runtime implementation state | absent as required | `PASS_SCOPE` |

## Reuse Impact Assessment

1. **Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?**
   Ponovno se uporabijo G77-131 exact owner in contract pair, G77-150
   operation identity, G77-152 version/token dokazila, G77-155/G77-156 exact-
   address in durable-history pogodba, G77-163 source-binding meje, G77-168
   D1-D4 odločitev, G77-169 provisioning authority, G77-170 human protocol,
   CJ1/SHA-256 ter identity/digest, equality, generation in predecessor
   mehanizmi. Ed25519/RFC 8410/OpenSSL se uporabijo samo kot bounded external
   ceremony mechanics, ne kot nova ustavna avtoriteta.
2. **Katere nove zmogljivosti (če sploh) nastanejo?** Nastane en governance
   procedure/package contract. Nobena runtime ali kriptografska zmogljivost,
   ključ, anchor, validator, reader ali servis ne nastane.
3. **Ali katera obstoječa zmogljivost postane nedosegljiva?** Ne. Vsi
   certificirani artefakti, zgodovina, poizvedbe in produkcijski porabniki
   ostanejo dosegljivi in nespremenjeni.
4. **Ali implementacija ustvarja vzporedni tok?** Ne;
   `PARALLEL_PATHS = 0 -> 0`.
5. **Ali zmanjšuje ali povečuje število produkcijskih poti?** Ne;
   `PRODUCTION_PATHS = 1 -> 1`.

## Pattern Learning Evidence

| Candidate observation | G77-171 evidence | Promotion |
|---|---|---|
| `AUTHORITY_BEARING_RUNTIME_SOURCE_DISCOVERY_AND_REUSE_CLASSIFICATION` | procedure keeps runtime source absent | none |
| `PRE_IMPLEMENTATION_TRANSITIVE_CONSTITUTIONAL_DEPENDENCY_FRONTIER_ANALYSIS` | frontier is compiled into a public-only return contract | none |
| `NONCANONICAL_AUTHORITY_OBSERVATION_CAPABILITY_PATTERN` | proof verification remains observational | none |
| `AUTHORITY_BINDING_WITHOUT_AUTHORITY_DELEGATION` | D3 package fields do not delegate owner authority | none |
| `READ_PATH_VS_AUTHORITY_PATH_SEPARATION` | no reader path is created | none |
| `CONSTITUTIONAL_DEPENDENCY_BINDING_PATTERN` | challenge binds four exact predecessor targets | none |
| `TECHNOLOGY_FRONTIER_DETECTION` | one bounded technical choice closes procedure ambiguity | none |
| `PROVENANCE_MECHANISM_VS_AUTHORITY_SEPARATION` | Ed25519 proof is not owner admission | none |
| `CONSTITUTIONAL_DECISION_BOUNDARY_DETECTION` | technology remains within prior public-key class | none |
| `EXTERNAL_FACT_VS_IMPLEMENTATION_FACT_SEPARATION` | real owner ceremony remains external | none |
| `AUTHENTICATION_ANCHOR_LIFECYCLE_PATTERN` | generation-1 fields prepare but do not create lineage | none |
| `FUTURE_EXTERNAL_AUTHORITY_BINDING_GENERALIZATION_CANDIDATE` | scope remains External Status Owner | none |
| `PRIVATE_AUTHORITY_VS_PUBLIC_VERIFICATION_SEPARATION` | encrypted private file never enters public package | none |
| `INITIAL_TRUST_ANCHOR_BOOTSTRAP_PATTERN` | bootstrap remains downstream of admission | none |
| `AUTHENTICATED_AUTHORITY_TRANSITION_PATTERN` | predecessor NONE is exact only for initial generation | none |
| `EXTERNAL_OWNER_PROVISIONING_CEREMONY_PATTERN` | owner-only command procedure is deterministic | none |
| `PUBLIC_ANCHOR_ADMISSION_PATTERN` | candidate/proof remain pre-admission evidence | none |
| `PRIVATE_CONTROL_PROOF_WITHOUT_SECRET_DISCLOSURE_PATTERN` | detached Ed25519 proof returns no private key | none |
| `GENERATION_ZERO_TO_ONE_TRUST_INITIALIZATION_PATTERN` | contract prepares transition from zero to admitted generation 1 | none |
| `EXTERNAL_AUTHORITY_HUMAN_CEREMONY_COMPILATION_PATTERN` | eight obligations compiled into commands and checks | none |
| `PUBLIC_ONLY_AUTHORITY_RETURN_PACKAGE_PATTERN` | exactly one CJ1 file per return phase | none |
| `CHALLENGE_BOUND_SCOPE_PROOF_PATTERN` | signed challenge binds anchor, D3, D4, and nonce | none |
| `SECRET_EXCLUSION_GATE_PATTERN` | allowlist, strict schema, decoding, and certification are layered | none |

`PATTERN_DETECTED != CONSTITUTION_CHANGED`. No pattern is implemented,
promoted, activated, generalized beyond External Status Owner, or granted
authority.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| committed G77-170 baseline | branch/HEAD/tree/parent/subject and clean status | Git authentication | PASS |
| immediate G77-169 lineage | G77-170 parent equals G77-169 HEAD | Git lineage comparison | PASS |
| mandate and controlling evidence | SHA-256 table | hash recomputation | PASS |
| G77-170 blocker reconstruction | exact B01 and human state | predecessor review | PASS |
| G77-170 eight obligations | exact protocol compilation | completeness review | PASS |
| concrete-anchor absence | no key/certificate/material/binding appeared | repository search | PASS |
| private-material absence | extension, marker, and repository scan | secret scan | PASS |
| G77-165 readiness baseline | committed `NOT_READY` and no package | predecessor review | PASS |
| technology selection | Ed25519/RFC 8410/OpenSSL against criteria | bounded technical review | PASS |
| human ceremony procedure | exact path, permission, generation, export, and return steps | procedure audit | PASS |
| public candidate package | exact core, derived digest, and CJ1 encoding | schema/formula audit | PASS |
| challenge contract | exact scope, nonce, identity, and signed bytes | formula audit | PASS |
| anchor identity | exact domain-separated SHA-256 over SPKI DER | recomputation design review | PASS |
| proof package | exact signature and integrity schema | schema/formula audit | PASS |
| secret handling | encrypted owner-local key and no-return boundary | boundary audit | PASS |
| secret screening | layered allowlist/schema/decode/certification procedure | hostile review | PASS |
| D3 preparation | exact four targets plus extra authority NONE | scope audit | PASS |
| D4 preparation | generation 1/predecessor NONE/cardinalities one | lineage audit | PASS |
| independent certification preparation | complete 15-row obligation matrix | certification readiness review | PASS |
| hostile cases | complete 21-row matrix | deterministic hostile audit | PASS |
| ceremony execution | explicitly prohibited in G77-171 | scope review | NOT_APPLICABLE |
| key/certificate/signature generation | explicitly prohibited in G77-171 | scope review | NOT_APPLICABLE |
| anchor admission/certification | no returned candidate exists | admission assessment | BLOCKED |
| G77-165 rerun | prohibited and remains not ready | scope review | NOT_APPLICABLE |
| runtime/TLS/reader/deployment | prohibited in G77-171 | scope review | NOT_APPLICABLE |
| crypto/outcome/currentness authority | all new counts zero | authority inventory | PASS |
| persistence/validator/Result/canonical families | all new counts zero | capability inventory | PASS |
| topology | authority 1->1; production 1->1; parallel 0->0 | topology audit | PASS |
| pattern promotion | prohibited and absent | pattern review | PASS |
| G48 exact structure | six top-level sections and seven Code Evidence subsections | structural validation | PASS |
| whitespace integrity | sole new artifact | diff and whitespace checks | PASS |
| exact mutation inventory | final Git status | one-file validation | PASS |
| verdict uniqueness/finality | Section 6 | token count/final-content check | PASS |

The sole `BLOCKED` result concerns concrete admission, which is outside the
successful procedure-readiness state and declared under `Not Verified`. The
`NOT_APPLICABLE` rows are explicit mutation prohibitions, not skipped
procedure work.

# 5. Repository Mutation Summary

Modified files:

- CREATE
  `docs/governance/G77_171_CANDIDATE_H_STAGE_5_EXTERNAL_STATUS_OWNER_PROVISIONING_CEREMONY_EXECUTABLE_HUMAN_PROCEDURE_AND_CANDIDATE_PUBLIC_PACKAGE_CONTRACT_V1.md`
  — this deterministic external-owner human ceremony procedure and public
  candidate/challenge/proof package contract only.

No file is modified, deleted, or renamed. All predecessors remain unchanged.

Unchanged subsystems:

- G77-170 and every predecessor governance artifact;
- runtime APIs, models, CJ1, serializers, validators, persistence, readers,
  authentication, queries, package exports, and orchestration;
- keys, certificates, signatures, randomness, private secrets, credentials,
  TLS, endpoints, DNS, services, deployment, and production;
- Group SVT and Group R models, bytes, contracts, implementation, and tests;
- Replay, CRO, CLIA, Human, constituent, Certification, BEGIN, root,
  activation, and currentness authority.

API compatibility:

- unchanged; no runtime or public API is added or modified.

Boundary preservation:

- normative commands are human-executed only outside SAPIANTA under exact
  external-owner control;
- no command in the procedure was executed by Codex;
- no key, certificate, signature, randomness, challenge, package, credential,
  or private material was generated, received, printed, or stored;
- the future private key never leaves the owner boundary;
- the public contract embeds one exact SPKI DER identity and no alternate,
  fallback, URL, registry, provider, certificate, or CA authority;
- candidate/proof evidence cannot self-admit owner identity or D3 scope;
- the exact external owner remains the sole outcome authority;
- external vector history remains the sole currentness source; and
- anchor admission, D4 generation 1, independent certification, runtime, and
  G77-165 rerun remain unexecuted.

Unrelated pre-existing changes: none observed at task start.

Validation performed:

```text
Git branch/HEAD/tree/parent/subject and clean-worktree authentication
G77-170-to-G77-169 immediate-lineage validation
mandate, G48, predecessor, and CJ1 SHA-256 authentication
G77-168 D1-D4, G77-169 authority, and G77-170 blocker reconstruction
repository-wide key/certificate/private-material and TLS-path search
installed OpenSSL version/help inspection without material generation
RFC 8032, RFC 8410, and OpenSSL 3.0 documentation review
technology criteria and no-new-authority audit
human command, path, permissions, secret, export, and return-boundary audit
candidate/challenge/proof CJ1 schema and formula review
anchor identity, D3, D4, freshness, replay, and comparison review
secret screening and independent-certification completeness review
hostile authority, fallback, multi-candidate, and bootstrap audit
crypto/outcome/currentness/canonical/persistence/Result/topology accounting
G48 heading/subsection and Validation Matrix vocabulary validation
git diff --check and untracked-file whitespace validation
verdict uniqueness/finality and exact one-file mutation validation
```

No ceremony, key, certificate, signature, nonce, credential, endpoint,
service, runtime behavior, test, deployment, G77-165 rerun, or commit was
created.

# 6. Certification Verdict

`G77_STAGE_5_EXTERNAL_STATUS_OWNER_PROVISIONING_CEREMONY_READY_FOR_HUMAN_EXECUTION`
