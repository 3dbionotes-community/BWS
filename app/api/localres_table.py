import bisect
import csv
import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LocalResRow:
    emdb_id: str
    median: float
    quartile25: float
    quartile75: float

@dataclass(frozen=True)
class LocalResTable:
    path: str
    mtime: float          # last modified date of the file
    rows: dict            # "emd-xxxxx" -> LocalResRow
    sorted_medians: list  # sorted median list of all entries
    duplicates: int       # duplicate discarted total row number
    skipped: int          # invalid discarted total row number

    @property
    def date(self):
        return datetime.fromtimestamp(self.mtime, tz=timezone.utc).strftime("%Y-%m-%d")

    def get(self, emdb_id):
        return self.rows.get(normalize_emdb_id(emdb_id))

    def rank(self, median):
        if not self.sorted_medians:
            return None
        position = bisect.bisect_right(self.sorted_medians, median) # Counts (<=) medians of entries, not just (<)
        return int(position / len(self.sorted_medians) * 100)


def normalize_emdb_id(emdb_id):
    return emdb_id.strip().lower()

def _parse_float(value):
    number = float(value)
    if number <= 0:
        raise ValueError("non-positive value: %s" % value)
    return number


def read_table(path):
    rows = {}
    duplicates = 0
    skipped = 0
    with open(path, newline="") as tsv_file:
        for line_number, fields in enumerate(csv.reader(tsv_file, delimiter="\t"), start=1):
            if not fields or not fields[0].strip():
                continue
            try:
                emdb_id = normalize_emdb_id(fields[0])
                row = LocalResRow(
                    emdb_id=emdb_id,
                    median=_parse_float(fields[1]),
                    quartile25=_parse_float(fields[2]),
                    quartile75=_parse_float(fields[3]),
                )
            except (IndexError, ValueError) as exc:
                skipped += 1
                logger.warning("%s:%d skipped (%s)", path, line_number, exc)
                continue
            if emdb_id in rows:
                duplicates += 1
            rows[emdb_id] = row

    return LocalResTable(
        path=path,
        mtime=os.path.getmtime(path),
        rows=rows,
        sorted_medians=sorted(row.median for row in rows.values()),
        duplicates=duplicates,
        skipped=skipped,
    )


_cache = {}
_lock = threading.Lock()

def get_table(path):
    """Returns the table. Only re-reads if the file has changed"""
    mtime = os.path.getmtime(path)
    with _lock:
        table = _cache.get(path)
        if table is None or table.mtime != mtime:
            table = read_table(path)
            _cache[path] = table
            logger.info(
                "Loaded %s: %d entries, %d duplicates dropped, %d rows skipped",
                path, len(table.rows), table.duplicates, table.skipped,
            )
        return table