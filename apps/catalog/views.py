from django.shortcuts import render, get_object_or_404, redirect
from .models import DataSet, Publisher, DataSetFile


def index(request):
    # this view is intended as a simple demonstration of how to write a view
    # all views take the 'request' parameter, additional parameters can be
    # passed as part of the URL or as GET/POST parameters (see Django docs)
    #
    # Note: This view does not take parameters, but most will!

    # view code typically populates a dictionary of tempate context, here
    # quite a simple one
    #
    # these variables become available in the template's {{ }} and {% %} blocks
    context = {
        "num_datasets": DataSet.objects.count(),
        "num_publishers": Publisher.objects.count(),
    }

    # just to demonstrate, here is how you would obtain a parameter from the
    # querystring (e.g. /?name=Bart). request.GET is a dictionary of these
    # parameters
    context["name"] = request.GET.get("name", "anonymous user")

    # Aside: Any time you see code taking untrusted user input be suspicious!
    #  In older web frameworks, the code here would lead to a vulnerability
    #  since a user could put ?name=<some malicious html...> and inject that
    #  into the page.
    #
    # In practice, Django templates by default disallow HTML, which will
    # prevent this attack. Keep in mind that all input from the internet
    # is potentially hostile and should be escaped/treated with caution.

    # most views will end with a call to render, passing the template name
    # and context dictionary
    return render(request, "index.html", context)


def dataset_detail(request, dataset_id):
    ds = get_object_or_404(DataSet, id=dataset_id)

    # tabs for now; reorg later
    tabs = [
        {"id": "details", "title": "Details"},
        {"id": "metadata", "title": "Metadata"},
        {"id": "comments", "title": "Comments"},
        {"id": "collections", "title": "Collections"},
    ]

    context = {
        "ds": ds,
        "files": DataSetFile.objects.filter(dataset__id=dataset_id),
        "collections": [collection for collection in ds.curated_collections.all()],
        # "tags": ds.tags,
        "tabs": tabs,
    }

    return render(request, "dataset_detail.html", context)


def random_dataset(request):
    return redirect(
        "dataset-detail", DataSet.objects.all().order_by("?").values_list("id", flat=True)[0]
    )
