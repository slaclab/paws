from __future__ import print_function
import importlib
from collections import OrderedDict

from ..operations import Operation as opmod
from ..operations.Operation import Operation
from ..workflow.Workflow import Workflow
from ..models.TreeModel import TreeModel
from .. import plugins as pgns
from .. import pawstools
from .PawsPlugin import PawsPlugin

class PluginManager(TreeModel):
    """
    Tree structure for managing paws plugins.
    """

    def __init__(self,**kwargs):
        flag_dict = OrderedDict()
        flag_dict['select'] = False
        super(PluginManager,self).__init__(flag_dict)
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
        dct[opmod.inputs_tag] = pgin.inputs 
        return dct

    def load_from_dict(self,pgin_name,pgin_spec):
        """
        Load plugins from a dict that specifies their setup parameters.
        """
        #for tag, pgin_spec in plugin_dict.items():
        pgin_module = pgin_spec['plugin_module']
        pgin = self.load_plugin(pgin_module)
        if pgin is not None:
            if not issubclass(pgin,PawsPlugin):
                self.write_log('Did not find Plugin {} - skipping.'.format(pgin_uri))
            else:
                pgin = pgin()
                for name in pgin.inputs.keys():
                    if name in pgin_spec[opmod.inputs_tag]:
                        pgin.inputs[name] = pgin_spec[opmod.inputs_tag][name]
                pgin.start()
                # if already have this uri, first generate auto_tag
                #if self.tree_contains_uri(uri):
                #    uri = self.auto_tag(uri)
                #self.add_plugin(uri,pgin)
                self.set_item(pgin_name,pgin)
        else:
            self.write_log('Did not find Plugin {} - skipping.'.format(ptype))

    #def tree_update(self,parent_idx,itm_tag,itm_data):
    #    if isinstance(itm_data,Operation) or isinstance(itm_data,PawsPlugin):
    #        super(PluginManager,self).tree_update(parent_idx,itm_tag,self.build_tree(itm_data))
    #    else:
    #        super(PluginManager,self).tree_update(parent_idx,itm_tag,itm_data)

    def add_plugin(self,pgin_name,pgin):
        """
        Add a plugin, with key specified by pgin_name.
        If pgin_name is not unique (i.e. a plugin with that name already exists),
        this method will overwrite the existing plugin with a new one.
        """
        if not self.is_tag_valid(pgin_name): 
            raise pawstools.PluginNameError(self.tag_error_message(pgin_name))
        self.set_item(pgin_name,pgin)

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
            d[opmod.inputs_tag] = self.build_tree(x.inputs)
            d[opmod.outputs_tag] = self.build_tree(x.outputs)
        else:
            return super(PluginManager,self).build_tree(x) 
        return d

    def get_plugin(self,pgin_tag):
        return self.get_data_from_uri(pgin_tag)

    def load_plugin(self,pgin_module):    
        try:
            mod = importlib.import_module('.'+pgin_module,pgns.__name__)
            return mod.__dict__[pgin_module]
        except Exception as ex:
            msg = str('Exception occurred while loading plugin {}. '
            .format(pgin_module) + 'Error message: ' + ex.message)
            self.write_log(msg)
            raise pawstools.PluginLoadError(msg)   
 
    def n_plugins(self):
        return self.n_children() 

    def list_plugin_tags(self):
        return self.root_tags()
        #r = self.get_from_idx(self.root_index())
        #return [itm.tag for itm in r.children]

