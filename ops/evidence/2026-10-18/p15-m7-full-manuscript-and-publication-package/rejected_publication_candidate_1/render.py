"""Deterministic Markdown/table/math/figure PDF production,without scientific execution."""
import ast,hashlib,html,io,re
from pathlib import Path
import numpy as np
import matplotlib
from matplotlib import mathtext
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,LongTable,TableStyle,Image,KeepTogether,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from .source import P,R,E,ORDER,COHORTS,read,rows,write_rows,dump,sha,stats,fmt

WIDTH=A4[0]-112
FONT_DIR=Path(matplotlib.get_data_path())/'fonts/ttf'
for name,file in [('PaperSerif','DejaVuSerif.ttf'),('PaperBold','DejaVuSerif-Bold.ttf'),('PaperItalic','DejaVuSerif-Italic.ttf'),('PaperMono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/file)))
pdfmetrics.registerFontFamily('PaperSerif',normal='PaperSerif',bold='PaperBold',italic='PaperItalic',boldItalic='PaperBold')
STYLES={
    'p':ParagraphStyle('p',fontName='PaperSerif',fontSize=10.2,leading=14.7,spaceAfter=7,splitLongWords=True),
    'h1':ParagraphStyle('h1',fontName='PaperBold',fontSize=19,leading=25,spaceAfter=18,keepWithNext=True),
    'h2':ParagraphStyle('h2',fontName='PaperBold',fontSize=13.5,leading=18,spaceBefore=15,spaceAfter=8,keepWithNext=True),
    'h3':ParagraphStyle('h3',fontName='PaperBold',fontSize=11,leading=15,spaceBefore=11,spaceAfter=7,keepWithNext=True),
    'caption':ParagraphStyle('caption',fontName='PaperSerif',fontSize=8.5,leading=11.7,spaceBefore=5,spaceAfter=10),
    'reference':ParagraphStyle('reference',fontName='PaperSerif',fontSize=9,leading=12,spaceAfter=5,splitLongWords=True),
    'cell':ParagraphStyle('cell',fontName='PaperSerif',fontSize=7.4,leading=10,spaceAfter=0,splitLongWords=True),
    'headcell':ParagraphStyle('headcell',fontName='PaperBold',fontSize=7.4,leading=10,spaceAfter=0,splitLongWords=True),
}

def normal(text):
    return text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u2212','-').replace('\u2265','>=').replace('\u2264','<=')
def inline(text):
    text=html.escape(normal(text))
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="PaperMono">\1</font>',text)
    text=re.sub(r'\[([^\]]+)\]\((https?[^)]+)\)',r'<link href="\2" color="#35596a">\1</link>',text)
    return text
def mdtable(headers,data):
    def cell(v):
        if isinstance(v,bool):return 'True' if v else 'False'
        return str(v).replace('|','/').replace('\n','; ')
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join('---' for _ in headers)+'|']+['|'+'|'.join(cell(v) for v in row)+'|' for row in data])
def contrast_table(cohort):
    allrows=rows(P/'tables/REGISTERED_CONTRAST_ORDER.csv');data=[]
    for c in ORDER:
        r=next(r for r in allrows if r['cohort']==cohort and r['contrast']==c);ci=ast.literal_eval(r['CI95'])
        data.append([c,r['mean'],r['CI95'],r['raw_p'],r.get('Holm5_p') or 'not in family'])
    return mdtable(['Contrast','Mean gain','95% whole-mouse CI','Raw p','Holm5 p'],data)
