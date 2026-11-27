from django.test import TestCase
import os
import tempfile
import time

from django.test import SimpleTestCase

from .localres_table import get_table, read_table

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