"""Decode native PowerShell logs without assuming the host's default encoding."""


def decode_native_log(raw):
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16')
    return raw.decode('utf-8-sig')
