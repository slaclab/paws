from collections import OrderedDict
import copy
from functools import partial

from PySide import QtCore

from ..models.QTreeSelectionModel import QTreeSelectionModel
from ..operations import optools
from ..operations.Operation import Operation, Batch, Realtime
from .WfWorker import WfWorker


class Workflow(QTreeSelectionModel):
    """
    Tree structure for a Workflow built from paws Operations.
    """

    def __init__(self,wfman):
        super(Workflow,self).__init__({'select':False,'enable':True})
        self._running = False
        self.wfman = wfman

    # signal to emit when this workflow finishes execution.
    # connects to workflow manager's finish_wf slot.
    # which in turn emits workflow manager's wfdone signal. 
    exec_finished = QtCore.Signal()

    # Signal to emit when the state of this Workflow changes.
    # WfManager connects this to PluginManager
    # so that PluginManager can update the associated WorkflowPlugin
    # whenever this Workflow is updated.
    wf_updated = QtCore.Signal()

    @QtCore.Slot(str,Operation)
    def updateOperation(self,tag,op):
        self.update_op(tag,op)
        # processEvents() after updating an operation
        # so that the application can execute anything 
        # that was queued in the main event loop during the update,
        # such as updating views in the GUI.
        self.wfman.appref.processEvents()

    def is_running(self):
        return self._running

    def stop_wf(self):
        self._running = False

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.item_count())
        else:
            return super(Workflow,self).headerData(section,orientation,data_role)    

    def add_op(self,op_tag,new_op):
        """Add an Operation to the tree at the top level."""
        self.set_item(op_tag,new_op,self.root_index())
        self.wf_updated.emit() 

    def remove_op(self,rm_idx):
        """
        Remove an Operation from the workflow tree.
        """
        p_idx = self.parent(rm_idx)
        if not p_idx == self.root_index():
            msg = '[{}] Called remove_op on non-Operation at QModelIndex {}. \n'.format(__name__,rm_idx)
            raise ValueError(msg)
        rm_itm = self.get_from_idx(rm_idx)
        self.remove_item(rm_itm.tag,p_idx)
        self.wf_updated.emit() 

    def op_dict(self):
        op_names = [itm.tag for itm in self.get_from_idx(self.root_index()).children]
        op_dict = OrderedDict(zip(op_names,[self.get_data_from_uri(nm) for nm in op_names]))
        return op_dict

    def update_op(self,op_tag,new_op):
        """
        Update given uri op_tag to Operation new_op.
        """
        self.set_item(op_tag,new_op,self.root_index())
        self.wf_updated.emit() 

    def tree_update(self,parent_idx,itm_tag,itm_data):
        if isinstance(itm_data,Operation):
            super(Workflow,self).tree_update(parent_idx,itm_tag,self.build_tree(itm_data))
        else:
            super(Workflow,self).tree_update(parent_idx,itm_tag,itm_data)

    def build_tree(self,x):
        if isinstance(x,Operation):
            d = OrderedDict()
            d[optools.inputs_tag] = self.build_tree(x.inputs)
            d[optools.outputs_tag] = self.build_tree(x.outputs)
            return d
        else:
            return super(Workflow,self).build_tree(x) 

    def set_op_input_at_uri(self,uri,val):
        """
        Set an op input, indicated by uri, to provided value.
        uri must be of the form op_name.inputs.input_name.
        Currently shallower uris (e.g. op_name.inputs) 
        and deeper uris (e.g. op_name.inputs.input_list.0)
        are not supported.
        """
        p = uri.split('.')
        op = self.get_data_from_uri(p[0])
        op.inputs[p[2]] = val
        op.input_locator[p[2]].data = val

    # TODO: the following
    def check_wf(self):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        Return a status code and message for each of the Operations.
        """
        pass

    def execution_stack(self):
        """
        Build a stack (list) of lists of Operation uris,
        such that each list indicates a set of Operations
        whose dependencies are satisfied by the Operations above them.
        For Batch or Realtime operations, 
        the layer should be of the form[batch_name,[batch_stack]],
        where batch_name indicates the batch controller Operation,
        and batch_stack is built from self.batch_op_stack().
        """
        stk = []
        valid_wf_inputs = []
        continue_flag = True
        while not optools.stack_size(stk) == self.item_count(self.root_index()) and continue_flag:
            ops_rdy = []
            for itm in self.get_from_idx(self.root_index()).children:
                if not optools.stack_contains(itm.tag,stk):
                    if self.is_op_ready(itm.tag,valid_wf_inputs):
                        ops_rdy.append(itm.tag)
            # Finished building list of ops currently ready. Now filter these into stack.
            if any(ops_rdy):
                # Which of these are not Batch/Realtime ops?
                non_batch_rdy = []
                for op_tag in ops_rdy:
                    op = self.get_data_from_uri(op_tag)
                    if not isinstance(op,Batch) and not isinstance(op,Realtime):
                        non_batch_rdy.append(op_tag)
                if any(non_batch_rdy):
                    ops_rdy = non_batch_rdy
                    stk.append(ops_rdy)
                    for op_tag in ops_rdy:
                        op = self.get_data_from_uri(op_tag)
                        valid_wf_inputs += optools.get_valid_wf_inputs(op_tag,op)
                else:
                    batch_tag = ops_rdy[0]
                    ops_rdy = [batch_tag]
                    batch_op = self.get_data_from_uri(batch_tag)
                    batch_stk,batch_rdy = self.batch_op_stack(batch_tag,valid_wf_inputs)
                    stk.append([batch_tag,batch_stk])
                    valid_wf_inputs += optools.get_valid_wf_inputs(batch_tag,batch_op)
            else:
                continue_flag = False
        #print optools.print_stack(stk)
        return stk

    def print_stack(self,stk):
        stktxt = ''
        opt_newline = '\n'
        for i,lst in zip(range(len(stk)),stk):
            if i == len(stk)-1:
                opt_newline = ''
            first_op = self.get_data_from_uri(lst[0])
            if isinstance(first_op,Batch) or isinstance(first_op,Realtime):
                substk = lst[1]
                stktxt += ('[\'{}\':\n{}\n]'+opt_newline).format(lst[0],self.print_stack(lst[1]))
            else:
                stktxt += ('{}'+opt_newline).format(lst)
        return stktxt

    def is_op_ready(self,op_tag,valid_wf_inputs,batch_routes=[]):
        op = self.get_data_from_uri(op_tag)
        if isinstance(op,Batch):
            b_stk,op_rdy = self.batch_op_stack(op,valid_wf_inputs)
        elif isinstance(op,Realtime):
            rt_stk,op_rdy = self.batch_op_stack(op,valid_wf_inputs)
        else:
            inputs_rdy = []
            for name,il in op.input_locator.items():
                # TODO: Come up with a more airtight set of conditions here.
                # Should possibly check validity on plugin inputs and fs inputs.
                if il.src == optools.wf_input and il.tp == optools.ref_type and not il.val in valid_wf_inputs:
                    inp_rdy = False
                elif il.src == optools.batch_input and not itm.tag()+'.'+optools.inputs_tag+'.'+name in batch_routes:
                    inp_rdy = False
                else:
                    inp_rdy = True
                inputs_rdy.append(inp_rdy)
            if all(inputs_rdy):
                op_rdy = True
            else:
                op_rdy = False
        return op_rdy 

    def batch_op_stack(self,batch_op_tag,valid_wf_inputs):
        """
        Use batch_op.batch_ops() and a list of valid_wf_inputs 
        to build a stack (list) of lists of operations suitable for serial execution.
        """
        batch_op = self.get_data_from_uri(batch_op_tag)
        # Batch and Realtime execution operations expect to have their inputs loaded
        # by optools.load_inputs() before calling realtime_ops() or batch_ops()
        optools.load_inputs(batch_op,self)
        op_tags = []
        if isinstance(batch_op,Realtime):
            #exec_itms = [self.get_from_uri(uri)[0] for uri in b_itm.data.realtime_ops()]
            op_tags = batch_op.realtime_ops()
        elif isinstance(batch_op,Batch):
            #exec_itms = [self.get_from_uri(uri)[0] for uri in b_itm.data.batch_ops()]
            op_tags = batch_op.batch_ops()
        # make a copy of valid_wf_inputs so that the existing valid_wf_inputs list is not mutated 
        valid_batch_inputs = copy.copy(valid_wf_inputs)
        # add the batch's own valid inputs to the list
        valid_batch_inputs += optools.get_valid_wf_inputs(batch_op_tag,batch_op)
        # build the batch substack
        b_stk = []
        layer = []
        for op_tag in op_tags:
            if self.is_op_ready(op_tag,valid_batch_inputs,batch_op.input_routes()):
                layer.append(op_tag)
        while any(layer):
            b_stk.append(layer)
            for op_tag in layer:
                op = self.get_data_from_uri(op_tag)
                valid_batch_inputs += optools.get_valid_wf_inputs(op_tag,op)
            layer = []
            for op_tag in op_tags:
                if self.is_op_ready(op_tag,valid_batch_inputs,batch_op.input_routes()) and not optools.stack_contains(op_tag,b_stk):
                    layer.append(op_tag)
        b_rdy = len(op_tags) == optools.stack_size(b_stk) 
        return b_stk,b_rdy 

    def run_wf(self):
        self._running = True
        stk = self.execution_stack()
        msg = 'STARTING EXECUTION\n----\nexecution stack: \n'
        msg += self.print_stack(stk)
        msg += '\n----'
        self.wfman.write_log(msg)
        batch_flags = [isinstance(self.get_data_from_uri(lst[0]),Batch) for lst in stk]
        rt_flags = [isinstance(self.get_data_from_uri(lst[0]),Realtime) for lst in stk]
        layers_done = 0
        while not layers_done == len(stk): 
            # check if we are at a batch or rt op
            if batch_flags[layers_done]:
                self.run_wf_batch(stk[layers_done][0],stk[layers_done][1])
                layers_done += 1
            elif rt_flags[layers_done]:
                self.run_wf_realtime(stk[layers_done][0],stk[layers_done][1])
                layers_done += 1
            else:
                # get the portion of the stack from here to the next batch or rt op
                if (True in batch_flags[layers_done:]):
                    substk = stk[layers_done:layers_done+batch_flags[layers_done:].index(True)]
                elif (True in rt_flags[layers_done:]):
                    substk = stk[layers_done:layers_done+rt_flags[layers_done:].index(True)]
                else:
                    substk = stk[layers_done:]
                self.run_wf_serial(substk)
                layers_done += len(substk)
        # if not yet interrupted, wait for all threads to finish, then signal done
        if self.is_running():
            self.wfman.wait_for_threads()
            self.wfman.write_log('EXECUTION FINISHED')
            self.exec_finished.emit()

    def run_wf_serial(self,stk,thd_idx=None):
        """
        Serially execute the operations indicated by input stack stk.
        """
        if thd_idx is None:
            thd_idx = self.wfman.next_available_thread()
        for lst in stk:
            self.wfman.wait_for_thread(thd_idx)
            op_dict = OrderedDict() 
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                optools.load_inputs(op,self)
                op_dict[op_tag] = op
            # Copy op_dict so that it can be thread-mobile
            op_dict = copy.deepcopy(op_dict)
            # Make a new Worker, give None parent so that it can be thread-mobile
            wf_wkr = WfWorker(op_dict,None)
            wf_wkr.opDone.connect(self.updateOperation)
            wf_thread = QtCore.QThread(self)
            wf_wkr.moveToThread(wf_thread)
            self.wfman.register_thread(thd_idx,wf_thread)
            wf_thread.started.connect(wf_wkr.work)
            wf_thread.finished.connect( partial(self.wfman.finish_thread,thd_idx) )
            wf_thread.finished.connect(wf_thread.deleteLater)
            wf_thread.finished.connect(wf_wkr.deleteLater)
            wf_thread.start()
            msg = 'running {} in thread {}'.format(lst,thd_idx)
            self.wfman.write_log(msg)
            # TODO: Figure out how to remove this wait_for_thread(). 
            # It should be handled in Workflow.run_wf() 
            self.wfman.wait_for_thread(thd_idx)

    def run_wf_realtime(self,rt_op_tag,rt_stk):
        """
        Execute the operations indicated by stack rt_stk in real time
        under the control of the Realtime Operation indicated by rt_op_tag.
        """
        # TODO: Ensure rt execution runs smoothly on an initially empty input_iter().
        # TODO: Add a way to stop a realtime execution without stopping the whole workflow.
        # TODO: when calling update_op(rt_op), update only the new/changed children of the rt op
        rt_op = self.get_data_from_uri(rt_op_tag) 
        optools.load_inputs(rt_op,self)
        rt_op.run()
        self.update_op(rt_op_tag,rt_op)
        nx = 0
        wait_flag = False
        while self._running:
            # After rt_op.run(), it is expected that rt_op.input_iter()
            # will generate lists of input values that should be routed to rt_op.input_routes(),
            # unless there are no new inputs to run, in which case it will iterate None. 
            vals = rt_op.input_iter().next()
            if not None in vals:
                wait_flag = False
                inp_dict = OrderedDict( zip(rt_op.input_routes(), vals) )
                nx += 1
                for uri,val in inp_dict.items():
                    self.set_op_input_at_uri(uri,val)
                thd_idx = self.wfman.next_available_thread()
                #thd_idx = 0
                self.wfman.write_log( 'REALTIME EXECUTION {} in thread {}'.format(nx,thd))
                self.run_wf_serial(rt_stk,thd_idx)
                # wait for thread to finish before saving results
                self.wfman.wait_for_thread(thd_idx)
                saved_items_dict = OrderedDict()
                for uri in rt_op.saved_items():
                    save_data = self.get_data_from_uri(uri)
                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
                rt_op.output_list().append(saved_items_dict)
                self.update_op(rt_op_tag,rt_op)
            else:
                if not wait_flag:
                    self.wfman.write_log( 'Waiting for new inputs...' )
                    wait_flag = True
                self.wfman.loopwait(rt_op.delay())
        self.wfman.write_log( 'REALTIME EXECUTION TERMINATED' )
        return

    def run_wf_batch(self,batch_op_tag,batch_stk):
        """
        Batch-execute the items indicated by stack batch_stk 
        under the control of the Batch Operation indicated by batch_op_tag.
        """
        # TODO: when calling update_op(batch_op), update only the new/changed children of the batch op
        batch_op = self.get_data_from_uri(batch_op_tag) 
        optools.load_inputs(batch_op,self)
        batch_op.run()
        self.update_op(batch_op_tag,batch_op)
        # After batch_op.run(), it is expected that batch_op.input_list() will refer to a list of dicts,
        # where each dict has the form [workflow tree uri:input value]. 
        for i in range(len(batch_op.input_list())):
            if self._running:
                input_dict = batch_op.input_list()[i]
                for uri,val in input_dict.items():
                    self.set_op_input_at_uri(uri,val)
                thd_idx = self.wfman.next_available_thread()
                #thd_idx = 0
                self.wfman.write_log( 'BATCH EXECUTION {} / {} in thread {}'.format(i+1,len(batch_op.input_list()),thd_idx) )
                self.run_wf_serial(batch_stk,thd_idx)
                # wait for thread to finish before saving results
                self.wfman.wait_for_thread(thd_idx)
                saved_items_dict = OrderedDict()
                for uri in batch_op.saved_items():
                    save_data = self.get_data_from_uri(uri)
                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
                batch_op.output_list()[i] = saved_items_dict
                self.update_op(batch_op_tag,batch_op)
            else:
                self.wfman.write_log( 'BATCH EXECUTION TERMINATED' )
                return
        self.wfman.write_log( 'BATCH EXECUTION FINISHED' )

    def uri_to_embedded_dict(self,uri,data=None):
        path = uri.split('.')
        endtag = path[-1]
        d = OrderedDict()
        d[endtag] = data
        for tag in path[:-1][::-1]:
            parent_d = OrderedDict()
            parent_d[tag] = d
            d = parent_d
        return d

    def update_embedded_dict(self,d,d_new):
        for k,v in d_new.items():
            if k in d.keys():
                if isinstance(d[k],dict) and isinstance(d_new[k],dict):
                    # embedded dicts: recurse
                    d[k] = self.update_embedded_dict(d[k],d_new[k])
                else:
                    # existing d[k] is not dict, and d_new[k] is dict: replace  
                    d[k] = d_new[k]
            else:
                # d[k] does not exist: insert
                d[k] = v
        return d



    #    itm,idx = self.get_from_uri(uri)
    #    od = OrderedDict()
    #    od[itm.tag()] = data
    #    p_idx = self.parent(idx)
    #    # if this is a top level item, return od
    #    if p_idx == self.root_index():
    #        return od
    #    # else, package od under its parent's tag
    #    else:
    #        return self.uri_to_dict(self.build_uri(p_idx),od)

    # TODO: Add checking of plugins (il.src == optools.plugin_input)
    # TODO: Add checking of fs paths (il.src == optools.fs_input)
    #def update_io_deps(self):
    #    """
    #    Remove any broken dependencies in the workflow.
    #    Should only be called after all current data have been stored in the tree. 
    #    """
    #    for r,itm in zip(range(len(self.root_items)),self.root_items):
    #        op = itm.data
    #        op_idx = self.index(r,0,QtCore.QModelIndex())
    #        for name,il in op.input_locator.items():
    #            if il:
    #                if il.src == optools.wf_input and il.tp == optools.ref_type and not self.is_good_uri(il.val):
    #                    #vals = optools.val_list(il)
    #                    #for v in vals:
    #                    #    if not self.is_good_uri(v):
    #                    self.wfman.write_log('--- {}.{}.{} points to bad uri ({}): clearing InputLocator ---'.format(
    #                    itm.tag(),optools.inputs_tag,name,il.val))
    #                    op.input_locator[name] = optools.InputLocator(il.src,il.tp,None)
    #                    self.tree_dataChanged(op_idx)

