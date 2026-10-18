"""Fresh PDF content/bounds checks and rasterization for human visual inspection."""
import re,shutil,subprocess,sys
from pathlib import Path
from pypdf import PdfReader
import pdfplumber
from PIL import Image,ImageOps,ImageDraw
from .source import P,E,sha,dump,rows

def poppler():
    found=shutil.which('pdftoppm')
    if found:return found
    candidate=Path(sys.base_prefix).parent/'native/poppler/Library/bin/pdftoppm.exe'
    assert candidate.exists(),'Poppler missing. Add its bin directory to PATH; no result or neural-data substitute is allowed.'
    return str(candidate)

def raster_directory(name,pdf_path):
    return P/'work/rendered'/name/sha(pdf_path)[:12]

def check():
    outputs={}
    for name in ['MAIN_MANUSCRIPT','SUPPLEMENT']:
        p=P/(name+'.pdf');reader=PdfReader(p);texts=[page.extract_text() for page in reader.pages];text='\n'.join(texts)
        assert len(reader.pages)>4 and all(t.strip() for t in texts)
        assert 'DESCRIPTIVE ONLY' in text and 'N4' in text
        assert not re.search(r'[A-Za-z]:\\|/Users/|\\Users\\|\.codex',text),'Private machine path in PDF'
        assert not any(c in text for c in ['\ufffd','\u25a0','\x00']),'Missing/replacement glyph'
        assert '{{' not in text and 'REFERENCES}}' not in text
        for needle in ['0.08658239652342035','0.015625','0.15625','NYU-21','UCLA033']:
            assert needle in text,(name,needle)
        for result in rows(P/'tables/REGISTERED_CONTRAST_ORDER.csv'):
            if name=='SUPPLEMENT' or result['cohort']=='Final':
                assert result['mean'] in text,(name,result['contrast'],'Exact mean numeral split or absent')
        bounds=[]
        with pdfplumber.open(p) as doc:
            for number,page in enumerate(doc.pages,1):
                # PDF drawing order need not equal reading order: validate the
                # actual right-footer region,not the last extracted text line.
                footer=page.crop((page.width-85,page.height-43,page.width-30,page.height-12)).extract_text()
                assert footer and footer.strip()==str(number),(name,number,'Page number missing at right footer')
                bad=[c for c in page.chars if c['x0']<29 or c['x1']>page.width-29 or c['top']<15 or c['bottom']>page.height-14]
                assert not bad,(name,number,'text outside page safe bounds')
                bounds.append(dict(page=number,characters=len(page.chars),safe_bounds=True))
        folder=raster_directory(name,p);folder.mkdir(parents=True,exist_ok=True)
        subprocess.run([poppler(),'-r','85','-png',str(p),str(folder/'page')],check=True,capture_output=True)
        images=sorted(folder.glob('page-*.png'))
        assert len(images)==len(reader.pages)
        # All pages appear in contact sheets; selected pages are also reviewed full-size.
        contacts=P/'work/contact_sheets'/sha(p)[:12];contacts.mkdir(parents=True,exist_ok=True)
        sheets=[]
        for at in range(0,len(images),12):
            sheet=Image.new('RGB',(1240,1290),'#dce2e5');draw=ImageDraw.Draw(sheet)
            for j,src in enumerate(images[at:at+12]):
                with Image.open(src) as image:thumb=ImageOps.contain(image.convert('RGB'),(290,395))
                x=(j%4)*310+(310-thumb.width)//2;y=(j//4)*430+25
                sheet.paste(thumb,(x,y));draw.text(((j%4)*310+12,(j//4)*430+7),f'{name} page{at+j+1}',fill='black')
            dest=contacts/f'{name}_{at//12+1}.png';sheet.save(dest);sheets.append(dest.relative_to(P).as_posix())
        outputs[name]=dict(pdf_sha256=sha(p),pages=len(reader.pages),safe_text_bounds=bounds,missing_glyphs=False,private_paths=False,page_numbers=True,rendered_pages=len(images),contact_sheets=sheets,text_characters=len(text))
        (P/'work'/f'{name}_EXTRACTED.txt').write_text(text,encoding='utf8')
    dump(P/'PDF_AUTOMATED_QA.json',dict(scope='Every PDF page text/bounds/rasterization checked; independent visual inspection is a separate required gate',documents=outputs,visual_review_required=True))
    return outputs
