from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from urllib.parse import urlparse
from .models import DataSet, Publisher, Region, DataSetFile


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


def search(request):
    qd = request.GET.lists()
    print(qd)

    #outstanding issues
    #multiword search
    #should search funnel?
    #trying to connect datasets to filetypes
    #clear button
    #advsearch currently resets, handle like searchbar
    #page display
    #defaults to showing all datasets if hit search page without query

    result_dsets = DataSet.objects.all()

    # if query:
    #     result_dsets = dsets.filter(Q(name__icontains=query) | Q(description__icontains=query))
    #     display_dsets = list(result_dsets)

    for k, v in qd:
        if k == "query":
            result_dsets = result_dsets.filter(
                Q(name__icontains=v[0]) | Q(description__icontains=v[0])
            )
        elif k == "PublisherName" and v[0]:
            pid = Publisher.objects.get(name__icontains=v[0]).id
            result_dsets = result_dsets.filter(publisherid=pid)
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
        elif k == "region":
            regionids = [Region.objects.get(country_code=r).id for r in v]
            q = Q()
            for id in regionids:
                q |= Q(region_id=id)
            result_dsets = result_dsets.filter(q)
        elif k == "filetype":
            continue
        else:
            continue

    display_dsets = list(result_dsets)
    n_results = result_dsets.count()

    limit = int(request.GET.get("limit", 11))

    # if query:
    #     result_dsets = dsets.filter(Q(name__icontains=query) | Q(description__icontains=query))
    #     display_dsets = list(result_dsets)
    #     n_results = result_dsets.count()

    paginator = Paginator(display_dsets, limit)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    geoids = list(result_dsets.values_list("region", flat=True).distinct())

    geographies = []
    for id in geoids:
        geographies.append(Region.objects.get(id=id).country_code)
    geographies = sorted(geographies)

    ftypes = list(DataSetFile.objects.values_list("file_type", flat=True).distinct())
    ftypes = sorted(ftypes)

    print(request.get_full_path())

    # feel like I could be using urlparse in here somehow
    uri = request.get_full_path()
    if "page" in uri:
        index = uri.find("page")
        print(index)
        uri = uri[: index - 1]
    print(uri)
    print(request.get_full_path())

    context = {
        "keyword": request.GET.get("query", ""),
        "search_results": display_dsets,
        "n_results": n_results,
        "page": page_obj,
        "geographies": geographies,
        "filetypes": ftypes,
        "uri": uri,
    }

    return render(request, "search.html", context)
