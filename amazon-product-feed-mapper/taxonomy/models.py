from __future__ import unicode_literals
from django.db import models
from . import taxonomy_helper
# from search import es_indexer
from services import common_helper
from mptt.models import MPTTModel, TreeForeignKey 



class RawTaxonomy(models.Model):
    '''
    Stores a two-level product taxonomy. 
    Run 'python manage.py custom_commands' to copy the csv to the db
    ''' 
    level_0 = models.CharField(max_length=256, blank=False, null=True, editable=False) 
    level_1 = models.CharField(max_length=256, blank=False, null=True, editable=False)
    
    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % (self.level_0)


class ProductTaxonomy(MPTTModel, models.Model):
    '''
    Uses an abridged version of Google product taxonomy. Used primarily
    in faceting and breadcrumb construction.
    '''
    name = models.CharField(max_length=256, blank=False, null=True, editable=False)
    parent = TreeForeignKey('self', null=True, blank=False, related_name='children', editable=False)
    lineage_tags = models.CharField(max_length=256, blank=True, null=True, editable=False, unique=True)
    lineage_slugs = models.SlugField(max_length=256, blank=True, null=True, editable=False)
    breadcrumb = models.CharField(max_length=9999, blank=True, null=True, editable=False) 
    level_0 = models.CharField(max_length=256, blank=True, null=True, editable=True) 
    level_1 = models.CharField(max_length=256, blank=True, null=True, editable=True)
    
    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)

    def __unicode__(self):
        # the name shown in dropdowns, column label,
        #  and queryset label in the shell
        return '%s' % (self.name)

    class MPTTMeta:
        order_insertion_by = ['name']
    
    def save(self, *args, **kwargs):
        # TODO: populate the following fields only after all taxonomy
        # instances have been created
        if not self.lineage_tags:
            self.lineage_tags = taxonomy_helper.get_lineage_tags(self)
            if not self.lineage_slugs:
                self.lineage_slugs = taxonomy_helper.get_lineage_slugs(self.lineage_tags)
        if self.lineage_tags:
	         # populate taxonomy levels for es aggregation
	        taxonomy_helper.populate_tax_levels(self)
        if self.lineage_slugs:
            self.breadcrumb = taxonomy_helper.breadcumb_builder(self)
        super(ProductTaxonomy, self).save()

class TopLevelCategory(models.Model):
    '''
    Names, slugs, and static images of level_0 taxonomy objects. These objects
    are used to populate the top-level category list either on the home page or 
    elsewhere as necessary.

    Fields:
        enabled: indicates whether the product category is enabled 
            or not. Only three categories are enabled initially. Over time, more will be enabled.
    '''
    name = models.CharField(max_length=256, blank=False, null=True)
    slug = models.SlugField(max_length=256, blank=False, null=True)
    enabled = models.BooleanField(blank=True, default=False)

    # we're storing the image url directly as a string rather than
    # a url to keep it static
    # template references must take this into account
    # home icons are stored at /static/img/home-icons/
    image = models.CharField(max_length=256, blank=False, null=True, editable=True)


    # Data Transfer Status 
    data_dumped = models.BooleanField(default=False)
    
    def __unicode__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
    	if not self.name:
    		# populate the field
    		taxonomy_helper.populate_top_levels()
        if (self.name) and (not self.slug):
            self.slug = common_helper.slugify(self.name)
        super(TopLevelCategory, self).save()


