def transformed(source):
    edits={
        '    rows=bundle[\'rows\'];sessions=':"    from reuse_dynamics import fit_or_reuse,ReuseIntegrityError\n    states={}\n    rows=bundle['rows'];sessions=",
        'theta,metrics=m.fit(train,validation,ridge,seed);row.update(metrics)':"theta,metrics=fit_or_reuse(m,session,region,family,size,y,train,validation,ridge,seed);row.update(metrics)\n                                    states['%s_%s_%s_%s_%s_%s'%(session['session_id'],region,family,size,ridge,seed)]=theta",
        "    save('comparison_rows.json',dict(rows=rows))":"    np.savez(output/'model_states.npz',**states)\n    save('comparison_rows.json',dict(rows=rows))",
        "    save('gate_result.json',gate)":"    gate['model_states_sha256']=hashlib.sha256((output/'model_states.npz').read_bytes()).hexdigest()\n    save('gate_result.json',gate)",
        "                                except Exception as exc:":"""                                except ReuseIntegrityError as exc:
                                    save('mandatory_reuse_failure.json',dict(failure=str(exc),identity=row))
                                    save('comparison_rows.json',dict(rows=rows))
                                    save('gate_result.json',dict(gate='FAIL',scientific_verdict='INCONCLUSIVE',failure='MANDATORY_REUSE_INTEGRITY_FAILURE',completed_competition_fit_count=len(rows),final_values_exposed_to_analysis=False,final_holdout_evaluated=False))
                                    sys.exit(2)
                                except Exception as exc:"""
    }
    for old,new in edits.items():
        if source.count(old)!=1:raise RuntimeError('FROZEN_COMPETITION_DRIVER_DRIFT')
        source=source.replace(old,new,1)
    return source
