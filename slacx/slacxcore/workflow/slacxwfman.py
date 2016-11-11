from PySide import QtCore
import dask.threaded
from collections import OrderedDict

from ..treemodel import TreeModel
from ..treeitem import TreeItem
from ..operations import optools
from ..operations.slacxop import Operation, Batch
from ..operations.optools import InputLocator
from .slacxwf import Workflow

# TODO: See note on remove_op()

class WfManager(TreeModel):
    """
    Class for managing a Workflow(Operation) built from slacx Operations.
    """

    def __init__(self,**kwargs):
        self._n_loaded = 0 
        #TODO: build a saved tree from kwargs
        #if 'wf_loader' in kwargs:
        #    with f as open(wf_loader,'r'): 
        #        self.load_from_file(f)
        self._wf_dict = {}       # this will be a dict for a dask.threaded graph 
        super(WfManager,self).__init__()
        if 'logmethod' in kwargs:
            self.logmethod = kwargs['logmethod']
        else:
            self.logmethod = None
        self.inputs_child_index = 0
        self.outputs_child_index = 1

    def add_op(self,uri,new_op):
        """Add an Operation to the tree as a new top-level TreeItem."""
        # Count top-level rows by passing parent=QModelIndex()
        ins_row = self.rowCount(QtCore.QModelIndex())
        # Make a new TreeItem, column 0, invalid parent 
        new_treeitem = TreeItem(ins_row,0,QtCore.QModelIndex())
        new_treeitem.data = new_op
        new_treeitem.set_tag( uri )
        new_treeitem.set_long_tag( new_op.__doc__ )
        self.beginInsertRows(
        QtCore.QModelIndex(),ins_row,ins_row)
        # Insertion occurs between notification methods
        self.root_items.insert(ins_row,new_treeitem)
        self.endInsertRows()
        # Render Operation inputs and outputs as children
        indx = self.index(ins_row,0,QtCore.QModelIndex())
        self.io_subtree(new_op,indx)
        self._n_loaded += 1

    def update_op(self,uri,new_op):
        """
        Replace Operation in treeitem indicated by uri with new_op.
        Then, ensure that any dependencies broken in the process are reset to their defaults.
        """
        item, indx = self.get_from_uri(uri)
        # If an updated op has different io structure, 
        # go through and clobber any broken dependencies.
        current_op = item.data
        for nm in current_op.inputs.keys():
            if not nm in new_op.inputs.keys():
                inp_uri = uri+'.Inputs.'+nm
                self.remove_input_locators(inp_uri)
        for nm in current_op.outputs.keys():
            if not nm in new_op.outputs.keys():
                out_uri = uri+'.Outputs.'+nm
                self.remove_input_locators(out_uri)
        # Put the new op in the treeitem
        item.data = new_op
        item.set_long_tag( new_op.__doc__ )
        # Update the op subtrees
        self.build_io_subtrees(new_op,indx)

    def remove_input_locators(self,uri):
        # Loop through the ops.
        for item in self.root_items:
            op = item.data
            # If any input locators are set to this uri, clobber them.
            for name,il in op.input_locator.items():
                if il:
                    if il.val == uri:
                        op.input_locator[name] = None             

    def io_subtree(self,op,parent):
        """Add inputs and outputs subtrees as children of an Operation TreeItem"""
        # Get a reference to the parent item
        p_item = parent.internalPointer()
        # TreeItems as placeholders for inputs, outputs lists
        inputs_treeitem = TreeItem(self.inputs_child_index,0,parent)
        inputs_treeitem.set_tag('Inputs')
        inputs_treeitem.set_long_tag('Operation Inputs')
        outputs_treeitem = TreeItem(self.outputs_child_index,0,parent)
        outputs_treeitem.set_tag('Outputs')
        outputs_treeitem.set_long_tag('Operation Outputs')
        # Insert the new TreeItems
        self.beginInsertRows(parent,self.inputs_child_index,self.outputs_child_index)
        p_item.children.insert(self.inputs_child_index,inputs_treeitem)
        p_item.children.insert(self.outputs_child_index,outputs_treeitem)
        self.endInsertRows()
        # Populate the new TreeItems with op.inputs and op.outputs
        self.build_io_subtrees(op,parent)

    def build_io_subtrees(self,op,parent):
        # Get a reference to the parent (operation root) item
        p_item = parent.internalPointer()
        # Get references to the inputs and outputs subtrees
        inputs_treeitem = p_item.children[self.inputs_child_index]
        outputs_treeitem = p_item.children[self.outputs_child_index]
        # Get the QModelIndexes of the subtrees 
        inputs_indx = self.index(self.inputs_child_index,0,parent)
        outputs_indx = self.index(self.outputs_child_index,0,parent)
        # Eliminate any existing children
        nc_i = inputs_treeitem.n_children()
        nc_o = outputs_treeitem.n_children()
        self.removeRows(0,nc_i,inputs_indx)
        self.removeRows(0,nc_o,outputs_indx)
        # Build io trees from io dicts:
        self.build_from_dict(op.inputs,inputs_indx)
        self.build_from_dict(op.outputs,outputs_indx)
        # Now go through and set_long_tag for the op inputs and outputs
        for name, val in op.inputs.items():
            uri = p_item.tag()+'.Inputs.'+name
            item, indx = self.get_from_uri(uri)
            item.set_long_tag( optools.parameter_doc(name,val,op.input_doc[name]) )
        for name, val in op.outputs.items():
            uri = p_item.tag()+'.Outputs.'+name
            item, indx = self.get_from_uri(uri)
            item.set_long_tag( optools.parameter_doc(name,val,op.output_doc[name]) )

    def build_from_dict(self,d,parent):
        print 'called build_from_dict on:'
        print d
        n_items = len(d)
        self.beginInsertRows(parent,0,n_items-1)
        p_item = parent.internalPointer()
        i=0
        for name,val in d.items():
            d_item = TreeItem(i,0,parent)
            d_item.set_tag(name)
            d_item.data = val
            p_item.children.insert(i,d_item)
            self.build_next(val,self.index(i,0,parent))
            i += 1
        self.endInsertRows()

    def build_from_list(self,l,parent):
        print 'called build_from_list on:'
        print l
        n_items = len(l)
        self.beginInsertRows(parent,0,n_items-1)
        p_item = parent.internalPointer()
        for i in range(n_items):
            name = str(i)
            val = l[i]
            l_item = TreeItem(i,0,parent)
            l_item.set_tag(name)
            l_item.data = val
            p_item.children.insert(i,l_item)
            self.build_next(val,self.index(i,0,parent))
        self.endInsertRows()
       
    def build_next(self,val,parent): 
        if isinstance(val,Operation):
            self.io_subtree(val,parent)
        elif isinstance(val,dict):
            self.build_from_dict(val,parent)
        elif isinstance(val,list):
            self.build_from_list(val,parent)
        else:
            pass

        #self.beginInsertRows(outputs_indx,0,n_outputs-1)
        #for i in range(n_outputs):
        #    name,val = output_items[i]
        #    out_treeitem = TreeItem(i,0,outputs_indx)
        #    out_treeitem.set_tag(name)
        #    out_treeitem.set_long_tag( optools.parameter_doc(name,val,op.output_doc[name]) )
        #    out_treeitem.data = val
        #    outputs_treeitem.children.insert(i,out_treeitem)
        #self.endInsertRows()

    def remove_op(self,rm_indx):
        """Remove an Operation from the workflow tree"""
        rm_row = rm_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),rm_row,rm_row)
        # Removal occurs between notification methods
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        # TODO: update any Operations that depended on the removed one

    # Overloaded data() for WfManager
    def data(self,item_indx,data_role):
        if (not item_indx.isValid()):
            return None
        item = item_indx.internalPointer()
        if item_indx.column() == 1:
            if item.data is not None:
                if ( isinstance(item.data,Operation)
                    or isinstance(item.data,list)
                    or isinstance(item.data,dict) ):
                    return type(item.data).__name__ 
                else:
                    return ' '
            else:
                return ' '
        else:
            return super(WfManager,self).data(item_indx,data_role)

    # Overloaded headerData() for WfManager 
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.rowCount(QtCore.QModelIndex()))
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return "type"
        else:
            return None

    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        Return a status code and message for each of the Operations.
        """
        pass

    def find_batch_item(self):
        #hasbatch = False
        for item in self.root_items:
            #if item.data:
            if isinstance(item.data,Batch):
                return item 
        return None

    def run_wf_batch(self):
        """
        Executes the workflow for each of the inputs provided by a Batch(Operation)
        """
        # Find the batch input maker
        # TODO: Deal with multiple batch executors
        batch_maker_item = self.find_batch_item() 
        if not batch_maker_item:
            msg = '[{}] Attempted batch execution, could not find batch input'.format(__name__)
            if self.logmethod:
                self.logmethod(msg)
            raise ValueError(msg)
        else:
            batch_maker = batch_maker_item.data
        # Run any dependencies of the batch inputs
        dep = self.dependency_list(batch_maker_item)
        if self.logmethod:
            self.logmethod('Running batch execution dependencies: {}'.format([item.tag() for item in dep]))
        for item in dep:
            op = item.data
            #if self.logmethod:
            #    self.logmethod('Loading inputs for {}: {}'.format(str(item.tag()),type(op).__name__))
            self.load_inputs(op)
            if self.logmethod:
                self.logmethod('Running {}: {}'.format(str(item.tag()),type(op).__name__))
            op.run()
            #if self.logmethod:
            #    self.logmethod('Updating {}: {}'.format(str(item.tag()),type(op).__name__))
            self.update_op(item.tag(),op)
        # Build the batch. After batch_maker.run(), it is expected that batch_maker.input_list()
        # will produce a list of dicts, where each dict has the form [workflow tree uri:input value]. 
        if self.logmethod:
            self.logmethod('Running batch maker {}: {}'.format(
                str(batch_maker_item.tag()),type(batch_maker).__name__))
        self.load_inputs(batch_maker)
        batch_maker.run()
        self.update_op(batch_maker_item.tag(),batch_maker)
        try:
            for i in range(len(batch_maker.input_list())):
                input_dict = batch_maker.input_list()[i]
                #print 'input dict {}:'.format(i)
                #print input_dict
                for uri,val in input_dict.items():
                    optag = uri.split('.')[0]
                    inptag = uri.split('.')[2]
                    item, indx = self.get_from_uri(optag)
                    op = item.data
                    op.inputs[inptag] = val
                # Inputs are set, run in serial 
                if self.logmethod:
                    self.logmethod( 'Running batch {} / {}'.format(i,len(batch_maker.input_list())-1) )
                to_run = self.dependency_list()
                # Remove batch maker from the operations to run
                to_run.pop(to_run.index(self.find_batch_item()))
                # Execute the remaining ops in serial
                self.run_wf_serial(to_run)
                # Save dict of outputs in batch_maker.output_list()
                batch_maker.output_list()[i]=self.wf_as_dict(to_run)
            # Update batch maker to load results
            self.update_op(batch_maker_item.tag(),batch_maker)
        except Exception as ex:
            msg = 'Batch seems to have failed. Error message: {}'.format(ex.message)
            # Save any work that did finish:
            self.update_op(batch_maker_item.tag(),batch_maker)
            if self.logmethod:
                self.logmethod(msg)
            print msg
            raise ex

    def wf_as_dict(self,op_items=None):
        od = OrderedDict()
        if not op_items:
            op_items = self.root_items
        for item in op_items:
            od[item.tag()] = item.data
        return od
            #uri = item.tag()+'.Outputs'
            #outputs_item = item.children[self.outputs_child_index]
            #for output_item in outputs_item.children:
            #    uri = uri+'.'+output_item.tag()
            #    od[uri] = output_item.data

    def dependency_list(self,root_item=None):
        """
        Get an ordered list of Operation-containing items, 
        such that their serial execution will provide consistent dependencies,
        satisfying eventually the dependencies of provided Operation-containing root_item. 
        If no root_item is given, a serial execution list for the entire workflow is returned.
        """
        ordered_items = []
        if root_item:
            ordered_items.insert(0,root_item)
            done = False
            while not done:
                #print 'ordered items:'
                #print [item.tag() for item in ordered_items]
                done = True
                for item in ordered_items:
                    #print 'seeking dependencies for item {}'.format(item.tag())
                    op = item.data
                    #print 'item.data type: {}'.format(type(op).__name__)
                    for name in op.inputs.keys():
                        src = op.input_src[name]
                        if src == optools.op_input:
                            op_tag = op.input_locator[name].val.split('.')[0]
                            io_tag = op.input_locator[name].val.split('.')[1]
                            if io_tag == 'Outputs':
                                op_item, indx = self.get_from_uri(op_tag)
                                if not op_item in ordered_items:
                                    #print 'item {} depends on item {}'.format(item.tag(),op_item.tag())
                                    ordered_items.insert(0,op_item)
                                    done = False
                                #else:
                                #    print 'item {} is already in the dependency list'.format(op_item.tag())
            # At the end, remove root_item from the end, so it does not appear self-dependent.
            ordered_items.pop(-1)
        else:
            # Loop through operations. If no input source is optools.op_input, append.
            for item in self.root_items:
                op = item.data
                if not optools.op_input in [src for name,src in op.input_src.items()]:
                    ordered_items.append(item)
                    #print '[{}] item {} has no workflow-dependent inputs'.format(__name__,item)
            next_items = self.items_ready(ordered_items)
            while next_items:
                for item in next_items:
                    #print '[{}] item {} has satisfied input dependencies'.format(__name__,item)
                    ordered_items.append(item)
                next_items = self.items_ready(ordered_items)
        return ordered_items

    def items_ready(self,items_done):
        """
        Give a list of Operations whose inputs are satisfied, given items_done
        """
        rdy = []
        for item in self.root_items:
            op = item.data
            op_rdy = True
            for inpname in op.inputs.keys():
                if op.input_src[inpname] == optools.op_input:
                    # Get the uri for this input
                    inp_uri = op.input_locator[inpname].val
                    # Check that the uri points to a thing that exists in this workflow
                    if not self.is_good_uri(inp_uri):
                        op_rdy = False
            if not item in items_done and op_rdy:
                rdy.append(item)
        return rdy 

    def run_wf_serial(self,to_run=None):
        """
        Run the workflow by building a serial dependency list 
        and running the listed operations in order. 
        """
        # TODO: Execute workflow in its own thread.
        if self.logmethod:
            self.logmethod('starting serial execution.')
        if not to_run:
            to_run = self.dependency_list()
        #if self.logmethod:
        #    self.logmethod('Order of operations: {}'.format([str(item.tag()) for item in to_run]))
        for item in to_run:
            op = item.data
            #if self.logmethod:
            #    self.logmethod('Loading inputs for {}: {}'.format(item.tag(),type(op).__name__))
            self.load_inputs(op)
            if self.logmethod:
                self.logmethod('Running {}: {}'.format(item.tag(),type(op).__name__))
            op.run()
            self.update_op(item.tag(),op)
        if self.logmethod:
            self.logmethod('finished serial execution.')

    def load_inputs(self,op):
        print '--- load inputs ---'
        for name,val in op.input_locator.items():
            print 'before load: input {} = {}'.format(name,op.inputs[name])
            if isinstance(val,InputLocator):
                val.data = self.locate_input(val)
                op.inputs[name] = val.data
            #else:
            # No inputLocator for this input. 
            # Do nothing and trust the input to be set by other means.
            print 'after load: input {} = {}'.format(name,op.inputs[name])
        print '--- end load inputs ---'

    def run_wf_graph(self):
        """
        Run the workflow by building a dask-compatible dict,
        then calling dask.threaded.get(dict, key)
        for each of the keys corresponding to operation outputs.
        TODO: optimize the execution of this by making the smallest
        possible number of calls to get().
        """
        # build the graph, get the list of outputs
        outputs_list = self.load_wf_dict()
        print 'workflow graph as dict:'
        print self._wf_dict

    def is_good_uri(self,uri):
        path = uri.split('.')
        parent_indx = QtCore.QModelIndex()
        for itemuri in path:
            try:
                row = self.list_tags(parent_indx).index(itemuri)
            except ValueError as ex:
                return False
            qindx = self.index(row,0,parent_indx)
            # get TreeItem from QModelIndex
            item = self.get_item(qindx)
            # set new parent in case the path continues...
            parent_indx = qindx
        return True

    def load_wf_dict(self):
        """
        Build a dask-compatible dictionary from the Operations in this tree
        """
        self._wf_dict = {}
        for j in range(len(self.root_items)):
            item = self.root_items[j]
            # Unpack the Operation
            op = item.data
            keyindx = 0
            input_keys = [] 
            input_vals = ()
            for name,val in op.inputs.items():
                # Add a locate_input line for each input 
                dask_key = 'op'+str(j)+'inp'+str(keyindx)
                self._wf_dict[dask_key] = (self.locate_input, val)
                keyindx += 1
                input_keys.append(name)
                input_vals = input_vals + (dask_key)
            # Add a set_inputs line for op j
            dask_key = 'op'+str(j)+'_load'
            self._wf_dict[key] = (self.set_inputs, op, input_keys, input_vals) 
            # Add a run_op line for op j
            dask_key = 'op'+str(j)+'_run'
            self._wf_dict[key] = (self.run_op, op) 
            # Keep track of the keys corresponding to operation outputs.
            keyindx = 0
            output_keys = []
            for name,val in op.outputs.items():
                # Add a get_output line for each output
                dask_key = 'op'+str(j)+'out'+str()
                self._wf_dict[dask_key] = (self.get_output, val)
                keyindx += 1
                output_keys.append(name)

    @staticmethod
    def set_inputs(op,keys,vals):
        """
        By the time this is called, vals should be bound to actual input values by dask.
        Each dask key should have been assigned to a (self.locate_input, val)
        """
        for i in range(len(keys)):
            key = keys[i]
            val = vals[i] 
            op.inputs[key] = val
        return op 

    @staticmethod
    def run_op(op):
        return op.run()

    def locate_input(self,inplocator):
        """
        Return the data pointed to by a given InputLocator object.
        If this is called on anything other than an InputLocator,
        it does nothing and returns the input argument.
        """
        #if type(inplocator).__name__ == 'InputLocator':
        if isinstance(inplocator,InputLocator):
            src = inplocator.src
            val = inplocator.val
            print 'called locate_input for src {}, val {}'.format(src,val)
            if src in optools.valid_sources:
                if (src == optools.fs_input
                or src == optools.text_input): 
                    return val 
                elif src == optools.op_input:
                    io_type = val.split('.')[1]
                    # So far this supports two scenarios:
                    if io_type == 'Outputs':
                        # 1) val is a uri pointing to an op output. 
                        # Return data by getting it from the uri.
                        item, indx = self.get_from_uri(val)
                        return item.data
                    elif io_type == 'Inputs':
                        # 2) val is an input uri for setting values during execution.
                        # Return the uri directly.
                        return val
            else: 
                msg = 'found input source {}, should be one of {}'.format(
                src, valid_sources)
                raise ValueError(msg)
        else:
            # if this method gets called on an input that is not an InputLocator,
            # do nothing, return the input.
            print 'called locate_input on non-InputLocator: {}'.format(inplocator)
            return inplocator

    def get_from_uri(self, uri):
        path = uri.split('.')
        parent_indx = QtCore.QModelIndex()
        for itemuri in path:
            # get QModelIndex of item 
            row = self.list_tags(parent_indx).index(itemuri)
            qindx = self.index(row,0,parent_indx)
            # get TreeItem from QModelIndex
            item = self.get_item(qindx)
            # set new parent in case the path continues...
            parent_indx = qindx
        return item, qindx

    def next_uri(self,prefix):
        indx = 0
        goodtag = False
        while not goodtag:
            testtag = prefix+'{}'.format(indx)
            if not testtag in self.list_tags(QtCore.QModelIndex()):
                goodtag = True
            else:
                indx += 1
        return testtag
                    
    # Overload columnCount()
    def columnCount(self,parent):
        """Let WfManager have two columns, one for item tag, one for item type"""
        return 2

