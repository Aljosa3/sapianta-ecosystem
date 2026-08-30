#!/usr/bin/env python3
"""Repository-only positive and fail-closed matrix for the GD context."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import jsonschema
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
LAUNCHER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
WRAPPER_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness/"
    "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_PATH = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAUNCHER = load(LAUNCHER_PATH, "g77_256gd_existing_fm_owner")
WRAPPER = load(WRAPPER_PATH, "g77_256gd_existing_fm_wrapper")
PREFIX = "G77_256GDTEST01"
GENERATION = (
    PREFIX
    + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
)
OPERATION = PREFIX + "_OPERATION_001"


def reseal(context: dict) -> dict:
    context["context_sha256"] = hashlib.sha256(
        LAUNCHER.canonical_bytes(
            {key: value for key, value in context.items() if key != "context_sha256"}
        )
    ).hexdigest()
    return context


def context_for(root: Path, *, prefix: str = PREFIX) -> dict:
    generation = (
        prefix
        + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
    )
    return LAUNCHER.build_operation_context(
        repository_root=REPOSITORY_ROOT,
        repository_head="a" * 40,
        repository_tree="b" * 40,
        generation_identity=generation,
        operation_identity=prefix + "_OPERATION_001",
        identity_namespace_prefix=prefix,
        operation_evidence_root=root / "operation",
        transient_root=root / "transient",
    )


def write_context(root: Path, context: dict) -> Path:
    path = root / "context.json"
    path.write_bytes(LAUNCHER.canonical_bytes(context))
    return path


def synthetic_authority(context: dict) -> dict:
    authorization = {
        "schema_id": LAUNCHER.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": "e" * 64,
        "authorized_context_sha256": context["context_sha256"],
        "authorized_operation_identity": context["operation_identity"],
        "authorized_generation_identity": context["generation_identity"],
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_repository_head": context["repository_head"],
        "authorized_repository_tree": context["repository_tree"],
        "authorized_constitutional_anchor_head": LAUNCHER.CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": LAUNCHER.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_attempt_operational_attempt_limit": 1,
        "retry_limit": 0,
        "repair_limit": 0,
        "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False,
        "provider_authorized": False,
        "trusted_access_authorized": False,
        "authorization_reusable": False,
        "auto_continuable": False,
    }
    return {
        "schema_id": LAUNCHER.AUTHORITY_SCHEMA,
        "authorization": authorization,
        "authorization_sha256": LAUNCHER.authority_sha256(authorization),
    }


class FreshContextPositiveTests(unittest.TestCase):
    def test_canonical_schema_accepts_context_and_rejects_unknown_fields(self):
        schema_path = REPOSITORY_ROOT / (
            ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
            "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json"
        )
        schema = json.loads(schema_path.read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        with tempfile.TemporaryDirectory(prefix="g77_256gd_schema_") as temporary:
            context = context_for(Path(temporary))
            jsonschema.validate(context, schema)
            context["unknown_field"] = "forbidden"
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(context, schema)

    def test_isolated_context_is_canonical_sealed_and_has_39_identities(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_context_") as temporary:
            root = Path(temporary)
            context = context_for(root)
            path = write_context(root, context)
            loaded = LAUNCHER.fresh_context.load_context(
                path, repository_root=REPOSITORY_ROOT
            )
            self.assertEqual(loaded, context)
            self.assertEqual(len(LAUNCHER.fresh_context.derived_identity_tokens(PREFIX)), 39)
            self.assertEqual(len(set(loaded["guest_output_relative_paths"])), 8)
            self.assertEqual(loaded["canonical_argv"].count("-nic"), 1)
            index = loaded["canonical_argv"].index("-nic")
            self.assertEqual(loaded["canonical_argv"][index + 1], "none")

    def test_materialization_ga_visibility_and_authority_free_readiness_pass(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_static_") as temporary:
            root = Path(temporary)
            context = context_for(root)
            path = write_context(root, context)
            materialized = LAUNCHER.materialize_operation_state(
                repository_root=REPOSITORY_ROOT,
                context=context,
                context_source_path=path,
            )
            self.assertEqual(materialized["qemu_execution_count"], 0)
            prepared = LAUNCHER.prepare_receipt_parent(REPOSITORY_ROOT, context)
            self.assertTrue(prepared["receipt_namespace_unused"])
            readiness = LAUNCHER.authority_free_static_readiness(
                repository_root=REPOSITORY_ROOT,
                context=context,
                observed_head=context["repository_head"],
                observed_tree=context["repository_tree"],
                repository_clean=True,
                observed_asset_sha256=LAUNCHER.observe_context_assets(
                    REPOSITORY_ROOT, context
                ),
            )
            self.assertEqual(readiness["result"], "STATIC_READINESS_PASS")
            self.assertEqual(readiness["human_operational_authorization_count"], 0)
            self.assertEqual(readiness["qemu_execution_count"], 0)

    def test_test_only_non_authority_fixture_binds_context(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_authority_") as temporary:
            context = context_for(Path(temporary))
            authority = synthetic_authority(context)
            file_sha = hashlib.sha256(LAUNCHER.canonical_bytes(authority)).hexdigest()
            result = LAUNCHER.validate_execution_admission(
                context=context,
                authority=authority,
                authority_file_sha256=file_sha,
                supplied_authority_sha256=file_sha,
                observed_head=context["repository_head"],
                observed_tree=context["repository_tree"],
                anchor_is_ancestor=True,
                repository_clean=True,
                observed_asset_sha256=LAUNCHER.context_asset_expectations(context),
                argv=context["canonical_argv"],
                canonical_argv_sha256=context["canonical_argv_sha256"],
                receipt_namespace_consumed=False,
            )
            self.assertEqual(result["result"], "ADMIT_TO_BOOT_BOUNDARY_ONLY")

    def test_existing_wrapper_consumes_context_and_derives_full_family(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_wrapper_") as temporary:
            context = context_for(Path(temporary))
            with mock.patch.object(WRAPPER, "FC_SOURCE", FC_PATH):
                namespace = WRAPPER.load_specialized_namespace(context)
            self.assertEqual(namespace["GENERATION_ID"], GENERATION)
            self.assertEqual(namespace["RAW_ROOT"], WRAPPER.RAW_ROOT)
            self.assertEqual(
                namespace["CONTINUATION_MANIFEST_PATH"].name,
                PREFIX + "_CONTINUATION_MANIFEST_V1.json",
            )


class FreshContextNegativeTests(unittest.TestCase):
    def assert_context_denied(self, context: dict, pattern: str | None = None):
        manager = self.assertRaisesRegex(ValueError, pattern) if pattern else self.assertRaises(ValueError)
        with manager:
            LAUNCHER.fresh_context.validate_context(
                context, repository_root=REPOSITORY_ROOT
            )

    def test_missing_bad_seal_historical_reuse_and_malformed_values_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_negative_") as temporary:
            root = Path(temporary)
            baseline = context_for(root)
            missing = copy.deepcopy(baseline)
            del missing["operation_identity"]
            self.assert_context_denied(missing, "fields missing")
            bad_seal = copy.deepcopy(baseline)
            bad_seal["context_sha256"] = "0" * 64
            self.assert_context_denied(bad_seal, "seal mismatch")
            for field, value in (
                ("identity_namespace_prefix", "G77_256FM"),
                ("generation_identity", "G77_256FM_REUSED"),
                ("operation_identity", "G77_256FM_OPERATION_001"),
                ("overlay_path", "relative/overlay.qcow2"),
                ("serial_path", str(root / "x" / ".." / "serial.log")),
            ):
                with self.subTest(field=field):
                    mutated = copy.deepcopy(baseline)
                    mutated[field] = value
                    reseal(mutated)
                    self.assert_context_denied(mutated)

    def test_duplicate_key_and_noncanonical_context_files_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_json_") as temporary:
            root = Path(temporary)
            context = context_for(root)
            duplicate = root / "duplicate.json"
            duplicate.write_text('{"x":1,"x":2}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                LAUNCHER.fresh_context.load_context(
                    duplicate, repository_root=REPOSITORY_ROOT
                )
            noncanonical = root / "noncanonical.json"
            noncanonical.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not canonical"):
                LAUNCHER.fresh_context.load_context(
                    noncanonical, repository_root=REPOSITORY_ROOT
                )

    def test_symlink_overlap_duplicate_and_incomplete_sinks_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_layout_") as temporary:
            root = Path(temporary)
            baseline = context_for(root)
            target = root / "target"
            target.mkdir()
            alias = root / "alias"
            alias.symlink_to(target, target_is_directory=True)
            symlinked = copy.deepcopy(baseline)
            symlinked["operation_evidence_root"] = str(alias)
            symlinked["receipt_parent"] = str(alias / "receipts")
            symlinked["pre_receipt_path"] = str(alias / "receipts" / f"{PREFIX}_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
            symlinked["post_receipt_path"] = str(alias / "receipts" / f"{PREFIX}_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
            symlinked["runtime_export_root"] = str(alias / "runtime_export")
            symlinked["runtime_manifest_path"] = str(alias / "runtime_export" / f"{PREFIX}_CONTINUATION_MANIFEST_V1.json")
            argv = symlinked["canonical_argv"]
            symlinked["canonical_argv"] = [item.replace(str(root / "operation"), str(alias)) for item in argv]
            symlinked["canonical_argv_sha256"] = LAUNCHER.fresh_context.argv_sha256(symlinked["canonical_argv"])
            reseal(symlinked)
            self.assert_context_denied(symlinked, "symlink")

            overlap = copy.deepcopy(baseline)
            overlap["transient_root"] = overlap["operation_evidence_root"]
            overlap["overlay_path"] = overlap["transient_root"] + "/guest-overlay.qcow2"
            overlap["serial_path"] = overlap["transient_root"] + "/serial.log"
            overlap["canonical_argv"] = LAUNCHER.fresh_context.derive_canonical_argv(
                overlay_path=Path(overlap["overlay_path"]),
                serial_path=Path(overlap["serial_path"]),
                seed_path=Path(overlap["qemu_executable_base_seed_checkout_bindings"]["seed"]["path"]),
                checkout_path=Path(overlap["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]),
                wrapper_host_root=REPOSITORY_ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness",
                dn_harness_host_root=REPOSITORY_ROOT / ".github/governance/evidence/g77_256dn_p03_diagnostic_v1/harness",
                runtime_export_root=Path(overlap["runtime_export_root"]),
            )
            overlap["canonical_argv_sha256"] = LAUNCHER.fresh_context.argv_sha256(overlap["canonical_argv"])
            reseal(overlap)
            self.assert_context_denied(overlap, "overlap")

            incomplete = copy.deepcopy(baseline)
            incomplete["guest_output_relative_paths"] = incomplete["guest_output_relative_paths"][:-1]
            reseal(incomplete)
            self.assert_context_denied(incomplete, "incomplete")

    def test_every_declared_host_sink_collision_is_denied(self):
        for index in range(11):
            with self.subTest(index=index), tempfile.TemporaryDirectory(
                prefix=f"g77_256gd_collision_{index}_"
            ) as temporary:
                root = Path(temporary)
                context = context_for(root)
                path = write_context(root, context)
                LAUNCHER.materialize_operation_state(
                    repository_root=REPOSITORY_ROOT,
                    context=context,
                    context_source_path=path,
                )
                LAUNCHER.prepare_receipt_parent(REPOSITORY_ROOT, context)
                sinks = LAUNCHER.fresh_context.complete_mutable_sink_paths(context)
                target = sinks[index]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("collision\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "collision"):
                    LAUNCHER.fresh_context.validate_freshness(
                        context, overlay_materialized=True
                    )

    def test_argv_network_manifest_context_and_authority_mismatch_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_mismatch_") as temporary:
            root = Path(temporary)
            baseline = context_for(root)
            argv = copy.deepcopy(baseline)
            argv["canonical_argv"][argv["canonical_argv"].index("-nic") + 1] = "user"
            argv["canonical_argv_sha256"] = LAUNCHER.fresh_context.argv_sha256(argv["canonical_argv"])
            reseal(argv)
            self.assert_context_denied(argv, "outside approved")

            authority = synthetic_authority(baseline)
            for field in ("authorized_context_sha256", "authorized_canonical_argv_sha256"):
                with self.subTest(field=field):
                    mutated = copy.deepcopy(authority)
                    mutated["authorization"][field] = "0" * 64
                    mutated["authorization_sha256"] = LAUNCHER.authority_sha256(mutated["authorization"])
                    file_sha = hashlib.sha256(LAUNCHER.canonical_bytes(mutated)).hexdigest()
                    with self.assertRaisesRegex(RuntimeError, "binding mismatch"):
                        LAUNCHER.validate_execution_admission(
                            context=baseline,
                            authority=mutated,
                            authority_file_sha256=file_sha,
                            supplied_authority_sha256=file_sha,
                            observed_head=baseline["repository_head"],
                            observed_tree=baseline["repository_tree"],
                            anchor_is_ancestor=True,
                            repository_clean=True,
                            observed_asset_sha256=LAUNCHER.context_asset_expectations(baseline),
                            argv=baseline["canonical_argv"],
                            canonical_argv_sha256=baseline["canonical_argv_sha256"],
                            receipt_namespace_consumed=False,
                        )

    def test_materialization_root_collisions_are_denied_before_overlay_creation(self):
        for field in ("operation_evidence_root", "transient_root"):
            with self.subTest(field=field), tempfile.TemporaryDirectory(
                prefix="g77_256gd_root_collision_"
            ) as temporary:
                root = Path(temporary)
                context = context_for(root)
                context_path = write_context(root, context)
                Path(context[field]).mkdir()
                with self.assertRaisesRegex(RuntimeError, "root collision"):
                    LAUNCHER.materialize_operation_state(
                        repository_root=REPOSITORY_ROOT,
                        context=context,
                        context_source_path=context_path,
                    )
                self.assertFalse(Path(context["overlay_path"]).exists())

    def test_overlay_and_undeclared_runtime_export_collisions_are_denied(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_overlay_collision_") as temporary:
            context = context_for(Path(temporary))
            overlay = Path(context["overlay_path"])
            overlay.parent.mkdir()
            overlay.write_text("collision\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "overlay collision"):
                LAUNCHER.fresh_context.validate_freshness(context)

        with tempfile.TemporaryDirectory(prefix="g77_256gd_export_collision_") as temporary:
            context = context_for(Path(temporary))
            runtime_export = Path(context["runtime_export_root"])
            runtime_export.mkdir(parents=True)
            (runtime_export / "UNDECLARED_OUTPUT.json").write_text(
                "{}\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "undeclared writable sink"):
                LAUNCHER.fresh_context.validate_freshness(context)

    def test_checkout_preboot_readiness_denies_missing_and_drift_matrix(self):
        with tempfile.TemporaryDirectory(prefix="g77_256gd_checkout_") as temporary:
            root = Path(temporary)
            context = context_for(root)
            checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
            checkout["path"] = str(root / "missing")
            with self.assertRaisesRegex(RuntimeError, "checkout missing"):
                LAUNCHER.validate_checkout_preboot_readiness(context)

            checkout_path = root / "checkout"
            checkout_path.mkdir()
            checkout["path"] = str(checkout_path)

            def git_observation(_path, *arguments):
                if arguments == ("rev-parse", "HEAD"):
                    return checkout["head"]
                if arguments == ("rev-parse", "HEAD^{tree}"):
                    return checkout["tree"]
                if arguments == ("status", "--porcelain"):
                    return ""
                if arguments == ("symbolic-ref", "-q", "HEAD"):
                    raise subprocess.CalledProcessError(1, arguments)
                raise AssertionError(arguments)

            for command, value, pattern in (
                (("rev-parse", "HEAD"), "0" * 40, "wrong HEAD"),
                (("rev-parse", "HEAD^{tree}"), "0" * 40, "wrong TREE"),
                (("status", "--porcelain"), " M drift", "dirty"),
            ):
                with self.subTest(command=command):
                    def drifted(path, *arguments, _command=command, _value=value):
                        if arguments == _command:
                            return _value
                        return git_observation(path, *arguments)

                    with mock.patch.object(LAUNCHER, "git", side_effect=drifted):
                        with self.assertRaisesRegex(RuntimeError, pattern):
                            LAUNCHER.validate_checkout_preboot_readiness(context)

            checkout["read_only_mount"] = False
            with mock.patch.object(LAUNCHER, "git", side_effect=git_observation):
                with self.assertRaisesRegex(RuntimeError, "read-only"):
                    LAUNCHER.validate_checkout_preboot_readiness(context)


class StaticArchitectureProofTests(unittest.TestCase):
    def test_candidate_semantics_unchanged_and_bindings_only_reissued(self):
        old_path = REPOSITORY_ROOT / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
            "G77_256FM_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json"
        )
        new_path = REPOSITORY_ROOT / (
            ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/candidate/"
            "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
        )
        old = json.loads(old_path.read_bytes())["manifest"]
        new = json.loads(new_path.read_bytes())["manifest"]
        old = copy.deepcopy(old)
        new = copy.deepcopy(new)
        for value in (old, new):
            value["required_head"] = "<REPOSITORY_BINDING>"
            value["source_tree"] = "<TREE_BINDING>"
            for binding in value["extension_bindings"]:
                if binding["identity"] == "G77_256FM_WRONG_ATTEMPT_ADAPTER":
                    binding["sha256"] = "<WRAPPER_BINDING>"
        new["extension_bindings"] = [
            binding
            for binding in new["extension_bindings"]
            if binding["identity"] != "SAPIANTA_FRESH_OPERATION_CONTEXT_V1_IMPLEMENTATION"
        ]
        self.assertEqual(old, new)

    def test_ee_projection_fixture_is_non_executable_and_context_exact(self):
        operation_root = REPOSITORY_ROOT / (
            ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
            "binding_operation/runtime_export"
        )
        context = LAUNCHER.fresh_context.load_context(
            operation_root / LAUNCHER.fresh_context.GUEST_CONTEXT_FILENAME,
            repository_root=REPOSITORY_ROOT,
        )
        fixture_path = REPOSITORY_ROOT / (
            ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/bindings/"
            "G77_256GD_EE_CONTEXT_PATH_PROJECTION_FIXTURE_V1.py"
        )
        fixture = load(fixture_path, "g77_256gd_ee_projection")
        self.assertFalse(hasattr(fixture, "main"))
        self.assertIn("TEST_ONLY", fixture.FIXTURE_CLASSIFICATION)
        self.assertEqual(
            fixture.CONTINUATION_MANIFEST_PATH.name,
            Path(context["runtime_manifest_path"]).name,
        )

    def test_single_launcher_single_qemu_order_and_no_auto_preparation(self):
        tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
        functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }
        main = functions["main"]
        names = [
            (node.func.id, node.lineno)
            for node in ast.walk(main)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        readiness = [line for name, line in names if name == "authority_free_static_readiness"]
        authority_load = [line for name, line in names if name == "load_authority"]
        final = [line for name, line in names if name == "validate_final_admission"]
        writes = sorted(line for name, line in names if name == "write_atomic")
        qemu = [
            node.lineno
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        self.assertEqual(len(readiness), 1)
        self.assertEqual(len(authority_load), 1)
        self.assertEqual(len(final), 1)
        self.assertEqual(len(writes), 2)
        self.assertEqual(len(qemu), 1)
        self.assertLess(readiness[0], authority_load[0])
        self.assertLess(authority_load[0], final[0])
        self.assertLess(final[0], writes[0])
        self.assertLess(writes[0], qemu[0])
        self.assertLess(qemu[0], writes[1])
        self.assertNotIn("prepare_receipt_parent", [name for name, _ in names])
        source = LAUNCHER_PATH.read_text(encoding="utf-8")
        self.assertEqual(source.count("subprocess.run(argv, check=False)"), 2)
        self.assertNotIn("while ", source)
        self.assertNotIn("FY_ROOT /", source)

    def test_context_and_static_inputs_are_reobserved_after_authority_load(self):
        tree = ast.parse(LAUNCHER_PATH.read_text(encoding="utf-8"))
        main = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        named_calls = [
            (node.func.id, node.lineno)
            for node in ast.walk(main)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        attribute_calls = [
            (node.func.attr, node.lineno)
            for node in ast.walk(main)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        readiness = next(
            line for name, line in named_calls if name == "authority_free_static_readiness"
        )
        authority_load = next(
            line for name, line in named_calls if name == "load_authority"
        )
        final_admission = next(
            line for name, line in named_calls if name == "validate_final_admission"
        )
        context_loads = sorted(
            line for name, line in attribute_calls if name == "load_context"
        )
        asset_observations = sorted(
            line for name, line in named_calls if name == "observe_context_assets"
        )
        self.assertEqual(len(context_loads), 2)
        self.assertEqual(len(asset_observations), 2)
        self.assertLess(context_loads[0], readiness)
        self.assertLess(readiness, authority_load)
        self.assertLess(authority_load, context_loads[1])
        self.assertLess(context_loads[1], asset_observations[1])
        self.assertLess(asset_observations[1], final_admission)


if __name__ == "__main__":
    unittest.main()
