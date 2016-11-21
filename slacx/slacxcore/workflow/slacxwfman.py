import os
import time
import traceback
from collections import OrderedDict
import copy

from PySide import QtCore
from functools import partial
import dask.threaded
import yaml

from ..treemodel import TreeModel
from ..treeitem import TreeItem
from ..operations import optools
from ..operations.slacxop import Operation, Batch, Realtime
from ..operations.optools import InputLocator
from .. import slacxtools

class WfManager(TreeModel):
    """
    Class for managing a Workflow built from slacx Operations.
    """

    def __init__(self,**kwargs):
        super(WfManager,self).__init__()
        self.inputs_child_index = 0
        self.outputs_child_index = 1
        if 'logmethod' in kwargs:
            self.logmethod = kwargs['logmethod']
        else:
            self.logmethod = None
        if 'wfl' in kwargs:
            self.load_from_file( kwargs['wfl'] )
        if 'app' in kwargs:
            self.appref = kwargs['app']
        else:
            self.appref = None
        self._wf_dict = {}       
        #print 'system thread count:'
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._wf_threads = dict.fromkeys(range(self._n_threads)) 
        # Set up a flag to indicate whether threads are available.
        self._exec_ready = True 
        if self.logmethod:
            self.logmethod('Slacx workflow manager started, working with {} threads'.format(self._n_threads))

    def load_inputs(self,op):
        """
        Loads data for an Operation from that Operation's input_locator.
        It is expected that op.input_locator[name] will refer to an InputLocator.
        """
        # TODO: Migrate this to slacxop.Operation
        for name,il in op.input_locator.items():
            if isinstance(il,InputLocator):
                src = il.src
                if not src == optools.batch_input:
                    il.data = self.locate_input(il)
                    op.inputs[name] = il.data
                else:
                    # batch executor should have already set the input
                    il.data = op.inputs[name]
            else:
                msg = '[{}] Found broken Operation.input_locator for {}: {}'.format(
                __name__, name, il)
                raise ValueError(msg)

    def locate_input(self,inplocator):
        """
        Return the data pointed to by a given InputLocator object.
        """
        # TODO: Migrate this to slacxop.Operation
        #if isinstance(inplocator,InputLocator):
        src = inplocator.src
        tp = inplocator.tp
        val = inplocator.val
        #print 'called locate_input for src {}, val {}'.format(src,val)
        if src == optools.user_input: 
            if tp == optools.none_type:
                val = None 
            elif tp == optools.int_type:
                val = int(val)
            elif tp == optools.float_type:
                val = float(val)
            elif tp == optools.str_type:
                val = str(val)
            elif tp == optools.bool_type:
                val = bool(val)
            elif tp == optools.list_type:
                # val is expected to be a widget containing the list data
                val = self.list_from_widget(val) 
            else:
                msg = 'type selection {}, should be one of {}'.format(src,optools.valid_types)
                raise ValueError(msg)
            return val
        elif src == optools.wf_input:
            io_type = val.split('.')[1]
            if io_type == 'Outputs':
                # 1) val is a uri pointing to an op output. 
                # Return data by getting it from the uri.
                item, indx = self.get_from_uri(val)
                return item.data
            elif io_type == 'Inputs':
                # 2) val is an input uri, and we should trust that this input has been loaded.
                # Grab the data from the InputLocator at that uri and return it.
                item, indx = self.get_from_uri(val)
                il = item.data 
                return il.data
        elif src == optools.fs_input:
            return val 
        elif src == optools.batch_input:
            # Trust the Batch executor has set the input values.
            # Do nothing, return val.
            return val 
        else: 
            msg = 'found input source {}, should be one of {}'.format(
            src, valid_sources)
            raise ValueError(msg)
        #else:
        #    # if this method gets called on an input that is not an InputLocator,
        #    # do nothing, return the input.
        #    #print 'called locate_input on non-InputLocator: {}'.format(inplocator)
        #    return inplocator


    def load_from_file(self,opman,wfl):
        """
        Load things in to the Workflow from an OpManager and a YAML .wfl file 
        """
        # TODO: Migrate to own module
        # TODO: Clear or store the current workflow
        f = open(wfl, "r")
        dct = yaml.load(f)
        f.close()
        for uri, opdict in dct.items():
            opname = opdict['type']
            op = opman.get_op_byname(opname)()
            ilspec = opdict['Inputs']
            for name, srctypeval in ilspec.items():
                op.input_src[name] = srctypeval['src']
                op.input_type[name] = srctypeval['type']
                il = optools.InputLocator(srctypeval['src'],srctypeval['type'],srctypeval['val'])
                op.input_locator[name] = il
            self.add_op(uri,op)
        #print dct
        
    def save_to_file(self,filename):
        """
        Save the current image of the Workflow as a YAML 
        """
        # TODO: Migrate to own module
        if not os.path.splitext(filename)[1] == '.wfl':
            filename = filename+'.wfl'
        #filename = slacxtools.rootdir+'/'+'test.wfl'
        wf_dict = OrderedDict() 
        #wf_dict = {} 
        for row in range(len(self.root_items)):
            item = self.root_items[row]
            idx = self.index(row,0,QtCore.QModelIndex())
            uri = self.build_uri(idx)
            wf_dict[str(uri)] = self.op_dict(item)
        if self.logmethod:
            self.logmethod( 'dumping current workflow image to {}'.format(filename) )
        f = open(filename, "w")
        #yaml.dump(wf_dict, f, encoding='utf-8')
        yaml.dump(wf_dict, f)
        f.close()
    def op_dict(self,op_item):
        #dct = {}
        dct = OrderedDict() 
        op = op_item.data
        dct['type'] = type(op).__name__ 
        dct['Inputs'] = self.inputs_dict(op)
        #dct['Outputs'] = self.outputs_dict(op)
        return dct
    def inputs_dict(self,op):
        #dct = {}
        dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            dct[name] = {'src':il.src,'type':il.tp,'val':str(il.val)}
        return dct
    def outputs_dict(self,op):
        #dct = {}
        dct = OrderedDict() 
        for name in op.outputs.keys():
            dct[name] = str(op.outputs[name])
        return dct

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
        #self._n_loaded += 1

    def remove_op(self,rm_indx):
        """Remove an Operation from the workflow tree"""
        rm_row = rm_indx.row()
        self.beginRemoveRows(
        QtCore.QModelIndex(),rm_row,rm_row)
        # Removal occurs between notification methods
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        # TODO: update any Operations that depended on the removed one
        if isinstance(item_removed.data,Operation):
            self.update_io_deps(item_removed.tag(),item_removed.data)

    def update_op(self,uri,new_op):
        """
        Replace Operation in treeitem indicated by uri with new_op.
        Clean up any dependencies that are broken in the process.
        """
        item, indx = self.get_from_uri(uri)
        # If an updated op has different io structure, 
        # go through and clobber any broken dependencies.
        current_op = item.data
        self.update_io_deps(uri,current_op,new_op)
        # Put the new op in the treeitem
        item.data = new_op
        item.set_long_tag( new_op.__doc__ )
        # Update the op subtrees
        # TODO: Try this with a call to TreeModel.dataChanged() instead?
        self.build_io_subtrees(new_op,indx)

    def update_io_deps(self,uri,current_op,new_op=None):
        """
        Explicitly remove any broken dependencies in the workflow
        created by replacing current_op with new_op.
        Provide no new_op (defaults to None) if current_op is being removed.
        """
        if not new_op:
            for nm in current_op.inputs.keys():
                inp_uri = uri+'.Inputs.'+nm
                self.remove_input_deps(inp_uri)
            for nm in current_op.outputs.keys():
                out_uri = uri+'.Outputs.'+nm
                self.remove_input_deps(out_uri)
        else:
            for nm in current_op.inputs.keys():
                # check if new_op has different inputs...
                if not nm in new_op.inputs.keys() or (
                nm in new_op.inputs.keys() and not (
                current_op.input_src[nm] == new_op.input_src[nm]
                and current_op.input_type[nm] == new_op.input_type[nm]
                and current_op.input_locator[nm].val == new_op.input_locator[nm].val )):
                    inp_uri = uri+'.Inputs.'+nm
                    self.remove_input_deps(inp_uri)
            for nm in current_op.outputs.keys():
                # repeat the process for new_op outputs...
                if not nm in new_op.outputs.keys():
                    out_uri = uri+'.Outputs.'+nm
                    self.remove_input_deps(out_uri)

    def remove_input_deps(self,uri):
        # Loop through the ops.
        for row in range(len(self.root_items)):
            item = self.root_items[row]
            op = item.data
            idx = self.index(row,0,QtCore.QModelIndex())
            # If any input locators are set to this uri, clobber them.
            for name,il in op.input_locator.items():
                if il.val == uri:
                    op.input_locator[name] = optools.InputLocator()
                    # Update the op that has been changed.
                    # TODO: Do this with a call to TreeModel.dataChanged()?
                    self.build_io_subtrees(op,indx)

    def list_from_widget(self,widg):
        print '[{}]: need to implement list_from_widget'.format(__name__)
        return None

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
        self.build_from_dict(op.input_locator,inputs_indx)
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

    # Overload columnCount()
    def columnCount(self,parent):
        """Let WfManager have two columns, one for item tag, one for item type"""
        return 2

    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        Return a status code and message for each of the Operations.
        """
        pass

    def find_batch_items(self):
        batch_items = [] 
        for item in self.root_items:
            if isinstance(item.data,Batch):
               batch_items.append(item)
        return batch_items 

    def find_rt_items(self):
        rt_items = [] 
        for item in self.root_items:
            if isinstance(item.data,Realtime):
               rt_items.append(item)
        return rt_items 

    def run_and_update(self,item):
        """
        Run the Operation at item.data and update its data in the tree
        """
        op = item.data
        self.load_inputs(op)
        if self.logmethod:
            self.logmethod('Running {}'.format(str(item.tag())))
        #op_thread = slacxtools.OpExecThread(op,self)
        #op_thread.start()
        op.run()
        self.update_op(item.tag(),op)

    def run_deps(self,item):
       deps = self.upstream_list(item)
       if deps:
           if self.logmethod:
               self.logmethod('Running dependencies for {}: {}'.format(item, [dep.tag() for dep in deps]))
           for dep in deps:
               self.run_and_update(item)

    def run_wf(self):
        if self.find_rt_items():
            self.run_wf_realtime()
        elif self.find_batch_items():
            self.run_wf_batch()
        else:
            self.run_wf_serial()

    def next_available_thread(self):
        for idx,th in self._wf_threads.items():
            if not th:
                self._exec_ready = True
                return idx
        self._exec_ready = False
        return None

    def run_wf_serial(self,to_run=None):
        """
        Run the workflow by building a serial dependency list 
        and running the listed operations in order. 
        """
        if self.logmethod:
            self.logmethod('starting serial execution.')
        if not to_run:
            to_run = self.serial_execution_list()
        # Find the next available thread
        th_idx = self.next_available_thread()
        while not self._exec_ready:
            # Check again in a few seconds    
            time.sleep(3)
            if self.logmethod:
                self.logmethod('Found no threads available, waiting...')
            th_idx = self.next_available_thread()
        wf_wkr = slacxtools.WfWorker(self,to_run)
        #wf_thread = QtCore.QThread(self)
        #wf_wkr.moveToThread(wf_thread)
        #self._wf_threads[th_idx] = wf_thread
        #if self.logmethod:
        #    self.logmethod('Starting execution in thread {}.'.format(th_idx))
        #wf_thread.started.connect(wf_wkr.work)
        #wf_thread.finished.connect( partial(self.finish_thread,th_idx) )
        #import pdb; pdb.set_trace()
        #wf_thread.start()
        wf_wkr.work()

    def finish_thread(self,th_idx):
        print 'finished execution in thread {}.'.format(th_idx)
        if self.logmethod:
            self.logmethod('finished execution in thread {}.'.format(th_idx))
        self._wf_threads[th_idx].quit()
        #self._wf_threads[th_idx].exit(0)
        self._wf_threads[th_idx] = None

    def run_wf_realtime(self):
        """
        Executes the workflow under the control of the local Realtime(Operation) instances
        """
        rt_items = self.find_rt_items() 
        if not rt_items:
            msg = '[{}] Attempted real-time execution, could not find realtime controller'.format(__name__)
            if self.logmethod:
                self.logmethod(msg)
            raise ValueError(msg)
        else:
            for rt_item in rt_items:
                if self.logmethod:
                    self.logmethod( 'Running dependencies... ' )
                self.run_deps(rt_item)
                if self.appref:
                    self.appref.processEvents()
                if self.logmethod:
                    self.logmethod( 'Preparing Realtime controller... ' )
                self.run_and_update(rt_item)
                if self.appref:
                    self.appref.processEvents()
            #try:
            if self.logmethod:
                self.logmethod( 'To infinity... ' )
            while True:
                for rt_item in rt_items:
                    rt = rt_item.data
                    # After rt.run(), it is expected that rt.input_iter()
                    # will iterate lists of input values whose respective routes are rt.input_routes().
                    # unless there are no new inputs to run, in which case it will iterate None. 
                    vals = rt.input_iter().next()
                    inp_dict = dict( zip(rt.input_routes(), vals) )
                    print 'next inputs:'
                    print inp_dict
                    #for i in range(len(rt.input_list())):
                    #    input_dict = batch_maker.input_list()[i]
                    if inp_dict and not None in vals:
                        for uri,val in inp_dict.items():
                            self.set_op_input_at_uri(uri,val)
                        #to run = rt.downstream_ops()
                        to_run = self.downstream_ops(rt_item)
                        self.run_wf_serial(to_run)
                        rt.output_list().append(self.ops_as_dict(to_run))
                        # Update rt to load results
                        self.update_op(rt_item.tag(),rt)
                    if self.appref:
                        self.appref.processEvents()
                    # sleep as long as the rt controller says
                    time.sleep(rt.delay())
            #except UserPushedStopButtonException as ex:
            #   exit gracefully
            #except Exception as ex:
            #    ex.message = 'Realtime execution seems to have failed. Error message: {}'.format(ex.message)
            #    # Save any work that did finish:
            #    self.update_op(rt_item.tag(),rt)
            #    tb = traceback.format_exc()
            #    if self.logmethod:
            #        self.logmethod(ex.message)
            #        self.logmethod(tb)
            #    raise ex

    def run_wf_batch(self):
        """
        Executes the workflow under the control of the local Batch(Operation) instances
        """
        b_items = self.find_batch_items() 
        if not b_items:
            msg = '[{}] Attempted batch execution, could not find batch controller'.format(__name__)
            if self.logmethod:
                self.logmethod(msg)
            raise ValueError(msg)
        else:
            for b_item in b_items:
                if self.logmethod:
                    self.logmethod( 'Running dependencies... ' )
                self.run_deps(b_item)
                if self.appref:
                    self.appref.processEvents()
                if self.logmethod:
                    self.logmethod( 'Preparing Batch controller... ' )
                self.run_and_update(b_item)
                if self.appref:
                    self.appref.processEvents()
                b = b_item.data
                # After b.run(), it is expected that b.input_list()
                # will produce a list of dicts, where each dict has the form [workflow tree uri:input value]. 
                #try:
                for i in range(len(b.input_list())):
                    input_dict = b.input_list()[i]
                    for uri,val in input_dict.items():
                        self.set_op_input_at_uri(uri,val)
                    # Inputs are set, run in serial 
                    if self.logmethod:
                        self.logmethod( 'Running batch {} / {}'.format(i,len(b.input_list())-1) )
                    #to run = b.downstream_ops()
                    to_run = self.downstream_ops(b_item)
                    self.run_wf_serial(to_run)
                    b.output_list()[i]=self.ops_as_dict(to_run)
                    self.update_op(b_item.tag(),b)
                    if self.appref:
                        self.appref.processEvents()
                # Update b to load results
                self.update_op(b_item.tag(),b)
                if self.logmethod:
                    self.logmethod( 'Batch execution complete.' )
                #except Exception as ex:
                #    ex.message = 'Batch seems to have failed. Error message: {}'.format(ex.message)
                #    # Save any work that did finish:
                #    self.update_op(b_item.tag(),b)
                #    tb = traceback.format_exc()
                #    if self.logmethod:
                #        self.logmethod(ex.message)
                #        self.logmethod(tb)
                #    raise ex

    def set_op_input_at_uri(self,uri,val):
        """Set an op input, indicated by uri, to provided value."""
        path = uri.split('.')
        if not len(path) == 3:
            msg = 'uri {} should have format Operation.Inputs.inputname'.format(uri)
            raise ValueError(msg)
        op_itm, idx = self.get_from_uri(path[0])
        op = op_itm.data
        if path[1] == 'Inputs' and path[2] in op.inputs.keys():
            op.inputs[path[2]] = val
        else:
            msg = 'uri {} does not specify Inputs, or specifies an invalid inputname'.format(uri)
            raise ValueError(msg)

    def ops_as_dict(self,op_items=None):
        od = OrderedDict()
        if not op_items:
            op_items = self.root_items
        for item in op_items:
            od[item.tag()] = copy.deepcopy(item.data)
            #print 'od[{}]: inputs {}'.format(item.tag(),item.data.inputs)
        return od

    def upstream_list(self,root_item):
        """
        Get an ordered list of Operation-containing items, 
        such that their serial execution will provide consistent dependencies,
        satisfying eventually the dependencies of provided root_item. 
        """
        ordered_items = [root_item]
        done = False
        while not done:
            done = True
            for item in ordered_items:
                op = item.data
                for name in op.inputs.keys():
                    # Check if this input is supposed to come from a field in another Operation
                    src = op.input_src[name]
                    if src == optools.wf_input:
                        # Check whether or not this is an Output field 
                        uri = op.input_locator[name].val
                        op_tag = uri.split('.')[0]
                        io_tag = uri.split('.')[1]
                        op_item, indx = self.get_from_uri(op_tag)
                        if io_tag == 'Outputs' and not op_item in ordered_items:
                            ordered_items.insert(0,op_item)
                            done = False
        # Remove root_item from the end
        ordered_items.pop(-1)
        return ordered_items

    def serial_execution_list(self):
        ordered_items = []
        for item in self.root_items:
            op = item.data
            if not optools.wf_input in [src for name,src in op.input_src.items()]:
                ordered_items.append(item)
        next_items = self.items_ready(ordered_items)
        while next_items:
            ordered_items = ordered_items + next_items
            next_items = self.items_ready(ordered_items)
        return ordered_items

    def downstream_ops(self,op_item):
        """
        Give the list of Operations downstream of a given Operation.
        The input Operation should have an implementation of input_routes(),
        as in for example the Batch and Realtime base classes.
        """
        ds_items = []
        op = op_item.data
        # Get uris of inputs that will be set by the op 
        inroutes = op.input_routes()
        for uri in inroutes:
            in_op_tag = uri.split('.')[0]
            in_op_item, indx = self.get_from_uri(in_op_tag)
            # Exclude Batches and Realtimes from downstream ops.
            # TODO: Consider how / whether embedded Batches / Realtimes should work
            if ( not isinstance(in_op_item.data,Batch)
            and not isinstance(in_op_item.data,Realtime) ):
                ds_items.append(in_op_item)
        next_items = self.items_ready(ds_items)
        while next_items:
            next_items = self.items_ready(ds_items)
            pop_list = []
            for i in range(len(next_items)):
                in_item = next_items[i]
                if isinstance(in_item.data,Batch) or isinstance(in_item.data,Realtime):
                    pop_list.append(i)
                else:
                    ds_items.append(in_item)
            for idx in pop_list:
                next_items.pop(idx)
        return ds_items

    def items_ready(self,items_done):
        """
        Give a list of Operations whose inputs are satisfied, given items_done
        """
        rdy = []
        for item in self.root_items:
            op = item.data
            op_rdy = True
            for name,src in op.input_src.items():
                if src == optools.wf_input:
                    # Get the uri for this input
                    inp_uri = op.input_locator[name].val
                    uri_fields = inp_uri.split('.')
                    op_uri = uri_fields[0]
                    # Get the op.inout.name three-level uri
                    uri_tl = uri_fields[0]+'.'+uri_fields[1]+'.'+uri_fields[2] 
                    # Check that the op exists in items_done 
                    if not op_uri in self.list_tags(QtCore.QModelIndex()): 
                        op_rdy = False
                    # TODO: I think the second of these two checks is the more complete.
                    # Remove the first one when all is vetted at some future date.
                    if not self.is_good_uri(uri_tl):
                        op_rdy = False
            if not item in items_done and op_rdy:
                rdy.append(item)
        return rdy 

    def get_from_uri(self, uri):
        """Get from this tree the item at the given uri."""
        path = uri.split('.')
        parent_indx = QtCore.QModelIndex()
        try:
            for itemuri in path:
                # get QModelIndex of item 
                row = self.list_tags(parent_indx).index(itemuri)
                qindx = self.index(row,0,parent_indx)
                # get TreeItem from QModelIndex
                item = self.get_item(qindx)
                # set new parent in case the path continues...
                parent_indx = qindx
            return item, qindx
        except Exception as ex:
            msg = '-----\nbad uri: {}\n-----'.format(uri)
            raise ex(msg+ex.message)

    def next_uri(self,prefix):
        indx = 0
        goodtag = False
        while not goodtag:
            testtag = prefix+'_{}'.format(indx)
            if not testtag in self.list_tags(QtCore.QModelIndex()):
                goodtag = True
            else:
                indx += 1
        return testtag
                    
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

