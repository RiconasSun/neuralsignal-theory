from __future__ import annotations

import argparse
import math
import os

import nibabel as nib
import numpy as np

from common import ensure_dir, root_path, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a fixed native-space grid atlas from a reference BOLD image.")
    parser.add_argument("--reference-bold", required=True)
    parser.add_argument("--out", default=root_path("preprocessing", "grid_atlas_216roi.nii.gz"))
    parser.add_argument("--bins-x", type=int, default=6)
    parser.add_argument("--bins-y", type=int, default=6)
    parser.add_argument("--bins-z", type=int, default=6)
    args = parser.parse_args()

    ref = nib.load(args.reference_bold)
    shape = ref.shape[:3]
    labels = np.zeros(shape, dtype=np.int16)
    roi_id = 1
    x_edges = np.linspace(0, shape[0], args.bins_x + 1, dtype=int)
    y_edges = np.linspace(0, shape[1], args.bins_y + 1, dtype=int)
    z_edges = np.linspace(0, shape[2], args.bins_z + 1, dtype=int)
    for xi in range(args.bins_x):
        for yi in range(args.bins_y):
            for zi in range(args.bins_z):
                xs, xe = x_edges[xi], x_edges[xi + 1]
                ys, ye = y_edges[yi], y_edges[yi + 1]
                zs, ze = z_edges[zi], z_edges[zi + 1]
                if xs == xe or ys == ye or zs == ze:
                    continue
                labels[xs:xe, ys:ye, zs:ze] = roi_id
                roi_id += 1

    ensure_dir(os.path.dirname(args.out))
    atlas = nib.Nifti1Image(labels, ref.affine, ref.header)
    atlas.set_data_dtype(np.int16)
    nib.save(atlas, args.out)
    write_json(
        root_path("preprocessing", "grid_atlas_216roi.json"),
        {
            "atlas": os.path.abspath(args.out),
            "reference_bold": os.path.abspath(args.reference_bold),
            "shape": list(shape),
            "bins": [args.bins_x, args.bins_y, args.bins_z],
            "n_rois": int(labels.max()),
            "status": "generated",
            "limitation": "Native image-space grid atlas; suitable for first reproducible pipeline run, not a neuroanatomical atlas claim.",
        },
    )
    print(f"wrote {int(labels.max())} ROI atlas to {args.out}")


if __name__ == "__main__":
    main()
