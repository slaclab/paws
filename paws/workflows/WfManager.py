from __future__ import print_function
from collections import OrderedDict
from functools import partial
import copy
#from multiprocessing import Process,Pool

from ..operations.OpManager import OpManager
from ..plugins.PluginManager import PluginManager
from .Workflow import Workflow
from .. import pawstools

class WfManager(object):
    """Manager for paws Workflows. 

    The WfManager is the most-used object in paws.
    WfManager keeps a reference to a PluginManager and OpManager
    for access to whatever PawsPlugins and Operations
    are found in the current installation of paws.
    """

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
        self.pool=None

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def add_workflow(self,wf_name):
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
        wf = Workflow()
        if not wf.is_tag_valid(wf_name): 
            raise pawstools.WfNameError(wf.tag_error_message(wf_name))
        #wf.message_callback = self.message_callback
        self.workflows[wf_name] = wf
        self.wf_running[wf_name] = False
        return wf

    def add_operation(self,wf_name,op_name,op_uri):
        """Name and add an Operation to a Workflow.

        Parameters
        ----------
        wf_name : str
            name of the Workflow to add the Operation to
        op_name : str
            name to give to the new Operation
        op_uri : str
            uri for locating the Operation
        """
        self.workflows[wf_name].add_operation(op_name,self.get_operation(op_uri))

    def get_operation(self,op_uri):
        """Get the Operation at `op_uri` from self.op_manager"""
        return self.op_manager.get_operation(op_uri)

    def n_workflows(self):
        """Return the current number of Workflows"""
        return len(self.workflows)

    def run_workflow(self,wf_name):
        # TODO: support running these off the main thread:
        # implement running_lock for running flag, 
        # data_lock (use in data_callback) for updating inputs/outputs
        """Execute the workflow indicated by `wf_name`"""
        wf = self.workflows[wf_name]
        self.message_callback('preparing workflow {} for execution'.format(wf_name))
        stk,diag = wf.execution_stack()
        wf_clone = self.prepare_wf(wf_name,stk)
        wf_clone.data_callback = wf.data_callback
        self.wf_clones[wf_name] = wf_clone
        self.wf_running[wf_name] = True
        wf_clone.run()
        self.message_callback('execution finished')

    def stop_workflow(self,wf_name):
        """Stop the workflow indicated by `wf_name`"""
        self.message_callback('stopping workflow {}'.format(wf_name))
        if wf_name in self.wf_clones.keys():
            wf = self.wf_clones.pop(wf_name)
            wf.stop()
        self.wf_running[wf_name] = False

    def prepare_wf(self,wf_name,stk):
        wf_clone = self.workflows[wf_name].build_clone()
        for input_uri,pgn_itm_uri in wf_clone.plugin_connections.items():
            pgn_itm = self.plugin_manager.get_data_from_uri(pgn_itm_uri)
            wf_clone.set_item(input_uri,pgn_itm)
        for input_uri,wf_name in wf_clone.workflow_connections.items():
            stk,diag = self.workflows[wf_name].execution_stack()
            new_wf = self.prepare_wf(wf_name,stk)
            wf_clone.set_item(input_uri,wf)
            # TODO: think about appropriate way for these workflows to callback,
            # keep in mind they may be batch-executed, maybe in parallel 
            #new_wf.message_callback = self.workflows[wf_name].message_callback
            #new_wf.data_callback = self.workflows[wf_name].data_callback
        return wf_clone

    def setup_dict(self):
        """Return a dict that describes the Workflow setup.""" 
        wf_dict = OrderedDict() 
        for op_name,op in self.operations.items():
            wf_dict[op_name] = op.setup_dict()
        wf_dict['INPUTS'] = self.inputs
        wf_dict['OUTPUTS'] = self.outputs
        wf_dict['CONNECTIONS'] = self.op_connections
        wf_dict['DEPENDENCIES'] = self.op_dependencies
        wf_dict['ENABLED_FLAGS'] = self.op_enabled_flags()
        return wf_dict

    def load_workflow(self,wf_name,wf_setup_dict):
        """Load a workflow from a dict that specifies its parameters.

        If `wf_name` is not unique, self.workflows[wf_name] is overwritten.

        Parameters
        ----------
        wf_name : str
            name to be given to the new workflow
        wf_setup_dict : dict
            dict specifying workflow setup
        """
        self.add_workflow(wf_name)
        wfins = wf_setup_dict.pop('INPUTS')
        wfouts = wf_setup_dict.pop('OUTPUTS')
        cond_ins = wf_setup_dict.pop('CONDITIONAL_INPUTS')
        deps = wf_setup_dict.pop('DEPENDENCIES')
        op_enable_flags = wf_setup_dict.pop('ENABLED_FLAGS')
        for op_tag, op_setup_dict in wf_setup_dict.items():
            self.workflows[wf_name].load_operation(op_tag,op_setup_dict,self.op_manager)
            if not op_enable_flags[op_tag]:
                self.workflows[wf_name].disable_op(op_tag)
        for inpname,inpval in wfins.items():
            self.workflows[wf_name].connect_input(inpname,inpval)
        for outname,outval in wfouts.items():
            self.workflows[wf_name].connect_output(outname,outval)
        for op_name, dep_ops in deps.items():
            self.workflows[wf_name].set_dependency(op_name,dep_ops)

    def setup_dict(self):
        d = {} 
        d['OP_ENABLED_FLAGS'] = {k:True for k in self.op_manager.keys() if self.op_manager.is_op_enabled(k)}
        d['PAWS_VERSION'] = __version__
        wfman_dict = OrderedDict.fromkeys(self.workflows)
        for wfname,wf in self.workflows.items():
            wfman_dict[wfname] = wf.setup_dict() 
        d['WORKFLOWS'] = wfman_dict
        pgin_dict = OrderedDict.fromkeys(self.plugin_manager.plugins.keys()) 
        for pgin_name,pgin in self.plugin_manager.plugins.items():
            pgin_dict[pgin_name] = pgin.setup_dict()
        d['PLUGINS'] = pgin_dict
        return d

    def save_to_wfl(self,wfl_filename):
        """Save workflows, plugins, and active operations to a .wfl file.

        The .wfl file is really just a YAML file. 

        Parameters
        ----------
        wfl_filename : str
            full path of the .wfl file to be saved-
            extension is optional, 
            and an existing file will be overwritten.
        """
        if not os.path.splitext(wfl_filename)[1] == '.wfl':
            wfl_filename = wfl_filename + '.wfl'
        pawstools.save_file(wfl_filename,self.setup_dict())

