from elasticsearch_dsl import Search, A, Q
from elasticsearch_dsl.connections import connections
import search.search_helper as search_helper
from search.general_search.general_search import GeneralSearch
from services import decorators
from django.conf import settings
import copy
import re
import services.loggers as loggers
logger = loggers.Loggers(__name__).get_logger()


class FacetedSearch(object):
	'''
	Performs faceted search using Elasticsearch.
	'''

	def __init__(self, url_path, query_dict):
		self.url_path = url_path
		self.query_dict = query_dict

		# create ES connection
		connections.create_connection()

	def filter_query_builder(self, unfiltered=False, **kwargs):
			'''
			Return the boolean filter query to be passed to ES.
			'''
			qs_filter_kwargs = kwargs.get('qs_filter_kwargs')
			filter_list = []
			master_filter = None
			unfiltered = False
			if qs_filter_kwargs:
				for filter_type in qs_filter_kwargs:
					if filter_type == 'sort_by':
						# Ignore this; sorting is handled separately
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
				except Exception as e:
					msg = '{}: {}'.format(type(e).__name__, e.args[0])
					logger.exception(msg)
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
			if response:
				for hit in response:
					reverse_token = hit.slug
		elif name_requested:
			gs = GeneralSearch(slug=token)
			response = gs.search_slug()
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
			'qs_filter_kwargs': filter_kwargs,
			'user_sorted': user_sorted,
		}
		return qs_objects

	def set_sorting(self, sorting_slug=None, default=False):
		'''
		Return the sort field, sort label, and sort_by slug for 
		user-selected sorting. 
		'''
		sort_fields, sort_labels = self._get_faceting_fields(sorting=True)
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
		url_tokens = self.get_url_tokens()
		count = len(url_tokens)
		agg_level = 0
		cat_filter_list = []
		raw_crumbs = []
		agg_level = count - 1 # level to aggregate on
		if url_tokens[-1] == 'o':
			url_tokens.pop(-1)
			count -= 1
			agg_level = 1
		for i in range(count):
			# prevent aggregating once we've reached a terimnal node
			try:
				if url_tokens[i] != 'topics':
					token_level = i - 1 # token level in the hierarchy 
					level_str = 'level_' + str(token_level)
					unslugified = self.get_reverse_token(url_tokens[i], name_requested=True)
					crumb_dict = {unslugified: url_tokens[i]}
					param_dict = {level_str: unslugified}
					cat_filter_list.append(param_dict)
					raw_crumbs.append(crumb_dict)
			except Exception as e:
				msg = '{}: {}'.format(type(e).__name__, e.args[0])
				logger.exception(msg)
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
				except Exception as e:
					msg = '{}: {}'.format(type(e).__name__, e.args[0])
					logger.exception(msg)

			current_qs += '/'
		current_qs_base = copy.deepcopy(current_qs)
		kwargs['current_qs_base'] = current_qs_base
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

		This function is called after ES has built aggregations. 

		The implementation here resembles that of overstock.com. 

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
		# TODO: all filter_name and filter_slug values need to be indexed by ES for faceting to work
		response = kwargs.get('response')
		kwargs = self.get_current_qs(**kwargs)
		kwargs = self.get_agg_fields(names=True, **kwargs)
		agg_name_list = kwargs.get('agg_name_list')
		current_qs = kwargs.get('current_qs')
		qs_dict = {}
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
			except Exception as e:
				msg = '{}: {}'.format(type(e).__name__, e.args[0])
				logger.exception(msg)
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
		except Exception as e:
			msg = '{}: {}'.format(type(e).__name__, e.args[0])
			logger.exception(msg)
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
			{u'Baby Products': [586, /baby-products/]},
			{other siblings at this level},

			At a deeper level:
			{u'Bedding': [12, /baby-products/nursery/bedding]},
			{other siblings at this level},

		'''
		cat_filter_list = kwargs.get('cat_filter_list')
		kwargs = self.get_aggregations(**kwargs)
		aggregation_list = kwargs.get('aggregation_list')
		url_prefix = self.url_path
		url_tokens = self.get_url_tokens() 
		kwargs['url_prefix'] = url_prefix
		kwargs = self.qs_builder(**kwargs)
		for agged_dict in aggregation_list:
			for agged_name, buckets in agged_dict.items():
				params = {
						'buckets': buckets,
						 'agged_name': agged_name,
					}
				# handle category aggregation
				if agged_name == 'category':
					kwargs = self._build_cat_aggs(params, **kwargs)
		return kwargs

	def _build_cat_aggs(self, params, **kwargs):
		'''
		Build buckets for term-filtered taxonomy/category hits. These aggegations are 
		shown under the 'Category' facet in the navigaiton pane. We have limited our 
		taxonomy depth to two levels. This leaves us with the following:
			level_0: 
					Electronics,
					Appliances,
					...

			level_1 (pick Electronics):
					Laptops,
					Desktops,
					...
		'''
		buckets = params.get('buckets')
		current_level = kwargs.get('current_level')
		agged_name = params.get('agged_name')
		current_qs = kwargs.get('current_qs')
		url_prefix = kwargs.get('url_prefix')
		processed_buckets = {}
		bucket_list = []
		url = '-1'
		for bucket in buckets:
			param_dict = {current_level: bucket.key} 
			url_suffix = self.url_builder(param_dict)
			if bucket.doc_count >= 1:
				url_tokens = self.get_url_tokens()
				if len(url_tokens) > 1:
					url_suffix, url_prefix = self._set_flag(param_dict, url_prefix, url_tokens)
			if not url_prefix:
				url = '/' + url_suffix + current_qs
			else:
				url = url_prefix + url_suffix + current_qs
			dict_value = [bucket.doc_count, url]
			bucket_dict = {bucket.key: dict_value}
			bucket_list.append(bucket_dict)
			processed_buckets[agged_name] = bucket_list
			kwargs['processed_buckets'] = processed_buckets
		return kwargs

	def _set_flag(self, param_dict, url_prefix, url_tokens):
		'''
		Add 'o' flags to bucket URLs. Adding an 'o' flag means appending
		\o\ to the end of the URL. This is necessary when we're dealing with 
		taxonomy nodes that lack any children to aggregate on. Lack of aggregation 
		means there's nothing to show in the navigation pane. This is the behavior 
		we expect based on how we implemented faceting. However, it's not very 
		user friendly because users have no way of navigating back to the parent 
		taxonomy. Here, appending an 'o' flag lets us know that we are 

		NB: 'o' stands for 'one' to denote that we currently have one aggregated 
		bucket that we can click on (this has no bearing on how many documents the 
		bucket itself has as long as it's greater than 0.  

		Flag is set if the number of tokens in url_token is greater one. A single 
		token means we're at the root; setting a flag at the root effectively 
		disables aggregation farther down the tree; we don't want that.

		The approach has a problem but it's good enough for us. It'll become
		problematic if there are more than two taxonomy levels. For example,
		currently we have something like level_0=Electronics and level_1=Laptops.
		We've deliberately limited the depth for SEO and user friendliness. 
		Inreasing the depth will set a flag at level_1. If level_2 exists,
		it won't get aggregated. This gets even more complicated if different
		categories have variable taxonomy depths. We avoid all that by simply 
		requiring that all our taxonomies be two levels deep.

		What's happening?
			E.g. [1] incoming url: /topics/ 
					--> flag not set:  /topics/electronics/ 

				[2] incoming url: /topics/electronics/ 
					--> flag set to: /topics/electronics/laptops/o/
						siblings: /topics/electronics/desktops/o/
								/topics/electronics/cameras/o/
						...etc.

		What does it mean?
			Clicking on any url with the flag set shows the aggregated 
			results for that bucket.  The url changes like so:

			[3]/topics/electronics/laptops/o/ --> [4]/topics/electronics/

			The bucket display text (the url text shown) for both [3] and
			[4] is Laptops. Clickig on [4] simulates taxonomy ascension or 
			the back button and leads to [3]. At [3], we're now back to where 
			we were, i.e. the Laptops bucket is shown along with its siblings 
			as in [2]. 

		Why do it this way?
			Again, SEO and user-friendliness is a factor. By SEO, we mean allowing 
			search engines to be able to crawl the entire catalog. The behavior is 
			static but the back-end execution of it is entirely dynamic. There are 
			obviously other ways to do it but this is far more challenging and the 
			simplicity of using it in the front-end is commensurately satisfying.  
		''' 
		if url_tokens[-1] == 'o':
			# there's an existing o flag; drop the flag from the url
			new_url_path = self.url_path.split(url_tokens[-2])[0]
			url_prefix = new_url_path
			url_suffix = ''
		else:
			url_suffix = self.url_builder(param_dict) + 'o/'
		return url_suffix, url_prefix

	def get_aggregations(self, **kwargs):
		'''
		Return a list containing all the aggegations in the ES response
		object. This includes category aggregates and user filtration 
		aggregates like color, brand, and condition.
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
		except Exception as e:
			msg = '{}: {}'.format(type(e).__name__, e.args[0])
			logger.exception(msg)
		kwargs['aggregation_list'] = aggregation_list
		return kwargs


	def filter_bucket_builder(self, **kwargs):
		'''
		Return processed buckets for filters received from a GET request,
		i.e., through query_dict. 
		Filter examples: color, brand, condition 
		'''
		#TODO: We have disabled filtering for the time being. When ready, 
		# remove the return statement below and let the code execute.
		return kwargs

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
					bucket_dict = {bucket_name: dict_value}
					bucket_list.append(bucket_dict)
					processed_buckets[agg_name] = bucket_list
		except Exception as e:
			# no aggregations have been made
			msg = '{}: {}'.format(type(e).__name__, e.args[0])
			logger.exception(msg)
			pass
		return kwargs

	def _get_kwargs_qs(self, **kwargs):
		'''
		Create and return kwargs with GET querystrings. If filtering parameters are 
		present, disable user filtering on level_0 (root).

		We're disabling user filtering on level_0 because it makes no logical
		sense to allow filtering by brand, color, condition (all examples) at 
		the product domain level. Otherwise, we'll have Kenmore Microwaves
		appearing alongside Macbook Pro Retinas. (We're just being pure by 
			isolating unrelated categories from being aggregated at the 
			same time. This is different from sorting, which allows for different
			categories to appear alongside one another, which is fine.) 
		'''
		kwargs = {}
		kwargs.update(self.qs_parser())
		if kwargs['qs_filter_kwargs']:
			user_filtering_allowed = False
		return kwargs

	def _update_kwargs(self, **kwargs):
		'''
		Update kwargs with aggregation parameters and breadcrumb.
		'''
		response_dict = {}
		cat_filter_params = [] # category filters
		current_level = 0
		breadcrumb = []
		cat_filter_terms = []
		user_filtering_allowed = False
		cat_filter_list = kwargs.get('cat_filter_list')
		raw_crumbs = kwargs.get('raw_crumbs')
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
		kwargs['user_filtering_allowed'] = user_filtering_allowed
		kwargs['cat_filter_params'] = cat_filter_params
		kwargs['response_dict'] = response_dict
		return kwargs

	def staging(self):
		'''
		Return a dictionary consisting of the various elements of a search query
		to be used in the final query sent to Elasticsearch. 
		'''
		kwargs = self._get_kwargs_qs()
		cat_filter_list, raw_crumbs, agg_level = self.url_parser()
		next_agg_level = int(agg_level[-1]) + 1
		kwargs.update({
				'cat_filter_list': cat_filter_list,
				'raw_crumbs': raw_crumbs,
				'agg_level': agg_level,
				'next_agg_level': next_agg_level,
			})
		kwargs = self._update_kwargs(**kwargs)
		return kwargs

	def get_sort_dict(self, **kwargs):
		'''
		Return a sort object consisting of all the sorting options
		and their URLs.
		'''
		sort_labels = self._get_faceting_fields(sorting=True, labels=True)
		sort_dict_list = []
		qs = kwargs.get('current_qs_base')
		sort_prefix = '&sort_by='
		if not qs:
			qs = self.url_path
			sort_prefix = '?sort_by='
		else:
			if '/' in qs:
				qs = qs[:-1] #exclude the last slash
		for slug, label in sort_labels.items():
			url = qs + sort_prefix + slug + '/'
			sort_dict = {label: url}
			sort_dict_list.append(sort_dict)
		return sort_dict_list

	def get_agg_fields(self, names=False, fields=False, **kwargs):
		'''
		Define and return aggregation fields. 

		Aggregation fields are defined in search.models.AggregationField. 
		Field examples: 
				{'brand': 'brand.raw'},
				{'color': 'color.raw'},
				{'condition': 'condition.raw'}

			The key is whatever we want to call it. It's what's displayed in
			the front-end in the navigation pane and in the url. The value is the 
			only one that matters and the one Elasticsearch understands. 
			The .raw attributes tells Elasticsearch to use the untokenized version of
			the field.

			We've set up our ES index so that all indexed fields are Snowball tokenized
			with only some being Keyword tokenized as well. Keyword tokenized fields require exact
			match and thus have an ES relevance score of 0.0 or 1.0. These fields are 
			accessed through .raw notation. (Keyword tokenization is designed for terms 
			that don't make sense in isolation, .e.g 'New', 'York' are meaningless as they 
			relate to an American city but 'New York' is meaningful. On the other hand, 
			Snowball tokenization allows for getting a hit for 'New York' with a high 
			relevance score by simply searching for 'new', 'york', or 'new york'. This is
			the logic behind using both tokenization types on our fields: allow them to 
			be searchable by users but also enable us do aggregations that require exact
			match).
		
		NB: The comments throughout this module use 'brand', 'color', and 
			'condition'as aggregation field examples. These examples are obvisouly
			limited. However, the parameterization below, i.e. querying the
			fields from Elasticsearch directly, allows us to scale the number of 
			facets we can have infinitely.
		'''
		agged_qs_list = []
		agg_name_list = []
		default_agg_list = self._get_faceting_fields(aggregation=True)
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
	def _get_faceting_fields(self, aggregation=False, sorting=False, labels=False):
		'''
		Get all the available aggregation or sorting fields from Elasticsearch 
		db.
		'''
		gs = GeneralSearch()
		fields = None
		if aggregation:
			hits = gs.get_faceting_fields(aggregation=True)
			default_agg_list = []
			for hit in hits:
				default_agg_list.append({hit.agg_name: hit.agg_field})
			return default_agg_list
		elif sorting:
			hits = gs.get_faceting_fields(sorting=True)
			sort_fields = {}
			sort_labels = {}
			for hit in hits:
				sort_fields[hit.sort_slug] = hit.sort_field
				sort_labels[hit.sort_slug] = hit.sort_label
			if labels:
				return sort_labels
			return sort_fields, sort_labels
		
	def agg_query_builder(self, s, BUCKET_SIZE, **kwargs):
		'''
		Return a search object with aggregation fields applied.
		'''
		agg_level = kwargs.get('agg_level')
		agg_lvl_int = int(agg_level[-1])
		if agg_lvl_int > 0:
			kwargs = self.get_agg_fields(fields=True, **kwargs)
			agg_field_list = kwargs.get('agg_field_list')
			for agg_dict in agg_field_list:
				for agg_name, agg_field in agg_dict.items():
					b = A('terms', size=BUCKET_SIZE, field=agg_field)
					s.aggs.bucket(agg_name, b)
		return s, kwargs

	def _set_sorting(self, s, **kwargs):
		'''
		Set sorting on ES search instance.
		'''
		if 'qs_filter_kwargs' in kwargs:
			sort_field = kwargs.get('sort_field')
			if sort_field:
				s = s.sort(sort_field)  
			else:
				s = s.sort('date_created')
		return s

	def _set_bool_filtering(self, s, **kwargs):
		'''
		Set user-selecting drill down filters on ES search instance.

		Bool filtering is different from term filtering in that we 
		use logical operators to allow for a different combination of 
		filters, e.g. color, brand, condition, all at the same time. Bool 
		terms are not mutually exclusive, i.e. they can be all true, all false, 
		or a combination of true and false at any given taxonomy level.
		'''
		if 'qs_filter_kwargs' in kwargs:
			user_filters = self.filter_query_builder(**kwargs)
			if user_filters:
				s = s.query('bool', filter=user_filters)
		return s

	def _set_term_filtering(self, s, **kwargs):
		'''
		Set term filtering for category isolation. 

		Term filtering is different from bool filtering in that only a single
		term can be filtered at a time. In our particular case, we are filtering 
		on taxonomy levels. Terms are mutually exclusive, i.e. we can only be at one
		taxonomy level at a time. The level we're on (or the one the user clicked on)
		is the term we're filtering on, e.g. level_0.

		NB: It's worth noting that we're iterating filter_params below even through
		we said terms are mutually exclusive. By iterating, we're descending a taxonomy
		tree, i.e. drilling down. (Ascension is also possible but that's handled through 
		breadcrumbs and clicking on the current category agg name again (true if we're 
		at the node only), both of which just drop the last taxonomy level from the 
		filtering querystring and initiate a new search query).  
		'''
		cat_filter_params = kwargs.get('cat_filter_params')
		if cat_filter_params: 
			for filter_param in cat_filter_params:
				s = s.filter('term', **filter_param)
		return s


	def _get_search_instance(self, **kwargs):
		'''
		Instantiate and return an Elasticsearch search instance. Set the 
		maximum number of aggregation buckets to 10.

		In practical terms, bucket size is the number of siblings at a given 
		taxonomy level. As of 7/17/17, we have seven siblings on level_0 and 
		an average of nine on level_1. Electronics currently has 14 children,
		i.e. buckets, so we'll set our bucket size to 15. 
		'''
		# set the max number of buckets to retrieve
		agg_level = kwargs.get('agg_level')
		BUCKET_SIZE = 15
		s = Search(index='article')
		agg_on_field = agg_level + '.raw'
		cat_lv_dict = {'field': agg_on_field}
		a = A('terms', size=BUCKET_SIZE, **cat_lv_dict)
		s.aggs.bucket('category', a)
		return s, BUCKET_SIZE

	def _debug_pretty_print(self, s):
		#TODO: for debugging
		if settings.DEBUG:
			search_helper.pretty_print(s.to_dict())

	def _pair_aggs_bucketvals(self, **kwargs):
		'''
		Pair aggregation bucket names and bucket values. 

		Bucket names are either taxonomy level names (Electronics, Laptops, etc)
		or filter names (Brand, Color, Condition). Bucket values are url slugs 
		that a user can click on, which initiates a new search query. The search 
		query comes back to FacetedSearch and then gets processed. Once processed,
		the user sees the results for the URL they clicked on 
		but is also shown (in the navigation pane) URLs to other buckets and 
		filtering parameters applicable to the current search results.

		We've implemented faceting such that to the user, the navigation looks 
		like clicking on links to load static pages. Instead, everything is dynamic.
		By masking search queries as URL slugs and limiting the search to exhibit a very 
		specific behavior, we have eliminated the need for a complicated implementation. 
		'''
		agg_names = []
		response_dict = kwargs.get('response_dict')
		filtered_buckets = kwargs.get('processed_buckets')
		if filtered_buckets:
			for agged_name, buckets in filtered_buckets.items():
				agg_names.append(agged_name)
				response_dict[agged_name] = buckets
		return response_dict, agg_names

	def _get_pagination_qs(self, **kwargs):
		pagination_qs = kwargs.get('current_qs')
		if pagination_qs:
			# remove the final forward slash
			pagination_qs = pagination_qs[:-1]
		return pagination_qs

			
	@decorators.validate_faceted_url
	def search(self):
		'''
		Return faceted search results consisting of the default category 
		aggregation and user-selected filters, if applicable. 
		'''
		response_dict = {}
		try:
			kwargs = self.staging()

			# get search instance
			s, BUCKET_SIZE = self._get_search_instance(**kwargs)
			s =  self._set_term_filtering(s, **kwargs)

			# Aggregate on fields for users to filter on 
			s, kwargs = self.agg_query_builder(s, BUCKET_SIZE, **kwargs)
			
			# applying sorting and filtering 
			s = self._set_sorting(s, **kwargs)
			s = self._set_bool_filtering(s, **kwargs)
			
			# get search hits
			response, hit_list = self.get_response(s)
			kwargs.get('response_dict')['hit_list'] = hit_list
			kwargs['response'] = response

			# get formatted facets
			kwargs =  self.bucket_builder(**kwargs)
			kwargs = self.filter_bucket_builder(**kwargs)
			sort_dict = self.get_sort_dict(**kwargs)
			pagination_qs = self._get_pagination_qs(**kwargs)

			# update response with formatted aggregations and other values
			response_dict, agg_names = self._pair_aggs_bucketvals(**kwargs)
			filtered_tokens = self.filtered_tokens()
			response_dict.update({
					'filtered_tokens': filtered_tokens,
					'agg_names': agg_names,
					'sort_dict': sort_dict,
					'sort_by_label': kwargs.get('sort_label'),
					'pagination_qs': pagination_qs,
			})

			self._debug_pretty_print(s)
		except Exception as e:
			msg = '{}: {}'.format(type(e).__name__, e.args[0])
			logger.exception(msg)
		return response_dict

	
	

