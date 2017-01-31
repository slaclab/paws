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
                    # Expect this input to have been set by self.set_op_input_at_uri().
                    # Refer that input value to il.data.
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

    def remove_op(self,rm_idx):
        """Remove an Operation from the workflow tree"""
        rm_row = rm_idx.row()
        self.beginRemoveRows(QtCore.QModelIndex(),rm_row,rm_row)
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        self.tree_dataChanged(rm_idx)
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
            d = OrderedDict() 
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
                    if il.src == optools.wf_input and il.tp == optools.auto_type and not self.is_good_uri(il.val):
                        #vals = optools.val_list(il)
                        #for v in vals:
                        #    if not self.is_good_uri(v):
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

    def batch_op_stack(self,b_itm,valid_wf_inputs):
        """
        Use b_itm.data.batch_ops() and a list of valid_wf_inputs 
        (a list of uris that are good inputs from the workflow)   
        to build a stack (list) of lists of operations 
        such that all Operations in the stack have their dependencies satisfied
        by the Operations above them.     
        """
        if isinstance(b_itm.data,Realtime):
            exec_itms = [self.get_from_uri(uri)[0] for uri in b_itm.data.realtime_ops()]
        elif isinstance(b_itm.data,Batch):
            exec_itms = [self.get_from_uri(uri)[0] for uri in b_itm.data.batch_ops()]
        else:
            exec_itms = []
        valid_batch_inputs = copy.copy(valid_wf_inputs)
        layer = []
        for test_itm in exec_itms:
            if self.is_op_ready(test_itm,valid_batch_inputs,b_itm.data.input_routes()):
                layer.append(test_itm)
        b_stk = []
        while any(layer):
            b_stk.append(layer)
            for itm in layer:
                valid_batch_inputs += self.get_valid_wf_inputs(itm)
            layer = []
            for test_itm in exec_itms:
                if self.is_op_ready(test_itm,valid_batch_inputs,b_itm.data.input_routes()) and not self.stack_contains(test_itm,b_stk):
                    layer.append(test_itm)
        b_rdy = len(exec_itms) == self.stack_size(b_stk) 
        return b_stk,b_rdy 

    def stack_size(self,stk):
        sz = 0
        for lst in stk:
            if isinstance(lst[0].data,Batch) or isinstance(lst[0].data,Realtime):
                sz += self.stack_size(lst[1])+1
            else:
                sz += len(lst)
        return sz

    def stack_contains(self,itm,stk):
        for lst in stk:
            if isinstance(lst[0].data,Batch) or isinstance(lst[0].data,Realtime):
                if itm == lst[0] or self.stack_contains(itm,lst[1]):
                    return True
            else:
                if itm in lst:
                    return True
        return False

    def print_stack(self,stk):
        stktxt = ''
        for lst in stk:
            if isinstance(lst[0].data,Batch) or isinstance(lst[0].data,Realtime):
                substk = lst[1]
                stktxt += '[{}:\n{}]\n'.format(lst[0].tag(),self.print_stack(lst[1]))
                #[[itm.tag() for itm in sublst] for sublst in substk])
            else:
                stktxt += '{}\n'.format([itm.tag() for itm in lst])
        return stktxt

    def execution_stack(self):
        """
        Build a stack (list) of lists of TreeItems,
        such that each TreeItem list contains a set of Operations
        whose dependencies are satisfied by the operations above them.
        For Batch or Realtime operations, the layer should be of the form[batch_item,batch_stack],
        where batch_item.data is the batch controller Operation,
        and batch_stack is built from self.batch_op_stack().
        """
        stk = []
        valid_wf_inputs = []
        continue_flag = True
        while not self.stack_size(stk) == len(self.root_items) and continue_flag:
            items_rdy = []
            for itm in self.root_items:
                if not self.stack_contains(itm,stk):
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
                    b_rt_itm = items_rdy[0]
                    items_rdy = [b_rt_itm]
                    b_rt_stk,b_rt_rdy = self.batch_op_stack(b_rt_itm,valid_wf_inputs)
                    stk.append([b_rt_itm,b_rt_stk])
                    valid_wf_inputs += self.get_valid_wf_inputs(b_rt_itm)
            else:
                continue_flag = False
        #print 'RESOLVED A STACK'
        #print 'STACK PRINTOUT:'
        #print self.print_stack(stk)
        return stk

    def is_op_ready(self,itm,valid_wf_inputs,batch_routes=[]):
        if isinstance(itm.data,Batch):
            b_stk,op_rdy = self.batch_op_stack(itm,valid_wf_inputs)
        elif isinstance(itm.data,Realtime):
            rt_stk,op_rdy = self.batch_op_stack(itm,valid_wf_inputs)
        else:
            op = itm.data
            inputs_rdy = []
            for name,il in op.input_locator.items():
                if il.src == optools.wf_input and il.tp == optools.auto_type and not il.val in valid_wf_inputs:
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

    def finish_thread(self,th_idx):
        self.write_log('finished execution in thread {}'.format(th_idx))
        self._wf_threads[th_idx] = None

    def loopwait(self,interval):
        l = QtCore.QEventLoop()
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.timeout.connect(l.quit)
        t.start(interval)
        l.exec_()
        # This processEvents() is meant to process any Signals that were emitted during waiting.
        self.appref.processEvents()

    def run_wf(self):
        self._running = True
        stk = self.execution_stack()
        msg = 'STARTING EXECUTION\n----\nexecution stack: \n'
        #for to_run in stk:
        #    msg = msg + '\n{}'.format( [itm.tag() for itm in to_run] ) 
        msg += self.print_stack(stk)
        msg += '\n----'
        self.write_log(msg)
        batch_flags = [isinstance(itm_lst[0].data,Batch) for itm_lst in stk]
        rt_flags = [isinstance(itm_lst[0].data,Realtime) for itm_lst in stk]
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
        # if not yet interrupted, signal done
        if self.is_running():
            self.wfdone.emit()

    def run_wf_serial(self,stk,thd=0):
        """
        Serially execute the operations contained in the stack stk.
        """
        self.write_log('SERIAL EXECUTION STARTING in thread {}'.format(thd))
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

    def run_wf_realtime(self,rt_itm,stk):
        """
        Executes the workflow under the control of one Realtime controller Operation.
        where the realtime controller Operation is found at rt_itm.data.
        """
        self.write_log( 'Preparing Realtime controller... ' )
        rt = rt_itm.data
        self.load_inputs(rt)
        rt.run()
        self.update_op(rt_itm.tag(),rt)
        self.appref.processEvents()
        nx = 0
        while self._running:
            # TODO: Add a way to stop a realtime execution without stopping the whole workflow.
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
                opdict = OrderedDict()
                for uri in rt.saved_items():
                    itm,idx = self.get_from_uri(uri)
                    opdict.update(self.wf_item_to_dict(uri,itm))
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
        Executes the items in the stack stk under the control of one Batch controller Operation
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
                opdict = OrderedDict()
                for uri in b.saved_items():
                    itm,idx = self.get_from_uri(uri)
                    opdict.update(self.wf_item_to_dict(uri,itm))
                b.output_list()[i] = opdict
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
        """
        Set an op input, indicated by uri, to provided value.
        uri must be of the form op_name.inputs.input_name.
        Currently shallower uris (e.g. op_name.inputs) 
        and deeper uris (e.g. op_name.inputs.input_dict.input_param)
        are not supported.
        """
        p = uri.split('.')
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



