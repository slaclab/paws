from functools import partial

from PySide import QtCore

from .wf_plugin import WorkflowPlugin
from .workflow import Workflow

class WfManager(QtCore.QObject):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, performs operations on them.
    """

    # this signal should emit the name of the workflow that finished.
    wfdone = QtCore.Signal(str)

    @QtCore.Slot(str)
    def finish_wf(self,wfname):
        self.wfdone.emit(wfname)

    def __init__(self,plugin_manager,qapp_reference):
        self.workflows = {} 
        self.appref = qapp_reference 
        self.plugman = plugin_manager
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        #self._wf_threads = dict.fromkeys(range(self._n_threads)) 
        self.logmethod = None
        super(WfManager,self).__init__()

    def n_wf(self):
        return len(self.workflows)

    def write_log(self,msg):
        if self.logmethod:
            self.logmethod(msg)
        else:
            print(msg)

    def wf_threads(self):
        return self._wf_threads

    def add_wf(self,wfname):
        wf = Workflow(self)
        wf.exec_finished.connect( partial(self.finish_wf,wfname) )
        wf.logmethod = self.logmethod
        self.workflows[wfname] = wf
        # for every new workflow, add a plugin 
        self.plugman.add_plugin(wfname,WorkflowPlugin(wf))

    def run_wf(self,wfname):
        self.workflows[wfname].run_wf()

    def stop_wf(self,wfname):
        self.workflows[wfname].stop_wf()


