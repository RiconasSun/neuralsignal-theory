"""Only offset-state reuse and proven convergence-impossibility stop are new."""

def transformed(source):
    edits={
      '    from task_offset import fit_offset\n':'    from frozen_offset import fit_offset\n    from impossibility import early_failure\n',
      "                ot,ov,xt,xv,diagnostics=fit_offset(y,valid,saved['conditions_A'],saved['conditions_B'],saved['orders_A'],saved['orders_B'])\n":"                ot,ov,xt,xv,diagnostics=fit_offset(session['session_id'],region,session['sha256'],y,valid,saved['conditions_A'],saved['conditions_B'],saved['orders_A'],saved['orders_B'])\n",
      "        if critical:break\n    expected=len(sessions)*2*57*3\n":"        if critical:break\n        known=[s for s in sessions if any(r['family']!='baseline' and r['session_id']==s for r in rows)]\n        critical,possible=early_failure(rows,known)\n        save('prefix_'+session['session_id']+'.json',dict(known_sessions=known,possible_configuration_counts=possible,validation_scores_used_for_stop=False))\n        if critical:break\n    expected=len(sessions)*2*57*3\n"
    }
    for old,new in edits.items():
        if source.count(old)!=1:raise RuntimeError('FROZEN_MODEL_DRIVER_SOURCE_DRIFT')
        source=source.replace(old,new,1)
    return source