def build_tables():
    final=rows(P/'tables/FINAL_FINAL_SOURCE_AND_C_QC.csv');unit=rows(P/'tables/FINAL_SELECTED_UNIT_QC.csv')
    tables={'FINAL_RESULTS':contrast_table('Final'),'DEVELOPMENT_RESULTS':contrast_table('Development')}
    tables['FINAL_QC_SUMMARY']=mdtable(['Mouse','C epochs','D metadata epochs','C-qualified','Admitted'],[[r['subject'],r['C_epochs'] or 'not read',r['D_metadata_epochs'] or 'not read',r['C_qualified_units'] or 'not read',r['C_admitted']] for r in final])
    tables['FINAL_UNITS']=mdtable(['Mouse/rank','Cluster ID','Selected UUID','C Hz','ISI fraction'],[[r['subject']+'/'+r['rank'],r['cluster_id'],r['UUID'],fmt(r['C_rate_Hz'],7),fmt(r['C_ISI_fraction'],4)] for r in unit])
    select=rows(P/'tables/DEVELOPMENT_B_SELECTION.csv')
    tables['B_SELECTION']=mdtable(['Configuration','B LL/unit-bin','Nominal q','Selected'],[[r['configuration'],fmt(r['equal_mouse_B_LL_unit_bin'],10) if r['equal_mouse_B_LL_unit_bin'] else 'unavailable',r['nominal_parameters'],r['selected']] for r in select])
    certs=rows(P/'tables/FINAL_NUMERICAL_CERTIFICATES.csv')
    tables['NUMERICAL_SUMMARY']=mdtable(['C fit group','Endpoints','Largest PG','Largest AD','Largest FD'],[[title,len(part),fmt(max(float(x['PG']) for x in part),7),fmt(max(float(x['AD']) for x in part),7),fmt(max(float(x['FD']) for x in part),7)] for title,part in [('Main',[r for r in certs if r['case']=='PRIMARY']),('Sensitivity',[r for r in certs if r['case']!='PRIMARY'])]])
    tables['ALL_FINAL_CERTIFICATES']=mdtable(['Mouse/case/configuration','Free q','PG','AD error','FD max','Iter'],[[r['subject']+'/'+r['case']+'/'+r['configuration'],r['free_parameters'],fmt(r['PG'],4),fmt(r['AD'],4),fmt(r['FD'],4),r['iterations']] for r in certs])
    animals=[];hetero=[];controls=[];coverage=[];anatomy=[]
    for cohort,folder in COHORTS.items():
        fn='E_MOUSE_EFFECTS.csv' if cohort=='Development' else 'FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv'
        for c in ORDER:
            for r in rows(R/folder/'tables'/fn):
                if r['contrast']==c:animals.append([cohort[:3],r['subject'],c,fmt(r['effect'],10),r['unit_bins']])
            d=stats(cohort)[c];eff=np.array([r['effect'] for r in d['mouse_effects']]);labci=d['lab_block_bootstrap_CI95']
            hetero.append([cohort[:3],c,f'{fmt(min(eff),6)} / {fmt(max(eff),6)}',fmt(d['median'],6),fmt(d['SD'],6),d['positive_mice'],fmt(d['equal_lab_mean'],6),f'[{fmt(labci[0],6)},{fmt(labci[1],6)}]'])
        prefix='E' if cohort=='Development' else 'D';summary=read(R/folder/f'results/{prefix}_CONTROL_SUMMARY.json')
        for c in ORDER:
            for n in ['N1','N2','N3','N4']:
                d=summary[c][n];missing='UNAVAILABLE' in d['status']
                controls.append([cohort[:3],c,n,d['n_mice'],'unavailable' if missing else str(d['mice_above_reference_median']), 'unavailable' if missing else ('wheel LL diagnostic' if n=='N3' else str(d['descriptive_disruption_gate'])),d['p_reference'],d['Holm4_reference_p']])
        for path in sorted((R/folder/f'results/{prefix}_controls').glob('*.json')):
            d=read(path)
            # Small per-mouse suite documents contain saved summaries,not neural arrays.
            if not isinstance(d,dict):continue
            mouse=d['subject'];assert set(d['suites'])=={'N1','N2','N3','N4'}
            for suite,state in d['suites'].items():
                cov=state['coverage']
                coverage.append({'cohort':cohort,'subject':mouse,'suite':suite,'status':state['status'],
                    'available':cov['available'],'epochs':cov['epochs'],'total_epochs':cov['total_epochs'],
                    'coverage':cov,'source':path.relative_to(R).as_posix()})
        for r in rows(R/folder/'tables/ANATOMY_LAYER_PROXY.csv'):
            anatomy.append([cohort[:3],r['subject'],r['case'],r['units'],r['superficial_units'],r['middle_units'],r['deep_units'],r['unspecified_units']])
        sens=rows(R/folder/'tables'/('E_SENSITIVITIES.csv' if cohort=='Development' else 'FINAL_SENSITIVITIES.csv'))
        tab=[]
        for case in [f'S{i:02}' for i in range(1,12)]:
            for c in ORDER[:3]:
                r=next(r for r in sens if r['case']==case and r['contrast']==c)
                n=r.get('n_mice',r.get('mice'));ci=ast.literal_eval(r['CI95']) if r['CI95'] and r['CI95']!='None' else None
                tab.append([case,c,n,fmt(r['mean'],8) if r['mean'] else 'unavailable',f'[{fmt(ci[0],8)},{fmt(ci[1],8)}]' if ci else 'unavailable',r.get('status','')])
        tables[cohort.upper()+'_SENSITIVITIES']=mdtable(['Case','Contrast','Mice','Mean','95% whole-mouse CI','Status'],tab)
    tables['ALL_MOUSE_EFFECTS']=mdtable(['Cohort','Mouse','Contrast','Effect','Scored unit-bins'],animals)
    tables['HETEROGENEITY']=mdtable(['Cohort','Contrast','Min / max','Median','SD','Positive','Equal-lab mean','Lab-block CI95'],hetero)
    tables['ALL_CONTROLS']=mdtable(['Cohort','Contrast','Suite','Mice','Above median','Descriptive gate','p_ref','Holm4'],controls)
    write_rows(P/'tables/REFERENCE_MOUSE_COVERAGE.csv',coverage)
    assert len(coverage)==64
    tables['REFERENCE_COVERAGE']=mdtable(['Cohort','Mouse','Suite','Eligible / total epochs','Available'],[[r['cohort'][:3],r['subject'],r['suite'],str(r['epochs'])+' / '+str(r['total_epochs']),r['available']] for r in coverage])
    tables['ANATOMY']=mdtable(['Cohort','Mouse','Population','Units','Superficial','Middle','Deep','Root/unknown'],anatomy)
    dump(P/'tables/PUBLICATION_TABLES.json',tables)
    return tables

