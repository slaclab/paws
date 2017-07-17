from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy
import time

from PySide import QtCore

from .QWfWorker import QWfWorker
from .QWorkflow import QWorkflow
from ..core import pawstools
from ..core.operations import Operation as op
from ..core.operations import optools
from ..core.workflow.Workflow import Workflow
from ..core.operations.Operation import Operation, Batch, Realtime


class QWfManager(QtCore.QObject):
    """
    A Qt Signal-slot manager for paws Workflows.
    Takes a reference to a WfManager in the constructor.
    The QWfManager works mostly by
    calling on the methods of the WfManager.
    """

    def __init__(self,wfman,app):
        super(QWfManager,self).__init__()
        self.wfman = wfman
        self.app = app 
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        self.qworkflows = OrderedDict() 
        self.wf_running = OrderedDict()

    def add_wf(self,wfname):
        """
        Add a QWorkflow to self.qworkflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow()
        self.wfman.workflows[wfname] = wf
        self.qworkflows[wfname] = QWorkflow(wf)
        self.wf_running[wfname] = False
        self.wf_updated.emit(wfname)
        #wf.exec_finished.connect( partial(self.finish_wf,wfname) )
        #wf.setParent(self)
        #self.workflows[wfname] = wf
        # for every new workflow, add a plugin 
        #self.workflows[wfname] 
        #wf_pgin = WorkflowPlugin()
        #wf_pgin.inputs['workflow'] = wf
        #wf_pgin.start()
        #self.qplugman.add_plugin(wfname,wf_pgin)

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
        return self.wfman.workflows[wfname].get_data_from_uri(opname)

    def run_wf(self,wfname):
        """
        Serially execute the operations of QWfManager.qworkflows[wfname].
        Uses optools.execution_stack() to determine execution order,
        and executes operations away from the main gui thread. 
        """
        self.wf_running[wfname] = True
        stk,diag = optools.execution_stack(self.wfman.workflows[wfname])
        self.wfman.write_log('STARTING {} \nEXECUTION STACK: \n'
        .format(wfname)+optools.print_stack(stk))
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
        self.app.processEvents()
        #for op_tag in op_list: 
        ops = [self.get_op(wfname,opname) for opname in op_list]
        for op in ops:
            optools.load_inputs(op,self.wfman.workflows[wfname],self.wfman.plugman)
        self.app.processEvents()
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
        try:
            wf_thread.start()
        except Exception as ex:
            wf_wkr.deleteLater()
            wf_thread.quit()
            wf_thread.deleteLater()
            raise ex
        self.app.processEvents()
        self.wait_for_thread(thd_idx)
        self.wf_updated.emit(wfname)
        # and another one here.
        self.app.processEvents()

    def execute_batch(self,wfname,batch_op_tag,batch_stk):
        # TODO: run this under a timer, take measures to speed it up
        batch_op = self.wfman.workflows[wfname].get_data_from_uri(batch_op_tag) 
        optools.load_inputs(batch_op,self.wfman.workflows[wfname],self.wfman.plugman)
        batch_op.run()
        self.qworkflows[wfname].set_op(batch_op_tag,batch_op)
        self.app.processEvents()
        n_batch = len(batch_op.input_list())
        for i in range(n_batch):
            if self.wf_running[wfname]:
                input_dict = batch_op.input_list()[i]
                for uri,val in input_dict.items():
                    self.qworkflows[wfname].set_op_input_at_uri(uri,val)
                self.wfman.write_log( 'BATCH EXECUTION {} / {}'.format(i+1,n_batch) )
                self.app.processEvents()
                for batch_lst in batch_stk:
                    self.execute_serial(wfname,batch_lst)
                saved_items_dict = OrderedDict()
                for uri in batch_op.saved_items():
                    # TODO # BUG: there is the chance for infinite recursion here
                    # if the batch is asked to save an upstream item?
                    save_data = copy.deepcopy(self.wfman.workflows[wfname].get_data_from_uri(uri))
                    save_dict = self.wfman.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.wfman.update_embedded_dict(saved_items_dict,save_dict)
                batch_op.output_list()[i] = saved_items_dict
                #self.qworkflows[wfname].set_item(batch_op_tag,batch_op)
                # Rather than re-setting the entire batch_op,
                # try just updating the outputs subtree for this iteration.
                batch_output_uri = batch_op_tag+'.'+op.outputs_tag+'.'+batch_op.batch_outputs_tag()+'.'+str(i)
                self.qworkflows[wfname].tree_update_at_uri(batch_output_uri,saved_items_dict)
                self.app.processEvents()
            else:
                raise pawstools.WorkflowAborted('[{}] {} was signaled to stop.'
                .format(__name__,wfname)) 

    def execute_realtime(self,wfname,rt_op_tag,rt_stk):
        #import pdb; pdb.set_trace()
        rt_op = self.wfman.workflows[wfname].get_data_from_uri(rt_op_tag) 
        optools.load_inputs(rt_op,self.wfman.workflows[wfname],self.wfman.plugman)
        rt_op.run()
        self.qworkflows[wfname].set_op(rt_op_tag,rt_op)
        self.app.processEvents()
        #keep_running = True
        n_exec = 0
        wait_iter = 0
        while self.wf_running[wfname]:
        #while keep_running:
            vals = rt_op.input_iter().next()
            if not None in vals:
                n_exec += 1
                wait_iter = 0
                inp_dict = OrderedDict( zip(rt_op.input_routes(), vals) )
                for uri,val in inp_dict.items():
                    self.qworkflows[wfname].set_op_input_at_uri(uri,val) 
                self.wfman.write_log( 'REALTIME EXECUTION {}'.format(n_exec))
                self.app.processEvents()
                for rt_lst in rt_stk:
                    self.execute_serial(wfname,rt_lst)
                saved_items_dict = OrderedDict()
                for uri in rt_op.saved_items():
                    save_data = copy.deepcopy(self.wfman.workflows[wfname].get_data_from_uri(uri))
                    save_dict = self.wfman.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.wfman.update_embedded_dict(saved_items_dict,save_dict)
                rt_op.output_list().append(saved_items_dict)
                output_uri = rt_op_tag+'.'+op.outputs_tag+'.'+rt_op.batch_outputs_tag()+'.'+str(n_exec)
                self.qworkflows[wfname].tree_update_at_uri(output_uri,saved_items_dict)
                self.app.processEvents()
            else:
                #if wait_iter == 0:
                self.wfman.write_log( 'Waiting for new inputs...' )
                self.app.processEvents()
                wait_iter += 1 
                self.loopwait(rt_op.delay())
                #time.sleep(float(rt_op.delay())/1000.0)
            if wait_iter > 1000:
                self.wfman.write_log('Waited too long. Exiting...')
                self.app.processEvents()
                #keep_running = False
                self.wf_running[wfname] = False

    @QtCore.Slot(str,str,Operation)
    def updateOperation(self,wfname,tag,op):
        self.qworkflows[wfname].set_item(tag,op)
        # processEvents() to kickstart the main event loop 
        # after finishing the update.
        # Application may freeze under some conditions
        # if this processEvents() is left out.
        self.app.processEvents()

    def finish_thread(self,th_idx,wfname):
        #print 'finishing thread {}'.format(th_idx)
        self._wf_threads[th_idx] = None
        self.wf_updated.emit(wfname)
        # processEvents() to kickstart the main event loop 
        # after finishing the update.
        # Application may freeze under some conditions
        # if this processEvents() is left out.
        self.app.processEvents()

    def register_thread(self,thread_idx,thread):
        self._wf_threads[thread_idx] = thread

    def wf_threads(self):
        return self._wf_threads

    def wait_for_thread(self,th_idx):
        """Wait for the thread at self._wf_threads[th_idx] to be finished"""
        #print 'waiting for thread {}'.format(th_idx)
        # when waiting for a thread to execute something,
        # processEvents() to ensure main event loop is current.
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


