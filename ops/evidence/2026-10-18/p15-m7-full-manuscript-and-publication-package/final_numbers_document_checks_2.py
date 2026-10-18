"""Independent JSON/CSV/PDF/SVG document consistency, never scientific execution."""
from pathlib import Path
import ast,csv,hashlib,json,re,xml.etree.ElementTree as ET
from pypdf import PdfReader
import pdfplumber
R=Path(__file__).resolve().parents[4];P=R/'paper15_manuscript';E=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def mdrows(text):return [[v.strip() for v in line.strip().strip('|').split('|')] for line in text.splitlines() if line.startswith('|')]
candidate=read(P/'CANDIDATE.json');assert sha(P/'CANDIDATE.json')=='c98ee27cd207a556ac087fb220f05b81392ae2dbe01f4629d0c5682eb3bc94f7'
for rel,h in candidate['hashes'].items():assert sha(P/rel)==h,rel
lock=read(P/'SOURCE_HASHES.json');assert len(lock['hashes'])==3099
for rel,h in lock['hashes'].items():
    assert 'work' not in Path(rel).parts and Path(rel).suffix.lower() not in {'.npz','.npy','.nwb','.h5'} and sha(R/rel)==h,rel
oracle=read(E/'RESULTS_CONSISTENCY_ORACLE.json');assert oracle['registered_contrast_order']==['B4-B1','B4-B3','B4-B2','D-B4','C-B4','D-S']
baseline=read(E/'baseline.json');assert len(baseline['requirements'])==326 and baseline['source_sha256']==sha(E/'OWNER_REQUEST.txt')
mapping=read(P/'tables/SAVED_TABLE_SOURCE_MAP.json')
for rel,item in mapping.items():assert sha(P/rel)==item['sha256']==sha(R/item['source'])
pub=rows(P/'tables/REGISTERED_CONTRAST_ORDER.csv');assert len(pub)==12
maintext=(P/'MAIN_MANUSCRIPT.md').read_text();supp=(P/'SUPPLEMENT.md').read_text();sm=mdrows(supp)
animal_count=0;sens_count=0;controls_count=0
for cohort,prefix,old in [('Development','DEVELOPMENT','paper15_r1'),('Final','FINAL','paper15_final1')]:
    source=oracle['cohorts'][cohort]
    assert [r['contrast'] for r in pub if r['cohort']==cohort]==oracle['registered_contrast_order']
    for r in [x for x in pub if x['cohort']==cohort]:
        q=source['main'][r['contrast']]
        assert float(r['mean'])==q['equal_mouse_mean'] and ast.literal_eval(r['CI95'])==q['CI95'] and float(r['raw_p'])==q['paired_sign_flip_p'] and (float(r['Holm5_p']) if r['Holm5_p'] else None)==q.get('Holm5_adjusted_p')
        assert any(v[:5]==[r['contrast'],r['mean'],r['CI95'],r['raw_p'],r['Holm5_p'] or 'not in family'] for v in sm)
    animal=rows(P/'tables'/('DEVELOPMENT_E_MOUSE_EFFECTS.csv' if cohort=='Development' else 'FINAL_FINAL_INDIVIDUAL_MOUSE_EFFECTS.csv'))
    for r in animal:
        oldrow=next(x for x in source['main'][r['contrast']]['mouse_effects'] if x['subject']==r['subject'])
        assert float(r['effect'])==oldrow['effect'] and int(r['unit_bins'])==oldrow['unit_bins'] and float(r['left_LL'])==oldrow['left_LL'] and float(r['right_LL'])==oldrow['right_LL'];animal_count+=1
        assert any(v==[cohort[:3],r['subject'],r['contrast'],format(float(r['effect']),'.10g'),r['unit_bins']] for v in sm)
    sens=rows(P/'tables'/('DEVELOPMENT_E_SENSITIVITIES.csv' if cohort=='Development' else 'FINAL_FINAL_SENSITIVITIES.csv'));assert len(sens)==33
    for r in sens:
        q=source['sensitivities'][r['case']][r['contrast']];assert float(r['mean'])==q['equal_mouse_mean'] and ast.literal_eval(r['CI95'])==q['CI95'] and int(r.get('mice',r.get('n_mice')))==q['n_mice'] and r['status']==q['status'];sens_count+=1
        ci='['+','.join(format(float(v),'.8g') for v in q['CI95'])+']'
        assert any(v==[r['case'],r['contrast'],str(q['n_mice']),format(q['equal_mouse_mean'],'.8g'),ci,q['status']] for v in sm)
    ctl=rows(P/'tables'/('DEVELOPMENT_E_CONTROLS.csv' if cohort=='Development' else 'FINAL_FINAL_CONTROLS.csv'));assert len(ctl)==24
    for r in ctl:
        q=source['controls'][r['contrast']][r['suite']];assert int(r.get('mice',r.get('n_mice')))==q['n_mice'] and float(r['p_reference'])==q['p_reference'];controls_count+=1
coverage=rows(P/'tables/REFERENCE_MOUSE_COVERAGE.csv');assert len(coverage)==64
for r in coverage:
    original=read(R/r['source'])['suites'][r['suite']];assert ast.literal_eval(r['coverage'])==original['coverage'] and ast.literal_eval(r['available'])==original['coverage']['available'] and r['status']==original['status']
num=rows(P/'tables/FINAL_NUMERICAL_CERTIFICATES.csv');assert len(num)==392
for r in num:
    p=R/'paper15_final1'/r['certificate'];q=read(p)
    assert sha(p)==r['sha256'] and r['status']==q['status']=='NUMERICAL_PASS' and int(r['stored_vector_length'])==len(q['coefficients'])==int(r['free_parameters'])==q['free_parameters']
    assert float(r['PG'])==q['PG'] and float(r['AD'])==q['independent']['AD_max_scaled'] and int(r['iterations'])==q['iterations']
