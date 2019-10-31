from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search, Q, A

class GeneralSearch(object):
    '''
    Makes general search queries against Elasticsearch. Queries 
    can be user-specified in the browser or server-side for faceting,
    taxonomy mapping, breadcrumb construction, etc. 
    '''
    def __init__(self, **kwargs):
        self.pk = kwargs.get('pk')
        self.slug = kwargs.get('slug')
        self.name = kwargs.get('name')
        self.query = kwargs.get('query')
        connections.create_connection()

    def search_by_pk(self):
        '''
        Search by pk. Return exact match.
        ''' 
        s = Search(index="article")
        s = s.query("match", article_id=self.pk)
        response = self.get_response(s)
        return response

    def search_slug(self):
        '''
        Search either by slug or by name. Return exact match.
        '''
        s = Search(index="slug")
        if self.slug:
            field_dict = {'slug.raw': self.slug}
            s = s.filter("term", **field_dict)
        elif self.name:
            field_dict = {'name.raw': self.name}
            s = s.filter("term", **field_dict)
           
        response = self.get_response(s)
        return response

    def search_by_query(self):
        '''
        Search by query. Return any matching hits.
        '''
        s = Search(index="article")
        s = s.query('query_string', query=self.query)
        response = self.get_response(s)
        return response

    def get_all_articles(self):
        '''
        Get all articles from the index.
        '''
        s = Search(index="article")
        s = s.query("match_all")
        s.sort('created', {'order': 'desc'}) #sort in descending order
        response = self.get_response(s)
        return response

    def get_faceting_fields(self, aggregation=False, sorting=False):
        if aggregation:
            s = Search(index="aggregation_field")
        elif sorting:
            s = Search(index="sort_field")
        if aggregation or sorting:
            s = s.query("match_all")
            response = self.get_response(s)
            return response

    def get_response(self, s):
        '''
        Get a response.

        NB: This may never apply to us but there's a TransportError
        if hit count is >= 10k. 
        '''
        MAX_HITS = 100
        response = s.execute()
        count = s.count()  
        if count > MAX_HITS + 1:
            # only return the top 100 results
            response = s[:MAX_HITS].execute()
        else:
            # if we don't include this else, elasticsearch only returns the first
            # 10 results by default
            response = s[:count].execute()
        return response


