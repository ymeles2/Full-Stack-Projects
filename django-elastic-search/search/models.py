from __future__ import unicode_literals
from services import common_helper
from django.db import models

class Slug(models.Model):
    '''
    Stores slug used in faceted search for url paths. Hence, the slugs 
    mostly come from ProductTaxonomy. 
    '''
    # TODO: why was the name field ever set to unique?
    name = models.CharField(max_length=256, blank=False, null=True,editable=True)
    slug = models.SlugField(max_length=256, blank=False, null=True, unique=True, editable=False)
    base_slug = models.SlugField(max_length=256, blank=False, null=True, editable=False)

    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)

    def __unicode__(self):
        # the name shown in dropdowns, column label,
        # and queryset label in the shell
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        if not self.base_slug:
            self.base_slug = common_helper.slugify(self.name)
            self.slug = common_helper.unique_slugify(self.base_slug, Slug)
        super(Slug, self).save()



    def indexing(self, index=None, bulk=False):
    	import search.index.es_indexer as es_indexer
        # return ES index obj
        indexable_dict = {
                '_id': self.pk,
                'name': self.name,
                'slug': self.slug,
            }
        index_obj = index(meta={'id': self.pk},\
                     **indexable_dict)
        if bulk:
            return index_obj.to_dict(include_meta=True)
        return index_obj

class AggregationField(models.Model):
    '''
    Stores aggregation fields for faceted navigation. FacetedSearch queries these
    fields directly from Elasticsearch.

    E.g. 
        name: brand
        field: brand.raw

    The name is what's shown in the url and navigation pane. The field is what's passed 
    to Elasticsearch for aggregating.
    '''
    agg_name = models.CharField(max_length=32, blank=False, null=True)
    agg_field = models.CharField(max_length=32, blank=False, null=True)

    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % (self.agg_name)

    def indexing(self, index=None, bulk=False):
        import search.index.es_indexer as es_indexer
        # return ES index obj
        indexable_dict = {
                'agg_name': self.agg_name,
                'agg_field': self.agg_field,
            }
        index_obj = index(meta={'id': self.pk}, **indexable_dict)
        if bulk:
            return index_obj.to_dict(include_meta=True)
        return index_obj

class SortField(models.Model):
    '''
    Stores sorting fields for faceted navigation. Like AggregationField objects,
    SortField objects are also queried from Elasticsearch.
    '''
    sort_label = models.CharField(max_length=32, blank=False, null=True)
    sort_slug = models.CharField(max_length=32, blank=False, null=True)
    sort_field = models.CharField(max_length=32, blank=False, null=True)

    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)
    
    def __unicode__(self):
        return '%s' % (self.sort_label)

    def indexing(self, index=None, bulk=False):
        import search.index.es_indexer as es_indexer
        # return ES index obj
        indexable_dict = {
                'sort_label': self.sort_label,
                'sort_slug': self.sort_slug,
                'sort_field': self.sort_field,
            }
        index_obj = index(meta={'id': self.pk}, **indexable_dict)
        if bulk:
            return index_obj.to_dict(include_meta=True)
        return index_obj


from services import signals
slug_signal_obj = signals.ESIndexSignal(Slug)
agg_field_signal_obj = signals.ESIndexSignal(AggregationField)
sort_field_signal_obj = signals.ESIndexSignal(SortField)
slug_signal_obj.ready()
agg_field_signal_obj.ready()
sort_field_signal_obj.ready()
