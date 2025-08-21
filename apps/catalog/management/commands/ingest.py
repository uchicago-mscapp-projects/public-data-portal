import importlib
import structlog
import os
import shutil
import json
from django_typer.management import Typer
from ingestion.utils import logger
from ingestion.data_models import UpstreamDataset
from catalog.models import DataSet, Publisher, Region
from pydantic import model_dump_json

app = Typer()

@app.command()

def command(self, name: str):
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
        save_to_json(details, name)

def set_dir_path(name: str):
    cwd = os.getcwd()
    dir_path = f"{os.path.dirname(cwd)}/ingest_json/{name}"

    return dir_path

def prep_dir(name: str):
    dir_path = set_dir_path(name)

    #if directory already exists, empty for overwrite
    if os.path.exists(dir_path):
        empty_dir(name)
        logger.info(f"Existing {name} directory has been emptied.")
    #otherwise create directory for first scrape data
    else:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"New directory {name} has been created.")


def save_to_json(updata: UpstreamDataset, name: str):
    dir_path = set_dir_path(name)
    file_path = os.path_join(dir_path, updata.publisher_upstream_id)
    json_upd = model_dump_json(updata)

    with open(file_path, "w") as f:
        json.dump(json_upd, f)
        logger.info(f"""Dataset {updata.publisher_upstream_id}
                    saved to {name} directory.""")


def empty_dir(name: str):
    if name == "" or ".." in name:
        raise ValueError("Invalid scraper name.")

    dir_path = set_dir_path(name)

    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as e:
            logger.info(f"Failed to delete file {filepath}", detail=e)


def ingest_to_db(name: str):
    db_entries = DataSet.objects.filter(publisher=name) # will need to assure this name is consistent in db?
    db_entries_ids = set(db_entries.values_list("upstream_id", flat=True))

    incoming_datasets = load_incoming_ds(name)
    incoming_ds_ids = set()

    if Publisher.objects.filter(name=name).exists(): # publisher object exists, retrieve from db
        publisher = Publisher.objects.filter(name=name)
    else: # publisher not in system yet, create entry
        publisher = Publisher.objects.create(
            name = dataset["publisher_name"],
            kind = "gn", # will need to revisit this, figure out how we will set
            url = dataset["publisher_url"]
        )

    for dataset in incoming_datasets:

        if Region.objects.filter(country_code=dataset["region_country_code"]).exists(): # region object exists, retrieve from db
            region = Region.objects.filter(country_code=dataset["region_country_code"])
        else: # region not in system yet, create entry
            region = Region.objects.create(
                name = dataset["region_name"],
                country_code = dataset["region_country_code"]
            )

        if dataset["upstream_id"] in db_entries_ids: # existing dataset entry, update
            # only apply change to entry with matching publisher name And upstream_id for unique id
            DataSet.objects.filter(publisher__name=dataset["publisher_name"], upstream_id=dataset["upstream_id"]).update(
                name = dataset["name"],
                description = dataset["description"],
                upstream_upload_time = dataset["upstream_upload_time"],
                start_date = dataset["start_date"],
                end_date = dataset["end_date"],
                publisher = publisher,
                region = region,
                source_url = dataset["source_url"],
                upstream_id = dataset["upstream_id"],
                license = dataset["license"],
                temporal_collection = None,
                curated_collection = None,
                quality_score = 0
            )
        else: # no existing entry, create
            DataSet.objects.create(
                name = dataset["name"],
                description = dataset["description"],
                upstream_upload_time = dataset["upstream_upload_time"],
                start_date = dataset["start_date"],
                end_date = dataset["end_date"],
                publisher = publisher,
                region = region,
                source_url = dataset["source_url"],
                upstream_id = dataset["upstream_id"],
                license = dataset["license"],
                temporal_collection = None,
                curated_collection = None,
                quality_score = 0
            )

        incoming_ds_ids.add(dataset["upstream_id"])

    print("(Would be) Deleted record upstream_ids:")
    for id in list(db_entries_ids - incoming_ds_ids):
        print(id)


def load_incoming_ds(name: str):
    cwd = os.getcwd()
    file_path = f"{os.path.dirname(cwd)}/ingest_json/{name}/json_file_name.json"

    with open(file_path, "r") as f:
        incoming_json = json.load(f)
        return incoming_json["datasets"]