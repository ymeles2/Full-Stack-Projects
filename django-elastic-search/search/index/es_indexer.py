from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
# from fooreviews import models as fr_models
import fooreviews.models, taxonomy.models, search.models
# import # from taxonomy import models as tx_models
from elasticsearch_dsl import DocType, Text, Keyword, Integer, Date, Search, Q, A
from elasticsearch_dsl.query import MultiMatch

connections.create_connection()

class ArticleIndex(DocType):
    article_id = Integer()
    product_name = Text(analyzer='snowball')
    # title = Text(analyzer='snowball', fields={'raw': Keyword()})
    published = Date() #TODO: we have date_created. what's the difference?
    updated = Date() # TODO: we have dat_updated. what's the diff?
    content = Text(analyzer='snowball')
    meta_description = Text(analyzer='snowball')
    taxonomy = Keyword()
    lineage_tags = Text(analyzer='snowball')
    image = Keyword()
    date_created = Date()
    date_updated  = Date()
    get_absolute_url = Keyword()
    level_0 = Text(analyzer='snowball', fields={'raw': Keyword()})
    level_1 = Text(analyzer='snowball', fields={'raw': Keyword()})
    brand = Text(analyzer='snowball', fields={'raw': Keyword()})
    color = Text(analyzer='snowball', fields={'raw': Keyword()})
    condition = Text(analyzer='snowball', fields={'raw': Keyword()})
    adjusted_rating = Keyword()
    adjusted_star_rating = Keyword()
    review_count = Keyword()
    aspect_count = Keyword()
    
    class Meta:
        index = 'article'

class SlugIndex(DocType):
    name = Text(analyzer='snowball', fields={'raw': Keyword()}) 
    slug = Text(analyzer='snowball', fields={'raw': Keyword()})
    class Meta:
        index = 'slug'

class AggregationFieldIndex(DocType):
    agg_name = Text(analyzer='snowball', fields={'raw': Keyword()}) 
    agg_field = Text(analyzer='snowball', fields={'raw': Keyword()})
    class Meta:
        index = 'aggregation_field'

class SortFieldIndex(DocType):
    sort_label = Text(analyzer='snowball', fields={'raw': Keyword()}) 
    sort_slug = Text(analyzer='snowball', fields={'raw': Keyword()})
    sort_field = Text(analyzer='snowball', fields={'raw': Keyword()})
    class Meta:
        index = 'sort_field'


def bulk_index(**kwargs):
    article_index = kwargs.get('article')
    slug_index = kwargs.get('slug')
    aggregation_index = kwargs.get('aggregation')
    sort_index = kwargs.get('sort')
    es = Elasticsearch()
    fr_models = fooreviews.models
    s_models = search.models

    # TODO: parameterize the conditionals
    if article_index:
        ArticleIndex.init()
        bulk(client=es, actions=(b.indexing(index=ArticleIndex, bulk=True,) for b in fr_models.Article.objects.all().iterator()))

    if slug_index:
        SlugIndex.init()
        bulk(client=es, actions=(b.indexing(index=SlugIndex, bulk=True) for b in s_models.Slug.objects.all().iterator()))

    if aggregation_index:
        AggregationFieldIndex.init()
        bulk(client=es, actions=(b.indexing(index=AggregationFieldIndex, bulk=True) for b in s_models.AggregationField.objects.all().iterator()))

    if sort_index:
        SortFieldIndex.init()
        bulk(client=es, actions=(b.indexing(index=SortFieldIndex, bulk=True) for b in s_models.SortField.objects.all().iterator()))


    
