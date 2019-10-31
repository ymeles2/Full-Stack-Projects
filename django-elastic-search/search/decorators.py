from django.http import Http404
from general_search import GeneralSearch

def validate_faceted_url(function):
	'''
		Validate the URL. A user could have manually modified the URL to see its 
		behavior. In such cases, we want to respond only if the combination of 
		changes results in a valid URL. A URL under /browse-topics/ is considered
		valid only if all the tokens in the modified URL are found in 
		the slug index. We do not care if their combination results in a valid 
		search query at this stage.'''

	def validate_url(instance):
		# TODO: log validation failures
		url_tokens = instance.url_path.replace('/', ' ').split()
		num_tokens = len(url_tokens)
		count = 0
		for i in range(num_tokens):
			gs = GeneralSearch(slug=url_tokens[i])
			response = gs.search_slug()
			if response:
				count += 1
		if count == num_tokens or url_tokens[0] == 'all-review-topics':
			# all the tokens are found in the slug index
			instance = modify_url(instance)
			return function(instance)
		else:
			# raise 404
			raise Http404
	def modify_url(instance):
		'''
		Modify the url if the forward slash is missing from the end or 
		there is more than one.
		'''
		url_tokens = instance.url_path.replace('/', ' ').split()
		new_url = ''
		for token in url_tokens:
			new_url += token + '/'
		instance.url_path = '/' + new_url
		return instance		

	return validate_url
