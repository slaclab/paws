from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy
import os

from PySide import QtCore

from .QWfWorker import QWfWorker
from ..core.workflows.Workflow import Workflow
from ..core.operations import Operation as opmod
from .QTreeSelectionModel import QTreeSelectionModel
from ..core.operations import optools
from . import qttools
from ..core.operations.Operation import Operation

class QWorkflow(Workflow,QTreeSelectionModel):
    """
    A QTreeSelectionModel representing a Workflow
    """
    wfFinished = QtCore.Signal()
    emitMessage = QtCore.Signal(str)
    opFinished = QtCore.Signal(str)
    emitData = QtCore.Signal(str,object)

    def __init__(self):
        super(QWorkflow,self).__init__()

    @QtCore.Slot(str,str,object)
    def relayOpData(self,op_tag,data_uri,data):
        self.emitData.emit(op_tag+'.'+data_uri,data)

    @QtCore.Slot(str)
    def relayMessage(self,msg):
        self.emitMessage.emit(msg)

    @QtCore.Slot(str,str,object)
    def updateOpInput(self,opnm,inpnm,inpdata):
        self.set_op_item(opnm,'inputs.'+inpnm,inpdata)

    @QtCore.Slot(str,str,object)
    def updateOpOutput(self,opnm,outnm,outdata):
        self.set_op_item(opnm,'outputs.'+outnm,outdata)

    @QtCore.Slot(str,str,object)
    def updateOpItem(self,opnm,item_uri,item_data):
        self.set_op_item(opnm,item_uri,item_data)

    @QtCore.Slot(str,str,object)
    def updateItem(self,item_uri,item_data):
        self.set_item(item_uri,item_data)

    def add_op(self,op_tag,op):
        op.message_callback = self.message_callback
        op.data_callback = partial( self.relayOpData,op_tag )
        self.set_item(op_tag,op)

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} operation(s) loaded".format(self.root_item().n_children())
        else:
            return super(QWorkflow,self).headerData(section,orientation,data_role)    

    def execute(self):
        stk,diag = self.execution_stack()
        self.message_callback(os.linesep+'running workflow:'+os.linesep+self.print_stack(stk))
        for lst in stk:
            self.message_callback('running: {}'.format(lst))
            for op_tag in lst: 
                op = self.get_data_from_uri(op_tag) 
                for inpnm,il in op.input_locator.items():
                    if il.tp == opmod.workflow_item:
                        #op.inputs[inpnm] = self.locate_input(il)
                        self.set_op_item(op_tag,'inputs.'+inpnm,self.locate_input(il))
                        if self.data_callback:
                            self.data_callback(op_tag+'.inputs.'+inpnm,op.inputs[inpnm])
                op.run()
                for outnm,outdata in op.outputs.items():
                    if self.data_callback:
                        out_uri = op_tag+'.outputs.'+outnm
                        if outdata is not None:
                            self.data_callback(out_uri,outdata)
                        #print('done setting {}'.format(out_uri))
                self.opFinished.emit(op_tag)
                    #self.record_op_output(op_tag,outnm,outdata)
                #self.set_item(op_tag,op)
                #self.opChanged.emit(op_tag,op)
        self.wfFinished.emit()

