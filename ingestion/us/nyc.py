from typing import Generator
from ingestion.data_models import PartialDataset
from ingestion.utils import make_request, logger


API_URL = "https://data.cityofnewyork.us/api/views.json"


def list_datasets() -> Generator[PartialDataset, None, None]:
    """
    Fetch datasets from NYC Open Data.
    """

    logger.info("Fetching NYC Open Data datasets")

    data = make_request(API_URL)

    for d in data:

        name = d.get("name")
        description = d.get("description")
        dataset_id = d.get("id")

        if not dataset_id:
            continue

        url = f"https://data.cityofnewyork.us/d/{dataset_id}"

        yield PartialDataset(
            name=name,
            description=description,
            source_url=url,
        )
