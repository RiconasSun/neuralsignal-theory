"""Bound raw-index receipts and previous QC before any cached reuse."""
import register as r


def validate(audit,binding,expected,audit_sha,previous=None,previous_sha=None):
    if audit.get('raw_index_valid') is not True or audit.get('old_cast_equivalence_proved') is not True:
        raise ValueError('INDEX_AUDIT_NOT_STRICT_TRUE')
    for key in ('mouse_id','session_id','group'):
        if audit.get(key)!=expected[key] or binding.get(key)!=expected[key]:
            raise ValueError('INDEX_AUDIT_IDENTITY_MISMATCH')
    if binding.get('source')!=expected['source'] or binding.get('index_registration_sha256')!=expected['index_registration_sha256']:
        raise ValueError('INDEX_SOURCE_REGISTRATION_MISMATCH')
    if binding.get('audit_sha256')!=audit_sha:
        raise ValueError('INDEX_AUDIT_HASH_MISMATCH')
    if previous is not None:
        if not previous_sha or binding.get('previous_output_sha256')!=previous_sha:
            raise ValueError('PREVIOUS_QC_HASH_MISMATCH')
        for key in ('mouse_id','session_id','group'):
            if previous.get(key)!=expected[key]:raise ValueError('PREVIOUS_QC_IDENTITY_MISMATCH')
        if previous.get('source_etag')!=expected['source']['etag']:
            raise ValueError('PREVIOUS_QC_SOURCE_MISMATCH')
        if previous.get('final_values_exposed_to_analysis') is not False or previous.get('final_holdout_evaluated') is not False:
            raise ValueError('PREVIOUS_QC_ACCESS_STATE_INVALID')
    return True
