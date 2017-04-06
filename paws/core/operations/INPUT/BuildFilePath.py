from ..operation import Operation
from .. import optools

class BuildFilePath(Operation):
    """
    This operation builds a file path from a filesystem directory,
    a filename provided by another workflow item or text input,
    and an extension provided by text input.
    """

    def __init__(self):
        input_names = ['dir_path','filename','ext']
        output_names = ['filepath']
        super(BuildFilePath, self).__init__(input_names, output_names)
        self.input_doc['dir_path'] = 'filesystem path pointing to the directory containing the file'
        self.input_doc['filename'] = 'name of the file, no path, no extension'
        self.input_doc['ext'] = 'extension for the file- the leading period is optional and will be appended if not provided'
        self.input_src['dir_path'] = optools.fs_input
        self.input_src['filename'] = optools.wf_input
        self.input_src['ext'] = optools.text_input
        self.input_type['dir_path'] = optools.path_type
        self.input_type['filename'] = optools.ref_type
        self.input_type['ext'] = optools.str_type
        self.output_doc['filepath'] = 'filepath will be path/to/dir/filename.ext' 

    def run(self):
        ext = self.inputs['ext']
        if not ext[0] == '.':
            ext = '.'+ext
        p = self.inputs['dir_path']
        if not p[-1] == '/':
            p = p + '/'
        fn = self.inputs['filename']
        self.outputs['filepath'] = p + fn + ext

