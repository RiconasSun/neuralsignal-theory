# Exact freeze byte identity

The r3 registration helper printed SHA25666e57e3d4964c323bd45218a731bad3bef62ea746b93a56f25be815ad34ced99 for its in-memory LF text. Python Windows text-mode write translated newlines to CRLF. The actual identical source_freeze.json and archived source_freeze_r3.json byte SHA256 is cbc8d6f024dd92aacb7952e1d03d907bd56ea3592b9e02ca9d2220110e674564, independently read back by the scientific reviewer.

Only actual sha(file) is used by the broker, signatures and review. No scientific source or hash map changed. Root .gitattributes preserves all bytes with -text. Future candidate/evidence identities are computed from saved bytes.
