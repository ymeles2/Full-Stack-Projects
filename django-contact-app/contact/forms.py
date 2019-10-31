import models
from django import forms

class ContactForm(forms.ModelForm):
	class Meta:
	    model = models.Contact
	    widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email Address'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message'}),
        }
	    fields = ['name', 'email', 'subject', 'message']