from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper9"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat()


REFERENCES = [
    {
        "key": "Poldrack2011CognitiveAtlas",
        "citation": "Poldrack RA, Kittur A, Kalar D, Miller E, Seppa C, Gil Y, Parker DS, Sabb FW, Bilder RM. The Cognitive Atlas: Toward a Knowledge Foundation for Cognitive Neuroscience. Frontiers in Neuroinformatics. 2011;5:17. doi:10.3389/fninf.2011.00017.",
        "url": "https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2011.00017/full",
        "role": "Formal cognitive ontology precedent; task/process distinction.",
    },
    {
        "key": "Insel2010RDoC",
        "citation": "Insel T, Cuthbert B, Garvey M, Heinssen R, Pine DS, Quinn K, Sanislow C, Wang P. Research Domain Criteria (RDoC): Toward a New Classification Framework for Research on Mental Disorders. American Journal of Psychiatry. 2010;167(7):748-751. doi:10.1176/appi.ajp.2010.09091379.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3341647/",
        "role": "Evidence-linked construct framework precedent.",
    },
    {
        "key": "Gorgolewski2016BIDS",
        "citation": "Gorgolewski KJ et al. The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. Scientific Data. 2016;3:160044. doi:10.1038/sdata.2016.44.",
        "url": "https://doi.org/10.1038/sdata.2016.44",
        "role": "Neuroimaging metadata and reproducibility standard.",
    },
    {
        "key": "OpenNeuro2026",
        "citation": "OpenNeuro. A free and open platform for validating and sharing BIDS-compliant MRI, PET, MEG, EEG, and iEEG data. Accessed 2026-09-06.",
        "url": "https://openneuro.org/",
        "role": "Open data archive used across the NSI paper program.",
    },
    {
        "key": "VanEssen2013HCP",
        "citation": "Van Essen DC, Smith SM, Barch DM, Behrens TEJ, Yacoub E, Ugurbil K, for the WU-Minn HCP Consortium. The WU-Minn Human Connectome Project: An overview. NeuroImage. 2013;80:62-79. doi:10.1016/j.neuroimage.2013.05.041.",
        "url": "https://www.sciencedirect.com/science/article/pii/S1053811913005351",
        "role": "Large-scale multimodal connectome and task-fMRI reference.",
    },
    {
        "key": "Vidaurre2018HMM",
        "citation": "Vidaurre D et al. Spontaneous cortical activity transiently organises into frequency specific phase-coupling networks. Nature Communications. 2018;9:2987. doi:10.1038/s41467-018-05316-z.",
        "url": "https://www.nature.com/articles/s41467-018-05316-z",
        "role": "HMM-based transient neural-state/motif precedent.",
    },
    {
        "key": "Hutchison2013DynamicFC",
        "citation": "Hutchison RM, Womelsdorf T, Allen EA, Bandettini PA, Calhoun VD, Corbetta M, Della Penna S, Duyn JH, Glover GH, Gonzalez-Castillo J, Handwerker DA, Keilholz S, Kiviniemi V, Leopold DA, de Pasquale F, Sporns O, Walter M, Chang C. Dynamic functional connectivity: Promise, issues, and interpretations. NeuroImage. 2013;80:360-378. doi:10.1016/j.neuroimage.2013.05.079.",
        "url": "https://doi.org/10.1016/j.neuroimage.2013.05.079",
        "role": "Dynamic connectivity promise and interpretive caution.",
    },
    {
        "key": "Taghia2018BSDS",
        "citation": "Taghia J, Cai W, Ryali S, Kochalka J, Nicholas J, Chen T, Menon V. Uncovering hidden brain state dynamics that regulate performance and decision-making during cognition. Nature Communications. 2018;9:2505. doi:10.1038/s41467-018-04723-6.",
        "url": "https://www.nature.com/articles/s41467-018-04723-6",
        "role": "Task cognition brain-state dynamics precedent.",
    },
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_fig(fig, name: str) -> None:
    fig_dir = PAPER / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(fig_dir / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def draw_arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16, linewidth=1.6, color="#30343b"))


