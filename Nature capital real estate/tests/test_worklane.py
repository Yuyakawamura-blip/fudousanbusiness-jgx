"""Contract tests for the work-lane selector: what is free, what a claim writes, and that claims never collide."""
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('worklane', Path(__file__).parents[1] / 'scripts/worklane.py')
lanes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lanes)

HEAD = '# board\n\nprose | with a pipe\n\n| ID | S | Needs | Touches | Item | Who |\n| --- | --- | --- | --- | --- | --- |\n'

def board(*rows):
    return HEAD + ''.join(f'| {r} |\n' for r in rows) + '\ntrailing text\n'

def pick(path, who='w', dry_run=False):
    out = io.StringIO()
    code = lanes.run(Namespace(command='pick', who=who, dry_run=dry_run), path, path.parent, Path('/repo'), 'now', out)
    return code, out.getvalue()

def claim_in_process(path, who):
    return pick(Path(path), who)


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
        self.assertIn('localhost:8002', out)
        self.assertEqual(lanes.parse(self.path.read_text())[1][3:], ('c', (), 'f', 'b', 'alice now'))

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


if __name__ == '__main__':
    unittest.main()
