"""
Per-residue validation tracks, prepared offline in the format the viewer expects.

Source today: EMV generated `.aa.pdb` files (`<emdb>/<pdb>.<algorithm>.aa.pdb`), the same
files LRS reads. For each PDB, one JSON with the tracks of every map it was
validated against; the endpoint only reads it.
"""
import json
import logging
import os
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

# Same order and minVal thresholds as the previous pdbAnnotFromMap endpoint
ALGORITHMS = [
    # (algorithm, algoType, threshold for minVal)
    ("deepres", "localResolution", 1.5),
    ("monores", "localResolution", 1.5),
    ("blocres", "localResolution", 1.5),
    ("mapq", "modelQuality", -1),
    ("fscq", "modelQuality", -3),
    ("daq", "modelQuality", -1),
]
ALGORITHM_NAMES = {name for name, _, _ in ALGORITHMS}

AA_PDB_RE = re.compile(r"^(?P<pdb>\d[a-z0-9]{3})\.(?P<algorithm>[a-z]+)\.aa\.pdb$")


def scan_emv_dir(source_dir):
    """
    Walk <source_dir>/<emdb>/ once.
    Returns {pdb: {emdb: {algorithm: path}}}.
    """
    found = defaultdict(lambda: defaultdict(dict))
    for emdb in sorted(os.listdir(source_dir)):
        map_dir = os.path.join(source_dir, emdb)
        if not emdb.startswith("emd-") or not os.path.isdir(map_dir):
            continue
        for fname in os.listdir(map_dir):
            match = AA_PDB_RE.match(fname)
            if match and match["algorithm"] in ALGORITHM_NAMES:
                found[match["pdb"]][emdb][match["algorithm"]] = os.path.join(map_dir, fname)
    return found


def read_ca_values(path):
    """
    {chain: [(residue number, value)]} from the CA atoms of an .aa.pdb.
    Value in columns 55-60, as LRS does.
    """
    chains = defaultdict(list)
    with open(path) as pdb_file:
        for line in pdb_file:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            try:
                value = float(line[54:60])
            except ValueError:
                continue
            chains[line[21]].append((line[22:26].strip(), value))
    return chains


def make_track(algorithm, algo_type, threshold, chain, residues):
    values = [value for _, value in residues]
    above = [value for value in values if value > threshold]
    return {
        "chain": chain,
        "data": [{"begin": residue, "value": value} for residue, value in residues],
        "minVal": min(above) if above else min(values),
        "maxVal": max(values),
        "algorithm": algorithm,
        "algoType": algo_type,
    }


def build_map_tracks(files):
    """{algorithm: path} of one map -> {chain: [track, ...]} in ALGORITHMS order."""
    tracks = defaultdict(list)
    for algorithm, algo_type, threshold in ALGORITHMS:
        path = files.get(algorithm)
        if path is None:
            continue
        for chain, residues in read_ca_values(path).items():
            tracks[chain].append(make_track(algorithm, algo_type, threshold, chain, residues))
    return dict(tracks)


def choose_default_map(maps):
    """Map with most algorithms; on a tie, the highest EMDB number (most recent)."""
    return max(maps, key=lambda emdb: (len(maps[emdb]), int(emdb.split("-")[1])))


def build_pdb_document(pdb, maps, source="EMV"):
    """maps: {emdb: {algorithm: path}} -> document to save, or None if no data."""
    doc_maps = {}
    for emdb, files in maps.items():
        tracks = build_map_tracks(files)
        if tracks:
            doc_maps[emdb] = tracks
    if not doc_maps:
        return None
    available = {emdb: maps[emdb] for emdb in doc_maps}
    return {
        "pdb": pdb,
        "source": source,
        "default_emdb": choose_default_map(available),
        "maps": doc_maps,
    }


def write_json_atomic(doc, path):
    """Write to a temporary file and rename, so readers never see half a file."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as json_file:
        json.dump(doc, json_file, separators=(",", ":"))
    os.replace(tmp_path, path)


def get_chain_tracks(tracks_dir, pdb, chain):
    """Tracks of the default map for one chain, or None."""
    path = os.path.join(tracks_dir, "%s.json" % pdb.lower())
    try:
        with open(path) as json_file:
            doc = json.load(json_file)
    except FileNotFoundError:
        return None
    return doc["maps"][doc["default_emdb"]].get(chain)