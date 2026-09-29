"""Non-operational certification of the existing FM composition and readiness."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[5]
FM_REL = '.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py'
spec = importlib.util.spec_from_file_location('p05_binding_fm', ROOT / FM_REL)
fm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fm)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def context(checkout, head, tree):
    return {'canonical_argv': ['qemu-system-x86_64', '-virtfs',
        f'local,path={checkout},mount_tag=aigol_checkout,security_model=none,readonly=on'],
        'qemu_executable_base_seed_checkout_bindings': {'checkout': {
            'path': str(checkout), 'head': head, 'tree': tree,
            'detached': True, 'clean': True, 'read_only_mount': True}}}


class ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='p05_binding_certification_')
        cls.base = Path(cls.temp.name)
        cls.source = cls.base / 'parent_source'
        cls.source.mkdir()
        git(cls.source, 'init', '-q')
        git(cls.source, 'config', 'user.name', 'P05 certification')
        git(cls.source, 'config', 'user.email', 'p05@example.invalid')
        (cls.source / '.gitignore').write_text('sapianta_system/\n*.pyc\n')
        (cls.source / 'tests').mkdir()
        (cls.source / 'tests/fixture.txt').write_text('parent fixture\n')
        git(cls.source, 'add', '.')
        git(cls.source, 'commit', '-qm', 'fixture')
        cls.head = git(cls.source, 'rev-parse', 'HEAD')
        cls.tree = git(cls.source, 'rev-parse', 'HEAD^{tree}')
        cls.checkout = cls.base / 'checkout'
        fm.materialize_guest_self_contained_checkout(source_repository=cls.source,
            checkout_path=cls.checkout, expected_head=cls.head, expected_tree=cls.tree)
        fm.materialize_guest_self_contained_checkout(source_repository=ROOT / 'sapianta_system',
            checkout_path=cls.checkout / 'sapianta_system',
            expected_head=fm.NESTED_DEPENDENCY_HEAD, expected_tree=fm.NESTED_DEPENDENCY_TREE)
        cls.ctx = context(cls.checkout, cls.head, cls.tree)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_independent_parent_nested_and_readonly_readiness(self):
        proof = fm.validate_checkout_preboot_readiness(self.ctx)
        self.assertEqual(proof['checkout_head_tree'], 'PASS')
        self.assertEqual(proof['preauth_pinned_nested_projection']['observed_head'], fm.NESTED_DEPENDENCY_HEAD)
        self.assertFalse(proof['preauth_pinned_nested_projection']['parent_identity_authenticates_nested_bytes'])
        self.assertEqual(proof['preauth_pinned_nested_projection']['guest_visible_path'], '/mnt/aigol/sapianta_system')

    def test_fixed_source_and_wrong_root_head_tree_dirty(self):
        self.assertEqual(fm.authenticate_pinned_nested_source(ROOT), ROOT / 'sapianta_system')
        with self.assertRaises(RuntimeError):
            fm.authenticate_pinned_nested_source(self.base)
        for args, replacement in [
            (('rev-parse', '--show-toplevel'), str(ROOT)),
            (('rev-parse', 'HEAD'), '0' * 40),
            (('rev-parse', 'HEAD^{tree}'), '0' * 40),
            (('status', '--porcelain'), ' M runtime/__init__.py')]:
            original = fm._er_consumer_git
            def altered(path, *arguments):
                return replacement if arguments == args else original(path, *arguments)
            with self.subTest(args=args), mock.patch.object(fm, '_er_consumer_git', side_effect=altered):
                with self.assertRaises(RuntimeError):
                    fm.authenticate_pinned_nested_source(ROOT)

    def test_substitute_contains_pin_but_wrong_head(self):
        fake = self.base / 'substituted'
        fake.mkdir()
        nested = fake / 'sapianta_system'
        fm.materialize_guest_self_contained_checkout(source_repository=ROOT / 'sapianta_system',
            checkout_path=nested, expected_head=fm.NESTED_DEPENDENCY_HEAD,
            expected_tree=fm.NESTED_DEPENDENCY_TREE)
        git(nested, 'checkout', '-q', '--detach', 'HEAD^')
        self.assertEqual(git(nested, 'cat-file', '-t', fm.NESTED_DEPENDENCY_HEAD), 'commit')
        with self.assertRaisesRegex(RuntimeError, 'immutable authority'):
            fm.authenticate_pinned_nested_source(fake)

    def test_missing_and_redirected_projection_readiness(self):
        nested = self.checkout / 'sapianta_system'
        moved = self.base / 'temporarily_absent'
        nested.rename(moved)
        try:
            with self.assertRaisesRegex(RuntimeError, 'nested projection missing'):
                fm.validate_checkout_preboot_readiness(self.ctx)
            nested.symlink_to(moved, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, 'redirected'):
                fm.authenticate_nested_projection(self.ctx)
            nested.unlink()
        finally:
            moved.rename(nested)

    def test_ignored_shadow_bytes_and_assume_unchanged_tamper(self):
        nested = self.checkout / 'sapianta_system'
        for relative in ['runtime/shadow.pyc', '__init__.py', 'runtime.pyc']:
            path = nested / relative
            path.write_bytes(b'unauthenticated')
            try:
                with self.subTest(relative=relative), self.assertRaises(RuntimeError):
                    fm.authenticate_nested_projection(self.ctx)
            finally:
                path.unlink()
        path = nested / 'runtime/__init__.py'
        original = path.read_bytes()
        git(nested, 'update-index', '--assume-unchanged', 'runtime/__init__.py')
        try:
            path.write_bytes(b'# tampered\n')
            self.assertEqual(git(nested, 'status', '--porcelain'), '')
            with self.assertRaisesRegex(RuntimeError, 'tampered nested runtime'):
                fm.authenticate_nested_projection(self.ctx)
        finally:
            path.write_bytes(original)
            git(nested, 'update-index', '--no-assume-unchanged', 'runtime/__init__.py')

    def test_parent_import_shadow_and_wrong_parent_identity(self):
        for relative in ['sapianta_system.pyc', 'tests/sapianta_system.pyc']:
            path = self.checkout / relative
            path.write_bytes(b'shadow')
            try:
                with self.assertRaisesRegex(RuntimeError, 'import shadow'):
                    fm.authenticate_nested_projection(self.ctx)
            finally:
                path.unlink()
        bad = context(self.checkout, fm.NESTED_DEPENDENCY_HEAD, self.tree)
        with self.assertRaisesRegex(RuntimeError, 'checkout wrong HEAD'):
            fm.validate_checkout_preboot_readiness(bad)

    def test_destination_collision_and_symlink_source(self):
        with self.assertRaisesRegex(RuntimeError, 'destination collision'):
            fm.materialize_guest_self_contained_checkout(source_repository=ROOT / 'sapianta_system',
                checkout_path=self.checkout / 'sapianta_system',
                expected_head=fm.NESTED_DEPENDENCY_HEAD, expected_tree=fm.NESTED_DEPENDENCY_TREE)
        redirected = self.base / 'redirected_source'
        redirected.mkdir()
        (redirected / 'sapianta_system').symlink_to(ROOT / 'sapianta_system', target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, 'redirected'):
            fm.authenticate_pinned_nested_source(redirected)

    def test_runtime_file_symlink_and_wrong_projection_pins(self):
        path = self.checkout / 'sapianta_system/runtime/__init__.py'
        saved = self.base / 'saved_init'
        path.rename(saved)
        path.symlink_to(saved)
        try:
            with self.assertRaises(RuntimeError):
                fm.authenticate_nested_projection(self.ctx)
        finally:
            path.unlink()
            saved.rename(path)
        for name in ('NESTED_DEPENDENCY_HEAD', 'NESTED_DEPENDENCY_TREE'):
            with mock.patch.object(fm, name, '0' * 40), self.assertRaises(RuntimeError):
                fm.authenticate_nested_projection(self.ctx)

    def test_readonly_mount_and_tracked_collision(self):
        bad = context(self.checkout, self.head, self.tree)
        bad['canonical_argv'][-1] = bad['canonical_argv'][-1].replace('readonly=on', 'readonly=off')
        with self.assertRaisesRegex(RuntimeError, 'read-only'):
            fm.validate_checkout_preboot_readiness(bad)
        original = fm._er_consumer_git
        def collision(path, *args):
            if path == self.checkout and args[0] == 'ls-tree':
                return '100644 blob tracked-parent-content\tsapianta_system'
            return original(path, *args)
        with mock.patch.object(fm, '_er_consumer_git', side_effect=collision):
            with self.assertRaisesRegex(RuntimeError, 'collides with parent tracked'):
                fm.authenticate_nested_projection(self.ctx)

    def test_canonical_composition_actual_parent_and_nested_materializer(self):
        self._certify_composition(False)

    def test_operation_scoped_composition(self):
        self._certify_composition(True)

    def _certify_composition(self, operation_scoped):
        # Authority, freshness and overlay construction are isolated fixtures.
        # Both checkout materializations, source binding, and post-composition
        # identities/bytes execute unchanged against real pinned repositories.
        work = self.base / ('scoped_composition' if operation_scoped else 'composition')
        work.mkdir()
        checkout = work / 'transient/checkout' if operation_scoped else work / 'checkout'
        ctx = context(checkout, git(ROOT, 'rev-parse', 'HEAD'), git(ROOT, 'rev-parse', 'HEAD^{tree}'))
        ctx.update(operation_evidence_root=str(work / 'operation'), transient_root=str(work / 'transient'),
            runtime_export_root=str(work / 'transient/export'), runtime_manifest_path=str(work / 'transient/export/manifest.json'),
            overlay_path=str(work / 'transient/overlay'), guest_adapter_binding={
                'projection_root': str(work / 'transient/adapter'), 'source_path': fm.WRAPPER,
                'projected_path': str(work / 'transient/adapter/adapter.py'),
                'bootstrap_projected_path': str(work / 'transient/adapter/bootstrap.py')})
        fixture = work / 'fixture.json'
        fixture.write_text('{}')
        real_run = subprocess.run
        def no_qemu(argv, **kwargs):
            if argv[0] == 'qemu-img':
                Path(argv[-1]).write_bytes(b'non-operational overlay fixture')
                return subprocess.CompletedProcess(argv, 0)
            if 'qemu' in str(argv[0]):
                raise AssertionError('QEMU execution forbidden')
            return real_run(argv, **kwargs)
        with mock.patch.object(fm, 'authenticate_review_to_current_admission', return_value={}), \
             mock.patch.object(fm, 'authenticate_current_committed_jm_route'), \
             mock.patch.object(fm, 'validate_immutable_context_bindings'), \
             mock.patch.object(fm.fresh_context, 'validate_freshness'), \
             mock.patch.object(fm.fresh_context, 'checkout_lifecycle_binding', return_value=(fm.fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE if operation_scoped else 'TEST_FIXTURE')), \
             mock.patch.object(fm, 'preauth_fresh_checkout_destination_readiness'), \
             mock.patch.object(fm, 'resolve_candidate_source', return_value=('fixture.json', fixture)), \
             mock.patch.object(fm.subprocess, 'run', side_effect=no_qemu), \
             mock.patch.object(fm, 'materialize_guest_self_contained_checkout', wraps=fm.materialize_guest_self_contained_checkout) as materializer:
            result = fm.materialize_operation_state(repository_root=ROOT, context=ctx, context_source_path=fixture)
        self.assertEqual(materializer.call_count, 2)
        self.assertEqual(materializer.call_args_list[1].kwargs['source_repository'], ROOT / 'sapianta_system')
        self.assertEqual(materializer.call_args_list[1].kwargs['checkout_path'], checkout / 'sapianta_system')
        self.assertEqual(result['checkout_materialization']['observed_head'], ctx['qemu_executable_base_seed_checkout_bindings']['checkout']['head'])
        self.assertEqual(result['nested_materialization']['observed_head'], fm.NESTED_DEPENDENCY_HEAD)
        self.assertEqual(result['qemu_execution_count'], 0)


if __name__ == '__main__':
    unittest.main()
