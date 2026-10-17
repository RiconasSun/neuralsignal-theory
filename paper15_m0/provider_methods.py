"""Small official source excerpts for clocks/artifact semantics, no dataset search."""
import datetime,hashlib,json,requests
from .coverage import P,dump
def main():
    md=P/'source';ledger=json.loads((md/'ACCESS.json').read_text(encoding='utf8'))
    revfile=md/'IBLLIB_REVISION.json'
    if not revfile.exists():
        r=requests.get('https://api.github.com/repos/int-brain-lab/ibllib/commits/master',timeout=60);r.raise_for_status()
        dump(revfile,dict(sha=r.json()['sha'],url=r.url,time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    sha=json.loads(revfile.read_text(encoding='utf8'))['sha']
    for f in ['brainbox/io/one.py','ibllib/ephys/spikes.py','ibllib/ephys/ephysqc.py','ibllib/ephys/sync_probes.py','ibllib/io/extractors/ephys_fpga.py','ibllib/pipes/ephys_tasks.py']:
        dest=md/('ibllib_'+f.replace('/','_')+'.source')
        if dest.exists():continue
        url=f'https://raw.githubusercontent.com/int-brain-lab/ibllib/{sha}/{f}'
        r=requests.get(url,timeout=90);r.raise_for_status();b=r.content
        assert len(ledger)<190 and sum(x['bytes'] for x in ledger)+len(b)<30000000
        dest.write_bytes(b);ledger.append(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),kind='official_method_source'))
        dump(md/'ACCESS.json',ledger)
        print(f,len(b))
if __name__=='__main__':main()
