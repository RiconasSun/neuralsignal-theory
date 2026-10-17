"""Bounded public documentation and two pilot-session metadata, no spike loading."""
import datetime, hashlib, json
from pathlib import Path
import requests
from .coverage import P, dump

DOCS={
 'license':'https://registry.opendata.aws/ibl-brain-wide-map/',
 'release':'https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html',
 'download':'https://docs.internationalbrainlab.org/notebooks_external/data_download.html',
 'spikes':'https://docs.internationalbrainlab.org/notebooks_external/loading_spikesorting_data.html',
 'trials':'https://docs.internationalbrainlab.org/notebooks_external/loading_trials_data.html',
 'wheel':'https://docs.internationalbrainlab.org/notebooks_external/loading_wheel_data.html'}

def main():
    f=P/'PILOT_IDENTITY_FREEZE.json'
    if not f.exists():
        s=json.loads((P/'results/COVERAGE_SUMMARY.json').read_text(encoding='utf8'))
        dump(f,dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),mission='P15-SENSORIMOTOR-DATA-FIRST-M0',
            rule='Registered metadata-only tier/trial/lexical rule',pilots=s['pilot'],
            reserved_final_neural_access=False,all_pilot_mouse_sessions_permanently_development=True,
            prior_IBL_neural_exposure=False,source_exposure_evidence=['paper13/M0_REPORT.md','paper14_native1/FINAL_DELIVERY.json'],
            selected_region=s['selected_region'],source_license='Native IBL BWM CC BY 4.0, official AWS registry',
            no_models=True,no_new_scientific_thresholds=True))
    md=P/'source';md.mkdir(exist_ok=True)
    ledgerfile=md/'ACCESS.json';ledger=json.loads(ledgerfile.read_text(encoding='utf8')) if ledgerfile.exists() else []
    for name,url in DOCS.items():
        dest=md/(name+'.html')
        if dest.exists():continue
        assert len(ledger)<200 and sum(x['bytes'] for x in ledger)<30000000
        r=requests.get(url,timeout=90);r.raise_for_status();b=r.content
        assert len(b)+sum(x['bytes'] for x in ledger)<=30000000
        # Official download page contains shared demo credentials; save no credential-bearing HTML.
        # URLs, retrieval hash and non-secret limited excerpts are sufficient source receipts.
        if name=='download':
            dest=md/'download_receipt.json'
            dump(dest,dict(url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),
                note='Official ONE/ALF load_dataset/load_object documentation verified; raw page not archived because it includes public demo credentials.'))
        else:dest.write_bytes(b)
        ledger.append(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),kind='documentation',time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        dump(ledgerfile,ledger)
    for p in json.loads(f.read_text(encoding='utf8'))['pilots']:
        dest=md/(p['eid']+'.json')
        if dest.exists():continue
        url='https://openalyx.internationalbrainlab.org/sessions/'+p['eid']
        r=requests.get(url,timeout=90);r.raise_for_status();b=r.content
        assert len(ledger)<200 and len(b)+sum(x['bytes'] for x in ledger)<=30000000
        data=r.json();assert data['subject']==p['subject']
        # Session endpoint contains public dataset/file records only. No neural arrays requested.
        dump(dest,data)
        ledger.append(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),kind='pilot_metadata',time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
        dump(ledgerfile,ledger)
        print(p['subject'],len(data.get('data_dataset_session_related',[])), 'metadata records')

if __name__=='__main__':main()
