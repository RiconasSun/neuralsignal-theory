# P12 Isolated Custody Recovery

**Stopped:** new M2FAIL / INCONCLUSIVE on source779839471 ReadTimeoutError.
8of26 sessions completed (4development/4final);1failed;17not executed.
No real A/B analysis export,M3-M7 fits,nulls or final evaluation occurred.
See MILESTONE_STATUS.md,QC_REPORT.md and results/closeout.json.
The newly authorized per-exposure ridge and all-family common offset were
registered prospectively;this does not override the failed prerequisite.

This is a new access-policy track. The original M1PASS,original M2FAIL,
original M0 and every P1-P11/native-support artifact remain immutable.
Prospective access registration:registration.json. Native implementation binding:
ROLE_POLICY1.json and role_registration.json. Source-only bounded retry:
transport_registration1.json. None changes scientific splits/QC/grids/thresholds.

## Real Boundary
The provided tool sandbox is NOT the scientific analysis principal:its actual
read/key/DACL probes failed,including exact-package-SID denial. Those failures
are retained. A separately launched native AppContainer with no capabilities,
clean whitelisted environment and no inherited handles passes file/key/DACL,
direct-network and custodian-memory negative probes while running copied
Python/numpy/scipy/h5py/cryptography. See results/isolation/native_profile_runtime2.json.

The host and interactive tool controller are trusted orchestration/custody.
They can administer profiles and access private material. This is real kernel
enforcement against the designated restricted analysis process,not protection
against a malicious operator/administrator or independent-human custody.
Operator procedural blinding remains a limitation. Never run scientific model
selection in the broad-filesystem tool sandbox or host interpreter.

## Four Compartments
A development train:private until M2cohort admission,then permitted restricted
analysis export. B development validation:sealed until registered M3evaluation.
C final calibration:private QC only now,unit-level results not model-selection
inputs;parameter fitting reserved for frozen M6policy. D final evaluation:
AES256-GCM,private keys;no evaluation or analysis exposure before independently
authorized M6release. A/B/C/D do not share decryption keys.

Raw complete target-unit source vectors are ephemeral custody memory,not
analysis exports. Source offsets/byte digests/calibration detail stay private.
Fixed-size count tensors are encrypted without compression;ciphertext hashes
are public integrity receipts,plaintext/whole-session spike hashes are not.
Compartment keys and allreal data are ignored under .private/;copied runtimes
and anypermitted later A/Bexports are ignored under exports/.

## Execution
Registration is append-once and already executed:
`python paper12_custody1/register.py`

Frozen native-role registration is append-once and already executed:
`python paper12_custody1/register_role_policy.py`

Historical trusted host extraction command after allpreconditions:
`python paper12_custody1/index3.py`
Must run outside AppContainer and preserve source version/byte checks. Failure
receipts prevent automatic replay over failed sessions. Original failed source
smoke is not deleted;uncompressed retry has distinct private/output namespace.
The earlier transport1 and index2 entrypoints are historical only. Independent
review identified two index/reuse integrity issues; append-only index validation,
all26 live metadata-index audits and source/identity/hash-bound protected issuer
attestation now govern index3. source_safe4 changes only diagnostic filenames
and close idempotence, not the frozen range/version/length checks. Do not rerun
the original extractor or automatically overwrite failed/interrupted sessions.
The current preserved index2 failure now stops index3. Do not automatically
retry or invoke a new extractor namespace. A bounded prospective same-source
transport recovery needs separate human authorization. No new dataset search.

Public actual-QC aggregation:
`python paper12_custody1/aggregate4.py`
This retains all26 candidates, explicitly labels missing receipts NOT_EXECUTED,
checks preserved index audits and receipt identities, and never reads private
calibration detail. A software test PASS is not cohort admission or study PASS.

One-command PowerShell saved-evidence reproduction:
`powershell -NoProfile -ExecutionPolicy Bypass -File paper12_custody1/reproduce.ps1`
Requires Python with numpy/scipy/h5py/cryptography/requests/pywin32 installed.
This verifies frozen historical hashes, tests and saved public QC aggregation.
It does NOT rerun live OS probes, acquire/decode source data, reproduce model
experiments or unlock holdouts. Its receipt is under ignored replay/.

Functional synthetic tests:
`python -m unittest discover -s paper12_custody1 -p "test_*.py" -v`
Fixtures do not count as experimental results or live security proof. Actual
native probes are in separate saved receipts. Live reruns create/delete only
mission-owned temporary profiles and change only mission-owned copied runtime
ACLs;no global runtime ACL loosening,credentials or security setting changes.

Finalrelease is not an automatic self-asserted gate here. If independent
release condition cannot be enforced,stop for explicit human authorization.
Source-decoded,analysis-exposed and final-evaluated states are separate.

This package must not claim that source byte checks prove native packet
continuity,histological accuracy,biological primitives,NAP or CWP validation.
