# HCP-YA 2025 Subject-Level Connectomes

This directory contains generated subject-level structural matrices for Paper 5.

Current completed analysis:

```text
paper5/hcp_connectomes/bedpostx_dyad_proxy/
```

Each `.npz` file stores:

```text
raw_counts
connectome
parcel_ids
seeds_per_parcel
max_steps
min_steps
step_size_vox
```

The current matrix is a cortical aparc68 BedpostX dyad1 endpoint-propagation proxy aligned to the fMRI state extraction order. It is a real subject-level diffusion-derived structural proxy, but it is not a gold-standard MRtrix ACT/SIFT2 tractography connectome.

Primary evidence:

```text
paper5/results/paper5_e4_connectome_proxy_qc.csv
paper5/results/paper5_e4_e8_structural_proxy_results.json
paper5/attachments/A9_HCP_Structural_Proxy_Final_Results.md
```

Gold-standard target for a future stronger Paper 5 version:

```text
HCP preprocessed dMRI
-> MSMT-CSD
-> ACT
-> iFOD2 probabilistic tractography
-> SIFT2
-> Schaefer-200 + subcortex parcel-by-parcel structural matrix
```
