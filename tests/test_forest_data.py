"""Contract tests for automatic updates and preserving the last good snapshot."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('forest_sync', Path(__file__).parents[1] / 'scripts/update_forest_data.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

def fixture():
    return {'success': True, 'result': {'name': 'layer', 'private': False, 'state': 'active',
        'organization': {'name': 'rinya', 'title': '林野庁'}, 'title': '森林計画対象森林レイヤ',
        'metadata_modified': '2026-07-27T06:43:22', 'notes': 'source notes', 'num_resources': 1,
        'resources': [{'id': 'test-01', 'name': 'fr_layer_01_2025.7z', 'url': 'https://example.org/01.7z', 'format': '7z'}]}}

class SyncTest(unittest.TestCase):
    def test_prefecture_and_actual_format(self):
        r = sync.normalize(fixture())['resources'][0]
        self.assertEqual((r['prefecture'], r['format']), ('北海道', '7z'))

    def test_unknown_new_resource_is_preserved(self):
        p = fixture(); p['result']['resources'][0]['name'] = 'new-data.geojson'
        r = sync.normalize(p)['resources'][0]
        self.assertIsNone(r['prefecture'])
        self.assertEqual(r['name'], 'new-data.geojson')

    def test_add_remove_and_replace_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'catalog.json'; p = fixture()
            sync.update(p, output, '2026-09-01T00:00:00+00:00')
            added = copy.deepcopy(p['result']['resources'][0]); added.update(id='test-02', name='fr_layer_02_2025.7z')
            p['result']['resources'].append(added); p['result']['num_resources'] = 2
            data = sync.update(p, output, '2026-09-02T00:00:00+00:00')
            self.assertEqual(len(data['resources']), 2)
            p['result']['resources'].pop(0); p['result']['num_resources'] = 1
            p['result']['resources'][0]['url'] = 'https://example.org/new.7z'
            data = sync.update(p, output, '2026-09-03T00:00:00+00:00')
            self.assertEqual([r['id'] for r in data['resources']], ['test-02'])
            self.assertEqual(data['resources'][0]['url'], 'https://example.org/new.7z')

    def test_unchanged_content_preserves_changed_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'catalog.json'
            first = sync.update(fixture(), out, '2026-09-01T00:00:00+00:00')
            second = sync.update(fixture(), out, '2026-09-02T00:00:00+00:00')
            self.assertEqual(first['changed_at'], second['changed_at'])
            self.assertNotEqual(first['checked_at'], second['checked_at'])
            p = fixture(); p['result']['notes'] = 'changed explanation'
            third = sync.update(p, out, '2026-09-03T00:00:00+00:00')
            self.assertNotEqual(second['fingerprint'], third['fingerprint'])

    def test_invalid_responses_never_overwrite_snapshot(self):
        bad = []
        p = fixture(); p['success'] = False; bad.append(p)
        p = fixture(); p['result']['resources'] = []; bad.append(p)
        p = fixture(); p['result']['num_resources'] = 2; bad.append(p)
        p = fixture(); p['result']['resources'][0]['url'] = 'javascript:alert(1)'; bad.append(p)
        p = fixture(); p['result']['organization']['name'] = 'other'; bad.append(p)
        p = fixture(); p['result']['private'] = True; bad.append(p)
        p = fixture(); p['result']['resources'] *= 2; p['result']['num_resources'] = 2; bad.append(p)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'catalog.json'; sync.update(fixture(), output)
            before = output.read_bytes()
            for payload in bad:
                with self.subTest(payload=payload):
                    with self.assertRaises(ValueError): sync.update(payload, output)
                    self.assertEqual(before, output.read_bytes())

    def test_html_is_not_executable(self):
        p = fixture(); p['result']['notes'] = '<script>alert(1)</script>&emsp;test'
        self.assertNotIn('<script>', sync.normalize(p)['notes'])

if __name__ == '__main__': unittest.main()
