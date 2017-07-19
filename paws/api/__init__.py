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

    def set_plugin_input(self,pgin_tag,input_name,**kwargs):
        src,tp,val = self._parse_src_tp_val(kwargs)
        pgin = self._plugin_manager.get_data_from_uri(pgin_tag)
        if src is None:
            src = pgin.input_src[input_name]
        if tp is None:
            tp = pgin.input_type[input_name]
        if val is None:
            val = pgin.inputs[input_name]
        if src == opmod.text_input:
            pgin.inputs[input_name] = optools.cast_type_val(tp,val)
        else:
            pgin.inputs[input_name] = val 

    def start_plugin(self,pgin_name):
        pgin = self.get_plugin(pgin_name)
        pgin.start()

    def get_plugin(self,pgin_name):
        return self._plugin_manager.get_data_from_uri(pgin_name)

    def remove_op(self,op_tag,wfname=None):
        wf = self.get_wf(wfname)
        wf.remove_item(op_tag)

    def set_input(self,opname,input_name,wfname=None,**kwargs):
        op = self.get_op(opname,wfname) 
        src,tp,val = self._parse_src_tp_val(kwargs)
        if src is None:
            src = op.input_locator[input_name].src
        if tp is None:
            tp = op.input_locator[input_name].tp
        if val is None:
            val = op.input_locator[input_name].val
        il = opmod.InputLocator(src,tp,val)
        op.input_locator[input_name] = il

    @staticmethod
    def _parse_src_tp_val(kw_dict): 
        src = None
        tp = None
        val = None
        if 'src' in kw_dict:
            if kw_dict['src'] in opmod.input_sources:
                src = opmod.valid_sources[ opmod.input_sources.index(kw_dict['src']) ]
                # Any default type setting can go here.
                if src == opmod.batch_input:
                    tp = opmod.auto_type
                if src == opmod.fs_input:
                    tp = opmod.path_type
                if src == opmod.wf_input:
                    tp = opmod.ref_type
            else:
                #TODO: error? warning?
                src = opmod.no_input
        if 'tp' in kw_dict:
            if kw_dict['tp'] in opmod.input_types:
                tp = opmod.valid_types[ opmod.input_types.index(kw_dict['tp']) ]
            else:
                #TODO: error? warning?
                tp = opmod.none_type
        if 'val' in kw_dict:
            val = kw_dict['val']
        return src,tp,val

    def get_output(self,opname,output_name,wfname=None):
        op = self.get_op(opname,wfname)
        return op.outputs[output_name]

    def execute(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        self._wf_manager.run_wf(wfname)
        
    def save_config(self):
        ops.save_config()

    def save_workflow(self,wfl_filename):
        """
        Save the current workflow to a .wfl file,
        as specified by wfl_filename.
        If the given filename does not have the .wfl extension,
        it will be appended.
        """
        if not os.path.splitext(wfl_filename)[1] == '.wfl':
            wfl_filename = wfl_filename + '.wfl'
        self._wf_manager.logmethod( 'dumping workflow {} to {}'.format(self._current_wf_name,wfl_filename) )
        d = {} 
        wf_dict = OrderedDict() 
        for opname in self.current_wf().list_op_tags():
            op = self.current_wf().get_data_from_uri(opname)
            wf_dict[opname] = self._wf_manager.op_setup_dict(op)
        d['WORKFLOW'] = wf_dict
        pawstools.update_file(wfl_filename,d)

    def save_plugins(self,wfl_filename):
        """
        Save the current set of plugins to a .wfl file,
        as specified by wfl_filename.
        If the given filename does not have the .wfl extension,
        it will be appended.
        """
        if not os.path.splitext(wfl_filename)[1] == '.wfl':
            wfl_filename = wfl_filename + '.wfl'
        self._wf_manager.logmethod( 'dumping plugins to {}'.format(wfl_filename) )
        d = {} 
        pgin_dict = OrderedDict() 
        for pgin_name in self._plugin_manager.root_tags():
            if not pgin_name == 'wf_manager':
                pgin = self._plugin_manager.get_data_from_uri(pgin_name)
                pgin_dict[pgin_name] = self._plugin_manager.plugin_setup_dict(pgin)
        d['PLUGINS'] = pgin_dict
        pawstools.update_file(wfl_filename,d)

    def op_count(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        return self._wf_manager.workflows[wfname].n_children()

    def list_op_tags(self,wfname=None):
        if wfname is None:
            wfname = self._current_wf_name
        return self._wf_manager.workflows[wfname].list_op_tags()

    #def inspect_objects(self):
    #    """
    #    Use QObject.findChildren() to count references to child objects
    #    of the top-level paws resource managers.
    #    Return a report of the result as a string.
    #    """
    #    opman_children = self._op_manager.findChildren(QtCore.QObject)
    #    wfman_children = self._wf_manager.findChildren(QtCore.QObject)
    #    plugman_children = self._plugin_manager.findChildren(QtCore.QObject)
    #    rpt = str('paws QObject count:\n'
    #        + 'operations manager: {}\n{}...\n'.format(len(opman_children),opman_children)
    #        + 'plugins manager: {}\n{}\n'.format(len(plugman_children),plugman_children)
    #        + 'workflow manager: {}\n{}\n'.format(len(wfman_children),wfman_children))
    #    for wfname,wf in self._wf_manager.workflows.items():
    #        wf_children = wf.findChildren(QtCore.QObject)
    #        rpt += '\tworkflow {}: {}\n\t{}\n'.format(wfname,len(wf_children),wf_children)
    #    return rpt
        
#def core_app(app_args=[]):
#    """
#    Return a reference to a new QCoreApplication or a currently running QApplication.
#    
#    Input arguments are passed to the QApplication constructor.
#    If a RuntimeError is thrown,
#    it is assumed that a QApplication is already running,
#    and an attempt is made to return a reference to that QApplication.
#    If that fails, this returns None.
#
#    :param app_args: arguments to pass to the QApplication constructor
#    :type args: sequence
#    :returns: reference to a new or existing QCoreApplication
#    :return type: PySide.QtCore.QCoreApplication or None
#    """
#    try:
#        app = QtCore.QCoreApplication(app_args)
#    except RuntimeError:
#        try:
#            app = QtCore.QCoreApplication.instance()
#        except:
#            app = None
#    return app

