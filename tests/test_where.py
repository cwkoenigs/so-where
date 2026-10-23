"""Behavioral checks; never mutate the delivered sample or external systems."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from datetime import timedelta

BASE = Path(__file__).resolve().parents[1]
HELPER = BASE / 'so-where/references/where.py'
spec = importlib.util.spec_from_file_location('where', HELPER)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class MapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = json.loads((BASE / 'demo/registry.json').read_text())
        # Refresh fixture observation times only inside isolated tests, for repeatability.
        for r in self.data['records']:
            for e in r['evidence']:
                e['observed_at'] = (w.now() - timedelta(days=1)).isoformat(timespec='seconds')
            if r['state'] == 'curated':
                r['verified_at'] = w.promotable(r).isoformat(timespec='seconds')
        w.save(self.root, self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def test_incomplete_job_cannot_promote(self):
        before = copy.deepcopy(self.data)
        with self.assertRaisesRegex(ValueError, 'uncertainties'):
            w.mutate(self.data, 'promote', {'id': 'k-a10007'})
        self.assertEqual(self.data, before)

    def test_service_requires_all_three_observation_scopes(self):
        r = self.data['records'][0]
        r.update(state='draft', verified_at=None)
        r['evidence'] = [e for e in r['evidence'] if e['scope'] != 'runtime']
        with self.assertRaisesRegex(ValueError, 'runtime evidence'):
            w.mutate(self.data, 'promote', {'id': r['id']})

    def test_matching_folder_does_not_prove_deployment(self):
        r = self.data['records'][0]
        r.update(state='draft', verified_at=None)
        r['evidence'][1]['deployment'] = 'different-release'
        with self.assertRaisesRegex(ValueError, 'source evidence'):
            w.mutate(self.data, 'promote', {'id': r['id']})

    def test_promotion_uses_observation_not_current_time(self):
        changed, rid = w.mutate(self.data, 'promote', {'id': 'k-a10005'})
        r = next(r for r in changed['records'] if r['id'] == rid)
        self.assertEqual(r['state'], 'curated')
        self.assertEqual(r['verified_at'], r['evidence'][0]['observed_at'])
        self.assertEqual(self.data['records'][4]['state'], 'draft')

    def test_browser_fractional_seconds_survive_promotion(self):
        r = self.data['records'][4]
        observed = (w.now() - timedelta(seconds=2)).replace(microsecond=123000)
        r['evidence'][0]['observed_at'] = observed.isoformat(timespec='milliseconds')
        changed, _ = w.mutate(self.data, 'promote', {'id': r['id']})
        result = changed['records'][4]
        self.assertEqual(w.parse_time(result['verified_at']), observed)
        w.save(self.root, changed)

    def test_stale_build_does_not_refresh_observations(self):
        r = self.data['records'][0]
        for e in r['evidence']:
            e['observed_at'] = (w.now() - timedelta(days=40)).isoformat(timespec='seconds')
        r['verified_at'] = w.promotable(r, allow_stale=True).isoformat(timespec='seconds')
        before = copy.deepcopy(self.data)
        w.build(self.root, self.data)
        self.assertEqual(w.freshness(r), 'Stale')
        self.assertEqual(self.data, before)
        self.assertIn('Stale', (self.root / 'START.md').read_text())
        r.update(state='draft', verified_at=None)
        with self.assertRaisesRegex(ValueError, 'stale'):
            w.mutate(self.data, 'promote', {'id': r['id']})

    def test_relocation_preserves_id_previous_snapshot_and_does_not_move_source(self):
        source = self.root / 'original.md'
        source.write_text('Original source stays here.')
        r = self.data['records'][4]
        r['locations'][0]['uri'] = source.as_uri()
        target = self.root / 'not-created.md'
        changed, rid = w.mutate(self.data, 'relocate', {'id': r['id'], 'old': source.as_uri(),
            'new': target.as_uri(), 'reason': 'Reference updated after a separate project move'})
        result = next(s for s in changed['records'] if s['id'] == rid)
        self.assertEqual(result['state'], 'draft')
        self.assertIsNone(result['verified_at'])
        self.assertEqual(result['history'][-1]['before']['locations'][0]['uri'], source.as_uri())
        self.assertEqual(source.read_text(), 'Original source stays here.')
        self.assertFalse(target.exists())

    def test_amend_preserves_snapshot_and_invalidates_verification(self):
        r = copy.deepcopy(self.data['records'][0])
        r['summary'] = 'New understanding'
        changed, _ = w.mutate(self.data, 'amend', {'id': r['id'], 'record': r, 'reason': 'New evidence'})
        result = changed['records'][0]
        self.assertEqual(result['state'], 'draft')
        self.assertIsNone(result['verified_at'])
        self.assertEqual(result['history'][-1]['before']['summary'], self.data['records'][0]['summary'])

    def test_sample_evidence_rejected_in_real_map(self):
        self.data['demo'] = False
        with self.assertRaisesRegex(ValueError, 'sample evidence'):
            w.validate(self.data)

    def test_dangling_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'dangling'):
            w.mutate(self.data, 'link', {'id': 'k-a10001', 'type': 'depends_on', 'to': 'k-ffffff'})

    def test_future_observation_rejected(self):
        self.data['records'][0]['evidence'][0]['observed_at'] = (w.now() + timedelta(days=1)).isoformat()
        with self.assertRaisesRegex(ValueError, 'future'):
            w.validate(self.data)

    def test_exports_resolve_wiki_links_and_preserve_evidence(self):
        w.build(self.root, self.data)
        for path in (self.root/'obsidian').glob('*.md'):
            for rid in re.findall(r'\[\[(k-[0-9a-f]{6})\|', path.read_text()):
                self.assertTrue((path.parent/(rid+'.md')).exists(), rid)
        note = (self.root/'obsidian/k-a10002.md').read_text()
        self.assertIn('Incoming runs_on', note)
        self.assertIn('../evidence/harbor-investigation.md', note)

    def test_embedded_json_cannot_end_script_element(self):
        self.data['records'][4]['summary'] = '</script><script>alert(1)</script>'
        w.build(self.root, self.data)
        page = (self.root/'index.html').read_text()
        self.assertNotIn('</script><script>alert(1)', page)
        self.assertIn('\\u003c/script', page)

    def test_cli_mutation_round_trip(self):
        result = subprocess.run([sys.executable, str(HELPER), '--root', str(self.root),
            'promote', 'k-a10005'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(w.read(self.root)['revision'], 1)
        self.assertTrue((self.root/'registry.json.bak').exists())
        self.assertTrue((self.root/'index.html').exists())

    def test_http_persistence_revision_guard_and_origin_boundary(self):
        process = subprocess.Popen([sys.executable, '-u', str(HELPER), '--root', str(self.root),
            'serve', '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            line = process.stdout.readline()
            match = re.search(r'http://127.0.0.1:\d+', line)
            self.assertIsNotNone(match, line)
            base = match.group()
            result = json.load(urlopen(base+'/api/registry', timeout=3))
            payload = {'id': 'k-a10005', 'expected_revision': 0}
            headers = {'Content-Type':'application/json','X-Where-Token':result['csrf']}
            def post(p, h):
                return urlopen(Request(base+'/api/promote', data=json.dumps(p).encode(),headers=h),timeout=3)
            with self.assertRaises(HTTPError) as err:
                post(payload, {**headers, 'Origin':'https://unrelated.example.test'})
            self.assertEqual(err.exception.code, 400)
            with self.assertRaises(HTTPError):
                post(payload, {**headers, 'X-Where-Token':'wrong'})
            changed = json.load(post(payload, headers))
            self.assertEqual(changed['registry']['revision'], 1)
            self.assertEqual(w.read(self.root)['records'][4]['state'], 'curated')
            with self.assertRaises(HTTPError) as err:
                post(payload, headers)
            self.assertEqual(err.exception.code, 409)
            with self.assertRaises(HTTPError):
                urlopen(base+'/../so-where/references/where.py',timeout=3)
        finally:
            process.terminate()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
