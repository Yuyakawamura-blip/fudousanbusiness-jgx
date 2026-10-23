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
import re
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile

PROJECT = 'Nature capital real estate'
STATUSES = 'ocxb'
NONE_FREE = 3  # exit code when nothing can be picked
PORT_FIRST, PORT_LAST = 8001, 8999  # 8000 is the user's own preview server

# An open PLAN.md item names the lanes that cover it, or none; check_site.py rejects a new item without the tag.
OPEN_ITEM = re.compile(r'^\s*(?:[-*]|\d+\.)\s+\[ \]')  # same patterns in check_site.py
LANE_TAG = re.compile(r'<!-- lane: ([^>]*?) -->')

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


def add(text, lane, needs, touches, item, status='o', who='', before=None):
    """Return the board text with a new lane row, at the end or just above lane `before`.

    The whole board is checked again afterwards, so an unknown Needs or a repeated ID writes nothing.
    """
    rows = parse(text)
    if not rows:
        raise BoardError('the board has no lanes to add after; add the first row by hand')
    if status not in ('o', 'b'):
        raise BoardError(f'a new lane starts as o or b, not {status!r}')
    if status == 'b' and not who:
        raise BoardError('a blocked lane needs --note saying what it waits for')
    parts = [lane, status, ', '.join(needs) or '-', touches, item, who]
    for name, value in zip(COLUMNS, parts):
        if '|' in value or len(value.splitlines()) > 1:  # splitlines also breaks on \r and U+2028
            raise BoardError(f'{name} cannot contain "|" or a line break')
    if not lane or lane.split() != [lane]:
        raise BoardError(f'lane ID {lane!r} must be one word')
    if before is None:
        at = rows[-1].line + 1
    else:
        found = [r for r in rows if r.id == before]
        if not found:
            raise BoardError(f'no lane {before} to add before')
        at = found[0].line
    lines = text.splitlines(keepends=True)
    if not lines[at - 1].endswith('\n'):
        lines[at - 1] += '\n'
    lines.insert(at, '| ' + ' | '.join(parts) + ' |\n')
    new = ''.join(lines)
    parse(new)
    return new


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


def plan_gaps(plan, rows):
    """Open PLAN.md items the board cannot hand out: no lane tag, or a tag naming a lane with no row."""
    ids, gaps = {r.id for r in rows}, []
    for n, line in enumerate(plan.splitlines(), 1):
        if not OPEN_ITEM.match(line):
            continue
        tag = LANE_TAG.search(line)
        missing = [t for t in map(str.strip, tag.group(1).split(',')) if t not in ids | {'none'}] if tag else []
        if tag and not missing:
            continue
        why = f'no row for {", ".join(missing)}' if tag else 'no lane tag'
        gaps.append(f'  PLAN.md:{n} ({why}): {OPEN_ITEM.sub("", LANE_TAG.sub("", line)).strip()[:60]}')
    return gaps


def read_plan(root):
    """PLAN.md as pushed (rows are added only for items already on develop); None and the reason if unreadable."""
    shown = git(root, 'show', f'origin/develop:{PROJECT}/PLAN.md')
    return (shown.stdout, None) if not shown.returncode else (None, shown.stderr.strip())


def report_plan(rows, root, plan, out):
    text, error = plan(root)
    if text is None:
        print(f'\nPLAN.md not checked against the board: {error}', file=out)
        return
    gaps = plan_gaps(text, rows)
    if gaps:
        print('\nOpen PLAN.md items on origin/develop that no lane covers. Add a row with `worklane.py add <ID>`'
              ' and tag the item <!-- lane: <ID> -->, or tag it <!-- lane: none -->:', *gaps, sep='\n', file=out)


def host_port_free(port):
    """Whether nothing (another lane's container included) listens on this port of the host."""
    with socket.socket() as s:
        try:
            s.bind(('127.0.0.1', port))
        except OSError:
            return False
    return True


