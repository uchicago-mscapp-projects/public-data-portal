import importlib
import structlog
import os
import shutil
import json
import glob

# from time import sleep
from django_typer.management import Typer
from ingestion.utils import logger
from ingestion.data_models import UpstreamDataset
from apps.catalog.models import DataSet, Publisher, PublisherKind, Region, DataSetFile

PUB_SCR_CROSS = {"us.cary_nc": "Town of Cary", "oecd": "OECD"}

app = Typer()


@app.command()
def command(self, name: str, cleardb: bool, ingestonly: bool):
    if cleardb:
        clear_db(name)

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

    ingest_to_db(name)


def clear_db(name: str):
    """resets db for specified scraper for development testing"""
    # map internal scraper name to external publisher name
    pubname = PUB_SCR_CROSS[name]
    if Publisher.objects.filter(name=pubname).exists():
        p = Publisher.objects.get(name=pubname)
    else:
        return
    # if scraper dsets exist, delete them
    DataSet.objects.filter(publisher_id=p.id).delete()  # delete datasets
    p.delete()  # delete publisher
    logger.info(f"{name} scraper has been removed from the database.")
    # sleep(10)

    # cary_dsets = DataSet.objects.filter(publisher_id=p)
    # to_delete_ids = set(cary_dsets.values_list("upstream_id", flat=True))
    # print(f"{name} datasets to be removed from database: {len(to_delete_ids)}")


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
            # retrieve/create corresponding publisher obj for dataset in db
            publisher, _ = Publisher.objects.get_or_create(
                name=dataset["publisher_name"],
                defaults={
                    "kind": PublisherKind.GOV_NATIONAL,  # will need to revisit this
                    "url": dataset["publisher_url"],
                },
            )

            # load in existing db entries for publisher into flattened set
            db_entries = DataSet.objects.filter(publisher=publisher)
            db_entries_ids = set(db_entries.values_list("upstream_id", flat=True))

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

        ds_obj, _ = DataSet.objects.update_or_create(
            publisher__name=dataset["publisher_name"],
            upstream_id=dataset["upstream_id"],
            defaults=ds_values,
        )

        for file_json in dataset["files"]:
            ds_file, _ = DataSetFile.objects.get_or_create(
                original_url=file_json["url"],
                defaults={
                    "dataset": ds_obj,
                    "url": file_json["url"],
                    "file_type": file_json["file_type"],
                    "file_size_mb": file_json["file_size_mb"],
                },
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
