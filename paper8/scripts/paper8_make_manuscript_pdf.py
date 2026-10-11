from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "PAPER8_MANUSCRIPT_CURRENT.md"
FIGURES = [
    (
        ROOT / "figures" / "figure1_p8_nuisance_ladder_transition_contrast.png",
        "Figure 1. HCP measured-physiology transition contrast",
        "Same-minus-different transition similarity remained negative across the nuisance ladder.",
    ),
    (
        ROOT / "figures" / "figure2_p8_nuisance_ladder_classification.png",
        "Figure 2. HCP secondary condition classification",
        "0-back versus 2-back block-start classification was above chance but is not the primary transition-reproducibility endpoint.",
    ),
    (
        ROOT / "figures" / "figure3_p8_v2_transition_nulls.png",
        "Figure 3. P8-v2 primary endpoint null audit",
        "The primary same-transition contrast did not survive label-shuffle comparison.",
    ),
    (
        ROOT / "figures" / "figure4_p8_v2_classification_nulls.png",
        "Figure 4. P8-v2 classification null audit",
        "The secondary classification signal exceeded simple shuffle nulls, while metadata-only prediction remained a serious competing explanation.",
    ),
    (
        ROOT / "figures" / "figure5_p8_ds005795_streaming_nuisance_ladder.png",
        "Figure 5. ds005795 convergent measured-physiology extension",
        "Measured physiology improved global BOLD prediction in ds005795, but this does not rescue the failed HCP primary gate.",
    ),
]
OUT = ROOT / "output" / "pdf" / "paper8_manuscript_preview.pdf"
RESULTS = ROOT / "results"


def markdown_to_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False
    code_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                blocks.append(("code", "\n".join(code_lines)))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            blocks.append(("space", ""))
        elif line.startswith("# "):
            blocks.append(("h1", line[2:]))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:]))
        else:
            blocks.append(("p", line))
    return blocks


def draw_text_page(pdf: PdfPages, page_blocks: list[tuple[str, str]], page_no: int) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    y = 0.94
    for kind, text in page_blocks:
        if kind == "h1":
            ax.text(0.08, y, text, fontsize=16, weight="bold", ha="left", va="top", wrap=True)
            y -= 0.055
        elif kind == "h2":
            ax.text(0.08, y, text, fontsize=12.5, weight="bold", ha="left", va="top", wrap=True)
            y -= 0.038
        elif kind == "code":
            for wrapped in text.splitlines() or [""]:
                for segment in textwrap.wrap(wrapped, width=82) or [""]:
                    ax.text(0.1, y, segment, fontsize=8.3, family="monospace", ha="left", va="top")
                    y -= 0.018
            y -= 0.008
        elif kind == "space":
            y -= 0.012
        else:
            for segment in textwrap.wrap(text, width=92):
                ax.text(0.08, y, segment, fontsize=9.4, ha="left", va="top")
                y -= 0.021
            y -= 0.006
    ax.text(0.5, 0.035, f"Paper 8 manuscript preview - page {page_no}", fontsize=8, ha="center", va="center")
    pdf.savefig(fig)
    plt.close(fig)


def paginate(blocks: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    pages: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    used = 0.0
    for kind, text in blocks:
        if kind == "h1":
            cost = 3.0
        elif kind == "h2":
            cost = 2.0
        elif kind == "code":
            cost = max(1.5, len(text.splitlines()) * 1.0)
        elif kind == "space":
            cost = 0.6
        else:
            cost = max(1.0, len(textwrap.wrap(text, width=92)) * 1.0)
        if current and used + cost > 38:
            pages.append(current)
            current = []
            used = 0.0
        current.append((kind, text))
        used += cost
    if current:
        pages.append(current)
    return pages


def draw_figure_page(pdf: PdfPages, page_no: int, figure_path: Path, title: str, caption: str) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0.08, 0.18, 0.84, 0.66])
    image = mpimg.imread(figure_path)
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.08, 0.9, title, fontsize=14, weight="bold")
    fig.text(0.08, 0.1, caption, fontsize=9, wrap=True)
    fig.text(0.5, 0.035, f"Paper 8 manuscript preview - page {page_no}", fontsize=8, ha="center", va="center")
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blocks = markdown_to_blocks(MANUSCRIPT.read_text(encoding="utf-8"))
    pages = paginate(blocks)
    with PdfPages(OUT) as pdf:
        page_no = 1
        for page_blocks in pages:
            draw_text_page(pdf, page_blocks, page_no)
            page_no += 1
        for figure_path, title, caption in FIGURES:
            if figure_path.exists():
                draw_figure_page(pdf, page_no, figure_path, title, caption)
                page_no += 1
    payload = {
        "paper": "Paper 8",
        "status": "PASS_MANUSCRIPT_PDF_GENERATED",
        "pdf": str(OUT),
        "source_manuscript": str(MANUSCRIPT),
        "source_figures": [str(item[0]) for item in FIGURES if item[0].exists()],
        "n_pages": page_no - 1,
        "claim_boundary": "Preview PDF generated from current manuscript and figures. Author, affiliation, ethics, contributions, conflicts, and funding metadata still require submitter confirmation.",
    }
    (RESULTS / "p8_manuscript_pdf.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
