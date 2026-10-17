# Preserved final-review editorial diagnostic

Mission: P14-V2-CANONICAL-NATIVE-RECOVERY.

Candidate under inspection: CANDIDATE_FREEZE.json SHA256142221d2d7ebfc95136f9e520a14fc248da155edaac6ccbcb1b5baca941a0845. Final archive acceptance has not yet been issued for this candidate.

The reviewer found literal mojibake in CANONICAL_NATIVE_REPORT.md lines36/62 and its prepare_closeout.py template lines39/65: the intended ranges6-7 and M2-M7 contain a corrupted en-dash encoding. `rg` confirms this is stored content, not merely terminal display. The scientific numbers and meaning remain recoverable; this is an ordinary documentation defect, not a new scientific source failure or evidence for a P0/P1 scientific issue.

The requested minimal repair is ASCII range punctuation in those two report/template locations. Preserve the prior candidate freeze, update affected payload/candidate identities, rerun affected saved reproduction and resume final independent review on the stable repaired candidate. No source rule, threshold, animal, model, result or neural access change is requested or authorized by this note. The reviewer made no implementation/report edit.
