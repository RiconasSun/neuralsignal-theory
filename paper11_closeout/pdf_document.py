"""Paginated academic PDFs from generated saved-evidence Markdown and figures."""
import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               Image, KeepTogether)
from reportlab import rl_config
rl_config.invariant = 1

HERE = Path(__file__).resolve().parent


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<link href="\2" color="#267C9A">\1</link>', text)
    return text


def render(source, target):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PaperTitle', fontName='Times-Bold', fontSize=20, leading=24, spaceAfter=14))
    styles.add(ParagraphStyle(name='PaperBody', fontName='Times-Roman', fontSize=10.5, leading=14, spaceAfter=8,
                              alignment=TA_LEFT, splitLongWords=1))
    styles.add(ParagraphStyle(name='PaperHeading', fontName='Times-Bold', fontSize=13, leading=16, spaceBefore=12,
                              spaceAfter=7, keepWithNext=True))
    styles.add(ParagraphStyle(name='PaperSubheading', fontName='Times-Bold', fontSize=11, leading=14,
                              spaceBefore=8, spaceAfter=5, keepWithNext=True))
    styles.add(ParagraphStyle(name='PaperCaption', fontName='Times-Roman', fontSize=9, leading=12, spaceAfter=12))
    styles.add(ParagraphStyle(name='TableCell', fontName='Times-Roman', fontSize=8, leading=10, splitLongWords=1))
    styles.add(ParagraphStyle(name='TableHead', fontName='Times-Bold', fontSize=8, leading=10, splitLongWords=1))
    width=6.8*inch
    doc=SimpleDocTemplate(str(target), pagesize=(8.5*inch,11*inch), leftMargin=.85*inch,rightMargin=.85*inch,
                          topMargin=.65*inch,bottomMargin=.65*inch, title=source.stem+' | P11 exploratory benchmark',
                          author='NEURALSIGNAL INSTITUTE', pageCompression=1)
    lines=source.read_text(encoding='utf-8').splitlines(); story=[]; i=0; eq=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1; continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),styles['PaperTitle'])); i+=1; continue
        if line.startswith('## '):
            story.append(Paragraph(inline(line[3:]),styles['PaperHeading'])); i+=1; continue
        if line.startswith('### '):
            story.append(Paragraph(inline(line[4:]),styles['PaperSubheading'])); i+=1; continue
        if line.startswith('$$'):
            eq+=1; path=source.parent/'equations'/f'eq{eq}.png'
            image=Image(str(path)); scale=min(width/image.imageWidth, .6*inch/image.imageHeight)
            image.drawWidth=image.imageWidth*scale; image.drawHeight=image.imageHeight*scale
            image.hAlign='LEFT'; story.extend([image,Spacer(1,8)]); i+=1; continue
        if line.startswith('!['):
            path=source.parent/re.search(r'\]\((.*?)\)',line)[1]
            image=Image(str(path)); scale=min(width/image.imageWidth,3.7*inch/image.imageHeight)
            image.drawWidth=image.imageWidth*scale; image.drawHeight=image.imageHeight*scale
            image.hAlign='CENTER'; i+=1
            while i<len(lines) and not lines[i].strip(): i+=1
            group=[Spacer(1,7),image,Spacer(1,6)]
            if i<len(lines) and lines[i].startswith('Figure '):
                group.append(Paragraph(inline(lines[i]),styles['PaperCaption'])); i+=1
            story.append(KeepTogether(group)); continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',c) for c in cells): rows.append(cells)
                i+=1
            lengths=[min(35,max(len(str(row[col])) for row in rows)) for col in range(len(rows[0]))]
            weights=[max(9,n) for n in lengths]
            widths=[width*n/sum(weights) for n in weights]
            parsed=[[Paragraph(inline(c),styles['TableHead' if n==0 else 'TableCell']) for c in row] for n,row in enumerate(rows)]
            tab=Table(parsed,colWidths=widths,repeatRows=1,hAlign='LEFT')
            tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEF2F3')),
                 ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#8B9A9E')),
                 ('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#D7DFE0')),
                 ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
                 ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            if len(rows)<=12:
                headings=[]
                while story and isinstance(story[-1],Paragraph) and getattr(story[-1].style,'keepWithNext',False):
                    headings.insert(0,story.pop())
                for heading in headings: heading.keepWithNext=0
                story.append(KeepTogether(headings+[tab]))
            else:
                story.append(tab)
            story.append(Spacer(1,8)); continue
        paragraph=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![','$$')):
            paragraph.append(lines[i].strip()); i+=1
        style=styles['PaperCaption'] if line.startswith(('Table ','Figure ')) else styles['PaperBody']
        story.append(Paragraph(inline(' '.join(paragraph)),style))

    def page(canvas, document):
        canvas.saveState();canvas.setFont('Times-Roman',8);canvas.setFillColor(colors.HexColor('#53676E'))
        canvas.drawString(.85*inch,.35*inch,'Exploratory benchmark | Independent validation not executed')
        canvas.drawRightString(7.65*inch,.35*inch,str(document.page));canvas.restoreState()
    doc.build(story,onFirstPage=page,onLaterPages=page)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(HERE/'output'))
    folder=Path(parser.parse_args().output).resolve()
    if HERE not in folder.parents:raise ValueError('Output outside closeout')
    for name in ('manuscript','supplement'):
        render(folder/(name+'.md'),folder/(name+'.pdf'))
    print('Two paginated academic PDFs generated.')
