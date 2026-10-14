"""Storage-path implementation correction; unchanged statistical formulas/families."""
import study as r
def main():
    r.save(r.HERE/'statistics_path_recovery_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_full_null_inference':True,'original_statistics_registration_sha256':r.sha(r.HERE/'statistics_registration.json'),'mouse_statistics_source_unchanged_sha256':r.sha(r.HERE/'mouse_statistics.py'),'recovered_analyze_saved_sha256':r.sha(r.HERE/'analyze_saved.py'),'change':'Read the exact completed checkpoint/job aggregate instead of the failed partial native directory. No statistic, bootstrap seed, effect definition, p-value family or model selection changed.','null_resume_registration_sha256':r.sha(r.HERE/'null_resume_registration.json'),'final_access':False})
if __name__=='__main__':main()
