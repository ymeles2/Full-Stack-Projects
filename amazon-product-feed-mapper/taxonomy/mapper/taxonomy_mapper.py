from taxonomy import models
import time
from services import loggers
logger = loggers.Loggers(__name__).get_logger()


class TaxonomyMapper(object):
    '''
    Maps raw taxonomy names into a a hierarchical tree by building parent-child 
    relations.

    Tested to work with complex hierarchical relations such as those found in 
    Amazon product feed.  
    '''
    def __init__(self, **kwargs):
        self.taxonomy_list = self.get_taxonomy()
  
    def get_taxonomy(self):
        '''
            Return a tagged list of taxonomy dictionary objects. Tagging here means 
            establishing parent-child relationships as key-value pairs. The parent 
            is the key and the child is the value.
        ''' 
        raw_taxonomy_set = models.RawTaxonomy.objects.all()
        taxonomy_raw_list = []
        for tax_dict_obj in raw_taxonomy_set.values():
            '''
                A tax_dict_obj is a dictionary object containing all the fields
                and values of an instance of a raw taxonomy object, i.e. a 
                single row in the table. We are iterating through the columns of
                seach row. 
            '''
            i = 0
            TAXONOMY_LEVELS = 1
            temp_list = []
            while i <= TAXONOMY_LEVELS:
                key = 'level_' + str(i)  
                value = tax_dict_obj[key]
                if value is not None:
                    temp_list.append(value)
    #                level_dict[value.encode('utf-8')] = i
                i += 1
            taxonomy_raw_list.append(temp_list)

    #
        taxonomy_list_tagged = []
        for row in taxonomy_raw_list:
            temp_list = []
            i = 0
            levels = len(row)
            for i in range(levels-1):
                temp_dict = {}
                index = levels - 1 - i
                child = row[index]
                parent = row[index-1]
                temp_dict[parent] = child
                temp_list.append(temp_dict)
                i += 1
            taxonomy_list_tagged.append(list(reversed(temp_list)))
        
        
        # clean the data by removing empty lists
        taxonomy_list_cleaned = [x for x in taxonomy_list_tagged if x != []]
        return taxonomy_list_cleaned


    def get_child_obj(self, taxonomy_name, parent_obj, row, index):
        '''
        Using taxonomy_name, get child_obj. First build a mini lineage using the 
        ancestors from the taxonomy object. Then compare it to a row mini lineage, 
        which includes the taxonomy names up to index. Return the object where the 
        row mini lineage matches the taxonomy object mini lineage.
        '''
        child_obj = None
        row_dict_list = row[:index+1] # a partial lineage up to index
        queryset = models.ProductTaxonomy.objects.filter(name=taxonomy_name).prefetch_related()
        for possible_child in queryset:
            
            ancestors = possible_child.get_ancestors()
            tax_lineage = []
            for ancestor in ancestors:
                tax_lineage.append(ancestor)
            tax_lineage.append(possible_child)
            tax_dict_list = [] # a partial lineage through possible_child
            for i in range(len(tax_lineage) - 1):
                parent = tax_lineage[i]
                child = tax_lineage[i+1]
                tax_dict = {parent.name: child.name}
                tax_dict_list.append(tax_dict)
            if tax_dict_list == row_dict_list:
                child_obj = possible_child
                return child_obj
        return child_obj
            

    def get_parent_obj(self, index, tax_dict_list, row, child=False):
        '''
        Given the name of an object, return its taxonomy object. 
        '''
        parent_tax_obj = None
        child_tax_obj = None
        if tax_dict_list:
            if index == 0:
                tax_dict = tax_dict_list[0]
                for obj in tax_dict:
                    parent_tax_obj = obj
                    child_tax_obj = tax_dict[obj]
            else:
                tax_dict = tax_dict_list[index-1]
                row_dict = row[index-1]
                for obj in tax_dict:
                    # the value of the dict would be the parent object for a new
                    # child object
                    parent_tax_obj = tax_dict[obj]
                    if child:
                        parent_tax_obj = obj
                        child_tax_obj = tax_dict[obj]
                    
                for row_str in row_dict:
                    parent_row_str = row_dict[row_str]
                    if child:
                        parent_row_str = row_str
                        child_row_str = row_dict[row_str]
                
                #assert that the tax and row objects refer to the same thing
                assert(parent_tax_obj.name == parent_row_str)
                if child:
                    assert(child_tax_obj.name == child_row_str)
        if child:
            return child_tax_obj          
        return parent_tax_obj

    def get_g_parent(self, parent_tax_obj=None, row=None, tax_dict_list=None, index=0):
        '''
        Return the grandparent taxonomy object or the row equivalent (str object). 
        '''
        if row:
            row_g_parent = None
            parent = parent_tax_obj.name
            row_root_node = row[0]
            for val in row_root_node:
                if val == parent:
                    row_g_parent = None
                elif row_root_node[val] == parent:
                    row_g_parent = val
            if not row_g_parent:
                # we're not at the root node, i.e. index > 0
                for dict_obj in row:
                    for key in dict_obj:
                        parent_obj = key
                        child_obj = dict_obj[key]
                    if parent_obj == parent_tax_obj.parent.name:
                        # Since we're not at the root node, we must assume our parent
                        # object must have a parent, i.e. a row_g_parent
                        row_g_parent = parent_obj
                    elif child_obj == parent_tax_obj.parent.name:
                        row_g_parent = child_obj
            return row_g_parent
        if tax_dict_list:
            tax_dict = tax_dict_list[index-1]
            for val in tax_dict:
                row_g_parent_obj = val
                return row_g_parent_obj
            
        if parent_tax_obj:
            return parent_tax_obj.parent
        
    def get_root_node(self, parent, child, root_node_dicts):
        '''
        Return root parent and child taxonomy objects.
        '''
        parent_tax_obj = None
        child_tax_obj = None
        for dict_obj in root_node_dicts:
            for val in dict_obj:
                parent_obj_str = val.name
                child_obj_str = dict_obj[val].name
                if parent_obj_str == parent:
                    parent_tax_obj = val
                    if child_obj_str == child:
                        # let's make sure this isn't a situation where only the 
                        # parent is in the root and the child hasn't been added yet
                        child_tax_obj = dict_obj[val]
                        return parent_tax_obj, child_tax_obj
        return parent_tax_obj, child_tax_obj 
                
                

    def is_related(self, parent, child, master_tax_dict_list):
        '''
        Check if there is an existing relation between the parent and the child.
        Return True if there is a relation, False otherwise.
        A relation here simply means key-value pairing.
        '''
        p_c_dict = {}
        p_c_dict[parent] = child
        if p_c_dict in master_tax_dict_list:
            return True
        return False

    def save_current(self, **kwargs):
        '''
        Add objects to a dictionary or a list and return the updated values.
        '''
        child_instance = kwargs['child_instance']
        parent_instance = kwargs['parent_instance']
        tax_dict = kwargs['tax_dict']
        tax_dict_list = kwargs['tax_dict_list']
        tax_str_dict = kwargs['tax_str_dict']
        tax_str_list = kwargs['tax_str_list']
        master_tax_str_list = kwargs['master_tax_str_list']
        tax_dict[parent_instance] = child_instance
        tax_dict_list.append(tax_dict)
        tax_str_dict[parent_instance.name] = child_instance.name
        tax_str_list.append(tax_str_dict)
        master_tax_str_list.append(tax_str_dict)
        return kwargs

    def pre_save_current(self, parent_instance, child_instance, kwargs):
        kwargs['parent_instance'] = parent_instance
        kwargs['child_instance'] = child_instance 
        return self.save_current(**kwargs)
        

    def mapper(self):
        '''
        Given a raw table of taxonomy names, map them by building parent-child
        relations.

        To execute, clear the Taxonomy db table first and then call this
        function from the shell.  

        TODO: this function needs to be refactored but we're not going to do that. 
            We know that it works and that it only gets used to populate the taxonomy 
            fields of a website once and maybe another time when migrating to some other
            db or server. Further, we have moved away from using the number of taxonomies 
            that initially necessitated writing this module. Instead of 15,000, we're now 
            only using about 140. This is due to a change in philisophy after implementing
            the module. Therefore, we have no compelling reason to use. We might even 
            not use it all in the future. But for now, we'll acknowledge the sunk cost fallacy
            and put up with it.
        '''

        i = 0
        tax_str_master = []
        master_lineage = []
        master_tax_str_list = []
        root_node_dicts = []
        logger.info('Mapping taxonomies...')
        for row in self.taxonomy_list:
            msg = 'Mapping taxonomy: {}'.format(row)
            logger.info(msg)
            j = 0
            tax_dict_list = []
            tax_str_list = []
            for dict_obj in row:
                tax_dict = {}
                tax_str_dict = {}
                kwargs = {
                        'parent_instance': None,
                        'child_instance': None,
                        'tax_dict':tax_dict,
                        'tax_dict_list': tax_dict_list,
                        'tax_str_dict': tax_str_dict,
                        'tax_str_list': tax_str_list,
                        'master_tax_str_list': master_tax_str_list,
                }
                for parent, child in dict_obj.iteritems():
            
                    # ignore empty parent-child pair
                    if parent and child:
                        if models.ProductTaxonomy.objects.all() is not None:
                            # a model object exists, i.e. the db is not empty

                            parent_exists = models.ProductTaxonomy.objects.filter(name=parent).exists()
                            child_exists = models.ProductTaxonomy.objects.filter(name=child).exists()
                            if parent_exists and not child_exists: 
                                # parent exists but child doesn't 
                                # get parent taxonomy object and relate that to 
                                # a newly created child
                                if j == 0:
                                    # we're at the root
                                    root_parent, root_child = self.get_root_node(parent, child, root_node_dicts)
                                    if root_parent == None:
                                        # a rare instance where the parent can exist 
                                        # elsewhere as a child of some other lineage
                                        # but is now making an appearnce for the first
                                        # time as a root node
                                        # E.g. Shoes; it appears as a child of Costumes & Accessories
                                        # but also a level_0 object, i.e. a root node later on
                                        root_parent = models.ProductTaxonomy.objects.create(name=parent)
                                        
                                    if root_child == None:
                                        # we have a new root node, i.e a new parent-child for root
                                        parent_instance = root_parent
                                        child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                        root_node = {parent_instance:child_instance }
                                        root_node_dicts.append(root_node)
                                        kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)
                                    else:
                                        # a root node exists with the given parent and child
                                        kwargs = self.pre_save_current(root_parent, root_child, kwargs)
                                else:
                                    parent_instance = self.get_parent_obj(j, tax_dict_list, row)
                                    child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                    kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)

                            elif parent_exists and child_exists:
                                child_instance = None
                                # both objects exist in the db
                                if j == 0:
                                    # we're at the root
                                    root_parent, root_child = self.get_root_node(parent, child, root_node_dicts)
                                    if root_parent == None:
                                        # a rare instance where the parent can exist 
                                        # elsewhere as a child of some other lineage
                                        # but is now making an appearnce for the first
                                        # time as a root node
                                        # E.g. Shoes; it appears as a child of Costumes & Accessories
                                        # but also a level_0 object, i.e. a root node, later on
                                        root_parent = models.ProductTaxonomy.objects.create(name=parent)
                                    if root_child == None:
                                        # we have a new root node, i.e a new parent-child for root
                                        # this is a situation where even though both the parent and child objects exist,
                                        # the parent-child combo is not found in the root nodes
                                        parent_instance = root_parent
                                        child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                        root_node = {parent_instance:child_instance }
                                        root_node_dicts.append(root_node)
                                        kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)
                                    else:
                                        kwargs = self.pre_save_current(root_parent, root_child, kwargs)
                                else:
                                    parent_instance = self.get_parent_obj(j, tax_dict_list, row)
                                    # is the parent related to the child?
                                    related = self.is_related(parent, child, master_tax_str_list)
                                    if related:
                                        # who's the grand parent?
                                        g_parent = self.get_g_parent(parent_tax_obj=parent_instance)
                                        if g_parent:
                                            row_g_parent = self.get_g_parent(parent_tax_obj=parent_instance, row=row)
                                            if row_g_parent == g_parent.name:
                                                # we have an a -> b -> c relation
                                                # we need to get the c taxonomy 
                                                # object
                                                child_instance = self.get_child_obj(child, parent_instance, row, j)
                                                if not child_instance:
                                                    # we have an isolated b -> c relation; this relation appears multiple times
                                                    # with the same root_node
                                                    child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                                kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)
    #                                               

                                            else:
                                                # we have an isolated b -> c relation
                                                # find the proper g_parent and relate
                                                # the objects to get a -> b -> c
                                                g_parent_instance = self.get_g_parent(index=j, tax_dict_list=tax_dict_list)
                                                parent_instance =  models.ProductTaxonomy.objects.create(name=parent, parent=g_parent_instance)
                                                child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                                kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)

                                    else:
                                        # if there's no existing relation, get the parent
                                        # taxonomy object and link it to a newly created
                                        # child taxonomy object
                                        #parent_instance = # get the parent instance for the current dict object
                                        child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                        kwargs = self.pre_save_current(parent_instance, child_instance, kwargs)
                            else:
                                # parent and child objects do not exist
                                parent_instance = models.ProductTaxonomy.objects.create(name=parent)
                                child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                                root_node = {parent_instance:child_instance }
                                root_node_dicts.append(root_node)
                                kwargs= self.pre_save_current(parent_instance, child_instance, kwargs)



                        else: 
                            # there's no model object; this is the case on a clean db table
                            parent_instance = models.ProductTaxonomy.objects.create(name=parent)
                            child_instance = models.ProductTaxonomy.objects.create(name=child, parent=parent_instance)
                            kwargs= self.pre_save_current(parent_instance, child_instance, kwargs)
                j += 1
            i += 1