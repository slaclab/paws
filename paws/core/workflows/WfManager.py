from __future__ import print_function
from collections import OrderedDict
import copy
import traceback
import time

from .. import operations as ops
from .Workflow import Workflow
from ..operations import Operation as opmod
from ..operations.Operation import Operation#, Batch, Realtime        
from ..operations import optools
from .. import pawstools

class WfManager(object):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, 
    performs operations on them.
    Keeps a reference to a PluginManager
    for access to PawsPlugins.
    """

    def __init__(self):
        super(WfManager,self).__init__()
        self.workflows = OrderedDict() 
        self.logmethod = print 
        self.plugin_manager = None

    def get_op(self,wfname,op_tag):
        return self.workflows[wfname].get_data_from_uri(op_tag)

    def n_wf(self):
        return len(self.workflows)

    def add_wf(self,wfname):
        """
        Add a workflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow()
        if not wf.is_tag_valid(wfname): 
            raise pawstools.WfNameError(wf.tag_error_message(wfname))
        wf.message_callback = self.logmethod
        self.workflows[wfname] = wf

    def run_wf(self,wfname):
        """
        Execute the workflow indicated by input wfname
        """
        wf = self.workflows[wfname]
        self.logmethod('preparing workflow {} for execution'.format(wfname))
        stk,diag = wf.execution_stack()
        self.prepare_wf(wf,stk)
        wf.execute()
        self.logmethod('execution finished')

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
                        # runtime inputs should be set directly, without using il.val.
                        # this is because, when calling wf.wf_setup_dict(), il.val gets serialized.
                        # workflow_item inputs should be set later, during execution.
                        # the no_input case ends up setting the input to None
                        #op.inputs[inpname] = self.locate_input(il)
                        wf.set_op_item(op_tag,'inputs.'+inpname,self.locate_input(il))

    def locate_input(self,il):
        """
        Return the data pointed to by a given InputLocator object.
        """
        if il.tp == opmod.no_input or il.val is None:
            return None
        elif il.tp == opmod.basic_type:
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
        # changed: let basic_type inputs be loaded directly,
        # without using InputLocators.
        #elif il.tp == opmod.basic_type:
        #    return il.val

    # TODO: the following
    def check_wf(self,wf):
        """
        Check the dependencies of the workflow.
        Ensure that all loaded operations have inputs that make sense.
        Return a status code and message for each of the Operations.
        """
        pass

    def uri_to_embedded_dict(self,uri,data=None):
        path = uri.split('.')
        endtag = path[-1]
        d = OrderedDict()
        d[endtag] = data
        for tag in path[:-1][::-1]:
            parent_d = OrderedDict()
            parent_d[tag] = d
            d = parent_d
        return d

    def update_embedded_dict(self,d,d_new):
        for k,v in d_new.items():
            if k in d.keys():
                if isinstance(d[k],dict) and isinstance(d_new[k],dict):
                    # embedded dicts: recurse
                    d[k] = self.update_embedded_dict(d[k],d_new[k])
                else:
                    # existing d[k] is not dict, and d_new[k] is dict: replace  
                    d[k] = d_new[k]
            else:
                # d[k] does not exist: insert
                d[k] = v
        return d

    def load_from_dict(self,wfname,wf_spec,op_manager):
        """
        Create a workflow with name wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input dict wf_spec specifies Workflow setup,
        including all operations, Workflow.inputs, and Workflow.outputs.
        """
        self.add_wf(wfname)
        wfins = wf_spec.pop('WORKFLOW_INPUTS')
        wfouts = wf_spec.pop('WORKFLOW_OUTPUTS')
        opflags = wf_spec.pop('OP_ENABLE_FLAGS')
        for inpname,inpval in wfins.items():
            self.workflows[wfname].connect_wf_input(inpname,inpval)
        for outname,outval in wfouts.items():
            self.workflows[wfname].connect_wf_output(outname,outval)
        for op_tag, op_setup in wf_spec.items():
            self.workflows[wfname].add_op(op_tag,\
            self.workflows[wfname].build_op_from_dict(op_setup,op_manager))
            self.workflows[wfname].set_op_enabled(op_tag,opflags[op_tag])

