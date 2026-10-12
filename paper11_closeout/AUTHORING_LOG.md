# Authoring and Verification Record

All entries concern document engineering, not new scientific experiments.
Existing scientific evidence was frozen before authoring; no model/data runner
or external metadata request was executed in this closeout.

- Codex-code wrapper stopped before execution on its production-risk keyword
  check. No override or wrapper code mutation; scoped direct-tool implementation.
- Initial document build referenced a nonexistent baseline-selection key
  `global`; actual frozen key is `one_SE_baseline`. Fixed after source inspection,
  with a baseline-role regression check. Scientific selection never changed.
- MathText rejected the initial transpose styling; changed only the rendering
  notation to a supported roman T. Same mathematical definition.
- The bundled Poppler does not include pdftotext. Used bundled pdfplumber for
  glyph-bound checks and Poppler pdftoppm for every page raster; no installation.
- First visual pass found a Figure4legend/last-row overlap and an imprecise
  frontier legend. Moved the legend outside the data area and labelled the21
  Poisson baselines as a grid, not all as the strongest comparator. All figures
  regenerated and their source/sidecar hashes refreshed.
- Short tables are kept together; saved conditional-CI display rounded to six
  decimals for readability. Full original numeric CSV bytes remain unchanged.
- Final heading/table grouping initially assumed every ParagraphStyle had a
  keepWithNext field. A document-generation/replay attempt failed explicitly;
  used a false default for ordinary body styles and reran the complete pipeline.
  No gate was issued from that failed attempt or earlier stale PDF bytes.

Author contributions, funding, conflicts and submission approval are unknown,
explicitly disclosed, not fabricated. Manuscript completion does not certify
submission readiness or clear any historical scientific warning.
