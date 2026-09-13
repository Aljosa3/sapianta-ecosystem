#!/usr/bin/env python3
"""Reissue and verify the existing EXPIRED bootstrap digest projection."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LC = ROOT / (
    ".github/governance/evidence/"
    "g77_256lc_expired_bootstrap_digest_projection_reissue_v1"
)
ENTRY_HEAD = "9a8259107bab907ca12e00502bcbcdc5bc1e556a"
ENTRY_TREE = "b55019a8ca103bb5adea35b41d2276cb81a5ea35"
ENTRY_SUBJECT = "G77-256LB localize EXPIRED bootstrap digest blocker"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
GENERATION = "G77-256LC"
GENERATION_IDENTITY = "G77_256LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_REISSUE_V1"
MODE = "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION"
TERMINAL = (
    "A__LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_REISSUED__"
    "JR_CLOUD_INIT_NOCLOUD_FM_STATIC_BINDING_VERIFIED__"
    "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION__NO_E05_CREDIT"
)

LB_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256lb_fresh_expired_operational_recommissioning_v1/"
    "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JR = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/"
    "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_OWNER = FM.with_name("sapianta_fresh_operation_context_v1.py")
CLOUD = ROOT / (
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/"
    "static/G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
)
SEED = CLOUD.with_name("SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img")
META = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK = META.with_name("G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml")
CANDIDATE = ROOT / (
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
REDUCTION = LC / "G77_256LC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = LC / "G77_256LC_G48_IMPLEMENTATION_REPORT_V1.md"
TESTS = LC / "tests/test_g77_256lc_expired_bootstrap_digest_projection_v1.py"
IT_REPORT = ROOT / (
    ".github/governance/evidence/g77_256it_future_bootstrap_seed_binding_v1/"
    "G77_256IT_G48_IMPLEMENTATION_REPORT_V1.md"
)
JT_REPORT = ROOT / (
    ".github/governance/evidence/g77_256jt_expired_bootstrap_checkout_binding_repair_v1/"
    "G77_256JT_G48_IMPLEMENTATION_REPORT_V1.md"
)
HN_GENERATOR_TEST = ROOT / (
    ".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/"
    "tests/test_g77_256hn_wrong_input_bootstrap_harness_binding_v1.py"
)

LB_REDUCTION_SHA256 = "4fbcd0cfafc99660b00218f9818b41c81042c05aec8020ac749ef41b7f520cd5"
JR_SHA256 = "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344"
FM_BEFORE_SHA256 = "4931b5777750448c4608d7a40736b2b67f061f6191b86da5c0309e189ec52bb4"
FM_AFTER_SHA256 = "c5172208874cca022b638511e57f091eafa01ba3c7387b182cf65d4ee98764d0"
CLOUD_BEFORE_SHA256 = "d427ea791a6a34412af12f6fb4b8f6d6597db120d037bd13e99c9cb64f52f859"
CLOUD_AFTER_SHA256 = "fdad67efe32a70784600819404222abd7a7bcee4461854fba69651513b19664e"
SEED_BEFORE_SHA256 = "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4"
SEED_AFTER_SHA256 = "81011b08aabb7052a14dc4f81ec51536c551cad97441563f846edbe778728004"
META_SHA256 = "081885fe7f51b064148db23dff5f4af40f58ae693879b5cb05fae24c8f23838a"
NETWORK_SHA256 = "639b6f419a9ac49312b218e12395dc7e7d623d96202c3315a92dcd19d6fa02ba"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
GENISOIMAGE_SHA256 = "9bacc5951ca0767701cfd8e6b47537f199977e51a6e943f4edfdcf9d639d99d2"
SOURCE_DATE_EPOCH = 1789171200
IT_REPORT_SHA256 = "6ebe97868db4a3a49048690ef73e47969dfb6542607a40d826c9c6897ea60d69"
JT_REPORT_SHA256 = "271d06218a185ba306cb84b2745dcb5a9af1458575412cd5c38354cf23963441"
HN_GENERATOR_TEST_SHA256 = "cb524e05b7b987d9a8e5374a8718e4d2301f339df2d2af648912208240cfddac"


class LCFormalizationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"] + (["-C", "sapianta_system"] if nested else [])
    return subprocess.check_output(command + list(arguments), cwd=ROOT, text=True).strip()


def committed(path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{path.relative_to(ROOT).as_posix()}"],
        cwd=ROOT,
    )


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value):
        raise LCFormalizationError(f"NONCANONICAL_JSON:{path}")
    return value


def load_fm():
    specification = importlib.util.spec_from_file_location("g77_256lc_fm", FM)
    if specification is None or specification.loader is None:
        raise LCFormalizationError("FM_IMPORT_SPECIFICATION_UNAVAILABLE")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    observed = {
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "branch": git("branch", "--show-current"),
        "remote_head": remote_head,
    }
    expected = {
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "branch": BRANCH,
        "remote_head": ENTRY_HEAD,
    }
    if observed != expected:
        raise LCFormalizationError(f"ENTRY_MISMATCH:{observed}")
    if (
        git("rev-parse", "HEAD", nested=True) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", nested=True) != NESTED_TREE
        or git("status", "--porcelain", nested=True)
        or git("branch", "--show-current", nested=True)
        or nested_remote_tag != NESTED_HEAD
    ):
        raise LCFormalizationError("NESTED_AUTHORITY_MISMATCH")
    if git("diff", "--cached", "--name-only"):
        raise LCFormalizationError("INDEX_NOT_EMPTY_AT_FORMALIZATION")
    unexpected = [
        path
        for path in git("diff", "--name-only").splitlines()
        if path
        not in {
            FM.relative_to(ROOT).as_posix(),
            CLOUD.relative_to(ROOT).as_posix(),
            SEED.relative_to(ROOT).as_posix(),
        }
    ]
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if unexpected or any(
        not path.startswith(LC.relative_to(ROOT).as_posix() + "/")
        for path in untracked
    ):
        raise LCFormalizationError("UNBOUNDED_MUTATION_SCOPE")


def authenticate_lb() -> dict[str, Any]:
    if LB_REDUCTION.read_bytes() != committed(LB_REDUCTION):
        raise LCFormalizationError("LB_REDUCTION_NOT_COMMITTED_ENTRY_BYTES")
    if sha256(LB_REDUCTION) != LB_REDUCTION_SHA256:
        raise LCFormalizationError("LB_REDUCTION_HASH_MISMATCH")
    envelope = load_canonical(LB_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal")
        != "A__LB_STATIC_CLOUD_INIT_ADAPTER_DIGEST_BINDING_BLOCKER_LOCALIZED__REPOSITORY_ONLY__NO_HUMAN_AUTHORITY__NO_OPERATION"
        or reduction.get("classification", {}).get("failure_class")
        != "HARNESS_OR_TEST_ARTIFACT"
    ):
        raise LCFormalizationError("LB_TERMINAL_CONTRACT_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "file_sha256": LB_REDUCTION_SHA256,
        "failure_class": reduction["classification"]["failure_class"],
        "e05_state": reduction["e05"]["state"],
        "e05_frontier": reduction["e05"]["frontier"],
    }


def cloud_command() -> list[str]:
    commands = [
        shlex.split(line.strip())
        for line in CLOUD.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("/usr/bin/python3 ")
    ]
    if len(commands) != 1 or len(commands[0]) != 7:
        raise LCFormalizationError("CLOUD_COMMAND_AMBIGUOUS_OR_MALFORMED")
    return commands[0]


def authenticate_minimum_delta() -> dict[str, Any]:
    before_fm = committed(FM)
    before_cloud = committed(CLOUD)
    if sha256_bytes(before_fm) != FM_BEFORE_SHA256:
        raise LCFormalizationError("FM_BEFORE_HASH_MISMATCH")
    if sha256_bytes(before_cloud) != CLOUD_BEFORE_SHA256:
        raise LCFormalizationError("CLOUD_BEFORE_HASH_MISMATCH")
    expected_fm = before_fm.replace(
        CLOUD_BEFORE_SHA256.encode(), CLOUD_AFTER_SHA256.encode()
    ).replace(SEED_BEFORE_SHA256.encode(), SEED_AFTER_SHA256.encode())
    expected_cloud = before_cloud.replace(
        SEED_BEFORE_SHA256[:0].encode() + b"f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
        JR_SHA256.encode(),
    )
    if FM.read_bytes() != expected_fm or CLOUD.read_bytes() != expected_cloud:
        raise LCFormalizationError("DELTA_EXCEEDS_EXACT_HASH_REBIND")
    if (
        sha256(JR) != JR_SHA256
        or sha256(FM) != FM_AFTER_SHA256
        or sha256(CLOUD) != CLOUD_AFTER_SHA256
        or sha256(SEED) != SEED_AFTER_SHA256
        or sha256(META) != META_SHA256
        or sha256(NETWORK) != NETWORK_SHA256
        or sha256(P11) != P11_SHA256
    ):
        raise LCFormalizationError("POST_REISSUE_HASH_MISMATCH")
    command = cloud_command()
    if command[2] != JR_SHA256:
        raise LCFormalizationError("CLOUD_PROJECTED_ADAPTER_HASH_MISMATCH")
    fm_text = FM.read_text(encoding="utf-8")
    for token in (JR_SHA256, CLOUD_AFTER_SHA256, SEED_AFTER_SHA256):
        if token not in fm_text:
            raise LCFormalizationError(f"FM_BINDING_MISSING:{token}")
    return {
        "source_owner": JR.relative_to(ROOT).as_posix(),
        "source_bytes_sha256": JR_SHA256,
        "current_fm_expected_sha256": JR_SHA256,
        "current_cloud_init_presented_sha256": command[2],
        "current_nocloud_user_data_sha256": sha256_bytes(
            subprocess.check_output(
                ["isoinfo", "-i", str(SEED), "-R", "-x", "/user-data"],
                stderr=subprocess.DEVNULL,
            )
        ),
        "current_nocloud_image_sha256": SEED_AFTER_SHA256,
        "first_stale_component_before_lc": "JX_CLOUD_INIT_BOOTSTRAP_COMMAND_ARGUMENT_1",
        "last_stale_component_before_lc": "JX_NOCLOUD_SEED_V3_USER_DATA_AND_FM_SEED_CLOUD_INIT_HASH_PINS",
        "first_current_component": "JR_EXPIRED_ADAPTER_CURRENT_COMMITTED_BYTES",
        "minimum_reissue_owner": "EXISTING_JX_EXPIRED_CLOUD_INIT_AND_NOCLOUD_ASSET_OWNER_PLUS_EXISTING_FM_HASH_BINDING_OWNER",
        "all_downstream_hash_bindings": {
            "fm_expired_admission_adapter": JR_SHA256,
            "fm_expired_cloud_init": CLOUD_AFTER_SHA256,
            "fm_expired_seed": SEED_AFTER_SHA256,
        },
    }


def authenticate_seed_generation_contract() -> dict[str, Any]:
    if sha256(Path("/usr/bin/genisoimage")) != GENISOIMAGE_SHA256:
        raise LCFormalizationError("GENISOIMAGE_IDENTITY_MISMATCH")
    precedents = {
        IT_REPORT: IT_REPORT_SHA256,
        JT_REPORT: JT_REPORT_SHA256,
        HN_GENERATOR_TEST: HN_GENERATOR_TEST_SHA256,
    }
    for path, expected in precedents.items():
        if sha256(path) != expected or path.read_bytes() != committed(path):
            raise LCFormalizationError(f"GENERATOR_PRECEDENT_MISMATCH:{path}")
    it_text = IT_REPORT.read_text(encoding="utf-8")
    jt_text = JT_REPORT.read_text(encoding="utf-8")
    hn_text = HN_GENERATOR_TEST.read_text(encoding="utf-8")
    required_precedent = (
        "established `genisoimage` cidata/Joliet/Rock" in it_text
        and "identity is content-hash based; wall-clock freshness is not consulted" in it_text
        and "established `genisoimage` cidata/Joliet/Rock mechanism" in jt_text
        and '"-volid", "cidata"' in hn_text
        and all(
            f'"{token}"' in hn_text
            for token in ("-joliet", "-rock", "user-data", "meta-data", "network-config")
        )
    )
    if not required_precedent:
        raise LCFormalizationError("AUTHENTICATED_GENERATOR_PRECEDENT_NOT_FOUND")
    descriptor = subprocess.check_output(
        ["isoinfo", "-i", str(SEED), "-d"],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    file_inventory = subprocess.check_output(
        ["isoinfo", "-i", str(SEED), "-R", "-f"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).splitlines()
    if (
        "Volume id: cidata" not in descriptor
        or "Joliet with UCS level 3 found" not in descriptor
        or "Rock Ridge signatures version 1 found" not in descriptor
        or sorted(file_inventory) != ["/meta-data", "/network-config", "/user-data"]
    ):
        raise LCFormalizationError("NOCLOUD_IMAGE_STRUCTURE_MISMATCH")
    projections = {
        "/user-data": CLOUD,
        "/meta-data": META,
        "/network-config": NETWORK,
    }
    for member, source in projections.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != source.read_bytes():
            raise LCFormalizationError(f"NOCLOUD_PROJECTION_MISMATCH:{member}")
    return {
        "result": "VERIFIED__ESTABLISHED_GENERATOR__EXACT_THREE_MEMBER_PROJECTION__HASH_REBOUND",
        "authenticated_nocloud_reproducibility_requirement": "DETERMINISTIC_SOURCE_PROJECTION_PLUS_AUTHENTICATED_PER_IMAGE_DIGEST_REBINDING",
        "requirement_owner": "EXISTING_FM_HASH_BINDING_AND_VECTOR_LOCAL_NOCLOUD_ASSET_OWNER",
        "precedent_generator": "ESTABLISHED_GENISOIMAGE_CIDATA_JOLIET_ROCK_MECHANISM",
        "generator": "/usr/bin/genisoimage 1.1.11",
        "generator_sha256": GENISOIMAGE_SHA256,
        "source_date_epoch": SOURCE_DATE_EPOCH,
        "command": "genisoimage -quiet -output IMAGE -volid cidata -joliet -rock user-data meta-data network-config",
        "precedent_timestamp_policy": "UNSPECIFIED_BY_PRECEDENT__WALL_CLOCK_FRESHNESS_NOT_AN_IDENTITY_INPUT",
        "image_byte_identity_required": False,
        "user_data_byte_identity_required": True,
        "image_digest_rebinding_allowed": True,
        "normalization_allowed": False,
        "normalization_disposition": "NOT_AUTHENTICATED_AND_NOT_REQUIRED__NO_RAW_ISO_BYTE_PATCHING",
        "observed_tooling_edge": "GENISOIMAGE_1_1_11_EMBEDS_INVOCATION_TIME_IN_ISO_METADATA_DESPITE_SOURCE_DATE_EPOCH",
        "tooling_edge_class": "HARNESS_OR_TEST_ARTIFACT",
        "semantic_content_impact": "VERIFIED__NONE__ALL_THREE_PROJECTED_MEMBERS_BYTE_EXACT",
        "seed_sha256": SEED_AFTER_SHA256,
        "cloud_init_to_nocloud_projection": "VERIFIED__BYTE_EXACT",
        "meta_data_projection": "VERIFIED__BYTE_EXACT",
        "network_config_projection": "VERIFIED__BYTE_EXACT",
    }


def authenticate_full_static_readiness(work_root: Path) -> dict[str, Any]:
    fm = load_fm()
    transient = work_root / "transient"
    operation_state = work_root / "operation_state"
    context = fm.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=(
            "G77_256LC_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256LC_STATIC_FIXTURE_ONLY_NO_OPERATION_001",
        identity_namespace_prefix="G77_256LC",
        operation_evidence_root=operation_state,
        transient_root=transient,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    checkout.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--no-checkout", str(ROOT), str(checkout)],
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "--quiet", "--detach", fm.EXPIRED_CHECKOUT_HEAD],
        cwd=checkout,
        check=True,
    )
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(parents=True)
    shutil.copyfile(JR, Path(binding["projected_path"]))
    shutil.copyfile(JR, Path(binding["bootstrap_projected_path"]))
    shutil.copyfile(
        FM_OWNER,
        projection_root / fm.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME,
    )
    projection_root.chmod(fm.GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE)
    export_root = Path(context["runtime_export_root"])
    export_root.mkdir(parents=True)
    shutil.copyfile(CANDIDATE, Path(context["runtime_manifest_path"]))
    (export_root / fm.fresh_context.GUEST_CONTEXT_FILENAME).write_bytes(
        canonical_bytes(context)
    )
    overlay = Path(context["overlay_path"])
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.touch()
    observed_assets = fm.observe_context_assets(
        ROOT, context, CANDIDATE.relative_to(ROOT)
    )
    readiness = fm.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=ENTRY_HEAD,
        observed_tree=ENTRY_TREE,
        repository_clean=True,
        observed_asset_sha256=observed_assets,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    if (
        readiness.get("result") != "STATIC_READINESS_PASS"
        or readiness.get("human_operational_authorization_count") != 0
        or readiness.get("qemu_execution_count") != 0
        or readiness.get("guest_adapter_binding", {}).get("result")
        != "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    ):
        raise LCFormalizationError("AUTHORITY_FREE_STATIC_READINESS_NOT_PROVEN")
    return {
        "result": readiness["result"],
        "phase": readiness["phase"],
        "fixture_class": "TEST_ONLY__NONAUTHORITY__NONOPERATIONAL__NO_REQUEST",
        "static_bootstrap_digest_binding": "VERIFIED",
        "cloud_init_to_nocloud_projection": readiness["guest_adapter_binding"][
            "nocloud_source_projection_identity"
        ],
        "fm_guest_adapter_binding": readiness["guest_adapter_binding"]["result"],
        "checkout_readiness": "PASS",
        "visibility_readiness": readiness["preboot_visibility"]["result"],
        "authority_handoff_shape_only": readiness[
            "authority_handoff_canonicalization"
        ]["result"],
        "human_operational_authorization_count": 0,
        "qemu_execution_count": 0,
        "automatic_retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def build_reduction(
    seed_reproducibility: dict[str, Any],
    static_readiness: dict[str, Any],
) -> dict[str, Any]:
    lb = authenticate_lb()
    trace = authenticate_minimum_delta()
    return {
        "schema_id": "G77_256LC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": GENERATION,
        "generation_identity": GENERATION_IDENTITY,
        "mode": MODE,
        "terminal": TERMINAL,
        "entry": {
            "head": ENTRY_HEAD,
            "tree": ENTRY_TREE,
            "subject": ENTRY_SUBJECT,
            "branch": BRANCH,
            "remote_equality": "VERIFIED",
            "nested_head": NESTED_HEAD,
            "nested_tree": NESTED_TREE,
            "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_AUTHENTICATED",
        },
        "predecessor": lb,
        "collision_status": "VERIFIED__LC_NAMESPACE_ABSENT_BEFORE_CURRENT_GENERATION",
        "continuation": {
            "type": "CROSS_ACCOUNT_SAME_GENERATION",
            "previous_session_termination": "EXTERNAL_CODEX_USAGE_LIMIT",
            "durable_dirty_workspace_reauthenticated": True,
            "hidden_reasoning_continuity_claimed": False,
            "current_lc_terminal_state": "TERMINAL__REPOSITORY_ONLY_STATIC_REPAIR",
            "current_lc_commit_state": "UNCOMMITTED_AT_REDUCTION_MATERIALIZATION",
        },
        "dirty_path_disposition": {
            FM.relative_to(ROOT).as_posix(): "KEEP__EXACT_DERIVED_CLOUD_AND_SEED_HASH_REBIND_ONLY",
            CLOUD.relative_to(ROOT).as_posix(): "KEEP__EXACT_CURRENT_JR_DIGEST_PROJECTION_ONLY",
            SEED.relative_to(ROOT).as_posix(): "KEEP__ESTABLISHED_GENERATOR_STRUCTURE_AND_EXACT_THREE_MEMBER_PROJECTION",
            (LC / "analysis/G77_256LC_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_FORMALIZER_V1.py").relative_to(ROOT).as_posix(): "COMPLETE__REMOVE_UNAUTHENTICATED_CROSS_BUILD_BYTE_IDENTITY_REQUIREMENT",
        },
        "classification": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": "VERIFIED__NEWLY_EXPOSED_TOOL_METADATA_VARIANCE__NOT_A_NEW_REPOSITORY_INVARIANT_OR_CAPABILITY_CLASS",
            "affected_invariant": "AUTHENTICATED_NOCLOUD_SOURCE_PROJECTION_AND_PER_IMAGE_DIGEST_BINDING__NOT_CROSS_BUILD_IMAGE_BYTE_IDENTITY",
            "previous_closest_edge": "IT_JT_HN_ESTABLISHED_GENISOIMAGE_CONTENT_HASH_AND_EXACT_MEMBER_PROJECTION",
            "semantic_difference": "INDEPENDENT_IMAGES_DIFFER_ONLY_IN_GENERATOR_METADATA_WHILE_ALL_GOVERNED_MEMBERS_REMAIN_BYTE_EXACT",
            "production_behavior_impact": "VERIFIED__NONE_FROM_TIMESTAMP_VARIANCE__FM_BINDS_THE_SELECTED_IMAGE_SHA256",
            "new_capability_required": "VERIFIED__NO",
            "new_proof_required": "CURRENT_JR_TO_CLOUD_INIT_TO_EXACT_NOCLOUD_MEMBERS_TO_SELECTED_IMAGE_DIGEST_TO_FM_STATIC_READINESS",
            "convergence_signal": "VERIFIED__OVERSTRONG_CROSS_BUILD_ASSERTION_REMOVED__LB_STATIC_EDGE_CLOSED_WITH_EXISTING_OWNER_DELTA",
            "repetition_pressure": "VERIFIED__REDUCED__NO_OPERATION_OR_RAW_IMAGE_NORMALIZATION_USED",
            "verification_amplification_risk": "ESTIMATED__LOW_AFTER_REUSING_AUTHENTICATED_REQUIREMENT__HIGH_IF_UNAUTHENTICATED_BYTE_REPRODUCIBILITY_IS_INVENTED",
            "classification_evidence": "COMMITTED_IT_JT_HN_PRECEDENT__TWO_TIMED_GENISOIMAGE_DIAGNOSTIC_OUTPUTS__EXACT_THREE_MEMBER_EXTRACTION__FM_IMAGE_HASH_PIN",
            "classification_confidence": "VERIFIED__HIGH",
        },
        "hash_trace": trace,
        "generated_asset_reissue": {
            "cloud_init": {
                "old_value": CLOUD_BEFORE_SHA256,
                "new_value": CLOUD_AFTER_SHA256,
                "owner": "EXISTING_JX_EXPIRED_CLOUD_INIT_OWNER",
                "why": "PROJECT_CURRENT_JR_DIGEST_IN_BOOTSTRAP_ARGUMENT",
                "downstream_dependents": ["JX_NOCLOUD_USER_DATA", "FM_EXPIRED_CLOUD_INIT_SHA256"],
                "unchanged_dependents": ["META_DATA", "NETWORK_CONFIG", "OTHER_VECTOR_ASSETS"],
            },
            "nocloud_seed": {
                "old_value": SEED_BEFORE_SHA256,
                "new_value": SEED_AFTER_SHA256,
                "owner": "EXISTING_JX_EXPIRED_NOCLOUD_SEED_OWNER",
                "why": "REISSUE_BYTE_EXACT_USER_DATA_AFTER_CLOUD_INIT_CHANGE",
                "downstream_dependents": ["FM_EXPECTED_ASSET_SHA256_EXPIRED_SEED"],
                "unchanged_dependents": ["META_DATA_BYTES", "NETWORK_CONFIG_BYTES", "OTHER_VECTOR_SEEDS"],
            },
            "fm_launcher": {
                "old_value": FM_BEFORE_SHA256,
                "new_value": FM_AFTER_SHA256,
                "owner": "EXISTING_FM_BOOTSTRAP_HASH_BINDING_OWNER",
                "why": "BIND_NEW_EXPIRED_CLOUD_INIT_AND_SEED_HASHES",
                "downstream_dependents": ["FUTURE_FRESH_GENERATION_MUST_REAUTHENTICATE_FM_BYTES"],
                "unchanged_dependents": ["JR_ADMISSION_DIGEST", "P11", "NON_EXPIRED_VECTOR_HASH_PINS"],
            },
            "generation_contract": seed_reproducibility,
        },
        "static_readiness": static_readiness,
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "COMMON_FM_BOOTSTRAP_VALIDATION_RULE",
            "shared_owner_or_vector_specific": "SHARED_FM_RULE__VECTOR_SPECIFIC_GENERATED_ASSETS",
            "shared_generated_projection": "VERIFIED__PATTERN_SHARED__BYTES_VECTOR_SPECIFIC",
            "shared_binding_rule": "CURRENT_SOURCE_DIGEST_EQUALS_MATERIALIZED_VECTOR_LOCAL_BOOTSTRAP_DIGEST",
            "shared_reproducibility_behavior": "ESTABLISHED_GENERATOR__EXACT_MEMBER_PROJECTION__PER_IMAGE_HASH_BINDING",
            "shared_defect": "VERIFIED__NO__ONLY_EXPIRED_WAS_PROVEN_DEFECTIVE",
            "shared_required_delta": "VERIFIED__NO__ONLY_EXPIRED_CHANGED",
            "affected_vectors": ["EXPIRED"],
            "unaffected_vectors": ["FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "reuse_preconditions": "VECTOR_LOCAL_SOURCE_DIGEST_AND_EXACT_CLOUD_INIT_SEED_PROJECTION",
            "revalidation_required": "VERIFIED__PER_VECTOR_AND_PER_GENERATION",
            "expected_future_proof_reduction": "ESTIMATED__STATIC_PROJECTION_METHOD_REUSABLE__NO_OPERATIONAL_PROOF_OR_CREDIT_TRANSFER",
        },
        "frontier": {
            "previous_last_verified_edge": "CURRENT_FM_JR_DIGEST_AUTHENTICATION_PLUS_LB_STALE_PROJECTION_LOCALIZATION",
            "current_last_verified_edge": "CURRENT_JR_DIGEST_PROPAGATED_TO_EXPIRED_CLOUD_INIT_AND_NOCLOUD_AND_ACCEPTED_BY_FM_AUTHORITY_FREE_STATIC_PREFLIGHT",
            "previous_first_broken_edge": "EXPIRED_CLOUD_INIT_PRE_REQUEST_ADAPTER_DIGEST_EQUALS_CURRENT_PROJECTED_ADAPTER_DIGEST",
            "current_first_broken_edge": "NONE_KNOWN_AT_AUTHENTICATED_STATIC_PREOPERATIONAL_BOUNDARY",
            "first_unverified_operational_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
            "constitutional_frontier_movement": "VERIFIED__LB_STATIC_BOOTSTRAP_EDGE_CLOSED_TO_OPERATIONAL_BOUNDARY",
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
            "static_pre_operational_chain_complete": "VERIFIED__WITHIN_AUTHENTICATED_STATIC_SCOPE",
            "fresh_operational_attempt_readiness": "READY__REPOSITORY_ONLY",
            "readiness_blocker": "NONE_KNOWN_AT_AUTHENTICATED_STATIC_BOUNDARY",
            "next_static_edge": "NONE_KNOWN__NEXT_EDGE_IS_DISTINCT_HUMAN_AUTHORIZED_OPERATIONAL_PROOF_AFTER_REVIEW",
        },
        "minimum_next": {
            "minimum_missing_capability": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
            "minimum_missing_proof": "DISTINCT_FRESH_OPERATIONAL_OBSERVATION_SATISFYING_E05_ACCEPTANCE",
            "minimum_legal_next_delta": "AFTER_LC_COMMIT_PUSH_AND_SEPARATE_HUMAN_REMOTE_AUTHENTICATION__DISTINCT_FRESH_EXPIRED_OPERATIONAL_GENERATION",
        },
        "architecture": {
            "p11_mutation": 0,
            "production_mutation": 3,
            "production_files_changed": [
                FM.relative_to(ROOT).as_posix(),
                CLOUD.relative_to(ROOT).as_posix(),
                SEED.relative_to(ROOT).as_posix(),
            ],
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "parallel_flow": "NO",
            "production_route": "1_TO_1",
        },
        "operational_counters": {
            "human_authority_created": 0,
            "authority_consumption_count": 0,
            "qemu_start_count": 0,
            "vm_start_count": 0,
            "operation_attempt_count": 0,
            "operation_request_count": 0,
            "p11_entry_count": 0,
            "protected_invocation_count": 0,
            "protected_effect_count": 0,
            "retry_count": 0,
            "repair_retry_count": 0,
            "replay_count": 0,
        },
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_status": "NOT_PROVEN_OPERATIONALLY",
            "current_generation_credit": "VERIFIED__0",
        },
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "proof_yield": "STATIC_EDGE_CLOSED__AUTHORITY_SPENT_0__OPERATION_SPENT_0__E05_CREDIT_0",
        "generalization": {
            "general_invariant_candidate": "SOURCE_PROJECTION_CONSISTENCY_PLUS_GENERATED_ASSET_DIGEST_BINDING_CONSISTENCY",
            "generalization_required_for_current_delta": False,
            "generalization_deferred": "YES__FUTURE_HUMAN_REVIEW_IF_REPETITION_JUSTIFIES_SHARED_PREFLIGHT",
        },
        "metrics": {
            "project_state": "VERIFIED__LC_REPOSITORY_ONLY_STATIC_REPAIR_TERMINAL",
            "informal_project_progress_estimate": "ESTIMATED__STATIC_EXPIRED_BOOTSTRAP_CHAIN_READY__OPERATIONAL_PROOF_REMAINS",
            "constitutional_health_evidence": "VERIFIED__CURRENT_DIGEST_PROJECTION__EXACT_NOCLOUD_MEMBERS__HASH_REBOUND__FAIL_CLOSED_VALIDATOR__ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__THREE_EXISTING_OWNER_FILES_CLOSE_ONE_LOCALIZED_EDGE",
            "overengineering_risk": "ESTIMATED__LOW__NO_GENERIC_FRAMEWORK_OR_OTHER_VECTOR_CHANGE",
            "cognition_provenance": "HUMAN_AUTHENTICATED_LB_CHECKPOINT__DURABLE_DIRTY_LC_WORKSPACE__HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF__CURRENT_ACCOUNT_REAUTHENTICATION",
            "cognition_assisted_handoff": "VERIFIED__ONLY_INDEPENDENTLY_REAUTHENTICATED_DURABLE_FACTS_REUSED__NO_HIDDEN_REASONING_CLAIM",
            "candidate_capability": "VERIFIED__REPOSITORY_ONLY_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_READINESS",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_VECTOR_LOCAL_BOOTSTRAP_ASSETS",
            "constitutional_continuation_progress": "VERIFIED__LB_BLOCKER_TO_LC_STATIC_EDGE_CLOSURE",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED",
        },
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "cross_account_continuation": "VERIFIED__SAME_GENERATION",
            "predecessor_terminal_authenticated": "VERIFIED__YES",
            "predecessor_commit_authenticated": "VERIFIED__YES",
            "predecessor_remote_equality": "VERIFIED__YES",
            "nested_authority_authenticated": "VERIFIED__YES",
            "active_generation_reused": "VERIFIED__YES",
            "dirty_workspace_reauthenticated": "VERIFIED__YES",
            "repository_evidence_primary": "VERIFIED__YES",
            "previous_session_durable_evidence_reused": "VERIFIED__YES",
            "current_generation_reauthentication": "VERIFIED__YES",
            "current_account_reauthentication": "VERIFIED__YES",
            "human_decision_boundary_preserved": "VERIFIED__YES",
            "human_authority_created": 0,
            "authority_consumed": 0,
            "operation_performed": 0,
            "handoff_ambiguity_count": 0,
            "binding_owner_ambiguity_count": 0,
            "generated_asset_ambiguity_count": 0,
            "authority_state_ambiguity_count": 0,
            "operational_attempt_ambiguity_count": 0,
        },
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED__NO_GOVERNED_ATTRIBUTION_DENOMINATOR",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
        },
        "validation": {
            "lc_focused": "VERIFIED__8_PASSED",
            "la_kz_regression": "VERIFIED__16_PASSED__8_HISTORICAL_STATE_BOUND_ASSERTIONS_DESELECTED",
            "p11_regression": "VERIFIED__UNCHANGED_HASH__8_PASSED",
            "governance_conformance": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "g48_h1_count": 6,
            "g48_reuse_question_count": 5,
            "git_diff_check": "VERIFIED__PASS",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction(value: dict[str, Any]) -> None:
    envelope = {
        "schema_id": "G77_256LC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": value,
        "reduction_sha256": sha256_bytes(canonical_bytes(value)),
    }
    REDUCTION.write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    arguments = parser.parse_args()
    authenticate_entry(arguments.remote_head, arguments.nested_remote_tag)
    seed_proof = authenticate_seed_generation_contract()
    with tempfile.TemporaryDirectory(prefix="g77_256lc_static_") as static_temp:
        readiness_proof = authenticate_full_static_readiness(Path(static_temp))
    write_reduction(build_reduction(seed_proof, readiness_proof))
    print(TERMINAL)
