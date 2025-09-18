from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import DataSet, Publisher, Region, DataSetFile
from urllib.parse import urlparse


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


def about(request):
    return render(request, "about.html", {})


def dataset_detail(request, dataset_id):
    ds = get_object_or_404(DataSet, id=dataset_id)

    # tabs for now; reorg later
    tabs = [
        {"id": "details", "title": "Details"},
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


def search(request):
    #creates list of tuples like [(param, [value1, value2, value3]), (param, [value1])]
    querydict = request.GET.lists()

    # outstanding issues
    # multiword search donesies
    # should search funnel? no, donesies
    # trying to connect datasets to filetypes see picture donesies
    # clear button hmmm
    # advsearch currently resets, handle like searchbar, inputs... donesies maybe
    # page display, do whatever is easy scroll was disabled
    # defaults to showing all datasets if hit search page without query, yeah just fix thing outstanding
    #get tags when they're ready
    #sort
    #weird thing with pubtype

    #default to show all datasets if no search criteria
    result_dsets = DataSet.objects.all()

    parameters = {}
    for k, v in querydict:
        if k == "query":
            result_dsets = result_dsets.filter(
                Q(name__icontains=v[0]) | Q(description__icontains=v[0])
            )
            parameters[k] = v[0]
        elif k == "PublisherName" and v[0]:
            pid = set(Publisher.objects.filter(name__icontains=v[0]).values_list("id", flat=True))
            result_dsets = result_dsets.filter(publisher_id__in=pid)
            parameters[k]=v[0]
        elif k == "pubtype":
            q = Q()
            for pt in v:
                print("pt", pt)
                q |= Q(kind=pt)
                print("Q", q)
            pubids = list(Publisher.objects.filter(q).values_list("id", flat=True).distinct())
            print(pubids)
            q = Q()
            for id in pubids:
                q |= Q(publisher_id=id)
            result_dsets = result_dsets.filter(q)
            parameters[k]=v
        elif k == "region":
            regionids = [Region.objects.get(country_code=r).id for r in v]
            q = Q()
            for id in regionids:
                q |= Q(region_id=id)
            result_dsets = result_dsets.filter(q)
            parameters[k]=v
        elif k == "filetype":
            dsetids = set(DataSetFile.objects.filter(file_type__in=v).values_list("dataset_id", flat=True))
            result_dsets = result_dsets.filter(id__in=dsetids)
            parameters[k]=v
        else:
            continue

    display_dsets = list(result_dsets)
    n_results = result_dsets.count()

    limit = int(request.GET.get("limit", 11))

    # handles pagination and returns uri so search params retained as page turns
    paginator = Paginator(display_dsets, limit)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    uri = request.get_full_path()
    if "page" in uri:
        index = uri.find("page")
        uri = uri[: index - 1]

    # list of potential regions to filter search with
    geoids = list(DataSet.objects.values_list("region", flat=True).distinct())
    geographies = []
    for id in geoids:
        geographies.append(Region.objects.get(id=id).country_code)
    geographies = sorted(geographies)

    # list of potential filetypes to filter search with
    ftypes = list(DataSetFile.objects.values_list("file_type", flat=True).distinct())
    ftypes = sorted(ftypes)

    context = {
        "keyword": request.GET.get("query", ""),
        "search_results": display_dsets,
        "n_results": n_results,
        "page": page_obj,
        "geographies": geographies,
        "filetypes": ftypes,
        "uri": uri,
        "parameters": parameters
    }

    return render(request, "search.html", context)


def random_dataset(request):
    return redirect(
        "dataset-detail", DataSet.objects.all().order_by("?").values_list("id", flat=True)[0]
    )
