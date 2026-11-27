import os

from django.core.management.base import BaseCommand

from api.dataPaths import VALIDATION_TRACKS_DIR
from api.validation_tracks import build_pdb_document, scan_emv_dir, write_json_atomic


class Command(BaseCommand):
    """
    Build per-residue validation tracks (viewer format) from EMV .aa.pdb files.
    One JSON per PDB in --out.
    """

    help = "Build per-residue validation tracks from EMV .aa.pdb files"

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True,
                            help="Folder with one subfolder per EMDB map (emd-xxxxx) containing <pdb>.<algorithm>.aa.pdb")
        parser.add_argument("--out", default=VALIDATION_TRACKS_DIR,
                            help="Output folder (default: %(default)s)")
        parser.add_argument("--pdb", action="append",
                            help="Only this PDB (can be repeated)")

    def handle(self, *args, **options):
        source, out = options["source"], options["out"]
        os.makedirs(out, exist_ok=True)

        self.stdout.write("Scanning %s ..." % source)
        found = scan_emv_dir(source)
        pdbs = [pdb.lower() for pdb in options["pdb"]] if options["pdb"] else sorted(found)
        self.stdout.write("%d PDB entries with .aa.pdb files; building %d" % (len(found), len(pdbs)))

        built = empty = several_maps = failed = 0
        for number, pdb in enumerate(pdbs, start=1):
            if pdb not in found:
                self.stderr.write("%s: no .aa.pdb files" % pdb)
                empty += 1
                continue
            try:
                doc = build_pdb_document(pdb, found[pdb])
            except Exception as exc:
                self.stderr.write("%s: %s" % (pdb, exc))
                failed += 1
                continue
            if doc is None:
                empty += 1
                continue
            if len(doc["maps"]) > 1:
                several_maps += 1
            write_json_atomic(doc, os.path.join(out, "%s.json" % pdb))
            built += 1
            if number % 1000 == 0:
                self.stdout.write("  %d / %d" % (number, len(pdbs)))

        self.stdout.write(self.style.SUCCESS(
            "Built %d, without data %d, failed %d, with several maps %d"
            % (built, empty, failed, several_maps)))