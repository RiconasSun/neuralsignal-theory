import unittest
from derive import file_rows, metadata_sessions


class InventoryTests(unittest.TestCase):
    def test_folder_not_unit(self):
        self.assertEqual(file_rows([{'type': 'files', 'id': '1', 'attributes': {'kind': 'folder'}}]), [])

    def test_mat_txt_one_session(self):
        rows = [{'id': str(i), 'materialized_path': '/Events Files/BJH024_CoCo_Sess1.' + ext,
                 'name': 'BJH024_CoCo_Sess1.' + ext} for i, ext in enumerate(['mat', 'txt'])]
        self.assertEqual(len(metadata_sessions(rows)), 1)
        self.assertIsNone(metadata_sessions(rows)[0]['hippocampal_units'])

    def test_unknown_labels_retained(self):
        x = metadata_sessions([{'id': 'x', 'materialized_path': '/Events Files/odd.txt', 'name': 'odd.txt'}])
        self.assertEqual(x[0]['patient_file_label'], 'UNKNOWN')
        self.assertEqual(x[0]['eligible'], 'UNKNOWN')

    def test_task_sessions_not_independent_patients(self):
        rows = [{'id': str(i), 'materialized_path': '/Events Files/BJH024_' + task + '.txt',
                 'name': 'BJH024_' + task + '.txt'} for i, task in enumerate(['CoCo_Sess1', 'ImageNet_Sess1'])]
        sessions = metadata_sessions(rows)
        self.assertEqual(len(sessions), 2)
        self.assertEqual(len({r['patient_file_label'] for r in sessions}), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
