import importlib
import structlog
import os
import shutil
import json
import glob
from django_typer.management import Typer
from ingestion.utils import logger
from ingestion.data_models import UpstreamDataset
from apps.catalog.models import DataSet, Publisher, PublisherKind, Region

app = Typer()


@app.command()
def command(self, name: str, clearcary: bool, ingestonly: bool):
    if clearcary:
        # not sure if this should be "us/cary_nc" or "us.cary_nc"
        if name != "us.cary_nc":
            raise ValueError("clearcary flag is to only be used with us/cary_nc scraper")
        clear_carync()

    if not ingestonly:
        try:
            mod = importlib.import_module(f"ingestion.{name}")
            list_datasets = mod.list_datasets
            get_dataset_details = mod.get_dataset_details
        except (ImportError, AttributeError) as e:
            self.secho(f"Could not import: {e}", fg="red")
            return

        self.secho(f"Running ingestion.{name}.list_datasets()", fg="blue")

        prep_dir(name)

        for pd in list_datasets():
            logger.info("partial dataset", pdata=pd)
            details = get_dataset_details(pd)
            logger.info("details", detail=details)

            if details is None:
                continue
            save_to_json(details, name)

    # ingest_to_db(name)


def clear_carync():
    """resets cary_nc for development testing"""
    # empty out directory, deletes all the json
    empty_dir("us.cary_nc")
    # delete the leftover, empty directory
    dir_path = set_dir_path("us.cary_nc")
    os.rmdir(dir_path)
    logger.info("Existing Cary NC json and directory have been deleted.")

    # clear carync datasets from db
    p = Publisher.objects.get(name="Town of Cary")
    ## actual code to run
    # DataSet.objects.filter(publisher=p).delete() #delete datasets
    # p.delete() #delete publisher
    # logger.info("Cary NC scraper has been removed from the database.")

    # shows ids of datasets that would be deleted
    cary_dsets = DataSet.objects.filter(publisher=p)
    to_delete_ids = set(cary_dsets.values_list("upstream_id", flat=True))
    print("Cary NC datasets to be removed from database:")
    for id in list(to_delete_ids):
        print(id)


def set_dir_path(name: str):
    cwd = os.getcwd()
    dir_path = f"{os.path.dirname(cwd)}/ingest_json/{name}"

    return dir_path


def prep_dir(name: str):
    dir_path = set_dir_path(name)

    # if directory already exists, empty for overwrite
    if os.path.exists(dir_path):
        empty_dir(name)
        logger.info(f"Existing {name} directory has been emptied.")
    # otherwise create directory for first scrape data
    else:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"New directory {name} has been created.")


def save_to_json(updata: UpstreamDataset, name: str):
    dir_path = set_dir_path(name)
    file_path = os.path.join(dir_path, f"{updata.upstream_id}.json")
    json_upd = updata.model_dump_json()
    json_upd_data = json.loads(json_upd)

    with open(file_path, "w") as f:
        json.dump(json_upd_data, f)
        logger.info(f"""Dataset {updata.upstream_id}
                    saved to {name} directory.""")


def empty_dir(name: str):
    if name == "" or ".." in name:
        raise ValueError("Invalid Directory: Potentially Unsafe Filepath")

    dir_path = set_dir_path(name)

    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception as e:
            logger.info(f"Failed to delete file {filepath}", detail=e)


def ingest_to_db(name: str):
    incoming_datasets = load_incoming_ds(name)
    incoming_ds_ids = set()

    for i, dataset in enumerate(incoming_datasets):
        # only run on first iteration
        if i == 0:
            # load in existing db entries for publisher into flattened set
            db_entries = DataSet.objects.filter(publisher=dataset["publisher_name"])
            db_entries_ids = set(db_entries.values_list("upstream_id", flat=True))

            # retrieve/create corresponding publisher obj for dataset in db
            publisher, _ = Publisher.objects.get_or_create(
                name=dataset["publisher_name"],
                defaults={
                    "kind": PublisherKind.GOV_NATIONAL,  # will need to revisit this, figure out how we will set
                    "url": dataset["publisher_url"],
                },
            )

        # for each iter, retrieve/create corresponding region obj for dataset in db
        region, _ = Region.objects.get_or_create(
            country_code=dataset["region_country_code"], defaults={"name": dataset["region_name"]}
        )

        ds_values = {
            "name": dataset["name"],
            "description": dataset["description"],
            "upstream_upload_time": dataset["upstream_upload_time"],
            "start_date": dataset["start_date"],
            "end_date": dataset["end_date"],
            "publisher": publisher,
            "region": region,
            "source_url": dataset["source_url"],
            "upstream_id": dataset["upstream_id"],
            "license": dataset["license"],
            "quality_score": 0,
        }

        _, _ = DataSet.objects.update_or_create(
            publisher__name=dataset["publisher_name"],
            upstream_id=dataset["upstream_id"],
            defaults=ds_values,
        )

        incoming_ds_ids.add(dataset["upstream_id"])

    print("(Would be) Deleted record upstream_ids:")
    for id in list(db_entries_ids - incoming_ds_ids):
        print(id)


def load_incoming_ds(name: str):
    file_path = os.path.join(set_dir_path(name), "*.json")
    json_files = glob.glob(file_path)
    incoming_datasets = []

    for json_file in json_files:
        with open(json_file, "r") as f:
            incoming_json = json.load(f)
            incoming_datasets.append(incoming_json)

    return incoming_datasets
