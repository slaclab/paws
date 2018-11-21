from __future__ import print_function
from collections import OrderedDict
import importlib

from ..pawstools.DictTree import DictTree 
from .. import operations as ops
from ..pawstools import OperationLoadError

class OpManager(DictTree):
    """OpManager provides access to and control over paws Operations."""

    def __init__(self):
        # TODO: handle flags
        #default_flags = OrderedDict()
        #default_flags['enabled'] = False
        super(OpManager,self).__init__()
        self.ops_enabled = DictTree()
        self.message_callback = self.tagged_print 
        self.cat_op_list = []
        self.load_operations()

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def get_operation(self,op_key):
        """Get an Operation, enable it if needed, instantiate, return.

        Parameters
        ----------
        op_key : str
            key indicating the operation module,
            e.g. PROCESSING.TESTS.Fibonacci.

        Returns
        -------
        op : Operation
            the instantiated Operation 
        """
        if not self.is_op_enabled(op_key):
            try:
                self.enable_op(op_key)
            except Exception:
                raise OperationLoadError('Error loading {}'.format(op_key)) 
        op = self.get_data(op_key)
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
            detected by paws.operations at startup.
        """
        for cat_op in cat_op_list:
            self.add_cat(cat_op[0])
            if cat_op[1]:
                self.add_op(cat_op[0],cat_op[1])
                self.cat_op_list.append((cat_op[0],cat_op[1]))

    def add_cat(self,cat_module):
        """Add category `cat_module` to the tree."""
        cat_tags = cat_module.split('.')
        cat_key = cat_tags[0]
        if not cat_key in self.keys():
            self.set_data(cat_key,{})
            self.ops_enabled.set_data(cat_key,{})
        if len(cat_tags) > 1:
            for cat_tag in cat_tags[1:]:
                cat_key = cat_key+'.'+cat_tag
                if not cat_key in self.keys():
                    self.set_data(cat_key,{})
                    self.ops_enabled.set_data(cat_key,{})

    def add_op(self,cat_module,op_name):
        """Add label for an Operation at `op_name` under category `cat_module`."""
        op_key = cat_module+'.'+op_name
        self.set_data(op_key,None)
        self.ops_enabled.set_data(op_key,False)

    def enable_op(self,op_module):
        """Import Operation module and add its Operation to the tree.

        This method imports the Operation to check compatibility,
        and then sets the 'enabled' flag to True.
        After this, the Operation is available via self.get_op()

        Parameters
        ----------
        op_module : str
            Name of the Operation module.
            Example: If class MyOperation is in the CATEGORY.MyOperation module,
            retrieve it with `op_module` = 'CATEGORY.MyOperation'.
        """
        op_name = op_module.split('.')[-1]
        try:
            m = importlib.import_module('.'+op_module,ops.__name__)
        except ImportError:
            raise OperationLoadError('Error loading {}'.format(op_module)) 
        op = getattr(m,op_name)
        optest = op()
        self.set_data(op_module,op)
        self.ops_enabled[op_module] = True

    def is_op_enabled(self,op_module):
        """Return boolean indicating whether Operation is enabled.

        Parameters
        ----------
        op_module : str
            Name of the Operation module.
            see enable_op().
        """
        return self.ops_enabled[op_module] 

    def n_ops(self):
        return len(self.cat_op_list) 

    def list_operations(self):
        return [catnm+'.'+opnm for catnm,opnm in self.cat_op_list] 