def choose_port(rows, port_free):
    """The lowest preview port that no claimed or blocked lane has recorded and nothing on the host is using.

    Row numbers are not used: a row added above a claimed lane would hand its port to the next claim.
    """
    taken = {int(m) for r in rows if r.status in 'cb' for m in re.findall(r'\bport (\d+)\b', r.who)}
    for port in range(PORT_FIRST, PORT_LAST + 1):
        if port not in taken and port_free(port):
            return port
    raise BoardError(f'no free preview port in {PORT_FIRST}-{PORT_LAST}')


def session_name(now):
    """A name for a worker that gave none: the minute it started plus 4 random hex digits (1 in 65536 to repeat).

    Agents asked to make up "random" digits tend to repeat the same ones, so the randomness comes from here.
    """
    return f'claude-{now:%m%d-%H%M}-{secrets.token_hex(2)}'


def instructions(row, root, port):
    """Commands for a claimed lane: its own worktree, branch and preview port."""
    slug = row.id.lower()
    tree = root.parent / f'{root.name}-{slug}'
    project = tree / PROJECT
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
        f'When pushed: python3 "{root / PROJECT}/scripts/worklane.py" finish {row.id}  (from outside the worktree;'
        ' stops the preview, removes the worktree and branch, marks the lane x)',
        f'If you stop early: python3 "{root / PROJECT}/scripts/worklane.py" mark {row.id} o',
    ])


def git(cwd, *args):
    return subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, text=True)


def docker_stop(name):
    # A container that is not running is already in the state we want, so the result is ignored.
    subprocess.run(['docker', 'stop', name], capture_output=True)


def finish(lane, root, stop=docker_stop):
    """Clean up a pushed lane; raise BoardError, touching nothing, when cleanup could lose work."""
    slug = lane.lower()
    tree, branch = root.parent / f'{root.name}-{slug}', f'lane/{slug}'
    if Path.cwd().resolve().is_relative_to(tree.resolve()):
        raise BoardError(f'run finish from outside {tree}; it removes that folder')
    if git(root, 'fetch', 'origin').returncode:
        raise BoardError('git fetch origin failed, so it cannot be checked that the lane was pushed')
    git(root, 'worktree', 'prune')  # forget a worktree whose folder was deleted by hand, so its branch can go
    if tree.exists():
        status = git(tree, 'status', '--porcelain', '--ignored')
        if status.returncode:
            raise BoardError(f'git status failed in {tree}: {status.stderr.strip()}')
        # Ignored files count: .env* and *.pem are ignored here. Finder's .DS_Store is the one exception.
        left = [l[3:] for l in status.stdout.splitlines() if Path(l[3:].rstrip('/')).name != '.DS_Store']
        if left:
            raise BoardError(f'{tree} has uncommitted or ignored files ({", ".join(left[:5])}); '
                             'commit and push them, or remove them yourself')
        # HEAD, not just the branch: a commit made on a detached HEAD or another branch lives only here.
        if git(tree, 'merge-base', '--is-ancestor', 'HEAD', 'origin/develop').returncode:
            raise BoardError(f'the commit checked out in {tree} is not in origin/develop; push it first')
    has_branch = not git(root, 'rev-parse', '--verify', '--quiet', f'refs/heads/{branch}').returncode
    if has_branch and git(root, 'merge-base', '--is-ancestor', branch, 'origin/develop').returncode:
        raise BoardError(f'{branch} has commits that are not in origin/develop; push them first')
    if tree.exists():
        removed = git(root, 'worktree', 'remove', str(tree))
        if removed.returncode:
            raise BoardError(f'git worktree remove {tree} failed: {removed.stderr.strip()}')
    # From here nothing can lose work, so the remaining steps report rather than refuse.
    notes = []
    if has_branch and git(root, 'branch', '-D', branch).returncode:  # safe: all in origin/develop
        notes.append(f'could not delete {branch}')
    stop(f'ncre-{slug}')
    return f'Removed {tree} and {branch}, stopped ncre-{slug}' + ''.join(f'; {n}' for n in notes)


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


