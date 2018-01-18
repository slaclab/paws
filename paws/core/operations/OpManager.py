from __future__ import print_function
from collections import OrderedDict
import importlib

from ..models.TreeModel import TreeModel
from ..models.TreeItem import TreeItem
from .. import operations as ops
from ..operations.Operation import Operation

class OpManager(TreeModel):
    """OpManager provides access to and control over paws Operations."""

    def __init__(self):
        default_flags = OrderedDict()
        default_flags['active'] = False
        super(OpManager,self).__init__(default_flags)
        self.message_callback = print 
        self.cat_op_list = []
        self.load_operations()

    def get_operation(self,operation_uri):
        """Get an Operation, activate it if needed, instantiate, return.

        Parameters
        ----------
        operation_uri : str
            uri indicating the operation module,
            e.g. PROCESSING.TESTS.Fibonacci.

        Returns
        -------
        op : Operation
            the instantiated Operation 
        """
        if not self.is_op_activated(operation_uri):
            try:
                self.activate_op(operation_uri)
            except ImportError as ex:
                from paws.core.pawstools import OperationLoadError
                msg = 'Most likely, the system '\
                    'does not have the right dependencies '\
                    'for Operation {}'.format(operation_uri)
                raise OperationLoadError(msg) 
        op = self.get_data_from_uri(operation_uri)
        return op()

    def load_operations(self,cat_op_list=ops.cat_op_list):
        """Load Operations into OpManager.

        Parameters
        ----------
        cat_op_list : list of (str,str), optional
            Each element in the list is a tuple containing two strings.
            The first string in the tuple indicates the category subpackage.
            The second string in the tuple indicates the operation module.
            The default is to load all operations 
            detected by paws.core.operations at startup.
        """
        for cat_op in cat_op_list:
            self.add_cat(cat_op[0])
            if cat_op[1]:
                self.add_op(cat_op[0],cat_op[1])
                self.cat_op_list.append((cat_op[0],cat_op[1]))

    def add_cat(self,cat_module):
        """Add category `cat_module` to the tree."""
        itm = self._root_item
        cat_tags = cat_module.split('.')
        cat_uri = cat_tags[0]
        if not self.contains_uri(cat_uri):
            self.set_item(cat_uri,{})
        if len(cat_tags) > 1:
            for cat_tag in cat_tags[1:]:
                cat_uri = cat_uri+'.'+cat_tag
                if not self.contains_uri(cat_uri):
                    self.set_item(cat_uri,{})

    def add_op(self,cat_module,op_name):
        """Add label for an Operation at `op_name` under category `cat_module`."""
        op_uri = cat_module+'.'+op_name
        self.set_item(op_uri,None)

    def activate_op(self,op_module):
        """Import Operation module and add its Operation subclass to the tree.

        This method imports the Operation to check compatibility,
        and then sets the 'active' flag to True.
        After this, the Operation is available
        via self.get_op()

        Parameters
        ----------
        op_module : str
            Name of the Operation module.
            Example: If class MyOperation is in the CATEGORY.MyOperation module,
            retrieve it with `op_module` = 'CATEGORY.MyOperation'.
        """
        op_name = op_module.split('.')[-1]
        m = importlib.import_module('.'+op_module,ops.__name__)
        op = getattr(m,op_name)
        optest = op()
        self.set_item(op_module,op)
        op_itm = self.get_from_uri(op_module)
        self.set_flagged(op_itm,'active',True)

    def is_op_activated(self,op_module):
        """Return boolean indicating whether Operation is active.

        Parameters
        ----------
        op_module : str
            Name of the Operation module.
            see activate_op().
        """
        op_itm = self.get_from_uri(op_module)
        return op_itm.flags['active']

    def n_ops(self):
        return len(self.cat_op_list) 

    def list_operations(self):
        return [catnm+'.'+opnm for catnm,opnm in self.cat_op_list] 

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
                    # this should be the case for non-activated ops
                    tree_string = tree_string + rowprefix + '{} (disabled) \n'.format(k)
                elif isinstance(x,dict):
                    # this should be the case for a subcat
                    next_cat_tree = self.print_cat(cat_uri+'.'+k,rowprefix+'    ')
                    tree_string = tree_string + rowprefix + '{}: {}'.format(k,next_cat_tree)
                else:
                    # the only remaining case is an activated operation
                    tree_string = tree_string + rowprefix + '{} \n'.format(k)
        return tree_string


