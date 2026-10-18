"""Saved-only post-batch reporting/audit; never reruns scientific evaluation."""
import socket
import runpy
import numpy as np
from paper15_final1.source import P,E,read,dump,sha


def denied(*args,**kwargs):raise PermissionError('Reporting denies neural-array/network access')


def run():
    socket.socket.connect=denied;socket.create_connection=denied;np.load=denied
    claim=read(P/'D_BATCH_CLAIM.json')
    assert claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH' and claim['attempt']==claim['D_batches']==1
    for name,h in claim['result_hashes'].items():assert sha(P/'results'/name)==h
    from paper15_final1.report import build
    build()
    interpretation=runpy.run_path(str(E/'scientific_interpretation.py'))
    interpretation['append_interpretation']()
    from paper15_final1.saved_audit import audit_fits,audit_D
    result=dict(fits=audit_fits(),D_saved_arithmetic=audit_D(),source_array_loads=0,
                new_real_fits=0,new_real_objective_AD_FD=0,D_reassessment=False,network_denied=True,
                D_claim_sha256=sha(P/'D_BATCH_CLAIM.json'))
    dump(E/'SAVED_FINAL_AUDIT_BEFORE_ARCHIVE.json',result)
    print('Complete saved-only report and independent arithmetic assembled without D reassessment')


if __name__=='__main__':run()
