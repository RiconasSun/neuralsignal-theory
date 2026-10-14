"""Registered primary mouse inference; scalar saved scores only."""
import study as r
def main():
    from mouse_statistics import aggregate
    reg=r.load(r.HERE/'statistics_registration.json')
    if r.sha(r.HERE/'mouse_statistics.py')!=reg['source_sha256']['mouse_statistics.py']:raise RuntimeError('FROZEN_STATISTICS')
    r.save(r.HERE/'primary_analysis_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_primary_inference':True,'source_sha256':r.sha(r.HERE/'analyze_primary.py'),'statistics_registration_sha256':r.sha(r.HERE/'statistics_registration.json'),'score_sha256':r.sha(r.HERE/'results/science/native/scientific_scores.json'),'final_access':False})
    value=aggregate(r.load(r.HERE/'results/science/native/scientific_scores.json')['rows']);r.save(r.HERE/'results/primary_statistics.json',value)
    print(value['primary']['statistics'])
if __name__=='__main__':main()
