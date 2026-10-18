"""One command: saved-result arithmetic,tables,figures and manuscript PDFs only."""
import datetime,importlib.metadata,json,sys,unittest
from .source import P,E,R,read,dump,sha,verify_sources,lock_process

def run():
    lock_process()
    def candidate_check():
        if (P/'CANDIDATE.json').exists():
            for name,h in read(P/'CANDIDATE.json')['hashes'].items():assert sha(P/name)==h,name
    candidate_check()
    for line in (P/'requirements.txt').read_text(encoding='utf8').splitlines():
        name,version=line.split('==');assert importlib.metadata.version(name)==version,name
    count=verify_sources()
    from .production import collect,existing_arithmetic,render_figures
    from .render import render_documents
    from .qa import check
    print('Verified immutable saved source identities',count,flush=True)
    collect();existing_arithmetic();print('Copied saved tables and reproduced original mouse arithmetic',flush=True)
    render_figures();print('Seven figures exported to PNG/SVG/PDF',flush=True)
    render_documents();print('Main manuscript and supplement PDF produced',flush=True)
    qa=check();assert verify_sources()==count
    suite=unittest.defaultTestLoader.loadTestsFromName('paper15_manuscript.test_documents')
    result=unittest.TextTestRunner(verbosity=1).run(suite);assert result.wasSuccessful()
    receipt=dict(mission='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',saved_only=True,source_hashes_verified=count,
        original_result_numbers_unchanged=True,neural_arrays_loaded=0,old_scientific_modules_imported=0,new_real_fits=0,
        new_prediction_or_likelihood_calls=0,new_hypothesis_tests=0,Final_D_rerun_count=0,figures=7,figure_formats=['PNG450dpi','SVG','PDF'],
        PDF_pages={k:v['pages'] for k,v in qa.items()},PDF_hashes={k:v['pdf_sha256'] for k,v in qa.items()},
        process_network_denied=True,process_numpy_array_loading_denied=True,document_regressions=result.testsRun,scope='Original saved arithmetic and document production,not raw-data fit reproduction')
    dump(P/'SAVED_REPRODUCTION.json',receipt)
    assert not any(n.startswith(('paper15_m0','paper15_m1','paper15_dev','paper15_r1','paper15_final1')) for n in sys.modules)
    candidate_check()
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':run()
