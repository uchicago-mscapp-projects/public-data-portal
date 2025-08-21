import importlib
import structlog
from django_typer.management import Typer
from ingestion.utils import logger
from apps.catalog.models import DataSet, Publisher, DataSetFile

app = Typer()


@app.command()
def command(self):
    pass


def mirror_datasets():
    mirror_publishers = Publisher.objects.filter(mirror=True)
    mirror_publishers_names = set(mirror_publishers.values_list("name", flat=True))


    # need to figure out most efficient way to go about this, can either:
    #
    # 1) query DataSetFile obj directly (based on dataset__publisher) --> more efficient? 
    #    but then need to access DataSet somehow later for last_mirrored update, 
    #    also will this make updating DataSetFile urls complicated? (no unique id on DataSetFile model)
    #
    # 2) iterate over DataSet obj, then access DataSetFile for each --> have access to DataSet and DataSetFile for changes
    
    for publisher_name in mirror_publishers_names:
        
        dataset_files = DataSetFile.objects.filter(dataset__publisher=publisher_name)
        dataset_files_urls = set(dataset_files.values_list("url", flat=True))
        print(dataset_files_urls) # would actually download files, save to block storage, redirect dataset url, etc. here


def update_last_mirrored(publisher: str, upstream_id: str):
    dataset = DataSet.objects.filter(publisher__name=publisher, upstream_id=upstream_id)
    #dataset.update(last_mirrored=Time.now())
            
            


