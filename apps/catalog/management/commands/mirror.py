import importlib
import structlog
from django_typer.management import Typer
from ingestion.utils import logger
from django.utils import timezone
from apps.catalog.models import DataSet, Publisher, DataSetFile

app = Typer()


@app.command()
def command(self):
    self.secho("Running dataset mirroring for applicable publishers.", fg="blue")
    mirror_datasets()


def mirror_datasets():
    # retrieve all publishers marked for mirroring, flatten names into list
    mirror_publishers = Publisher.objects.filter(mirror=True)
    mirror_publishers_names = set(mirror_publishers.values_list("name", flat=True))

    for publisher_name in mirror_publishers_names:
        # retrieve all datasets for given publisher, flatten upstream ids into list
        datasets = DataSet.objects.filter(publisher__name=publisher_name)
        dataset_ids = set(datasets.values_list("upstream_id", flat=True))

        for dataset_id in dataset_ids:
            # retrieve all dataset file objects for given dataset
            dataset_files = DataSetFile.objects.filter(
                dataset__upstream_id=dataset_id, dataset__publisher__name=publisher_name
            )
            updated_dataset_files = []

            for dataset_file in dataset_files:
                # use helper method for new block storage url
                new_url = download_dataset(dataset_file.url)

                # update url, add dataset file to list for bulk update later
                dataset_file.url = new_url
                updated_dataset_files.append(dataset_file)

            # chatgpt helped with this -->
            # asked if possible to update multiple objects at once with diff values
            DataSetFile.objects.bulk_update(updated_dataset_files, ["url"])

        # chatgpt --> asked if way to update multiple objects at once with same value
        DataSet.objects.filter(publisher__name=publisher_name, upstream_id__in=dataset_ids).update(
            last_mirrored=timezone.now()
        )

        logger.info(f"Datasets successfully mirrored for publisher: {publisher_name}")


# will update this once block storage info sorted out
def download_dataset(url: str):
    block_url = ""
    return block_url
