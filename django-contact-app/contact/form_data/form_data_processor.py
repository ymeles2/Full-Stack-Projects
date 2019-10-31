import contact.models as cct_models
import contact.forms as forms
import services.loggers as loggers
logger = loggers.Loggers(__name__).get_logger()

class FormDataProcessor(object):
	'''
	Processes contact form submission before saving the data to db.
	'''
	def __init__(self, request, **kwargs):
		self.request = request

	def process_data(self):
		'''
		Clean form data and save it to the database. Return a context
		dictionary to populate post-submission messages.
		'''
		context = {}
		try:
			if self.request.method == 'GET':
				f = forms.ContactForm() 
			else:
				f = forms.ContactForm(self.request.POST or None) 
				if f.is_valid():
					record = {
						'name': f.cleaned_data.get('name'),
						'email': f.cleaned_data.get('email'),
						'subject': f.cleaned_data.get('subject'),
						'message': f.cleaned_data.get('message'),
						'timestamp': f.cleaned_data.get('timestamp'),
					}
					# save the form to the db
					cct_models.Contact.objects.create(**record)
					context['submitted'] = True
			context['form'] = f
		except Exception as e:
			msg = '{}: {}'.format(type(e).__name__, e.args[0])
			logger.exception(msg)
		return context
	    