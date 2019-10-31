from elasticsearch_dsl import Search, A, Q
from elasticsearch_dsl.connections import connections
# from elasticsearch import Elasticsearch
import search_helper
from general_search import GeneralSearch
from services import decorators
# from exceptions import KeyError
from django.conf import settings
# from django.http import Http404
import copy
import re
import inspect


class FacetedSearch(object):
	'''
	Performs faceted search using Elasticsearch.
	'''

	def __init__(self, url_path, query_dict):
		self.url_path = url_path
		self.query_dict = query_dict

		# create ES connection
		connections.create_connection()
		# self.client = Elasticsearch()

	def get_sort_object(self, **kwargs):
		'''
		Return a sort object consisting of all the sorting options
		and their URLs.
		'''
		sort_labels = [
				{'Most Recent': 'most_recent'},
				{'Most Popular': 'most_popular'},
				{'Highest Rated': 'highest_rated'},
				
			]
		sort_dict_list = []
		qs = kwargs.get('current_qs_base')
		sort_prefix = '&sort_by='
		if not qs:
			qs = self.url_path
			sort_prefix = '?sort_by='
		else:
			if '/' in qs:
				qs = qs[:-1] #exclude the last slash
		for obj in sort_labels:
			for label, slug in obj.items():
				url = qs + sort_prefix + slug + '/'
				sort_dict = {label: url}
				sort_dict_list.append(sort_dict)
		# for obj in sort_dict_list:
		# 	print obj
		return sort_dict_list

	def filter_query_builder(self, unfiltered=False, **kwargs):
			'''
			Return the boolean filter query to be passed to ES.
			'''
			qs_filter_kwargs = kwargs.get('qs_filter_kwargs')
			filter_list = []
			master_filter = None
			unfiltered = False
			# sort_filter = None
			if qs_filter_kwargs:
				for filter_type in qs_filter_kwargs:
					if filter_type == 'sort_by':
						# TODO: handle sort
						# sort_field = kwargs.get('sort_field')
						# sort_filter = [Q("term", **sort_field)]
						pass
					else:
						filter_dict_list = qs_filter_kwargs[filter_type]
						for filter_dict in filter_dict_list:
							for filter_field, filter_name in filter_dict.items():
								# e.g. filter_param:  {'brand.raw': u'Apple'}
								filter_param = {filter_field: filter_name}
								q = Q("term", **filter_param)
								filter_list.append(q)
			if filter_list:
				try:
					if len(filter_list) == 1:
						# one filter parameter
						master_filter = filter_list[0]
					else:
						# one or more filter parameters
						for i in range(len(filter_list) - 1):
							if master_filter:
								if unfiltered:
									master_filter = master_filter | filter_list[i+1]
								else:
									master_filter = master_filter & filter_list[i+1]
							else:
								if unfiltered:
									master_filter = filter_list[i] | filter_list[i+1]
								else:
									master_filter = filter_list[i] & filter_list[i+1]
				except:
					# ignore any index errors
					pass
			return master_filter

	def get_response(self, s, no_hits=False):
		hit_list = []
		MAX_HITS = 1999
		count = s.count()
		if count > MAX_HITS:
		    response = s[:MAX_HITS].execute()
		else:
		    response = s[:count].execute()	
		if no_hits:
			return response	
		for hit in response: 
			hit_list.append(hit)
		return response, hit_list

	def get_qs_tokens(self, key=None, filtered_tokens=False):
		'''
		Return a tokenized querystring. 
		'''
		tokens = []
		all_tokens = []
		if key in self.query_dict:
			string = self.query_dict.getlist(key)[0]
			tokens = string.replace('/', ' ').replace('~', ' ').split()
		if filtered_tokens:
			# Get all the tokens, regardless of the key 
			for obj in self.query_dict:
				new_string = self.query_dict[obj]
				new_tokens = new_string.replace('/', ' ').replace('~', ' ').split()
				all_tokens += new_tokens[:]
			return all_tokens
		return tokens

	def filtered_tokens(self):
		'''
		Return the names of all the filtered tokens.
		'''
		slug_tokens =  self.get_qs_tokens(filtered_tokens=True)
		name_tokens = []
		for slug in slug_tokens:
			name = self.get_reverse_token(slug, name_requested=True)
			name_tokens.append(name)
		return name_tokens


	def get_reverse_token(self, token, slug_requested=False, name_requested=False):
		'''
		Return the reverse of the given token. If the name is given, return the 
		slug and vice versa.
		'''
		reverse_token = ''
		if slug_requested:
			gs = GeneralSearch(name=token)
			response = gs.search_slug()
			# response = general_search.search_slug(name=token)
			if response:
				for hit in response:
					reverse_token = hit.slug
		elif name_requested:
			gs = GeneralSearch(slug=token)
			response = gs.search_slug()
			# response = general_search.search_slug(slug=token)
			if response:
				for hit in response:
					reverse_token = hit.name
		return reverse_token

	def get_facet_breadcrumb(self, raw_crumbs):
		'''
		Return a breadcrumb dictionary object, where the crumb name is the key 
		and the url is the value. Include a left margin offset for each crumb object in
		the breadcrumb. This will be used for indentation in the template. 

		Return object example:
			url: browse-topics/a/b/c/
			raw_crumbs =
						[
							{'A': 'a/'},
							{'B': 'a/b/'},
							{'C': 'a/b/c/'},
						]
			processed_crumbs = 
						[	
							{'All Topics': 'topics/'},
							{'A': 'topics/a/'},
							{'B': 'topics/a/b/'},
							{'C': 'topcis/a/b/c/'},
						]
		'''

		# TODO: both the raw and processed look the same. Do we need this function? 


		processed_crumbs = []
		margin_offset = []
		indentation = 0
		crumb_dict = {'All Topics': 'topics/'}
		cumulative_slug = 'topics/'
		processed_crumbs.append(crumb_dict)
		margin_offset.append(indentation)
		if raw_crumbs:
			for dict_obj in raw_crumbs:
				for key, value in dict_obj.items():
					cumulative_slug += value + '/'
					indentation += 20 # pixels
					crumb_dict = {key: cumulative_slug}
					processed_crumbs.append(crumb_dict)
					margin_offset.append(indentation)
		return zip(processed_crumbs, margin_offset)


	def qs_parser(self):
		'''
		Tokenize a querystring and return a kwargs dictionary containing 
		the appropriate data structure for each filtering mechanism. 

		A query_dict can have multiple filters in it. 
		E.g.: filter_brand: samsung_apple_google 
			  filter_color: green_black_orange
			  sort_by: most_popular 

		Return value:
		filter_kwargs = [ 
			{'brand.raw': 'Samsung'},
			{'color.raw': 'Black'},
			{'color.raw': 'Orange'},
		]
		'''
		sort_by = ''
		sort_label = ''
		user_sorted = ''
		sort_field = {}
		filter_kwargs = {}
		if self.query_dict:
			for filter_type in self.query_dict:
				filter_dict_list = []
				querystring = self.query_dict.getlist(filter_type)[0]
				if filter_type == 'sort_by':
					if '/' in querystring:
						querystring = querystring[:-1] #remove the forward slash
					sort_by, sort_field, sort_label, user_sorted = \
						self.set_sorting(sorting_slug=querystring)
				else:
					filter_field = filter_type + '.raw'
					slug_tokens = self.get_qs_tokens(key=filter_type)
					for slug in slug_tokens:
						name = self.get_reverse_token(slug, name_requested=True)
						filter_dict = {filter_field: name}
						filter_dict_list.append(filter_dict)
				if filter_type !='sort_by':
					filter_kwargs[filter_type] = filter_dict_list

		qs_objects = {
			'sort_by': sort_by,
			'sort_label':  sort_label,
			'sort_field': sort_field,
			'filter_kwargs': filter_kwargs,
			'user_sorted': user_sorted,
		}
		return qs_objects

	def set_sorting(self, sorting_slug=None, default=False):
		'''
		Return the sort field, sort label, and sort_by slug for 
		user-selected sorting. 
		'''
		sort_fields = {
				'highest_rated': 'rating',
				'most_popular': 'view_count',
				'most_recent': 'date_created',
		}
		sort_labels = {
				'highest_rated': 'Highest Rated',
				'most_popular': 'Most Popular',
				'most_recent': 'Most Recent',
		}
		sort_by = ''
		sort_label = ''
		sort_field = ''
		user_sorted = False
		if 'sort_by' in self.query_dict:
			self.query_dict = self.query_dict.copy()
			sort_by = self.query_dict.pop('sort_by')[0]
			user_sorted = True
			if '/' in sort_by:
				sort_by = sort_by[:-1]
			sort_field = sort_fields[sort_by]
			sort_label = sort_labels[sort_by]
		return sort_by, sort_field, sort_label, user_sorted

	def get_url_tokens(self):
		'''
		Return a tokenized version of the url. 
		'''
		url_tokens = self.url_path.replace('/', ' ').split()
		return url_tokens
	def url_parser(self):
		'''
		Parse the url and construct a list consisting of unslugified strings,
		aggregation level, and current level.

		E.g.:
		url_path = /baby-products/nursery/bedding/
		cat_filter_list = [
						{level_0.raw: u'Baby Products'},
						{level_1.raw: u'Nursery'},
					]
		agg_level_str = level_2

		Aggregation is done on the children of the current level (level 2) so 
		it should always be one level after. (Level_2 actually doesn't exist. 
		We've limited the max depth of our hiearchies to 2 for SEO reasons).
		'''
		# url_tokens = self.url_path.replace('/', ' ').split()
		url_tokens = self.get_url_tokens()
		count = len(url_tokens)
		agg_level = 0
		cat_filter_list = []
		raw_crumbs = []
		agg_level = count - 1 # level to aggregate on
		for i in range(count):
			# prevent aggregating once we've reached a terimnal node
			if url_tokens[-1] == 'o':
				url_tokens.pop(-1)
				# url_tokens.pop(-2)
				agg_level = 1
			try:
				if url_tokens[i] != 'topics':
					token_level = i - 1 # token level in the hierarchy 
					level_str = 'level_' + str(token_level)
					unslugified = self.get_reverse_token(url_tokens[i], name_requested=True)
					crumb_dict = {unslugified: url_tokens[i]}
					param_dict = {level_str: unslugified}
					cat_filter_list.append(param_dict)


					# print '-------in url_parser------'
					# print 'param_dict: ', param_dict 
					# print 'url_tokens[i]: ', url_tokens[i]
					# print '-----------------'


					raw_crumbs.append(crumb_dict)
			except:
				# popping the list would cause index out of range error
				pass
		agg_level_str = 'level_' + str(agg_level)
		return cat_filter_list, raw_crumbs, agg_level_str

	def url_builder(self, param_dict):
		'''
		Return a slugified url substring. Use an indexed set of slugs rather
		than slugifying it every time to construct the url. 

		E.g.
		param_dict: {level_0: u'Baby Products'}
		slug: /baby-products/ 

		'''
		slug = ''
		if param_dict:
			for key, value in param_dict.items():
				slug = self.get_reverse_token(value, slug_requested=True)
				slug += '/'
		return slug


	def get_current_qs(self, base=False, **kwargs):
		'''
		Return the current querystring.

		E.g. 
			Available filter types: brand, color, condition
			current_qs: ?brand=a~b~c&color=r~g~b&condition=n~o~u/
		'''
		current_qs = ''
		user_sorted = kwargs.get('user_sorted')
		ft_slug_tokens = [] # slugs under a given filter type 
		if self.query_dict:
			sorted_keys = []
			for key in self.query_dict:
				sorted_keys.append(key)
			sorted_keys = sorted(sorted_keys)
			current_qs = '?' + sorted_keys[0] + '='
			for i in range(len(sorted_keys)):
				key = sorted_keys[i]
				ft_slug_tokens = self.get_qs_tokens(key=key)
				string = ''
				for j in range(len(ft_slug_tokens)):
					token = ft_slug_tokens[j]
					if j == 0:
						current_qs += token 
					else:
						current_qs += '~' + token
				if key != sorted_keys[-1]:
					current_qs += '&'
				try:
					current_qs += sorted_keys[i+1] + '='
				except:
					pass

			current_qs += '/'
		current_qs_base = copy.deepcopy(current_qs)
		kwargs['current_qs_base'] = current_qs_base
		# if base:
		# 	return current_qs_base
		if user_sorted:
			# append sorting querstyring to current_qs
			sort_by = kwargs.get('sort_by')
			if current_qs:
				current_qs = current_qs[:-1] + '&' + 'sort_by=' + sort_by + '/'
			else:
				current_qs = '?sort_by=' + sort_by + '/'
		kwargs['current_qs'] = current_qs
		return kwargs

	def qs_builder(self, **kwargs):
		'''
		Return a list of dictionaries where the key is the filter type
		and the value is its querystring. 

		This function is called asfter ES has built aggregations. 

		The implementation here resembles that of overstock.com. Doing so this
		way allows us to bypass using any Javascript. In theory this should improve 
		the overall speed of the website and make it easy for SEO. 

		E.g. 
		Filtered object (i.e. the bucket name): Samsung 
		querystring: /?brand=samsung 

		Return object:
			If no existing filter:
			{
				u'Samsung': '/?brand=samsung',
				u'Apple': '/?brand=apple',
				u'Google': /?brand=google',
			}

			Let's say there's an existing filter on Samsung. The return object 
			should look like this:
			{
				u'Samsung': '' ,
				u'Apple': '/?brand=samsung~apple',
				u'Google': /?brand=samsung~google',
			}

			If existing filter on Samsung and Apple:
			{
				u'Samsung': '?/brand=apple',
				u'Apple': '/?brand=samsung',
				u'Google': /?brand=samsung~apple~google',
			}

			What all of this means is that clicking on an already-filtered 
			parameter is the equivalent of removing it from the querystring.
			  
		'''
		response = kwargs.get('response')
		kwargs = self.get_current_qs(**kwargs)
		kwargs = self.get_agg_fields(names=True, **kwargs)
		agg_name_list = kwargs.get('agg_name_list')
		current_qs = kwargs.get('current_qs')
		qs_dict = {}
		# try:
		for i in range(len(agg_name_list)):
			agg_name = agg_name_list[i]
			qs_skeleton = '?' + agg_name + '=/' # e.g. '?brand=/'
			try:
				buckets = response.aggregations[agg_name]
				for bucket in buckets:
					filter_name = bucket.key
					filter_slug = self.get_reverse_token(filter_name, slug_requested=True)
					if current_qs:
						# '?brand=a~b/'' ==> '?brand=b' if filter_slug == a
						new_qs = self.prune_qs(current_qs, filter_slug)
						new_qs = self.clean_qs(new_qs)
						if new_qs == current_qs:
							new_qs = self.insert_filter_slug(new_qs, filter_slug, agg_name)
							if not new_qs:
							 	# '?brand=a/' ==> '?brand=a&color=b/'
								new_qs += current_qs[:-1] + '&' + agg_name + '=' + \
										filter_slug + '/'
								if 'sort_by' in new_qs:
									new_qs = self.shuffle_qs(new_qs)
						elif new_qs == qs_skeleton:
							# '?brand=a' ==> '?brand=/' ==> '' if filter_slug == a
							new_qs = '' 
					else:
						new_qs = '?' + agg_name + '=' + filter_slug + '/'
					qs_dict[filter_name] = new_qs
			except:
				# ignore KeyError issues on /all-reveiw-topics/
				pass
		kwargs['qs_dict'] = qs_dict
		return kwargs

	def shuffle_qs(self, qs):
		'''
		Rearrange the order of filter parameters in the querystring.
		We always want the sort paramter to appear at the end of the qs.
		'''
		qs_copy = copy.deepcopy(qs)
		match = re.findall(r'sort_by=[\w]+', qs_copy)[0] # we should only get a single match
		qs_copy = qs_copy.replace(match, '') 
		qs_copy = self.clean_qs(qs_copy, sorted_qs=True)
		qs_copy = qs_copy[:-1] + '&' + match + '/'
		return qs_copy

	def insert_filter_slug(self, qs, slug, agg_name):
		'''
		Return a querystring after appending the slug after its filter
		type.
		'''
		qs_copy = copy.deepcopy(qs)
		agg_name_index = qs.find(agg_name)
		offset = agg_name_index + len(agg_name + '=')
		string = ''
		if agg_name in qs:
			string = qs_copy[:offset] + slug + '~' + qs_copy[offset:]
		return string

	def prune_qs(self, qs, slug):
		'''
		Return a pruned querystring after removing 
		any substring of qs matching slug. 
		'''
		new_qs = qs.replace(slug, '').replace('=~', '=').replace('~~', '~').\
				replace('~&', '&')
		return new_qs

	def clean_qs(self, qs, sorted_qs=False):
		'''
		Return a cleaned querystring.

		A querystring is considered 'dirty' if it has any of the following 
		substrings in it:
			'?filter_type=&', '&filter_type=&', '&filter_type=/

		A sorted qs may have some artifacts after shuffling:
		E.g: &&, ?&, &/

		This can happen after removing the last filter slug from the 
		querystring of a given filter type.  

		'''
		qs_copy = copy.deepcopy(qs)
		matches = re.findall(r'\?[\w]+=&|&[\w]+=&|&[\w]+=\/', qs)
		pattern1 = re.compile('\?[\w]+=&')
		pattern2 = re.compile('&[\w]+=&')
		pattern3 = re.compile('&[\w]+=\/')
		if sorted_qs:
			if '&&' in qs_copy:
				qs_copy = qs_copy.replace('&&', '&')
			elif '?&' in qs_copy:
				qs_copy = qs_copy.replace('?&', '?')
			if '&/' in qs_copy:
				qs_copy = qs_copy.replace('&/', '/')
		try:
			for match in matches:
				if pattern1.match(match):
					qs_copy = qs_copy.replace(match, '?')
				elif pattern2.match(match):
					qs_copy = qs_copy.replace(match, '&')
				elif pattern3.match(match):
					qs_copy = qs_copy.replace(match, '/')
		except:
			pass 
		return qs_copy

	def bucket_builder(self, **kwargs): 
		'''
		Create a structured bucket list consisting of the name of each bucket, its 
		item count, and its url. 

		Return obj structure:

		Category bucket list: [{level_name: [doc_count, bucket_url]}, ...]
		Filter bucket list: handled by a separate function
		
		E.g.
		Category bucket:
			{u'Baby Products': [586, /baby-products/]}

			At a deeper level:
			{u'Bedding': [12, /baby-products/nursery/bedding]}

		'''
		cat_filter_list = kwargs.get('cat_filter_list')
		current_level = kwargs.get('current_level')
		next_agg_level = kwargs.get('next_agg_level')
		response = kwargs.get('response')
		is_user_filtered = kwargs.get('is_user_filtered')
		sort_by = kwargs.get('sort_by')
		processed_buckets = {}
		user_sorted = False
		kwargs = self.get_aggregations(**kwargs)
		aggregation_list = kwargs.get('aggregation_list')
		# url_prefix = 'topics/' #+ self.url_path
		url_prefix = self.url_path
		# url_tokens = self.url_path.replace('/', ' ').split()
		url_tokens = self.get_url_tokens()
		# if url_tokens[0] == 'topics':
		# 	# exclude the 'topics' slug from the prefix
		# 	url_prefix = ''
		# 	for i in range(len(url_tokens)):
		# 		if i > 0:
		# 			url_prefix += url_tokens[i] + '/' 
		kwargs['url_prefix'] = url_prefix
		kwargs = self.qs_builder(**kwargs)
		current_qs = kwargs.get('current_qs')
		# print '-----------------'
		# print 'url_prefix outside ', url_prefix
		# print '---------------------'
		for agged_dict in aggregation_list:
			for agged_name, buckets in agged_dict.items():
				# only handle the category aggregation
				if agged_name == 'category':
					bucket_list = []
					for bucket in buckets:
						param_dict = {current_level: bucket.key} 
						url_suffix = self.url_builder(param_dict)
						if bucket.doc_count == 1:
							# the facet container disappears on the front-end if
							# a bucket with a count of 1 is clicked; we don't 
							# want this to happen. 
							# print 'url_suffix: ', url_suffix
							url_tokens = self.get_url_tokens()
							# print 'url_tokens in bb: ', url_tokens
							if url_tokens[-1] == 'o':
								# there's an existing o flag
								new_url_path = self.url_path.split(url_tokens[-2])[0]
								url_prefix = new_url_path
								url_suffix = ''
								# print 'new prefix: ', url_prefix
								# self.url_path = new_url_path + '/random/'
							else:
								url_suffix = self.url_builder(param_dict) + 'o/'
								# print 'url_suffix in else: ', url_suffix

							
						if not url_prefix:
							url = '/' + url_suffix + current_qs
						else:
							url = url_prefix + url_suffix + current_qs

						
						dict_value = [bucket.doc_count, url]
						bucket_dict = {bucket.key: dict_value}

						# print 'bucket_dict: ', bucket_dict
						# print 'url_prefix: ', url_prefix
						# print 'url_suffix: ', url_suffix
						# print '------------'
						bucket_list.append(bucket_dict)
						processed_buckets[agged_name] = bucket_list
						kwargs['processed_buckets'] = processed_buckets
		return kwargs

	def get_aggregations(self, **kwargs):
		'''
		Return a list containing all the aggegations in the ES response
		object.
		'''
		aggregation_list = []
		response = kwargs.get('response')
		kwargs = self.get_agg_fields(names=True, **kwargs)
		agg_name_list = kwargs.get('agg_name_list')
		cat_buckets = response.aggregations['category']
		agg_dict = {'category': cat_buckets}
		aggregation_list.append(agg_dict)
		try:
			for name in agg_name_list:
				agg_dict = {name: response.aggregations[name]}
				aggregation_list.append(agg_dict)
		except:
			pass
		kwargs['aggregation_list'] = aggregation_list
		return kwargs


	def filter_bucket_builder(self, unfiltered=False, **kwargs):
		'''
		Return processed buckets for filters received from a GET request,
		i.e., through query_dict.  
		'''
		response = kwargs.get('response')
		url_prefix = kwargs.get('url_prefix')

		processed_buckets = kwargs.get('processed_buckets')
		qs_dict = kwargs.get('qs_dict')
		kwargs = self.get_agg_fields(names=True, **kwargs)
		agg_name_list = kwargs.get('agg_name_list')
		try:
			for agg_name in agg_name_list:
				bucket_list = []
				buckets = response.aggregations[agg_name]
				for bucket in buckets:
					bucket_name = bucket.key
					qs_url = qs_dict[bucket_name]
					full_url = url_prefix + qs_url
					dict_value = [bucket.doc_count, full_url]
					# print 'calling function: ', inspect.stack()[1][3]
					bucket_dict = {bucket_name: dict_value}
					bucket_list.append(bucket_dict)
					processed_buckets[agg_name] = bucket_list
					# print '---in filter bb------'
					# print 'bucket_dict: ', bucket_dict
					# print '---------'
		except:
			# necessary when no aggregations have been made
			pass
		return kwargs

	def exclusion_query_builder(self, s_unfiltered):
		'''
		Return filter queries to be excluded from ES search. 
		'''
		filter_kwargs = self.qs_parser() 
		d = []
		for f_key, f_value in filter_kwargs.items():
			for f_dict in f_value:
				d.append(f_dict)
		for f_dict in d:
			for key, value in f_dict.items():
				exclusion_term = {key: value}
				s_unfiltered = s_unfiltered.query('bool', filter=[~Q('term', **exclusion_term)])
		return s_unfiltered
		

	def process_unfiltered(self, **kwargs):
		'''
		Return a search object with an unfiltered search query.  
		'''
		kwargs = self.agg_query_builder(**kwargs)
		s = kwargs.get('s')
		# s = self.exclusion_query_builder(s)
		user_filters = self.filter_query_builder(unfiltered=True, **kwargs)
		s = s.query('bool', filter=user_filters)
		search_helper.pretty_print(s.to_dict())
		response = self.get_response(s, no_hits=True) 
		kwargs['response'] = response
		filtered_buckets = kwargs.get('processed_buckets')
		kwargs =  self.bucket_builder(**kwargs)
		kwargs = self.filter_bucket_builder(**kwargs)
		unfiltered_buckets = kwargs.pop('processed_buckets')
		merged_buckets = {key: value + unfiltered_buckets[key] for \
							key, value in filtered_buckets.iteritems()}
		kwargs['processed_buckets'] = merged_buckets
		return kwargs


	def staging(self):
		'''
		Return a dictionary consisting of the various elements of a search query
		to be used in the final query sent to Elasticsearch. 
		'''

		cat_filter_list, raw_crumbs, agg_level = self.url_parser()
		next_agg_level = int(agg_level[-1]) + 1
		kwargs = {
				'cat_filter_list': cat_filter_list,
				'raw_crumbs': raw_crumbs,
				'agg_level': agg_level,
				'next_agg_level': next_agg_level,
			}

		response_dict = {} 
		brand_cat_filter_params = []
		cat_filter_params = [] # category filters
		current_level = 0
		breadcrumb = []
		cat_filter_terms = []
		is_user_filtered = False
		qs_objects = self.qs_parser()
		
		kwargs['qs_filter_kwargs'] = qs_objects.get('filter_kwargs')
		kwargs['sort_by'] = qs_objects.get('sort_by')
		kwargs['sort_field'] = qs_objects.get('sort_field')
		kwargs['sort_label'] = qs_objects.get('sort_label')
		kwargs['user_sorted'] = qs_objects.get('user_sorted')
		if kwargs['qs_filter_kwargs']:
			is_user_filtered = False
		
		if cat_filter_list:
			breadcrumb = self.get_facet_breadcrumb(raw_crumbs)
			for param_dict in cat_filter_list:
				for level_num, level_name in param_dict.items():
					filter_param = {level_num + '.raw': level_name}
					prev_level = int(level_num[-1])
					cat_filter_params.append(filter_param)
			current_level = prev_level + 1

		response_dict['breadcrumb'] = breadcrumb
		kwargs['current_level'] = current_level
		kwargs['is_user_filtered'] = is_user_filtered
		kwargs['cat_filter_params'] = cat_filter_params
		kwargs['response_dict'] = response_dict
		return kwargs
	def get_agg_fields(self, names=False, fields=False, **kwargs):
		'''
		Return aggregation fields and names.
		'''
		# print 'calling function: ', inspect.stack()[1][3]
		agged_qs_list = []
		agg_name_list = []
		default_agg_list = [
				{'brand': 'brand.raw'},
				{'color': 'color.raw'},
				{'condition': 'condition.raw'},
			]
		if names:
			# get the keys
			for agg_dict in default_agg_list:
				for key in agg_dict:
					agg_name_list.append(key)
			kwargs['agg_name_list'] = agg_name_list
		if fields:
			# get the key-value pairs
			kwargs['agg_field_list'] = default_agg_list 
		if self.query_dict:
			for key in self.query_dict:
				if key != 'sort_by':
					agg_name = key
					agg_field = key + '.raw'
					agg_dict = {agg_name: agg_field}
					agged_qs_list.append(agg_dict)
			kwargs['agged_qs_list'] = agged_qs_list
		return kwargs

	def agg_query_builder(self, **kwargs):
		'''
		Return a search object with aggregation fields applied.
		'''
		BUCKET_SIZE = kwargs.get('BUCKET_SIZE')
		s = kwargs.get('s')
		kwargs = self.get_agg_fields(fields=True, **kwargs)
		agg_field_list = kwargs.get('agg_field_list')
		for agg_dict in agg_field_list:
			for agg_name, agg_field in agg_dict.items():
				b = A('terms', size=BUCKET_SIZE, field=agg_field)
				s.aggs.bucket(agg_name, b)
		kwargs['s'] = s
		return kwargs

			
	@decorators.validate_faceted_url
	def search(self):
		'''
		Return faceted search results consisting of the default category 
		aggregation and or user-submitted filters. 
		'''
		kwargs = self.staging()
		agg_level = kwargs.get('agg_level')
		cat_filter_params = kwargs.get('cat_filter_params')
		brand_cat_filter_params = kwargs.get('brand_cat_filter_params')
		is_user_filtered = kwargs.get('is_user_filtered')
		response_dict = kwargs.get('response_dict')
		agg_lvl_int = int(agg_level[-1])
		# if agg_lvl_int > 2:
		# 	agg_level = agg_level[:-1] + str(2)
		# 	agg_lvl_int = 2
		sort_by_extracted = None
		# print 'self.query_dict: ', self.query_dict 

		# set the max number of buckets to retrieve
		BUCKET_SIZE = 400
		kwargs['BUCKET_SIZE'] = BUCKET_SIZE

		s = Search(index='article')
		agg_on_field = agg_level + '.raw'
		cat_lv_dict = {'field': agg_on_field}

		a = A('terms', size=BUCKET_SIZE, **cat_lv_dict)
		s.aggs.bucket('category', a)
		if cat_filter_params:
			# TODO: sort needs to be applied somewhere 
			for filter_param in cat_filter_params:
				# print ''
				# print filter_param
				# print ''
				s = s.filter('term', **filter_param)
		s_unfiltered = copy.deepcopy(s) 
		kwargs['s_unfiltered'] = s_unfiltered
		try:
			# Aggregate on fields for users to filter on 
			if agg_lvl_int > 0:
				kwargs['s'] = s
				kwargs = self.agg_query_builder(**kwargs)
			else:
				# enable category aggregation on all levels but disable 
				# user filtering on level_0
				is_user_filtered = False
		except:
			pass

		if 'qs_filter_kwargs' in kwargs:
			sort_field = kwargs.get('sort_field')
			if sort_field:
				s = s.sort('date_created') # TODO: sort on sort_field once all the fields are available
				# s = s.sort(sort_field) 
			else:
				s = s.sort('date_created')

			user_filters = self.filter_query_builder(**kwargs)
			if user_filters:
				s = s.query('bool', filter=user_filters)
			

		
		#TODO: for debugging
		if settings.DEBUG:
			search_helper.pretty_print(s.to_dict())

		response, hit_list = self.get_response(s)
		response_dict['hit_list'] = hit_list
		kwargs['response'] = response
		kwargs =  self.bucket_builder(**kwargs)
		kwargs = self.filter_bucket_builder(**kwargs)
		sort_obj = self.get_sort_object(**kwargs)
		pagination_qs = kwargs.get('current_qs')
		if pagination_qs:
			# remove the final forward slash
			pagination_qs = pagination_qs[:-1]


		# TODO: get rid of process_unfiltered and all related code (as of 7/16/17)
		# TODO: enable this once the logic of navigating 
		# filtered and unfiltered parameters is clear 
		# if self.query_dict:
		# 	kwargs['s'] = s_unfiltered
		# 	kwargs = self.process_unfiltered(**kwargs)

		agg_names = []
		filtered_buckets = kwargs.get('processed_buckets')
		try:
			for agged_name, buckets in filtered_buckets.items():
				agg_names.append(agged_name)
				response_dict[agged_name] = buckets
		except:
			pass
		filtered_tokens = self.filtered_tokens()
		response_dict['filtered_tokens'] = filtered_tokens
		response_dict['agg_names'] = agg_names
		response_dict['sort_dict'] = sort_obj
		response_dict['sort_by_label'] = kwargs.get('sort_label')
		response_dict['pagination_qs'] = pagination_qs
		# print '------------in faceted search ---------------'
		# for val in response_dict:
		# 	print val, response_dict[val]
		# print '------------in faceted search ---------------'

		return response_dict