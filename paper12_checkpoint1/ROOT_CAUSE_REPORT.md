# Windows Checkpoint Diagnosis

The exact process/handle responsible for the historical WinError5 is not
identified. No protected experimental contents were inspected. The mechanism
and a scoped alternative were investigated with disposable synthetic fixtures.

## Observations

The registered original protected-directory sequence had 5/200 failures in
candidate1, 0/200 in candidate2 and 3/200 in candidate3. All trials, including
unfavorable ones, remain saved. The previous 1/20 and real M2 failure remain
unchanged. A synthetic open child without delete sharing reproduces directory
rename denial with unchanged custody ACL. This proves a capable mechanism, not
the identity of any historical endpoint-security process or open handle.

Six controlled native probes found: MoveFileExW worked with a closed destination
but returned5 with either open shared-delete or open non-delete-sharing target.
ReplaceFileW worked with closed/shared-delete targets and returned32 with a
non-delete-sharing target. Source/destination ACLs and same-volume location were
held constant. These are measured results on this Windows installation.

The implementation therefore publishes a fully verified single envelope file
with MoveFileExW when absent; explicit expected-old-digest replacement uses
ReplaceFileW with flags0 and a protected same-volume backup. No ignore-ACL flag,
copy-delete fallback, permission widening or security-control disable is used.
Microsoft documents the replacement function's ACL/attribute preservation and
sharing requirements. [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew).

## Other Diagnosed Conditions

Child-only DELETE denial is insufficient when the parent grants DELETE_CHILD.
The injection now restricts both, obtains native access-denied5, and verifies
the candidate rejects the altered DACL without repairing it. Sharing-conflict
probes separately obtain32; writer fencing obtains33. These are not conflated.
Windows sharing/deletion access rules are described in [CreateFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea).

Long crash-fixture journal paths caused Python FileNotFoundError. Compact journal
names use a 128-bit digest prefix, while the complete256-bit artifact/source
identity remains mandatory and conflicting identities fail closed. Paths at or
above the candidate's explicit248-character staging bound are refused. Extended
Win32 names are used where native APIs require them. This does not enable global
long-path policy or claim support for arbitrary path lengths.

Writes are flushed, fsynced and closed before replacement. Staging files receive
the original custody DACL before the mid-write crash hook. Persistent append-only
intent/result records fence three total publication calls across restart; saved
terminal results stop even if interruption prevented a STOP file. Per-target
native byte-range locks prevent conflicting writers.

Read-only/reparse/out-of-study paths are rejected; other-volume roots are refused
before I/O. No actual cross-volume move was performed. No antivirus or endpoint
security configuration was changed or asserted to be the historical cause.

## Preserved Failures

Candidate1:200 ordinary commits passed but5/18 injection tests failed.
Candidate2:200 passed but3/18 failed. Both remain FAIL/CHECKPOINT_REPAIR_UNVERIFIED,
with matching code snapshots and original seals. Prospective amendments record
API/path/oracle corrections; no successful seed selection or failure deletion.

## Interpretation Boundary

Verification concerns atomic visibility/integrity and safe-stop behavior in
tested synthetic Windows contexts, not power-loss durability, every filesystem,
or a malicious host administrator. Mid-write termination is tested explicitly;
before/after-publication termination is separately tested. Interruption inside
an indivisible native replacement instruction was not instrumented. Actual
transport integration and physiological/scientific admission were not executed.
