"""Contract tests for the commit-gating checks of the written site rules."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('check_site', Path(__file__).parents[1] / 'scripts/check_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)

P = 'Nature capital real estate'
HEAD = ('<link rel="icon" href="a.svg"><link rel="apple-touch-icon" href="a.png">'
        + ''.join(f'<meta property="{n}" content="x">' for n in sorted(site.OGP)))

def page(title='私たちについて | ネイチャーキャピタル・リアルエステイト', head=HEAD, body=''):
    return f'<!doctype html><html><head><title>{title}</title>{head}</head><body>\n{body}\n</body></html>'

def reasons(problems):
    return [reason for _, reason in problems]

class PageTest(unittest.TestCase):
    def test_valid_page_passes(self):
        body = ('<img src="a.webp" alt=""><a href="https://example.org/" target="_blank" rel="noreferrer noopener">x</a>'
                '<a href="https://yuyakawamura-blip.github.io/fudousanbusiness-jgx/about/">self</a><a href="../">up</a>'
                '<a href="https://forms.gle/x" target="_blank" rel="noopener noreferrer">相談</a>')
        self.assertEqual(site.check_page('about/index.html', page(body=body)), [])

    def test_img_without_alt_reports_its_line(self):
        [(line, reason)] = site.check_page('index.html', page(body='<p>\n<img src="a.webp"></p>'))
        self.assertEqual(line, 3)
        self.assertIn('alt', reason)

    def test_inline_event_handler(self):
        self.assertIn('onclick', reasons(site.check_page('index.html', page(body='<a href="#" onclick="go()">x</a>')))[0])

    def test_external_link_needs_target_and_rel(self):
        for href in ('https://docs.google.com/forms/d/x', 'http://example.org/', '//example.org/'):
            for attrs in ('', 'target="_blank" rel="noreferrer"', 'rel="noopener noreferrer"'):
                body = f'<a href="{href}" {attrs}>x</a>'
                self.assertEqual(len(site.check_page('index.html', page(body=body))), 1, (href, attrs))

    def test_title_suffix_by_language(self):
        self.assertEqual(len(site.check_page('index.html', page(title='私たちについて'))), 1)
        self.assertEqual(len(site.check_page('index.html', page(title='ネイチャーキャピタル・リアルエステイト'))), 1)
        en = 'Forestry | Nature Capital\n   Real Estate'  # A wrapped title still counts.
        self.assertEqual(site.check_page('forest/en/index.html', page(title=en)), [])
        self.assertEqual(len(site.check_page('forest/en/index.html', page())), 1)

    def test_missing_head_tags(self):
        missing = reasons(site.check_page('index.html', page(head='<link rel="icon" href="a.svg">')))
        self.assertEqual(len(missing), 1 + len(site.OGP))
        # The 404 page needs the icons but not the sharing tags.
        self.assertEqual(site.check_page('404.html', page(head='<link rel="icon apple-touch-icon" href="a">')), [])

class BaselineTest(unittest.TestCase):
    def test_counts_only_the_matching_file_type(self):
        counts = site.count_patterns({'a.css': '.a{color:red !important}.b{x:y! important}', 'a.js': 'var x; var y',
                                      'b.js': 'el.innerHTML = s', 'c.html': 'var !important'})
        self.assertEqual(counts, {'!important in CSS': 2, 'var in JS': 2, 'innerHTML in JS': 1})

    def test_rising_above_the_baseline_fails_and_falling_passes(self):
        baseline = {'var in JS': 2}
        self.assertEqual(site.over_baseline({'var in JS': 2}, baseline), [])
        self.assertEqual(site.over_baseline({'var in JS': 1}, baseline), [])
        self.assertEqual(len(site.over_baseline({'var in JS': 3}, baseline)), 1)

class ImportTest(unittest.TestCase):
    def test_finds_top_level_modules_but_not_relative_ones(self):
        source = 'import os.path, json\nfrom urllib.parse import x\nfrom . import y\nimport requests'
        self.assertEqual(site.imported_modules(source), {'os', 'json', 'urllib', 'requests'})

    def test_stdlib_or_not(self):
        for name in ('os', 'json', 'urllib', 'sys', 'html'):
            self.assertTrue(site.is_stdlib(name), name)
        self.assertFalse(site.is_stdlib('no_such_module_for_check_site'))

class StagedTest(unittest.TestCase):
    def test_site_and_listed_root_files_pass(self):
        paths = [f'{P}/docs/index.html', 'AGENTS.md', 'CLAUDE.md', '.github/workflows/checks.yml', '.githooks/pre-commit']
        self.assertEqual(site.check_staged(paths, [], {}), ([], []))

    def test_archive_and_other_projects_fail(self):
        problems, _ = site.check_staged([f'{P}/archive/old.html', 'jgx-hp', 'notes.txt'], [], {})
        self.assertEqual(len(problems), 3)

    def test_deleting_outside_the_site_passes_but_not_in_archive(self):
        deleted = {'.DS_Store', f'{P}/archive/old.html'}
        problems, _ = site.check_staged(sorted(deleted), [], {}, deleted)
        self.assertEqual(len(problems), 1)
        self.assertIn('archive', problems[0])

    def test_new_images(self):
        added = [f'{P}/docs/assets/ok-photo.webp', f'{P}/docs/assets/photo.png', f'{P}/docs/assets/My Photo.webp',
                 f'{P}/docs/assets/big-photo.webp', f'{P}/scripts/fixture.png']
        problems, warnings = site.check_staged(added, added, {f'{P}/docs/assets/big-photo.webp': 400 * 1024})
        self.assertEqual(len(problems), 2)  # photo.png is not WebP; "My Photo" is not kebab-case.
        self.assertEqual(len(warnings), 1)

class PlanTagTest(unittest.TestCase):
    PATCH = ('diff --git a/PLAN.md b/PLAN.md\n--- a/PLAN.md\n+++ b/PLAN.md\n'
             '@@ -3 +3 @@\n- [ ] old\n+- [x] old\n'
             '@@ -9,0 +10,5 @@\n+- [ ] new <!-- lane: E-NEW -->\n+  - [ ] nested\n+15. [ ] numbered\n'
             '+- [ ] skipped <!-- lane: none -->\n+plain text with - [ ] inside\n')

    def test_only_added_open_items_without_a_tag_fail(self):
        self.assertEqual(site.untagged_items(self.PATCH), [11, 12])

    def test_headers_before_the_first_hunk_are_not_lines(self):
        self.assertEqual(site.untagged_items('+++ b/- [ ] x\n'), [])

class MessageTest(unittest.TestCase):
    def test_good_message(self):
        self.assertEqual(site.check_message('ヘッダーの「無料相談」をそろえる\n\nCo-Authored-By: x\n# comment'), [])

    def test_bad_messages(self):
        self.assertEqual(len(site.check_message('あ' * 51)), 1)
        self.assertEqual(len(site.check_message('Fix the header')), 1)
        self.assertEqual(len(site.check_message('fix: ヘッダーを直す')), 1)
        self.assertEqual(len(site.check_message('feat(nav)!: ヘッダーを直す')), 1)
        self.assertEqual(len(site.check_message('# only a comment\n')), 1)

    def test_a_japanese_label_is_not_a_prefix(self):
        self.assertEqual(site.check_message('トップ: 文言を直す'), [])

    def test_custom_comment_character(self):
        self.assertEqual(site.check_message('; 件名を書いてください\nヘッダーを直す', comment=';'), [])

    def test_git_generated_messages_pass(self):
        for subject in ('Merge branch \'develop\'', 'Revert "ヘッダーを直す"', 'Reapply "Revert ' + '"x" ' * 20 + '"',
                        'fixup! ヘッダーを直す'):
            self.assertEqual(site.check_message(subject), [], subject)

class SiteTest(unittest.TestCase):
    def test_the_real_site_passes(self):
        self.assertEqual(site.check_site(), [])

    def test_a_broken_copy_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in {'docs/index.html': page(body='<img src="a.webp">'), 'docs/a.css': '.a{x:y !important}' * 99,
                               'scripts/x.py': 'import requests_not_installed\n'}.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(text)
            self.assertEqual(len(site.check_site(root)), 3)

if __name__ == '__main__':
    unittest.main()
