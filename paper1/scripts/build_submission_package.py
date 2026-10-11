from __future__ import annotations

import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PAPER1_MANUSCRIPT_CURRENT.md"
ATTACHMENTS = ROOT / "attachments"
SUBMISSION = ROOT / "submission"
FIGURES = ROOT / "manuscript" / "figures"
RESULTS = ROOT / "results"


FIGURE_CAPTIONS = {
    "figure_1_framework.png": "Figure 1. Paper 1 framework. The experiment compares flat task labels and CWP-style compositional labels for prediction of held-out brain-state transitions.",
    "figure_2_stage_sanity.png": "Figure 2. Stage sanity check. Subject-held-out ENCODE/MAINTAIN/PROBE classification was weak under the current native-grid pipeline.",
    "figure_3_m0_m4.png": "Figure 3. M0-M4 comparison. The incremental Task+CWP gain over the strong task baseline was inconclusive.",
    "figure_4_unseen_combination.png": "Figure 4. Leave-one-combination-out prediction. CWP-style composition improved within-dataset OOD MSE relative to the strong task baseline.",
    "figure_5_unseen_domain.png": "Figure 5. Leave-one-domain-out prediction. CWP-style composition improved within-dataset unseen-domain MSE in ds001635.",
    "figure_6_null_falsification.png": "Figure 6. Null/falsification tests. True CWP labels outperformed the sampled matched pseudo-ontology/null distribution in the implemented null suite.",
    "figure_7_external_failure.png": "Figure 7. External validation. CWP-only transfer did not beat the strong task baseline on ds001634.",
}


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    base["Title"].fontName = "Helvetica-Bold"
    base["Title"].fontSize = 18
    base["Title"].leading = 22
    base["Heading1"].fontName = "Helvetica-Bold"
    base["Heading1"].fontSize = 14
    base["Heading1"].leading = 17
    base["Heading2"].fontName = "Helvetica-Bold"
    base["Heading2"].fontSize = 12
    base["Heading2"].leading = 15
    base["BodyText"].fontName = "Helvetica"
    base["BodyText"].fontSize = 9.5
    base["BodyText"].leading = 13
    base.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            backColor=colors.whitesmoke,
            borderColor=colors.lightgrey,
            borderWidth=0.25,
            borderPadding=4,
        )
    )
    base.add(
        ParagraphStyle(
            name="Caption",
            parent=base["BodyText"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#475569"),
        )
    )
    return base


def clean_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def add_markdown(story: list, markdown: str, style: dict[str, ParagraphStyle], base_dir: Path) -> None:
    lines = markdown.splitlines()
    code_mode = False
    code_lines: list[str] = []
    bullet_lines: list[str] = []

    def flush_bullets() -> None:
        if not bullet_lines:
            return
        items = [
            ListItem(Paragraph(clean_inline(item), style["BodyText"]), leftIndent=10)
            for item in bullet_lines
        ]
        story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
        story.append(Spacer(1, 0.06 * inch))
        bullet_lines.clear()

    def flush_code() -> None:
        if not code_lines:
            return
        story.append(Preformatted("\n".join(code_lines), style["CodeBlock"]))
        story.append(Spacer(1, 0.08 * inch))
        code_lines.clear()

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            if code_mode:
                flush_code()
                code_mode = False
            else:
                flush_bullets()
                code_mode = True
            continue
        if code_mode:
            code_lines.append(line)
            continue

        image_match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
        if image_match:
            flush_bullets()
            image_path = (base_dir / image_match.group(2)).resolve()
            if image_path.exists():
                img = Image(str(image_path))
                max_width = 6.7 * inch
                max_height = 4.8 * inch
                scale = min(max_width / img.imageWidth, max_height / img.imageHeight, 1.0)
                img.drawWidth = img.imageWidth * scale
                img.drawHeight = img.imageHeight * scale
                story.append(img)
                story.append(Paragraph(clean_inline(image_match.group(1)), style["Caption"]))
                story.append(Spacer(1, 0.12 * inch))
            continue

        if not line.strip():
            flush_bullets()
            story.append(Spacer(1, 0.06 * inch))
            continue
        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[2:]), style["Title"]))
            story.append(Spacer(1, 0.12 * inch))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[3:]), style["Heading1"]))
            story.append(Spacer(1, 0.06 * inch))
        elif line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[4:]), style["Heading2"]))
            story.append(Spacer(1, 0.04 * inch))
        elif line.startswith("- "):
            bullet_lines.append(line[2:])
        else:
            flush_bullets()
            story.append(Paragraph(clean_inline(line), style["BodyText"]))
            story.append(Spacer(1, 0.04 * inch))
    flush_bullets()
    flush_code()


