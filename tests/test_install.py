import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'scripts/install_skill.py')
installer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_existing_runtimes_link_to_one_canonical_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)
            for runtime in ['.codex','.claude']:
                (home/runtime).mkdir()
            installer.install(home)
            installer.install(home)
            for runtime in ['.codex','.claude']:
                link=home/runtime/'skills/so-where'
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(),ROOT/'so-where')

    def test_real_directory_conflict_preserves_both_runtimes(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)
            (home/'.codex').mkdir()
            owned=home/'.claude/skills/so-where'
            owned.mkdir(parents=True)
            (owned/'local.txt').write_text('Keep me')
            with self.assertRaisesRegex(ValueError,'Refusing'):
                installer.install(home)
            self.assertFalse((home/'.codex/skills/so-where').exists())
            self.assertEqual((owned/'local.txt').read_text(),'Keep me')
