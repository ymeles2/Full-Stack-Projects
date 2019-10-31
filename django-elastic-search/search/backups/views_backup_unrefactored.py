from django.views import generic
from django.shortcuts import render
from faceted_search import FacetedSearch
import helper
import models
import search.search_data.searchlistview as searchlistview


class SearchListView(generic.ListView):
    template_name = 'search/search.html'
    def get_queryset(self):
    	return None

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context.update(searchlistview.search(self.request))
        # count = 0
        # is_paginated = False
        # single_result = False
        # search_result = None
        # paginated_list = None
        # if self.request.method == 'GET' and 'q' in self.request.GET:
        #     q = self.request.GET['q']
        #     if q is not None and q != '':
        #         try:
        #             search_result = helper.get_search_hits(q=q)
        #             print '-----------just called helper.get_search_hits-----------'
        #             print '------------module helper------: ', helper
        #         except Exception:
        #             print 'possible TransportError----------------------- handle appropriately'
        #         if  search_result:
        #             count = len(search_result)
        #             if count > 10:
        #                 is_paginated = True
        #             if  count == 1 :
        #                 single_result = True
        #         else:
        #             #valid search returned no result
        #             pass
        #     else:
        #         #invalid/empty form submission
        #         pass  
        #     context['q'] = q
        # if search_result:
        #     page = self.request.GET.get('page')
        #     paginated_list = helper.custom_paginator(search_result, page)
        # context['count'] = count
        # context['is_paginated'] = is_paginated
        # context['single_result'] = single_result
        # context['paginated_list'] = paginated_list
        # context['search_results'] = True
        return context



class CategoryListView(generic.ListView):
    template_name = 'fooreviews/category.html'
    def get_queryset(self):
        '''
            Return an empty queryset; we'll make the actual db
            queries in get_context_data; ListView must return a queryset of
            some kind as per Django rules.
        '''
        return None
        # return models.Article.objects.none()
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        url_path = self.request.path
        query_dict = self.request.GET.copy()
        page = query_dict.get('page')
        if page:
            del(query_dict['page'])
        fs = FacetedSearch(url_path, query_dict)
        response_dict = fs.search() 
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

        # recombine the facets with category facets first
        facets = cat_facet[:] + filter_facets[:]

        article_hit_list = response_dict['hit_list']
        breadcrumb = response_dict['breadcrumb']
        sort_by_label = response_dict['sort_by_label']

        count = 0
        is_paginated = False    
        single_result = False
        paginated_list = None
        if article_hit_list:
            count = len(article_hit_list)
            if count > 10:
                is_paginated = True
            if  count == 1 :
                single_result = True
            paginated_list= helper.custom_paginator(article_hit_list, page)
        
        # TODO: use paginated_list .has_next etc. to construct rel prev/next  
        sort_dict = response_dict.get('sort_dict')
        if not sort_dict:
            sort_dict = False
        context['category'] = 'root'
        # context['paginated_list'] = article_hit_list
        context['paginated_list'] = paginated_list
        context['is_paginated'] = is_paginated
        context['single_result'] = single_result
        context['breadcrumb_obj'] = breadcrumb
        context['sort_by_label'] = response_dict.get('sort_by_label')
        context['sort_dict'] = sort_dict
        context['facets'] = facets
        context['facet_slugs'] = facet_slugs
        context['pagination_qs'] = response_dict.get('pagination_qs')
        context['category'] = 'Category'
        context['filtered_tokens'] = response_dict.get('filtered_tokens')
        return context
