"""Restricted native running reader, with explicit exact alias and precision metadata."""
import contextlib
import hashlib
import h5py
import numpy as np

ALIAS='/processing/running/running_wheel_rotation/timestamps'
TARGET='/processing/running/running_speed/timestamps'
ROT='/processing/running/running_wheel_rotation/data'
END='/processing/running/running_speed_end_times/timestamps'
SCALARS=('/identifier','/session_start_time','/timestamps_reference_time')
ALLOWED=frozenset((*SCALARS,ROT,ALIAS,TARGET,END))


def attributes(obj):
    out={}
    for name in ['unit','conversion','offset','interval','namespace','neurodata_type','object_id','nwb_version']:
        if name not in obj.attrs:continue
        attr=obj.attrs.get_id(name)
        if attr.get_storage_size()>4096 or np.prod(attr.shape or (1,))>16:
            raise ValueError('Oversized registered attribute')
        value=obj.attrs[name]
        if isinstance(value,bytes):value=value.decode('utf8')
        if isinstance(value,np.generic):value=value.item()
        if not isinstance(value,(str,int,float,bool)) or (isinstance(value,float) and not np.isfinite(value)):
            raise ValueError('Unsupported attribute metadata')
        if isinstance(value,str) and len(value.encode())>4096:raise ValueError('Attribute size')
        out[name]=value
    return out


def object_metadata(obj,file):
    same=bool(obj.file.id==file.id)
    if not same:raise ValueError('Cross-file object denied')
    out={'type':type(obj).__name__,'address':int(h5py.h5o.get_info(obj.id).addr),'same_file':same,'attributes':attributes(obj)}
    if isinstance(obj,h5py.Dataset):out.update({'shape':list(obj.shape),'dtype':obj.dtype.str})
    return out


def resolve(file,path,audit):
    if path not in ALLOWED:raise ValueError('Unregistered/neural path denied before lookup')
    parent=file;walked=''
    for part in path.strip('/').split('/'):
        if not isinstance(parent,h5py.Group):raise ValueError('Unexpected intermediate dataset')
        current=walked+'/'+part;link=parent.get(part,getlink=True)
        row={'path':current,'requested_path':path,'link_class':type(link).__name__ if link is not None else 'Missing',
             'literal_target':getattr(link,'path',None),'parent_address':int(h5py.h5o.get_info(parent.id).addr)}
        audit.append(row)
        if isinstance(link,h5py.SoftLink):
            if current!=ALIAS or path!=ALIAS or link.path!=TARGET:
                raise ValueError('Unexpected/relative/cyclic internal alias denied')
            target=resolve(file,TARGET,audit) # canonical path remains HardLink-only
            native=parent[part] # only the already verified fixed literal alias
            one,two=object_metadata(native,file),object_metadata(target,file)
            if native.id!=target.id or one['address']!=two['address']:
                raise ValueError('Exact alias source-object identity failed')
            row.update({'resolved_metadata':one,'expected_object_match':True})
            return native
        if not isinstance(link,h5py.HardLink):
            raise ValueError('Missing/external/noncanonical source link denied')
        obj=parent[part];row['metadata']=object_metadata(obj,file)
        parent=obj;walked=current
    return parent


@contextlib.contextmanager
def value_scope(file, permitted, reads):
    old_get=h5py.Dataset.__getitem__
    names=['__array__','__iter__','read_direct'];old={n:getattr(h5py.Dataset,n) for n in names}
    def deny(*a,**kw):raise ValueError('Unregistered dataset value API denied')
    def get(dataset,key,*a,**kw):
        address=int(h5py.h5o.get_info(dataset.id).addr)
        if dataset.file.id!=file.id or address not in permitted:
            raise ValueError('Neural/unknown dataset value access denied')
        name=permitted[address]
        scalar=name in SCALARS
        if (scalar and key!=()) or (not scalar and not (isinstance(key,slice) and key==slice(None))):
            raise ValueError('Only exact registered native scalar/vector reads')
        reads.append(name)
        return old_get(dataset,key,*a,**kw)
    h5py.Dataset.__getitem__=get
    for n in names:setattr(h5py.Dataset,n,deny)
    try:yield
    finally:
        h5py.Dataset.__getitem__=old_get
        for n,fn in old.items():setattr(h5py.Dataset,n,fn)


def native_running(file,item,header,audit,reads,captured,first=False,persist=None):
    if attributes(file).get('nwb_version')!='2.2.2':raise ValueError('Frozen source NWB version')
    datasets={path:resolve(file,path,audit) for path in sorted(ALLOWED)}
    if any(not isinstance(ds,h5py.Dataset) for ds in datasets.values()):raise ValueError('Registered source objects must be datasets')
    if any(datasets[x].size!=1 for x in SCALARS):raise ValueError('Original identity scalar shape')
    for path in [ROT,ALIAS,TARGET,END]:
        d=datasets[path]
        allowed=['<f4','<f8'] if path==ROT else ['<f8']
        if d.ndim!=1 or d.dtype.str not in allowed or not 0<len(d)<=2000000:
            raise ValueError('Unsupported native source storage/row metadata')
    if first and datasets[ROT].dtype.str!='<f4':raise ValueError('Known first-source native dtype changed')
    if datasets[ALIAS].id!=datasets[TARGET].id:raise ValueError('Canonical timestamp identity mismatch')
    if not len(datasets[ROT])==len(datasets[ALIAS])==len(datasets[END]):raise ValueError('Same-row source shape mismatch')
    rotattr=attributes(datasets[ROT]);parentattr=attributes(datasets[ROT].parent)
    if rotattr.get('unit')!='radians' or parentattr.get('unit','radians')!='radians':raise ValueError('Native angular units')
    for field,expected in [('conversion',1.),('offset',0.)]:
        if rotattr.get(field,expected)!=expected:raise ValueError('Nonidentity native rotation scaling')
    for path in [TARGET,END]:
        attr=attributes(datasets[path])
        if attr.get('unit')!='seconds':raise ValueError('Native timestamp seconds required')
        if attr.get('conversion',1.)!=1. or attr.get('offset',0.)!=0.:raise ValueError('Native clock conversion forbidden')
    permitted={int(h5py.h5o.get_info(ds.id).addr):path for path,ds in datasets.items() if path!=ALIAS}
    with value_scope(file,permitted,reads):
        clocks={}
        for path in SCALARS:
            value=np.asarray(datasets[path][()]).item()
            if isinstance(value,bytes):value=value.decode('utf8')
            value=str(value)
            if len(value)>512:raise ValueError('Oversized source identity scalar')
            expected=str(item['session_id']) if path=='/identifier' else header[path]
            if value!=expected:raise ValueError('Original source identifier/clock scalar mismatch')
            clocks[path]=value
        # Preserve originals before any promotion; a later failure retains captures.
        for key,path in [('rotation',ROT),('start',TARGET),('end',END)]:
            captured[key]=datasets[path][:]
            if persist is not None:persist(key,captured[key])
    return {'root':object_metadata(file,file),'objects':{p:object_metadata(d,file) for p,d in datasets.items()},
            'source_clock_scalars':clocks,'rotation_attributes':rotattr,'same_file_alias_identity':True,
            'original_writer_same_row_mapping':'Frozen nwb_writer.py source maps net_rotation/start_time/end_time from the same running_speed rows; actual link identity/shapes checked; no physical sensor-truth claim.'}
