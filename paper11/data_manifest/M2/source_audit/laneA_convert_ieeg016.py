#!/usr/bin/env python3
"""IEEG016 (Boran et al. GIN NIX release, doi:10.12751/g-node.d76994) -> BIDS-derivative dataset holding ONLY
the single-unit content (spike times, mean/std waveforms, unit metadata) plus per-trial task tables, keyed to the
subject/session labels of OpenNeuro ds004752 (sciAdv_identifier crosswalk). The scalp-EEG / iEEG time series
are NOT exported (they are already published as ds004752 / NEMAR on004752).

Usage: laneA_convert_ieeg016.py <nix_dir> <ds004752_meta_dir> <out_dir> <report_dir>
  ds004752_meta_dir: flat dir of ds004752 v1.0.1 files named like sub-01__ses-01__ieeg__<file>
Values are copied as stored in the NIX files (no rescaling, no re-sorting of spikes, no re-referencing)."""
import collections, csv, hashlib, json, os, re, sys
from concurrent.futures import ProcessPoolExecutor
import h5py, numpy as np

NIX, DSMETA, OUT, REP = sys.argv[1:5]
TASK = 'verbalWM'


def s(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    return v


def prop(sec, name):
    """NIX property value (first value) from a metadata section group."""
    ds = sec['properties'][name]
    v = ds[()]
    v = v[0]['value'] if v.dtype.names else v[0]
    v = s(v)
    if isinstance(v, (np.floating,)):
        v = float(v)
    if isinstance(v, (np.bool_,)):
        v = bool(v)
    return v


def fmt(v):
    if v is None:
        return 'n/a'
    if isinstance(v, float):
        if np.isnan(v):
            return 'n/a'
        return repr(v) if v != int(v) else str(int(v))
    return str(v)


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def source_names(f, grp):
    """Return list of (name, [child names]) for a NIX entity's sources."""
    out = []
    if 'sources' not in grp:
        return out
    for k in grp['sources']:
        g = grp['sources'][k]
        kids = [s(g['sources'][c].attrs.get('name', c)) for c in g['sources']] if 'sources' in g else []
        out.append((s(g.attrs.get('name', k)), kids))
    return out


def one(path):
    base = os.path.basename(path)[:-3]
    m = re.match(r'Data_Subject_(\d+)_Session_(\d+)$', base)
    subj, sess = int(m.group(1)), int(m.group(2))
    strings = collections.Counter()
    with h5py.File(path, 'r') as f:
        # ---- privacy: every string attribute and string dataset value in the file
        def visit(name, obj):
            strings[name.split('/')[-1][:200]] += 0  # keep key namespace small
            for k, v in obj.attrs.items():
                v = s(v)
                if isinstance(v, str) and k not in ('entity_id',):
                    strings[f'attr:{k}={v[:300]}'] += 1
            if isinstance(obj, h5py.Dataset) and obj.size <= 200000:
                if obj.dtype.kind in 'OS' or (obj.dtype.names and any(obj.dtype[n].kind in 'OS' for n in obj.dtype.names)):
                    vals = obj[()]
                    for x in np.atleast_1d(vals).ravel():
                        if isinstance(x, np.void) or (hasattr(x, 'dtype') and x.dtype.names):
                            for n in x.dtype.names:
                                y = s(x[n])
                                if isinstance(y, str) and y:
                                    strings[f'val:{y[:300]}'] += 1
                        else:
                            y = s(x)
                            if isinstance(y, str) and y:
                                strings[f'val:{y[:300]}'] += 1
        f.visititems(visit)
        strings = collections.Counter({k: v for k, v in strings.items() if v})

        md = f['metadata']
        subj_meta = {k: prop(md['Subject'], k) for k in md['Subject']['properties']}
        gen = md['General']
        general = {k: prop(gen, k) for k in gen['properties']}
        for sk in gen['sections']:
            for pk in gen['sections'][sk]['properties']:
                general[f'{sk}/{pk}'] = prop(gen['sections'][sk], pk)
        task = {k: prop(md['Task'], k) for k in md['Task']['properties']}
        sesm = {k: prop(md['Session'], k) for k in md['Session']['properties']}
        trials = []
        tp = md['Session']['sections']['Trial properties']['sections']
        for tk in sorted(tp, key=lambda x: int(s(tp[x].attrs['name']).split('_')[-1])):
            t = {k: prop(tp[tk], k) for k in tp[tk]['properties']}
            t['_section'] = s(tp[tk].attrs['name'])
            trials.append(t)

        blk = f['data'][base]
        da = blk['data_arrays']
        # ---- units
        units = {}
        spikes = []
        for k in da:
            name = s(da[k].attrs.get('name', k))
            mw = re.match(r'Spike_Waveform_Unit_(\d+)_(u[A-Za-z]+)_(\d+)$', name)
            mt = re.match(r'Spike_Times_Unit_(\d+)_(u[A-Za-z]+)_(\d+)_Trial_(\d+)$', name)
            if mw:
                u = int(mw.group(1))
                d = units.setdefault(u, {'unit_id': u, 'microwire': f'{mw.group(2)}{mw.group(3)}'})
                arr = da[k]['data'][()]
                dims = da[k]['dimensions']
                lab = [s(x) for x in dims['1']['labels'][()]]
                d['waveform'] = {lab[i]: arr[i].tolist() for i in range(arr.shape[0])}
                d['waveform_unit'] = s(da[k].attrs.get('unit'))
                d['waveform_sampling_interval'] = float(dims['2'].attrs['sampling_interval'])
                d['waveform_offset'] = float(dims['2'].attrs['offset'])
                d['waveform_nix_name'] = name
            elif mt:
                u = int(mt.group(1)); tr = int(mt.group(4))
                d = units.setdefault(u, {'unit_id': u, 'microwire': f'{mt.group(2)}{mt.group(3)}'})
                d.setdefault('trials_present', set()).add(tr)
                if 'macro' not in d:
                    srcs = source_names(f, da[k])
                    for nm, kids in srcs:
                        macro = [x for x in kids if re.match(r'^m[A-Z]+\d+$', x)]
                        anat = [x for x in kids if x not in macro]
                        d['nix_source'] = nm
                        d['macro_contact'] = macro[0] if macro else 'n/a'
                        d['anatomical_location'] = anat[0] if anat else 'n/a'
                    d['spike_time_unit'] = s(da[k].attrs.get('unit'))
                v = da[k]['data'][()]
                for x in np.atleast_1d(v):
                    spikes.append((u, tr, float(x)))
                d['n_spikes'] = d.get('n_spikes', 0) + int(np.atleast_1d(v).size)
        # ---- per-trial event tags (spike-time clock)
        events = []
        event_clock = None
        g = {}
        for gname, suffix in (('Trial events single tags spike times', 'Spike_Times'),
                              ('Trial events single tags iEEG', 'iEEG')):
            if gname in blk['groups'] and 'tags' in blk['groups'][gname] and len(blk['groups'][gname]['tags']):
                g = blk['groups'][gname]['tags']; event_clock = gname; break
        for k in g:
            nm = s(g[k].attrs['name'])
            mm = re.match(r'Event_(.+)_Trial_(\d+)_(?:Spike_Times|iEEG)$', nm)
            pos = g[k]['position'][()].tolist(); ext = g[k]['extent'][()].tolist() if 'extent' in g[k] else [None]
            unit = [s(x) for x in g[k]['units'][()]] if 'units' in g[k] else []
            dur = ext[-1]
            if dur is not None and abs(dur) < 1e-300:
                dur = None  # denormal placeholder in iEEG-clock tags: no stated extent
            events.append({'trial': int(mm.group(2)) if mm else None, 'nix_event': mm.group(1) if mm else nm,
                           'onset': pos[-1], 'duration': dur, 'unit': unit[-1] if unit else None})
        # ---- macro-electrode table (labels, MNI) for the unit macro contacts
        mni = {}
        if 'iEEG_Electrode_MNI_Coordinates' in da:
            lab = [s(x) for x in da['iEEG_Electrode_MNI_Coordinates']['dimensions']['1']['labels'][()]]
            xyz = da['iEEG_Electrode_MNI_Coordinates']['data'][()]
            manual = da['iEEG_Electrode_Manual_Entry']['data'][()].ravel().tolist() if 'iEEG_Electrode_Manual_Entry' in da else [None] * len(lab)
            mni = {lab[i]: (xyz[i].tolist(), manual[i] if manual[i] is None else bool(manual[i])) for i in range(len(lab))}
        n_ieeg = int(da['iEEG_Data_Trial_01']['data'].shape[0]) if 'iEEG_Data_Trial_01' in da else None
    return {'file': os.path.basename(path), 'subject': subj, 'session': sess, 'subject_meta': subj_meta,
            'general': general, 'task': task, 'session_meta': sesm, 'trials': trials, 'units': units,
            'spikes': spikes, 'events': events, 'event_clock': event_clock, 'mni': mni, 'n_ieeg_channels': n_ieeg,
            'strings': dict(strings), 'sha256': sha256(path), 'size': os.path.getsize(path)}


def load_ds(sub, ses):
    p = f'{DSMETA}/sub-{sub:02d}__ses-{ses:02d}__ieeg__sub-{sub:02d}_ses-{ses:02d}_task-{TASK}_run-01_events.tsv'
    if not os.path.exists(p):
        return None
    return list(csv.DictReader(open(p), delimiter='\t'))


def trial_sig(rows, nix):
    if nix:
        return [(int(t['Set size']), str(t['Probe letter']), round(float(t['Response time']), 3)) for t in rows]
    return [(int(float(r['SetSize'])), r['ProbeLetter'], round(float(r['ResponseTime']), 3)) for r in rows]


def wtsv(p, header, rows):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(header)
        for r in rows:
            w.writerow([fmt(x) for x in r])


def wjson(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, 'w'), indent=2, ensure_ascii=False)
    open(p, 'a').write('\n')


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(REP, exist_ok=True)
    files = sorted(os.path.join(NIX, x) for x in os.listdir(NIX) if x.endswith('.h5'))
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(one, files))
    # participants crosswalk from ds004752 participants.tsv (sciAdv_identifier)
    part = list(csv.DictReader(open(f'{DSMETA}/participants.tsv'), delimiter='\t'))
    xw = {int(r['sciAdv_identifier']): r for r in part if r['sciAdv_identifier'].strip() not in ('n/a', '')}
    report = {'files': [], 'crosswalk': [], 'totals': {}}
    allstr = collections.Counter()
    subj_rows = {}
    sessions = collections.defaultdict(list)
    for r in res:
        sub = r['subject']; bsub = xw[sub]['participant_id']; bsubn = int(bsub[4:])
        allstr.update(r['strings'])
        nix_sig = trial_sig(r['trials'], True)
        # session crosswalk: same session number first, else search all ds004752 sessions of the subject
        match = None; cands = []
        for ses in range(1, 10):
            rows = load_ds(bsubn, ses)
            if rows is None:
                continue
            ds_sig = trial_sig(rows, False)
            same = sum(1 for a, b in zip(nix_sig, ds_sig) if a == b)
            cands.append((ses, len(ds_sig), same))
            if len(ds_sig) == len(nix_sig) and same == len(nix_sig) and match is None:
                match = ses
        report['crosswalk'].append({'nix_file': r['file'], 'nix_subject': sub, 'nix_session': r['session'],
                                    'bids_subject': bsub, 'ds004752_session_match': match,
                                    'nix_trials': len(nix_sig), 'candidates(ses,ntrials,identical_trials)': cands})
        ses_label = f"ses-{match:02d}" if match else f"ses-nix{r['session']:02d}"
        sm = r['subject_meta']
        subj_rows[bsub] = [bsub, sub, sm.get('Age'), sm.get('Sex'), sm.get('Handedness'), sm.get('Pathology'),
                           sm.get('Depth electrodes'), sm.get('Electrodes in seizure onset zone (SOZ)')]
        d = f'{OUT}/{bsub}/{ses_label}/ieeg'
        pre = f'{d}/{bsub}_{ses_label}_task-{TASK}'
        units = [r['units'][u] for u in sorted(r['units'])]
        ntr = int(r['session_meta']['Number of trials'])
        wtsv(pre + '_units.tsv',
             ['unit_id', 'microwire', 'macro_contact', 'anatomical_location', 'macro_contact_mni_x',
              'macro_contact_mni_y', 'macro_contact_mni_z', 'macro_label_manual_entry', 'n_spikes',
              'n_trials_with_spike_array', 'nix_waveform_array'],
             [[u['unit_id'], u['microwire'], u.get('macro_contact'), u.get('anatomical_location'),
               *(r['mni'].get(u.get('macro_contact'), ([None] * 3, None))[0]),
               r['mni'].get(u.get('macro_contact'), (None, None))[1],
               u.get('n_spikes', 0), len(u.get('trials_present', ())), u.get('waveform_nix_name')] for u in units])
        spk = sorted(r['spikes'], key=lambda x: (x[0], x[1]))  # stable: keeps source order within a unit/trial
        wtsv(pre + '_spikes.tsv', ['unit_id', 'trial', 'spike_time'], spk)
        w0 = next((u for u in units if 'waveform' in u), None)
        nsamp = len(w0['waveform']['Mean']) if w0 else 0
        rows = []
        for u in units:
            if 'waveform' in u:
                for stat in ('Mean', 'Std'):
                    rows.append([u['unit_id'], stat.lower()] + u['waveform'][stat])
        wtsv(pre + '_waveforms.tsv', ['unit_id', 'statistic'] + [f's{i:02d}' for i in range(nsamp)], rows)
        tr = r['trials']
        wtsv(pre + '_trials.tsv', ['trial', 'set_size', 'probe_letter', 'match', 'correct', 'response',
                                   'response_time', 'artifact'],
             [[int(t['Trial number']), int(t['Set size']), t['Probe letter'], int(t['Match']), int(t['Correct']),
               t['Response'], t['Response time'], int(bool(t['Artifact']))] for t in tr])
        ev = sorted(r['events'], key=lambda e: (e['trial'] or 0, e['onset']))
        wtsv(pre + '_trialevents.tsv', ['trial', 'onset', 'duration', 'nix_event'],
             [[e['trial'], e['onset'], e['duration'], e['nix_event']] for e in ev])
        sessions[bsub].append([ses_label, r['file'], r['sha256'], ntr, len(units), sum(u.get('n_spikes', 0) for u in units),
                               f'ses-{match:02d}' if match else 'n/a'])
        report['files'].append({'file': r['file'], 'size': r['size'], 'sha256': r['sha256'], 'bids': f'{bsub}/{ses_label}',
                                'n_units': len(units), 'n_spikes': sum(u.get('n_spikes', 0) for u in units),
                                'n_trials': ntr, 'n_ieeg_channels_not_exported': r['n_ieeg_channels'],
                                'units_without_waveform': [u['unit_id'] for u in units if 'waveform' not in u],
                                'units_without_spikes': [u['unit_id'] for u in units if 'trials_present' not in u],
                                'waveform_sampling_interval': sorted({u.get('waveform_sampling_interval') for u in units if 'waveform' in u}),
                                'waveform_offset': sorted({u.get('waveform_offset') for u in units if 'waveform' in u}),
                                'waveform_unit': sorted({u.get('waveform_unit') for u in units if 'waveform' in u}),
                                'spike_time_unit': sorted({str(u.get('spike_time_unit')) for u in units}),
                                'spike_time_range': [min((x[2] for x in r['spikes']), default=None), max((x[2] for x in r['spikes']), default=None)],
                                'trial_duration': r['session_meta'].get('Trial duration'),
                                'event_tag_group': r['event_clock'],
                                'groups': None,
                                'event_names': sorted({re.sub(r'_[A-Za-z]{8}$|_x{8}$', '_<letters>', e['nix_event']) for e in r['events']})})
        report.setdefault('task', r['task']); report.setdefault('general', r['general'])
    for bsub, rows in sessions.items():
        wtsv(f'{OUT}/{bsub}/{bsub}_sessions.tsv', ['session_id', 'nix_source_file', 'nix_source_sha256', 'n_trials',
                                                   'n_units', 'n_spikes', 'ds004752_session'], sorted(rows))
    wtsv(f'{OUT}/participants.tsv', ['participant_id', 'sciAdv_identifier', 'age', 'sex', 'handedness', 'pathology',
                                     'depth_electrodes', 'soz_electrodes'], [subj_rows[k] for k in sorted(subj_rows)])
    report['totals'] = {'files': len(res), 'units': sum(f['n_units'] for f in report['files']),
                        'spikes': sum(f['n_spikes'] for f in report['files']),
                        'sessions_matched_to_ds004752': sum(1 for c in report['crosswalk'] if c['ds004752_session_match'])}
    json.dump(report, open(f'{REP}/convert_report.json', 'w'), indent=1, default=str)
    with open(f'{REP}/privacy_strings.tsv', 'w') as f:
        for k, v in sorted(allstr.items(), key=lambda x: -x[1]):
            f.write(f'{v}\t{k}\n')
    print(json.dumps(report['totals']))
    for c in report['crosswalk']:
        print(c['nix_file'], c['bids_subject'], c['ds004752_session_match'], c['candidates(ses,ntrials,identical_trials)'])


if __name__ == '__main__':
    main()
