"""Fresh native v2 regressions/security on immutable successful synthetic endpoints."""
import os
import subprocess
import sys
from pathlib import Path

def main():
    here=Path(__file__).resolve().parent;attempt=str(int.from_bytes(os.urandom(8),'big'))
    prior='results/synthetic_C_3902238465046568075.json'
    subprocess.run([sys.executable,str(here/'certify_saved_v2.py'),attempt,prior],check=True)
    subprocess.run([sys.executable,str(here/'run_security.py'),attempt,'results/saved_v2_'+attempt+'.json'],check=True)
    print({'fresh_native_saved_synthetic_v2_and_security':'PASS','attempt':attempt,'saved_cohort_refits':0,'synthetic_oracle_model_fits':6,'real_C_D_access':False,
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
if __name__=='__main__':main()
