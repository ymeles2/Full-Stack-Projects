from services import common_helper
import models 

def get_lineage_tags(taxonomy_obj):
    '''
    Construct a lineage for taxonomy_obj and return a list object 
    consisting of comma-separated string names of the taxonomy 
    objects in the lineage.
    '''
    lineage = []
    ancestors = taxonomy_obj.get_ancestors()
    for ancestor in ancestors:
        lineage.append(ancestor.name)
    lineage.append(taxonomy_obj.name)
    return lineage

def get_lineage_slugs(lineage_tags):
    '''
    Slugify all lineage tags in lineage_str and return a string 
    object.
    '''
    lineage_slugs = []
    # the type of the object changes to unicode if it has already been saved
    # to the db but not if we're in the middle of creating the model object
    if not isinstance(lineage_tags, list):
        # cast the unicode object to a list if not already in this type
        lineage_tags = eval(lineage_tags)
    for tag in lineage_tags:
        slug = common_helper.slugify(tag)
        lineage_slugs.append(slug)
    return lineage_slugs


def populate_tax_levels(taxonomy_obj):
    '''
    Populate taxonomy level fields in the product taxonomy object.
    Used by ES in faceting.  
    '''
    # E.g.:
    # level_0: a
    # level_1: a, b
    # ...
    # so an and so forth
    levels_list = [
            taxonomy_obj.level_0,
            taxonomy_obj.level_1,
    ]

    if not all(levels_list):
        # populate the fields only if all of them are empty
        lineage_list = taxonomy_obj.lineage_tags
        if not isinstance(lineage_list, list):
        	lineage_list = eval(lineage_list)
        temp_list = []
        for i in range(len(lineage_list)):
            # level = 'level_' + str(i)
            temp_list.append(lineage_list[i])
        
        # we cannot reference the attributes of 'self' dynamically 
        # so we'll just catch the index error  
        try:
            taxonomy_obj.level_0 = temp_list[0]
            taxonomy_obj.level_1 = temp_list[1]
        except IndexError:
            pass

def populate_product_taxonomy():
	'''
	Populate the various fields of product taxonomy object.
	'''
	a = models.ProductTaxonomy.objects.all()
	if a:
		for obj in a:
			obj.save()

def populate_top_levels():
    '''
    Populate top level categories. 
    '''
    # clear the table first
    models.TopLevelCategory.objects.all().delete()
    pt_set = models.ProductTaxonomy.objects.all()
    top_level_set = pt_set.filter(level=0)
    for obj in top_level_set:
    	models.TopLevelCategory.objects.create(name=obj.name)
    top_level_set = models.TopLevelCategory.objects.all()
    for obj in top_level_set:
        # populate the slug field
        obj.save()

def get_top_level_cats():
    '''
    Return the names, slugs, and image file names of top_level 
    categories.

    We are only showing the following topics in the early stage:
    Electronics, Appliances, Bags & Travel
    '''
    topics_list = []
    topics = models.TopLevelCategory.objects.all().order_by('name')
    for topic in topics:
        if topic.enabled:
            topic_attrs = [topic.name, topic.slug, topic.image]
            topics_list.append(topic_attrs)
    return topics_list



def breadcumb_builder(taxonomy_obj):
    '''
    Construct a breadcrumb using individual slugs in lineage_slugs.
    Return a list containing the full breadcrumbs.

    E.g.
    lineage_tags = ['A', 'B', 'C', 'D']
    lineage_slugs = ['a', 'b', 'c', 'd']
    breadcrumb_list = [
                    {A: topics/a/},
                    {B: topics/a/b/},
                    {C: topics/a/b/c/},
                    {D: topics/a/b/c/d },
            ]
    '''
    lineage_tags = taxonomy_obj.lineage_tags
    lineage_slugs = taxonomy_obj.lineage_slugs
    if not isinstance(lineage_tags, list):
        lineage_tags = eval(lineage_tags)
    if not isinstance(lineage_slugs, list):
        lineage_slugs = eval(lineage_slugs)

    breadcrumb_list = []
    cumulative_crumb = 'topics/'
    z = zip(lineage_tags, lineage_slugs)
    for tag, slug in z:
        cumulative_crumb += slug + '/'
        crumb_dict = {tag: cumulative_crumb}
        breadcrumb_list.append(crumb_dict)
    return breadcrumb_list