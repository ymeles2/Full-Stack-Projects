from django.contrib import admin
import models

class SlugAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'base_slug',]
    search_fields = ['name', 'slug', 'base_slug',]
    # class Meta:
    #     model = models.Slug

class AggregationFieldAdmin(admin.ModelAdmin):
	list_display = ['agg_name', 'agg_field']

class SortFieldAdmin(admin.ModelAdmin):
	list_display = ['sort_label', 'sort_slug', 'sort_field']

admin.site.register(models.Slug, SlugAdmin)
admin.site.register(models.AggregationField, AggregationFieldAdmin)
admin.site.register(models.SortField, SortFieldAdmin)