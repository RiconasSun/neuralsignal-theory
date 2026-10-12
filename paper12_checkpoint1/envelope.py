"""Verified single-file immutable checkpoints; synthetic-only, no network API."""
import hashlib
import json
import struct
MAGIC=b'P12CP001'
MAX_BODY=4194304


def pack(body,source):
    if not isinstance(body,bytes) or not body or len(body)>MAX_BODY:raise ValueError('BODY_SIZE_INVALID')
    header=dict(source=source,bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
    text=json.dumps(header,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
    if len(text)>65536:raise ValueError('HEADER_SIZE_INVALID')
    return MAGIC+struct.pack('<I',len(text))+text+body


def unpack(value,source,expected_body_sha256):
    if len(value)<12 or value[:8]!=MAGIC:raise ValueError('ENVELOPE_MAGIC_INVALID')
    size=struct.unpack('<I',value[8:12])[0]
    if not 0<size<=65536 or len(value)<12+size:raise ValueError('ENVELOPE_HEADER_INVALID')
    header=json.loads(value[12:12+size]);body=value[12+size:]
    if set(header)!=set(('source','bytes','sha256')) or header['source']!=source:
        raise ValueError('SOURCE_IDENTITY_INVALID')
    digest=hashlib.sha256(body).hexdigest()
    if not body or len(body)>MAX_BODY or type(header['bytes']) is not int or len(body)!=header['bytes']:
        raise ValueError('COMPLETE_LENGTH_INVALID')
    if header['sha256']!=digest or digest!=expected_body_sha256:raise ValueError('BODY_HASH_INVALID')
    return body
