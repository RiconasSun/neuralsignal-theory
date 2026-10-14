"""One independently provisioned native falsification job, no shared ACL cleanup."""
import sys
import launch
import study as r
def main():
    mission=r.HERE;job=sys.argv[1]
    if job not in ('job0','job1','job2'):raise RuntimeError('FIXED_JOB')
    reg=r.load(mission/'null_resume_registration.json');assignment=next(z for z in reg['jobs'] if z['job']==job);here=mission/'jobs'/job
    if r.sha(here/'execution_registration.json')!=assignment['execution_registration_sha256']:raise RuntimeError('FROZEN_JOB')
    for n,d in reg['source_sha256'].items():
        if r.sha(mission/n)!=d:raise RuntimeError('FROZEN_RESUME_SOURCE')
    a=launch.security();r.HERE=here;code=here/'exports/code';jobreg=r.load(here/'execution_registration.json')
    for n,d in jobreg['code_sha256'].items():
        if r.sha(code/n)!=d:raise RuntimeError('FROZEN_CODE')
    if (here/'results/nulls_launch_receipt.json').exists():raise RuntimeError('NO_JOB_RETRY')
    launch.native('nulls',here/'exports/development_AB',code,jobreg['code_sha256'],a)
if __name__=='__main__':main()
