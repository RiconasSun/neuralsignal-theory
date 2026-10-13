"""Training-only original/replay comparison; validation fields never exported or used."""
import study as r


def main():
    original=[];replayed=[];comparisons=[]
    for path in sorted((r.PREVIOUS/'results/M3/progressive1').glob('*.json')):
        record=r.load(path)
        if record.get('family')!='baseline' or record.get('kind')=='stationary':continue
        keys=('mouse_id','session_id','region','kind','ridge','seed','optimizer_success','optimizer_message',
              'iterations','objective_calls','projected_gradient','bound_hits','penalized_training_objective',
              'training_LL_nats_per_unit_bin')
        old={k:record[k] for k in keys};old['original_receipt_sha256']=r.sha(path);original.append(old)
        name=f"{old['region']}_{old['kind']}_{old['ridge']}_{old['seed']}.json"
        new=r.load(r.HERE/'results/diagnosis'/name);replayed.append(new)
        history=new['accepted_iteration_history']
        relative=abs(history[-1]['loss']-history[-2]['loss'])/max(1.,abs(history[-1]['loss']),abs(history[-2]['loss'])) if len(history)>1 else None
        comparisons.append(dict(region=old['region'],kind=old['kind'],ridge=old['ridge'],seed=old['seed'],
            iterations_match=old['iterations']==new['iterations'],message_match=old['optimizer_message']==new['optimizer_message'],
            training_objective_difference=new['penalized_training_objective']-old['penalized_training_objective'],
            projected_gradient_difference=new['projected_gradient']-old['projected_gradient'],
            last_relative_objective_change=relative))
    if len(original)!=120 or len(replayed)!=120:raise RuntimeError('ORIGINAL_FAILURE_DENOMINATOR')
    r.save(r.HERE/'results/original_training_diagnostics.json',dict(rows=original,fit_count=120,
        original_trajectories_recorded=False,validation_fields_excluded=True),True)
    r.save(r.HERE/'results/diagnosis_audit.json',dict(comparisons=comparisons,
        all_iterations_match=all(x['iterations_match'] for x in comparisons),
        all_messages_match=all(x['message_match'] for x in comparisons),
        maximum_objective_difference=max(abs(x['training_objective_difference']) for x in comparisons),
        maximum_projected_gradient_difference=max(abs(x['projected_gradient_difference']) for x in comparisons),
        minimum_replay_pg=min(x['projected_gradient'] for x in replayed),
        maximum_replay_pg=max(x['projected_gradient'] for x in replayed),
        maximum_fd_error=max(max(x[k]['max_relative_errors']) for x in replayed for k in ('initial_gradient_check','terminal_gradient_check')),
        maximum_sampled_condition_number=max(c['condition_number'] for x in replayed for c in x['conditioning']),
        total_bound_hits=sum(x['bound_hits'] for x in replayed),
        original_failures_preserved=True,validation_driven_decisions=False),True)
    print('ALL120_TRAINING_DIAGNOSTICS_AUDITED; VALIDATION_NOT_USED')


if __name__=='__main__':main()
