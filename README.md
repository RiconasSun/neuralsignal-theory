# NeuralSignal Theory

NSI research protocols, scripts, manuscripts, analysis results and figures for
P1-P10, including the P10R regional/hierarchical analysis plan.

Repository branch: [test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).
The presence of a paper package does not establish support for its hypotheses.
Consult each paper's claim audit and limitations before interpreting results.

## Data and Figures

| Paper | Source and Reproduction Guide |
| --- | --- |
| P1 | [Data sources, samples, access, pipeline and figures](paper1/DATA_AVAILABILITY.md) |
| P2 | [Data sources, samples, access, pipeline and figures](paper2/DATA_AVAILABILITY.md) |
| P3 | [Data sources, samples, access, pipeline and figures](paper3/DATA_AVAILABILITY.md) |
| P4 | [Data sources, samples, access, pipeline and figures](paper4/DATA_AVAILABILITY.md) |
| P5 | [Data sources, samples, access, pipeline and figures](paper5/DATA_AVAILABILITY.md) |
| P6 | [Data sources, samples, access, pipeline and figures](paper6/DATA_AVAILABILITY.md) |
| P7 | [Data sources, samples, access, pipeline and figures](paper7/DATA_AVAILABILITY.md) |
| P8 | [Data sources, samples, access, pipeline and figures](paper8/DATA_AVAILABILITY.md) |
| P9 | [Data sources, samples, access, pipeline and figures](paper9/DATA_AVAILABILITY.md) |
| P10 | [Data sources, samples, access, pipeline and figures](paper10/DATA_AVAILABILITY.md) |

Raw participant brain imaging, electrophysiology, physiological recordings,
and tractography are excluded from Git. Source metadata, selected sample
records, derived analysis tables, scripts, plots and paper text are retained.
The small generated grid atlas in P1 is a processing resource, not participant
data, and is retained. Credentials and runtime caches are excluded.

Data are obtained from the original OpenNeuro/NEMAR or HCP/BALSA providers.
Follow their licenses and access terms. Local audit versions, DOI versions and
actual downloaded revisions are distinguished where they differ or are unknown.
HCP download manifests may name legacy package keys; the 2025 protocol title
does not by itself prove every local package came from that release.

- [Withheld local raw-file inventory and SHA256](publication/raw_file_inventory.csv)
- [Figure-to-generator and input mapping](publication/figure_provenance.csv)
- [Published artifact checksums](publication/artifact_checksums.csv)

Historical PDFs remain archived snapshots. Updated data availability is in the
current Markdown manuscripts and their linked per-paper guides.

## Reproduction

Use the original per-paper A3 pipeline and A10 commands after obtaining the
specified data and dependencies. Existing Makefile targets run analyses using
their documented local prerequisites; they are not a universal automatic raw
data downloader. Missing inputs must not be replaced with fabricated data.

After a scientific rerun, rebuild the publication inventory from the project root:

```powershell
python scripts/build_publication_provenance.py
python scripts/build_publication_provenance.py --check
```

The check verifies publication checksums, local references and Git exclusion
rules. It does not verify scientific conclusions or prove a raw-data rerun.

No new blanket license is assigned to upstream datasets, third-party material,
or research artifacts by this publication operation. Consult source licenses.
