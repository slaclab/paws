from collections import OrderedDict
import copy

from ..plugins.WorkflowPlugin import WorkflowPlugin
from .Workflow import Workflow
from ..operations.Operation import Operation, Batch, Realtime        
from ..operations import optools        

class WfManager(object):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, 
    performs operations on them.
    """

    def __init__(self,plugin_manager):
        #super(WfManager,self).__init__()
        self.workflows = OrderedDict() 
        self.plugman = plugin_manager
        self.logmethod = None

    def n_wf(self):
        return len(self.workflows)

    def write_log(self,msg):
        if self.logmethod:
            self.logmethod(msg)
        else:
            print(msg)

    def add_wf(self,wfname):
        """
        Add a workflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow(self)
        self.workflows[wfname] = wf
        # for every new workflow, add a plugin 
        wf_pgin = WorkflowPlugin()
        wf_pgin.inputs['workflow'] = self.workflows[wfname] 
        wf_pgin.start()
        self.plugman.set_item(wfname,wf_pgin)

    def run_wf(self,wfname):
        """
        Serially execute the operations of WfManager.workflows[wfname].
        Uses Workflow.execution_stack() to determine execution order,
        and performs all operations in serial.
        """
        stk,diag = self.workflows[wfname].execution_stack()
        for lst in stk:
            batch_flag = isinstance(self.workflows[wfname].get_data_from_uri(lst[0]),Batch)
            rt_flag = isinstance(self.workflows[wfname].get_data_from_uri(lst[0]),Realtime)
            if not any([batch_flag,rt_flag]):
                self.execute_serial(wfname,lst)
            elif batch_flag:
                self.execute_batch(wfname,lst[0],lst[1])
            elif rt_flag:
                self.execute_realtime(wfname,lst[0],lst[1])

    def execute_batch(self,wfname,batch_op_tag,batch_stk):
        batch_op = self.workflows[wfname].get_data_from_uri(batch_op_tag) 
        optools.load_inputs(batch_op,self.workflows[wfname])
        batch_op.run()
        self.workflows[wfname].set_item(batch_op_tag,batch_op)
        n_batch = len(batch_op.input_list())
        for i in range(n_batch):
            input_dict = batch_op.input_list()[i]
            for uri,val in input_dict.items():
                self.workflows[wfname].set_item(uri,val)
            self.write_log( 'BATCH EXECUTION {} / {}'.format(i+1,n_batch) )
            for batch_lst in batch_stk:
                self.execute_serial(wfname,batch_lst)
            saved_items_dict = OrderedDict()
            for uri in batch_op.saved_items():
                save_data = self.workflows[wfname].get_data_from_uri(uri)
                save_dict = self.uri_to_embedded_dict(uri,save_data) 
                saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
            batch_op.output_list()[i] = saved_items_dict
            self.workflows[wfname].set_item(batch_op_tag,batch_op)

    def execute_realtime(self,wfname,rt_op_tag,rt_stk):
        rt_op = self.workflows[wfname].get_data_from_uri(rt_op_tag) 
        optools.load_inputs(rt_op,self.workflows[wfname])
        rt_op.run()
        self.workflows[wfname].set_item(rt_op_tag,rt_op)
        keep_running = True
        n_exec = 0
        while keep_running:
        #TODO: ways to control the loop exit condition
            vals = rt_op.input_iter().next()
            if not None in vals:
                n_exec += 1
                wait_iter = 0
                inp_dict = OrderedDict( zip(rt_op.input_routes(), vals) )
                self.write_log( 'REALTIME EXECUTION {}'.format(n_exec))
                for uri,val in inp_dict.items():
                    self.workflows[wfname].set_item(uri,val) 
                for rt_lst in rt_stk:
                    self.execute_serial(wfname,rt_lst)
                saved_items_dict = OrderedDict()
                for uri in rt_op.saved_items():
                    save_data = self.workflows[wfname].get_data_from_uri(uri)
                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
                rt_op.output_list().append(saved_items_dict)
                self.workflows[wfname].set_item(rt_op_tag,rt_op)
            else:
                if wait_iter == 0:
                    self.write_log( 'Waiting for new inputs...' )
                wait_iter += 1 
                time.sleep(float(rt_op.delay())/1000.0)
            if wait_iter > 1000:
                self.write_log( 'Waited 1000 loops of {}ms. Exiting...'.format(rt_op.delay()) )
                keep_running = False

    def execute_serial(self,wfname,op_list):
        self.write_log('workflow {} running {}'.format(wfname,op_list))
        for op_tag in op_list: 
            op = self.workflows[wfname].get_data_from_uri(op_tag) 
            optools.load_inputs(op,self.workflows[wfname])
            op.run() 
            self.workflows[wfname].set_item(op_tag,op)

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

    def load_from_dict(self,wfname,opman,opdict):
        """
        Create a workflow with name wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input opdict specifies operation setup,
        where each item in opdict provides enough information
        to get an Operation from OpManager opman
        and set up its Operation.input_locators.
        """
        self.add_wf(wfname)
        for opname, op_setup in opdict.items():
            op = self.build_op_from_dict(op_setup,opman)
            if isinstance(op,Operation):
                self.workflows[wfname].set_item(opname,op)
            else:
                self.write_log('[{}] Failed to load {}.'.format(uri))

    def op_setup_dict(self,op):
        op_mod = op.__module__[op.__module__.find('operations'):]
        op_mod = op_mod[op_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_mod
        inp_dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            inp_dct[name] = {'src':copy.copy(il.src),'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct[optools.inputs_tag] = inp_dct 
        return dct

    def build_op_from_dict(self,op_setup,opman):
        op_uri = op_setup['op_module']
        op = opman.get_data_from_uri(op_uri)
        if issubclass(op,Operation):
            op = op()
            op.load_defaults()
            il_setup_dict = op_setup[optools.inputs_tag]
            for name in op.inputs.keys():
                if name in il_setup_dict.keys():
                    src = il_setup_dict[name]['src']
                    #if 'tp' in il_setup_dict[name].keys():
                    tp = il_setup_dict[name]['tp']
                    val = il_setup_dict[name]['val']
                    if tp in optools.invalid_types[src]:
                        il = optools.InputLocator(src,optools.none_type,None)
                    else:
                        il = optools.InputLocator(src,tp,val)
                    op.input_locator[name] = il
                    # dereference any existing inputs
                    # LAP: commented out bc it should be handled in op.load_defaults()
                    #op.inputs[name] = None
            return op
        else:
            return None

    #def auto_name(self,wfname):
    #    """
    #    Generate the next unique workflow name by appending '_x',
    #    where x is a minimal nonnegative integer.
    #    """
    #    goodname = False
    #    prefix = wfname
    #    idx = 1
    #    while not goodname:
    #        if not wfname in self.workflows.keys():
    #            goodname = True
    #        else:
    #            wfname = prefix+'_{}'.format(idx)
    #            idx += 1
    #    return wfname 

