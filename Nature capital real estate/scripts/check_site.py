#!/usr/bin/env python3
"""Check the written rules in AGENTS.md and maintenance/design.md that a script can check.

Run with no options for the contents of the site, with --staged for what is about to be committed
(the pre-commit hook runs both), with --range BASE for every commit pushed since BASE (CI), or with
--commit-msg FILE from the commit-msg hook.
"""
import argparse
import ast
from html.parser import HTMLParser
import importlib.util
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import sysconfig

SITE = Path(__file__).resolve().parents[1]
DOCS = SITE / 'docs'
PROJECT = SITE.name
SUFFIX_JA = ' | ネイチャーキャピタル・リアルエステイト'
SUFFIX_EN = ' | Nature Capital Real Estate'
HEAD = {'icon', 'apple-touch-icon'}
OGP = {'og:type', 'og:site_name', 'og:title', 'og:description', 'og:url', 'og:image', 'og:locale', 'twitter:card'}
NO_OGP = {'404.html'}  # Not shared and not indexed (robots noindex).
EXTERNAL = re.compile(r'^(https?:)?//', re.I)
PUBLIC = re.compile(r'^(https?:)?//yuyakawamura-blip\.github\.io/fudousanbusiness-jgx/', re.I)  # This site itself.
# Counts in today's code that the rules say not to add to. A commit may lower them, never raise them;
# when one goes down, lower it here too so it cannot creep back.
BASELINE = {'!important in CSS': 9, 'var in JS': 6, 'innerHTML in JS': 1}
PATTERNS = {'!important in CSS': ('.css', re.compile(r'!\s*important')),
            'var in JS': ('.js', re.compile(r'\bvar\s')),
            'innerHTML in JS': ('.js', re.compile(r'\binnerHTML\b'))}
ROOT_FILES = {'CLAUDE.md', 'AGENTS.md', '.gitignore'}
ROOT_DIRS = {'.github', '.githooks', '.claude'}
NEW_IMAGE = {'.webp', '.svg'}
IMAGE = NEW_IMAGE | {'.png', '.jpg', '.jpeg', '.gif', '.avif', '.bmp', '.tif', '.tiff'}
KEBAB = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
MAX_IMAGE = 300 * 1024
JAPANESE = re.compile(r'[぀-ヿ㐀-鿿]')
PREFIX = re.compile(r'^[A-Za-z]+(\([^)]*\))?!?:\s')
AUTO_MESSAGE = re.compile(r'^(Merge |Revert "|Reapply "|fixup! |squash! |amend! )')
BOT = 'github-actions[bot]'  # Commits catalog.json on main with an English message.
IN_PROGRESS = ('MERGE_HEAD', 'REVERT_HEAD', 'CHERRY_PICK_HEAD')  # Their changes were checked where they were made.


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title, self.head, self.problems = '', False, set(), []

    def handle_starttag(self, tag, attrs):
        a, line = dict(attrs), self.getpos()[0]
        if tag == 'title': self.in_title = True
        if tag == 'link': self.head.update((a.get('rel') or '').split())
        if tag == 'meta' and (a.get('property') or a.get('name')): self.head.add(a.get('property') or a.get('name'))
        if tag == 'img' and 'alt' not in a: self.problems.append((line, '<img> has no alt (use alt="" for decoration)'))
        handlers = sorted(k for k in a if k.startswith('on'))
        if handlers: self.problems.append((line, f'inline event handler {", ".join(handlers)} (design.md §16)'))
        href = (a.get('href') or '').strip()
        if tag == 'a' and EXTERNAL.match(href) and not PUBLIC.match(href):
            rel = set((a.get('rel') or '').lower().split())
            if a.get('target') != '_blank' or not {'noopener', 'noreferrer'} <= rel:
                self.problems.append((line, 'external link needs target="_blank" rel="noopener noreferrer"'))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False

    def handle_data(self, data):
        if self.in_title: self.title += data


def check_page(rel, text):
    """Return (line, reason) for each rule the page breaks; rel is the path inside docs/."""
    page = Page()
    page.feed(text)
    problems = list(page.problems)
    title = ' '.join(page.title.split())
    suffix = SUFFIX_EN if '/en/' in '/' + rel else SUFFIX_JA
    if not title.endswith(suffix) or title == suffix.lstrip(' |'):
        problems.append((1, f'<title> should be "page name{suffix}"'))
    wanted = HEAD if rel in NO_OGP else HEAD | OGP
    for name in sorted(wanted - page.head):
        problems.append((1, f'<head> is missing {name} (copy the head of an existing page)'))
    return problems


def count_patterns(files):
    """files maps a path to its text; return how many times each PATTERNS entry occurs."""
    counts = dict.fromkeys(PATTERNS, 0)
    for path, text in files.items():
        for name, (ext, pattern) in PATTERNS.items():
            if path.endswith(ext):
                counts[name] += len(pattern.findall(text))
    return counts


def over_baseline(counts, baseline=BASELINE):
    return [f'{name}: {counts[name]} (baseline {baseline[name]}); remove the new one'
            for name in counts if counts[name] > baseline[name]]


def imported_modules(source):
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names.add(node.module.split('.')[0])
    return names


def is_stdlib(name):
    if name in getattr(sys, 'stdlib_module_names', ()) or name in sys.builtin_module_names:
        return True
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.origin:
        return False
    origin = Path(spec.origin).resolve()
    stdlib = Path(sysconfig.get_paths()['stdlib']).resolve()
    return stdlib in origin.parents and 'site-packages' not in origin.parts


