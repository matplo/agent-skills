import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import venv

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/setup-project.py'
spec = importlib.util.spec_from_file_location('setup_project', SCRIPT)
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class RegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_dir = tempfile.TemporaryDirectory(prefix='physics env ')
        cls.prefix = Path(cls.env_dir.name) / '.venv'
        venv.create(cls.prefix, with_pip=False)

    @classmethod
    def tearDownClass(cls):
        cls.env_dir.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name)

    def run_setup(self, *extra, override=True):
        args = ['--project', str(self.project)]
        if override:
            args += ['--venv', str(self.prefix)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return setup.main(args + list(extra))

    def test_real_venv_registration_preserves_content_and_is_idempotent(self):
        agents = self.project / 'AGENTS.md'
        agents.write_text('# Existing instructions\nKeep these.\n')
        self.assertEqual(self.run_setup(), 0)
        self.assertTrue(agents.read_text().startswith('# Existing instructions\nKeep these.\n'))
        config = json.loads((self.project / setup.CONFIG).read_text())
        self.assertEqual(config['kind'], 'venv')
        self.assertEqual(config['prefix'], str(self.prefix))
        self.assertFalse(config['hepyy_available'])
        before = {p.name: p.read_bytes() for p in self.project.iterdir()}
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.project.iterdir()})
        self.assertIn('/' + setup.CONFIG, (self.project / '.gitignore').read_text())

    def test_dry_run_writes_nothing(self):
        self.assertEqual(self.run_setup('--dry-run'), 0)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_invalid_markers_prevent_all_writes(self):
        claude = self.project / 'CLAUDE.md'
        claude.write_text(setup.START)
        self.assertEqual(self.run_setup(), 1)
        self.assertEqual(list(self.project.iterdir()), [claude])
        self.assertEqual(claude.read_text(), setup.START)

    def test_symlink_is_not_followed(self):
        target = self.project / 'original.md'
        target.write_text('Keep me')
        (self.project / 'AGENTS.md').symlink_to(target)
        self.assertEqual(self.run_setup(), 1)
        self.assertEqual(target.read_text(), 'Keep me')

    def test_system_and_base_require_explicit_choice(self):
        for kind, base, flag in [('system', False, '--allow-system'), ('conda', True, '--allow-base')]:
            with self.subTest(kind=kind), patch.object(setup, 'inspect_environment', return_value={
                'kind': kind, 'is_conda_base': base, 'prefix': '/example',
                'python': '/example/bin/python', 'hepyy_available': False,
            }):
                self.assertEqual(self.run_setup(override=False), 1)
                self.assertEqual(self.run_setup(flag, '--dry-run', override=False), 0)

    def test_auto_detection_uses_current_interpreter(self):
        with patch.object(setup.sys, 'executable', str(self.prefix / 'bin/python')):
            self.assertEqual(self.run_setup(override=False), 0)
        config = json.loads((self.project / setup.CONFIG).read_text())
        self.assertEqual(config['prefix'], str(self.prefix))

    def test_venv_wins_over_inherited_conda_prefix(self):
        with patch.dict('os.environ', {'CONDA_PREFIX': '/another/conda', 'CONDA_DEFAULT_ENV': 'base'}):
            env = setup.inspect_environment(self.prefix / 'bin/python')
        self.assertEqual(env['kind'], 'venv')
        self.assertFalse(env['is_conda_base'])

    def test_override_kind_must_match(self):
        self.assertEqual(self.run_setup('--conda-prefix', str(self.prefix), override=False), 1)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_foreign_config_is_preserved(self):
        config = self.project / setup.CONFIG
        config.write_text('{"custom": true}\n')
        self.assertEqual(self.run_setup(), 1)
        self.assertEqual(list(self.project.iterdir()), [config])

    def test_no_arguments_only_prints_help(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(setup.main([]), 0)
        self.assertIn('Examples:', output.getvalue())


if __name__ == '__main__':
    unittest.main()
