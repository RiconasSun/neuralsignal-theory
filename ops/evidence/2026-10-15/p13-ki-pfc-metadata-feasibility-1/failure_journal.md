# Preserved unsuccessful attempts

1. first_schemas.log: receipt JSON was mistakenly included by manifest glob, raising KeyError before any NWB header request. Fixed exact page filename pattern; original freeze/log preserved and regression added.
2. System Python lacked openpyxl; no installation needed: independent checker uses the existing bundled Python(openpyxl3.1.5), different implementation from stdlib XML production parser. No data or assertions changed.
3. interval_archive_attempt1.log: zipfile omitted read length in bounded EOCD tail; rejected before archive bytes. Added narrowly bounded <=65558byte tail compatibility, keeping all byte/range limits.
4. interval_archive_attempt2.log: HTTP response header case was lower-case and Zenodo supplies no ETag. Fixed case-insensitive header handling; NWB strict ETag rule unchanged. Documentation ZIP uses only exact published record/path/declaredchecksum, ranges retain SHA256; full checksum remains explicitly unverified. Original3405byte response journal retained.
5. interval_archive_attempt3.log: successful3918-entry directory/168interval-metadata-only members using1641805bytes, no full1.9GB archive or neural metrics read.
6. Exact interval creator commit lookups failed in specified public repository; journal and source log retained. This is a scientific/provenance limitation, not silently repaired or treated as verified creation code.

No model fits, neural arrays, score tuning, scientific threshold changes or historical study edits occurred. No external model-service CLI calls were retried.
