#!/usr/bin/env python3
"""Pick the next free work lane from WORKLANES.md so several workers can run at once.

Status is one character: o open, c claimed, x completed, b blocked (waiting on a person or thing).
A lane is free when it is open and every lane in its Needs column is completed.
The board lives in the main checkout (found through git's common dir), so every worktree sees one board.
"""
import argparse
from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime
import fcntl
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PROJECT = 'Nature capital real estate'
STATUSES = 'ocxb'
NONE_FREE = 3  # exit code when nothing can be picked
PORT_BASE = 8000  # the user's own preview server; lanes use PORT_BASE + row number

Row = namedtuple('Row', 'index line id status needs touches item who')
COLUMNS = ('ID', 'S', 'Needs', 'Touches', 'Item', 'Who')


class BoardError(Exception):
    pass


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def parse(text):
    """Return the lane rows of the board; raise BoardError on a malformed board."""
    rows, lines, in_table = [], text.splitlines(), False
    for i, line in enumerate(lines):
        if not line.startswith('|'):
            in_table = False
            continue
        parts = cells(line)
        if tuple(parts) == COLUMNS:
            in_table = True
            continue
        if not in_table or set(''.join(parts)) <= set('-: '):
            continue
        if len(parts) != len(COLUMNS):
            raise BoardError(f'line {i + 1}: expected {len(COLUMNS)} columns, got {len(parts)}')
        lane, status, needs, touches, item, who = parts
        if status not in STATUSES:
            raise BoardError(f'line {i + 1}: status {status!r} is not one of {STATUSES}')
        deps = tuple(d.strip() for d in needs.split(',') if d.strip() not in ('', '-'))
        rows.append(Row(len(rows) + 1, i, lane, status, deps, touches, item, who))
    ids = [r.id for r in rows]
    for r in rows:
        if ids.count(r.id) > 1:
            raise BoardError(f'lane {r.id} appears more than once')
        for d in r.needs:
            if d not in ids:
                raise BoardError(f'lane {r.id} needs unknown lane {d}')
            if d == r.id:
                raise BoardError(f'lane {r.id} needs itself')
    return rows


def waiting_on(row, rows):
    done = {r.id for r in rows if r.status == 'x'}
    return [d for d in row.needs if d not in done]


def free(rows):
    """Open lanes whose dependencies are all completed, in board order (board order is priority)."""
    return [r for r in rows if r.status == 'o' and not waiting_on(r, rows)]


def update(text, lane, status, who):
    """Return the board text with one lane's status and Who cell replaced."""
    rows = {r.id: r for r in parse(text)}
    if lane not in rows:
        raise BoardError(f'no lane {lane}')
    if status not in STATUSES:
        raise BoardError(f'status {status!r} is not one of {STATUSES}')
    lines = text.splitlines(keepends=True)
    r = rows[lane]
    end = '\n' if lines[r.line].endswith('\n') else ''
    parts = [r.id, status, ', '.join(r.needs) or '-', r.touches, r.item, who]
    lines[r.line] = '| ' + ' | '.join(parts) + ' |' + end
    return ''.join(lines)


def summary(rows):
    """Why nothing is free: one line per lane that is not completed."""
    out = []
    for r in rows:
        if r.status == 'c':
            out.append(f'  {r.id}: claimed ({r.who})')
        elif r.status == 'b':
            out.append(f'  {r.id}: blocked ({r.who or "see Item"})')
        elif r.status == 'o':
            out.append(f'  {r.id}: waiting on {", ".join(waiting_on(r, rows))}')
    return out


def instructions(row, root):
    """Commands for a claimed lane: its own worktree, branch and preview port."""
    slug = row.id.lower()
    tree = root.parent / f'{root.name}-{slug}'
    project = tree / PROJECT
    port = PORT_BASE + row.index
    return '\n'.join([
        f'Claimed {row.id}: {row.item}',
        f'Touches: {row.touches}',
        '',
        'Set up (run once; ask the user before anything that pushes):',
        f'  git -C "{root}" fetch origin',
        f'  git -C "{root}" worktree add -b lane/{slug} "{tree}" origin/develop',
        f'  docker run -d --rm --name ncre-{slug} -p 127.0.0.1:{port}:80 \\',
        f'    -v "{project}/docs":/usr/share/nginx/html:ro \\',
        f'    -v "{project}/maintenance/nginx.conf":/etc/nginx/conf.d/default.conf:ro nginx:1.27-alpine',
        f'Preview: http://localhost:{port}/__preview/  (use this port, not 8000)',
        f'Work in: {project}',
        f'When finished: python3 "{root / PROJECT}/scripts/worklane.py" mark {row.id} x',
        f'If you stop early: python3 "{root / PROJECT}/scripts/worklane.py" mark {row.id} o',
    ])


def main_checkout():
    common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True, check=True, cwd=Path(__file__).parent).stdout.strip()
    return Path(common).parent


@contextmanager
def locked(common_dir):
    with open(common_dir / 'worklanes.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield
        # released when the file closes


def write(board, text):
    fd, tmp = tempfile.mkstemp(dir=board.parent, prefix='.worklanes-')
    with os.fdopen(fd, 'w') as f:
        f.write(text)
    os.replace(tmp, board)


def run(args, board, common_dir, root, now, out=sys.stdout):
    with locked(common_dir):
        text = board.read_text()
        rows = parse(text)
        if args.command == 'list':
            for r in rows:
                print(f'{r.status} {r.id:<14} {r.item}', file=out)
            return 0
        if args.command == 'mark':
            who = args.note if args.note is not None else (
                f'{args.who} {now}' if args.status == 'c' else
                f'done {now}' if args.status == 'x' else '')
            write(board, update(text, args.lane, args.status, who))
            print(f'{args.lane} -> {args.status}', file=out)
            return 0
        choices = free(rows)
        if not choices:
            print('No work lanes are available. Stop here unless you are given further instructions.', file=out)
            print('\n'.join(summary(rows)), file=out)
            return NONE_FREE
        row = choices[0]
        if args.dry_run:
            print(f'Would claim {row.id}: {row.item}', file=out)
            return 0
        write(board, update(text, row.id, 'c', f'{args.who} {now}'))
        print(instructions(row._replace(status='c'), root), file=out)
        return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--board', type=Path, help='board file (default: WORKLANES.md in the main checkout)')
    sub = p.add_subparsers(dest='command')
    pick = sub.add_parser('pick', help='claim the next free lane (the default)')
    sub.add_parser('list', help='show every lane and its status')
    mark = sub.add_parser('mark', help='set one lane to o, c, x or b')
    mark.add_argument('lane')
    mark.add_argument('status', choices=list(STATUSES))
    mark.add_argument('--note', help='text for the Who column (e.g. what a blocked lane waits for)')
    for s in (p, pick, mark):
        s.add_argument('--who', default=os.environ.get('USER', 'worker'), help='name recorded on a claim')
    for s in (p, pick):
        s.add_argument('--dry-run', action='store_true', help='show the lane without claiming it')
    args = p.parse_args(argv)
    args.command = args.command or 'pick'
    root = main_checkout()
    common_dir = root / '.git'
    board = args.board or root / PROJECT / 'WORKLANES.md'
    try:
        return run(args, board, common_dir, root, datetime.now().strftime('%Y-%m-%d %H:%M'))
    except BoardError as e:
        print(f'WORKLANES.md: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
