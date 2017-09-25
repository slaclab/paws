from collections import OrderedDict
from functools import partial
import copy

from PySide import QtCore

from .QWfWorker import QWfWorker
from ..core.workflow.Workflow import Workflow
from ..core.operations import Operation as opmod
from .QTreeSelectionModel import QTreeSelectionModel
from ..core.operations import optools
from . import qttools

class QWorkflow(Workflow,QTreeSelectionModel):
    """
    A QTreeSelectionModel representing a Workflow
    """
    opChanged = QtCore.Signal(str)
    opFinished = QtCore.Signal(str)

    def __init__(self,wfman):
        super(QWorkflow,self).__init__(wfman)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    def execute_op(self,op_tag,pool=None):
        if pool is None:
            super(QWorkflow,self).execute_op(op_tag)
            self.opChanged.emit(op_tag)
            self.opFinished.emit(op_tag)
        else:
            op = self.get_data_from_uri(op_tag) 
            self.load_inputs(op,self.wf_manager,self.wf_manager.plugin_manager)
            self.opChanged.emit(op_tag)
            # construct a QRunnable around a copy of the Operation
            qr = qttools.RunnableExecutor( op.copy() ) 
            # Call QThreadPool.start(QRunnable) - executes runnable.run()
            pool.start(qr)
            # TODO: connect the qrunnable started signal to ProcessEvents()
            self.wf_manager.app.processEvents()
            self.set_item(op_tag,op)
            self.opChanged.emit(op_tag)
            self.opFinished.emit(op_tag)
        self.wf_manager.app.processEvents()

    #def execute(self):
    #    stk,diag = self.execution_stack()
    #    self.execute_from_layer(stk,0)
    #    self.write_log('execution finished')
          
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

