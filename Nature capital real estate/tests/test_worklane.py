"""Contract tests for the work-lane selector: what is free, what a claim writes, and that claims never collide."""
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('worklane', Path(__file__).parents[1] / 'scripts/worklane.py')
lanes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lanes)

HEAD = '# board\n\nprose | with a pipe\n\n| ID | S | Needs | Touches | Item | Who |\n| --- | --- | --- | --- | --- | --- |\n'

def board(*rows):
    return HEAD + ''.join(f'| {r} |\n' for r in rows) + '\ntrailing text\n'

def pick(path, who='w', dry_run=False, port_free=lambda port: True):
    out = io.StringIO()
    code = lanes.run(Namespace(command='pick', who=who, dry_run=dry_run), path, path.parent, Path('/repo'), 'now', out,
                     port_free=port_free)
    return code, out.getvalue()

def claim_in_process(path, who):
    return pick(Path(path), who)

def add_lane(path, lane, needs='-', status='o', note=None, before=None, item='i'):
    out = io.StringIO()
    args = Namespace(command='add', lane=lane, touches='f', item=item, needs=needs, status=status, note=note,
                     before=before)
    return lanes.run(args, path, path.parent, Path('/repo'), 'now', out), out.getvalue()

def add_in_process(path, lane):
    return add_lane(Path(path), lane)


class Selection(unittest.TestCase):
    def test_open_lane_with_completed_needs_is_free(self):
        rows = lanes.parse(board('A | x | - | f | a | ', 'B | o | A | f | b | '))
        self.assertEqual([r.id for r in lanes.free(rows)], ['B'])

    def test_claimed_blocked_done_and_waiting_lanes_are_not_free(self):
        rows = lanes.parse(board('A | c | - | f | a | me', 'B | b | - | f | b | why', 'C | x | - | f | c | ',
                                 'D | o | A | f | d | '))
        self.assertEqual(lanes.free(rows), [])
        self.assertEqual(lanes.waiting_on(rows[3], rows), ['A'])

    def test_board_order_is_priority(self):
        rows = lanes.parse(board('B | o | - | f | b | ', 'A | o | - | f | a | '))
        self.assertEqual(lanes.free(rows)[0].id, 'B')

    def test_malformed_boards_are_rejected(self):
        for rows in (['A | o | Z | f | a | '], ['A | o | - | f | a | ', 'A | o | - | f | a | '],
                     ['A | q | - | f | a | '], ['A | o | - | f | a'], ['A | o | A | f | a | ']):
            with self.subTest(rows=rows), self.assertRaises(lanes.BoardError):
                lanes.parse(board(*rows))

    def test_update_changes_only_that_row(self):
        text = board('A | o | - | f | a | ', 'B | o | A | g | b | ')
        new = lanes.update(text, 'B', 'c', 'me now')
        self.assertEqual([l for l in new.splitlines() if l not in text.splitlines()], ['| B | c | A | g | b | me now |'])
        self.assertEqual(len(new.splitlines()), len(text.splitlines()))


