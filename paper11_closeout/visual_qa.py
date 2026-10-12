"""Render every PDF page and create traceable visual QA contact sheets."""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

HERE=Path(__file__).resolve().parent
POPPLER=Path('C:/Users/85993/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(HERE/'output'))
    output=Path(parser.parse_args().output).resolve(); qa=output/'visual_qa';qa.mkdir(exist_ok=True)
    report={}
    for name in ('manuscript','supplement'):
        subprocess.run([str(POPPLER/'pdftoppm.exe'),'-r','85','-png',str(output/(name+'.pdf')),str(qa/name)],check=True,capture_output=True)
        pages=sorted(qa.glob(name+'-*.png'))
        metrics=[]
        for page in pages:
            image=Image.open(page).convert('RGB'); arr=np.asarray(image)
            fraction=float(np.mean(np.min(arr,axis=2)<225))
            assert fraction>.008,page
            metrics.append({'page':page.name,'width':image.width,'height':image.height,'ink_fraction':fraction})
        report[name]={'pages':len(pages),'pixels':metrics}
        for chunk in range(0,len(pages),8):
            sheet=Image.new('RGB',(4*320,2*440),'#E6EBEC');draw=ImageDraw.Draw(sheet)
            for j,page in enumerate(pages[chunk:chunk+8]):
                image=Image.open(page).convert('RGB');image.thumbnail((310,405))
                x=(j%4)*320+(320-image.width)//2;y=(j//4)*440+24
                sheet.paste(image,(x,y));draw.text(((j%4)*320+8,(j//4)*440+6),page.stem,fill='#202B30')
            sheet.save(qa/f'{name}_sheet{chunk//8+1}.png')
    figures=sorted((output/'figures').glob('F*.png'))
    sheet=Image.new('RGB',(1800,4*430),'white');draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(figures):
        image=Image.open(path).convert('RGB');assert image.width>1500
        arr=np.asarray(image);assert np.std(arr)>10
        image.thumbnail((880,385));x=(j%2)*900+(900-image.width)//2;y=(j//2)*430+30
        sheet.paste(image,(x,y));draw.text(((j%2)*900+10,(j//2)*430+5),path.stem,fill='#202B30')
    sheet.save(qa/'figure_sheet.png')
    subprocess.run(['C:/Users/85993/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
                    str(HERE/'pdf_bounds.py'),'--output',str(output)],check=True)
    (qa/'render_metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('All PDF pages rendered/nonblank; text bounds checked:', {k:v['pages'] for k,v in report.items()})


if __name__=='__main__':main()
