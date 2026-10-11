.PHONY: e0 e1 e2 e3 e4 e5 e6 e7 e8 e1-e4 e1-e8 reproduce smoke

PYTHON ?= python

EVENTS_GLOB ?= data_raw/ds001635/**/*events.tsv
TIMESERIES_GLOB ?= state_extraction/input_timeseries/**/*.csv
BOLD_GLOB ?= data_raw/ds001635/**/*_bold.nii.gz
ATLAS_IMG ?=
TR ?= 2.0
EXTERNAL_STATES ?= external_validation/stage_states_external.csv
EXTERNAL_EVENTS_GLOB ?= data_raw/ds001634/**/*events.tsv
EXTERNAL_BOLD_GLOB ?= data_raw/ds001634/**/*_bold.nii.gz
EPOCHS ?= 500
E6_PERMUTATIONS ?= 100

e0:
	$(PYTHON) scripts/e0_data_qc_audit.py --events-glob "$(EVENTS_GLOB)" --timeseries-glob "$(TIMESERIES_GLOB)" --external-states "$(EXTERNAL_STATES)"

e1:
	$(PYTHON) scripts/e1_extract_states.py --events-glob "$(EVENTS_GLOB)" --timeseries-glob "$(TIMESERIES_GLOB)" --bold-glob "$(BOLD_GLOB)" --native-grid --grid-bins 6,6,6 $(if $(TR),--tr "$(TR)",)

e2:
	$(PYTHON) scripts/e2_cwp_existence.py --states state_extraction/stage_states.csv

e3:
	$(PYTHON) scripts/e3_task_vs_cwp.py --states state_extraction/stage_states.csv --epochs "$(EPOCHS)"

e4:
	$(PYTHON) scripts/e4_unseen_combination.py --states state_extraction/stage_states.csv --epochs "$(EPOCHS)"

e5:
	$(PYTHON) scripts/e5_unseen_domain.py --states state_extraction/stage_states.csv --epochs "$(EPOCHS)"

e6:
	$(PYTHON) scripts/e6_null_falsification.py --states state_extraction/stage_states.csv --epochs "$(EPOCHS)" --permutations "$(E6_PERMUTATIONS)"

e7:
	$(PYTHON) scripts/e7_external_dataset.py --train-states state_extraction/stage_states.csv --external-states "$(EXTERNAL_STATES)" --epochs "$(EPOCHS)"

e8:
	$(PYTHON) scripts/e8_statistics_reproduction.py

e1-e4: e1 e2 e3 e4

e1-e8:
	$(PYTHON) scripts/run_e1_e8.py --events-glob "$(EVENTS_GLOB)" --timeseries-glob "$(TIMESERIES_GLOB)" --bold-glob "$(BOLD_GLOB)" --native-grid --grid-bins 6,6,6 $(if $(TR),--tr "$(TR)",) --external-states "$(EXTERNAL_STATES)" --external-events-glob "$(EXTERNAL_EVENTS_GLOB)" --external-bold-glob "$(EXTERNAL_BOLD_GLOB)" --epochs "$(EPOCHS)" --e6-permutations "$(E6_PERMUTATIONS)"

reproduce: e1-e8

smoke:
	$(PYTHON) scripts/smoke_test_e1_e8.py
