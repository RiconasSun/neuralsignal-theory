# Supplemental Manufacturer Context

Read after evaluation as explanatory context only. Not an input to the frozen
decision rule; no gate,99mapping or conversion changed. No native recordings
were downloaded or decoded. Revision1.1,2013-05-31,PDFpage2 reviewed.

Neuralynx distinguishes event ID from TTL input value and event string. Its
format documentation specifies microsecond Cheetah timestamps for event
records and CSC block starts, plus sample frequency and valid-sample counts.
Consequently a native metadata-only continuity audit would need block-start
timestamps/valid counts/gap evidence, not only a first event label. A label99
cannot be identified as a recording marker by confusing event ID with TTL.
[Official file formats](https://neuralynx.com/_software/NeuralynxDataFileFormats.pdf).

The event entity records TTL changes and user-entered event strings. That is
not a general numerical99experiment-boundary definition. Dataset-specific
author mapping remains necessary.
[Official event overview](https://neuralynx.com/cheetah-ref-guide/Events/EventOverview.html).

Hardware field conventions do not measure synchronization accuracy of these
five sessions, certify they used identical clock settings, or recover missing
raw support from their released NWB annotations. They identify the precise
independent evidence needed for a future authorized metadata-only study.
