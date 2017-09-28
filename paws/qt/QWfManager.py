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
    # of the workflow that finished.
    wfFinished = QtCore.Signal(str)

    # a signal for carrying textual output
    # e.g. for message board logging
    emitMessage = QtCore.Signal(str)

    @QtCore.Slot(str)
    def relayMessage(self,msg):
        self.emitMessage.emit(msg)

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
        wf.emitMessage.connect(self.relayMessage)
        wf.message_callback = wf.emitMessage.emit
        wf.wfFinished.connect( partial(self.stop_wf,wfname) )
        self.workflows[wfname] = wf
        self.wf_running[wfname] = False
        self.wfAdded.emit(wfname)

    def stop_wf(self,wfname):
        self.write_log('stopping workflow {}'.format(wfname))
        self.wf_running[wfname] = False
        #self.wfFinished.emit(wfname)

    def run_wf(self,wfname,pool=None):
        wf = self.workflows[wfname]
        stk,diag = wf.execution_stack()
        self.write_log('preparing workflow {} for execution'.format(wfname))
        self.prepare_wf(wf,stk)
        if pool is None:
            self.wf_running[wfname] = True
            wf.execute()
            self.write_log('execution finished')
        else:
            # Copy the workflow so it can be moved off the main thread.
            # Connect some signals so that the local copy gets updated
            # as the remote copy gets executed. 
            wf_clone = wf.clone_wf()
            wf_clone.message_callback = wf_clone.emitMessage.emit
            wf_clone.emitMessage.connect(self.relayMessage)
            wf_clone.data_callback = wf_clone.emitData.emit
            wf_clone.emitData.connect(wf.updateItem)
            wf_clone.wfFinished.connect( partial(self.stop_wf,wfname) )
            # construct a QRunnable around a copy of the Workflow 
            qr = qttools.RunnableExecutor( wf_clone ) 
            # Call QThreadPool.start(QRunnable) - executes runnable.run()
            self.wf_running[wfname] = True
            pool.start(qr)