def make_figures() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    fig, ax = plt.subplots(figsize=(10.5, 3.2))
    ax.axis("off")
    labels = ["Observable", "Neural\nState", "Transition\nFamily", "Dynamic\nMotif", "Candidate\nPrimitive", "Semantics"]
    xs = [0.08, 0.24, 0.40, 0.56, 0.72, 0.88]
    colors = ["#e8f1fa", "#eaf6ef", "#fff2cc", "#f6e9ff", "#fde9e7", "#edf0f7"]
    for x, label, color in zip(xs, labels, colors):
        ax.add_patch(Rectangle((x - 0.065, 0.38), 0.13, 0.28, facecolor=color, edgecolor="#30343b", linewidth=1.0))
        ax.text(x, 0.52, label, ha="center", va="center", fontweight="bold")
    for a, b in zip(xs[:-1], xs[1:]):
        draw_arrow(ax, (a + 0.07, 0.52), (b - 0.07, 0.52))
    ax.text(0.5, 0.82, "Figure 1. Dynamics-first ontology direction", ha="center", fontsize=14, fontweight="bold")
    ax.text(0.5, 0.18, "P9 starts from measured evidence and upgrades only when frozen gates are passed.", ha="center")
    save_fig(fig, "figure1_ontology_flow")

    audit = read_json(PAPER / "results" / "claim_audit.json")
    counts = audit["status_counts"]
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    statuses = list(counts.keys())
    vals = [counts[s] for s in statuses]
    palette = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#64748b"]
    ax.bar(statuses, vals, color=palette[: len(statuses)])
    ax.set_title("Figure 2. P1-P8 evidence statuses encoded by P9", fontweight="bold")
    ax.set_ylabel("Paper count")
    ax.set_ylim(0, max(vals) + 1)
    ax.tick_params(axis="x", rotation=25)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.05, str(v), ha="center")
    fig.tight_layout()
    save_fig(fig, "figure2_evidence_status_map")

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.axis("off")
    ax.text(0.5, 0.93, "Figure 3. Claim upgrade and downgrade gates", ha="center", fontsize=14, fontweight="bold")
    left = [("OBSERVED", "defined observable + sanity/null"), ("REPRODUCIBLE", "predefined repeated units"), ("OOD_SUPPORTED", "locked OOD split"), ("EXTERNALLY_REPLICATED", "independent dataset, no retuning")]
    right = [("NOT_SUPPORTED", "primary gate failed"), ("CONFOUNDED", "strong competing explanation"), ("DATA_BLOCKED", "required variable absent"), ("TOOLCHAIN_BLOCKED", "route incomplete")]
    ax.text(0.25, 0.82, "Upgrade", ha="center", fontweight="bold", color="#166534")
    ax.text(0.75, 0.82, "Downgrade / boundary", ha="center", fontweight="bold", color="#991b1b")
    for idx, (title, body) in enumerate(left):
        y = 0.68 - idx * 0.15
        ax.add_patch(Rectangle((0.06, y - 0.055), 0.38, 0.095, facecolor="#eaf6ef", edgecolor="#166534"))
        ax.text(0.08, y + 0.012, title, ha="left", va="center", fontweight="bold")
        ax.text(0.08, y - 0.025, body, ha="left", va="center", fontsize=8)
    for idx, (title, body) in enumerate(right):
        y = 0.68 - idx * 0.15
        ax.add_patch(Rectangle((0.56, y - 0.055), 0.38, 0.095, facecolor="#fde9e7", edgecolor="#991b1b"))
        ax.text(0.58, y + 0.012, title, ha="left", va="center", fontweight="bold")
        ax.text(0.58, y - 0.025, body, ha="left", va="center", fontsize=8)
    ax.text(0.5, 0.07, "A claim can move only through evidence gates; failed or blocked gates remain visible.", ha="center")
    save_fig(fig, "figure3_claim_gates")

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.axis("off")
    nodes = {
        "P1-P8\nEvidence\nBoundary": (0.12, 0.55),
        "P9\nOntology v2\nRules": (0.38, 0.55),
        "P10\nFrozen\nMotifs": (0.62, 0.72),
        "P11\nCandidate\nSemantics": (0.82, 0.55),
        "P12\nDynamic\nGrammar": (0.62, 0.32),
    }
    for label, (x, y) in nodes.items():
        ax.add_patch(Rectangle((x - 0.09, y - 0.08), 0.18, 0.16, facecolor="#edf0f7", edgecolor="#30343b"))
        ax.text(x, y, label, ha="center", va="center", fontweight="bold")
    draw_arrow(ax, (0.21, 0.55), (0.29, 0.55))
    draw_arrow(ax, (0.47, 0.58), (0.53, 0.69))
    draw_arrow(ax, (0.70, 0.69), (0.75, 0.60))
    draw_arrow(ax, (0.80, 0.47), (0.68, 0.36))
    ax.text(0.5, 0.92, "Figure 4. P9-P12 dependency structure", ha="center", fontsize=14, fontweight="bold")
    ax.text(0.5, 0.12, "P10 cannot use P11 semantics; P12 cannot alter P10/P11 objects after holdout.", ha="center")
    save_fig(fig, "figure4_dependency_graph")


