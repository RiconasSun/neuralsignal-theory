"""Frozen saved provider descriptors only; unknown units/undecoded fields stay so."""
import numpy as np
from .source import ROOT,sha
from .baseline_A import read


def describe(record,units):
    path=ROOT/record['header_file']
    if sha(path.read_bytes())!=record['header_sha256']:raise ValueError('Descriptor header identity mismatch')
    header=read(path);values=header['decoded_values'];coordinates={};attributes={}
    for name in ['AP','DV','ML']:
        key='/general/extracellular_ephys/electrodes/'+name
        if key in values:
            coordinates[name]=[values[key][u['electrode_row']] for u in units]
            attributes[name]=next(a['attrs'] for a in header['schema'] if a['path']==key)
    rows=read(ROOT/'paper13_ki_feasibility1/results/review1/audit.json')['all_records']
    source=next(a for a in rows if a['recording_id']==record['recording_id'] and a['dandiset']=='000473')
    conditions=sorted({a['exptype'] for a in source['source_table_matches'] if a.get('exptype')})
    depth_masks={}
    if 'DV' in coordinates and np.isfinite(np.asarray(coordinates['DV'],dtype=float)).all():
        order=sorted(range(8),key=lambda j:(coordinates['DV'][j],units[j]['unit_id']))
        depth_masks={'lower_raw_DV_rank4':[j in order[:4] for j in range(8)],'higher_raw_DV_rank4':[j in order[4:] for j in range(8)]}
    return {'header_sha256':record['header_sha256'],'unit_ids':[u['unit_id'] for u in units],
        'provider_coordinates':coordinates,'provider_coordinate_attributes':attributes,
        'physical_depth_units_verified':False,'depth_rank_masks':depth_masks,
        'genotype':values.get('/general/subject/genotype','NOT_DECODED_FROM_SOURCE; field present in schema, value not examined'),
        'documented_conditions':conditions,'source_table_rows':source['source_table_matches'],
        'probe_id':source.get('probe_id'),'one_probe_per_mouse':True,'independent_probe_replication':False}
