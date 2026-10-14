"""Bind already-registered statistics implementation before score inference."""
import study as r
def main():
    r.save(r.HERE/'statistics_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_mouse_inference':True,'protocol_sha256':r.sha(r.HERE/'PROTOCOL.md'),'science_gate_sha256':r.sha(r.HERE/'results/science/native/gate_result.json'),'source_sha256':{n:r.sha(r.HERE/n) for n in ('mouse_statistics.py','test_statistics.py','analyze_saved.py')},'paired_mouse_family':4,'bootstrap':10000,'null_families':[16,16],'final_access':False})
if __name__=='__main__':main()
