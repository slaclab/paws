from collections import OrderedDict

from ...Operation import Operation
from ... import Operation as opmod 
from ... import optools

class RealtimeFromFiles(Operation):
    """
    Use file paths matching a regex to generate
    inputs for repeated execution of a workflow, 
    as the files arrive in a specified directory.
    Collects the outputs produced for each of the inputs.
    """

    def __init__(self):
        input_names = ['dir_path','regex','workflow','input_name','new_files_only','delay']
        output_names = ['realtime_inputs','realtime_outputs']
        super(RealtimeFromFiles,self).__init__(input_names,output_names)
        self.input_doc['dir_path'] = 'path to directory of input files'
        self.input_doc['regex'] = 'regular expression with wildcards, '\
            'used to filter or locate input files'
        self.input_doc['workflow'] = 'the Workflow to be executed'
        self.input_doc['input_name'] = 'name of the workflow input '\
            'where the file paths will be used'
        self.input_doc['new_files_only'] = 'if true, '\
            'ignore existing files and only process new arrivals'
        self.input_doc['delay'] = 'delay in milliseconds '\
            'before searching again when new files were not found '\
            'in the previous search'
        self.output_doc['realtime_inputs'] = 'list of dicts '\
            'containing [input_name:input_value] '\
            'for each file path used as workflow input'
        self.output_doc['realtime_outputs'] = 'list of dicts '\
            'containing [output_name:output_value] '\
            'for all of the workflow.outputs'
        self.input_type['workflow'] = opmod.entire_workflow
        self.inputs['regex'] = '*.tif' 
        self.inputs['new_files_only'] = True 
        self.inputs['delay'] = 100 
        
    def run(self):
        """
        This should create an iterator 
        whose next() gives a {uri:value} dict 
        built from the latest-arrived file 
        """
        dirpath = self.inputs['dir_path']
        rx = self.inputs['regex']
        inpnm = self.inputs['input_name']
        dly = self.inputs['delay']
        process_existing_files = not self.inputs['new_files_only']
        it = optools.FileSystemIterator(dirpath,rx,process_existing_files) 
        self.outputs['realtime_inputs'] = it
        self.outputs['realtime_outputs'] = [] 
        wf = self.inputs['workflow'] 
        nx = 0 # total number of executions
        nd = 0 # number of consecutive delays
        keep_going = True
        wf.write_log('STARTING REALTIME EXECUTION')
        while keep_going:
            p = it.next()
            if p is None:
                # delay
                if nd == 0:
                    wf.write_log('WAITING FOR FILES...')
                time.sleep(float(dly)/1000.) 
                nd+=1
                if nd == 1000:
                    wf.write_log('ABORTING')
                    keep_going = False 
            else:
                nd = 0
                #input_dict_list.append( {inpname:filename} )
                wf.set_wf_input(inpname,filename)
                wf.write_log('EXECUTION {}'.format(nx))
                nx+=1
                wf.execute()
                self.outputs['realtime_outputs'].append(wf.wf_outputs_dict())
        wf.write_log('REALTIME EXECUTION STOPPED')
                


