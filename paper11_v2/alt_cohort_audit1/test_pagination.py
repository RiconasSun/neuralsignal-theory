import unittest
from urllib.parse import parse_qs, urlsplit
from inventory_complete import paged


class PaginationTests(unittest.TestCase):
    def test_maintains_page(self):
        q = parse_qs(urlsplit(paged('https://api.osf.io/v2/files/abc/?page=7')).query)
        self.assertEqual(q['page'], ['7'])
        self.assertEqual(q['page[size]'], ['100'])

    def test_idempotent(self):
        u = 'https://api.osf.io/v2/nodes/vh5kq/files/?page%5Bsize%5D=10&page=3'
        self.assertEqual(paged(paged(u)), paged(u))

    def test_preserves_filters(self):
        q = parse_qs(urlsplit(paged('https://api.osf.io/v2/nodes/?filter[public]=true')).query)
        self.assertEqual(q['filter[public]'], ['true'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
