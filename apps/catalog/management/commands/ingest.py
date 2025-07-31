import importlib
import structlog
from django_typer.management import Typer

logger = structlog.get_logger("pdp.ingestion")

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
