"""Original byte-range reader with a separate append-only operational journal."""
import json
from paper13_ki_execution1.source import SourceReader as OriginalReader
from .common import P


class SourceReader(OriginalReader):
    def __init__(self, record):
        # Existing final evaluator already checks complete sealed C identity.
        # Keep this direct-constructor path behind the same original once marker.
        from . import final_D
        source=final_D.approved()
        marker=P/'results/final_D/ONCE_EXECUTION.json'
        if not marker.is_file():raise PermissionError('No D decoder before once-only final consumption')
        consumed=json.loads(marker.read_text(encoding='utf8'))
        if consumed['authorization_id']!=final_D.AUTHORIZATION_ID or consumed['source_freeze']!=source:
            raise PermissionError('D source authority/consumption mismatch')
        super().__init__(record)
        # The inherited original transport/cache/custody/budget methods are unchanged.
        # Never append to the historical source log bound by prior scientific freezes.
        self.journal=P/'results/source_access.jsonl'
        prior=[json.loads(line) for line in self.journal.read_text(encoding='utf8').splitlines()] if self.journal.is_file() else []
        self.total_calls+=len(prior)
        self.total_bytes+=sum(row.get('bytes',0) for row in prior)
