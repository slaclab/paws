from __future__ import print_function
from multiprocessing import Process,Pool
from collections import OrderedDict
import copy
import traceback
import time

from ..operations import optools
from ..operations.OpManager import OpManager
from ..plugins.PluginManager import PluginManager
from .Workflow import Workflow
from ..operations import Operation as opmod
from ..operations.Operation import Operation
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
            an operations manager (paws.core.operations.OpManager.OpManager)-
            if not provided, a default OpManager will be created.
        plugin_manager : PluginManager (optional)
            a plugins manager (paws.core.plugins.PluginManager.PluginManager)-
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
        self.message_callback = print
        self.wf_threads = OrderedDict()

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
        wf.message_callback = self.message_callback
        self.workflows[wf_name] = wf
        self.wf_running[wf_name] = False
        return wf

    def n_workflows(self):
        """Return the current number of Workflows"""
        return len(self.workflows)

    def run_workflow(self,wf_name,pool=None):
        """Execute the workflow indicated by `wf_name`"""
        wf = self.workflows[wf_name]
        self.message_callback('preparing workflow {} for execution'.format(wf_name))
        stk,diag = wf.execution_stack()
        self.prepare_wf(wf,stk)
        if pool is None:
            self.wf_running[wf_name] = True
            wf.run()
            self.message_callback('execution finished')
        else:
            wf_clone = wf.build_clone()
            wf_clone.message_callback = wf.message_callback
            wf_clone.data_callback = wf.set_item
            # TODO: how do we know when a cloned wf is finished? 
            # need to implement a finished_callback?
            # or is there something in the Process that can help?
            #wf_clone.wfFinished.connect( partial(self.stop_workflow,wf_name) )
            for op_name,op in wf_clone.operations.items():
                op.message_callback = wf.message_callback
                op.data_callback = partial( wf.set_op_item,op_name )
            self.wf_clones[wf_name] = wf_clone
            # temporary for debugging:
            wf_clone.run()
            self.message_callback('execution finished')
            #wf_proc = Process(target=wf_clone.run,name=wf_name)
            #pool[wf_name] = wf_proc 

    def stop_workflow(self,wf_name):
        """Stop the workflow indicated by `wf_name`"""
        self.message_callback('stopping workflow {}'.format(wf_name))
        if wf_name in self.wf_clones.keys():
            wf = self.wf_clones.pop(wf_name)
            wf.stop()
        else:
            wf = self.workflows[wf_name]
            wf.stop()
        self.wf_running[wf_name] = False

    def prepare_wf(self,wf,stk):
        """
        For all of the operations in stack stk,
        load all inputs that are not workflow items. 
        """
        for lst in stk:
            for op_tag in lst:
                op = wf.get_data_from_uri(op_tag)
                for inpname,il in op.input_locator.items():
                    if il.tp not in [opmod.runtime_type,opmod.workflow_item]:
                        # NOTE 1: runtime inputs should be set directly, without using il.val.
                        # this is because, when saving a workflow, il.val gets serialized.
                        # NOTE 2: workflow_item inputs should be set later, during execution.
                        wf.set_op_item(op_tag,'inputs.'+inpname,self.locate_input(il))

    def locate_input(self,il):
        """
        Return the data pointed to by a given InputLocator object.
        """
        # note, workflow items will be fetched by the workflow during execution
        if il.tp == opmod.basic_type:
            return il.val
        elif il.tp == opmod.entire_workflow:
            wf = self.workflows[il.val]
            stk,diag = wf.execution_stack()
            self.prepare_wf(wf,stk)
            return wf
            #return self.workflows[il.val]
        elif il.tp == opmod.plugin_item:
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


