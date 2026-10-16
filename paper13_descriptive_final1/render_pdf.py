"""Render frozen saved manuscript text; no scientific computation or data access."""
import html
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether

P=Path(__file__).resolve().parent


def clean(text):
    for left,right in [('−','-'),('–','-'),('—','-'),('≥','>='),('≤','<='),('→',' to '),('’',"'"),('“','"'),('”','"')]:text=text.replace(left,right)
    text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',html.escape(text))
    return text


def render(source,output,wide=False):
    pagesize=landscape(A4) if wide else A4
    width=pagesize[0]-100
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PaperBody',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8,splitLongWords=True))
    styles.add(ParagraphStyle(name='PaperCell',fontName='Helvetica',fontSize=6.5 if wide else 7,leading=8.5,splitLongWords=True))
    styles['Title'].fontSize=19;styles['Title'].leading=24
    styles['Heading1'].fontSize=14;styles['Heading1'].leading=18
    styles['Heading2'].fontSize=11.5;styles['Heading2'].leading=15
    doc=SimpleDocTemplate(str(output),pagesize=pagesize,rightMargin=50,leftMargin=50,topMargin=54,bottomMargin=49,
        title=source.stem+' - P13 descriptive post-amendment',author='Author review pending')
    lines=source.read_text(encoding='utf8').splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        image=re.match(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            from PIL import Image as PILImage
            path=source.parent/image.group(2)
            with PILImage.open(path) as pic:w,h=pic.size
            story.append(Image(str(path),width=width,height=width*h/w))
            story.append(Paragraph(clean(image.group(1)),styles['Caption'] if 'Caption' in styles else styles['PaperBody']))
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[s.strip() for s in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',s) for s in cells):rows.append(cells)
                i+=1
            n=max(len(r) for r in rows)
            weights=[1.]*n
            if n>5:weights[0]=1.25;weights[1]=1.6
            widths=[width*w/sum(weights) for w in weights]
            data=[[Paragraph(clean(cell),styles['PaperCell']) for cell in row]+['']*(n-len(row)) for row in rows]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf2')),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#50677b')),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#cbd5df')),
                ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            story.extend([table,Spacer(1,10)]);continue
        if line.startswith('# '):story.append(Paragraph(clean(line[2:]),styles['Title']));i+=1;continue
        if line.startswith('## '):story.append(Paragraph(clean(line[3:]),styles['Heading1']));i+=1;continue
        if line.startswith('### '):story.append(Paragraph(clean(line[4:]),styles['Heading2']));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![')):
            paragraph.append(lines[i].strip());i+=1
        story.append(Paragraph(clean(' '.join(paragraph)),styles['PaperBody']))
    def footer(canvas,document):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526171'))
        canvas.drawString(50,25,'P13 - descriptive post-amendment; broad confirmation withheld')
        canvas.drawRightString(pagesize[0]-50,25,str(document.page));canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


if __name__=='__main__':
    folder=P/'manuscript'
    render(folder/'Manuscript.md',folder/'Manuscript.pdf')
    render(folder/'Supplement.md',folder/'Supplement.pdf',wide=True)
    print('Two saved manuscript PDFs created; no scientific execution.')