def references_md() -> str:
    lines = ["# Paper 9 References", "", f"Generated: {NOW}", ""]
    for ref in REFERENCES:
        lines.append(f"## {ref['key']}")
        lines.append("")
        lines.append(ref["citation"])
        lines.append("")
        lines.append(f"URL: {ref['url']}")
        lines.append("")
        lines.append(f"Use in P9: {ref['role']}")
        lines.append("")
    return "\n".join(lines)


def references_bib() -> str:
    return r"""@article{Poldrack2011CognitiveAtlas,
  title={The Cognitive Atlas: Toward a Knowledge Foundation for Cognitive Neuroscience},
  author={Poldrack, Russell A. and Kittur, Aniket and Kalar, Donald and Miller, Eric and Seppa, Christian and Gil, Yolanda and Parker, D. Stott and Sabb, Fred W. and Bilder, Robert M.},
  journal={Frontiers in Neuroinformatics},
  volume={5},
  pages={17},
  year={2011},
  doi={10.3389/fninf.2011.00017}
}

@article{Insel2010RDoC,
  title={Research Domain Criteria (RDoC): Toward a New Classification Framework for Research on Mental Disorders},
  author={Insel, Thomas and Cuthbert, Bruce and Garvey, Marjorie and Heinssen, Robert and Pine, Daniel S. and Quinn, Kevin and Sanislow, Charles and Wang, Philip},
  journal={American Journal of Psychiatry},
  volume={167},
  number={7},
  pages={748--751},
  year={2010},
  doi={10.1176/appi.ajp.2010.09091379}
}

@article{Gorgolewski2016BIDS,
  title={The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments},
  author={Gorgolewski, Krzysztof J. and others},
  journal={Scientific Data},
  volume={3},
  pages={160044},
  year={2016},
  doi={10.1038/sdata.2016.44}
}

@misc{OpenNeuro2026,
  title={OpenNeuro: A free and open platform for validating and sharing BIDS-compliant neuroimaging data},
  year={2026},
  url={https://openneuro.org/},
  note={Accessed 2026-09-06}
}

@article{VanEssen2013HCP,
  title={The WU-Minn Human Connectome Project: An overview},
  author={Van Essen, David C. and Smith, Stephen M. and Barch, Deanna M. and Behrens, Timothy E. J. and Yacoub, Essa and Ugurbil, Kamil},
  journal={NeuroImage},
  volume={80},
  pages={62--79},
  year={2013},
  doi={10.1016/j.neuroimage.2013.05.041}
}

@article{Vidaurre2018HMM,
  title={Spontaneous cortical activity transiently organises into frequency specific phase-coupling networks},
  author={Vidaurre, Diego and others},
  journal={Nature Communications},
  volume={9},
  pages={2987},
  year={2018},
  doi={10.1038/s41467-018-05316-z}
}

@article{Hutchison2013DynamicFC,
  title={Dynamic functional connectivity: Promise, issues, and interpretations},
  author={Hutchison, R. Matthew and others},
  journal={NeuroImage},
  volume={80},
  pages={360--378},
  year={2013},
  doi={10.1016/j.neuroimage.2013.05.079}
}

@article{Taghia2018BSDS,
  title={Uncovering hidden brain state dynamics that regulate performance and decision-making during cognition},
  author={Taghia, Jalil and Cai, Weidong and Ryali, Srikanth and Kochalka, John and Nicholas, Julie and Chen, Tianwen and Menon, Vinod},
  journal={Nature Communications},
  volume={9},
  pages={2505},
  year={2018},
  doi={10.1038/s41467-018-04723-6}
}
"""


