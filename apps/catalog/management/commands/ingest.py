import importlib
import structlog
import os
import shutil
from django_typer.management import Typer
from ingestion.utils import logger

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

    for pd in list_datasets():
        logger.info("partial dataset", pdata=pd)
        details = get_dataset_details(pd)
        logger.info("details", detail=details)
        # TODO: this should save the datasets to disk & then import them

def empty_dir(name: str):
    cwd = os.getcwd()
    dir_path = f"{os.path.dirname(cwd)}/ingest_json/{name}"

    for filename in os.listdir(dir_path):
        filepath = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as e:
            logger.info(f"Failed to delete file {filepath}", detail=e)

def ingest_to_db():
    pass
