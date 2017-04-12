import importlib
from collections import OrderedDict

from PySide import QtCore

from ..operations import optools
from ..TreeSelectionModel import TreeSelectionModel
from ..TreeItem import TreeItem
from .. import plugins as pgns
from .PawsPlugin import PawsPlugin
from .WorkflowPlugin import WorkflowPlugin

class PluginManager(TreeSelectionModel):
    """
    Tree structure for managing paws plugins.
    """

    def __init__(self,**kwargs):
        super(PluginManager,self).__init__()
        self.logmethod = None

    @QtCore.Slot(str)
    def update_plugin(self,pgin_name):
        #import pdb;pdb.set_trace()
        itm, idx = self.get_from_uri(pgin_name)
        self.tree_update(idx,itm.data)

    def load_from_dict(self,pgin_dict):
        """
        Load plugins from a dict that specifies their setup parameters.
        """
        for uri, pgin_spec in pgin_dict.items():
            pgin_name = pgin_spec['type']
            pgin = self.get_plugin_byname(pgin_name)
            if pgin is not None:
                if not issubclass(pgin,PawsPlugin):
                    self.write_log('Did not find Plugin {} - skipping.'.format(pgin_name))
                else:
                    pgin = pgin()
                    for name in pgin.inputs.keys():
                        if name in pgin_spec[optools.inputs_tag]:
                            pgin.inputs[name] = pgin_spec[optools.inputs_tag][name]
                    pgin.start()
                    # if already have this uri, first generate auto_tag
                    if self.tree_contains_uri(uri):
                        uri = self.auto_tag(uri)
                    self.add_plugin(uri,pgin)
            else:
                self.write_log('Did not find Plugin {} - skipping.'.format(pgin_name))

    def list_plugins(self):
        return [itm.tag() for itm in self.root_item().children]

    @staticmethod
    def plugin_dict(pgin):
        dct = OrderedDict()
        dct['type'] = type(pgin).__name__
        dct[optools.inputs_tag] = pgin.inputs 
        return dct

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
        # TODO: Ensure plugin names are unique
        self.add_item(pgin_tag,pgin,self.root_index())
        #ins_row = self.n_items(self.root_index())
        #itm = TreeItem(ins_row,0,self.root_index())
        #itm.set_tag( pgin_tag )
        #self.beginInsertRows(self.root_index(),ins_row,ins_row)
        #self.root_item().children.insert(ins_row,itm)
        #self.endInsertRows()
        #idx = self.index(ins_row,0,self.root_index()) 
        #self.tree_update(idx,pgin)

    def build_dict(self,x):
        """Overloaded build_dict to handle Plugins"""
        if isinstance(x,PawsPlugin):
            d = x.content() 
        else:
            d = super(PluginManager,self).build_dict(x)
        return d

    def remove_plugin(self,rm_idx):
        """Remove a Plugin from the tree"""
        self.remove_item(rm_idx)
        #rm_row = rm_idx.row()
        #self.beginRemoveRows(QtCore.QModelIndex(),rm_row,rm_row)
        #item_removed = self.root_item().children.pop(rm_row)
        #self.endRemoveRows()
        #self.tree_dataChanged(rm_idx)

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
            return "Plugins: {} active".format(self.root_item().n_children())
        elif (data_role == QtCore.Qt.DisplayRole and section == 1):
            return super(PluginManager,self).headerData(section,orientation,data_role)    
        else:
            return None


