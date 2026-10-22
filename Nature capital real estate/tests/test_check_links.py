"""Contract tests for the offline link check and the optional external probe."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('check_links', Path(__file__).parents[1] / 'scripts/check_links.py')
links = importlib.util.module_from_spec(spec)
spec.loader.exec_module(links)

PUBLIC = 'https://yuyakawamura-blip.github.io/fudousanbusiness-jgx/'

def site(tmp, files):
    root = Path(tmp)
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root

def page(body='', head=''):
    return f'<!doctype html><html><head>{head}</head><body>\n{body}\n</body></html>'

def reasons(problems):
    return [(p.file, p.link, p.reason) for p in problems]

class LocalTest(unittest.TestCase):
    def test_valid_site_has_no_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {
                'index.html': page('<a href="about/">a</a><a href="about/#team">t</a><a href="#top">top</a>'
                                   '<img src="assets/a.webp" srcset="assets/a.webp 1x, assets/b.webp 2x" alt="">'
                                   '<a href="https://example.org/">x</a><a href="mailto:a@example.org">m</a>'
                                   '<section id="top"></section>',
                                   f'<link rel="stylesheet" href="styles.css"><meta property="og:url" content="{PUBLIC}">'),
                'about/index.html': page('<h2 id="team">T</h2><a href="../">home</a><a href="../about">same</a>',
                                         f'<meta property="og:url" content="{PUBLIC}about/">'
                                         f'<meta property="og:image" content="{PUBLIC}assets/a.webp">'),
                'styles.css': '.a { background: url("assets/a.webp"); }\n.b { behavior: url(#default#VML); }',
                'assets/a.webp': '', 'assets/b.webp': ''})
            self.assertEqual(links.check(root), [])

    def test_missing_file_reports_file_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<p>\n<a href="gone/">x</a></p>')})
            [problem] = links.check(root)
            self.assertEqual((problem.file, problem.line, problem.link), ('index.html', 3, 'gone/'))

    def test_missing_fragment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<a href="#nowhere">x</a><a href="about/#gone">y</a>'),
                              'about/index.html': page('<h2 id="team">T</h2>')})
            self.assertEqual([p.link for p in links.check(root)], ['#nowhere', 'about/#gone'])

    def test_links_must_stay_inside_the_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            # outside.html exists on disk but is not published, so linking to it is broken.
            site(tmp, {'docs/index.html': page('<a href="../outside.html">x</a><a href="/other/">y</a>'),
                       'outside.html': ''})
            self.assertEqual(reasons(links.check(Path(tmp) / 'docs')),
                             [('index.html', '../outside.html', 'outside the site'),
                              ('index.html', '/other/', 'outside the site')])

    def test_base_href_resolves_from_site_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            # 404.html is served for missing paths at any depth, so it pins links with <base>.
            root = site(tmp, {'deep/404.html': page('<a href="about/">a</a><img src="assets/a.webp" alt="">',
                                                    '<base href="/fudousanbusiness-jgx/" />'),
                              'about/index.html': page(), 'assets/a.webp': ''})
            self.assertEqual(links.check(root), [])

    def test_css_url_resolves_from_the_css_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'vendor/map.css': '.ok { background: url(images/ok.png); }\n.bad { background: url(images/gone.png); }',
                              'vendor/images/ok.png': ''})
            self.assertEqual(reasons(links.check(root)), [('vendor/map.css', 'images/gone.png', 'missing file')])

    def test_ogp_must_point_at_real_files_and_the_page_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page(),
                              'about/index.html': page(head=f'<meta property="og:url" content="{PUBLIC}">'
                                                            f'<meta property="og:image" content="{PUBLIC}assets/gone.jpg">')})
            self.assertEqual(sorted(p.reason for p in links.check(root)), ['missing file', 'og:url is not this page'])

    def test_og_url_on_another_site_is_not_this_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page(head='<meta property="og:url" content="https://example.com/wrong/">')})
            self.assertEqual(reasons(links.check(root)), [('index.html', 'https://example.com/wrong/', 'og:url is not this page')])

    def test_file_names_are_case_sensitive_like_github_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<a href="About/">a</a><img src="assets/A.webp" alt="">'),
                              'about/index.html': page(), 'assets/a.webp': ''})
            self.assertEqual([p.link for p in links.check(root)], ['About/', 'assets/A.webp'])

    def test_public_url_in_any_spelling_is_checked_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            host = 'yuyakawamura-blip.github.io/fudousanbusiness-jgx/'
            root = site(tmp, {'index.html': page(f'<a href="HTTPS://{host}gone1/">a</a><a href="//{host}gone2/">b</a>'
                                                 f'<a href="http://{host}gone3/">c</a><a href="//{host}">ok</a>')})
            self.assertEqual(len(links.check(root)), 3)
            self.assertEqual(links.external(root), {})

    def test_trailing_slash_after_a_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<a href="other.html/">x</a>'), 'other.html': page()})
            self.assertEqual(reasons(links.check(root)), [('index.html', 'other.html/', 'missing file')])

    def test_base_naming_a_file_resolves_from_its_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'about/index.html': page('<img src="x.webp" alt="">', '<base href="/fudousanbusiness-jgx/about/index.html">'),
                              'about/x.webp': ''})
            self.assertEqual(links.check(root), [])

    def test_css_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'styles.css': '/* .old {\n background: url(old.png); } */\n.new { background: url(gone.png); }'})
            self.assertEqual([(p.link, p.line) for p in links.check(root)], [('gone.png', 3)])

class ExternalTest(unittest.TestCase):
    def test_external_links_are_collected_not_checked_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<a href="https://example.org/">x</a>\n<a href="https://example.org/">y</a>'),
                              'styles.css': '@import url("https://fonts.example.org/css");'})
            self.assertEqual(links.check(root), [])
            found = links.external(root)
            self.assertEqual(sorted(found), ['https://example.org/', 'https://fonts.example.org/css'])
            self.assertEqual(found['https://example.org/'], [('index.html', 2), ('index.html', 3)])

    def test_failed_probe_is_a_warning_with_a_reason(self):
        def opener(request, timeout):
            raise links.HTTPError(request.full_url, 404, 'Not Found', {}, None)
        self.assertEqual(links.probe('https://example.org/', opener), 'HTTP 404')

    def test_external_failures_do_not_fail_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = site(tmp, {'index.html': page('<a href="https://example.org/">x</a>')})
            self.assertEqual(links.main([str(root), '--external'], probe=lambda url: 'HTTP 500'), 0)
            (root / 'index.html').write_text(page('<a href="gone/">x</a>'))
            self.assertEqual(links.main([str(root)]), 1)

if __name__ == '__main__': unittest.main()
