"""Generate source-faithful publication guides without rerunning scientific analyses."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publication"
REPO = "https://github.com/RiconasSun/neuralsignal-theory/tree/test"
DATASETS = {
    "ds001635": ("1.0.1 (local manuscript DOI)", "10.18112/openneuro.ds001635.v1.0.1", "CC-BY 4.0 per local P1 metadata"),
    "ds001634": ("1.0.1 (local manuscript DOI)", "10.18112/openneuro.ds001634.v1.0.1", "CC-BY 4.0 per local P1 metadata"),
    "ds004469": ("1.1.3 (local P2 manuscript DOI)", "10.18112/openneuro.ds004469.v1.1.3", "See provider dataset license"),
    "ds004117": ("Dataset DOI version 1.0.1; BIDS format version 1.7.0 is not a release identifier; exact download commit not recorded", "10.18112/openneuro.ds004117.v1.0.1", "CC0 per local P6 audit and provider metadata"),
    "ds004752": ("Dataset DOI version 1.0.1; BIDS format version 1.4.0 is not a release identifier; exact download commit not recorded", "10.18112/openneuro.ds004752.v1.0.1", "CC0 per local P6 audit and provider metadata"),
    "ds005795": ("1.0.0", "10.18112/openneuro.ds005795.v1.0.0", "See provider dataset license"),
    "HCP-YA": ("2025 release named in local protocols; inspect download manifests for actual package keys", "", "HCP/BALSA authorized access and data-use terms"),
}
PAPER_DATA = {
    1: ["ds001635", "ds001634"], 2: ["ds001635", "ds001634", "ds004469"],
    3: ["ds001635", "ds001634", "ds004469"], 4: ["ds001635", "ds001634", "ds004469"],
    5: ["HCP-YA"], 6: ["ds004117", "ds004752"], 7: ["HCP-YA"],
    8: ["HCP-YA", "ds005795"], 9: [], 10: ["ds004117", "ds004752"],
}
RAW_SUFFIXES = (".nii", ".nii.gz", ".mif", ".tck", ".edf", ".bdf", ".fif", ".vhdr", ".vmrk", ".eeg", ".set", ".fdt", "_physio.tsv.gz")
ATLAS = "paper1/preprocessing/grid_atlas_216roi.nii.gz"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def link(path: Path) -> str:
    rel = relative(path)
    return f"[{rel}]({REPO}/{rel})"


def available_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, capture_output=True, check=True,
    )
    return sorted({ROOT / name.decode("utf-8") for name in result.stdout.split(b"\0") if name})


def figure_records(paper: Path) -> list[dict]:
    scripts = list((paper / "scripts").glob("*.py"))
    records = []
    for figure in sorted(paper.rglob("*.png")):
        if "figures" not in figure.parts:
            continue
        matches = []
        for script in scripts:
            source = script.read_text(encoding="utf-8-sig")
            if figure.stem not in source:
                continue
            tree = ast.parse(source)
            literals = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
            inputs = set()
            for value in literals:
                if value.endswith((".csv", ".json", ".npz", ".tsv")):
                    direct = ROOT / value.replace("\\", "/")
                    if direct.is_file():
                        inputs.add(relative(direct))
                    else:
                        inputs.update(relative(p) for p in paper.rglob(Path(value).name) if p.is_file())
            matches.append((relative(script), sorted(inputs)))
        records.append({
            "paper": paper.name, "figure": relative(figure),
            "generators": " ; ".join(m[0] for m in matches),
            "script_scope_inputs": " ; ".join(sorted({i for _, inputs in matches for i in inputs})),
            "mapping_basis": "Literal figure name in source; inputs are script-wide, inspect function for panel subset" if matches else "Historical figure; generator not identified by literal name",
        })
    return records


def build() -> None:
    OUT.mkdir(exist_ok=True)
    files = available_files()
    raw = [p for p in ROOT.glob("paper*/**/*") if p.is_file() and str(p).lower().endswith(RAW_SUFFIXES) and relative(p) != ATLAS and ".secrets" not in p.parts]
    raw_rows = []
    for path in sorted(raw):
        rel = relative(path)
        raw_rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": digest(path),
                         "dataset": next((d for d in DATASETS if d in rel), "HCP-YA" if path.parts[-1].endswith((".mif", ".tck")) else "Inspect upstream manifest"),
                         "subject": next(iter(re.findall(r"sub-[A-Za-z0-9]+", rel)), next(iter(re.findall(r"/(\d{6})/", rel)), "See original filename/manifest")),
                         "session": next(iter(re.findall(r"ses-[A-Za-z0-9]+", rel)), "Not encoded in path"),
                         "task": next(iter(re.findall(r"task-[A-Za-z0-9]+", rel)), "Not encoded in path"),
                         "run": next(iter(re.findall(r"run-[A-Za-z0-9]+", rel)), "Not encoded in path"),
                         "access": "Obtain from original provider; not redistributed"})
    write_csv(OUT / "raw_file_inventory.csv", raw_rows, ["path", "bytes", "sha256", "dataset", "subject", "session", "task", "run", "access"])
    all_figures = []
    for number in range(1, 11):
        paper = ROOT / f"paper{number}"
        records = figure_records(paper)
        all_figures.extend(records)
        lines = [f"# P{number} Data and Figure Availability", "", "Publication documentation added 2026-10-10; scientific results are unchanged.", "",
                 "## Original Data", "", "Raw participant imaging/signals and tractography are not redistributed. Figures are derived results or conceptual diagrams, not substitutes for downloadable source data.", ""]
        for dataset in PAPER_DATA[number]:
            version, doi, access = DATASETS[dataset]
            url = "https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release" if dataset == "HCP-YA" else f"https://openneuro.org/datasets/{dataset}"
            lines += [f"- [{dataset}]({url}): {version}. Access/license: {access}."]
            if doi:
                lines += [f"  Dataset DOI recorded locally: [doi:{doi}](https://doi.org/{doi})."]
        if number == 9:
            lines += ["P9 introduces no raw dataset; its inputs are P1-P8 evidence artifacts and claim audits, not a new participant cohort."]
        if number == 10:
            lines += ["P10 consumes frozen P6 bandpower feature artifacts. ds004752 is a convergent check with a different feature space, not direct external replication."]
        if number == 8:
            lines += ["NEMAR mirror: [on005795](https://www.nemar.org/dataset/on005795), version v1.0.0; [manifest](https://data.nemar.org/on005795/v1.0.0/manifest.json)."]
        lines += ["", "Provider-link verification and historical version distinctions: [source registry](../publication/SOURCE_REGISTRY.md). The registry separates current metadata from the versions recorded by these analyses."]
        lines += ["", "## Samples, Processing, and Access", "", "The following existing records define actual selected subjects/runs, splits, exclusions, pipeline parameters and data access. Candidate inventories do not establish that every candidate was analyzed.", ""]
        refs = [p for p in files if p.is_file() and paper in p.parents and p.suffix in {".csv", ".json", ".md"} and (any(s in relative(p).lower() for s in ("manifest", "inventory", "cohort_lock", "subject_metrics", "download", "a2_", "a3_", "a5_", "a8_", "a10_")) or "protocol" in p.parts)]
        lines += [f"- {link(p)}" for p in refs]
        lines += ["", "Exact local withheld filenames and SHA256 values are in [raw_file_inventory.csv](../publication/raw_file_inventory.csv). This inventory describes files present at publication, not a reconstructed historical cohort. Missing historical raw files and unrecorded download revisions cannot be recovered from a checksum of current derived data.", "",
                  "For raw reproduction, obtain the indicated dataset release under its license, place files at the paths expected by the original manifests/scripts, and follow A3/A10. HCP requires your own authorized account; credentials remain local. A derived-data rerun does not prove raw-data preprocessing was reproduced.", "",
                  "## Figures and Generation", "", "| Figure | Generator Command | Analysis Inputs (Script Scope) | Mapping |", "| --- | --- | --- | --- |"]
        for row in records:
            commands = "<br>".join(f"`python {p}`" for p in row["generators"].split(" ; ") if p) or "Not identified; retain as historical artifact"
            inputs = "<br>".join(link(ROOT / p) for p in row["script_scope_inputs"].split(" ; ") if p) or "Conceptual figure or inputs constructed in code; inspect generator"
            lines.append(f"| {link(ROOT / row['figure'])} | {commands} | {inputs} | {row['mapping_basis']} |")
        lines += ["", "Generation commands may rerun analyses or contact source providers; inspect A10 and prerequisites before running. They are source mappings, not evidence of a fresh scientific rerun.", "",
                  "## Publication Record", "", f"Code and artifacts: [neuralsignal-theory/test]({REPO}).", "", "See [publication inventory](../publication/artifact_checksums.csv) for SHA256 values. Historical submission PDFs preserve earlier text; this guide and the current Markdown manuscript carry the updated availability supplement."]
        (paper / "DATA_AVAILABILITY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        manuscript = paper / "manuscript" / f"PAPER{number}_MANUSCRIPT_CURRENT.md"
        text = manuscript.read_text(encoding="utf-8")
        if "Publication supplement:" not in text:
            supplement = (
                f"\n\nPublication supplement: [P{number} data sources, sample manifests, access conditions, and figure provenance](../DATA_AVAILABILITY.md). "
                f"Code and derived artifacts: [neuralsignal-theory/test]({REPO}). "
                "Raw participant signals/imaging are obtained from original providers; "
                "local withheld filenames and SHA256 values are in "
                "[the raw inventory](../../publication/raw_file_inventory.csv). "
                "See [artifact checksums](../../publication/artifact_checksums.csv)."
            )
            if "## Data Availability" not in text:
                raise ValueError(f"Missing Data Availability section: {manuscript}")
            text = text.replace("## Data Availability", "## Data Availability" + supplement, 1)
        text = text.replace("## Code Availability\n\n[TO BE FILLED]", f"## Code Availability\n\n[Public code]({REPO}/paper{number}/scripts). See [the data guide](../DATA_AVAILABILITY.md) for prerequisites.")
        text = text.replace("Public repository URL: `[TO BE FILLED]`.", f"Public repository: [neuralsignal-theory/test]({REPO}).")
        text = text.replace("Public code URL: `[TO BE FILLED]`.", f"Public code: [neuralsignal-theory/test]({REPO}).")
        text = text.replace("Public repository and archival location: `[TO BE FILLED]`.", f"Repository: [neuralsignal-theory/test]({REPO}); archival DOI is not assigned.")
        if manuscript.read_text(encoding="utf-8") != text:
            manuscript.write_text(text, encoding="utf-8")
    write_csv(OUT / "figure_provenance.csv", all_figures, ["paper", "figure", "generators", "script_scope_inputs", "mapping_basis"])
    inventory = [p for p in available_files() if p.is_file() and p.suffix in {".csv", ".json", ".npz", ".png", ".pdf", ".py", ".ps1", ".md"} and "publication" not in p.parts and "ops" not in p.parts]
    write_csv(OUT / "artifact_checksums.csv", [{"path": relative(p), "bytes": p.stat().st_size, "sha256": digest(p)} for p in inventory], ["path", "bytes", "sha256"])
    print(json.dumps({"guides": 10, "figures": len(all_figures), "withheld_local_files": len(raw_rows), "checksummed_artifacts": len(inventory)}))


def check() -> None:
    errors = []
    with (OUT / "artifact_checksums.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        path = ROOT / row["path"]
        if not path.is_file() or digest(path) != row["sha256"]:
            errors.append(f"Checksum mismatch: {row['path']}")
    for number in range(1, 11):
        guide = ROOT / f"paper{number}" / "DATA_AVAILABILITY.md"
        manuscript = ROOT / f"paper{number}" / "manuscript" / f"PAPER{number}_MANUSCRIPT_CURRENT.md"
        if "../DATA_AVAILABILITY.md" not in manuscript.read_text(encoding="utf-8"):
            errors.append(f"Missing manuscript supplement: {manuscript.name}")
        for target in re.findall(r"\]\(([^)]+)\)", guide.read_text(encoding="utf-8")):
            if target.startswith(REPO + "/"):
                path = ROOT / target[len(REPO) + 1:]
            elif "://" not in target:
                path = guide.parent / target
            else:
                continue
            if not path.is_file():
                errors.append(f"Broken local reference: {target}")
    tracked = subprocess.check_output(["git", "-c", "core.quotepath=false", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    for name in tracked:
        if name and ((name.endswith(RAW_SUFFIXES) and name != ATLAS) or ".secrets/" in name or "__pycache__/" in name):
            errors.append(f"Forbidden tracked file: {name}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(json.dumps({"status": "PASS", "artifact_count": len(rows), "guides": 10, "scope": "publication integrity only; not scientific rerun"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else build()
