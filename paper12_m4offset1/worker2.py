"""Guard-only continuation of immutable diagnostic worker; mathematics unchanged."""
from pathlib import Path
import hashlib


def transformed(source):
    replacements={
      "    import numpy as np\n":"    import numpy as np\n    from roster_guard import validate_roster,validate_case\n",
      "        rows=prior['rows'];meta=prior['meta']\n":"        rows=prior['rows'];meta=prior['meta']\n        if hashlib.sha256(Path(__file__).with_name('reuse_records.json').read_bytes()).hexdigest()!=policy['reuse_records_sha256']:raise RuntimeError('REUSE_RECORDS_HASH')\n        validate_roster(rows,meta,states,manifest['sessions'][:1 if phase=='small' else 4])\n",
      "                if case in meta:continue\n":"                if case in meta:\n                    validate_case(case,arrays[region+'_A'],session,rows,meta)\n                    continue\n",
      "        valid=not failure and len(rows)==expected and len({(z['session_id'],z['region'],z['seed']) for z in rows})==expected and all(z['converged'] for z in rows)\n":"        valid=not failure and validate_roster(rows,meta,states,sessions)\n",
      "            save('offset_records.json',dict(rows=rows,meta=meta))\n":"            save('offset_records.json',dict(rows=rows,meta=meta))\n            gate['records_sha256']=hashlib.sha256((output/'offset_records.json').read_bytes()).hexdigest()\n",
      "    save('summary.json',dict(rows=rows,validation_access=False,final_access=False));save('gate_result.json',gate)\n":"    save('summary.json',dict(rows=rows,validation_access=False,final_access=False))\n    gate['summary_sha256']=hashlib.sha256((output/'summary.json').read_bytes()).hexdigest()\n    save('gate_result.json',gate)\n"
    }
    for old,new in replacements.items():
        if source.count(old)!=1:raise RuntimeError('GUARD_TRANSFORM_SOURCE_DRIFT')
        source=source.replace(old,new,1)
    return source


def main():
    source=Path(__file__).with_name('worker_v1.py').read_text()
    ns={'__name__':'guarded_offset_worker','__file__':__file__}
    exec(compile(transformed(source),__file__,'exec'),ns);ns['main']()


if __name__=='__main__':main()
