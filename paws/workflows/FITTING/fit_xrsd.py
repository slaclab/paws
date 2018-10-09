import os

from paws import pawstools
from paws.workflows.WfManager import WfManager 

wfmgr = WfManager()

wfmgr.add_workflow('fit_xrsd')
wfmgr.load_operations('fit_xrsd',
    read_q_I='IO.NumpyLoad',
    fit='PROCESSING.FITTING.XRSDFit',
    output_file='IO.FILESYSTEM.BuildFilePath',
    save_fit='IO.YAML.SaveXRSDSystem'
    )

wf = wfmgr.workflows['fit_xrsd']

wf.connect_input('q_I_file','read_q_I.inputs.file_path')

wf.connect('read_q_I.outputs.data','fit.inputs.q_I')
wf.connect_input('q_I','fit.inputs.q_I')
wf.connect_input('source_wavelength','fit.inputs.source_wavelength')
wf.connect_input('q_range','fit.inputs.q_range')
wf.connect_input('system','fit.inputs.system')
wf.connect_output('system_opt','fit.outputs.system')

wf.connect_input('output_dir','output_file.inputs.dir_path')
wf.connect_input('output_filename','output_file.inputs.filename')
wf.connect('read_q_I.outputs.filename','output_file.inputs.filename')
wf.connect('read_q_I.outputs.dir_path','output_file.inputs.dir_path')
wf.set_op_input('output_file','extension','yml')
wf.connect_output('output_file','output_file.outputs.file_path')

wf.connect('output_file.outputs.file_path','save_fit.inputs.file_path')
wf.connect('fit.outputs.system','save_fit.inputs.system')

wfmgr.save_to_wfl('fit_xrsd',os.path.join(pawstools.sourcedir,'workflows','FITTING','fit_xrsd.wfl'))

