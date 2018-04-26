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
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, 
    performs operations on them.
    Keeps a reference to a PluginManager
    for access to PawsPlugins.
    """

    def __init__(self,op_manager=None,plugin_manager=None):
        """Initialize a workflow manager.

        Parameters
        ----------
        op_manager : OpManager (optional)
            an operations manager (see paws.core.operations.OpManager)-
            if not provided, a default OpManager will be created.
        plugin_manager : PluginManager (optional)
            a plugins manager (see paws.core.plugins.PluginManager)-
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
        self.plugin_names = OrderedDict()
        self.message_callback = self.tagged_print
        self.pool=None

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def set_pool(self,pool):
        self.pool = pool
        self.plugin_manager.pool = pool

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

    def n_workflows(self):
        """Return the current number of Workflows"""
        return len(self.workflows)

    def run_workflow(self,wf_name):
        """Execute the workflow indicated by `wf_name`"""
        wf = self.workflows[wf_name]
        self.message_callback('preparing workflow {} for execution'.format(wf_name))
        stk,diag = wf.execution_stack()
        wf_clone = self.prepare_wf(wf_name,stk)
        wf_clone.data_callback = wf.data_callback
        #wf_clone.message_callback = wf.message_callback
        self.wf_clones[wf_name] = wf_clone
        #if pool is None:
        self.wf_running[wf_name] = True
        wf_clone.run()
        self.message_callback('execution finished')
        #else:
        #    # TODO: how do we know when a cloned wf is finished? 
        #    # need to implement a finished_callback?
        #    # or is there something in the Process that can help?
        #    #wf_clone.wfFinished.connect( partial(self.stop_workflow,wf_name) )
        #    # temporary for debugging:
        #    wf_clone.run()
        #    self.message_callback('execution finished')
        #    #wf_proc = Process(target=wf_clone.run,name=wf_name)
        #    #pool[wf_name] = wf_proc 

    def stop_workflow(self,wf_name):
        """Stop the workflow indicated by `wf_name`"""
        self.message_callback('stopping workflow {}'.format(wf_name))
        if wf_name in self.wf_clones.keys():
            wf = self.wf_clones.pop(wf_name)
            wf_pgn_names = self.plugin_names.pop(wf_name)
            wf.stop()
            for pgn_name in wf_pgn_names:
                if not any(pgn_name in pnms for pnms in self.plugin_names.values()):
                    self.plugin_manager.stop_plugin(pgn_name)
        #else:
        #    wf = self.workflows[wf_name]
        #    wf.stop()
        self.wf_running[wf_name] = False

    def prepare_wf(self,wf_name,stk):
        """
        For all of the operations in stack stk,
        load all inputs that are not workflow items. 
        """ 
        wf = self.workflows[wf_name]
        wf_clone = wf.build_clone()
        plugin_names = wf.plugin_names 
        #for op_name,op in wf_clone.operations.items():
        #    op.message_callback = wf.message_callback
        #    op.data_callback = partial( wf.set_op_item,op_name )
        for lst in stk:
            for op_tag in lst:
                op = wf_clone.get_data_from_uri(op_tag)
                for inpname,il in op.input_locator.items():
                    if il.tp == pawstools.plugin_item:
                        # Plugins are expected to be safe to communicate from any thread,
                        # so they need not be cloned or copied
                        wf_clone.set_op_item(op_tag,'inputs.'+inpname,
                        self.get_plugin_data(il))
                    elif il.tp == pawstools.entire_workflow:
                        if il.val in self.workflows.keys():
                            wf_name = il.val
                            input_wf = self.workflows[il.val]
                            input_wf_stk,diag = input_wf.execution_stack()
                            new_wf = self.prepare_wf(wf_name,input_wf_stk)
                            #new_wf = wf.build_clone()
                            # NOTE: setting this data_callback causes segfaults.
                            # TODO: figure out why the segfaults,
                            # and think of a good way to relay data back to the original workflow
                            #new_wf.data_callback = self.workflows[wf_name].data_callback
                            #new_wf.message_callback = self.workflows[wf_name].message_callback
                            wf_clone.set_op_item(op_tag,'inputs.'+inpname,new_wf)
                    elif il.tp not in [pawstools.runtime_type,pawstools.workflow_item]:
                        # NOTE 1: runtime inputs should be set at runtime, 
                        # so that the input does not get serialized,
                        # when and if the workflow gets serialized
                        # NOTE 2: workflow_item inputs are retrieved during execution
                        wf_clone.set_op_item(op_tag,'inputs.'+inpname,
                        copy.deepcopy(il.val))
                for inpname,il in op.input_locator.items():
                    if il.tp == pawstools.plugin_item and il.val is not None:
                        vals = il.val
                        if not isinstance(vals,list):
                            vals = [vals]
                        for val in vals:
                            pgin_name = val.split('.')[0]
                            if not pgin_name in plugin_names:
                                plugin_names.append(pgin_name)
        self.plugin_names[wf_name] = plugin_names
        #for pgn_name in plugin_names:
        #    if not self.plugin_manager.plugin_running[pgn_name]:
        #        self.plugin_manager.start_plugin(pgn_name) 
        return wf_clone

    def get_plugin_data(self,il):
        if isinstance(il.val,list):
            return [self.plugin_manager.get_data_from_uri(v) for v in il.val]
        else:
            return self.plugin_manager.get_data_from_uri(il.val)

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
        wfins = wf_setup_dict.pop('WORKFLOW_INPUTS')
        wfouts = wf_setup_dict.pop('WORKFLOW_OUTPUTS')
        opflags = wf_setup_dict.pop('OP_ENABLE_FLAGS')
        for op_tag, op_setup_dict in wf_setup_dict.items():
            self.workflows[wf_name].load_operation(op_tag,op_setup_dict,self.op_manager)
            if not opflags[op_tag]:
                self.workflows[wf_name].disable_op(op_tag)
        for inpname,inpval in wfins.items():
            self.workflows[wf_name].connect_input(inpname,inpval)
        for outname,outval in wfouts.items():
            self.workflows[wf_name].connect_output(outname,outval)


