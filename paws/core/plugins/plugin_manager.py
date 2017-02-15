import importlib

from PySide import QtCore

from ..operations import optools
from ..treemodel import TreeModel,TreeSelectionModel
from ..treeitem import TreeItem
from .. import plugins as pgns
from ..plugins.plugin import PawsPlugin

class PluginManager(TreeSelectionModel):
    """
    Tree structure for managing paws plugins.
    """

    def __init__(self,**kwargs):
        super(PluginManager,self).__init__()
        self.logmethod = None

    def load_from_dict(self,pgin_dict):
        """
        Load plugins from a dict that specifies their setup parameters.
        """
        while self.root_items:
            idx = self.index(self.rowCount(QtCore.QModelIndex())-1,0,QtCore.QModelIndex())
            self.remove_plugin(idx)
        for uri, pgin_spec in pgin_dict.items():
            pgin_name = pgin_spec['type']
            pgin = self.get_plugin_byname(pgin_name)
            if pgin is not None:
                if not issubclass(pgin,PawsPlugin):
                    self.write_log('Did not find Plugin {} - skipping.'.format(pgin_name))
                else:
                    pgin = pgin()
                    pgin.inputs = pgin_spec[optools.inputs_tag]
                    pgin.start()
                    self.add_plugin(uri,pgin)
            else:
                self.write_log('Did not find Plugin {} - skipping.'.format(pgin_name))
                

    def get_plugin_byname(self,pgin_name):    
        try:
            mod = importlib.import_module('.'+pgin_name,pgns.__name__)
            if pgin_name in mod.__dict__.keys():
                return mod.__dict__[pgin_name]
            else:
                self.write_log('Did not find plugin {} in module {}'.format(pgin_name,mod.__name__) + ex.message)
                return None 
        except Exception as ex:
            self.write_log('Trouble loading module for plugin {}. Error message: '.format(pgin_name) + ex.message)
            return None

    def write_log(self,msg):
        if self.logmethod:
            self.logmethod(msg)
        else:
            print(msg)

    def add_plugin(self,pgin_tag,pgin):
        """Add a Plugin to the tree as a new top-level TreeItem."""
        ins_row = self.rowCount(QtCore.QModelIndex())
        itm = TreeItem(ins_row,0,QtCore.QModelIndex())
        itm.set_tag( pgin_tag )
        self.beginInsertRows(QtCore.QModelIndex(),ins_row,ins_row)
        self.root_items.insert(ins_row,itm)
        self.endInsertRows()
        idx = self.index(ins_row,0,QtCore.QModelIndex()) 
        self.tree_update(idx,pgin)
        #self.tree_dataChanged(idx)

    def build_dict(self,x):
        """Overloaded build_dict to handle Plugins"""
        if isinstance(x,PawsPlugin):
            d = x.content() 
        else:
            d = super(PluginManager,self).build_dict(x)
        return d

    def remove_plugin(self,rm_idx):
        """Remove a Plugin from the tree"""
        rm_row = rm_idx.row()
        self.beginRemoveRows(QtCore.QModelIndex(),rm_row,rm_row)
        item_removed = self.root_items.pop(rm_row)
        self.endRemoveRows()
        self.tree_dataChanged(rm_idx)

    # Overloaded data() for PluginManager
    #def data(self,itm_idx,data_role):
    #    return super(PluginManager,self).data(itm_idx,data_role)
    #    #if (not itm_idx.isValid()):
    #    #    return None
    #    #itm = itm_idx.internalPointer()
    #    #if data_role == QtCore.Qt.DisplayRole:
    #    #    return itm.tag()
    #    #else:
    #    #    return None

    # Overloaded headerData() for PluginManager 
    def headerData(self,section,orientation,data_role):
        if (data_role == QtCore.Qt.DisplayRole and section == 0):
            return "Plugins: {} active".format(len(self.root_items))
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return super(PluginManager,self).headerData(section,orientation,data_role)    
        else:
            return None


