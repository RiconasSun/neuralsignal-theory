"""Bind post-snapshot independent audit artifacts without changing the first seal."""
import datetime
from .closeout_saved import P,R,load,once,ref,sha

def main():
    path=P/'PROTECTED_STATE_MANIFEST.json';original=load(path)
    before={row['path']:row for row in original['files']}
    actual={p.relative_to(R).as_posix():p for root in [P/'work',P/'results'] for p in root.rglob('*') if p.is_file()}
    assert before.keys()<=actual.keys(),'An original saved file is missing'
    # Full-byte original identities are rechecked by the final saved-only verifier.
    # This create-only supplement admits solely later independent audit products.
    extra=[ref(actual[name]) for name in sorted(actual.keys()-before.keys())]
    allowed={'paper16_development_r4/work/INDEPENDENT_INTERRUPTION_FILE_HASHES.json'}
    assert all(row['path'] in allowed for row in extra),'Unregistered post-snapshot private file'
    once(P/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json',{
        'mission':'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'original_manifest_sha256':sha(path),'files':extra,
        'purpose':'Append-only binding of independently created saved-evidence audit inventory',
        'original_scientific_files_changed':False,'new_scientific_calls':0})
    print({'original_files':len(before),'supplement_files':len(extra),'complete_union_files':len(actual)})

if __name__=='__main__':main()
