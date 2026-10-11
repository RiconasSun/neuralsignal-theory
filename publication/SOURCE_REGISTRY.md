# Data Source Registry

Publication review date: 2026-10-10. These links identify original data providers;
they do not assert a fresh download or scientific reproduction.

| Identifier | Analysis Metadata | Original Source and Access |
| --- | --- | --- |
| ds001635 | Local P1 manuscript records DOI version 1.0.1 and CC-BY 4.0 | [OpenNeuro](https://openneuro.org/datasets/ds001635), [DOI](https://doi.org/10.18112/openneuro.ds001635.v1.0.1) |
| ds001634 | Local P1 manuscript records DOI version 1.0.1 and CC-BY 4.0 | [OpenNeuro](https://openneuro.org/datasets/ds001634), [DOI](https://doi.org/10.18112/openneuro.ds001634.v1.0.1) |
| ds004469 | Local P2 manuscript records DOI version 1.1.3 | [Snapshot](https://openneuro.org/datasets/ds004469/versions/1.1.3), [DOI](https://doi.org/10.18112/openneuro.ds004469.v1.1.3) |
| ds004117 | DOI version 1.0.1; BIDSVersion 1.7.0 is a format version | [OpenNeuro](https://openneuro.org/datasets/ds004117), [DOI](https://doi.org/10.18112/openneuro.ds004117.v1.0.1) |
| ds004752 | DOI version 1.0.1; BIDSVersion 1.4.0 is a format version | [OpenNeuro](https://openneuro.org/datasets/ds004752), [DOI](https://doi.org/10.18112/openneuro.ds004752.v1.0.1) |
| ds005795 / on005795 | Local P8 audit specifies OpenNeuro 1.0.0 / NEMAR v1.0.0 | [OpenNeuro](https://openneuro.org/datasets/ds005795/versions/1.0.0), [DOI](https://doi.org/10.18112/openneuro.ds005795.v1.0.0), [NEMAR](https://www.nemar.org/dataset/on005795) |
| HCP-YA | Protocols name 2025; download manifest includes HCP_1200 keys | [Official 2025 release](https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release), [BALSA](https://balsa.wustl.edu/). Authorized access and data-use terms apply. |

## Fresh Provider Checks

- The [ds004117 provider metadata](https://raw.githubusercontent.com/OpenNeuroDatasets/ds004117/main/dataset_description.json) returns BIDSVersion 1.7.0, DatasetDOI version 1.0.1, and CC0.
- The [ds004752 provider metadata](https://raw.githubusercontent.com/OpenNeuroDatasets/ds004752/main/dataset_description.json) returns BIDSVersion 1.4.0, DatasetDOI version 1.0.1, and CC0.
- The [ds004469 current provider metadata](https://raw.githubusercontent.com/OpenNeuroDatasets/ds004469/main/dataset_description.json) now identifies DOI version 1.1.4 and CC0. This does not change the local analysis's recorded 1.1.3 version.
- The official HCP 2025 release page is accessible and explicitly advises against mixing the 2025 release with S1200. Existing HCP_1200 package keys must be reconciled against actual download records before claiming raw reproduction with 2025 data.
- OpenNeuro pages are JavaScript applications. Some dataset-page requests and the NEMAR description request did not return readable content in the verification tool. Their identifiers above are supported by existing local audits, not a claim of freshly validated download availability.

## Exact Samples and Unrecorded Metadata

Use per-paper A2/A5/A8, protocol, cohort, feature and subject-result files linked
by each DATA_AVAILABILITY.md. Subject/session/task/run labels in the raw inventory
are parsed from actual paths. "Not encoded in path" means that field was not
present in the filename, not that a session or task did not exist.

Some original P1 raw files recorded in historical manifests are no longer present
in this workspace. Current derived files and historical input manifests remain
published; no missing raw checksum or historical Git download commit is invented.
Raw-file SHA256 values certify current local bytes, not dataset publisher hashes.

Figure input mappings are explicitly script-wide and may include auxiliary
audit files or outputs. Inspect the named plotting function to select exact
panel inputs. Conceptual diagrams are labeled by their source code and require
no participant data input.
