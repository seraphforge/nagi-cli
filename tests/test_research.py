import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from nagi_cli.research import read_evidence, normalize_result, render_report

class ResearchTests(unittest.TestCase):
    def test_no_evidence(self):
        self.assertEqual(read_evidence([]), ('', []))

    def test_evidence_file(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'log.txt'
            p.write_text('test exit=0', encoding='utf-8')
            content, names = read_evidence([p])
            self.assertIn('test exit=0', content)
            self.assertEqual(names, [str(p)])

    def test_invalid_result(self):
        with self.assertRaises(ValueError):
            normalize_result({'background': 'not a list'})

    def test_render_disclaimer(self):
        data = normalize_result({'title': 'Test', 'scope': 'IoT'})
        data['evidence_files'] = []
        self.assertIn('尚未獨立驗證', render_report(data))

if __name__ == '__main__':
    unittest.main()
