from django.http import Http404
from search.navigation.faceted_search import FacetedSearch
import search.search_helper as s_helper
import services.loggers as loggers
logger = loggers.Loggers(__name__).get_logger()

class CategoryResult(object):
    '''
    Prepares context dictionary for populating faceted navigation.
    '''
    def __init__(self, request, **kwargs):
    	self.request = request
        self.page = None

    def _get_query_dict(self):
        query_dict = self.request.GET.copy()
        self.page = query_dict.get('page')
        if self.page:
            del(query_dict['page'])
        return query_dict

    def get_response(self):
        query_dict = self._get_query_dict()
        url_path = self.request.path
        fs = FacetedSearch(url_path, query_dict)
        response_dict = fs.search()
        return response_dict

    def get_facets(self, response_dict):
        '''
        Get aggregated facets and group them such that the 'category' 
        facet is first in the list. Sorting it this way helps us display
        the facets in a logical order.
        '''
       
        agg_names = sorted(response_dict['agg_names'])
        filter_facets = []
        cat_facet = []
        facet_slugs = []
        for name in agg_names:
            facet = {name.capitalize(): response_dict[name]}
            if name != 'category':
                filter_facets.append(facet)
            else:
                cat_facet.append(facet)
            facet_slugs.append({name.capitalize(): name})
        facets = cat_facet[:] + filter_facets[:]
        kwargs = {
            'facets': facets,
            'facet_slugs': facet_slugs,
        }
        return kwargs
    def get_paginated_hits(self, response_dict):
        count = 0
        is_paginated = False    
        single_result = False
        paginated_list = None
        article_hit_list = response_dict.get('hit_list')
        if article_hit_list:
            count = len(article_hit_list)
            if count > 10:
                is_paginated = True
            if  count == 1 :
                single_result = True
            paginated_list= s_helper.custom_paginator(article_hit_list, self.page)
        kwargs = {
            'paginated_list': paginated_list,
            'is_paginated': is_paginated,
            'single_result': single_result,
        }
        return kwargs

def get_category_context(request):
    '''
    Return a category context dictionary with aggregated facets 
    and paginated hits.
    '''
    # TODO: use paginated_list .has_next etc. to construct rel prev/next
    try:
        context = {}
        cr = CategoryResult(request)
        response_dict = cr.get_response()
        facet_dict = cr.get_facets(response_dict)
        hit_dict = cr.get_paginated_hits(response_dict)   
        context = {
            'category': 'Category',
            'breadcrumb_obj': response_dict.get('breadcrumb'), 
            'sort_by_label': response_dict.get('sort_by_label'),
            'filtered_tokens': response_dict.get('filtered_tokens'),
            'pagination_qs': response_dict.get('pagination_qs'),
            'sort_dict': response_dict.get('sort_dict'),   
        }
        context.update(facet_dict)
        context.update(hit_dict)
    except Exception as e:
        # TODO: is raising 404 here the proper thing to do?
        msg = 'Failed to get CategoryView context. Raising 404...'
        logger.exception(msg)
        raise Http404
    return context
    