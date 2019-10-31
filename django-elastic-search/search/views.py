from django.views import generic
import fooreviews.seo.seo as seo
import search.search_data.searchlistview as searchlistview
import search.search_data.categorylistview as categorylistview


class SearchListView(generic.ListView):
    template_name = 'search/search.html'
    def get_queryset(self):
    	return None

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context.update(searchlistview.search(self.request))
        context.update({'view_type': 'SearchListView'})
        context = seo.SEOMetaTags(context).get_meta_tags()
        return context

class CategoryListView(generic.ListView):
    template_name = 'fooreviews/category.html'
    def get_queryset(self):
        '''
        Return an empty queryset; we'll make the actual db
        queries in get_context_data; ListView must return a queryset of
        some kind.
        '''
        return None
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context.update(categorylistview.get_category_context(self.request))
        context.update({'view_type': 'CategoryListView'})
        context = seo.SEOMetaTags(context).get_meta_tags()
        return context
