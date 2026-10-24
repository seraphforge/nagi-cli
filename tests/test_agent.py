from pathlib import Path
import tempfile
import unittest
from nagi_cli.agent import allowed, safe_file, stage, environment_error, test_argv, context


class AgentTests(unittest.TestCase):
    def test_paths(self):
        for bad in ('../x', '/etc/passwd', '.env', 'src/.env.local', 'src/id_ed25519', 'src/../x', 'src\\x'):
            self.assertFalse(allowed(bad), bad)
        self.assertTrue(allowed('src/main.py'))

    def test_exact_match(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.py').write_text('old\n')
            with self.assertRaises(ValueError):
                stage(root, {'changes': [{'path': 'a.py', 'old': 'wrong', 'new': 'new\n'}]})
            self.assertEqual((root / 'a.py').read_text(), 'old\n')
            diff = stage(root, {'changes': [{'path': 'a.py', 'old': 'old\n', 'new': 'new\n'}]})
            self.assertIn('+new', diff)

    def test_atomic_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.py').write_text('original')
            with self.assertRaises(ValueError):
                stage(root, {'changes': [
                    {'path': 'a.py', 'old': 'original', 'new': 'changed'},
                    {'path': '../escape', 'old': '', 'new': 'bad'}]})
            self.assertEqual((root / 'a.py').read_text(), 'original')

    def test_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'link').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                safe_file(root, 'link/out.py')

    def test_environment_error(self):
        self.assertTrue(environment_error('/usr/bin/python: No module named pytest'))
        self.assertFalse(environment_error('FAILED test_calculator.py::test_add'))

    def test_test_command(self):
        self.assertEqual(test_argv('python -m pytest -q'), ['python', '-m', 'pytest', '-q'])
        with self.assertRaises(ValueError):
            test_argv('bash -c whoami')

    def test_no_truncated_originals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'huge.py').write_text('x' * 13000)
            (root / 'small.py').write_text('print(1)\n')
            self.assertNotIn('FILE huge.py', context(root))
            self.assertIn('FILE small.py', context(root))


if __name__ == '__main__':
    unittest.main()
