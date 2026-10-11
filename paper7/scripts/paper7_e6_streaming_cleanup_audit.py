from __future__ import annotations

import json
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
RESULTS = ROOT / "results"
DATA_MANIFEST = ROOT / "data_manifest"
HCP = PROJECT / "paper5" / "data_hcp_ya_2025" / "downloads" / "HCP_1200"

DEFAULT_SUBJECTS = [
    "106016",
    "108828",
    "110411",
    "111312",
    "111716",
    "113619",
    "113922",
    "114419",
    "115320",
    "116524",
    "117122",
    "118528",
    "118730",
    "118932",
    "120111",
    "122317",
    "122620",
    "123117",
    "123925",
    "124422",
    "125525",
    "126325",
    "127630",
    "127933",
    "128127",
    "128632",
    "129028",
    "130013",
    "130316",
    "131217",
    "131722",
    "133019",
    "133928",
    "135225",
    "135932",
    "136833",
    "138534",
    "139637",
    "140925",
    "144832",
    "146432",
    "147737",
    "148335",
    "148840",
    "149337",
    "149539",
    "149741",
    "151223",
    "151526",
    "151627",
    "153025",
    "154734",
    "156637",
    "159340",
    "160123",
    "161731",
    "162733",
    "163129",
    "176542",
    "178950",
    "188347",
    "189450",
    "190031",
    "192540",
    "196750",
    "198451",
    "199655",
    "201111",
    "208226",
    "211417",
    "211720",
    "212318",
    "214423",
    "221319",
    "239944",
    "245333",
    "280739",
    "298051",
    "366446",
    "397760",
    "414229",
    "499566",
    "654754",
    "672756",
    "751348",
    "756055",
    "792564",
    "856766",
    "857263",
    "899885",
]
FINAL_FILES = [
    "connectome_sift2_ext4_msmt_fsdefault84_smoke.csv",
    "assignments_ext4_msmt_fsdefault84.csv",
]
LARGE_INTERMEDIATES = [
    "nodes_fsdefault.mif",
    "nodes_fsdefault_dwi.mif",
    "nodes_dwi.mif",
    "dwi.mif",
    ".ext4_dwi_ready",
    "5tt.mif",
    "5tt_dwi.mif",
    "gmwmi_seed.mif",
    "wmfod_ext4.mif",
    "gm_ext4.mif",
    "csf_ext4.mif",
    "tracks_5k_ext4_msmt.tck",
    "sift2_weights_ext4_msmt.txt",
    "connectome_sift2_ext4_msmt_smoke.csv",
    "assignments_ext4_msmt.csv",
]


def file_record(path: Path) -> dict:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="*", default=DEFAULT_SUBJECTS)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    DATA_MANIFEST.mkdir(parents=True, exist_ok=True)
    subject_records = []
    for subject in args.subjects:
        subject_root = ROOT / "structural_connectomes" / "mrtrix_act_sift2_smoke" / subject
        final_files = [file_record(subject_root / name) for name in FINAL_FILES]
        intermediates = [file_record(subject_root / name) for name in LARGE_INTERMEDIATES]
        raw_dwi = file_record(HCP / subject / "T1w" / "Diffusion" / "data.nii.gz")
        subject_records.append(
            {
                "subject": subject,
                "final_files": final_files,
                "large_intermediates": intermediates,
                "raw_dwi": raw_dwi,
                "all_final_files_present": all(row["exists"] and row["size_bytes"] > 0 for row in final_files),
                "large_intermediates_absent": all(not row["exists"] for row in intermediates),
            }
        )
    payload = {
        "paper": "Paper 7",
        "experiment": "P7-E6-streaming-cleanup-audit",
        "status": "PASS_STREAMING_CLEANUP_AUDIT"
        if all(row["all_final_files_present"] and row["large_intermediates_absent"] for row in subject_records)
        else "FAILED_STREAMING_CLEANUP_AUDIT",
        "subjects": args.subjects,
        "subject_records": subject_records,
        "claim_boundary": "This audits preserved connectome outputs and removed local intermediates only. It does not test the structural hypothesis.",
    }
    (RESULTS / "p7_e6_streaming_cleanup_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS_STREAMING_CLEANUP_AUDIT":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
