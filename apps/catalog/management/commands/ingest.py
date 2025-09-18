import importlib
import structlog
import os
import shutil
import json
import glob
from django_typer.management import Typer
from ingestion.utils import logger
from ingestion.data_models import UpstreamDataset
from apps.catalog.models import (
    DataSet,
    Publisher,
    PublisherKind,
    Region,
    DataSetFile,
    IdentifierKind,
)
from functools import cache


app = Typer()


@app.command()
def command(self, name: str, cleardb: bool = False, ingestonly: bool = False):
    if cleardb:
        clear_db(name)

    if not ingestonly:
        # We have two potential strategies:
        #
        # 1) (preferred) list_datasets returns partial datasets
        #    which are then hydrated by get_dataset_details
        # 2) get_full_datasets returns fully-hydrated data sets
        try:
            mod = importlib.import_module(f"ingestion.{name}")

            if not hasattr(mod, "list_datasets") or not hasattr(mod, "get_dataset_details"):
                # will raise AttributError if none of the 3 are found
                get_full_datasets = mod.get_full_datasets
            else:
                # combine the two here for now, better logic TBD
                def get_full_datasets():
                    for pd in mod.list_datasets():
                        print(pd)
                        yield mod.get_dataset_details(pd)

        except ImportError as e:
            self.secho(f"Could not import: {e}", fg="red")
            return
        except AttributeError:
            self.secho("""Module did not contain
                       list_datasets/get_dataset_details or get_full_datasets""")

        prep_dir(name)

        self.secho(f"Running ingestion.{name}", fg="blue")

        for details in get_full_datasets():
            logger.info("details", detail=details)
            # TODO: this should save the datasets to disk & then import them
            if details is None:
                continue
            save_to_json(details, name)

    ingest_to_db(name)


def clear_db(name: str):
    """resets db for specified scraper for development testing"""
    # if scraper dsets exist, delete them
    if DataSet.objects.filter(scraper=name).exists():
        DataSet.objects.filter(scraper=name).delete()
        logger.info(f"{name} datasets has been removed from the database.")


def set_dir_path(name: str):
    cwd = os.getcwd()
    dir_path = f"{cwd}/ingest_json/{name}"
    dir_path = os.path.normpath(dir_path)

    return dir_path


def prep_dir(name: str):
    dir_path = set_dir_path(name)

    # if directory already exists, empty for overwrite
    if os.path.exists(dir_path):
        empty_dir(name)
        logger.info(f"Existing {dir_path} directory has been emptied.")
    # otherwise create directory for first scrape data
    else:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"New directory {dir_path} has been created.")


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

    # load in existing db entries for scraper into flattened set
    db_entries = DataSet.objects.filter(scraper=name)
    db_entries_ids = set(db_entries.values_list("upstream_id", flat=True))

    for dataset in incoming_datasets:
        # retrieve/create corresponding publisher obj for dataset in db
        publisher, _ = Publisher.objects.get_or_create(
            name=dataset["publisher_name"],
            defaults={
                "kind": PublisherKind.GOV_NATIONAL,  # will need to revisit this
                "url": dataset["publisher_url"] or "",
            },
        )

        # retrieve/create corresponding region obj for dataset in db
        region, _ = Region.objects.get_or_create(
            country_code=dataset["region_country_code"], defaults={"name": dataset["region_name"]}
        )

        # retrieve corresponding identifier kind objs for dataset in db
        identifier_kinds = []
        for kind in dataset["identifier_kinds"]:
            identifier_kind = get_identifier_kind(kind)

            if identifier_kind:  # valid IdentifierKind
                identifier_kinds.append(identifier_kind)
            else:  # invalid, skip
                logger.warning(
                    f"""Identifier kind {kind} not recognized by system and will
                    be omitted. Please double check or ingest identifier kind into
                    system using addidentifier.py command."""
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
            "quality_score": -1,
            "scraper": name,
            "identifier_kinds": identifier_kinds,
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
        
        for tag in dataset["tags"]:
            # add a model for tags
            # convert to lowercase
            # get or create tag object
            # OR could do this in a very stupid way temporarily
            pass

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


@cache
def get_identifier_kind(kind: str) -> IdentifierKind:
    # use filter() to allow for None return obj vs. get() which raises exception
    identifier_kind = IdentifierKind.objects.filter(kind=kind).first()
    return identifier_kind
