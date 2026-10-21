# Current R4 handoff — external interruption

This additive handoff supersedes the operational status of the immutable prospective CURRENT_HANDOFF.md. The scientific worker is stopped after owner-confirmed shutdown. Do not restart it, reset its deadline, refit the incomplete task, complete M4, claim E, access Final C/D or start M6/P17.

Read FINAL_REPORT.json, SCIENTIFIC_CLOSEOUT.md, EXECUTION_FACTS.json, TASK_OUTCOMES.json and FINAL_SCIENTIFIC_REVIEW_1.md in the mission evidence directory. The actual review accepted ACCEPTED_TRUTHFUL_INTERRUPTED_ARCHIVE_ONLY, with technical bug_count=0/warn_count=0. The only remaining external action is a separate owner decision on the exact reviewed public payload after local sealing/review/commit. The older 127-file approval is insufficient. Publication approval would authorize only transport of the reviewed commit; it would not authorize science.

One command for protected local saved-only verification:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_development_r4\REPRODUCE_SAVED.ps1
```

Requires original protected saved bundle and pinned runtime. No refit/network fallback. Actual self-containing commit SHA and clean/remote receipts reside in ignored mission evidence PUBLICATION_LOCAL/, outside scientific inventory and public payload.
