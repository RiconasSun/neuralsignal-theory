"""Read only authoritative published patient/anatomy tables, not neural arrays."""
import re
from html.parser import HTMLParser
from register import OUT, save


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.table = 0
        self.cell = None
        self.row = None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table += 1
        elif self.table and tag == 'tr':
            self.row = []
        elif self.table and tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == 'table':
            self.table -= 1
        elif tag in ('td', 'th') and self.cell is not None:
            if self.row is not None:
                self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row = None


def main():
    rows = {}
    for table, name in [(1, '041.receipt'), (2, '042.receipt')]:
        parser = Tables()
        parser.feed((OUT / 'osf_complete' / name).read_text(encoding='utf-8'))
        rows[str(table)] = parser.rows
    save(OUT / 'published_patient_anatomy_tables.json', rows)
    for key, value in rows.items():
        print('Table', key)
        for row in value:
            print(' | '.join(row).encode('ascii', errors='backslashreplace').decode())


def patient_counts():
    from register import read
    source = read(OUT / 'published_patient_anatomy_tables.json')['1']
    patients = {}
    current = None
    for row in source:
        if re.fullmatch(r'(WVU\d+|UIC\d+|BJH\d+)', row[0]):
            current = row[0]
            patients[current] = []
        if row[0] == 'Sum':
            current = None
        if current and len(row) >= 6 and all(cell.isdigit() for cell in row[-6:]):
            patients[current].append(int(row[-3]))
    return [{'published_patient_label': patient, 'published_hippocampal_counts_by_table_row': counts,
             'at_least_one_published_session_ge5': max(counts, default=0) >= 5,
             'table_rows_not_mapped_to_event_session_ids': True, 'full_eligibility': 'UNKNOWN'}
            for patient, counts in patients.items()]


if __name__ == '__main__':
    from register import save
    counts = patient_counts()
    save(OUT / 'published_hippocampal_patient_potential.json', counts)
    print('Published table patients:', len(counts), 'with >=5 units in some table row:',
          sum(p['at_least_one_published_session_ge5'] for p in counts))
