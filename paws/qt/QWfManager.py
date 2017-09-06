from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy
import time

from PySide import QtCore

from .QWfWorker import QWfWorker
from .QWorkflow import QWorkflow
from ..core import pawstools
from ..core.operations import Operation as opmod
from ..core.operations import optools
from ..core.workflow.Workflow import Workflow
from ..core.workflow.WfManager import WfManager
from ..core.operations.Operation import Operation


class QWfManager(WfManager,QtCore.QObject):
    """
    A Qt Signal-slot manager for paws Workflows.
    """

    def __init__(self,qapp,qpluginmanager):
        # NOTE: what happens when qpluginmanager gets passed to QObject.__init__?
        super(QWfManager,self).__init__(qpluginmanager)
        self.app = qapp 
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        self.wf_running = OrderedDict()

    def add_wf(self,wfname):
        """
        Add a QWorkflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = QWorkflow(self)
        if not wf.is_tag_valid(wfname): 
            raise pawstools.WfNameError(wf.tag_error_message(wfname))
        self.workflows[wfname] = wf
        self.wf_running[wfname] = False

    # this signal should emit the name
    # of the workflow that has been updated 
    wf_updated = QtCore.Signal(str)

    # this signal should emit the name
    # of the workflow that finished.
    wfdone = QtCore.Signal(str)

    @QtCore.Slot(str)
    def runWorkflow(self,wfname):
        self.run_wf(wfname)

    @QtCore.Slot(str)
    def stopWorkflow(self,wfname):
        self.stop_wf(wfname)

    def stop_wf(self,wfname):
        self.wf_running[wfname] = False
        self.wfdone.emit(wfname)


