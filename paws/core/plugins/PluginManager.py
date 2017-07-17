from __future__ import print_function
import importlib
from collections import OrderedDict

from ..operations import Operation as op
from ..operations.Operation import Operation
from ..workflow.Workflow import Workflow
from ..models.TreeModel import TreeModel
from .. import plugins as pgns
from .PawsPlugin import PawsPlugin

class PluginManager(TreeModel):
    """
    Tree structure for managing paws plugins.
    """

    def __init__(self,**kwargs):
        super(PluginManager,self).__init__()
        self.logmethod = print 

    def write_log(self,msg):
        self.logmethod(msg)
        #if self.logmethod:
        #else:
        #    print(msg)

    def plugin_setup_dict(self,pgin):
        pgin_mod = pgin.__module__[pgin.__module__.find('plugins'):]
        pgin_mod = pgin_mod[pgin_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['plugin_module'] = pgin_mod
        dct[op.inputs_tag] = pgin.inputs 
        return dct

    def load_from_dict(self,plugin_dict):
        """
        Load plugins from a dict that specifies their setup parameters.
        """
        for tag, pgin_spec in plugin_dict.items():
            pgin_uri = pgin_spec['plugin_module']
            pgin = self.get_plugin(pgin_uri)
            if pgin is not None:
                if not issubclass(pgin,PawsPlugin):
                    self.write_log('Did not find Plugin {} - skipping.'.format(pgin_uri))
                else:
                    pgin = pgin()
                    for name in pgin.inputs.keys():
                        if name in pgin_spec[op.inputs_tag]:
                            pgin.inputs[name] = pgin_spec[op.inputs_tag][name]
                    pgin.start()
                    # if already have this uri, first generate auto_tag
                    #if self.tree_contains_uri(uri):
                    #    uri = self.auto_tag(uri)
                    #self.add_plugin(uri,pgin)
                    self.set_item(tag,pgin)
            else:
                self.write_log('Did not find Plugin {} - skipping.'.format(ptype))

    #def tree_update(self,parent_idx,itm_tag,itm_data):
    #    if isinstance(itm_data,Operation) or isinstance(itm_data,PawsPlugin):
    #        super(PluginManager,self).tree_update(parent_idx,itm_tag,self.build_tree(itm_data))
    #    else:
    #        super(PluginManager,self).tree_update(parent_idx,itm_tag,itm_data)

    def build_tree(self,x):
        """
        Reimplemented TreeModel.build_tree() 
        so that TreeItems are built from PawsPlugins
        and Workflows and Operations.
        """
        if isinstance(x,PawsPlugin):
            #d = x.content()
            d = OrderedDict()
            for k,v in x.content().items():
                d[k] = self.build_tree(v)
        elif isinstance(x,Workflow):
            #d = x.op_dict()
            d = OrderedDict()
            for k,v in x.op_dict().items():
                d[k] = self.build_tree(v)
        elif isinstance(x,Operation):
            d = OrderedDict()
            d[op.inputs_tag] = self.build_tree(x.inputs)
            d[op.outputs_tag] = self.build_tree(x.outputs)
        else:
            return super(PluginManager,self).build_tree(x) 
        return d

    def get_plugin(self,pgin_type):    
        try:
            mod = importlib.import_module('.'+pgin_type,pgns.__name__)
            if pgin_type in mod.__dict__.keys():
                return mod.__dict__[pgin_type]
            else:
                msg = str('Did not find plugin {} in module {}'
                .format(pgin_type,mod.__name__))
                self.write_log(msg)
                return None 
        except Exception as ex:
            msg = str('Trouble loading module for plugin {}. '
            .format(pgin_name) + 'Error message: ' + ex.message)
            self.write_log(msg)
            return None

    def list_plugins(self):
        return self.root_tags()
        #r = self.get_from_idx(self.root_index())
        #return [itm.tag for itm in r.children]

