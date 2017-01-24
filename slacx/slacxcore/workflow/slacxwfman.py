from collections import OrderedDict
import copy
from functools import partial

from PySide import QtCore

from ..treemodel import TreeModel
from ..treeitem import TreeItem
from ..operations import optools
from ..operations.slacxop import Operation, Batch, Realtime
from .. import slacxtools
from .slacxwfworker import WfWorker

class WfManager(TreeModel):
    """
    Tree structure for managing a Workflow built from slacx Operations.
    """

    wfdone = QtCore.Signal()

    @QtCore.Slot(str,Operation)
    def updateOperation(self,tag,op):
        self.update_op(tag,op)

    def __init__(self,qapp_reference,plugin_manager,**kwargs):
        super(WfManager,self).__init__()
        # reference to app for helping thread control
        self.appref = qapp_reference 
        self.plugman = plugin_manager
        self._wf_dict = {}       
        # Flags to assist in thread control
        self._running = False
        self._n_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)) 
        #self._n_threads = QtCore.QThread.idealThreadCount()
        self.logmethod = None

    def write_log(self,msg):
        if self.logmethod:
            self.logmethod(msg)
        else:
            print(msg)
        if self.appref:
            self.appref.processEvents()

    def load_from_dict(self,opman,opdict):
        """
        Load things in to the Workflow from an OpManager
        using a dict that specifies operation setup.
        """
        while self.root_items:
            idx = self.index(self.rowCount(QtCore.QModelIndex())-1,0,QtCore.QModelIndex())
            self.remove_op(idx)
        for uri, op_spec in opdict.items():
            opname = op_spec['type']
            op = opman.get_op_byname(opname)
            if not issubclass(op,Operation):
                self.write_log('Did not find Operation {} - skipping.'.format(opname))
            else:
                op = op()
                ilspec = op_spec[optools.inputs_tag]
                for name, srctypeval in ilspec.items():
                    src = srctypeval['src']
                    tp = srctypeval['type']
                    val = srctypeval['val'] 
                    il = optools.InputLocator(src,tp,val)
                    op.input_locator[name] = il
                self.add_op(uri,op)
        # Not sure that this is necessary...
        #self.update_io_deps()
        
    def load_inputs(self,op):
        """
        Loads data for an Operation from that Operation's input_locators.
        It is expected that op.input_locator[name] will refer to an InputLocator.
        """
        for name,il in op.input_locator.items():
            if isinstance(il,optools.InputLocator):
                src = il.src
                if not src == optools.batch_input:
                    il.data = self.locate_input(il,op)
                    op.inputs[name] = il.data
                else:
                    # Batch executor should have already set the batch inputs.
                    il.data = op.inputs[name]
            else:
                msg = '[{}] Found broken Operation.input_locator for {}: {}'.format(
                __name__, name, il)
                raise ValueError(msg)

    def locate_input(self,il,op):
        """
        Return the data pointed to by a given InputLocator object.
        Takes the Operation that owns this inplocator as a second arg,
        so that if it is a Batch its input routes can be handled properly.
        """
        src = il.src
        tp = il.tp
        val = il.val
        if src == optools.no_input:
            return None
        elif src == optools.user_input: 
            return optools.cast_type_val(tp,val)
        elif src == optools.wf_input:
            return optools.parse_wf_input(self,il,op)
        elif src == optools.plugin_input:
            return optools.parse_plugin_input(self.plugman,il,op)
        elif src == optools.fs_input:
            # Trust that Operations using fs input 
            # are taking care of parsing the file names in whatever form
            return val 
        elif src == optools.batch_input:
            return val 
        else: 
            msg = 'found input source {}, should be one of {}'.format(
            src, optools.valid_sources)
            raise ValueError(msg)

    def add_op(self,uri,new_op):
        """Add an Operation to the tree as a new top-level TreeItem."""
        # Count top-level rows by passing parent=QModelIndex()
        ins_row = self.rowCount(QtCore.QModelIndex())
        itm = TreeItem(ins_row,0,QtCore.QModelIndex())
        itm.set_tag( uri )
        self.beginInsertRows(QtCore.QModelIndex(),ins_row,ins_row)
        self.root_items.insert(ins_row,itm)
        self.endInsertRows()
        idx = self.index(ins_row,0,QtCore.QModelIndex()) 
        self.tree_update(idx,new_op)
        # Should not need to update existing io dependencies when adding an op. 
        #self.update_io_deps()

    def remove_op(self,rm_idx):
        """Remove an Operation from the workflow tree"""
        rm_row = rm_idx.row()
        self.beginRemoveRows(QtCore.QModelIndex(),rm_row,rm_row)
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        # Inform views 
        self.tree_dataChanged(rm_idx)
        # Update any Operations that depended on the removed one
        self.update_io_deps()

    def update_op(self,uri,new_op):
        """
        Update Operation in treeitem indicated by uri.
        It is expected that new_op is a reference to the Operation stored at uri. 
        """
        itm, idx = self.get_from_uri(uri)
        self.tree_update(idx,new_op)
        self.update_io_deps()

    def build_dict(self,x):
        """Overloaded build_dict to handle Operations"""
        if isinstance(x,Operation):
            d = {} 
            d[optools.inputs_tag] = x.input_locator 
            d[optools.outputs_tag] = x.outputs
        else:
            d = super(WfManager,self).build_dict(x)
        return d

    # TODO: Add checking of plugins (il.src == optools.plugin_input)
    def update_io_deps(self):
        """
        Remove any broken dependencies in the workflow.
        Only effective after most recent data have been stored in the tree. 
        """
        for r,itm in zip(range(len(self.root_items)),self.root_items):
            op = itm.data
            op_idx = self.index(r,0,QtCore.QModelIndex())
            for name,il in op.input_locator.items():
                if il:
                    if il.src == optools.wf_input:
                        vals = optools.val_list(il)
                        for v in vals:
                            if not self.is_good_uri(v):
                                self.write_log('--- clearing InputLocator for {}.{}.{} ---'.format(
                                itm.tag(),optools.inputs_tag,name))
                                op.input_locator[name] = optools.InputLocator()
                                self.tree_dataChanged(op_idx)

    # TODO: the following
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

    def find_rt_item(self):
        rt_items = [] 
        for item in self.root_items:
            if isinstance(item.data,Realtime):
               rt_items.append(item)
        if len(rt_items) > 1:
            msg = 'Found {} Realtimes in workflow. Only one Realtime Operation is currently supported.'.format(len(rt_items))
            raise ValueError(msg)
        elif rt_items:
            return rt_items[0] 
        else:
            return []

    def is_running(self):
        return self._running

    def stop_wf(self):
        self._running = False

    def get_valid_wf_inputs(self,itm):
        """
        Return all of the TreeModel uris of itm and its children
        which can be used as downstream inputs in the workflow.
        """
        # valid_wf_inputs gains the operation, its input and output dicts, and their respective entries
        valid_wf_inputs = [itm.tag(),itm.tag()+'.'+optools.inputs_tag,itm.tag()+'.'+optools.outputs_tag]
        valid_wf_inputs += [itm.tag()+'.'+optools.outputs_tag+'.'+k for k in itm.data.outputs.keys()]
        valid_wf_inputs += [itm.tag()+'.'+optools.inputs_tag+'.'+k for k in itm.data.inputs.keys()]
        return valid_wf_inputs

    def batch_op_stack(self,itm_lst,b_itm,valid_wf_inputs):
        """
        Starting with batch item b_itm, take as many operations as possible from itm_lst
        and put them into an execution stack with coherent dependencies.
        """
        ds_lst = []
        rdy = False
        for uri in b_itm.data.input_routes():
            op_uri = uri.split('.')[0]
            tag_lst = [itm.tag() for itm in itm_lst]
            op_idx = tag_lst.index(op_uri)
            ds_lst.append(itm_lst[op_idx])
            #for itm in itm_lst:
            #    if itm.tag() == op_uri:
            #        ds_lst.append(itm) 
        stk = []
        while any(ds_lst):
            stk.append(ds_lst)
            #next_inputs = []
            #for itm in ds_lst:
            #    next_inputs += self.get_valid_wf_inputs(itm)
            valid_wf_inputs += self.get_valid_wf_inputs(itm)
            ds_lst = []
            for test_itm in itm_lst:
                #op_is_downstream = False
                #for il in test_itm.data.input_locator.values():
                #    if il.src == optools.wf_input and any([uri in next_inputs for uri in optools.val_list(il)]):
                #        op_is_downstream = True
                #if op_is_downstream and self.is_op_ready(test_itm,valid_wf_inputs+next_inputs):
                if self.is_op_ready(test_itm,valid_wf_inputs):
                    ds_lst.append(test_itm)
        rdy = len(itm_lst) == sum([len(lst) for lst in stk]) 
        return stk,rdy 

    def execution_stack(self):
        """
        Build a stack (list) of lists of TreeItems,
        such that each TreeItem list contains a set of Operations
        whose dependencies are satisfied by the operations above them.
        """
        stk = []
        valid_wf_inputs = []
        #batch_routes = []
        continue_flag = True
        while not sum([len(lst) for lst in stk]) == len(self.root_items) and continue_flag:
            items_rdy = []
            for itm in self.root_items:
                if not any([itm in lst for lst in stk]):
                    if self.is_op_ready(itm,valid_wf_inputs):
                        items_rdy.append(itm)
            if any(items_rdy):
                # Which of these are not Batch/Realtime ops?
                non_batch_rdy = [itm for itm in items_rdy if not isinstance(itm.data,Batch) and not isinstance(itm.data,Realtime)]
                if any(non_batch_rdy):
                    items_rdy = non_batch_rdy
                    stk.append(items_rdy)
                    for itm in items_rdy:
                        valid_wf_inputs += self.get_valid_wf_inputs(itm)
                else:
                    # When only Batch/Realtime ops are ready,
                    # take only one Batch/Realtime into the stack at a time,
                    # and follow it with its downstream operations
                    b_itm = items_rdy[0]
                    items_rdy = [b_itm]
                    #ds_stk,b_rdy = self.downstream_from_batch(b_itm,valid_wf_inputs) 
                    #ds_lst = b_itm.data.downstream_ops()
                    ds_itms = [self.get_from_uri(uri)[0] for uri in itm.data.downstream_ops()]
                    b_stk,b_rdy = self.batch_op_stack(ds_itms,b_itm,valid_wf_inputs)
                    stk.append([b_itm])
                    stk += b_stk
                    for b_lst in b_stk:
                        items_rdy += b_lst
                    valid_wf_inputs += self.get_valid_wf_inputs(b_itm)
            else:
                continue_flag = False
        return stk

    def is_op_ready(self,itm,valid_wf_inputs):
        if isinstance(itm.data,Batch) or isinstance(itm.data,Realtime):
            ds_itms = [self.get_from_uri(uri)[0] for uri in itm.data.downstream_ops()]
            b_stk,op_rdy = self.batch_op_stack(ds_itms,itm,valid_wf_inputs)
        else:
            op = itm.data
            inputs_rdy = []
            for j,name,il in zip(range(len(op.inputs)),op.input_locator.keys(),op.input_locator.values()):
                if il.src == optools.wf_input and not all([uri in valid_wf_inputs for uri in optools.val_list(il)]):
                    inp_rdy = False
                else:
                    inp_rdy = True
                inputs_rdy.append(inp_rdy)
            if all(inputs_rdy):
                op_rdy = True
            else:
                op_rdy = False
        return op_rdy 

        #if op_rdy and (isinstance(op,Realtime) or isinstance(op,Batch)):
        #    print '--- batch op {} may be ready...'.format(itm.tag())
        #    # but wait, Realtime/Batch ops are not ready unless their downstream operations WOULD BE provided for
        #    #print '{} is a batch - checking downstream....'.format(itm.tag())
        #    #import pdb; pdb.set_trace()
        #    ds_stk,batch_rdy = self.downstream_from_batch(itm,copy.copy(valid_wf_inputs))
        #    if not batch_rdy:
        #        print '--- Nope, it is not ready!'.format(itm.tag())
        #        op_rdy = False
        #if op_rdy:
        #    print 'OP {} IS READY!'.format(itm.tag())

    #def downstream_from_batch(self,b_itm,valid_wf_inputs):
    #    ds_lst = []
    #    batch_rdy = True
    #    for uri in b_itm.data.input_routes():
    #        op_uri = uri.split('.')[0]
    #        itm,idx = self.get_from_uri(op_uri)
    #        ds_lst.append(itm)
    #    stk = []
    #    while any(ds_lst):
    #        for itm in ds_lst:
    #            next_inputs = self.get_valid_wf_inputs(itm)
    #            valid_wf_inputs += next_inputs
    #        stk.append(ds_lst)
    #        ds_lst = []
    #        for test_itm in self.root_items:
    #            op_is_downstream = False
    #            if (not isinstance(test_itm.data,Batch) and not isinstance(test_itm.data,Realtime)
    #            and not any([test_itm in lst for lst in stk])):
    #                # check if itm has a wf_input referring to one of the next_inputs
    #                for il in test_itm.data.input_locator.values():
    #                    if il.src == optools.wf_input and any([uri in next_inputs for uri in optools.val_list(il)]):
    #                        # NOTE: this causes problems if a wf_input is given to post-process a batch output.
    #                        # Currently the solution is to enter manually the uri of the desired batch output.
    #                        op_is_downstream = True
    #                # now check if itm is ready given the hypothetical valid_wf_inputs
    #                if op_is_downstream:
    #                    if self.is_op_ready(test_itm,valid_wf_inputs,b_itm.data.input_routes()):
    #                        print 'downstream op {} is ready'.format(test_itm.tag())
    #                        ds_lst.append(test_itm)
    #                    # if any downstream_items are not ready, the batch is not ready
    #                    # i.e. if something in the batch uses an input that is upstream of the batch
    #                    else:
    #                        print 'downstream op {} is NOT ready'.format(test_itm.tag())
    #                        batch_rdy = False
    #    print 'found downstream of {}: {}'.format(b_itm.tag(),[[itm.tag() for itm in lst] for lst in stk])
    #    return stk,batch_rdy
