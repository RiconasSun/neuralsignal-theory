"""Bounded HDF5-header GET probes; never deserialize neural data."""
import json
import urllib.error
import urllib.request
import run_m1 as m1

URLS = [
    'https://gin.g-node.org/USZ_NCH/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/raw/0b27b34ecd0da217e4403bdd080b4a0d78f155fd/data_nix/Data_Subject_01_Session_01.h5',
    'https://gin.g-node.org/doi/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/raw/master/data_nix/Data_Subject_01_Session_01.h5',
    'https://gin.g-node.org/USZ_NCH/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM/raw/master/data_nix/Data_Subject_01_Session_01.h5',
]


def main():
    rows = []
    for url in URLS:
        row = {'url': url, 'method': 'GET Range bytes=0-7; read limit 8 bytes'}
        try:
            request = urllib.request.Request(url, headers={'Range': 'bytes=0-7', 'User-Agent': 'NSI-P11-coverage-header-probe'})
            with urllib.request.urlopen(request, timeout=30) as response:
                header = response.read(8)
                row.update(status=response.status, header_bytes_read=len(header), hdf5_signature=header == b'\x89HDF\r\n\x1a\n')
        except urllib.error.HTTPError as error:
            row.update(status=error.code, body_bytes_read=0)
        except OSError as error:
            row.update(error=str(error))
        rows.append(row)
    result = {'checked_at_utc': m1.now(), 'requests': rows, 'signal_values_decoded': False}
    m1.write_json(m1.PAPER / 'results/M2/bounded_get_access.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
