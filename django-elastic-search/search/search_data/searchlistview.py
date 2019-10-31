from search.general_search.general_search import GeneralSearch
import search.search_helper as s_helper
# from django.http import HttpRequest, Http404
# from django.http import HttpResponseServerError
import services.loggers as loggers
logger = loggers.Loggers(__name__).get_logger()

class SearchResult(object):
	'''
	Handles general user search queries (as apposed to faceted search).
	'''
	def __init__(self, request, **kwargs):
		self.request = request

	def get_search_results(self):
		kwargs = {}
		count = 0
		is_paginated = False
		single_result = False
		search_result = None
		paginated_list = None
		if self.request.method == 'GET' and 'q' in self.request.GET:
			q = self.request.GET['q']
			if q is not None and q != '':
				search_result = self.get_search_hits(q=q)
				if search_result:
					count = len(search_result)
					if count > 10:
						is_paginated = True
					if  count == 1 :
						single_result = True
				else:
					#valid search returned no result
					pass
			else:
				#invalid/empty form submission
				pass  
			kwargs['q'] = q
		if search_result:
			page = self.request.GET.get('page')
			paginated_list = s_helper.custom_paginator(search_result, page)
		result_dict = {
				'count': count,
				'is_paginated': is_paginated,
				'single_result': single_result,
				'paginated_list': paginated_list,
				'search_results': True,
			}
		kwargs.update(result_dict)
		return kwargs

	def get_search_hits(self, q=None, all_articles=False):
	    '''
	    Return search hits from ES. Get all articles sorted by date if 
	    all is self.requested.  
	    '''
	    hit_list = []
	    if all_articles:
	        gs = GeneralSearch()
	        hits = gs.get_all_articles()
	    elif q:
	        gs = GeneralSearch(query=q)
	        hits = gs.search_by_query()
	    if hits:
	        hit_list = []
	        for hit in hits:
	            hit_list.append(hit)
	    return hit_list

def search(request):
	try:
		sr = SearchResult(request)
		context = sr.get_search_results()
		return context
	except Exception as e:
		msg = '{}: {}'.format(type(e).__name__, e.args[0])
		logger.exception(msg)
		# return HttpResponseServerError()



