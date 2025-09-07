import importlib
import structlog
import csv
from django_typer.management import Typer
from ingestion.utils import logger
from apps.catalog.models import IdentifierKind, Identifier

app = Typer()


@app.command()
def command(self, kind: str, file_path: str, replace: bool = False):
    self.secho(
        f"Adding {kind} identifier(s) w/ replacement={replace} from file: {file_path}.", fg="blue"
    )
    add_identifier(kind, file_path, replace=replace)


def add_identifier(kind: str, file_path: str, replace: bool = False):
    # only reenter identifier into db if replace flag set
    if IdentifierKind.objects.filter(kind=kind).exists() and not replace:
        return

    # retrieve or create identifier kind obj for identifier from db
    identifier_kind, _ = IdentifierKind.objects.get_or_create(kind=kind)

    identifier_count = 0  # maybe helpful? can remove if not

    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            # may need to alter based on csv contents/format
            identifier_str = row[0]

            # create (or ignore if exists) identifier obj for each csv row
            identifier, _ = Identifier.objects.get_or_create(
                identifier_kind=identifier_kind, identifier=identifier_str
            )
            identifier_count += 1

    logger.info(
        f"{identifier_count} total identifiers registered for identifier kind: {identifier_kind}"
    )
