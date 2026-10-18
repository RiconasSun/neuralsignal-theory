"""Public source-response metadata without unnecessary credentials/cookies."""
SENSITIVE={'cookie','set-cookie','authorization','proxy-authorization','x-api-key'}
def sanitize_headers(headers):
    return {str(k):'<REDACTED_HEADER>' if str(k).lower() in SENSITIVE else str(v) for k,v in headers.items()}
