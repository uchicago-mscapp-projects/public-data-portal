from django.shortcuts import render, get_object_or_404
from .models import DataSet, Publisher


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

    # TO DO: handle case when dataset id not found
    #ds = DataSet.objects.get(id=dataset_id)

    context = {
        # LATER: get variables from dataset
        "ds": get_object_or_404(DataSet, id=dataset_id),

        # FOR NOW: strings for testing
        "dataset_id": dataset_id,
        "name": "Some data about something",
        "description": "Here is a description of the data.",
        "publisher": "Government of Canada",
        "region": "CA",
        "created_at": "created_at",
        "start_date": "start_date",
        "end_date": "end_date",
    }

    # just to demonstrate, here is how you would obtain a parameter from the
    # querystring (e.g. /?name=Bart). request.GET is a dictionary of these
    # parameters

    # TO DO: implement tabs to show collections / UGC with query strings
    #context["name"] = request.GET.get("name", "anonymous user")

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
    return render(request, "dataset_detail.html", context)
