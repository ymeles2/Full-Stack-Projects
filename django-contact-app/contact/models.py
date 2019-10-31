from __future__ import unicode_literals

from django.db import models

class Contact(models.Model):
    '''
    Implements a basic contact form.
    '''
    name  = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    subject  = models.CharField(max_length=256, blank=True, null=True)
    message = models.TextField(max_length=2000, blank=False, null=True)
    timestamp  = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return '%s' % (self.name)

    def body(self, n=60):
        if self.message:
            return self.message[:n] + '...'