def references():
    refs=read(P/'references/verified_references.json');text=[];bib=[]
    for r in refs:
        volume=(' '+r['volume']+':'+r['pages']) if r['volume'] else ''
        text.append(f"[{r['id']}] {r['authors']} ({r['year']}). {r['title']}. {r['journal']}{volume}. "+(f"https://doi.org/{r['doi']}" if r['doi'] else r['url']))
        fields={'author':'{'+r['authors']+'}','title':r['title'],'journal':r['journal'],'url':r['url']}
        if r['year']!='n.d.':fields['year']=r['year']
        for key in ['doi','volume','pages']:
            if r[key]:fields[key]=r[key]
        if r['id']>=10:fields['note']='Official documentation,accessed18October2026;access date is not a data version'
        bib.append('@'+('article' if r['id']<10 else 'misc')+'{'+r['key']+',\n'+',\n'.join('  '+k+' = {'+str(v)+'}' for k,v in fields.items())+'\n}')
    out='\n\n'.join(text);(P/'references/REFERENCES.md').write_text('# Verified bibliography\n\n'+out+'\n',encoding='utf8')
    (P/'references/references.bib').write_text('\n\n'.join(bib)+'\n',encoding='utf8')
    return out

def expand_sources():
    tables=build_tables();refs=references();cohort=rows(P/'tables/SOURCE_COHORT_IDENTITIES.csv')
    cards=[]
    for r in cohort:
        cards.append(f"**{r['subject']}** - {r['allocation']}; {r['lab']}; {r['date']}; session {r['session_number']}; {r['probe_name']}. Admitted: {r['admitted']}. "+('Exclusion: '+r['exclusion']+'.' if r['exclusion'] else 'No exclusion.')+f"\n\nSession eid: `{r['eid']}`\n\nProbe pid: `{r['pid']}`")
    for name in ['MAIN_MANUSCRIPT.md','SUPPLEMENT.md']:
        path=P/name;s=path.read_text(encoding='utf8');s=s.replace('{{REFERENCES}}',refs).replace('{{COHORT_CARDS}}','\n\n'.join(cards))
        for key,value in tables.items():s=s.replace('{{TABLE:'+key+'}}',value)
        # Keep the editable source's published statistics exact on every rebuild.
        # All replacements copy original saved strings,without rounded re-estimation.
        keys=iter(['FINAL_RESULTS'] if name=='MAIN_MANUSCRIPT.md' else ['DEVELOPMENT_RESULTS','FINAL_RESULTS'])
        pattern=r'\|Contrast\|Mean gain\|95% whole-mouse CI\|Raw p\|Holm5 p\|\n(?:\|[^\n]*\|\n?)+'
        s,n=re.subn(pattern,lambda match:tables[next(keys)]+'\n',s)
        assert n==(1 if name=='MAIN_MANUSCRIPT.md' else 2)
        if name=='SUPPLEMENT.md':
            pattern=r'\|Cohort\|Mouse\|Suite\|(?:Saved availability|Eligible / total epochs\|Available)\|\n(?:\|[^\n]*\|\n?)+'
            s,n=re.subn(pattern,lambda match:tables['REFERENCE_COVERAGE']+'\n',s);assert n==1
        assert '{{' not in s,'Unresolved publication include'
        path.write_text(s,encoding='utf8')

