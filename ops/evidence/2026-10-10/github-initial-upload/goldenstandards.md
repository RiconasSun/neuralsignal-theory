# GitHub Initial Upload

Mission: github-initial-upload
Target: https://github.com/RiconasSun/neuralsignal-theory.git
Branch: test
Baseline revision: 2, frozen before publication-tool edits on 2026-10-10.

## Approved Contract

Upload the local NSI project to the user-specified GitHub repository.
Preserve local research files and scientific results. Exclude credentials and
runtime caches. Never push main, force push, or create a pull request.
User approved code, papers, results, data-source links and provenance; raw
neuroimaging remains local. User approval: "就这么实现" after the data-link proposal.
Publish truthful existing evidence; absent historical metadata remains explicitly
unrecorded. This mission does not repair historical scientific evidence gaps.

## Requirement Baseline

| ID | Requirement | Verification | Status |
| --- | --- | --- | --- |
| REQ-001 | Preserve existing local files and research content | No deletion or product edits; upload-only diff | VERIFIED |
| REQ-002 | Upload the selected project scope to origin/test | Remote commit equals local commit | OPEN |
| REQ-003 | Exclude credentials and runtime caches | Explicit file inventory and secret-pattern scan | VERIFIED |
| REQ-004 | Exclude raw neuroimaging; retain it locally | User-approved scope; ignored-file audit | VERIFIED |
| REQ-005 | Record inventory, review, and final upload evidence | Evidence files and remote readback | OPEN |
| REQ-006 | Add source/version/access/sample/processing references for P1-P10 | Per-paper availability guides and source inventory | VERIFIED |
| REQ-007 | Link published figures to generation scripts and analysis inputs | Figure provenance table and local-link validation | VERIFIED |
| REQ-008 | Record checksums and reproducible publication instructions | Generated SHA256 inventory and validation command | VERIFIED |

baseline_requirement_count: 8
Test oracle: exact staged inventory, no confidential files, and matching remote
and local commit hashes. This is an upload mission, not scientific validation.

## Preflight

The workspace initially had no Git repository. Initialized a new test branch.
Remote ls-remote succeeded with no refs: repository is empty, so main/test
comparison and branch integration are not applicable to this initial upload.
GitHub authentication works outside the network-restricted sandbox.
No existing ops mission files or templates were found during initial discovery.
This explicit user upload request supplies the current mission contract.

## Product Decision

target_actor: reader or replicating researcher
product_problem: data and figure provenance must remain accessible without raw imaging redistribution
approved_product_behavior: source links, precise local inventories, existing pipeline references, explicit gaps, publication on test
primary_flow: README -> per-paper data guide -> source/manifest -> scripts -> figures
existing_behavior_preservation: all scientific analyses, claims, and local raw files preserved
non_goals: new analyses, fabricated snapshot identifiers, full raw-data reruns, main promotion
acceptance_behavior: all P1-P10 guides exist; figures and local references resolve; no raw scans or credentials tracked; origin/test hash matches
open_decisions: 0

## Baseline History

Revision 1 -> 2: explicit user decision resolved REQ-004 and added REQ-006
through REQ-008 for the approved data-link and provenance documentation.
