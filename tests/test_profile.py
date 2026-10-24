import tempfile
import unittest
from pathlib import Path
from nagi_cli.profile import load_profile, system_prompt

class ProfileTests(unittest.TestCase):
    def test_load(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'profile.yaml'
            p.write_text('identity:\n  role: Researcher\nresearch:\n  - CTF\n', encoding='utf-8')
            self.assertEqual(load_profile(p)['research'], ['CTF'])
    def test_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'profile.yaml'
            p.write_text('research: hello\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_profile(p)
    def test_prompt(self):
        self.assertIn('untrusted', system_prompt().lower())
