from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CONNECTOME_ROOT = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke"
FINAL_CONNECTOME = "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv"
EXT4_ROOT = "/home/a5993/p7_msmt_csd_ext4_diagnostic"


def wsl_stat(path: str) -> int:
    result = subprocess.run(
        ["wsl", "-e", "bash", "-lc", f"if [ -f {path!r} ]; then stat -c %s {path!r}; else echo 0; fi"],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(result.stdout.strip() or "0")


def wsl_unlink(path: str) -> None:
    if not path.startswith(f"{EXT4_ROOT}/") or not path.endswith("/dwi.mif"):
        raise RuntimeError(f"refusing unsafe ext4 cache path: {path}")
    subprocess.run(["wsl", "-e", "bash", "-lc", f"rm -f {path!r}"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude", nargs="*", default=[])
    args = parser.parse_args()
    excluded = set(args.exclude)
    RESULTS.mkdir(parents=True, exist_ok=True)
    removed = []
    for subject_dir in sorted(CONNECTOME_ROOT.iterdir()):
        if not subject_dir.is_dir() or subject_dir.name in excluded:
            continue
        final = subject_dir / FINAL_CONNECTOME
        if not (final.exists() and final.stat().st_size > 0):
            continue
        ext4_dwi = f"{EXT4_ROOT}/{subject_dir.name}/dwi.mif"
        size = wsl_stat(ext4_dwi)
        if size <= 0:
            continue
        wsl_unlink(ext4_dwi)
        removed.append({"subject": subject_dir.name, "ext4_path": ext4_dwi, "size_bytes": size})
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-ext4-dwi-cache-cleanup",
        "status": "PASS_EXT4_DWI_CACHE_CLEANUP",
        "claim_boundary": "P7 storage cleanup only. Removed WSL ext4 raw DWI derivatives only for subjects with preserved final fs_default84 connectomes.",
        "excluded_subjects": sorted(excluded),
        "removed_count": len(removed),
        "removed_bytes": sum(row["size_bytes"] for row in removed),
        "removed": removed,
    }
    out = RESULTS / "p7_ext4_dwi_cache_cleanup.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
