"""Exact frozen-object range validation; fixtures and real transport use same code."""
import re


def byte_range(header, size, block=4194304):
    match = re.fullmatch(r'bytes=(\d+)-(\d+)', header)
    if not match: raise RuntimeError('INVALID_PERMITTED_RANGE')
    start, end = map(int, match.groups())
    if start % block or start < 0 or end != min(start + block, size) - 1 or not start <= end < size:
        raise RuntimeError('INVALID_PERMITTED_RANGE')
    return start, end


def validate_headers(status, headers, start, end, size, etag):
    if status != 206 or headers.get('Content-Range') != f'bytes {start}-{end}/{size}' or headers.get('ETag') != etag:
        raise RuntimeError('SOURCE_VERSION_OR_RANGE_INVALID')
    if headers.get('Content-Encoding') not in (None, 'identity'):
        raise RuntimeError('SOURCE_ENCODING_INVALID')


def validate(status, headers, body, start, end, size, etag):
    validate_headers(status,headers,start,end,size,etag)
    if len(body) != end-start+1:
        raise RuntimeError('SOURCE_RESPONSE_LENGTH_INVALID')