units=rows(P/'tables/FINAL_SELECTED_UNIT_QC.csv');assert len(units)==48
for r in units:
    q=read(R/f"paper15_final1/results/{r['subject']}_C_QC.json");u=next(x for x in q['physiology'] if x['uuid']==r['UUID'])
    assert q['selected_unit_uuids'][int(r['rank'])-1]==r['UUID'] and float(r['C_rate_Hz'])==u['C_rate_Hz'] and float(r['C_ISI_fraction'])==u['C_refractory_fraction'] and ast.literal_eval(r['quartile_rates_Hz'])==u['original_C_quartile_rates']
cohort=rows(P/'tables/SOURCE_COHORT_IDENTITIES.csv');assert len(cohort)==20 and sum(r['admitted']=='False' for r in cohort)==4
selection_rows=rows(P/'tables/DEVELOPMENT_B_SELECTION.csv');assert len(selection_rows)==37
selection_denominator_defect='complete61candidate B-selection table' in supp
assert not selection_denominator_defect and '37 seed-grouped candidates representing61 optimizer starts per mouse' in supp
# Exact SVG clip proof, without importing/executing a renderer.
svg=ET.parse(P/'figures/Figure_2_Primary_mouse_effects.svg').getroot();ns={'s':'http://www.w3.org/2000/svg'}
clip={x.attrib['id']:x.find('s:rect',ns).attrib for x in svg.findall('.//s:clipPath',ns)};point_results=[]
for group in svg.findall('.//s:g',ns):
    if not group.attrib.get('id','').startswith('PathCollection_'):continue
    for sub in group.findall('.//s:g',ns):
        if 'clip-path' not in sub.attrib:continue
        box=clip[sub.attrib['clip-path'][5:-1]];x0=float(box['x']);y0=float(box['y']);x1=x0+float(box['width']);y1=y0+float(box['height'])
        for marker in sub.findall('s:use',ns):
            x=float(marker.attrib['x']);y=float(marker.attrib['y']);point_results.append(dict(group=group.attrib['id'],x=x,y=y,inside_clip=x0<=x<=x1 and y0<=y<=y1))
assert len(point_results)==16 and sum(not p['inside_clip'] for p in point_results)==0
fig3_ci=[v for cohort in oracle['cohorts'].values() for q in cohort['main'].values() for v in q['CI95']];assert all(-.042<=v<=.18 for v in fig3_ci)
ownother=[r['effect'] for c in oracle['cohorts'].values() for key in ['B4-B3','B4-B2'] for r in c['main'][key]['mouse_effects']];assert len(ownother)==32
pdfs={}
for name,n in [('MAIN_MANUSCRIPT',19),('SUPPLEMENT',36)]:
    path=P/(name+'.pdf');pages=PdfReader(path).pages;texts=[page.extract_text() for page in pages];assert len(pages)==n and all(texts)
    full='\n'.join(texts);assert not re.search(r'[A-Za-z]:\\|/Users/|\\Users\\|\.codex',full) and not any(c in full for c in ['\ufffd','\u25a0','\x00'])
    for r in pub:
        if name=='SUPPLEMENT' or r['cohort']=='Final':assert r['mean'] in full
    assert 'DESCRIPTIVE ONLY' in full and '0.15625' in full and 'NYU-21' in full and 'UCLA033' in full
    with pdfplumber.open(path) as doc:
        for j,page in enumerate(doc.pages,1):
            foot=page.crop((page.width-85,page.height-43,page.width-30,page.height-12)).extract_text();assert foot.strip()==str(j)
            assert not [c for c in page.chars if c['x0']<29 or c['x1']>page.width-29 or c['top']<15 or c['bottom']>page.height-14]
    pdfs[name]=dict(sha256=sha(path),pages=n,no_private_paths_or_missing_text_glyphs=True,page_numbers_and_text_bounds=True)
native=read(E/'NATIVE_DOCUMENT_REPRODUCTION_RECEIPT_4.json');assert native['candidate_sha256']==sha(P/'CANDIDATE.json') and native['exit_code']==0 and native['result']['document_regressions']==10 and sha(R/native['log_path'])==native['log_sha256']
for v in read(E/'VISUAL_REVIEW.json')['gallery']:assert sha(R/v['path'])==v['sha256']
out=dict(candidate_sha256=sha(P/'CANDIDATE.json'),baseline_sha256=sha(E/'baseline.json'),owner_contract_items_read=326,candidate_files=len(candidate['hashes']),source_hashes_verified=3099,original_csv_copies_exact=len(mapping),main_rows=12,animal_rows=animal_count,sensitivity_rows=sens_count,controls_rows=controls_count,coverage_rows=64,unit_QC_rows=48,numerical_certificate_rows=392,selection_group_rows=37,selection_starts_per_mouse=61,selection_denominator_defect=selection_denominator_defect,Figure2_saved_scatter_markers=point_results,Figure2_clipped_actual_marker_count=0,Figure3_all12CI_bounds_covered=True,Figure4_autoY_saved_values=32,PDFs=pdfs,source_arrays_read=0,scientific_modules_executed=0,new_fits_predictions_likelihood_ADFD=0,new_hypothesis_tests=0,Final_D_reruns=0)
with (E/'FINAL_NUMBERS_DOCUMENT_CHECKS_2.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in out.items() if k!='Figure2_saved_scatter_markers'},indent=2))