#
#    def downstream_from_batch(self,b_itm,stk_done):
#        stk = []
#        # The top layer will be strictly the batch input routes
#        lst = []
#        for uri in b_itm.data.input_routes():
#            op_uri = uri.split('.')[0]
#            itm,idx = self.get_from_uri(op_uri)
#            lst.append(itm)
#        while any(lst):
#            stk.append(lst)
#            lst = []
#            for itm in self.root_items:                
#                op = itm.data
#                if ( not isinstance(op,Batch) 
#                and not isinstance(op,Realtime)
#                and not any([itm in l for l in stk_done+stk])
#                and self.batch_op_ready(op,stk_done+stk) ):
#                    lst.append(itm)
#        return stk
#                
#
                #if isinstance(op,Batch) or isinstance(op,Realtime):
                #    # Batch/Realtime ops may have wf_inputs for saved_items() or input_routes()
                #    if not all([(uri in op.saved_items() or uri in op.input_routes()) for uri in inp_uris]):
                #        inputs_rdy[j] = False
#
#
#
#
#        lst = []            # list of operations in order they are found to be ready
#        stk = []            # stack, list of lists, of operations for flattening execution order
#        b_rts = []          # list of uris of batch input_routes for batch items in stk
#        valid_inputs = []   # list of uris of things available as inputs from stk
#            ops_rdy = []
#            for i,itm in zip(range(len(self.root_items)),self.root_items):
#                op = itm.data
#                op_is_ready = False
#                inputs_ready = np.zeros(len(op.inputs))
#                for il in op.input_locator:
#                if isinstance(op,Batch) or isinstance(op,Realtime):
#
#                    # check if all inputs are in valid_inputs
#                    # OR are in batch.input_routes() or batch.saved_items()
#
#                    b_rts = b_rts + op.input_routes()
#                else:
#
#                    # check if all inputs are in valid_inputs
#
#                if all(inputs_ready):
#                    op_is_ready = True
#                if op_is_ready:
#                    ops_rdy.append(op)
#                    
#                    # update valid_inputs: the operation, its input and output dicts, and their respective entries
#                    valid_inputs += [nxt_itm.tag(),nxt_itm.tag()+'.'+optools.inputs_tag,nxt_itm.tag()+'.'+optools.outputs_tag]
#                    valid_inputs += [nxt_itm.tag()+'.'+optools.outputs_tag+'.'+k for k in nxt_itm.data.outputs.keys()]
#                    valid_inputs += [nxt_itm.tag()+'.'+optools.inputs_tag+'.'+k for k in nxt_itm.data.inputs.keys()]
#
#            stk.append(ops_rdy)
#            lst = lst + ops_rdy
#
#    def execution_stack(self):
#        lst = []            # list of operations in order they are found to be ready
#        stk = []            # stack, list of lists, of operations for flattening execution order
#        b_rts = []          # list of uris of batch input_routes for batch items in stk
#        valid_inputs = []   # list of uris of things available as inputs from stk
#        nxt = True
#        while nxt:
#            nxt_itms = []
#            for itm in self.root_items:
#                op = itm.data
#                op_rdy = True
#                for name,il in op.input_locator.items(): 
#                    inp_uri = itm.tag()+'.'+optools.inputs_tag+'.'+name
#                    if il.src == optools.batch_input:
#                        # check if the uri of this input is provided by any input_routes
#                        if not inp_uri in b_rts:
#                            op_rdy = False
#                    elif il.src == optools.wf_input:
#                        #uri = il.val
#                        for uri in optools.val_list(il):
#                            f = uri.split('.')
#                            # check if the uri of this input is one of the fields of a finished op
#                            if not uri in valid_inputs and len(f) < 3:
#                                op_rdy = False
#                            elif len(f) >= 3:
#                                # check if this is pointing to a meta-output.
#                                # if so assume it will be generated during execution.
#                                if not f[0]+'.'+f[1]+'.'+f[2] in valid_inputs:
#                                    op_rdy = False
#                            # but wait, also check if this op is a Batch or Realtime 
#                            # that uses this uri in an input_route() or one of saved_items()
#                            # in either case, it's ok to have this uri pointing down or upstream 
#                            if isinstance(op,Realtime) or isinstance(op,Batch):
#                                if uri in op.input_routes() or uri in op.saved_items():
#                                    op_rdy = True
#                if op_rdy:
#                    if not itm in lst:
#                        nxt_itms.append(itm)
#            if not nxt_itms:
#                nxt = False
#            else:
#                # make sure Batch or Realtime ops get special treatment in the stack
#                b_rt_itms = [x for x in nxt_itms if isinstance(x.data,Realtime) or isinstance(x.data,Batch)]
#                if any(b_rt_itms):
#                    # add only one Batch or Realtime at its own level
#                    # but make sure it is as low as possible in the stack
#                    if len(b_rt_itms) == len(nxt_itms):
#                        b_rts += b_rt_itms[0].data.input_routes()
#                        nxt_itms = [b_rt_itms[0]]
#                    else:
#                        nxt_itms = [x for x in nxt_itms if not isinstance(x.data,Realtime) and not isinstance(x.data,Batch)]
#                for nxt_itm in nxt_itms:
#                    lst.append(nxt_itm)
#                    # valid inputs: the operation, its input and output dicts, and their respective entries
#                    valid_inputs += [nxt_itm.tag(),nxt_itm.tag()+'.'+optools.inputs_tag,nxt_itm.tag()+'.'+optools.outputs_tag]
#                    valid_inputs += [nxt_itm.tag()+'.'+optools.outputs_tag+'.'+k for k in nxt_itm.data.outputs.keys()]
#                    valid_inputs += [nxt_itm.tag()+'.'+optools.inputs_tag+'.'+k for k in nxt_itm.data.inputs.keys()]
#                stk.append(nxt_itms)
#        return stk


    def run_wf(self):
        self._running = True
        stk = self.execution_stack()
        msg = 'STARTING EXECUTION\n----\nexecution stack: '
        for to_run in stk:
            msg = msg + '\n{}'.format( [itm.tag() for itm in to_run] ) 
        msg += '\n----'
        self.write_log(msg)
        substk = []
        batch_flags = []
        batch_idx = []
        rt_flags = []
        rt_idx = []
        for i in range(len(stk)):
            lst = stk[i]
            if isinstance(lst[0].data,Batch):
                batch_flags.append(True)
                batch_idx.append(i)
                rt_flags.append(False)
            elif isinstance(lst[0].data,Realtime):
                batch_flags.append(False)
                rt_flags.append(True)
                rt_idx.append(i)
            else:   
                batch_flags.append(False)
                rt_flags.append(False)
        if sum(rt_flags) == 1 and not any(batch_flags):
            # Expect only one rt controller at a time.
            rt_itm = stk[rt_idx[0]][0]
            prestk = stk[:rt_idx[0]]
            itms_run = []
            if any(prestk):
                msg = '\n----\n pre-realtime execution stack: '
                for lst in prestk:
                    msg = msg + '\n{}'.format( [itm.tag() for itm in lst] ) 
                    itms_run = itms_run + lst 
                msg += '\n----'
                self.write_log(msg)
                self.run_wf_serial(prestk)
                rtstk = self.downstream_from_batch_item(rt_itm,prestk)
                if any(rtstk):
                    msg = '\n----\n realtime execution stack: '
                    for lst in rtstk:
                        msg = msg + '\n{}'.format( [itm.tag() for itm in lst] ) 
                        itms_run = itms_run + lst 
                    msg += '\n----'
                    self.write_log(msg)
                    self.run_wf_realtime(rt_itm,rtstk)
            poststk = []
            for lst in stk:
                postlst = [itm for itm in lst if not itm in itms_run and not isinstance(itm.data,Realtime)] 
                if any(postlst):
                    poststk.append(postlst)
            if any(poststk):
                msg = '\n----\n post-realtime execution stack: '
                for to_run in poststk:
                    msg = msg + '\n{}'.format( [itm.tag() for itm in to_run] ) 
                msg += '\n----'
                self.write_log(msg)
                self.run_wf_serial(poststk)
        elif any(rt_flags):
            raise ValueError('[{}] only one Realtime op at a time is supported, found {}'.format(
            __name__,sum(rt_flags)+sum(batch_flags)))
        elif any(batch_flags):
            n_batch = sum(batch_flags)
            b_itms = [stk[i][0] for i in batch_idx]
            itms_run = []
            for i in range(n_batch):
                prestk = [] 
                for lst in stk[:batch_idx[i]]:
                    prelst = [itm for itm in lst if not itm in itms_run and not isinstance(itm.data,Batch)]
                    if any(prelst):
                        prestk.append(prelst)
                if any(prestk):
                    msg = '\n----\n pre-batch execution stack: '
                    for lst in prestk:
                        msg = msg + '\n{}'.format( [itm.tag() for itm in lst] ) 
                        itms_run = itms_run + lst 
                    msg += '\n----'
                    self.write_log(msg)
                    self.run_wf_serial(prestk)
                bstk = self.downstream_from_batch_item(b_itms[i],stk[:batch_idx[i]])
                if any(bstk):
                    msg = '\n----\n batch execution stack: '
                    for lst in bstk:
                        msg = msg + '\n{}'.format( [itm.tag() for itm in lst] ) 
                        itms_run = itms_run + lst 
                    msg += '\n----'
                    self.write_log(msg)
                    self.run_wf_batch(b_itms[i],bstk)
            # any more serial ops?
            poststk = []
            for lst in stk:
                postlst = [itm for itm in lst if not itm in itms_run and not isinstance(itm.data,Batch)] 
                if any(postlst):
                    poststk.append(postlst)
            if any(poststk) and self.is_running():
                msg = '\n----\n post-batch execution stack: '
                for to_run in poststk:
                    msg = msg + '\n{}'.format( [itm.tag() for itm in to_run] ) 
                msg += '\n----'
                self.write_log(msg)
                self.run_wf_serial(poststk)
        else:
            self.run_wf_serial(stk)
        # if not interrupted, signal done
        if self.is_running():
            self.wfdone.emit()

