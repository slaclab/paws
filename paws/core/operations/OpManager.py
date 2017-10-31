from __future__ import print_function
from collections import OrderedDict
import importlib

from ..models.TreeModel import TreeModel
from ..models.TreeItem import TreeItem
from .. import operations as ops
from ..operations.Operation import Operation

class OpManager(TreeModel):
    """
    Tree structure for categorized storage and retrieval of Operations.
    """

    def __init__(self):
        default_flags = OrderedDict()
        default_flags['enable'] = False
        super(OpManager,self).__init__(default_flags)
        self.logmethod = print 
        self._n_ops = 0
        #self._n_cats = 0

    # override TreeModel.create_tree_item() to add 
    # the correct enable/disable flags. 
    #def create_tree_item(self,parent_itm,itm_tag):
    #    itm = TreeItem(parent_itm,itm_tag)
    #    #op_uri = self.build_uri(itm)
    #    #itm.flags['enable'] = False
    #    return itm

    def is_op_enabled(self,op_uri):
        op_itm = self.get_from_uri(op_uri)
        return op_itm.flags['enable']

    def n_ops(self):
        return self._n_ops

    def list_ops(self):
        return [catnm+'.'+opnm for catnm,opnm in ops.cat_op_list] 

    def load_cats(self,cat_list):
        for cat in cat_list:
            itm = self._root_item
            cat_tags = cat.split('.')
            cat_uri = cat_tags[0]
            if not self.contains_uri(cat_uri):
                self.set_item(cat_uri,{})
                #self._n_cats += 1
            if len(cat_tags) > 1:
                for cat_tag in cat_tags[1:]:
                    #if not cat_tag in self.list_child_tags(cat_uri):
                    cat_uri = cat_uri+'.'+cat_tag
                    if not self.contains_uri(cat_uri):
                        #print('set cat {}'.format(cat_uri))
                        self.set_item(cat_uri,{})
                        #self._n_cats += 1

    def load_ops(self,cat_op_list):
        """
        Load OpManager tree from input cat_op_list.
        Format of cat_op_list is [(category1,opname1),(category2,opname2),...].
        i.e. each operation in cat_op_list is specified by a tuple,
        where the first element is a category,
        and the second element is the name of the Operation.
        load_cats() should be called before load_ops()
        and should ensure that all cats in cat_op_list exist in the tree.
        """
        for cat_op in cat_op_list:
            self.add_op(cat_op[0],cat_op[1])
            self._n_ops += 1

    def add_op(self,cat,opname):
        """
        Add op name to the tree under category cat.
        """
        op_uri = cat+'.'+opname
        self.set_item(op_uri,None)
        #if ops.load_flags[op_uri]:
        #    try: 
        #        self.set_op_enabled(op_uri)
        #    except ImportError:
        #        self.logmethod('import error for {}: disabling operation'.format(op_uri))
        #        self.set_op_enabled(op_uri,False)
        #    except Exception as ex:
        #        self.logmethod('unexpected exception while importing {}. Message: {}'.format(op_uri,ex.message))
        #        self.set_op_enabled(op_uri,False)
        #else:

    def set_op_enabled(self,op_uri,flag=True):
        cat = op_uri[:op_uri.rfind('.')]
        opname = op_uri.split('.')[-1]
        if flag:
            mod = importlib.import_module('.'+op_uri,ops.__name__)
            op = getattr(mod,opname)
            optest = op()
            self.set_item(op_uri,op)
            op_itm = self.get_from_uri(op_uri)
            self.set_flagged(op_itm,'enable',flag)
        else:
            # disable the op: set ops.load_flags so that
            # add_op() replaces the treedata with None
            #ops.load_flags[op_uri] = False
            self.set_item(op_uri,None)

    def remove_op(self,op_uri):
        """Remove op from the tree by its full category.opname uri"""
        self.remove_item(op_uri)
        self._n_ops -= 1

    def print_cat(self,cat_uri,rowprefix='    '):
        """
        Generate a string that lists the contents 
        of the operations category specified by cat_uri
        """
        catdata = self.get_data_from_uri(cat_uri)
        tree_string = '\n' 
        if isinstance(catdata,dict):
            for k,x in catdata.items():
                if x is None:
                    # this should be the case for not-enabled ops
                    tree_string = tree_string + rowprefix + '{} (disabled) \n'.format(k)
                elif isinstance(x,dict):
                    # this should be the case for a subcat
                    next_cat_tree = self.print_cat(cat_uri+'.'+k,rowprefix+'    ')
                    tree_string = tree_string + rowprefix + '{}: {}'.format(k,next_cat_tree)
                else:
                    # the only remaining case is an enabled operation
                    tree_string = tree_string + rowprefix + '{} \n'.format(k)
        return tree_string



