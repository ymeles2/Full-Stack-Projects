
import csv
import json
import random
import re
import requests
import time

class CareerFair(object):
	'''
	Parses and outputs employer names and descriptions from the Viterbi Career 
	Gateway for a given major. 
	'''

	def __init__(self, *args, **kwargs):
		self.landing_url = kwargs.get('base')
		self.result_count = kwargs.get('count')
		self.major = kwargs.get('major')
		self.headers = self._set_header()
		if self.major:
			self.major = self.major.replace('_', ' ').lower()

		
	def get_employers(self):
		page_count = self._get_pagination()
		url_list = self._build_urls(page_count)
		response_list = []
		for url in url_list:
			response = self._get_request(url)
			response_list.append(response)
			time.sleep(5) # a 5-second delay
		self._parse_json(response_list)

	def _get_pagination(self):
		RESULTS_PER_PAGE = 20
		num_pages = self.result_count/RESULTS_PER_PAGE
		if self.result_count % RESULTS_PER_PAGE != 0:
			num_pages += 1
		return num_pages

	def _parse_json(self, responses):
		'''
		Parse the json and build a csv-friendly data structure. 

		NB: This is where we determine which columns to include or exclude from 
		the csv. Refer to the actual json (in Chrome or Firefox) and add more 
		columns in the for loop if desired. Data passed to csv must be a 
		key-value pair with 'flat' values, i.e. primitive strings or numbers 
		only.
		'''
		filtered_employers = []
		all_employers = []
		for response in responses:
			try:
				models_list = responses.json().get('models') 
				for data in models_list:
					employer_dict = {
						'company': data.get('name'),
						'positions': self._parse_list(data.get('position_types'), pos=True),
						'degrees': self._parse_list(data.get('degree_level'), degrees=True),
						'majors': self._parse_list(data.get('majors'), majors=True),
						'description': data.get('overview').encode('utf-8'),
					}
					if self._major_exists(employer_dict):
						filtered_employers.append(employer_dict)

					# unfiltered
					all_employers.append(employer_dict)
			except Exception as e:
				msg = '{}: {}'.format(type(e).__name__, e.args[0])
				print msg

		self._save_to_csv(filtered_employers, filtered=True)
		self._save_to_csv(all_employers)

	def _major_exists(self, employer_dict):
		majors = employer_dict.get('majors')
		if self.major and self.major in majors.lower():
			return True
		return False


	def _save_to_csv(self, data, filtered=False):
		filename = 'usc_viterbi_careerfair_unfiltered.csv'
		if filtered:
			major = self.major.replace(' ', '_')
			filename = filename.replace('unfiltered', 'filtered_{}'.format(major))

		# build field names	
		fields = sorted(data[0].keys())

		with open(filename, 'w') as csv_out:
			writer = csv.DictWriter(csv_out, fieldnames=fields)
			writer.writeheader()
			for row_dict in data:
				writer.writerow(row_dict)

		msg = 'Outputted file with name={}\n'.format(filename)
		print msg

	def _parse_list(self, list_data, majors=False, degrees=False, pos=False):
		'''
		'Flatten' a list object containing dictionary elements by turning them 
		into a single key-value pair, where the values are comma-separated 
		elements.
		Input:
			degrees = 
			[
				{
					"_id": 1,
					"_label": "Bachelors"
				},
				{
					"_id": 2,
					"_label": "Masters"
				},
				{
					"_id": 3,
					"_label": "PhD"
				}
			]

		Output:
			degrees = {'Bachelors, 'Masters, 'PhD'}

		'''
		data_dict = {}
		for ld in list_data:
			if majors:
				key = 'majors'
			elif degrees:
				key = 'degrees'
			elif pos:
				key = 'positions'
			if data_dict:
				data_dict[key] += ', ' + ld.get('_label')
			else:
				data_dict[key] = ld.get('_label')
		return data_dict.get(key)

	def _get_request(self, url):
		params = {'headers': self.headers}
		response = requests.get(self.landing_url, **params)
		return response
	
	def _set_header(self):
		USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
		USER_AGENT += " (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
		headers = requests.utils.default_headers()
		headers.update({'User-Agent': USER_AGENT})
		return headers

	def _build_urls(self, page_count):

		ajax_base = self._build_ajax_base()
		url_list = []
		for i in range(page_count):
			# ?js_disabled=1 is redundant; there's no js in the ajax response
			# but it's required due to accessibility issues
			url = '{}{}{}{}'.format(ajax_base, '&page=', i + 1, '?js_disabled=1')
			url_list.append(url)

		for i in range(page_count):
			random.shuffle(url_list)
		return url_list

	def _build_ajax_base(self):
		'''
		Parse out session-specific uid from the landing url and build 
		the base url for ajax requests. 

		Base url format: 'https://viterbi-usc-csm.symplicity.com/events/
								c495591c0cb4d00420fb15c629163e76/employers'
		session_uid: c495591c0cb4d00420fb15c629163
		'''
		UID_LENGTH = 32
		ajax_base = ''
		pattern = '{}{}{}'.format('\w{', UID_LENGTH, '}')
		session_uid = re.findall(pattern, self.landing_url)
		if session_uid:
			session_uid = session_uid[0]
			prefix = 'https://viterbi-usc-csm.symplicity.com/api/v2/'
			prefix += 'eventRegistration?approved=1&event='
			suffix = session_uid + '&id=' + session_uid
			ajax_base = prefix + suffix

		return ajax_base


'''
Execution: python careerfair.py example.com 168 --major chemical_engineering
		example.com: landing page (required)
		168:  result count (required)
		chemical_engineering:  major (optional)

		Landing page example: 'https://viterbi-usc-csm.symplicity.com/events/
								c495591c0cb4d00420fb15c629163e76/employers'
'''
def add_arguments(parser):
	help = 'Provide url, result count, and optional department or major. If'
	help += ' no major is provided, unfiltered results will be outputted.'
	help_m = 'Please provide a major. Replace any multi-word names with an '
	help_m += 'underscore. If more than one major is provided, only the '
	help_m += 'first one will be considered.'

	arguments = [
			{
				'argument': 'base',
				'settings': {
					'nargs': '+',
					'type': str,
					'help': help,
				}
			},
			{
				'argument': 'count',
				'settings': {
					'nargs': '+',
					'type': str,
				}
			},
			{
				'argument': '--major',
				'settings': {
					'nargs': '+',
					'type': str,
					'help': help_m,
				}
			}
	]
	for arg_dict in arguments:
		arg = arg_dict.get('argument')
		settings = arg_dict.get('settings')
		parser.add_argument(arg, **settings)
	return parser

def parse_arguments(parser):
	args = parser.parse_args()
	base, count, major = args.base, args.count, args.major
	kwargs = {
			'base': base[0],
			'count': int(count[0]),
			'major': None,
	}
	if major:
		kwargs['major'] = major[0]
	return kwargs


import argparse
parser = argparse.ArgumentParser(description='Career fair employers by major')
parser = add_arguments(parser)
kwargs = parse_arguments(parser)
cf = CareerFair(**kwargs)
cf.get_employers()



