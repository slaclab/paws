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

    def get_op(self,wfname,opname):
        return self.workflows[wfname].get_data_from_uri(opname)

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
                    if not il.tp == opmod.workflow_item:
                        #il.data = self.locate_input(il)
                        #op.inputs[name] = il.data
                        op.inputs[inpname] = self.locate_input(il)
                        wf.set_op_item(op_tag,'inputs.'+inpname,op.inputs[inpname])

    def locate_input(self,il):
        """
        Return the data pointed to by a given InputLocator object.
        """
        if il.tp == opmod.no_input or il.val is None:
            return None
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
        elif il.tp == opmod.auto_type:
            return il.val

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
        wfin_spec = wf_spec.pop('WORKFLOW_INPUTS')
        wfout_spec = wf_spec.pop('WORKFLOW_OUTPUTS')
        for inpname,inpval in wfin_spec.items():
            self.workflows[wfname].connect_wf_input(inpname,inpval)
        for outname,outval in wfout_spec.items():
            self.workflows[wfname].connect_wf_output(outname,outval)
        for opname, op_setup in wf_spec.items():
            op = self.build_op_from_dict(op_setup,op_manager)
            if isinstance(op,Operation):
                self.workflows[wfname].add_op(opname,op)
            else:
                self.logmethod('[{}] Failed to load {}.'.format(uri))

    def op_setup_dict(self,op):
        op_modulename = op.__module__[op.__module__.find('operations'):]
        op_modulename = op_modulename[op_modulename.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_modulename
        inp_dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            inp_dct[name] = {'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct[opmod.inputs_tag] = inp_dct 
        return dct

    def build_op_from_dict(self,op_setup,op_manager):
        op_uri = op_setup['op_module']
        if not ops.load_flags[op_uri]:
            op_manager.set_op_enabled(op_uri)
        op = op_manager.get_data_from_uri(op_uri)
        if issubclass(op,Operation):
            op = op()
            op.load_defaults()
            il_setup_dict = op_setup[opmod.inputs_tag]
            for name in op.inputs.keys():
                if name in il_setup_dict.keys():
                    tp = il_setup_dict[name]['tp']
                    val = il_setup_dict[name]['val']
                    op.input_locator[name] = opmod.InputLocator(tp,val) 
            return op
        else:
            return None