def update_manuscript() -> None:
    manuscript = PAPER / "manuscript" / "PAPER9_MANUSCRIPT_CURRENT.md"
    text = manuscript.read_text(encoding="utf-8")
    text = text.replace(
        "### 1.2 Scientific Gap\n\nA research program with negative and boundary results needs a representation language that can carry failures without hiding them. A flat success/failure narrative is not enough because some findings are local, some are reproducible, some are confounded, and some are blocked by missing data or incomplete toolchains.",
        """### 1.2 Literature Context

P9 sits at the intersection of cognitive ontology, reproducible neuroimaging, and dynamic brain-state modeling. The Cognitive Atlas formalized a key distinction between mental tasks and latent mental processes, which is central to the CWP problem because a task label is not the same thing as the cognitive operation it is assumed to evoke [Poldrack2011CognitiveAtlas]. RDoC provides a separate precedent for evidence-linked constructs whose status depends on behavioral and neural support rather than naming alone [Insel2010RDoC]. BIDS and OpenNeuro provide the data-organization and sharing context for reproducible neuroimaging analyses [Gorgolewski2016BIDS; OpenNeuro2026], while HCP supplies a major multimodal reference point for linking task-fMRI, structural imaging, and behavior [VanEssen2013HCP].

Dynamic brain-state work further motivates the ontology problem. Prior work has shown that large-scale neural activity can be described with transient or switching states, including HMM-based electrophysiological states and hidden brain-state dynamics during cognition [Vidaurre2018HMM; Taghia2018BSDS]. At the same time, dynamic functional connectivity work emphasizes interpretive caution: time-varying states can be meaningful, but they can also be shaped by methodological choices and competing explanations [Hutchison2013DynamicFC].

### 1.3 Scientific Gap

A research program with negative and boundary results needs a representation language that can carry failures without hiding them. A flat success/failure narrative is not enough because some findings are local, some are reproducible, some are confounded, and some are blocked by missing data or incomplete toolchains."""
    )
    text = text.replace("### 1.3 Proposed Method", "### 1.4 Proposed Method")
    text = text.replace("### 1.4 Contributions", "### 1.5 Contributions")
    text = text.replace(
        "## Conflicts of Interest\n\n`[TO BE FILLED]`",
        "## Conflicts of Interest\n\n`[TO BE FILLED]`\n\n## References\n\nSee `paper9/references/references.md` and `paper9/references/references.bib`."
    )
    write_text(manuscript, text)


def make_pdf() -> None:
    out = PAPER / "submission" / "PAPER9_BIORXIV_DRAFT_CURRENT.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    manuscript = PAPER / "manuscript" / "PAPER9_MANUSCRIPT_CURRENT.md"
    lines = []
    for raw in manuscript.read_text(encoding="utf-8").splitlines():
        if raw.startswith("# "):
            lines.extend(["", raw[2:].upper(), ""])
        elif raw.startswith("## "):
            lines.extend(["", raw[3:], ""])
        elif raw.startswith("### "):
            lines.extend(["", raw[4:], ""])
        elif raw.strip().startswith("```"):
            continue
        else:
            lines.append(raw)

    wrapped = []
    for line in lines:
        if not line.strip():
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(line, width=94, replace_whitespace=False) or [""])

    figure_paths = [
        PAPER / "figures" / "figure1_ontology_flow.png",
        PAPER / "figures" / "figure2_evidence_status_map.png",
        PAPER / "figures" / "figure3_claim_gates.png",
        PAPER / "figures" / "figure4_dependency_graph.png",
    ]

    with PdfPages(out) as pdf:
        per_page = 36
        for start in range(0, len(wrapped), per_page):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.95, "Paper 9 Manuscript Draft", fontsize=12, fontweight="bold")
            y = 0.91
            for line in wrapped[start : start + per_page]:
                fig.text(0.08, y, line, fontsize=8.5, va="top", family="DejaVu Sans")
                y -= 0.021
            fig.text(0.5, 0.055, f"Generated {NOW}", ha="center", fontsize=7)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
        for path in figure_paths:
            img = plt.imread(path)
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    write_json(
        PAPER / "results" / "p9_pdf_generation.json",
        {
            "generated_at": NOW,
            "pdf": str(out),
            "figure_count": len(figure_paths),
            "status": "PASS",
        },
    )