def table_flow(lines):
    parsed=[[s.strip() for s in line.strip().strip('|').split('|')] for line in lines]
    header=parsed[0];body=[r for r in parsed[1:] if not all(re.fullmatch('[: -]+',v) for v in r)]
    n=len(header)
    weights=[1]*n
    if header[0]=='Contrast':weights=[48,124,185,63,63]
    elif 'Selected UUID' in header:weights=[1.4,.7,3.8,.8,.8]
    elif header[0]=='Mouse/case/configuration':weights=[3.8,.65,1,1,1,.6]
    elif header[0]=='Configuration':weights=[2.3,1.35,.7,.7]
    elif header==['Columns','Raw definition']:weights=[.7,5]
    elif n==3:weights=[1,2.5,2.5]
    elif '95% whole-mouse CI' in header:weights=[.6,1,.45,1,2,1.8]
    elif n>=8:weights=[1.0]*n
    widths=[WIDTH*w/sum(weights) for w in weights]
    data=[[Paragraph(inline(v),STYLES['headcell'] if i==0 else STYLES['cell']) for v in row] for i,row in enumerate([header]+body)]
    table=LongTable(data,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edef')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#7b8e98')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d4dcdf')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7f8f9')]),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    return table

def math_flow(expression):
    folder=P/'work/equations';folder.mkdir(parents=True,exist_ok=True)
    target=folder/(hashlib.sha256(expression.encode()).hexdigest()+'.png')
    mathtext.math_to_image('$'+expression+'$',str(target),dpi=400,format='png',color='#24313b')
    with PILImage.open(target) as im:w,h=im.size
    width=min(WIDTH,w*.18);height=h*width/w
    return KeepTogether([Spacer(1,4),Image(str(target),width=width,height=height),Spacer(1,9)])

def pdf(name):
    source=P/(name+'.md');target=P/(name+'.pdf');lines=source.read_text(encoding='utf8').splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('$$'):
            expr=line[2:];i+=1
            while not expr.endswith('$$'):expr+=' '+lines[i].strip();i+=1
            story.append(math_flow(expr[:-2].strip()));continue
        image=re.fullmatch(r'!\[(.*)\]\(([^)]+)\)',line)
        if image:
            path=(P/image[2]).resolve();assert path.is_relative_to(P)
            with PILImage.open(path) as im:w,h=im.size
            scale=min(WIDTH/w,485/h);picture=Image(str(path),width=w*scale,height=h*scale)
            story.append(KeepTogether([Spacer(1,7),picture,Paragraph(inline(image[1]),STYLES['caption']),Spacer(1,7)]));i+=1;continue
        if line.startswith('|'):
            group=[]
            while i<len(lines) and lines[i].strip().startswith('|'):group.append(lines[i].strip());i+=1
            story.extend([table_flow(group),Spacer(1,10)]);continue
        if line.startswith('#'):
            depth=len(line)-len(line.lstrip('#'));style='h1' if depth==1 else ('h2' if depth==2 else 'h3')
            story.append(Paragraph(inline(line.lstrip('#').strip()),STYLES[style]));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','$$','![')):
            paragraph.append(lines[i].strip());i+=1
        style='reference' if re.match(r'^\[\d+\]',paragraph[0]) else 'p'
        story.append(Paragraph(inline(' '.join(paragraph)),STYLES[style]))
    title='P15 | Local spike-history prediction' if name=='MAIN_MANUSCRIPT' else 'P15 | Supplementary evidence'
    def page(canvas,doc):
        canvas.saveState();canvas.setFont('PaperSerif',8);canvas.setFillColor(colors.HexColor('#697780'))
        canvas.drawString(56,A4[1]-35,title)
        canvas.drawRightString(A4[0]-56,29,str(doc.page));canvas.drawString(56,29,'Development exploratory | Final DESCRIPTIVE ONLY')
        canvas.restoreState()
    document=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=56,leftMargin=56,topMargin=56,bottomMargin=49,
        title='Predictive Contributions of Local Spike History' if name=='MAIN_MANUSCRIPT' else 'Supplementary Methods and Results',author='Authors pending verification',invariant=1,pageCompression=1)
    document.build(story,onFirstPage=page,onLaterPages=page)

def render_documents():
    expand_sources()
    for name in ['MAIN_MANUSCRIPT','SUPPLEMENT']:pdf(name)
