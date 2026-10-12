"""Check every extracted text glyph lies inside final PDF page bounds."""
import argparse
import json
from pathlib import Path
import pdfplumber

parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
folder=Path(parser.parse_args().output);metrics={}
for name in ('manuscript','supplement'):
    with pdfplumber.open(folder/(name+'.pdf')) as pdf:
        failures=[]
        for number,page in enumerate(pdf.pages,1):
            for char in page.chars:
                if char['x0']<25 or char['x1']>page.width-25 or char['top']<20 or char['bottom']>page.height-15:
                    failures.append({'page':number,'character':char['text'],'x0':char['x0'],'x1':char['x1'],'top':char['top'],'bottom':char['bottom']})
        metrics[name]={'pages':len(pdf.pages),'out_of_bounds_glyphs':failures}
        assert not failures,(name,failures[:5])
(folder/'visual_qa'/'text_bounds.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print('Every PDF page glyph bound checked:',{k:v['pages'] for k,v in metrics.items()})
