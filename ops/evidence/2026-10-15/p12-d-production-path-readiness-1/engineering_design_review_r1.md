# Independent engineering/security design review r1

Reviewer: /root/final_custody_review, read-only independent agent. No protected data/key access. Review supplied before code freeze/testing.

Four P1 issues required repair: original encrypted AAD must use original locks/study/sourceETag; original mixed per-session namespaces cannot be represented by a flat source root; caller-supplied deployment hashes/key/anchor must not establish their own trust; all Host security dependencies including common/native/deployment loader must be verified.

Requested regression coverage: original-shaped cipher_core synthetic compatibility and actual-public metadata mapping; mixed-root synthetic producer delivery; protected pinned deployment plus key+anchor+owner substitution denial; common/native/authority/broker individual drift denial. No final approval yet. No protected real D/key reads performed. Authority remains pending.

Resolution candidate (awaiting formal preexecution review): producer original-context comparison and signed per-mouse source_roots; real_metadata public-only builder; RegisteredDeployment protected ACL+external digest and owner hash pin; host_identity checks every frozen new source; synthetic/unit coverage registered before execution.
