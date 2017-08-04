"""This module defines a class that presents an API for paws."""
from __future__ import print_function
import os
from functools import partial
from collections import OrderedDict

from ..core import pawstools
from ..core import operations as ops
from ..core import plugins 
from ..core.operations import Operation as opmod
from ..core.operations import optools
from ..core.operations.OpManager import OpManager 
from ..core.workflow.WfManager import WfManager 
from ..core.plugins.PluginManager import PluginManager 
from ..core.plugins.WfManagerPlugin import WfManagerPlugin

def start():
    """
    Instantiate and return a PawsAPI object. 

    paws.api.start() calls the PawsAPI constructor.

    :returns: a PawsAPI object
    :return type: paws.api.PawsAPI 
    """
    return PawsAPI()

class PawsAPI(object):
    """
    A container to facilitate interaction with a set of paws objects:
    an Operations Manager, a Workflow Manager, and a Plugins Manager. 
    """

    def __init__(self):
        super(PawsAPI,self).__init__()
        # Assign a function(str) to PawsAPI.logmethod
        # to change where messages get printed
        self.logmethod = print 
        self._op_manager = OpManager()
        self._plugin_manager = PluginManager()
        self._wf_manager = WfManager(self._plugin_manager)
        # TODO: load_cats and load_ops should happen outside the api.__init__
        # so that different api instances can have different operations loaded
        self._op_manager.load_cats(ops.cat_list) 
        self._op_manager.load_ops(ops.cat_op_list)
        self._current_wf_name = None 
        wfman_pgin = WfManagerPlugin()
        wfman_pgin.inputs['wf_manager'] = self._wf_manager 
        wfman_pgin.start()
        self._plugin_manager.set_item('wf_manager',wfman_pgin)

    def write_log(self,msg):
        self.logmethod(msg)

    def info(self):   
        info_msg = str('PAWS: the Platform for Automated Workflows by SSRL. '
        + 'Version: {}'.format(pawstools.version))
        print(info_msg)
        return info_msg
 
    def enable_op(self,op_spec):
        """
        Import and enable the Operation indicated by op_spec.
        The Operation becomes available to add to workflows by paws.api.add_op()
        """
        self._op_manager.set_op_enabled(op_spec)

    def disable_op(self,op_spec):
        """
        Disable the Operation indicated by op_spec.
        The Operation becomes unavailable until it is enabled again. 
        """
        self._op_manager.set_op_enabled(op_spec,False)

    def enable_plugin(self,pgin_name=''):
        """
        This tests the compatibility between the environment and the named plugin
        by attempting to import the plugin.
        If this does not throw an ImportError, 
        then the environment satisfies the plugin dependencies.
        """
        pkg = plugins.__name__
        #print 'start plugin {} from package {}'.format(pgin_name,pkg)
        mod = importlib.import_module('.'+pgin_name,pkg)
        #for nm, itm in mod.__dict__.items():
        #    if isinstance(itm,type):
        #        if issubclass(itm,PawsPlugin) and not nm == 'PawsPlugin':
        #            pgin = getattr(mod,nm)
        #            return

    def add_wf(self,wfname):
        self._wf_manager.add_wf(wfname)
        if not self._current_wf_name:
            self.select_wf(wfname)

    def select_wf(self,wfname):
        if wfname in self._wf_manager.workflows.keys():
            self._current_wf_name = wfname
        else:
            msg = str('requested workflow {} not found in {}'
            .format(wfname,self._wf_manager.workflows.keys()))
            raise ValueError(msg)

    def current_wf(self):
        if self._current_wf_name:
            return self._wf_manager.workflows[self._current_wf_name]    
        else:
            return None

    def get_wf(self,wfname=None):
        if wfname is None:
            return self.current_wf()
        else:
            return self._wf_manager.workflows[wfname]

    def get_op(self,opname,wfname=None):
        return self.get_wf(wfname).get_data_from_uri(opname) 

    def add_op(self,op_tag,op_spec,wfname=None):
        if ops.load_flags[op_spec]:
            wf = self.get_wf(wfname)
            # get the op referred to by op_spec
            op = self._op_manager.get_data_from_uri(op_spec)
            # instantiate with default inputs
            op = op()
            op.load_defaults()
            wf.set_item(op_tag,op)
        else:
            msg = str('Attempted to add Operation {}, '.format(op_spec)
            + 'but this Operation has not been enabled. '
            + 'Enable it with paws.api.enable_op() '
            + 'before adding it to a workflow.')
            self.write_log(msg) 
            raise pawstools.OperationDisabledError(msg)

    def add_plugin(self,pgin_tag,pgin_name):
        pgin = self._plugin_manager.get_plugin(pgin_name)
        pgin = pgin()
        self._plugin_manager.set_item(pgin_tag,pgin)

    def set_plugin_input(self,pgin_tag,input_name,val=None,tp=None):
        pgin = self._plugin_manager.get_data_from_uri(pgin_tag)
        if tp is None:
            # if type is not specified, take the plugin's default 
            tp = pgin.input_type[input_name]
        else:
            if tp in opmod.input_types:
                tp = opmod.valid_types[ opmod.input_types.index(tp) ]
            #else:
            #    tp = opmod.no_input
        if tp == opmod.no_input or val is None: 
            pgin.inputs[input_name] = None
        elif (tp == opmod.filesystem_path
        or tp == opmod.string_type):
            pgin.inputs[input_name] = str(val)
        elif tp == opmod.integer_type:
            pgin.inputs[input_name] = int(val)
        elif tp == opmod.float_type:
            pgin.inputs[input_name] = float(val)
        elif tp == opmod.bool_type:
            pgin.inputs[input_name] = bool(eval(str(val)))
        else:
            msg = '[{}] failed to parse plugin input {}, tp: {}, val: {}'.format(
            __name__,input_name,tp,val)
            raise ValueError(msg)

    def start_plugin(self,pgin_name):
        pgin = self.get_plugin(pgin_name)
        pgin.start()

    def get_plugin(self,pgin_name):
        return self._plugin_manager.get_data_from_uri(pgin_name)

    def remove_op(self,op_tag,wfname=None):
        wf = self.get_wf(wfname)
        wf.remove_item(op_tag)

    def set_input(self,wfname,opname,input_name,val=None,tp=None):
        op = self.get_op(opname,wfname) 
        if not input_name in op.inputs.keys():
            msg = str('Input name {} not valid for Operation {} ({}).'
            .format(input_name,opname,type(op).__name__))
            raise KeyError(msg)
        if tp is None:
            # if type is not specified, take the operation's default 
            tp = op.input_type[input_name]
        else:
            if tp in opmod.input_types:
                tp = opmod.valid_types[ opmod.input_types.index(tp) ]
            #else:
            #    tp = opmod.no_input
        if tp == opmod.no_input: 
            val = None
        elif (tp == opmod.filesystem_path 
        or tp == opmod.workflow_path
        or tp == opmod.string_type):
            val = str(val)
        elif tp == opmod.integer_type:
            val = int(val)
        elif tp == opmod.float_type:
            val = float(val)
        elif tp == opmod.bool_type:
            val = bool(eval(str(val)))
        else:
            msg = '[{}] failed to parse plugin input {}, tp: {}, val: {}'.format(
            __name__,input_name,tp,val)

        il = opmod.InputLocator(tp,val)
        op.input_locator[input_name] = il

    #@staticmethod
    #def _parse_src_tp_val(kw_dict): 
    #    src = None
    #    tp = None
    #    val = None
    #    if 'src' in kw_dict:
    #        if kw_dict['src'] in opmod.input_sources:
    #            src = opmod.valid_sources[ opmod.input_sources.index(kw_dict['src']) ]
    #            # Any default type setting can go here.
    #            if src == opmod.batch_input:
    #                tp = opmod.auto_type
    #            if src == opmod.fs_input:
    #                tp = opmod.path_type
    #            if src == opmod.wf_input:
    #                tp = opmod.ref_type
    #        else:
    #            #TODO: error? warning?
    #            src = opmod.no_input
    #    if 'tp' in kw_dict:
    #        if kw_dict['tp'] in opmod.input_types:
    #            tp = opmod.valid_types[ opmod.input_types.index(kw_dict['tp']) ]
    #        else:
    #            #TODO: error? warning?
    #            tp = opmod.none_type
    #    if 'val' in kw_dict:
    #        val = kw_dict['val']
    #    return src,tp,val

    def get_output(self,opname,output_name,wfname=None):
        op = self.get_op(opname,wfname)
        return op.outputs[output_name]

    def execute(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        self._wf_manager.run_wf(wfname)
        
    def save_config(self):
        ops.save_config()

    def save_to_wfl(self,wfl_filename):
        """
        Save the current workflows and plugins
        to a .wfl (YAML) file,
        specified by wfl_filename.
        If the given filename does not have the .wfl extension,
        it will be appended.
        """
        if not os.path.splitext(wfl_filename)[1] == '.wfl':
            wfl_filename = wfl_filename + '.wfl'
        self._wf_manager.logmethod( 'saving current state to {}'.format(wfl_filename) )
        d = {} 
        d['OP_LOAD_FLAGS'] = ops.load_flags
        d['PAWS_VERSION'] = pawstools.version 
        wfman_dict = OrderedDict()
        for wfname,wf in self._wf_manager.workflows:
            wf_dict = OrderedDict() 
            for opname in wf.list_op_tags():
                op = wf.get_data_from_uri(opname)
                wf_dict[opname] = self._wf_manager.op_setup_dict(op)
            wfman_dict[wfname] = wf_dict
        d['WORKFLOWS'] = wfman_dict
        pgin_dict = OrderedDict() 
        for pgin_name in self._plugin_manager.list_plugins():
            pgin = self._plugin_manager.get_data_from_uri(pgin_name)
            pgin_dict[pgin_name] = self._plugin_manager.plugin_setup_dict(pgin)
        d['PLUGINS'] = pgin_dict
        #pawstools.update_file(wfl_filename,d)
        pawstools.save_file(wfl_filename,d)

    def load_from_wfl(self,wfl_filename):
        # NOTE: code duplication with paws.ui.UiManager
        f = open(wfl_filename,'r')
        d = yaml.load(f)
        f.close()
        if 'PAWS_VERSION' in d.keys():
            wfl_version = d['PAWS_VERSION']
        else:
            wfl_version = '0.0.0'
        wfl_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',wfl_version)
        wfl_vparts = list(map(int,wfl_vparts.groups()))
        current_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',pawstools.version)  
        current_vparts = list(map(int,current_vparts.groups()))
        if wfl_vparts[0] < current_vparts[0] or wfl_vparts[1] < current_vparts[1]:
            # WARNING
            self.write_log('WARNING: paws (version {}) '\
            'is trying to load a state built in version {} - '\
            'this is likely to cause things to crash, '\
            'until the workflows and plugins are reviewed/refactored '\
            'under the current version.'.format(pawstools.version,wfl_version))  
        if 'OP_LOAD_FLAGS' in d.keys():
            ops.load_flags.update(d['OP_LOAD_FLAGS'])
        if 'WORKFLOWS' in d.keys():
            wf_dict = d['WORKFLOWS']
            for wfname,wfspec in wf_dict:
                self._wf_manager.load_from_dict(wfname,self._op_manager,wfspec)
        if 'PLUGINS' in d.keys():
            pgin_dict = d['PLUGINS']
            for pgin_name,pginspec in pgin_dict:
                self._plugin_manager.load_from_dict(pgin_name,pgin_dict)
    
    def op_count(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        return self._wf_manager.workflows[wfname].n_children()

    def list_op_tags(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        return self._wf_manager.workflows[wfname].list_op_tags()


