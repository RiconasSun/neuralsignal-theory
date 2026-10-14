import csv
import io

COLUMNS=['mouse_id','session_id','region','family','size','ridge','seed','converged','optimizer_message','iterations','objective_calls','projected_gradient','gradient_inf','bound_hits','parameter_count','elapsed_seconds']

def render(rows):
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=COLUMNS,extrasaction='ignore');w.writeheader();w.writerows(rows);return f.getvalue().encode('utf-8')
