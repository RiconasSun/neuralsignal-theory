.PHONY: reproduce-paper2 reproduce-paper3 reproduce-paper3-e1 reproduce-paper3-e2 reproduce-paper4 reproduce-paper4-online-confounds reproduce-paper5 reproduce-paper5-balsa-access-probe reproduce-paper5-online-structural-audit reproduce-paper9 reproduce-paper10

PYTHON ?= python

reproduce-paper2:
	$(PYTHON) paper2/scripts/run_paper2.py

reproduce-paper3:
	$(PYTHON) paper3/scripts/run_paper3_e1.py
	$(PYTHON) paper3/scripts/run_paper3_e2_e8.py

reproduce-paper3-e1:
	$(PYTHON) paper3/scripts/run_paper3_e1.py

reproduce-paper3-e2:
	$(PYTHON) paper3/scripts/run_paper3_e2_e8.py

reproduce-paper4:
	$(PYTHON) paper4/scripts/run_paper4_e1_e8.py

reproduce-paper4-online-confounds:
	$(PYTHON) paper4/scripts/recover_openneuro_confounds.py --dataset ds001635 --dataset ds001634 --dataset ds004469
	$(PYTHON) paper4/scripts/run_paper4_e1_e8.py

reproduce-paper5:
	$(PYTHON) paper5/scripts/run_paper5_hcp_e0_e8.py

reproduce-paper5-balsa-access-probe:
	$(PYTHON) paper5/scripts/probe_balsa_hcp_access.py

reproduce-paper5-online-structural-audit:
	$(PYTHON) paper5/scripts/audit_openneuro_structural_metadata.py --dataset ds001635 --dataset ds001634 --dataset ds004469
	$(PYTHON) paper5/scripts/run_paper5_e1_e8.py

reproduce-paper9:
	$(PYTHON) paper9/scripts/run_paper9.py

reproduce-paper10:
	$(PYTHON) paper10/scripts/run_paper10.py
