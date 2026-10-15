"""Dormant future custodian capability bridge. No CLI, keys or D decoder here."""
from pathlib import Path
from release_control import canonical,digest,read_json,verify_approval
from broker import hold_process
from native import security

def grant_after_consumption(approval_path,anchor_path,binding_root,ledger,receipt,producer):
    """Call a pinned custodian producer only AFTER independent REAL durable consumption.

    This function is never called by this engineering mission or its reproduction.
    A future separately authorized custodian producer owns decryption, scoped export
    and exact-package ACL grant. Controller/scientific processes receive no keys.
    """
    security().require_custodian()
    approval=read_json(approval_path);anchor=read_json(anchor_path)
    if anchor['realm']!='REAL_D' or receipt['realm']!='REAL_D':raise PermissionError('REAL_ONLY_BRIDGE')
    body=verify_approval(approval,anchor,binding_root)
    source=Path(producer.__code__.co_filename).resolve()
    if 'custodian_producer.py' not in body['artifacts'] or digest(source.read_bytes())!=body['artifacts']['custodian_producer.py']:raise PermissionError('PINNED_CUSTODIAN_PRODUCER_REQUIRED')
    if receipt['binding']!=digest(canonical(body)) or receipt['authorization_id']!=body['authorization_id'] or receipt['principal']!=body['principal']:raise PermissionError('EXACT_CONSUMPTION_REQUIRED')
    ledger=Path(ledger);used=read_json(ledger/'consumed.json');intent=read_json(ledger/'intent.json')
    fence=Path(anchor['fence_root'])/(body['authorization_id']+'.json')
    if not fence.exists() or used['binding']!=receipt['binding'] or intent['binding']!=receipt['binding'] or used['ledger_tail']!=receipt['ledger_tail']:raise PermissionError('DURABLE_RECORDS_REQUIRED')
    previous=anchor['genesis_sha256'];lines=(ledger/'events.jsonl').read_bytes().splitlines()
    if len(lines)!=3:raise PermissionError('EXACT_LEDGER_STATES_REQUIRED')
    for i,line in enumerate(lines):
        e=__import__('json').loads(line)
        if e['sequence']!=i or e['previous']!=previous or e['state']!=('GENESIS','INTENT','CONSUMED')[i]:raise PermissionError('BROKER_LEDGER_INVALID')
        previous=digest(canonical(e))
    if previous!=receipt['ledger_tail']:raise PermissionError('BROKER_LEDGER_TAIL')
    # An exclusive delivery fence poisons every crash/retry; no partial release rollback.
    from release_control import durable_new
    with hold_process(body['principal']['pid']) as (actual,verify_target):
        verify_target(body['principal'])
        durable_new(ledger/'delivery_started.json',{'authorization_id':body['authorization_id'],'binding':receipt['binding'],'principal':actual})
        verify_approval(approval,anchor,binding_root);verify_target(body['principal'])
        # The held OS process handle remains live throughout this narrowly scoped producer call.
        return producer(body,verify_target)