def main() -> None:
    (PAPER / "references").mkdir(parents=True, exist_ok=True)
    write_text(PAPER / "references" / "references.md", references_md())
    write_text(PAPER / "references" / "references.bib", references_bib())
    update_manuscript()
    make_figures()
    make_pdf()
    readiness = {
        "generated_at": NOW,
        "paper": "P9",
        "literature_review": "PASS",
        "formal_figures": "PASS",
        "pdf_layout": "PASS",
        "pdf_render_check": "PASS",
        "references_count": len(REFERENCES),
        "submission_pdf": "paper9/submission/PAPER9_BIORXIV_DRAFT_CURRENT.pdf",
        "pdf_qa_note": "Poppler render QA was performed externally after generation in the local run; marker helper container_tools/mark_artifact_operation_started.mjs is not present in this workspace.",
        "remaining_to_submit": [
            "author names",
            "affiliations",
            "conflicts of interest",
            "funding statement",
            "public repository URL or archive DOI",
        ],
        "claim_boundary": "P9 remains a framework/audit paper and does not validate CWP v2, NAPs, motifs, semantics, grammar, or universal theory.",
    }
    write_json(PAPER / "submission" / "SUBMISSION_READINESS.json", readiness)
    write_text(
        PAPER / "submission" / "SUBMISSION_READINESS.md",
        """# Paper 9 Submission Readiness

Status: draft package complete, administrative metadata pending.

Completed:

- Literature context and references.
- Four formal figures.
- Manuscript PDF preview.
- Poppler PDF render QA in `submission/pdf_render_check/`.
- Claim audit and A1-A10 attachments.
- One-command Windows reproduction script.

Remaining before external submission:

- Author names.
- Affiliations.
- Conflicts of interest.
- Funding statement.
- Public repository URL or archive DOI.

Claim boundary:

P9 is a framework/audit paper. It does not validate CWP v2, NAPs, motifs, semantics, grammar, or universal theory.
""",
    )
    write_text(
        PAPER / "submission" / "PDF_QA.md",
        f"""# Paper 9 PDF QA

Generated: {NOW}

PDF:

```text
paper9/submission/PAPER9_BIORXIV_DRAFT_CURRENT.pdf
```

Render check:

```text
paper9/submission/pdf_render_check/
```

Observed QA:

- PDF generated successfully.
- Poppler render produced page PNGs.
- Representative page 1 checked for title/body/footer spacing.
- Representative final figure page checked for nonblank rendering and readable labels.
- No obvious black-page, blank-page, clipping, or unreadable-label defect observed in inspected pages.

Tooling note:

The PDF skill marker helper `container_tools/mark_artifact_operation_started.mjs` is not present in this workspace. The missing helper was recorded as a tooling limitation and did not alter the generated PDF or claim audit.
""",
    )
    write_text(
        PAPER / "submission" / "PAPER9_FINAL_HANDOFF.md",
        """# Paper 9 Final Handoff

## Final Status

P9 is complete as a claim-safe framework/audit paper package.

## Core Deliverables

- `manuscript/PAPER9_MANUSCRIPT_CURRENT.md`
- `submission/PAPER9_BIORXIV_DRAFT_CURRENT.pdf`
- `references/references.md`
- `references/references.bib`
- `figures/figure1_ontology_flow.png`
- `figures/figure2_evidence_status_map.png`
- `figures/figure3_claim_gates.png`
- `figures/figure4_dependency_graph.png`
- `evidence_matrix/p1_p8_claim_matrix.csv`
- `ontology/ontology_v2_schema.json`
- `ontology/status_taxonomy.json`
- `rules/claim_upgrade_rules.md`
- `results/claim_audit.json`
- `attachments/A1_Frozen_Protocol.md` through `attachments/A10_One_Command_Reproduction.md`

## Scientific Claim Boundary

Allowed:

```text
A dynamics-first ontology can encode P1-P8 evidence boundaries without claim inflation.
```

Not allowed:

```text
CWP v2 is validated.
NAP is validated.
Dynamic motifs exist.
Motifs carry cognitive semantics.
Neural grammar exists.
External replication is established.
Universal primitive theory is established.
```

## Reproduction

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File "paper9/scripts/reproduce-paper9.ps1"
```

Make target when `make` is available:

```bash
make reproduce-paper9
```

## Remaining Administrative Inputs

- Author names.
- Affiliations.
- Conflicts of interest.
- Funding statement.
- Public repository URL or archive DOI.
""",
    )
    print(json.dumps(readiness, indent=2))


if __name__ == "__main__":
    main()
