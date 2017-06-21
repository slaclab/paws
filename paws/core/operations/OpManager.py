from __future__ import print_function
from .. import operations as ops
from ..operations import optools
from ..models.TreeModel import TreeModel

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
        Format of cat_op_list is [(category1,op1),(category2,op2),...].
        i.e. each operation in cat_op_list is specified by a tuple,
        where the first element is a category,
        and the second element is the Operation itself.
        load_cats() should be called before load_ops()
        and should ensure that all cats in cat_op_list exist in the tree.
        """
        #### BUILD OPERATIONS TREE
        # Tree will consist of nodes indicating categories,
        # with subcategories or Operations as children.
        for cat_op in cat_op_list:
            self.add_op(cat_op[0],cat_op[1])
            self._n_ops += 1

    def add_op(self,cat,op):
        """
        Add op to the tree under category specified by uri cat.
        """
        self.set_item(cat+'.'+op.__name__,op)

    def remove_op(self,op_uri):
        """Remove op from the tree by its full category.opname uri"""
        self.remove_item(op_uri)
        self._n_ops -= 1
