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
MANUSCRIPT = ROOT / "manuscript" / "PAPER7_MANUSCRIPT_CURRENT.md"
FIGURE = ROOT / "figures" / "paper7_final_structural_hypothesis_delta_mse.png"
OUT = ROOT / "output" / "pdf" / "paper7_manuscript_preview.pdf"
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
    ax.text(0.5, 0.035, f"Paper 7 manuscript preview - page {page_no}", fontsize=8, ha="center", va="center")
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


def draw_figure_page(pdf: PdfPages, page_no: int) -> None:
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0.08, 0.16, 0.84, 0.68])
    image = mpimg.imread(FIGURE)
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.08, 0.9, "Figure 1. Final structural hypothesis test", fontsize=14, weight="bold")
    fig.text(
        0.08,
        0.1,
        "Delta MSE is comparator minus true-subject structural model. Positive values favor true G_i. "
        "All final gates failed under the tested interface.",
        fontsize=9,
        wrap=True,
    )
    fig.text(0.5, 0.035, f"Paper 7 manuscript preview - page {page_no}", fontsize=8, ha="center", va="center")
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blocks = markdown_to_blocks(MANUSCRIPT.read_text(encoding="utf-8"))
    pages = paginate(blocks)
    with PdfPages(OUT) as pdf:
        for idx, page_blocks in enumerate(pages, start=1):
            draw_text_page(pdf, page_blocks, idx)
        draw_figure_page(pdf, len(pages) + 1)
    payload = {
        "paper": "Paper 7",
        "status": "PASS_MANUSCRIPT_PDF_GENERATED",
        "pdf": str(OUT),
        "source_manuscript": str(MANUSCRIPT),
        "source_figure": str(FIGURE),
        "n_pages": len(pages) + 1,
        "claim_boundary": "Preview PDF generated from current manuscript and final figure. Author, affiliation, ethics, and reference fields remain placeholders.",
    }
    (RESULTS / "p7_manuscript_pdf.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