#    def batch_op_ready(self,op,stk_done):
#        op_rdy = True
#        for name,il in op.input_locator.items():
#            if il.src == optools.wf_input: 
#                op_uri = il.val.split('.')[0]
#                itm,idx = self.get_from_uri(op_uri)
#                if not any([itm in lst for lst in stk_done]):
#                    op_rdy = False
#            if il.src == optools.batch_input:
#                # assume all ops taking batch input
#                # were processed in the top layer of the stack
#                op_rdy = False
#        return op_rdy

    def next_available_thread(self):
        for idx,th in self._wf_threads.items():
            if not th:
                return idx
        # if none found, wait for thread 0
        # TODO: something better
        self.wait_for_thread(0)
        return 0 

    def wait_for_thread(self,th_idx):
        """Wait for the thread at th_idx to be finished"""
        done = False
        interval = 1
        wait_iter = 0
        total_wait = 0
        while not done:
            done = True
            if self._wf_threads[th_idx]:
                if not self._wf_threads[th_idx].isFinished():
                    done = False
                if not done:
                    self.loopwait(interval)
                    self.appref.processEvents()
                    wait_iter += 1
                    total_wait += interval
                    if interval > float(total_wait)*0.1 and interval < 100:
                        interval = interval * 10
        if wait_iter > 0:
            self.write_log('... waited {} seconds for thread {}'.format(total_wait*0.001,th_idx))

    def wait_for_threads(self):
        """Wait for all workflow execution threads to finish"""
        done = False
        interval = 10
        wait_iter = 0
        while not done:
            done = True
            for idx,th in self._wf_threads.items():
                if not th.isFinished():
                    done = False
            if not done:
                self.loopwait(interval)
                self.appref.processEvents()
                wait_iter += 1
        if wait_iter > 0:
            self.write_log('... waited {}ms for threads to finish'.format(wait_iter*interval))

    def loopwait(self,interval):
        l = QtCore.QEventLoop()
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.timeout.connect(l.quit)
        t.start(interval)
        l.exec_()
        # This processEvents() is meant to process any Signals that were emitted during waiting.
        self.appref.processEvents()

    def run_wf_serial(self,stk=None,thd=0):
        """
        Run the workflow by building a dependency stack 
        and running the operations in order.
        The dependency stack is a list of lists, 
        where each list contains the items that are ready to be executed,
        assuming the items in the lists above it have been executed already.
        """
        self.write_log('SERIAL EXECUTION STARTING in thread {}'.format(thd))
        if not stk:
            stk = self.execution_stack()
        for lst in stk:
            self.wait_for_thread(thd)
            for itm in lst: 
                op = itm.data
                self.load_inputs(op)
            # Make a new Worker, give None parent so that it can be thread-mobile
            wf_wkr = WfWorker(lst,None)
            wf_wkr.opDone.connect(self.updateOperation)
            wf_thread = QtCore.QThread(self)
            wf_wkr.moveToThread(wf_thread)
            wf_thread.started.connect(wf_wkr.work)
            wf_thread.finished.connect( partial(self.finish_thread,thd) )
            msg = 'running {} in thread {}'.format([itm.tag() for itm in lst],thd)
            self.write_log(msg)
            self._wf_threads[thd] = wf_thread
            wf_thread.start()
        self.wait_for_thread(thd)
        self.write_log('SERIAL EXECUTION FINISHED in thread {}'.format(thd))

    def finish_thread(self,th_idx):
        self.write_log('finished execution in thread {}'.format(th_idx))
        self._wf_threads[th_idx] = None

    def run_wf_realtime(self,rt_itm,stk):
        """
        Executes the workflow under the control of one Realtime(Operation) 
        """
        self.write_log( 'Preparing Realtime controller... ' )
        rt = rt_itm.data
        self.load_inputs(rt)
        rt.run()
        self.update_op(rt_itm.tag(),rt)
        self.appref.processEvents()
        stk = self.downstream_from_batch_item(rt_itm)
        nx = 0
        while self._running:
            # After rt.run(), it is expected that rt.input_iter()
            # will generate lists of input values whose respective routes are rt.input_routes().
            # unless there are no new inputs to run, in which case it will iterate None. 
            vals = rt.input_iter().next()
            inp_dict = dict( zip(rt.input_routes(), vals) )
            if inp_dict and not None in vals:
                waiting_flag = False
                nx += 1
                for uri,val in inp_dict.items():
                    self.set_op_input_at_uri(uri,val)
                thd = self.next_available_thread()
                self.write_log( 'REALTIME EXECUTION {} in thread {}'.format(nx,thd))
                self.run_wf_serial(stk,thd)
                opdict = {}
                for lst in stk:
                    for itm in lst:
                        opdict.update(self.wf_item_to_dict(itm.tag(),itm))
                rt.output_list().append(opdict)
                self.update_op(rt_itm.tag(),rt)
            else:
                self.write_log( 'Waiting for new inputs...' )
                waiting_flag = True
                self.loopwait(rt.delay())
        self.write_log( 'REALTIME EXECUTION TERMINATED' )
        return

    def run_wf_batch(self,b_itm,stk):
        """
        Executes the items in the stack stk under the control of one Batch(Operation).
        """
        self.write_log( 'Preparing Batch controller... ' )
        b = b_itm.data
        self.load_inputs(b)
        b.run()
        self.update_op(b_itm.tag(),b)
        self.appref.processEvents()
        # After b.run(), it is expected that b.input_list() will refer to a list of dicts,
        # where each dict has the form [workflow tree uri:input value]. 
        for i in range(len(b.input_list())):
            if self._running:
                input_dict = b.input_list()[i]
                for uri,val in input_dict.items():
                    self.set_op_input_at_uri(uri,val)
                # inputs are set, run in serial 
                thd = self.next_available_thread()
                self.write_log( 'BATCH EXECUTION {} / {} in thread {}'.format(i+1,len(b.input_list()),thd) )
                self.run_wf_serial(stk,thd)
                if any(b.saved_items()):
                    for uri in b.saved_items():
                        itm,idx = self.get_from_uri(uri)
                        b.output_list()[i].update(self.wf_item_to_dict(uri,itm))
                else:
                    for lst in stk:
                        for itm in lst:
                            b.output_list()[i].update(self.wf_item_to_dict(itm.tag(),itm))
                self.update_op(b_itm.tag(),b)
            else:
                self.write_log( 'BATCH EXECUTION TERMINATED' )
                return
        self.write_log( 'BATCH EXECUTION FINISHED' )

    def wf_item_to_dict(self,uri,itm):
        od = OrderedDict()
        od[uri] = copy.deepcopy(itm.data)
        if isinstance(itm.data,Operation):
            inp_uri = uri+'.'+optools.inputs_tag  
            inp_itm,idx = self.get_from_uri(inp_uri)
            od.update(self.wf_item_to_dict(inp_uri,inp_itm))
            out_uri = uri+'.'+optools.outputs_tag  
            out_itm,idx = self.get_from_uri(out_uri)
            od.update(self.wf_item_to_dict(out_uri,out_itm))
        elif isinstance(itm.data,dict):
            for k,v in itm.data.items():
                itm_uri = uri+'.'+str(k)
                itm,idx = self.get_from_uri(itm_uri)
                od.update(self.wf_item_to_dict(itm_uri,itm))
        elif isinstance(itm.data,list):
            for i,itm in zip(range(len(itm.data)),itm.data):
                itm_uri = uri+'.'+str(i)
                itm,idx = self.get_from_uri(itm_uri)
                od.update(self.wf_item_to_dict(itm_uri,itm))
        return od

    def set_op_input_at_uri(self,uri,val):
        """Set an op input, indicated by uri, to provided value."""
        p = uri.split('.')
        # Allow some structure here: expect no meta-inputs. 
        op_itm, idx = self.get_from_uri(p[0])
        op = op_itm.data
        op.inputs[p[2]] = val

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
            return "Workflow: {} operation(s)".format(self.rowCount(QtCore.QModelIndex()))
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return "type"
        else:
            return None

    # Overload columnCount()
    def columnCount(self,parent):
        """Let WfManager have two columns, one for item tag, one for item type"""
        return 2


