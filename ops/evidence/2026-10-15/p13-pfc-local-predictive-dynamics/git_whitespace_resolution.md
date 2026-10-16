# Archival whitespace preservation

Initial staged diff whitespace gate failed: native CRLF was treated as trailing whitespace under repository * -text. Rechecking with cr-at-eol left only upstream provider README/HTML whitespace. Full unsuccessful checks retained in external initial_whitespace_failure.log and crlf_whitespace_check.log.

No source, registration, saved output, native log or protocol bytes were rewritten. Scoped .gitattributes permit native CRLF while retaining real trailing-space and space-before-tab checks for active code/test/docs/evidence. Only exact upstream README/HTML snapshots are binary display artifacts; their original SHA256 is checked by saved reproduction. Active Python tests/code remain textual and fully checked. This is not a scientific threshold, test assertion or acceptance-policy change.

The three new Git-display attribute files do not change the40 frozen replay/source/data artifacts and are independently included in the final Git manifest. Initial manifest73files retained; expanded manifest includes these attributes and this explanatory receipt. No scientific result rerun needed.
