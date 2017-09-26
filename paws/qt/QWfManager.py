from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy

from PySide import QtCore

from .QWfWorker import QWfWorker
from .QWorkflow import QWorkflow
from ..core import pawstools
from ..core.workflow.WfManager import WfManager
from . import qttools

class QWfManager(WfManager,QtCore.QObject):
    """
    A Qt Signal-slot manager for paws Workflows.
    """
    # this signal should emit the name
    # of the new workflow 
    wfAdded = QtCore.Signal(str)

    # this signal should emit the name
    # of the workflow that has been updated 
    wfUpdated = QtCore.Signal(str)

    # this signal should emit the name
    # of the workflow that finished.
    wfFinished = QtCore.Signal(str)

    @QtCore.Slot(str)
    def launchWorkflow(self,wfname):
        self.run_wf(wfname)

    @QtCore.Slot(str)
    def stopWorkflow(self,wfname):
        self.stop_wf(wfname)

    def __init__(self,qapp):
        super(QWfManager,self).__init__()
        self.app = qapp 
        self.wf_running = OrderedDict()

    def add_wf(self,wfname):
        """
        Add a QWorkflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = QWorkflow()
        if not wf.is_tag_valid(wfname): 
            raise pawstools.WfNameError(wf.tag_error_message(wfname))
        self.workflows[wfname] = wf
        self.wf_running[wfname] = False
        self.wfAdded.emit(wfname)

    def stop_wf(self,wfname):
        self.wf_running[wfname] = False
        self.wfFinished.emit(wfname)

    def run_wf(self,wfname,pool=None):
        print('calling run_wf({})'.format(wfname))
        wf = self.workflows[wfname]
        if pool is None:
            self.write_log('preparing workflow {} for execution'.format(wfname))
            stk,diag = wf.execution_stack()
            self.prepare_wf(wf,stk)
            wf.wfFinished.connect( partial(self.stop_wf,wfname) )
            self.wf_running[wfname] = True
            wf.execute(self.write_log)
            self.write_log('execution finished')
        else:
            wf = self.workflows[wfname]
            self.write_log('preparing workflow {} for execution'.format(wfname))
            stk,diag = wf.execution_stack()
            self.prepare_wf(wf,stk)
            # Copy the workflow so it can be moved off the main thread.
            # Connect some signals so that the local copy gets updated
            # as the remote copy gets executed. 
            wf_clone = wf.clone_wf()
            wf_clone.opChanged.connect(wf.update_op)
            # NOTE: do the connections get copied under copy()?
            # If not, need to re-set this one:
            #wf_copy.WfFinished.connect(self.stop_wf)
            # construct a QRunnable around a copy of the Workflow 
            qr = qttools.RunnableExecutor( wf_clone,self.write_log ) 
            #qr.runStarted.connect(self.app.processEvents)
            # Call QThreadPool.start(QRunnable) - executes runnable.run()
            self.wf_running[wfname] = True
            pool.start(qr)
            #wf.execute(self.write_log)
            self.write_log('execution finished')

    #    stk,diag = self.execution_stack(wf)
    #    for lst in stk:
    #        self.write_log('running: {}'.format(lst))
    #        for op_tag in lst: 
    #            op = self.get_data_from_uri(op_tag) 
    #            self.load_inputs(op,wf)
    #            self.opChanged.emit(op_tag,wfname)
    #            # construct a QRunnable around a copy of the Operation
    #            qr = qttools.RunnableExecutor( op.copy() ) 
    #            qr.runStarted.connect(self.wf_manager.app.processEvents)
    #            qr.opFinished.connect( partial(self.finish_op,op_tag,wfname) )
    #            # Call QThreadPool.start(QRunnable) - executes runnable.run()
    #            pool.start(qr)

    #def finish_op(self,op_tag,wfname,op):
    #    wf = self.workflows[wfname]
    #    wf.set_item(op_tag,op)
    #    self.opChanged.emit(op_tag,wfname)
    #    self.opFinished.emit(op_tag,wfname)
          
    #def execute_from_layer(self,stk,layer_index):
    #    print 'run layer {}'.format(layer_index)
    #    self.write_log('running: {}'.format(stk[layer_index]))
    #    lst = stk[layer_index] 
    #    # load the inputs
    #    for op_tag in lst:
    #        op = self.get_data_from_uri(op_tag) 
    #        self.load_inputs(op,self.wf_manager,self.wf_manager.plugin_manager)
    #        self.opChanged.emit(op_tag)
    #    op_dict = dict.fromkeys(lst)
    #    for op_tag in lst:
    #        # give ops to WfWorker as deep copies?
    #        #op_dict[op_tag] = copy.deepcopy(self.get_data_from_uri(op_tag))
    #        op_copy = copy.copy(self.get_data_from_uri(op_tag))
    #        op_dict[op_tag] = op_copy 
    #    # start a WfWorker
    #    wkr = QWfWorker(op_dict)
    #    # create a QThread
    #    thd = QtCore.QThread()
    #    # move the WfWorker to the QThread
    #    wkr.moveToThread(thd)
    #    # connect proper signals
    #    thd.started.connect(wkr.work)
    #    wkr.opDone.connect(self.finish_op)
    #    #wkr.allDone.connect(thd.quit)
    #    if not layer_index == len(stk):
    #        thd.finished.connect( partial(self.execute_from_layer,stk,layer_index+1) )
    #    # start the thread
    #    #thd.exec_()
    #    thd.start()
    #    self.wf_manager.app.processEvents()

    #def finish_op(self,op_tag,op):
    #    self.set_item(op_tag,op)
    #    self.opChanged.emit(op_tag)
    #    self.opFinished.emit(op_tag)






