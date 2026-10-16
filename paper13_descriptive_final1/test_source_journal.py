import unittest
import uuid
import json
from unittest.mock import patch
from . import common,final_D,source_adapter


class SourceJournalTests(unittest.TestCase):
    def test_new_transport_journal_preserves_inherited_methods_and_cumulative_budget(self):
        root=common.P/'work'/('source_log_'+uuid.uuid4().hex);(root/'results/final_D').mkdir(parents=True)
        (root/'results/final_D/ONCE_EXECUTION.json').write_text(json.dumps({'authorization_id':final_D.AUTHORIZATION_ID,'source_freeze':'reviewed'}))
        (root/'results/source_access.jsonl').write_text('{"bytes":15}\n{"bytes":15}\n')
        def original_init(reader,record):reader.total_calls=10;reader.total_bytes=100;reader.journal=root/'OLD_IMMUTABLE_LOG'
        with patch.object(source_adapter,'P',root),patch.object(final_D,'approved',return_value='reviewed'),patch.object(source_adapter.OriginalReader,'__init__',original_init):
            reader=source_adapter.SourceReader({})
            self.assertEqual(reader.journal,root/'results/source_access.jsonl')
            self.assertEqual(reader.total_calls,12);self.assertEqual(reader.total_bytes,130)
            self.assertFalse((root/'OLD_IMMUTABLE_LOG').exists())
        self.assertIs(source_adapter.SourceReader.block,source_adapter.OriginalReader.block)
        self.assertIs(source_adapter.SourceReader.read,source_adapter.OriginalReader.read)



if __name__=='__main__':unittest.main()
