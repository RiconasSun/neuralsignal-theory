$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot,'..'))
$runtime=[IO.Path]::Combine($root,'paper16_m1\work\runtime\Scripts\python.exe')
$sha=[Security.Cryptography.SHA256]::Create()
try {$digest=[BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($runtime))).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
if ($digest -ne 'de13d8017f63cb63b0b5bfd2f25e69245c9196433a224856ca1abde1e24d0cb7') {throw 'Frozen saved-verifier runtime launcher changed'}
& $runtime -B ([IO.Path]::Combine($PSScriptRoot,'reproduce_saved.py'))
exit $LASTEXITCODE
