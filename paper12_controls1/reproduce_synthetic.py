"""Fresh synthetic ledger/principal reproduction only, never real C/D."""
import subprocess
import sys
import uuid
from pathlib import Path
def main():
    here=Path(__file__).resolve().parent
    # Fresh numeric identifier guarantees no prior ledger/state is reset or overwritten.
    attempt=str(int.from_bytes(__import__('os').urandom(8),'big'))
    subprocess.run([sys.executable,str(here/'run_synthetic_calibration.py'),attempt],check=True)
    subprocess.run([sys.executable,str(here/'run_security.py'),attempt,'results/synthetic_C_'+attempt+'.json'],check=True)
    print({'fresh_native_synthetic_calibration_and_security':'PASS','attempt':attempt,'real_C_fit':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
if __name__=='__main__':main()
