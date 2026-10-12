"""Bibliography checks using only already-frozen local source documents."""
import json
from html.parser import HTMLParser
from pathlib import Path
from freeze import HERE, ROOT, load, sha


class Meta(HTMLParser):
    def __init__(self):
        super().__init__();self.values={}

    def handle_starttag(self, tag, attrs):
        if tag=='meta':
            a=dict(attrs)
            if a.get('name','').startswith('citation_'):
                self.values.setdefault(a['name'],[]).append(a.get('content',''))


def verify_references(output):
    freeze=load(HERE/'evidence_freeze.json')
    existing={6:'paper11_v2/alt_cohort_audit1/results/osf_complete/040.receipt',
              7:'paper11_v2/alt_cohort_audit1/results/figshare_document/001.receipt'}
    references=load(output/'references.json'); receipts=[]
    for reference in references:
        source=ROOT/reference['existing_verification_source']
        assert sha(source)==reference['source_sha256']
        record={'number':reference['number'],'new_search':False,'source_sha256':sha(source)}
        if reference['number'] in existing:
            name=existing[reference['number']]
            assert sha(ROOT/name)==freeze['previous_tracked_sha256'][name]
            parser=Meta();parser.feed((ROOT/name).read_text(encoding='utf-8'))
            title=parser.values.get('citation_title',[''])[0]
            doi=parser.values.get('citation_doi',[''])[0]
            assert title and title in reference['reference']
            assert doi and doi in reference['url']
            record.update(primary_source=name,primary_source_sha256=sha(ROOT/name),
                          title=title,doi=doi,authors=parser.values.get('citation_author',[]))
        receipts.append(record)
    return receipts


if __name__=='__main__':
    print(json.dumps(verify_references(HERE/'output'),indent=2))