def write_pdf(markdown_path: Path, pdf_path: Path, title: str) -> None:
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=title,
    )
    story: list = []
    add_markdown(story, markdown_path.read_text(encoding="utf-8"), styles(), markdown_path.parent)
    doc.build(story)


def build_supplement() -> Path:
    parts = [
        "# Supplementary Materials for Paper 1",
        "",
        "This supplement contains the A1-A10 reproducibility attachments generated from the frozen E0-E8 run.",
        "",
    ]
    for name in [
        "A1_Frozen_Protocol.md",
        "A2_Dataset_Manifest.md",
        "A3_Full_Pipeline.md",
        "A4_Baseline_Results.md",
        "A5_Holdout_Audit.md",
        "A6_Statistics.md",
        "A7_Null_Falsification.md",
        "A8_QC_Leakage_Audit.md",
        "A9_Limitations_Failed_Analyses.md",
        "A10_One_Command_Reproduction.md",
    ]:
        path = ATTACHMENTS / name
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("\n\n---\n")
    out = SUBMISSION / "SUPPLEMENTARY_MATERIAL_CURRENT.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def build_captions() -> Path:
    lines = ["# Figure Captions", ""]
    for figure, caption in FIGURE_CAPTIONS.items():
        lines.append(f"## {figure}")
        lines.append("")
        lines.append(caption)
        lines.append("")
    out = SUBMISSION / "FIGURE_CAPTIONS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def build_audit() -> Path:
    claim_audit = json.loads((RESULTS / "claim_audit.json").read_text(encoding="utf-8"))
    disallowed = [
        "CWP is validated.",
        "CWP clearly outperforms task labels overall.",
        "CWP externally replicates.",
        "The 216-ROI grid is a neuroanatomical atlas.",
    ]
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    findings = []
    for claim in disallowed:
        present = claim in manuscript
        findings.append({"claim": claim, "present_in_main_text": present, "status": "REVIEW" if present else "PASS"})
    audit = {
        "date": "2026-09-01",
        "submission_ready_status": "PARTIAL",
        "reason": "Scientific manuscript, figures, supplement, and claim audit are generated. Author identity, affiliation, conflicts, funding, and public code URL still require user-supplied values before live bioRxiv submission.",
        "paper_positioning": claim_audit["paper_positioning"],
        "gate_a_incremental": claim_audit["gate_a_incremental"],
        "gate_b_ood": claim_audit["gate_b_ood"],
        "gate_c_external": claim_audit["gate_c_external"],
        "claim_allowed_cwp_foundation_holds": claim_audit["claim_allowed_cwp_foundation_holds"],
        "claim_allowed_cwp_clearly_outperforms_task_labels": claim_audit["claim_allowed_cwp_clearly_outperforms_task_labels"],
        "disallowed_claim_scan": findings,
        "remaining_human_fields": [
            "author names",
            "affiliations",
            "corresponding author email",
            "funding statement",
            "author contributions",
            "conflicts of interest",
            "public repository or archive URL",
            "license choice for bioRxiv posting",
        ],
    }
    out = SUBMISSION / "SUBMISSION_CLAIM_AUDIT.json"
    out.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return out


def main() -> None:
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    build_captions()
    supplement = build_supplement()
    write_pdf(MANUSCRIPT, SUBMISSION / "PAPER1_BIORXIV_DRAFT_CURRENT.pdf", "Paper 1 bioRxiv draft")
    write_pdf(supplement, SUBMISSION / "SUPPLEMENTARY_MATERIAL_CURRENT.pdf", "Paper 1 supplementary material")
    build_audit()
    print(f"wrote submission package to {SUBMISSION}")


if __name__ == "__main__":
    main()
