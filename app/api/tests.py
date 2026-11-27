from django.test import TestCase
import os
import tempfile
import time
import json
from django.test import SimpleTestCase

from .localres_table import get_table, read_table
from .validation_tracks import build_pdb_document, get_chain_tracks, scan_emv_dir, write_json_atomic

# Create your tests here.

TABLE = (
    "emd-0001\t2.0\t1.5\t2.5\n"
    "emd-0002\t3.0\t2.5\t3.5\n"
    "emd-0003\t4.0\t3.5\t4.5\n"
    "emd-0002\t3.2\t2.7\t3.7\n"  
    "emd-0004\tbad\t1\t2\n"     
    "emd-0005\t-1\t-1\t-1\n"     
    "\n"
)


class LocalResTableTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        self.tmp.write(TABLE)
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_rows_duplicates_and_invalid(self):
        table = read_table(self.tmp.name)
        self.assertEqual(sorted(table.rows), ["emd-0001", "emd-0002", "emd-0003"])
        self.assertEqual(table.duplicates, 1)
        self.assertEqual(table.skipped, 2)

    def test_last_row_wins(self):
        row = read_table(self.tmp.name).get("EMD-0002")
        self.assertEqual((row.median, row.quartile25, row.quartile75), (3.2, 2.7, 3.7))

    def test_missing_entry(self):
        self.assertIsNone(read_table(self.tmp.name).get("emd-9999"))

    def test_rank_same_definition_as_before(self):
        table = read_table(self.tmp.name)
        self.assertEqual(table.rank(2.0), 33)
        self.assertEqual(table.rank(3.2), 66)
        self.assertEqual(table.rank(4.0), 100)
        self.assertEqual(table.rank(1.0), 0)

    def test_cache_reloads_when_file_changes(self):
        first = get_table(self.tmp.name)
        self.assertIs(get_table(self.tmp.name), first)
        with open(self.tmp.name, "a") as f:
            f.write("emd-0006\t5.0\t4.5\t5.5\n")
        future = time.time() + 10
        os.utime(self.tmp.name, (future, future))
        self.assertIn("emd-0006", get_table(self.tmp.name).rows)


def _atom(serial, name, residue, chain, number, value):
    """One ATOM line with the value in columns 55-60 (as in EMV .aa.pdb files)."""
    return "ATOM  %5d %-4s %3s %1s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f           C\n" % (
        serial, " " + name if len(name) < 4 else name, residue, chain, number, 0, 0, 0, value, 0)


class ValidationTracksTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        self.out = os.path.join(self.tmp.name, "out")
        os.makedirs(self.out)
        self._write("emd-11328/6zow.deepres.aa.pdb", [
            ("N", "ALA", "A", 27, 9.9), ("CA", "ALA", "A", 27, 3.95), ("CB", "ALA", "A", 27, 8.8),
            ("CA", "GLY", "A", 28, 1.2),   # below the 1.5 threshold: not used for minVal
            ("CA", "SER", "B", 1, 4.5),
            ("N", "CAS", "B", 2, 9.0),     # residue name contains "CA": not a CA atom
            ("CA", "CAS", "B", 2, 5.0),
        ])
        self._write("emd-11328/6zow.mapq.aa.pdb", [("CA", "ALA", "A", 27, 0.7)])
        self._write("emd-11328/6zow.fscqR.aa.pdb", [("CA", "ALA", "A", 27, 0.1)])  # ignored variant
        self._write("emd-27146/8d2q.fscq.aa.pdb", [("CA", "ALA", "A", 1, 0.1)])
        self._write("emd-29511/8d2q.fscq.aa.pdb", [("CA", "ALA", "A", 1, 0.2)])
        self._write("emd-29511/8d2q.daq.aa.pdb", [("CA", "ALA", "A", 1, 0.3)])
        for pdb, maps in scan_emv_dir(self.src).items():
            write_json_atomic(build_pdb_document(pdb, maps), os.path.join(self.out, pdb + ".json"))

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, relpath, rows):
        path = os.path.join(self.src, relpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("".join(_atom(i, *row) for i, row in enumerate(rows, start=1)))

    def test_scan(self):
        found = scan_emv_dir(self.src)
        self.assertEqual(sorted(found["6zow"]["emd-11328"]), ["deepres", "mapq"])
        self.assertEqual(sorted(found["8d2q"]), ["emd-27146", "emd-29511"])

    def test_only_ca_atoms_in_viewer_format_and_order(self):
        tracks = get_chain_tracks(self.out, "6ZOW", "A")
        self.assertEqual([t["algorithm"] for t in tracks], ["deepres", "mapq"])
        deepres = tracks[0]
        self.assertEqual(list(deepres), ["chain", "data", "minVal", "maxVal", "algorithm", "algoType"])
        self.assertEqual(deepres["data"], [{"begin": "27", "value": 3.95}, {"begin": "28", "value": 1.2}])
        self.assertEqual((deepres["minVal"], deepres["maxVal"]), (3.95, 3.95))
        chain_b = get_chain_tracks(self.out, "6zow", "B")[0]["data"]
        self.assertEqual(chain_b, [{"begin": "1", "value": 4.5}, {"begin": "2", "value": 5.0}])

    def test_default_map_has_most_algorithms(self):
        with open(os.path.join(self.out, "8d2q.json")) as f:
            doc = json.load(f)
        self.assertEqual(doc["default_emdb"], "emd-29511")
        self.assertEqual(sorted(doc["maps"]), ["emd-27146", "emd-29511"])

    def test_missing(self):
        self.assertIsNone(get_chain_tracks(self.out, "6zow", "Z"))
        self.assertIsNone(get_chain_tracks(self.out, "1abc", "A"))