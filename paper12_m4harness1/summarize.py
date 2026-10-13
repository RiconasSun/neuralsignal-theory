"""Saved public numerical errors and offset diagnostics only; no data or fits."""
import csv
import io
import study as r


def table():
    result=io.StringIO(newline='');writer=csv.writer(result,lineterminator='\n')
    writer.writerow(['test_identity','assertion_index','assertion','actual_error','threshold','decimal_places'])
    for i,row in enumerate(r.load(r.HERE/'results/numerical_gate.json')['assertions']):
        writer.writerow([row['test'],i,row['assertion'],row.get('actual',row.get('absolute_error')),
                         row.get('tolerance',row.get('delta')),row.get('places')])
    return result.getvalue()


def offset_table():
    result=io.StringIO(newline='');writer=csv.writer(result,lineterminator='\n')
    writer.writerow(['mouse_id','session_id','region','seed','ridge','converged','projected_gradient','iterations','objective_calls','optimizer_message','elapsed_seconds'])
    for path in sorted((r.HERE/'results/M4/native').glob('*_offset.json')):
        x=r.load(path)
        for row in x['seeds']:
            writer.writerow([x['mouse_id'],x['session_id'],x['region']]+[row[k] for k in
                ('seed','ridge','converged','projected_gradient','iterations','objective_calls','optimizer_message','elapsed_seconds')])
    return result.getvalue()


def main():
    (r.HERE/'results/numerical_error_table.csv').write_text(table(),encoding='utf-8',newline='')
    (r.HERE/'results/offset_diagnostics.csv').write_text(offset_table(),encoding='utf-8',newline='')
    native=r.HERE/'results/M4/native/gate_result.json'
    r.save(r.HERE/'results/result_summary.json',dict(numerical_gate=r.load(r.HERE/'results/numerical_gate.json'),
        M4=r.load(native) if native.exists() else dict(gate='NOT_EXECUTED'),
        M3_fits_reused=1638,M3_fits_repeated=0,source_requests=0,final_evaluation=False,
        original_failures_reclassified=False))


if __name__=='__main__':main()
