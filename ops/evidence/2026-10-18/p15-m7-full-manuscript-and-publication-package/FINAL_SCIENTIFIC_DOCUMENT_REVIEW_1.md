# Independent scientific/document consistency review — preserved unsuccessful candidate

Mission: P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE. Reviewer: /root/pivot_review.

Decision: **REPAIR_REQUIRED**. Open P0: **0**. Open P1: **2**. The current publication candidate is not accepted. These are document/presentation defects; they do not authorize changing any scientific outcome, criterion or original source.

Candidate SHA256: `f0ece0c97abaf4e621596f23da3d5f8b98f8e372e8ae6656524331fe8bc8ea75`.
Baseline SHA256: `0f310513b98352495da68900886145cd7fe6c81142a4f34e30cd7ebacf2df09a`.
Base: `bdec0e19621cc8018abe11c5633ce76aff611443`.

## P1 findings

### P1-01 — Development selection denominator is misstated

`paper15_manuscript/SUPPLEMENT.md`, S7, line309, states: **“The complete61candidate B-selection table follows”**. The displayed and copied original B_SELECTION table has **37 seed-grouped candidate configurations**, representing **61 optimizer starts per mouse** because D/S each have three starts. These denominators are distinct in the frozen `selection.groups()` implementation, selected-state freeze, original CSV and independent METHODS_CONSISTENCY_ORACLE. The erroneous sentence misstates search/selection accounting and contradicts the actual table. It also reaches the rendered supplement; correct table bytes elsewhere do not cure the explanatory error.

Minimum repair: describe **37 seed-grouped candidates representing61 optimizer starts per mouse**. Keep the original 37-row CSV, all selected configurations, every attempted fit and all original results unchanged. Extend a saved-table/document regression to require the actual37-row count and corrected explanation, and reject the old61-candidate wording. Relevant owner requirements: exact grids/selection records, trustworthy full Methods, and no unsupported scientific accounting (REQ-169/170/217/223).

### P1-02 — Figure2 clips an actual Development mouse effect

`paper15_manuscript/production.py:114` sets the shared Figure2 x-axis to **[-0.01,0.245]**. The preserved Development primary effect for **KS051 is0.2643258830149669**, outside that range. Its row label remains visible but its actual data point is clipped from all exported Figure2 formats and the main PDF. The independent number reviewer identified this defect; I confirmed the frozen plotting limit, saved effect and rendered figure/contact sheet. Reporting the mouse elsewhere does not satisfy a figure whose caption promises each mouse's measured point.

Minimum repair: compute shared plotting bounds from all16 saved mouse effects plus plotted means/interval endpoints, with a visible margin. Preserve the values, identities and cohort separation; no score transformation or new inference. Extend the existing Figure2 presentation regression to require every individual point and interval endpoint inside the visible bounds. Rebuild the affected PNG/SVG/PDF, main PDF, associated manifests/QA/contact sheets and current saved-only reproduction. Relevant requirements: actual values, all animal-level primary effects, correct axes/uncertainty and no clipped content (REQ-187/199/200/201/269/275).

## Review scope and independent checks completed

I read the archived OWNER_REQUEST and all326 baseline entries:320 original source-line clauses plus six explicit closure obligations. Heading/introduction clauses were treated as context; their substantive conjunctive requirements were checked in the corresponding manuscript/supplement/artifacts rather than claiming mere heading presence proves compliance. All original owner_line/text identities were retained. The original results-locked/no-neural/no-D boundaries remain in force.

I independently rehashed all **74 current candidate files** and all **3,099 preserved scientific/protocol/source/review artifacts**. No mismatch was found. I reviewed the complete19-page main/36-page supplement source, all S1-S16 methods/results sections, actual copied tables and source maps, seven-figure generating source, references/bibliography/attribution, A1-A10 evidence map,36 claim rows and all author questions A-J. The prior reviewer-owned Methods oracle was cross-checked against its frozen sources.

Scientific consistency otherwise checks out: 20 original12Development/8Final identities, actual10Development/eight labs and6Final/four labs, all four exclusions, source versions/native mapping/QC/strict-past timing/partitions, binary64 corrective history, nested Poisson models, HMM causal filtering/conditional likelihood, fixed DCT history C, static mixture S, three-seed joint-mass ensembles, objective/T versus effect/Q, nominal/active parameter distinctions, original solver/bounds/PG/AD/all-step FD rules and selected hyperparameters are accurately retained. The sole additional search-denominator error is P1-01 above.

The manuscript and supplement retain both cohorts' six contrast summaries in registered order, all individual effects/exposures, all392 Final numerical certificates,66 sensitivity states/64available,33 sensitivity panels per cohort and24 reference panels per cohort. Final S02 has6 mice,S03 has4 and remains unavailable. Sensitivity refits are B0-B4 only; D/C/S receive no unperformed robustness credit. The paper distinguishes true zero counts from invalid exposure and nominal curated-release units from inferential mice. No pooled or additional hypothesis test is claimed.

