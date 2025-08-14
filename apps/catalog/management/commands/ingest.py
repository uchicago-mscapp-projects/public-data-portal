import importlib
from django_typer.management import Typer

app = Typer()


@app.command()
def command(self, name: str):
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
        self.secho("Module did not contain list_datasets/get_dataset_details or get_full_datasets")

    self.secho(f"Running ingestion.{name}", fg="blue")

    for details in get_full_datasets():
        print("\t", details)
        # TODO: this should save the datasets to disk & then import them
