import csv
import io
import study as r


def offsets():
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['phase','mouse','session','region','seed','ridge','converged','PG','iterations','calls','initial_FD_max','terminal_FD_max','optimizer_message'])
    for phase in ('diagnosis','smoke','small','full'):
        path=r.HERE/f'results/{phase}/native/summary.json'
        if not path.exists():continue
        for x in r.load(path)['rows']:
            writer.writerow([phase,x['mouse_id'],x['session_id'],x['region'],x['seed'],x['ridge'],x['converged'],x['projected_gradient'],x['iterations'],x['objective_calls'],max(x['initial_gradient_check']['max_relative_errors']),max(x['terminal_gradient_check']['max_relative_errors']),x['optimizer_message']])
    return stream.getvalue()


def models():
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['mouse','session','region','family','kind','size','ridge','seed','converged','PG','parameters','training_LL','development_LL','iterations','calls','error'])
    path=r.HERE/'results/M4/native/comparison_rows.json'
    if path.exists():
        for x in r.load(path)['rows']:
            writer.writerow([x.get(k) for k in ('mouse_id','session_id','region','family','kind','size','ridge','seed','converged','projected_gradient','parameter_count','training_LL_nats_per_unit_bin','validation_LL_nats_per_unit_bin','iterations','objective_calls','error_code')])
    return stream.getvalue()


def main():
    (r.HERE/'results/offset_diagnostics.csv').write_text(offsets(),encoding='utf-8',newline='')
    (r.HERE/'results/model_comparison.csv').write_text(models(),encoding='utf-8',newline='')
    phases={p:r.load(r.HERE/f'results/{p}/native/gate_result.json') for p in ('diagnosis','smoke','small','full','M4') if (r.HERE/f'results/{p}/native/gate_result.json').exists()}
    r.save(r.HERE/'results/result_summary.json',dict(gates=phases,M3_fits_reused=1638,M3_fits_repeated=0,source_requests=0,final_access=False,preferred_regime_claim=False))


if __name__=='__main__':main()
