
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from taxonomy import models as tx_models
import models as s_models


def populate_slug_table():
    '''
    Populate the Slug table with Taxonomy names. This table is used by 
    Elasticsearch for faceted_search().  

    Instructions: Comment out the save() function in the Slug model first.
    populate the slugs after the objects have been created.
    '''  
    from fooreviews import models
    s_models.Slug.objects.all().delete()
    a = tx_models.ProductTaxonomy.objects.all()
    b_list = []
    for obj in a:
        b_list.append(obj.name)

    b_set_list = list(set(b_list))
    for val in b_set_list:
        s_models.Slug.objects.create(name=val)

    slug_set = s_models.Slug.objects.all()
    for obj in slug_set:
        obj.save()

def custom_paginator(list_obj, page):
    '''
    Paginate the results. We have to create a paginator object manually
    instead of using paginate_by parameter in views, which works with
    get_queryset() but not get_context_data().
    '''
    paginator = Paginator(list_obj, 10) # Show 10 results per page
    try:
        paginated_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_list = paginator.page(paginator.num_pages)
    return paginated_list

def pretty_print(obj):
    # FOR DEBUGGING
    '''
    Pretty print a nested dictionary object. Can be used for other objects, too.
    '''
    print json.dumps(obj, indent=4)