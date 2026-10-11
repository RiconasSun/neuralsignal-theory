from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CONNECTOME_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
FINAL_CONNECTOME = "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"

INTERMEDIATE_FILENAMES = {
    "5tt.mif",
    "5tt_dwi.mif",
    "gmwmi_seed.mif",
    "nodes_dwi.mif",
    "wmfod_ext4.mif",
    "gm_ext4.mif",
    "csf_ext4.mif",
    "tracks_5k_ext4_msmt.tck",
    "sift2_weights_ext4_msmt.txt",
    "assignments_ext4_msmt.csv",
    "connectome_sift2_ext4_msmt_smoke.csv",
}


def safe_subject_dir(path: Path) -> bool:
    try:
        path.resolve().relative_to(CONNECTOME_ROOT.resolve())
    except ValueError:
        return False
    return path.is_dir() and path.parent.resolve() == CONNECTOME_ROOT.resolve()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude", nargs="*", default=[])
    args = parser.parse_args()
    excluded = set(args.exclude)

    RESULTS.mkdir(parents=True, exist_ok=True)
    removed: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []

    for subject_dir in sorted(CONNECTOME_ROOT.iterdir()):
        if not safe_subject_dir(subject_dir):
            continue
        subject = subject_dir.name
        if subject in excluded:
            skipped.append({"subject": subject, "reason": "excluded_active_or_requested"})
            continue
        final = subject_dir / FINAL_CONNECTOME
        if not (final.exists() and final.stat().st_size > 0):
            skipped.append({"subject": subject, "reason": "missing_final_fsdefault84_connectome"})
            continue
        for name in sorted(INTERMEDIATE_FILENAMES):
            candidate = subject_dir / name
            if not candidate.exists():
                continue
            size = candidate.stat().st_size
            candidate.unlink()
            removed.append({"subject": subject, "path": str(candidate), "size_bytes": size})

    payload = {
        "paper": "Paper 7",
        "experiment": "P7-windows-intermediate-cleanup",
        "status": "PASS_WINDOWS_INTERMEDIATE_CLEANUP",
        "claim_boundary": (
            "P7 storage cleanup only. Removed Windows-side intermediate tractography files "
            "only for subjects with preserved final fs_default84 connectomes."
        ),
        "excluded_subjects": sorted(excluded),
        "removed_count": len(removed),
        "removed_bytes": sum(int(row["size_bytes"]) for row in removed),
        "removed": removed,
        "skipped": skipped,
    }
    out = RESULTS / "p7_windows_intermediate_cleanup.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
