#!/usr/bin/env python3
"""Check that every local link, image, fragment and CSS url() in docs/ resolves; external links are optional."""
import argparse
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import os
import posixpath
import re
from urllib.error import HTTPError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

DOCS = Path(__file__).resolve().parents[1] / 'docs'
PREFIX = '/fudousanbusiness-jgx/'
HOST = 'yuyakawamura-blip.github.io'
PUBLIC = 'https://' + HOST + PREFIX
CSS_URL = re.compile(r'''url\(\s*(['"]?)(.*?)\1\s*\)|@import\s+(['"])(.*?)\3''')

Problem = namedtuple('Problem', 'file line link reason')
Ref = namedtuple('Ref', 'file line link base kind')

class Page(HTMLParser):
    def __init__(self, file):
        super().__init__(convert_charrefs=True)
        self.file, self.base, self.ids, self.refs, self.og_url = file, None, set(), [], None

    def handle_starttag(self, tag, attrs):
        a, line = dict(attrs), self.getpos()[0]
        if a.get('id'): self.ids.add(a['id'])
        if tag == 'a' and a.get('name'): self.ids.add(a['name'])
        if tag == 'base' and a.get('href'): self.base = a['href']
        for key in ('href', 'src'):
            if a.get(key) and tag != 'base': self.refs.append((line, a[key].strip(), 'link'))
        for item in (a.get('srcset') or '').split(','):
            if item.strip(): self.refs.append((line, item.split()[0], 'link'))
        if tag == 'meta' and public_path(a.get('content') or ''):
            self.refs.append((line, a['content'], 'meta'))
        if tag == 'meta' and a.get('property') == 'og:url': self.og_url = (line, a.get('content') or '')

    handle_startendtag = handle_starttag

def public_path(link):
    """Return the site path of a link to the public site in any spelling (http, //, capitals), else None."""
    parts = urlsplit(link)
    if parts.scheme in ('', 'http', 'https') and parts.netloc.lower() == HOST and (parts.path + '/').startswith(PREFIX):
        return parts.path + ('#' + parts.fragment if parts.fragment else '')
    return None

def is_external(link):
    return (link.startswith('//') or urlsplit(link).scheme in ('http', 'https')) and not public_path(link)

def exists(root, rel):
    """True only when every part of rel matches a real name exactly: GitHub Pages is case-sensitive, macOS is not."""
    here = root
    for name in filter(None, rel.split('/')):
        if not here.is_dir() or name not in os.listdir(here):
            return False
        here = here / name
    return True

def scan(root):
    """Parse every page and stylesheet; return pages by path and every reference found."""
    pages, refs = {}, []
    for path in sorted(root.rglob('*.html')):
        rel = path.relative_to(root).as_posix()
        page = pages[rel] = Page(rel)
        page.feed(path.read_text(encoding='utf-8'))
        refs += [Ref(rel, line, link, page.base, kind) for line, link, kind in page.refs]
    for path in sorted(root.rglob('*.css')):
        rel, text = path.relative_to(root).as_posix(), path.read_text(encoding='utf-8')
        # Blank out comments but keep their line breaks, so line numbers stay true.
        text = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m[0]), text, flags=re.S)
        for m in CSS_URL.finditer(text):
            refs.append(Ref(rel, text.count('\n', 0, m.start()) + 1, (m[2] or m[4] or '').strip(), None, 'css'))
    return pages, refs

def resolve(root, ref):
    """Return (target path, fragment, reason); a reason means the reference is broken."""
    parts = urlsplit(public_path(ref.link) or ref.link)
    path, fragment = unquote(parts.path), unquote(parts.fragment)
    if ref.base:
        if not ref.base.startswith(PREFIX):
            return None, None, 'unsupported <base>'
        here = posixpath.dirname(ref.base[len(PREFIX):])  # A base naming a file resolves from its folder.
    else:
        here = posixpath.dirname(ref.file)
    if not path and not ref.base:
        return ref.file, fragment, None
    if path.startswith('/'):
        if not (path + '/').startswith(PREFIX):
            return None, None, 'outside the site'
        joined = path[len(PREFIX):]
    else:
        joined = posixpath.join(here, path)
    target = posixpath.normpath(joined) if joined else '.'
    if target == '..' or target.startswith('../'):
        return None, None, 'outside the site'
    target = '' if target == '.' else target
    if exists(root, target) and (root / target).is_dir():
        target = posixpath.join(target, 'index.html')
    elif path.endswith('/'):
        return None, None, 'missing file'  # GitHub Pages answers 404 for file.html/.
    if not exists(root, target) or not (root / target).is_file():
        return None, None, 'missing file'
    return target, fragment, None

def check(root):
    pages, refs = scan(root)
    problems = []
    for ref in refs:
        if not ref.link or ref.link.startswith('#') and ref.kind == 'css' or is_external(ref.link):
            continue
        if urlsplit(ref.link).scheme and not public_path(ref.link):
            continue  # mailto:, tel:, data: and the like.
        target, fragment, reason = resolve(root, ref)
        # Browsers scroll to the top for #top even without an element of that id.
        if not reason and fragment and fragment.lower() != 'top' and target in pages and fragment not in pages[target].ids:
            reason = 'missing fragment'
        if reason:
            problems.append(Problem(ref.file, ref.line, ref.link, reason))
    for rel, page in pages.items():
        if page.og_url and page.og_url[1] != PUBLIC + (rel[:-len('index.html')] if rel.endswith('index.html') else rel):
            problems.append(Problem(rel, page.og_url[0], page.og_url[1], 'og:url is not this page'))
    return sorted(problems, key=lambda p: (p.file, p.line))

def external(root):
    found = {}
    for ref in scan(root)[1]:
        if ref.kind != 'meta' and is_external(ref.link):
            found.setdefault(ref.link, []).append((ref.file, ref.line))
    return found

def probe(url, opener=urlopen):
    """Return None when the URL answers below 400, otherwise a short reason."""
    try:
        req = Request(url, headers={'User-Agent': 'NatureCapital-LinkCheck/1.0'})
        with opener(req, timeout=20) as response:
            return None if response.status < 400 else f'HTTP {response.status}'
    except HTTPError as error:
        return f'HTTP {error.code}'
    except Exception as error:
        return f'{type(error).__name__}: {error}'

def main(argv=None, probe=probe):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=DOCS, help='Site folder (default: docs/)')
    parser.add_argument('--external', action='store_true', help='Also request each external URL; failures are warnings only')
    args = parser.parse_args(argv)
    pages, refs = scan(args.root)
    problems = check(args.root)
    for p in problems:
        print(f'{p.file}:{p.line}: {p.link} ({p.reason})')
    sheets = len(list(args.root.rglob('*.css')))
    print(f'{len(refs)} references in {len(pages)} pages and {sheets} stylesheets; {len(problems)} broken')
    if args.external:
        found = external(args.root)
        with ThreadPoolExecutor(8) as pool:
            results = dict(zip(found, pool.map(probe, found)))
        warnings = {url: reason for url, reason in results.items() if reason}
        for url, reason in warnings.items():
            file, line = found[url][0]
            print(f'warning: {url} ({reason}) first used at {file}:{line}')
        print(f'{len(found)} external URLs; {len(warnings)} did not answer normally')
    return 1 if problems else 0

if __name__ == '__main__':
    raise SystemExit(main())
