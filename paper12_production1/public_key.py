"""Public-only candidate verification; cannot provision an authority or issue a right."""
import argparse
from pathlib import Path
from .authority import inspect_public_key
from .common import new

def main():
    p=argparse.ArgumentParser();p.add_argument('--public-key-file',required=True);p.add_argument('--owner-fingerprint',required=True);p.add_argument('--independent-fingerprint',required=True);p.add_argument('--output',required=True);args=p.parse_args()
    value=Path(args.public_key_file).read_text(encoding='ascii').strip();result=inspect_public_key(value,args.owner_fingerprint,args.independent_fingerprint)
    new(args.output,dict(result,public_key_hex=value,REAL_D_SIGNATURE_ISSUED=False,D_RELEASE_CONSUMED=False,D_EVALUATION_EXECUTED=False))
    print('CANDIDATE_VERIFIED_NOT_ACTIVATED; REAL authority remains pending protected provisioning and independent review.')

if __name__=='__main__':main()