class Claims(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'WORKLANES.md'

    def test_pick_claims_the_first_free_lane_and_prints_its_port(self):
        self.path.write_text(board('A | x | - | f | a | ', 'B | o | - | f | b | '))
        code, out = pick(self.path, 'alice')
        self.assertEqual(code, 0)
        self.assertIn('Claimed B', out)
        self.assertIn('localhost:8001', out)
        self.assertEqual(lanes.parse(self.path.read_text())[1][3:], ('c', (), 'f', 'b', 'alice now port 8001'))

    def test_port_follows_the_lane_not_its_row(self):
        # B holds 8001; a row added above it must not hand 8001 to the next claim.
        self.path.write_text(board('A | x | - | f | a | ', 'N | o | - | f | n | ', 'B | c | - | f | b | bob t port 8001'))
        self.assertIn('localhost:8002', pick(self.path)[1])

    def test_ports_of_claimed_and_blocked_lanes_are_skipped_others_reused(self):
        self.path.write_text(board('A | c | - | f | a | bob t port 8001', 'B | b | - | f | b | photos port 8002',
                                   'C | o | - | f | c | stale port 8003', 'D | o | - | f | d | '))
        self.assertIn('localhost:8003', pick(self.path)[1])

    def test_ports_in_use_on_the_host_are_skipped(self):
        self.path.write_text(board('A | o | - | f | a | '))
        self.assertIn('localhost:8003', pick(self.path, port_free=lambda port: port > 8002)[1])

    def test_no_free_port_is_an_error_and_claims_nothing(self):
        text = board('A | o | - | f | a | ')
        self.path.write_text(text)
        with self.assertRaises(lanes.BoardError):
            pick(self.path, port_free=lambda port: False)
        self.assertEqual(self.path.read_text(), text)

    def test_dry_run_does_not_write(self):
        text = board('A | o | - | f | a | ')
        self.path.write_text(text)
        self.assertEqual(pick(self.path, dry_run=True)[0], 0)
        self.assertEqual(self.path.read_text(), text)

    def test_nothing_free_says_stop_and_why(self):
        self.path.write_text(board('A | c | - | f | a | bob', 'B | o | A | f | b | ', 'C | b | - | f | c | photos'))
        code, out = pick(self.path)
        self.assertEqual(code, lanes.NONE_FREE)
        self.assertIn('No work lanes are available', out)
        for reason in ('A: claimed (bob)', 'B: waiting on A', 'C: blocked (photos)'):
            self.assertIn(reason, out)

    def test_simultaneous_workers_never_get_the_same_lane(self):
        self.path.write_text(board(*(f'L{i} | o | - | f | item | ' for i in range(6))))
        with ProcessPoolExecutor(8) as pool:
            results = list(pool.map(claim_in_process, [str(self.path)] * 8, [f'w{i}' for i in range(8)]))
        claimed = [out.split()[1].rstrip(':') for code, out in results if code == 0]
        self.assertEqual(sorted(claimed), [f'L{i}' for i in range(6)])
        self.assertEqual([code for code, _ in results].count(lanes.NONE_FREE), 2)
        self.assertTrue(all(r.status == 'c' for r in lanes.parse(self.path.read_text())))

    def test_simultaneous_workers_never_get_the_same_port(self):
        self.path.write_text(board(*(f'L{i} | o | - | f | item | ' for i in range(6))))
        with ProcessPoolExecutor(6) as pool:
            results = list(pool.map(claim_in_process, [str(self.path)] * 6, [f'w{i}' for i in range(6)]))
        ports = [port for _, out in results for port in re.findall(r'localhost:(\d+)/', out)]
        self.assertEqual(sorted(ports), [str(8001 + i) for i in range(6)])


class Adding(unittest.TestCase):
    """add puts a found lane on the board under the lock, and writes nothing when the board would be wrong."""
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'WORKLANES.md'

    def test_add_appends_one_row_and_keeps_the_rest(self):
        text = board('A | x | - | f | a | ', 'B | c | A | g | b | bob t port 8001')
        self.path.write_text(text)
        self.assertEqual(add_lane(self.path, 'N', needs='A, B', item='found in B')[0], 0)
        new = self.path.read_text()
        self.assertEqual(new.replace('| N | o | A, B | f | found in B |  |\n', ''), text)
        self.assertEqual([r.id for r in lanes.parse(new)], ['A', 'B', 'N'])

    def test_add_before_a_lane_gives_it_priority(self):
        self.path.write_text(board('A | o | - | f | a | ', 'B | o | - | f | b | '))
        add_lane(self.path, 'N', before='A')
        self.assertEqual([r.id for r in lanes.parse(self.path.read_text())], ['N', 'A', 'B'])
        self.assertIn('Claimed N', pick(self.path)[1])

    def test_blocked_lane_records_what_it_waits_for(self):
        self.path.write_text(board('A | o | - | f | a | '))
        add_lane(self.path, 'N', status='b', note='photos')
        self.assertEqual(lanes.parse(self.path.read_text())[1][3:], ('b', (), 'f', 'i', 'photos'))

    def test_bad_lanes_are_refused_and_write_nothing(self):
        text = board('A | o | - | f | a | ')
        self.path.write_text(text)
        for kwargs in ({'lane': 'A'}, {'lane': 'N', 'needs': 'Z'}, {'lane': 'N', 'before': 'Z'},
                       {'lane': 'N', 'item': 'a | b'}, {'lane': 'N', 'item': 'a\nb'}, {'lane': 'N', 'note': '\rb'},
                       {'lane': 'N', 'status': ''}, {'lane': 'N M'},
                       {'lane': 'N', 'status': 'b'}, {'lane': 'N', 'status': 'c'}, {'lane': 'N', 'needs': 'N'}):
            with self.subTest(**kwargs), self.assertRaises(lanes.BoardError):
                add_lane(self.path, **kwargs)
            self.assertEqual(self.path.read_text(), text)

    def test_simultaneous_adds_and_claims_lose_nothing(self):
        self.path.write_text(board(*(f'L{i} | o | - | f | item | ' for i in range(4))))
        with ProcessPoolExecutor(8) as pool:
            adds = [pool.submit(add_in_process, str(self.path), f'N{i}') for i in range(4)]
            claims = [pool.submit(claim_in_process, str(self.path), f'w{i}') for i in range(4)]
            self.assertTrue(all(f.result()[0] == 0 for f in adds + claims))
        rows = lanes.parse(self.path.read_text())
        self.assertEqual(sorted(r.id for r in rows), sorted([f'L{i}' for i in range(4)] + [f'N{i}' for i in range(4)]))
        self.assertEqual(sum(r.status == 'c' for r in rows), 4)


def git(cwd, *args):
    return subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, text=True, check=True).stdout


