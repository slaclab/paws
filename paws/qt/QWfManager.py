from collections import OrderedDict
from functools import partial
import copy

from PySide import QtCore

from .QWfWorker import QWfWorker
from .QWorkflow import QWorkflow
from ..core.operations import optools
from ..core.workflow.Workflow import Workflow
from ..core.plugins.WorkflowPlugin import WorkflowPlugin
from ..core.operations.Operation import Operation, Batch, Realtime

class QWfManager(QtCore.QObject):
    """
    A Qt Signal-slot manager for paws Workflows.
    Takes a reference to a WfManager in the constructor.
    The QWfManager works mostly by
    calling on the methods of the WfManager.
    """

    def __init__(self,wfman,qplugman,app):
        super(QWfManager,self).__init__()
        self.wfman = wfman
        self.qplugman = qplugman
        self.app = app 
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        self.qworkflows = OrderedDict() 
        self.wf_running = OrderedDict()
        self.wf_updated.connect( self.qplugman.update_plugin )

    def add_wf(self,wfname):
        """
        Add a QWorkflow to self.qworkflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow(self.wfman)
        self.wfman.workflows[wfname] = wf
        self.qworkflows[wfname] = QWorkflow(wf)
        self.wf_running[wfname] = False
        #wf.exec_finished.connect( partial(self.finish_wf,wfname) )
        #wf.setParent(self)
        #self.workflows[wfname] = wf
        # for every new workflow, add a plugin 
        #self.workflows[wfname] 
        wf_pgin = WorkflowPlugin()
        wf_pgin.inputs['workflow'] = wf
        wf_pgin.start()
        self.qplugman.add_plugin(wfname,wf_pgin)

    def load_from_dict(self,wfname,opman,opdict):
        """
        Create a workflow with name wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input opdict specifies operation setup,
        where each item in opdict provides enough information
        to get an Operation from OpManager opman
        and set up its Operation.input_locators.
        """
        self.add_wf(wfname)
        for opname, op_setup in opdict.items():
            op = self.wfman.build_op_from_dict(op_setup,opman)
            if isinstance(op,Operation):
                self.qworkflows[wfname].set_item(opname,op)
            else:
                self.wfman.write_log('Failed to load {} for workflow {}.'.format(opname,wfname))
        self.wf_updated.emit(wfname)

    def n_wf(self):
        return len(self.qworkflows)

    # this signal should emit the name
    # of the workflow that has been updated 
    wf_updated = QtCore.Signal(str)

    # this signal should emit the name
    # of the workflow that finished.
    wfdone = QtCore.Signal(str)

    #@QtCore.Slot(str)
    #def runWorkflow(self,wfname):
    #    self.run_wf(wfname)

    #@QtCore.Slot(str)
    #def stopWorkflow(self,wfname):
    #    self.stop_wf(wfname)

    def stop_wf(self,wfname):
        self.wf_running[wfname] = False
        self.wfdone.emit(wfname)

    def get_op(self,wfname,opname):
        return self.qworkflows[wfname].wf.get_data_from_uri(opname)

    def run_wf(self,wfname):
        """
        Serially execute the operations of QWfManager.qworkflows[wfname].
        Uses Workflow.execution_stack() to determine execution order,
        and executes operations away from the main gui thread. 
        """
        self.wf_running[wfname] = True
        stk,diag = self.qworkflows[wfname].wf.execution_stack()
        for lst in stk:
            first_op = self.get_op(wfname,lst[0])
            batch_flag = isinstance(first_op,Batch)
            rt_flag = isinstance(first_op,Realtime)
            if not any([batch_flag,rt_flag]):
                self.execute_serial(wfname,lst)
            elif batch_flag:
                self.execute_batch(wfname,lst[0],lst[1])
            elif rt_flag:
                self.execute_realtime(wfname,lst[0],lst[1])
        self.wait_for_threads()
        # TODO: wait only for the threads working on wfname
        self.stop_wf(wfname)

    def execute_serial(self,wfname,op_list):
        thd_idx = self.next_available_thread()
        self.wfman.write_log('[{}] workflow {} running {}'
        .format(thd_idx,wfname,op_list))
        ops = [self.get_op(wfname,opname) for opname in op_list]
        for op in ops:
            optools.load_inputs(op,self.qworkflows[wfname].wf)
        op_dict = OrderedDict(zip(op_list,ops))
        # Copy op_dict so that it can be thread-mobile
        op_dict = copy.deepcopy(op_dict)
        # Make a new Worker, give None parent so that it can be thread-mobile
        wf_wkr = QWfWorker(op_dict,None)
        wf_wkr.opDone.connect(partial(self.updateOperation,wfname))
        #wf_wkr.work()
        #wf_wkr.deleteLater()
        wf_thread = QtCore.QThread(self)
        wf_wkr.wfDone.connect(wf_thread.quit)
        wf_wkr.moveToThread(wf_thread)
        self.register_thread(thd_idx,wf_thread)
        wf_thread.started.connect(wf_wkr.work)
        wf_thread.finished.connect( partial(self.finish_thread,thd_idx,wfname) )
        wf_thread.finished.connect(wf_thread.deleteLater)
        wf_thread.finished.connect(wf_wkr.deleteLater)
        wf_thread.start()
        self.wait_for_thread(thd_idx)
        self.wf_updated.emit(wfname)

    def execute_batch(self,wfname,batch_op_tag,batch_stk):
        batch_op = self.qworkflows[wfname].wf.get_data_from_uri(batch_op_tag) 
        optools.load_inputs(batch_op,self.qworkflows[wfname].wf)
        batch_op.run()
        self.qworkflows[wfname].set_item(batch_op_tag,batch_op)
        n_batch = len(batch_op.input_list())
        for i in range(n_batch):
            input_dict = batch_op.input_list()[i]
            for uri,val in input_dict.items():
                self.qworkflows[wfname].set_op_input_at_uri(uri,val)
            self.wfman.write_log( 'BATCH EXECUTION {} / {}'.format(i+1,n_batch) )
            for batch_lst in batch_stk:
                self.execute_serial(wfname,batch_lst)
            saved_items_dict = OrderedDict()
            for uri in batch_op.saved_items():
                save_data = self.qworkflows[wfname].wf.get_data_from_uri(uri)
                save_dict = self.wfman.uri_to_embedded_dict(uri,save_data) 
                saved_items_dict = self.wfman.update_embedded_dict(saved_items_dict,save_dict)
            batch_op.output_list()[i] = saved_items_dict
            self.qworkflows[wfname].set_item(batch_op_tag,batch_op)

    def execute_realtime(self,wfname,rt_op_tag,rt_stk):
        pass

    @QtCore.Slot(str,str,Operation)
    def updateOperation(self,wfname,tag,op):
        self.qworkflows[wfname].set_item(tag,op)
        # processEvents() after updating an operation
        # so that the application can execute anything 
        # that was queued in the main event loop during the update,
        # such as updating views in the GUI.
        self.app.processEvents()

    def finish_thread(self,th_idx,wfname):
        #print 'finishing thread {}'.format(th_idx)
        self.app.processEvents()
        self._wf_threads[th_idx] = None
        self.wf_updated.emit(wfname)

    def register_thread(self,thread_idx,thread):
        self._wf_threads[thread_idx] = thread

    def wf_threads(self):
        return self._wf_threads

    def wait_for_thread(self,th_idx):
        """Wait for the thread at self._wf_threads[th_idx] to be finished"""
        #print 'waiting for thread {}'.format(th_idx)
        # when waiting for a thread to execute something,
        # best processEvents() to ensure that the application has a chance
        # to prepare the thing that will be executed
        self.app.processEvents()
        done = False
        interval = 1
        wait_iter = 0
        total_wait = 0
        while not done:
            #if wait_iter > 0:
            #    print '{}... still waiting for thread {} for {}ms'.format(wait_iter,th_idx,total_wait)
            done = True
            if self._wf_threads[th_idx] is not None:
                if not self._wf_threads[th_idx].isFinished():
                    done = False
                if not done:
                    if interval <= float(total_wait)*0.01 and interval <= 100:
                        interval = interval * 10
                    self.loopwait(interval)
                    wait_iter += 1
                    total_wait += interval

    def next_available_thread(self):
        for idx,th in self._wf_threads.items():
            if not th:
                #print '[{}] found available thread {}'.format(__name__,idx)
                return idx
        # if none found, wait for first thread in self.wfman.wf_threads 
        self.wait_for_thread(0)
        #print '[{}] falling back on thread 0'.format(__name__)
        return 0

    def wait_for_threads(self):
        """Wait for all workflow execution threads to finish"""
        for idx,th in self._wf_threads.items():
            self.wait_for_thread(idx)

    def loopwait(self,interval):
        """
        Create an event loop to delay some time without busywaiting.
        Time interval is specified in milliseconds.
        """
        l = QtCore.QEventLoop()
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.timeout.connect(l.quit)
        t.start(interval)
        l.exec_()
        # processEvents() to continue the main event loop while waiting.
        self.app.processEvents()

        # the wf_updated signal for this workflow is expected 
        # to be connected to the plugin manager at this point.
        # See WfManager.add_wf(). 
        #self.workflows[wfname].wf_updated.emit()



    # signal to emit when this workflow finishes execution.
    # connects to workflow manager's finish_wf slot.
    # which in turn emits workflow manager's wfdone signal. 
    #exec_finished = QtCore.Signal()

    # Signal to emit when the state of this Workflow changes.
    # WfManager connects this to PluginManager
    # so that PluginManager can update the associated WorkflowPlugin
    # whenever this Workflow is updated.
    #wf_updated = QtCore.Signal()


    #@QtCore.Slot(str)
    #def run_wf(self,wfname):
    #    self.workflows[wfname].run_wf()

    #@QtCore.Slot(str)
    #def finish_wf(self,wfname):
    #    self.wfdone.emit(wfname)

#    def run_wf(self):
#        self._running = True
#        stk = self.execution_stack()
#        msg = 'STARTING EXECUTION\n----\nexecution stack: \n'
#        msg += self.print_stack(stk)
#        msg += '\n----'
#        self.wfman.write_log(msg)
#        batch_flags = [isinstance(self.get_data_from_uri(lst[0]),Batch) for lst in stk]
#        rt_flags = [isinstance(self.get_data_from_uri(lst[0]),Realtime) for lst in stk]
#        layers_done = 0
#        while not layers_done == len(stk): 
#            # check if we are at a batch or rt op
#            if batch_flags[layers_done]:
#                self.run_wf_batch(stk[layers_done][0],stk[layers_done][1])
#                layers_done += 1
#            elif rt_flags[layers_done]:
#                self.run_wf_realtime(stk[layers_done][0],stk[layers_done][1])
#                layers_done += 1
#            else:
#                # get the portion of the stack from here to the next batch or rt op
#                if (True in batch_flags[layers_done:]):
#                    substk = stk[layers_done:layers_done+batch_flags[layers_done:].index(True)]
#                elif (True in rt_flags[layers_done:]):
#                    substk = stk[layers_done:layers_done+rt_flags[layers_done:].index(True)]
#                else:
#                    substk = stk[layers_done:]
#                self.run_wf_serial(substk)
#                layers_done += len(substk)
#        # if not yet interrupted, wait for all threads to finish, then signal done
#        if self.is_running():
#            self.wfman.wait_for_threads()
#            self.wfman.write_log('EXECUTION FINISHED')
#            self.exec_finished.emit()
#
#    def run_wf_serial(self,stk,thd_idx=None):
#        """
#        Serially execute the operations indicated by input stack stk.
#        """
#        if thd_idx is None:
#            thd_idx = self.wfman.next_available_thread()
#        for lst in stk:
#            self.wfman.wait_for_thread(thd_idx)
#            op_dict = OrderedDict() 
#            for op_tag in lst: 
#                op = self.get_data_from_uri(op_tag) 
#                optools.load_inputs(op,self)
#                op_dict[op_tag] = op
#            # Copy op_dict so that it can be thread-mobile
#            op_dict = copy.deepcopy(op_dict)
#            # Make a new Worker, give None parent so that it can be thread-mobile
#            wf_wkr = WfWorker(op_dict,None)
#            wf_wkr.opDone.connect(self.updateOperation)
#            wf_thread = QtCore.QThread(self)
#            wf_wkr.moveToThread(wf_thread)
#            self.wfman.register_thread(thd_idx,wf_thread)
#            wf_thread.started.connect(wf_wkr.work)
#            wf_thread.finished.connect( partial(self.wfman.finish_thread,thd_idx) )
#            wf_thread.finished.connect(wf_thread.deleteLater)
#            wf_thread.finished.connect(wf_wkr.deleteLater)
#            wf_thread.start()
#            msg = 'running {} in thread {}'.format(lst,thd_idx)
#            self.wfman.write_log(msg)
#            # TODO: Figure out how to remove this wait_for_thread(). 
#            # It should be handled in Workflow.run_wf() 
#            self.wfman.wait_for_thread(thd_idx)
#
#    def run_wf_realtime(self,rt_op_tag,rt_stk):
#        """
#        Execute the operations indicated by stack rt_stk in real time
#        under the control of the Realtime Operation indicated by rt_op_tag.
#        """
#        # TODO: Ensure rt execution runs smoothly on an initially empty input_iter().
#        # TODO: Add a way to stop a realtime execution without stopping the whole workflow.
#        # TODO: when calling update_op(rt_op), update only the new/changed children of the rt op
#        rt_op = self.get_data_from_uri(rt_op_tag) 
#        optools.load_inputs(rt_op,self)
#        rt_op.run()
#        self.update_op(rt_op_tag,rt_op)
#        nx = 0
#        wait_flag = False
#        while self._running:
#            # After rt_op.run(), it is expected that rt_op.input_iter()
#            # will generate lists of input values that should be routed to rt_op.input_routes(),
#            # unless there are no new inputs to run, in which case it will iterate None. 
#            vals = rt_op.input_iter().next()
#            if not None in vals:
#                wait_flag = False
#                inp_dict = OrderedDict( zip(rt_op.input_routes(), vals) )
#                nx += 1
#                for uri,val in inp_dict.items():
#                    self.set_op_input_at_uri(uri,val)
#                thd_idx = self.wfman.next_available_thread()
#                #thd_idx = 0
#                self.wfman.write_log( 'REALTIME EXECUTION {} in thread {}'.format(nx,thd))
#                self.run_wf_serial(rt_stk,thd_idx)
#                # wait for thread to finish before saving results
#                self.wfman.wait_for_thread(thd_idx)
#                saved_items_dict = OrderedDict()
#                for uri in rt_op.saved_items():
#                    save_data = self.get_data_from_uri(uri)
#                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
#                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
#                rt_op.output_list().append(saved_items_dict)
#                self.update_op(rt_op_tag,rt_op)
#            else:
#                if not wait_flag:
#                    self.wfman.write_log( 'Waiting for new inputs...' )
#                    wait_flag = True
#                self.wfman.loopwait(rt_op.delay())
#        self.wfman.write_log( 'REALTIME EXECUTION TERMINATED' )
#        return
#
#    def run_wf_batch(self,batch_op_tag,batch_stk):
#        """
#        Batch-execute the items indicated by stack batch_stk 
#        under the control of the Batch Operation indicated by batch_op_tag.
#        """
#        # TODO: when calling update_op(batch_op), update only the new/changed children of the batch op
#        batch_op = self.get_data_from_uri(batch_op_tag) 
#        optools.load_inputs(batch_op,self)
#        batch_op.run()
#        self.update_op(batch_op_tag,batch_op)
#        # After batch_op.run(), it is expected that batch_op.input_list() will refer to a list of dicts,
#        # where each dict has the form [workflow tree uri:input value]. 
#        for i in range(len(batch_op.input_list())):
#            if self._running:
#                input_dict = batch_op.input_list()[i]
#                for uri,val in input_dict.items():
#                    self.set_op_input_at_uri(uri,val)
#                thd_idx = self.wfman.next_available_thread()
#                #thd_idx = 0
#                self.wfman.write_log( 'BATCH EXECUTION {} / {} in thread {}'.format(i+1,len(batch_op.input_list()),thd_idx) )
#                self.run_wf_serial(batch_stk,thd_idx)
#                # wait for thread to finish before saving results
#                self.wfman.wait_for_thread(thd_idx)
#                saved_items_dict = OrderedDict()
#                for uri in batch_op.saved_items():
#                    save_data = self.get_data_from_uri(uri)
#                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
#                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
#                batch_op.output_list()[i] = saved_items_dict
#                self.update_op(batch_op_tag,batch_op)
#            else:
#                self.wfman.write_log( 'BATCH EXECUTION TERMINATED' )
#                return
#        self.wfman.write_log( 'BATCH EXECUTION FINISHED' )
#
#
