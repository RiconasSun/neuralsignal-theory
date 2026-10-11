from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
BALSA_URL = "https://balsa.wustl.edu/"
PROJECT_URL = "https://balsa.wustl.edu/project?project=HCP_YA"


def fetch(url: str) -> tuple[int | None, str, str]:
    try:
        req = Request(url, headers={"User-Agent": "NSI-Paper5-HCP-Probe/1.0"})
        with urlopen(req, timeout=30) as response:
            data = response.read().decode("utf-8", errors="replace")
            return response.status, data, ""
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return exc.code, body, str(exc)
    except URLError as exc:
        return None, "", str(exc)


def strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    index_status, index_html, index_error = fetch(BALSA_URL)
    project_status, project_html, project_error = fetch(PROJECT_URL)
    combined = strip_html(index_html + "\n" + project_html)
    payload = {
        "experiment": "P5-BALSA-HCP-access-probe",
        "status": "LOGIN_AND_DATA_USE_TERMS_REQUIRED"
        if "Login to Agree" in combined or "You have not yet agreed" in combined
        else "ACCESS_PROBE_INCONCLUSIVE",
        "balsa_url_status": index_status,
        "project_url_status": project_status,
        "index_error": index_error,
        "project_error": project_error,
        "hcp_project_detected": "HCP-Young Adult 2025" in combined,
        "data_use_terms_detected": "WU-Minn HCP Consortium Open Access Data Use Terms" in combined,
        "login_to_agree_detected": "Login to Agree" in combined,
        "connectomedb_project": "HCP_YA",
        "download_authorization_boundary": "Human HCP-YA 2025 data access requires a BALSA/ConnectomeDB account and acceptance of the applicable data-use terms. This script does not bypass access controls or store credentials.",
        "next_local_data_root": "paper5/data_hcp_ya_2025",
        "next_connectome_root": "paper5/hcp_connectomes",
    }
    (OUT / "balsa_hcp_access_probe.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] == "ACCESS_PROBE_INCONCLUSIVE":
        sys.exit(2)


if __name__ == "__main__":
    main()
