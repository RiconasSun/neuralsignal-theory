"""Exactly two pinned DANDI inventories and one pinned code/document source."""
import json
from transport import META,Transport,POLICY


def main():
    t=Transport()
    for candidate in POLICY['datasets']:
        ds,version=candidate['id'],candidate['version']
        base=f'https://api.dandiarchive.org/api/dandisets/{ds}/versions/{version}/'
        t.save(ds+'_version.json',base)
        url=base+'assets/?page_size=200'
        for page in range(POLICY['bounds']['api_pages']):
            body=json.loads(t.save(f'{ds}_assets_{page:02}.json',url))
            url=body.get('next')
            if not url:break
        else:raise RuntimeError('Manifest pagination bound exceeded')
    repo=json.loads(t.save('pfcmap_commit.json','https://api.github.com/repos/hejDMC/pfcmap/commits/HEAD'))
    commit=repo['sha']
    t.save('pfcmap_tree.json',f'https://api.github.com/repos/hejDMC/pfcmap/git/trees/{commit}?recursive=1')
    t.save('pfcmap_README.md',f'https://raw.githubusercontent.com/hejDMC/pfcmap/{commit}/README.md')
    t.save('reference.html','https://www.nature.com/articles/s41593-025-02190-z')
    print(json.dumps({'commit':commit,'requests':t.calls,'bytes':t.used}))


if __name__=='__main__':main()
