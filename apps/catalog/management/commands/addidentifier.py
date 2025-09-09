import importlib
import structlog
import csv
from django_typer.management import Typer
from ingestion.utils import logger
from apps.catalog.models import IdentifierKind, Identifier
from django.db import transaction

app = Typer()


@app.command()
def command(self, kind: str, file_path: str, replace: bool = False):
    self.secho(
        f"Adding {kind} identifiers w/ replacement={replace} from file: {file_path}.", fg="blue"
    )
    add_identifier(kind, file_path, replace=replace)


def add_identifier(kind: str, file_path: str, replace: bool = False):
    # make ingestion all or nothing to avoid partial ingestion if errors occur
    with transaction.atomic():
        # only reenter identifier into db if replace flag set
        if IdentifierKind.objects.filter(kind=kind).exists() and not replace:
            logger.warning(
                f"""Identifier kind {kind} already in system -- ingestion skipped.
                Set replace flag to True to replace existing identifier values."""
            )
            return

        # retrieve or create identifier kind obj for identifier from db
        identifier_kind, _ = IdentifierKind.objects.get_or_create(kind=kind)

        # replace flag set, remove existing identifiers in db
        if replace:
            Identifier.objects.filter(identifier_kind=identifier_kind).delete()
            logger.info(f"Existing identifier values for identifier kind {kind} removed.")

        new_identifier_count = 0

        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or not row[0].strip:
                    logger.warning("Invalid row.")
                    continue

                # may need to alter based on csv contents/format
                identifier_str = row[0]

                # create (or ignore if exists) identifier obj for each csv row
                identifier, created = Identifier.objects.get_or_create(
                    identifier_kind=identifier_kind, identifier=identifier_str
                )

                if created:
                    new_identifier_count += 1

        logger.info(
            f"{new_identifier_count} identifiers added for identifier kind: {identifier_kind}"
        )
