"""Document regressions; no scientific worker or neural-data execution."""
import csv,io,re,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from .source import P,R,ORDER,read,rows,write_rows,NoWorkers,lock_process

class DocumentRegressions(unittest.TestCase):
    def test_union_schema_preserves_development_and_final_columns(self):
        with tempfile.TemporaryDirectory(dir=P/'work') as d:
            p=Path(d)/'mixed.csv';write_rows(p,[{'contrast':'x','mice':10},{'contrast':'y','n_mice':6,'verdict':'DESCRIPTIVE ONLY'}])
            r=rows(p);self.assertEqual(r[0]['mice'],'10');self.assertEqual(r[1]['n_mice'],'6');self.assertEqual(r[1]['verdict'],'DESCRIPTIVE ONLY')

    def test_exact_registered_order_and_full_saved_strings(self):
        r=rows(P/'tables/REGISTERED_CONTRAST_ORDER.csv')
        for cohort in ['Development','Final']:
            self.assertEqual([x['contrast'] for x in r if x['cohort']==cohort],ORDER)
        p=next(x for x in r if x['cohort']=='Final' and x['contrast']=='B4-B1')
        self.assertEqual(p['mean'],'0.08658239652342035');self.assertEqual(p['raw_p'],'0.015625')
        self.assertEqual(len(rows(P/'tables/DEVELOPMENT_B_SELECTION.csv')),37)
        supplement=(P/'SUPPLEMENT.md').read_text(encoding='utf8')
        self.assertIn('37 seed-grouped candidates representing61 optimizer starts per mouse',supplement)
        self.assertNotIn('complete61candidate',supplement)

    def test_each_mouse_has_four_actual_coverage_panels(self):
        r=rows(P/'tables/REFERENCE_MOUSE_COVERAGE.csv');self.assertEqual(len(r),64)
        ids={(x['cohort'],x['subject']) for x in r};self.assertEqual(len(ids),16)
        for c,m in ids:self.assertEqual({x['suite'] for x in r if x['cohort']==c and x['subject']==m},{'N1','N2','N3','N4'})
        final=[x for x in r if x['cohort']=='Final' and x['suite']=='N4'];self.assertEqual(sum(x['available']=='True' for x in final),3)

    def test_no_legacy_scientific_imports(self):
        for name in ['paper15_m0.acquire','paper15_m1.synthetic','paper15_dev.training','paper15_r1.training','paper15_final1.d_batch']:
            with self.assertRaises(PermissionError):NoWorkers().find_spec(name)

    def test_array_and_network_denial_before_io(self):
        lock_process()
        with self.assertRaises(PermissionError):np.load('this-file-is-never-opened.npy')
        with self.assertRaises(PermissionError):socket.create_connection(('127.0.0.1',1))

    def test_utf8_publication_and_no_private_paths(self):
        for name in ['MAIN_MANUSCRIPT.md','SUPPLEMENT.md']:
            s=(P/name).read_text(encoding='utf8')
            for bad in ['\u00e2\u02c6','\u00c2\u00b1','\ufffd'] :self.assertNotIn(bad,s)
            self.assertIsNone(re.search(r'[A-Za-z]:\\|/Users/|\\Users\\|\.codex',s));self.assertNotIn('{{',s)

    def test_transpose_math_is_renderable(self):
        from matplotlib.mathtext import MathTextParser
        MathTextParser('path').parse(r'$R^{\mathsf{T}}z$')

    def test_changed_pdf_cannot_reuse_stale_raster_directory(self):
        from .qa import raster_directory
        with tempfile.TemporaryDirectory(dir=P/'work') as d:
            p=Path(d)/'fixture.pdf';p.write_bytes(b'first document')
            before=raster_directory('SYNTHETIC',p);p.write_bytes(b'changed page count')
            self.assertNotEqual(before,raster_directory('SYNTHETIC',p))

    def test_dense_figure_footers_do_not_overlap_axes(self):
        from . import production as p
        import matplotlib.pyplot as plt
        for fn in [p.figure5,p.figure6]:
            captured=[]
            with patch.object(p,'export',side_effect=lambda fig,name:captured.append(fig)):fn()
            fig=captured[0];fig.canvas.draw();renderer=fig.canvas.get_renderer();footer=fig.texts[-1].get_window_extent(renderer)
            for ax in fig.axes:
                labels=[ax.xaxis.label,*ax.get_xticklabels()]
                for label in labels:
                    if label.get_text():self.assertFalse(footer.overlaps(label.get_window_extent(renderer)),fn.__name__)
            plt.close(fig)

    def test_primary_summary_label_is_outside_data_region(self):
        from . import production as p
        import matplotlib.pyplot as plt
        captured=[]
        with patch.object(p,'export',side_effect=lambda fig,name:captured.append(fig)):p.figure2()
        fig=captured[0];fig.canvas.draw();renderer=fig.canvas.get_renderer()
        self.assertEqual(sum(len(ax.collections[0].get_offsets()) for ax in fig.axes),16)
        for ax,cohort in zip(fig.axes,['Development','Final']):
            from .source import stats
            saved=stats(cohort)['B4-B1'];lo,hi=ax.get_xlim()
            offsets=ax.collections[0].get_offsets()
            self.assertEqual(sorted(float(v) for v in offsets[:,0]),sorted(r['effect'] for r in saved['mouse_effects']))
            self.assertTrue(all(lo<float(v)<hi for v in [*offsets[:,0],saved['equal_mouse_mean'],*saved['CI95']]))
            for x,y in offsets:
                px,py=ax.transData.transform((float(x),float(y)))
                self.assertGreater(px,ax.bbox.x0+4);self.assertLess(px,ax.bbox.x1-4)
                self.assertGreater(py,ax.bbox.y0+4);self.assertLess(py,ax.bbox.y1-4)
            labels=[t for t in ax.get_yticklabels() if t.get_text()=='Mean /95% CI']
            self.assertEqual(len(labels),1);self.assertLess(labels[0].get_window_extent(renderer).x1,ax.bbox.x0)
            self.assertFalse(ax.texts)
        plt.close(fig)

if __name__=='__main__':lock_process();unittest.main()
