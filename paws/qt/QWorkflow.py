from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy
import os

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
    opInputChanged = QtCore.Signal(str,str,object)
    opOutputChanged = QtCore.Signal(str,str,object)
    wfFinished = QtCore.Signal()
    emitMessage = QtCore.Signal(str)

    @QtCore.Slot(str)
    def relayMessage(self,msg):
        self.emitMessage.emit(msg)

    @QtCore.Slot(str,str,object)
    def updateOpInput(self,opnm,inpnm,inpdata):
        self.set_op_item(opnm,opmod.inputs_tag+'.'+inpnm,inpdata)

    @QtCore.Slot(str,str,object)
    def updateOpOutput(self,opnm,outnm,outdata):
        self.set_op_item(opnm,opmod.outputs_tag+'.'+outnm,outdata)

    @QtCore.Slot(str,str,object)
    def updateOpItem(self,opnm,item_uri,item_data):
        self.set_op_item(opnm,item_uri,item_data)

    def add_op(self,op_tag,op):
        op.message_callback = self.relayMessage
        op.data_callback = partial( self.updateOpItem,op_tag )
        self.set_item(op_tag,op)

    def __init__(self):
        super(QWorkflow,self).__init__()

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    def execute(self):
        stk,diag = self.execution_stack()
        self.logmethod(os.linesep+'running workflow:'+os.linesep+self.print_stack(stk))
        for lst in stk:
            self.logmethod('running: {}'.format(lst))
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                for inpname,il in op.input_locator.items():
                    if il.tp == opmod.workflow_item:
                        #il.data = self.locate_input(il)
                        #op.inputs[name] = il.data
                        op.inputs[inpname] = self.locate_input(il)
                        self.opInputChanged.emit(op_tag,inpname,op.inputs[inpname])
                        #self.record_op_input(op_tag,inpname,op.inputs[inpname])
                #self.opChanged.emit(op_tag,op)
                op.run()
                for outnm,outdata in op.outputs.items():
                    self.opOutputChanged.emit(op_tag,outnm,outdata)
                    #self.record_op_output(op_tag,outnm,outdata)
                #self.set_item(op_tag,op)
                #self.opChanged.emit(op_tag,op)
        self.wfFinished.emit()