def run(args, board, common_dir, root, now, out=sys.stdout, stop=docker_stop, port_free=host_port_free,
        plan=read_plan):
    if args.command == 'finish':
        rows = {r.id: r for r in parse(board.read_text())}
        if args.lane not in rows:
            raise BoardError(f'no lane {args.lane}')
        if rows[args.lane].status != 'c':
            # A typo must not close (and so unblock the dependants of) a lane nobody worked on.
            print(f'Not finished: {args.lane} is not claimed (status {rows[args.lane].status})', file=out)
            return 1
        try:
            done = finish(args.lane, root, stop)  # outside the lock: fetch can be slow, other workers keep picking
        except BoardError as e:
            print(f'Not finished: {e}', file=out)
            return 1
        with locked(common_dir):
            write(board, update(board.read_text(), args.lane, 'x', f'done {now}'))
        print(f'{done}; {args.lane} -> x', file=out)
        return 0
    with locked(common_dir):
        text = board.read_text()
        rows = parse(text)
        if args.command == 'list':
            for r in rows:
                print(f'{r.status} {r.id:<14} {r.item}', file=out)
            report_plan(rows, root, plan, out)
            return 0
        if args.command == 'add':
            needs = [d.strip() for d in args.needs.split(',') if d.strip() not in ('', '-')]
            write(board, add(text, args.lane, needs, args.touches, args.item, args.status, args.note or '',
                             args.before))
            print(f'Added {args.lane} ({args.status})' + (f' above {args.before}' if args.before else ''), file=out)
            return 0
        if args.command == 'mark':
            who = args.note if args.note is not None else (
                f'{args.who} {now}' if args.status == 'c' else
                f'done {now}' if args.status == 'x' else '')
            old = {r.id: r for r in rows}.get(args.lane)
            port = old and old.status in 'cb' and re.search(r'\bport \d+\b', old.who)
            # choose_port reads ports from c and b lanes, so a mark must not drop one while the lane still holds it.
            if port and args.status in 'cb' and not re.search(r'\bport \d+\b', who):
                who = f'{who} {port.group()}'.strip()
            write(board, update(text, args.lane, args.status, who))
            print(f'{args.lane} -> {args.status}', file=out)
            if args.status == 'c' and args.note is None:
                print(f'Claimed as: {args.who}  (reuse this name with --who)', file=out)
            return 0
        choices = free(rows)
        if not choices:
            print('No work lanes are available. Stop here unless you are given further instructions.', file=out)
            print('\n'.join(summary(rows)), file=out)
            report_plan(rows, root, plan, out)  # the usual reason nothing is free: work that never got a row
            return NONE_FREE
        row = choices[0]
        if args.dry_run:
            print(f'Would claim {row.id}: {row.item}', file=out)
            return 0
        port = choose_port(rows, port_free)  # inside the lock, and recorded, so two claims never share a port
        write(board, update(text, row.id, 'c', f'{args.who} {now} port {port}'))
        print(instructions(row._replace(status='c'), root, port), file=out)
        print(f'Claimed as: {args.who}  (reuse this name with --who)', file=out)
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
    new = sub.add_parser('add', help='add a lane for work found while doing another lane')
    new.add_argument('lane')
    new.add_argument('--touches', required=True, help='files and lines the work changes')
    new.add_argument('--item', required=True, help='what to do, ending with where it was found')
    new.add_argument('--needs', default='-', help='comma-separated lanes that must finish first')
    new.add_argument('--status', choices=['o', 'b'], default='o', help='b when it waits on a person or thing')
    new.add_argument('--note', help='text for the Who column (required with --status b)')
    new.add_argument('--before', help='insert above this lane (board order is priority); default: at the end')
    done = sub.add_parser('finish', help='after pushing: stop the preview, remove the worktree and branch, mark x')
    done.add_argument('lane')
    for s in (p, pick, mark):
        s.add_argument('--who', help='name recorded on a claim (default: a new claude-MMDD-HHMM-hex4 name)')
    for s in (p, pick):
        s.add_argument('--dry-run', action='store_true', help='show the lane without claiming it')
    args = p.parse_args(argv)
    args.command = args.command or 'pick'
    now = datetime.now()
    args.who = getattr(args, 'who', None) or session_name(now)
    root = main_checkout()
    common_dir = root / '.git'
    board = args.board or root / PROJECT / 'WORKLANES.md'
    try:
        return run(args, board, common_dir, root, now.strftime('%Y-%m-%d %H:%M'))
    except BoardError as e:
        print(f'WORKLANES.md: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
