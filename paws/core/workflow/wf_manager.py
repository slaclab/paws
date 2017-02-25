from PySide import QtCore

from ..plugins.WorkflowPlugin import WorkflowPlugin

class WfManager(object):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, performs operations on them.
    """

    def __init__(self,plugin_manager,qapp_reference):
        self.wf_list = []
        self.appref = qapp_reference 
        self.plugman = plugin_manager
        self._n_threads = QtCore.QThread.idealThreadCount()
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        #self._wf_threads = dict.fromkeys(range(self._n_threads)) 
        super(WfManager,self).__init__()

    def add_wf(self,wf):
        self.wf_list.append(wf)
        # deliver a workflow plugin to plugin manager
        self.plugman.add_plugin(self.plugman.auto_tag('workflow'),WorkflowPlugin(wf))


