from django.contrib import admin
# from . import forms
from . import models 

class ContactAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'email', 'subject', 'body', 'timestamp',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'timestamp',)

    # TODO: disable delete, save new 
    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(models.Contact, ContactAdmin)
