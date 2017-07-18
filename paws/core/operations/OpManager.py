from __future__ import print_function
import importlib
from ..models.TreeModel import TreeModel
from .. import operations as ops
from ..operations.Operation import Operation

class OpManager(TreeModel):
    """
    Tree structure for categorized storage and retrieval of Operations.
    """

    def __init__(self):
        super(OpManager,self).__init__()
        self.logmethod = print 
        self._n_ops = 0
        self._n_cats = 0

    def write_log(self,msg):
        self.logmethod(msg)

    def n_ops(self):
        return self._n_ops

    def load_cats(self,cat_list):
        for cat in cat_list:
            itm = self._root_item
            cat_tags = cat.split('.')
            cat_uri = cat_tags[0]
            if not self.contains_uri(cat_uri):
                self.set_item(cat_uri,{})
                self._n_cats += 1
            if len(cat_tags) > 1:
                for cat_tag in cat_tags[1:]:
                    #if not cat_tag in self.list_child_tags(cat_uri):
                    cat_uri = cat_uri+'.'+cat_tag
                    if not self.contains_uri(cat_uri):
                        #print('set cat {}'.format(cat_uri))
                        self.set_item(cat_uri,{})
                        self._n_cats += 1

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
        if ops.load_flags[op_uri]:
            mod = importlib.import_module('.'+op_uri,ops.__name__)
            op = getattr(mod,opname)
            optest = op()
            self.set_item(op_uri,op)
        else:
            self.set_item(op_uri,None)

    def set_op_enabled(self,op_uri,flag=True):
        cat = op_uri[:op_uri.rfind('.')]
        opname = op_uri.split('.')[-1]
        if flag:
            # enable the op: set ops.load_flags so that
            # add_op() imports it and places it in the tree
            ops.load_flags[op_uri] = True
            self.write_log('Enabling Operation {}...'.format(op_uri))
        else:
            # disable the op: set ops.load_flags so that
            # add_op() replaces the treedata with None
            ops.load_flags[op_uri] = False
            self.write_log('Disabling Operation {}'.format(op_uri))
        self.add_op(cat,opname)
        if flag:
            self.write_log('Finished enabling {}'.format(op_uri))

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



