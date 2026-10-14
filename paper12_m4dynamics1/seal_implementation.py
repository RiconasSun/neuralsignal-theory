import study as r
from controls import verify

def main():
    verify()
    r.save(r.HERE/'implementation_registration2.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_fits=True,
        previous_registration_sha256=r.sha(r.HERE/'implementation_registration.json'),
        reason='Append six-bin Hybrid coverage and matching admission count; no mathematical model changes',
        sha256={p.name:r.sha(p) for p in r.HERE.glob('*.py')},
        frozen_offset_states_sha256=r.load(r.OFFSET/'results/full/native/gate_result.json')['state_sha256'],
        M3_repeated=False,offset_repeated=False,final_access=False))

if __name__=='__main__':main()