All six Final verdicts remain **DESCRIPTIVE ONLY**. Primary effect0.08658239652342035,95%CI[0.04944033234175033,0.14110164811873427],rawp0.015625 and all six positive effects do not clear the failed eight-mouse floor,width0.09166131577698394>0.01 or unestablished independence/sign-symmetry assumptions. All five secondary Holm values remain nonsignificant; the minimum possible adjusted value at n6 is0.15625. Development N1=7/10<8,its failed precision,Final D-B4/N2 and D-S/N1/N2 failures,and N4 unavailable at five Development/three Final mice are present in the main narrative and supplement. N3 is correctly identified as repeated B4 wheel-likelihood diagnostic,not D/C/all-movement evidence. No equivalence,causal mechanism,persistent biological state,model superiority,independent-lab,human/BCI or CWP/NAP validation is inferred.

Historical359 starts on rounded inputs,corrective1,135 and Final392 remain separated,cumulative1,886,with no reuse/retroactive validity or original-budget rewrite. Whole-record low-level decoding permission is distinguished from C-only scientific export; no third-party/admin-proof custody is claimed. Earlier noFinalaccess statements remain explicitly historical; the actual single D assessment is consumed. The present document production does not reopen it.

## Bibliography, attribution and visual evidence

All12 reference records correspond to primary methodological/source publications or official release/licence documentation. The preserved original Holm PDF verification record identifies Sture Holm,1979,Scandinavian Journal of Statistics6:65-70 and PDF SHA2564317a0d1555dad949dc1760605d925ba20037402827741fdf99cd8ea37e80c46. The failed Crossref DOI query is retained as failed and the unverified DOI is omitted; JSTOR stable4615733 remains. Hemerik/Goeman's2017online versus2018issue dates are differentiated. Citation scope is appropriate: literature motivates methods/confounds and does not supply this study's measured effect sizes.

Independent current online checks corroborated the [official AWS provider/licence/bucket](https://registry.opendata.aws/ibl-brain-wide-map/), [official IBL release denominator/version documentation](https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html), [original transformation-invariance reference](https://link.springer.com/article/10.1007/s11749-017-0571-1) and [original movement-confound author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC6768091/). Nature authentication redirection and an unsuccessful Holm PDF refetch were not called successful new full-text verification; the frozen primary-source records remain distinguishable. No external peer review,endorsement,publication/bioRxiv acceptance or invented author/funding/affiliation/ethics declaration is claimed. Authorized placeholders and actual author approval before submission are explicit.

I inspected all55 pages in the five supplied contact sheets, detailed supplement page22(full-precision tables), and Figure5 individually. Equations/table continuation/page numbers/references/cohort labels and visible unavailable panels are otherwise coherent; automated current PDF text/bounds/glyph/private-path proof and producer visual review are hash-bound. Figure2's missing point demonstrates why successful raster/bounds QA alone is not scientific figure completeness. Author review and publication polish cannot replace that point.

## Reproduction and closure assessment

The actual native PowerShell attempt3 receipt records exit0,10 document regressions,3,099 locked source checks,seven figure triplets,19/36PDF pages,unchanged candidate/PDF hashes and zero neural arrays,old scientific imports,new fits,predictions/likelihood calls,new hypotheses or D reruns. I verified its actual typed fields/log/PDF/candidate identity. Its success applies to the frozen state but does not detect the two document defects above. A corrected final candidate needs a fresh affected document rebuild/reproduction.

The saved-only implementation checks original stored mouse arithmetic/registered tests,not raw fit reproducibility. No old worker is imported or called. Dependency/Poppler/environment and human author/submission boundaries are documented. I statically reviewed `closeout.py` typed review/reproduction/PDF/visual/current-Git predicates and independently ran its **five synthetic metadata regressions under -W error**,all PASS. No Git mutation or scientific execution occurred. Review receipts with stale candidates,rejection/boolean-count substitution or absent live readback cannot create terminal acceptance.

Future Git clauses remain **OPEN**,not defects requiring self-referential invented hashes: actual scoped commit/push,remote changed-blob readback/clean and final STOP must occur later. Current FINAL_DELIVERY is visibly pending independent claim/source acceptance and real Git metadata. Its interim false/null fields are not premature completed-archive claims. A later metadata H2 may truthfully name actual H1; current H2's own receipt belongs outside its tracked bytes.

Exact path/hash-bound preservation of generated SVG formatting and the original BUILD_2 traceback may be considered separately if actual diagnostics show only nonsemantic whitespace and the same check passes every nonexempt file. That cannot exempt clipping,alter source identity,be a blanket future-generated-file waiver,or reuse a stale Figure2 SVG hash after repair.

## Required continuation

Preserve this rejected report and receipt. Repair only the grouped-candidate prose and Figure2 visibility,with focused document regressions and rebuilt/refrozen publication outputs. Preserve all3,099 old artifacts and all scientific values. Obtain final consistency review against the corrected candidate and actual new native reproduction before setting claim/source audit completion. Do not rerun neural fitting,predictions,D or new scientific tests. No additional scientific-source/document P0/P1 was found in the completed review.
