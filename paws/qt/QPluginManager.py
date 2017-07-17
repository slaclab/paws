from collections import OrderedDict

from PySide import QtCore

from .QTreeSelectionModel import QTreeSelectionModel
from ..core.plugins.PawsPlugin import PawsPlugin
from ..core.operations import Operation as op

class QPluginManager(QTreeSelectionModel):
    """
    A Qt Signal-slot manager for a TreeModel PluginManager.
    Takes a reference to a PluginManager in the constructor.
    The QPluginManager works mostly by
    calling on the methods of the PluginManager.
    """
    # TODO: Clean up headerData

    def __init__(self,plugman):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        super(QPluginManager,self).__init__(flag_dict,plugman)
        self.plugman = plugman

    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "{} plugin(s) loaded".format(self._tree._root_item.n_children())
        else:
            return super(QPluginManager,self).headerData(section,orientation,data_role)    

    def add_plugin(self,pgin_tag,pgin):
        """Add a Plugin to the tree at the top level."""
        self.set_item(pgin_tag,pgin,self.root_index())

    def remove_plugin(self,pgin_tag):
        self.remove_item(pgin_tag)

    @QtCore.Slot(str)
    def update_plugin(self,pgin_name):
        #import pdb; pdb.set_trace()
        self.set_item(pgin_name,self._tree.get_data_from_uri(pgin_name))

    def load_from_dict(self,plugin_dict):
        """
        Load plugins from a dict that specifies their setup parameters.
        """
        for tag, pgin_spec in plugin_dict.items():
            pgin_uri = pgin_spec['plugin_module']
            pgin = self._tree.get_plugin(pgin_uri)
            if pgin is not None:
                if not issubclass(pgin,PawsPlugin):
                    self._tree.write_log('Did not find Plugin {} - skipping.'.format(pgin_uri))
                    return 
            pgin = pgin()
            for name in pgin.inputs.keys():
                if name in pgin_spec[op.inputs_tag]:
                    pgin.inputs[name] = pgin_spec[op.inputs_tag][name]
            pgin.start()
            self.add_plugin(tag,pgin)

    #        self.plugman.contains_uri(pgin_name):
    #        #pgin = self.get_data_from_uri(pgin_name)
    #        #self.tree_update(self.root_index(),pgin_name,self.build_tree(pgin))

    #def remove_plugin(self,rm_idx):
    #    """Remove a Plugin from the tree"""
    #    p_idx = self.parent(rm_idx)
    #    if not p_idx == self.root_index():
    #        msg = '[{}] Called remove_plugin on non-Plugin at QModelIndex {}. \n'.format(__name__,rm_idx)
    #        raise ValueError(msg)
    #    self.remove_item(rm_itm.tag,p_idx)

    # Overloaded headerData() for PluginManager 
    #def headerData(self,section,orientation,data_role):
    #    if (data_role == QtCore.Qt.DisplayRole and section == 0):
    #        return "Plugins: {} active".format(self.item_count())
    #    elif (data_role == QtCore.Qt.DisplayRole and section == 1):
    #        return super(PluginManager,self).headerData(section,orientation,data_role)    
    #    else:
    #        return None