# TODO: continue from here
    def load_packaged_wfl(self,workflow_uri,wf_manager):
        wf_mod = importlib.import_module('.'+workflow_uri,workflows.__name__)
        wfl_path = sourcedir
        wfl_path = os.path.join(wfl_path,'workflows')
        p = workflow_uri.split('.')
        for mp in p:
            wfl_path = os.path.join(wfl_path,mp)
        wfl_filename = wfl_path+'.wfl'
        load_wfl(wfl_filename,wf_manager)

def load_wfl(wfl_filename,wf_manager):
    """Set up a OpManager, PluginManager, and WfManager from a .wfl file.

    Parameters
    ----------
    wfl_filename : str
        path to a .wfl file to be loaded
    """
    f = open(wfl_filename,'r')
    d = yaml.load(f)
    f.close()
    if 'PAWS_VERSION' in d.keys():
        wfl_version = d['PAWS_VERSION']
    else:
        wfl_version = '0.0.0'
    wfl_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',wfl_version)
    wfl_vparts = list(map(int,wfl_vparts.groups()))
    current_vparts = re.match(r'(\d+)\.(\d+)\.(\d+)',__version__)  
    current_vparts = list(map(int,current_vparts.groups()))
    if wfl_vparts[0] < current_vparts[0] or wfl_vparts[1] < current_vparts[1]:
        warnings.warn('WARNING: paws (version {}) '\
        'is trying to load a state built in version {} - '\
        'this is likely to cause things to crash, '\
        'until the workflows and plugins are reviewed/refactored '\
        'under the current version.'.format(__version__,wfl_version))  
    if 'OP_ACTIVATION_FLAGS' in d.keys():
        for op_module,flag in d['OP_ACTIVATION_FLAGS'].items():
            if op_module in operations.op_modules:
                if flag:
                    wf_manager.op_manager.activate_op(op_module)
    if 'WORKFLOWS' in d.keys():
        wf_dict = d['WORKFLOWS']
        for wf_name,wf_setup_dict in wf_dict.items():
            wf_manager.load_workflow(wf_name,wf_setup_dict)
    if 'PLUGINS' in d.keys():
        plugins_dict = d['PLUGINS']
        for plugin_name,plugin_setup_dict in plugins_dict.items():
            wf_manager.plugin_manager.load_plugin(plugin_name,plugin_setup_dict)




