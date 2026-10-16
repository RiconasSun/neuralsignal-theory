# Actual-result PDF verification

Main manuscript:8 portrait A4 pages. Supplement:7 landscape A4 pages. Both are descriptive research drafts requiring owner submission review. `PDF_RENDER_INVENTORY.json` records final PDF SHA256 identities, every rendered page and extracted text length.

All15 actual-result pages were rendered with the bundled Poppler `pdftoppm` at1400-pixel maximum dimension. The complete main/supplement contact sheets were visually inspected, as were full-size main pages4–5 (all-six statistics, animal effects and both figures) and supplement pages3and5 (scores/statistics, reference summaries and wide sensitivity table). Text extraction found no empty page, black-square character or replacement glyph. Contact sheets are preserved here as `PDF_MAIN_CONTACT.png` and `PDF_SUPPLEMENT_CONTACT.png`; full-size intermediates are under the ignored `paper13_descriptive_final1/work/final_pdf_qa` directory and can be regenerated from the saved PDFs.

No material clipping, overlap, lost table column, missing figure, unreadable number or missing claim restriction was observed. Repeated table headers and page footers remain visible. Original full-precision CSV/JSON values are the numerical audit source; display values are rounded consistently. Every primary and guard row includes its paired-mouse mean, corrected p-value and confidence interval; all nine animal rows and the recent-event6/9failed coverage row remain. Reference and optional/subthreshold rows are retained in the supplement and machine-readable tables.

The bundled Poppler emitted display-font lookup messages for Symbol/ArialUnicode while exiting0. Actual PDFs use visible Helvetica text/ASCII-normalized mathematical symbols, and rendered/extracted pages showed no missing glyph. These messages are retained as an environment diagnostic, not counted as unresolved document defects.

This is actual saved-result layout verification, distinct from the earlier synthetic PDF test. It involves no neural-source access, model fit, D likelihood computation or new control draw. Independent scientific/engineering final review remains separately recorded.
