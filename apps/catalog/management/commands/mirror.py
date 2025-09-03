import importlib
import structlog
from django_typer.management import Typer
from ingestion.utils import logger
from django.utils import timezone
from apps.catalog.models import DataSetFile

app = Typer()


@app.command()
def command(self):
    self.secho("Running dataset mirroring for applicable publishers.", fg="blue")
    mirror_datasets()


def mirror_datasets():
    # retrieve all dataset files for given publisher not already mirrored
    files = DataSetFile.objects.filter(dataset__publisher__mirror=True, last_mirrored__isnull=True)

    updated_dataset_files = []
    updated_publishers = set()

    # iterate over mirror-specified dataset files, loading into memory in 1000 size intervals
    # to avoid overbearing system
    for dataset_file in files.iterator(chunk_size=1000):
        # use helper method for new block storage url
        new_url = download_dataset(dataset_file.url)

        # update url, mirror timestamp, add dataset file to list for bulk update later
        dataset_file.mirrored_url = new_url
        dataset_file.last_mirrored = timezone.now()
        updated_dataset_files.append(dataset_file)

        updated_publishers.add(dataset_file.dataset.publisher.name)

    if updated_dataset_files:
        # runs singular SQL query for entire batch for efficiency, updating only
        # mirrored_url and last_mirrored fields
        DataSetFile.objects.bulk_update(updated_dataset_files, ["mirrored_url", "last_mirrored"])

    print("Mirrored publishers:")
    for publisher_name in list(updated_publishers):
        print(publisher_name)


# will update this once block storage info sorted out
def download_dataset(url: str):
    block_url = ""
    return block_url