class Finish(unittest.TestCase):
    """finish cleans up a pushed lane, and refuses whenever cleanup could lose work."""
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        git(base, 'init', '-q', '--bare', '-b', 'develop', 'origin.git')
        git(base, 'clone', '-q', str(base / 'origin.git'), 'repo')
        self.root = base / 'repo'
        for key, value in (('user.name', 't'), ('user.email', 't@example.org'), ('commit.gpgsign', 'false')):
            git(self.root, 'config', key, value)
        git(self.root, 'commit', '-q', '--allow-empty', '-m', 'start')
        git(self.root, 'push', '-q', 'origin', 'HEAD:develop')
        self.tree = base / 'repo-l1'
        git(self.root, 'worktree', 'add', '-q', '-b', 'lane/l1', str(self.tree), 'origin/develop')
        git(self.tree, 'commit', '-q', '--allow-empty', '-m', 'lane work')
        self.board = self.root / 'WORKLANES.md'
        self.board.write_text(board('L1 | c | - | f | a | me'))
        self.stopped = []

    def finish(self):
        out = io.StringIO()
        code = lanes.run(Namespace(command='finish', lane='L1'), self.board, self.root / '.git', self.root, 'now', out,
                         stop=self.stopped.append)
        return code, out.getvalue()

    def test_pushed_lane_is_cleaned_up_and_marked_done(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        code, out = self.finish()
        self.assertEqual(code, 0, out)
        self.assertFalse(self.tree.exists())
        self.assertEqual(git(self.root, 'branch', '--list', 'lane/l1'), '')
        self.assertEqual(self.stopped, ['ncre-l1'])
        self.assertEqual(lanes.parse(self.board.read_text())[0].status, 'x')

    def test_unpushed_commits_are_refused(self):
        code, out = self.finish()
        self.assertEqual(code, 1)
        self.assertIn('not in origin/develop', out)
        self.assertTrue(self.tree.exists())
        self.assertEqual(lanes.parse(self.board.read_text())[0].status, 'c')

    def test_uncommitted_changes_are_refused(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        (self.tree / 'draft.txt').write_text('unsaved')
        code, out = self.finish()
        self.assertEqual(code, 1)
        self.assertIn('uncommitted', out)
        self.assertTrue((self.tree / 'draft.txt').exists())
        self.assertEqual(self.stopped, [])

    def refused(self, why):
        code, out = self.finish()
        self.assertEqual(code, 1, out)
        self.assertIn(why, out)
        self.assertTrue(self.tree.exists())
        self.assertEqual(self.stopped, [])
        self.assertEqual(lanes.parse(self.board.read_text())[0].status, 'c')

    def test_commit_on_a_detached_head_is_refused(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        git(self.tree, 'checkout', '-q', '--detach')
        git(self.tree, 'commit', '-q', '--allow-empty', '-m', 'only reachable from the worktree HEAD')
        self.refused('not in origin/develop')

    def test_unpushed_work_on_another_branch_is_refused(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        git(self.tree, 'checkout', '-q', '-b', 'other')
        git(self.tree, 'commit', '-q', '--allow-empty', '-m', 'not pushed')
        self.refused('not in origin/develop')

    def test_ignored_files_are_refused_except_finder_clutter(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        (self.tree / '.gitignore').write_text('.env\n.DS_Store\n')
        git(self.tree, 'add', '.gitignore'); git(self.tree, 'commit', '-q', '-m', 'ignore')
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        (self.tree / '.DS_Store').write_text('finder')
        (self.tree / '.env').write_text('SECRET=1')
        self.refused('.env')
        (self.tree / '.env').unlink()
        self.assertEqual(self.finish()[0], 0)

    def test_folder_deleted_by_hand_still_cleans_up_the_branch(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        shutil.rmtree(self.tree)
        code, out = self.finish()
        self.assertEqual(code, 0, out)
        self.assertEqual(git(self.root, 'branch', '--list', 'lane/l1'), '')

    def test_failed_removal_leaves_the_preview_running(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        git(self.root, 'worktree', 'lock', str(self.tree))
        self.refused('worktree remove')

    def test_only_a_claimed_lane_can_be_finished(self):
        self.board.write_text(board('L1 | o | - | f | a | '))
        code, out = self.finish()
        self.assertEqual(code, 1)
        self.assertIn('not claimed', out)
        self.assertEqual(lanes.parse(self.board.read_text())[0].status, 'o')

    def test_running_inside_the_worktree_is_refused(self):
        git(self.tree, 'push', '-q', 'origin', 'HEAD:develop')
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tree)
        code, out = self.finish()
        self.assertEqual(code, 1)
        self.assertIn('outside', out)
        self.assertTrue(self.tree.exists())


if __name__ == '__main__':
    unittest.main()
