from __future__ import print_function
from collections import OrderedDict
import re
#from multiprocessing import Process,Pool

import yaml

from ..operations.OpManager import OpManager
from ..plugins.PluginManager import PluginManager
from .. import pawstools
from . import import_workflow

class WfManager(object):
    """Manager for paws Workflows."""

    def __init__(self,op_manager=None,plugin_manager=None):
        """Initialize a workflow manager.

        Parameters
        ----------
        op_manager : OpManager (optional)
            an operations manager (see paws.operations.OpManager)-
            if not provided, a default OpManager will be created.
        plugin_manager : PluginManager (optional)
            a plugins manager (see paws.plugins.PluginManager)-
            if not provided, a default PluginManager will be created.
        """
        super(WfManager,self).__init__()
        if not op_manager:
            op_manager = OpManager()
        if not plugin_manager:
            plugin_manager = PluginManager()
        self.op_manager = op_manager 
        self.plugin_manager = plugin_manager 
        self.workflows = OrderedDict() 
        # dict of workflow clones for executing across threads:
        self.wf_clones = OrderedDict()
        # dict of bools to keep track of who is at work:
        self.wf_running = OrderedDict() 
        self.message_callback = self.tagged_print

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def add_workflow(self,wf_name,wf_module):
        """Name and add a workflow.
    
        If `wf_name` is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
    
        Parameters
        ----------
        wf_name : str
            name to give to the new Workflow
    
        Returns
        -------
        wf : Workflow
            a reference to the new Workflow
        """
        wf = import_workflow(wf_module)() 
        if not wf.is_key_valid(wf_name): 
            raise KeyError(wf.key_error_message(wf_name))
    #    #wf.message_callback = self.message_callback
        self.workflows[wf_name] = wf
        self.wf_running[wf_name] = False
        return wf

    #def add_operation(self,wf_name,op_name,op_module_path):
    #    """Name and add an Operation to a Workflow.
    #
    #    Parameters
    #    ----------
    #    wf_name : str
    #        name of the Workflow to add the Operation to
    #    op_name : str
    #        name to give to the new Operation
    #    op_module_path : str
    #        path to locate the Operation module (e.g. CAT.SUBCAT.OpName)
    #    """
    #    self.workflows[wf_name].add_operation(op_name,self.get_operation(op_module_path))

    #def get_operation(self,op_module_path):
    #    """Get the Operation at `op_module_path` from self.op_manager"""
    #    return self.op_manager.get_operation(op_module_path)

    def run_workflow(self,wf_name,inputs={}):
        """Execute the workflow indicated by `wf_name`.

        The workflow is cloned, and the cloned workflow is executed.
        As it runs, depending on the implementation of Workflow.run(),
        the clone may update the original Workflow's data.

        Parameters
        ----------
        wf_name : str
            Name of the workflow to be executed,
            must be one of the keys in self.workflows.

        Returns
        -------
        wf_clone.outputs : dict
            Dict containing the cloned workflow's output data.
        """
        # TODO: support running these off the main thread:
        # implement running_lock for running flag, 
        # data_lock (use in data_callback) for updating inputs/outputs
        #wf = self.workflows[wf_name]
        #self.message_callback('preparing workflow {} for execution'.format(wf_name))
        #stk,diag = wf.execution_stack()
        #wf_clone = self.prepare_wf(wf_name,inputs)
        #wf_clone.data_callback = wf.data_callback
        self.wf_clones[wf_name] = self.workflows[wf_name].build_clone()  
        self.wf_running[wf_name] = True
        self.wf_clones[wf_name].run()
        self.message_callback('execution finished')
        return wf_clone.outputs

    def stop_workflow(self,wf_name):
        """Stop the workflow indicated by `wf_name`"""
        self.message_callback('stopping workflow {}'.format(wf_name))
        if wf_name in self.wf_clones.keys():
            wf = self.wf_clones.pop(wf_name)
            wf.stop()
        self.wf_running[wf_name] = False

    def load_workflow(self,wf_name,wf_dict):
        """Load a workflow from a dict that specifies its parameters.
        
        If `wf_name` is not unique, self.workflows[wf_name] is overwritten.
        
        Parameters
        ----------
        wf_name : str
            name to be given to the new workflow
        wf_dict : dict
            dict specifying workflow setup
        """
        self.add_workflow(wf_name,wf_dict['WF_MODULE'])
        for inpname,val in wf_dict['INPUTS'].items():
            self.workflows[wf_name].inputs[inpname] = val
        #for op_tag, op_module in wf_dict['OPERATIONS'].items():
        #    self.load_operation(wf_name,op_tag,op_module)
        #for outname,out_map in wf_dict['OUTPUTS'].items():
        #    self.workflows[wf_name].connect_output(outname,out_map)
        #for input_key,val in wf_dict['OP_INPUTS'].items():
        #    self.workflows[wf_name].set_wf_item(input_key,val)
        #for out_key, in_map in wf_dict['CONNECTIONS'].items():
        #    self.workflows[wf_name].connect(out_key,in_map)
        #for op_name, dep_ops in wf_dict['DEPENDENCIES'].items():
        #    self.workflows[wf_name].set_dependency(op_name,dep_ops)
        #for op_name, flag in wf_dict['ENABLED_FLAGS'].items():
        #    self.workflows[wf_name].set_op_enabled(op_name,flag)
        #for plugin_item_key, input_map in wf_dict['PLUGIN_CONNECTIONS'].items():
        #    self.workflows[wf_name].connect_plugin(plugin_item_key,input_map)
        #for wwffnm, input_map in wf_dict['WORKFLOW_CONNECTIONS'].items():
        #    self.workflows[wf_name].connect_workflow(wwffnm,input_map)

    def load_wfm(self,wfm_filename):
        """Set up the WfManager and its OpManager and PluginManager, from a .wfm file.
    
        Parameters
        ----------
        wfm_filename : str
            path to a .wfm file to be loaded
        """
        f = open(wfm_filename,'r')
        d = yaml.load(f)
        f.close()
        if 'PAWS_VERSION' in d.keys():
            wfm_version = d['PAWS_VERSION']
        else:
            wfm_version = '0.0.0'
        wfm_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',wfm_version)
        wfm_vparts = list(map(int,wfm_vparts.groups()))
        current_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',pawstools.__version__)  
        current_vparts = list(map(int,current_vparts.groups()))
        if wfm_vparts[0] < current_vparts[0] or wfm_vparts[1] < current_vparts[1]:
            warnings.warn('WARNING: paws (version {}) does not match file version ({})'\
            .format(pawstools.__version__,wfm_version))  
        if 'OP_ENABLED_FLAGS' in d.keys():
            for op_module,flag in d['OP_ENABLED_FLAGS'].items():
                self.op_manager.enable_op(op_module)
        if 'WORKFLOWS' in d.keys():
            wf_dict = d['WORKFLOWS']
            for wf_name,wf_setup_dict in wf_dict.items():
                self.load_workflow(wf_name,wf_setup_dict)
        if 'PLUGINS' in d.keys():
            self.plugin_manager.load_plugins(d['PLUGINS'])

    def load_operations(self,*args):
        return [self.load_operation(opmd) for opmd in args]
    
    def load_operation(self,op_module):
        """Load an Operation from a dict that specifies its parameters.

        If `op_name` is not unique, the Operation is overwritten.

        Parameters
        ----------
        op_module : str 
            key for locating Operation module 
        """
        if not self.op_manager.is_op_enabled(op_module):
            self.op_manager.enable_op(op_module)
        op = self.op_manager.get_data(op_module)()
        return op

    def setup_dict(self):
        d = {} 
        d['PAWS_VERSION'] = pawstools.__version__
        d['OP_ENABLED_FLAGS'] = {k:True for k in self.op_manager.list_operations() if self.op_manager.is_op_enabled(k)}
        wfman_dict = OrderedDict.fromkeys(self.workflows.keys())
        for wfname,wf in self.workflows.items():
            wfman_dict[wfname] = wf.setup_dict()
        d['WORKFLOWS'] = wfman_dict
        d['PLUGINS'] = self.plugin_manager.setup_dict()
        return d
    
    #    wf_dict['OPERATIONS'] = OrderedDict.fromkeys(wf.operations)
    #    for op_name,op in wf.operations.items():
    #        wf_dict['OPERATIONS'][op_name] = op.__module__[op.__module__.find('operations.')+11:] 
    #    wf_dict['OP_INPUTS'] = wf.op_inputs
    #    wf_dict['CONNECTIONS'] = wf.op_connections
    #    wf_dict['DEPENDENCIES'] = wf.op_dependencies
    #    wf_dict['ENABLED_FLAGS'] = wf.op_enabled_flags()
    #    wf_dict['PLUGIN_CONNECTIONS'] = wf.plugin_connections
    #    wf_dict['WORKFLOW_CONNECTIONS'] = wf.workflow_connections

    #def save_to_wfm(self,wfm_filename):
    #    """Save workflows, plugins, and active operations to a .wfm file.
    #
    #    The .wfm file is really just a YAML file. 
    #
    #    Parameters
    #    ----------
    #    wfm_filename : str
    #        full path of the .wfm file to be saved-
    #        extension is automatically appended if not provided, 
    #        and an existing file will be overwritten.
    #    """
    #    if not os.path.splitext(wfm_filename)[1] == '.wfm':
    #        wfm_filename = wfm_filename + '.wfm'
    #    #print('saving workflow manager setup to {}'.format(wfm_filename))
    #    pawstools.save_file(wfm_filename,self.setup_dict())

    #def save_to_wfl(self,wf_name,wfl_filename):
    #    if not os.path.splitext(wfl_filename)[1] == '.wfl':
    #        wfl_filename = wfl_filename + '.wfl'
    #    #print('saving {} to {}'.format(wf_name,wfl_filename))
    #    pawstools.save_file(wfl_filename,self.wf_setup_dict(wf_name))

    ## TODO: unify workflow load/save architecture
    #
    #def load_packaged_wfm(self,wf_key):
    #    # the following import saves a .wfm configuration file 
    #    #importlib.import_module('.'+workflow_key,pawstools.wf_module)
    #    import_workflow_module(wf_key)
    #    wfm_path = pawstools.sourcedir
    #    wfm_path = os.path.join(wfm_path,'workflows')
    #    p = wf_key.split('.')
    #    for mp in p:
    #        wfm_path = os.path.join(wfm_path,mp)
    #    wfm_filename = wfm_path+'.wfm'
    #    self.load_wfm(wfm_filename)

    #def load_packaged_workflow(self,wf_name,wf_key):
    #    # the following import saves a .wfl configuration file 
    #    #importlib.import_module('.'+wf_key,pawstools.wf_module)
    #    import_workflow_module(wf_key)
    #    wf_path = pawstools.sourcedir
    #    wf_path = os.path.join(wf_path,'workflows')
    #    p = wf_key.split('.')
    #    for mp in p:
    #        wf_path = os.path.join(wf_path,mp)
    #    wf_filename = wf_path+'.wfl'
    #    f = open(wf_filename,'r')
    #    d = yaml.load(f)
    #    f.close()
    #    self.load_workflow(wf_name,d)

    #def prepare_wf(self,wf_name,inputs):
    #    wf_clone = self.workflows[wf_name].build_clone()
    #    #for pgn_itm_key,input_map in wf_clone.plugin_connections.items():
    #    #    pgn_itm = self.plugin_manager.get_data(pgn_itm_key)
    #    #    for input_key in input_map:
    #    #        wf_clone.set_data(input_key,pgn_itm)
    #    #for wf_name,input_map in wf_clone.workflow_connections.items():
    #    #    stk,diag = self.workflows[wf_name].execution_stack()
    #    #    new_wf = self.prepare_wf(wf_name,stk)
    #    #    for input_key in input_map:
    #    #        wf_clone.set_data(input_key,new_wf)
    #        # TODO: think about appropriate way for these workflows to callback,
    #        # keep in mind they may be batch-executed, maybe in parallel 
    #        #new_wf.message_callback = self.workflows[wf_name].message_callback
    #        #new_wf.data_callback = self.workflows[wf_name].data_callback
    #    return wf_clone


