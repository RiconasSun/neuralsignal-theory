# Gate helper invocation correction

PRE_D_GATE_SEAL_1.log preserves a Python import failure before the helper body executed: launching the nested evidence script by filename placed its directory,rather than the repository root,on Python's ordinary import search path. No gate or D claim existed at failure.

The identical helper was then invoked through runpy.run_path from the repository root,as already used by the successful missing-approval denial test. No source,sys.path,sys.modules,scientific artifact,model or approved hash was changed. Actual gate and claim absence were asserted before invocation. PRE_D_GATE_SEAL_2.log records successful independent-receipt/full546hash/controller validation with no D source opened.

Only after this gate passed was the sole real D module command launched (REAL_D_ONE_SHOT_BATCH_1.log). The unsuccessful gate-helper invocation is not a neural fit or a D assessment and is retained permanently.
