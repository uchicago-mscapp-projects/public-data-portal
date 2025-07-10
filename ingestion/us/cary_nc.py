from ingestion.data_models import UpstreamDataset, PartialDataset

def list_datasets() -> list[PartialDataset]:
    return [
        ("https://example.com", None)
    ]

def get_dataset_details(pd: PartialDataset) -> UpstreamDataset:
    return None
