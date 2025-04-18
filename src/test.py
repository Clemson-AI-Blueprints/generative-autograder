
from autohint_injestion import ingest_project_data, wait_for_ingest_ready


if wait_for_ingest_ready():
    ingest_project_data("Justin")