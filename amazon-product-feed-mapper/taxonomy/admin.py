from django.contrib import admin
from . import models
from mptt.admin import MPTTModelAdmin

class ProductTaxonomyMPTTAdmin(MPTTModelAdmin):
    list_display = ('name',)
    search_fields = ('name',) 

    # disable deletion from the front-end
    def has_delete_permission(self, request, obj=None):
        return False


class TopLevelCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'enabled')
    class Meta:
        model = models.TopLevelCategory


admin.site.register(models.TopLevelCategory, TopLevelCategoryAdmin)
admin.site.register(models.ProductTaxonomy, ProductTaxonomyMPTTAdmin)





