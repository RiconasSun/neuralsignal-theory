import study as r
from controls import verify
from roster import validate

def main():
    verify();validate(r.load(r.HERE/'original_training_diagnostics.json')['rows'])
    sources=list(r.HERE.glob('*.py'))+[r.HERE/'original_training_diagnostics.json']
    r.save(r.HERE/'implementation_registration3.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_real_fits=True,
        previous_registration_sha256=r.sha(r.HERE/'implementation_registration2.json'),reason='Independent review guards: original oracle SHA, immutable 216 training reference, immediate numerical STOP',
        sha256={p.name:r.sha(p) for p in sources},final_access=False))

if __name__=='__main__':main()
