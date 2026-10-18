"""Authoritative binary64 hex native table plus verified JSON compatibility view."""
import json
import math
import struct
import numpy as np
import pandas as pd
from .source import json_safe,load_json

def encode_cell(value):
    if value is None:return dict(kind='none')
    if value is pd.NA:return dict(kind='pd.NA')
    if isinstance(value,(bool,np.bool_)):return dict(kind='bool',value=bool(value))
    if isinstance(value,(int,np.integer)):return dict(kind='integer',value=str(int(value)))
    if isinstance(value,(float,np.floating)):
        number=float(value)
        return dict(kind='binary64',bits=struct.pack('>d',number).hex(),
            classification='nan' if math.isnan(number) else 'positive_infinity' if number==math.inf else 'negative_infinity' if number==-math.inf else 'finite',
            hex=number.hex())
    if isinstance(value,str):return dict(kind='string',value=value)
    raise TypeError('Unsupported native table scalar: '+str(type(value)))

def decode_cell(cell,compatibility=False):
    kind=cell['kind']
    if kind=='binary64':
        value=struct.unpack('>d',bytes.fromhex(cell['bits']))[0]
        if math.isfinite(value):
            assert struct.pack('>d',float.fromhex(cell['hex']))==struct.pack('>d',value)
            assert cell['classification']=='finite'
        else:
            expected='nan' if math.isnan(value) else 'positive_infinity' if value>0 else 'negative_infinity'
            assert cell['classification']==expected
            if compatibility and math.isnan(value):return None
        return value
    if kind in ('none','pd.NA'):return None if compatibility or kind=='none' else pd.NA
    if kind=='integer':return int(cell['value'])
    if kind in ('bool','string'):return cell['value']
    raise ValueError('Unknown native scalar type')

def encode_table(frame):
    fields=list(frame.columns);assert len(fields)==len(set(fields))
    return dict(format='P15_NATIVE_BINARY64_HEX_V1',fields=fields,dtypes={f:str(frame[f].dtype) for f in fields},
        row_ordinals=list(range(len(frame))),index=[encode_cell(v) for v in frame.index],
        columns={f:[encode_cell(v) for v in frame[f].array] for f in fields})

def records(table):
    assert table['format']=='P15_NATIVE_BINARY64_HEX_V1'
    n=len(table['row_ordinals']);assert table['row_ordinals']==list(range(n))
    assert set(table['fields'])==set(table['columns'])==set(table['dtypes'])
    assert all(len(table['columns'][f])==n for f in table['fields'])
    return [{f:decode_cell(table['columns'][f][i],True) for f in table['fields']} for i in range(n)]

def verify_native(frame,table,view):
    assert table['fields']==list(frame.columns) and len(view)==len(frame)
    assert table['index']==[encode_cell(v) for v in frame.index]
    finite=0;classes={}
    for f in frame.columns:
        assert table['dtypes'][f]==str(frame[f].dtype)
        for i,value in enumerate(frame[f].array):
            encoded=encode_cell(value);assert encoded==table['columns'][f][i]
            classes[encoded.get('classification',encoded['kind'])]=classes.get(encoded.get('classification',encoded['kind']),0)+1
            recovered=decode_cell(encoded)
            if encoded['kind']=='binary64' and math.isfinite(float(value)):
                assert struct.pack('>d',float(value))==struct.pack('>d',recovered)==struct.pack('>d',view[i][f]);finite+=1
            else:assert view[i][f]==decode_cell(encoded,True)
    # Verify the actual complete persisted representation, not just an in-memory conversion.
    restored=load_json(json.dumps(json_safe(dict(native_table=table,trials=view)),allow_nan=False))
    assert restored['native_table']==table
    for i,row in enumerate(view):
        for f,value in row.items():
            if isinstance(value,float):assert struct.pack('>d',value)==struct.pack('>d',restored['trials'][i][f])
    return dict(finite_binary64_bit_patterns_verified=finite,classifications=classes,original_row_order=True,bitwise_pass=True)
