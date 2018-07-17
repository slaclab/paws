from collections import OrderedDict

import os.path

from ...Operation import Operation

inputs=OrderedDict(
    dir_path='',
    prefix='',
    filename='',
    suffix='',
    extension='')
outputs=OrderedDict(
    filename='',
    file_path='')

class BuildFilePath(Operation):
    """
    This operation helps to build file paths from workflow data.
    It takes a directory (full path), a filename, and an extension.
    The filename can optionally have a prefix or suffix inserted,
    to help with iteration of batches of files with similar names.
    """

    def __init__(self):
        super(BuildFilePath, self).__init__(inputs, outputs)
        self.input_doc['dir_path'] = 'filesystem path pointing to the directory containing the file- a trailing slash is optional'
        self.input_doc['prefix'] = 'any text to prepend to filename (prefix comes after dir_path, before filename)'
        self.input_doc['filename'] = 'name of the file: if an extension is included, it gets stripped.'
        self.input_doc['suffix'] = 'any text to append to filename (comes after filename, before ext)'
        self.input_doc['extension'] = 'extension for the file- the . is optional'
        self.output_doc['filename'] = 'filename will be <prefix><filename><suffix>' 
        self.output_doc['file_path'] = 'file_path will be <path><prefix><filename><suffix>.<extension>' 

    def run(self):
        p = self.inputs['dir_path']
        fn = self.inputs['filename']
        # strip the extension, if any?
        fn = os.path.splitext(fn)[0]
        ext = self.inputs['extension']
        if bool(ext):
            if not ext[0] == '.':
                ext = '.'+ext
        pf = self.inputs['prefix']
        sf = self.inputs['suffix']
        self.outputs['filename'] = pf+fn+sf
        full_filename = self.outputs['filename']+ext
        self.outputs['file_path'] = os.path.join(p,full_filename)
        self.message_callback('file path: {}'.format(self.outputs['file_path']))

