from __future__ import print_function
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
from ..core.operations.Operation import Operation

class QWorkflow(Workflow,QTreeSelectionModel):
    """
    A QTreeSelectionModel representing a Workflow
    """
    # this signal should emit the name
    # of the relevant operation,
    # as in opChanged(opname)
    opChanged = QtCore.Signal(str,Operation)
    wfFinished = QtCore.Signal()

    def __init__(self):
        super(QWorkflow,self).__init__()

    def update_op(self,op_tag,op):
        self.set_item(op_tag,op)
        self.opChanged.emit(op_tag,op)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    def execute(self,logmethod=print):
        stk,diag = self.execution_stack()
        for lst in stk:
            logmethod('running: {}'.format(lst))
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                for name,il in op.input_locator.items():
                    if il.tp == opmod.workflow_item:
                        il.data = self.locate_input(il)
                        op.inputs[name] = il.data
                self.opChanged.emit(op_tag,op)
                op.run()
                self.set_item(op_tag,op)
                self.opChanged.emit(op_tag,op)
        self.wfFinished.emit()

