import importlib
import structlog
from django_typer.management import Typer
from ingestion.utils import logger

app = Typer()


@app.command()
def command(self):
    pass

def load_mirror_datasets():
    pass
