"""Integer identity/ragged-bound validation before any narrowing conversion."""
import numpy as np


def identity(raw):
    array=np.asarray(raw)
    if array.ndim!=1 or array.dtype.kind not in 'iu':
        raise ValueError('SOURCE_INTEGER_VECTOR_INVALID')
    if array.size and (np.any(array<0) or int(array.max())>np.iinfo(np.int64).max):
        raise ValueError('SOURCE_INTEGER_REPRESENTATION_INVALID')
    return array.astype(np.int64,copy=False)


def offsets(raw,n_units,n_spikes):
    if not isinstance(n_spikes,int) or n_spikes<0 or n_spikes>np.iinfo(np.int64).max:
        raise ValueError('SOURCE_SPIKE_LENGTH_INVALID')
    array=identity(raw)
    if len(array)!=n_units or np.any(array>n_spikes) or np.any(array[1:]<array[:-1]):
        raise ValueError('SOURCE_RAGGED_BOUNDS_INVALID')
    if len(array) and int(array[-1])!=n_spikes or not len(array) and n_spikes:
        raise ValueError('SOURCE_RAGGED_FINAL_OFFSET_INVALID')
    return array
