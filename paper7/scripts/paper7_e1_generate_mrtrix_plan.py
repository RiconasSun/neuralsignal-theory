from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
P5 = PROJECT / "paper5"
HCP = P5 / "data_hcp_ya_2025" / "downloads" / "HCP_1200"
RESULTS = ROOT / "results"
CONNECTOMES = ROOT / "structural_connectomes" / "mrtrix_act_sift2"
FREESURFER_LUT = ROOT / "resources" / "FreeSurferColorLUT.txt"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    CONNECTOMES.mkdir(parents=True, exist_ok=True)
    subjects = sorted([p.name for p in HCP.iterdir() if p.is_dir()]) if HCP.exists() else []
    subject = subjects[0] if subjects else "<SUBJECT_ID>"
    base = HCP / subject if subjects else Path("<HCP_SUBJECT_DIR>")
    out = CONNECTOMES / subject

    commands = [
        f"mrconvert \"{base / 'T1w/Diffusion/data.nii.gz'}\" \"{out / 'dwi.mif'}\" -fslgrad \"{base / 'T1w/Diffusion/bvecs'}\" \"{base / 'T1w/Diffusion/bvals'}\"",
        f"dwi2response dhollander \"{out / 'dwi.mif'}\" \"{out / 'wm.txt'}\" \"{out / 'gm.txt'}\" \"{out / 'csf.txt'}\"",
        f"dwi2fod msmt_csd \"{out / 'dwi.mif'}\" \"{out / 'wm.txt'}\" \"{out / 'wmfod.mif'}\" \"{out / 'gm.txt'}\" \"{out / 'gm.mif'}\" \"{out / 'csf.txt'}\" \"{out / 'csf.mif'}\"",
        f"5ttgen freesurfer \"{base / 'T1w/aparc+aseg.nii.gz'}\" \"{out / '5tt.mif'}\" -lut \"{FREESURFER_LUT}\" -nocrop",
        f"mrtransform \"{out / '5tt.mif'}\" -template \"{out / 'wmfod.mif'}\" \"{out / '5tt_dwi.mif'}\" -interp nearest",
        f"mrtransform \"{base / 'T1w/aparc+aseg.nii.gz'}\" -template \"{out / 'wmfod.mif'}\" \"{out / 'nodes_dwi.mif'}\" -interp nearest",
        f"5tt2gmwmi \"{out / '5tt_dwi.mif'}\" \"{out / 'gmwmi_seed.mif'}\"",
        f"tckgen \"{out / 'wmfod.mif'}\" \"{out / 'tracks_10m.tck'}\" -algorithm iFOD2 -act \"{out / '5tt_dwi.mif'}\" -backtrack -crop_at_gmwmi -seed_gmwmi \"{out / 'gmwmi_seed.mif'}\" -select 10000000 -maxlength 250 -cutoff 0.01",
        f"tcksift2 \"{out / 'tracks_10m.tck'}\" \"{out / 'wmfod.mif'}\" \"{out / 'sift2_weights.txt'}\" -act \"{out / '5tt_dwi.mif'}\"",
        f"tck2connectome \"{out / 'tracks_10m.tck'}\" \"{out / 'nodes_dwi.mif'}\" \"{out / 'connectome_sift2.csv'}\" -tck_weights_in \"{out / 'sift2_weights.txt'}\" -symmetric -zero_diagonal -out_assignment \"{out / 'assignments.csv'}\"",
    ]

    payload = {
        "experiment": "P7-E1-mrtrix-command-plan",
        "status": "COMMAND_PLAN_ONLY_NOT_EXECUTED",
        "subject_template": subject,
        "connectome_output_root": str(CONNECTOMES),
        "commands": commands,
        "required_external_tools": [
            "MRtrix3: mrconvert, dwi2response, dwi2fod, 5ttgen, mrtransform, 5tt2gmwmi, tckgen, tcksift2, tck2connectome",
            "HCP FreeSurfer aparc+aseg segmentation for 5ttgen freesurfer",
            "FreeSurfer lookup table and frozen P7 node lookup table",
        ],
        "claim_boundary": "This script generates the frozen high-fidelity ACT/iFOD2/SIFT2 connectome command plan only. It does not generate connectomes.",
    }
    (RESULTS / "p7_e1_mrtrix_command_plan.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (RESULTS / "p7_e1_mrtrix_command_plan.ps1").write_text(
        "\n".join(["# Generated command plan. Review paths and LUTs before execution.", ""] + commands) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
