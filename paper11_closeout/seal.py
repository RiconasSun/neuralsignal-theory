"""Bind final document outputs; saved-only replay policy fixed before replay."""
from freeze import HERE, ROOT, sha, load
from build import write_json

output=HERE/'output'
files=[p for p in output.rglob('*') if p.is_file() and 'visual_qa' not in p.parts and p.name!='publication_manifest.json']
write_json(output/'publication_manifest.json',{
    'policy':'All tables/text/figures byte-identical; paginated PDFs text/page-count and50DPIpixel-identical, not filename-sensitive PDF object bytes',
    'outputs_sha256':{p.relative_to(output).as_posix():sha(p) for p in files},
    'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in list(HERE.glob('*.py'))+list(HERE.glob('*.ps1'))+[HERE/'manuscript.template.md']},
    'input_sha256':load(HERE/'evidence_freeze.json')['input_sha256'],
    'scientific_validation_pass':False,'original_R2':'FAIL / DATA_INSUFFICIENT','original_R3':'NOT EXECUTED'})
print('Publication artifact manifest sealed; no scientific gate changed.')
