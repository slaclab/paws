"""This minimally enhances the paws.api module to interface with qt-based applications."""

from PySide import QtCore

from .. import api as pawsapi
from .QOpManager import QOpManager
from .QWfManager import QWfManager
from .QPluginManager import QPluginManager
from ..core import operations as ops

def start(app):
    """
    Instantiate and return a QPawsAPI object.
    Requires a valid QApplication as input. 

    paws.api.start() calls the QPawsAPI constructor.

    :returns: a QPawsAPI object
    :return type: paws.api.QPawsAPI 
    """
    return QPawsAPI(app)

class QPawsAPI(pawsapi.PawsAPI,QtCore.QObject):
    wfSelectionChanged = QtCore.Signal(str)

    def __init__(self,app):
        super(QPawsAPI,self).__init__()
        # Replace the PawsAPI TreeModels and workflow manager 
        # with the Qt-enabled variants.
        self._op_manager = QOpManager()
        self._plugin_manager = QPluginManager()
        self._wf_manager = QWfManager(app)
        self._wf_manager.plugin_manager = self._plugin_manager
        # TODO: load_cats and load_ops should happen outside the api.__init__
        # so that different api instances can have different operations loaded
        self._op_manager.load_cats(ops.cat_list) 
        self._op_manager.load_ops(ops.cat_op_list)
        self.app = app

    #def set_logmethod(self,lm):
    #    super(QPawsAPI,self).set_logmethod(lm)
    # TODO: figure out how to disconnect this signal
    # so that it is only connected to one message slot at a time
    #    self._wf_manager.emitMessage.disconnect()
    #    self._wf_manager.emitMessage.connect(lm)

    def get_op_from_index(self,idx):
        return self._op_manager.get_data_from_index(idx)

    def get_op_uri_from_index(self,idx):
        return self._op_manager.get_uri_of_index(idx)

    def get_plugin_from_index(self,idx):
        return self._plugin_manager.get_data_from_index(idx)

    def select_wf(self,wfname):
        super(QPawsAPI,self).select_wf(wfname)
        self.wfSelectionChanged.emit(wfname)
        
    def stop_wf(self,wfname):
        self._wf_manager.stop_wf(wfname)

    def run_wf(self,wfname,pool=None):
        """
        Run the workflow indicated by wfname.
        If optional threadpool is provided,
        the workflow attempts to run in that threadpool.
        """
        self._wf_manager.run_wf(wfname,pool)

    def is_wf_running(self,wfname):
        return self._wf_manager.wf_running[wfname]
