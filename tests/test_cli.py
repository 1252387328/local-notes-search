import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(project):
    spec = importlib.util.spec_from_file_location(project.replace('-', '_'), ROOT / 'cli.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectTests(unittest.TestCase):
    def test_all_help_and_invalid_arguments(self):
        for path in [ROOT / 'cli.py']:
            with self.subTest(project=path.parent.name):
                result = subprocess.run([sys.executable, str(path), '--help'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([sys.executable, str(path), '--not-a-real-option'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)

    def test_notes_search_rebuild_filters_and_hidden(self):
        module = load('local-notes-search')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'notes'
            folder.mkdir()
            (folder / 'release.md').write_text('release checklist and documentation')
            (folder / '.hidden.md').write_text('release hidden')
            (folder / 'other.txt').write_text('other content')
            (folder / 'link.md').symlink_to(folder / 'release.md')
            db = Path(tmp) / 'index.db'
            self.assertEqual(module.index(folder, db), 2)
            result = module.search(db, 'release', 'release', 10)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], 'release.md')
            self.assertIn('[release]', result[0][1])
            (folder / 'release.md').unlink()
            self.assertEqual(module.index(folder, db), 1)
            self.assertEqual(module.search(db, 'release', '', 10), [])

if __name__ == '__main__':
    unittest.main()
