from collections import OrderedDict

from PySide import QtCore

from .QTreeSelectionModel import QTreeSelectionModel
from ..core.plugins.PawsPlugin import PawsPlugin
from ..core.operations import Operation as opmod
from ..core.plugins.PluginManager import PluginManager

class QPluginManager(PluginManager,QTreeSelectionModel):
    """
    A Qt Signal-slot manager for a TreeModel PluginManager.
    Takes a reference to a PluginManager in the constructor.
    The QPluginManager works mostly by
    calling on the methods of the PluginManager.
    """

    def __init__(self):
        super(QPluginManager,self).__init__()

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} plugin(s) loaded".format(self.n_plugins())
        else:
            return super(QPluginManager,self).headerData(section,orientation,data_role)    

    @QtCore.Slot(str)
    def update_plugin(self,pgin_name):
        self.set_item(pgin_name,self._tree.get_data_from_uri(pgin_name))