def check_staged(paths, added, sizes, deleted=()):
    """paths: every changed path from the repo root; added and deleted: those added or removed (count a rename
    as both); sizes: bytes of added files. Return (problems, warnings)."""
    problems, warnings = [], []
    for path in paths:
        parts = PurePosixPath(path).parts
        if parts[0] == PROJECT:
            if len(parts) > 1 and parts[1] == 'archive':
                problems.append(f'{path}: archive/ is not edited (AGENTS.md Don\'ts)')
        elif path not in deleted and not (path in ROOT_FILES or parts[0] in ROOT_DIRS):
            problems.append(f'{path}: outside this site; commit it in its own repository (AGENTS.md Deploy)')
    for path in added:
        p = PurePosixPath(path)
        if p.parts[:2] != (PROJECT, 'docs') or p.suffix.lower() not in IMAGE:
            continue
        if p.suffix.lower() not in NEW_IMAGE:
            problems.append(f'{path}: new images are WebP (AGENTS.md Conventions)')
        if not KEBAB.match(p.stem):
            problems.append(f'{path}: image names are lower-case kebab-case')
        if sizes.get(path, 0) > MAX_IMAGE:
            warnings.append(f'{path}: {sizes[path] // 1024} KB is over the 300 KB guide')
    return problems, warnings


def check_message(message, comment='#'):
    """Return the reasons the commit subject breaks the AGENTS.md rule (Japanese, 50 characters, no prefix)."""
    lines = [l for l in message.splitlines() if not l.startswith(comment)]
    subject = next((l.strip() for l in lines if l.strip()), '')
    if AUTO_MESSAGE.match(subject):
        return []
    problems = []
    if not subject:
        problems.append('the subject line is empty')
    if len(subject) > 50:
        problems.append(f'the subject line is {len(subject)} characters; keep it to 50')
    if subject and not JAPANESE.search(subject):
        problems.append('write the subject in Japanese')
    if PREFIX.match(subject):
        problems.append('drop the prefix (feat:, fix: and the like)')
    return problems


def site_files(docs):
    return [p for p in sorted(docs.rglob('*')) if p.is_file() and 'vendor' not in p.relative_to(docs).parts]


def check_site(site=SITE):
    docs, problems = site / 'docs', []
    files = site_files(docs)
    for path in files:
        if path.suffix == '.html':
            rel = path.relative_to(docs).as_posix()
            problems += [f'docs/{rel}:{line}: {reason}' for line, reason in check_page(rel, path.read_text(encoding='utf-8'))]
    texts = {p.relative_to(docs).as_posix(): p.read_text(encoding='utf-8') for p in files if p.suffix in ('.css', '.js')}
    problems += over_baseline(count_patterns(texts))
    for path in sorted((site / 'scripts').glob('*.py')) + sorted((site / 'tests').glob('*.py')):
        for name in sorted(imported_modules(path.read_text(encoding='utf-8'))):
            if not is_stdlib(name):
                problems.append(f'{path.relative_to(site)}: imports {name}; use the standard library only (design.md §17)')
    return problems


def git(*args, cwd=SITE):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def check_changes(diff, size_of):
    """Check the paths of one git diff (its arguments in diff); size_of(path) gives an added file's bytes."""
    root = Path(git('rev-parse', '--show-toplevel').strip())
    # --no-renames: a moved file counts as added, so a rename cannot slip past the image rules.
    names = lambda *f: [p for p in git('diff', '--no-renames', '--name-only', '-z', *f, *diff, cwd=root).split('\0') if p]
    added = names('--diff-filter=A')
    sizes = {p: size_of(p) for p in added if PurePosixPath(p).suffix.lower() in IMAGE}  # Submodules have no size.
    return check_staged(names(), added, sizes, set(names('--diff-filter=D')))


def git_size(rev):
    return lambda path: int(git('cat-file', '-s', f'{rev}:{path}').strip())


def staged():
    git_dir = Path(git('rev-parse', '--absolute-git-dir').strip())
    if any((git_dir / name).exists() for name in IN_PROGRESS):
        return [], []
    return check_changes(['--cached'], git_size(''))


def pushed(base):
    """Check the paths and commit messages of base..HEAD."""
    problems, warnings = check_changes([base, 'HEAD'], git_size('HEAD'))
    log = git('log', '--no-merges', '--format=%h%x1f%an%x1f%B%x1e', f'{base}..HEAD')
    for record in filter(str.strip, log.split('\x1e')):
        sha, author, message = record.strip('\n').split('\x1f', 2)
        if author != BOT:
            problems += [f'commit {sha}: {p}' for p in check_message(message)]
    return problems, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--staged', action='store_true', help='check only the paths staged for commit')
    mode.add_argument('--range', metavar='BASE', help='check only the paths and messages of BASE..HEAD')
    mode.add_argument('--commit-msg', type=Path, metavar='FILE', help='check only this commit message file')
    args = parser.parse_args(argv)
    if args.commit_msg:
        comment = subprocess.run(['git', 'config', 'core.commentChar'], capture_output=True, text=True).stdout.strip()
        problems = check_message(args.commit_msg.read_text(encoding='utf-8'), comment if len(comment) == 1 else '#')
        for p in problems:
            print(f'commit message: {p}', file=sys.stderr)
        return 1 if problems else 0
    if args.staged:
        problems, warnings = staged()
    elif args.range:
        problems, warnings = pushed(args.range)
    else:
        problems, warnings = check_site(), []
    for w in warnings:
        print(f'warning: {w}', file=sys.stderr)
    for p in problems:
        print(p, file=sys.stderr)
    print(f'site rules: {len(problems)} problems, {len(warnings)} warnings')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
