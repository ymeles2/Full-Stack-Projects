from django.shortcuts import render
import fooreviews.seo.seo as seo
import contact.form_data.form_data_processor as fdp

def contact(request):
    context = {}
    fd = fdp.FormDataProcessor(request)
    context = fd.process_data()
    context.update({
    		'title': '',
    		'view_type': 'Contact Us',
    		'template_type': 'contact_us',

    	})
    context = seo.SEOMetaTags(context).get_meta_tags()
    return render(request, 'fooreviews/about.html', context)
