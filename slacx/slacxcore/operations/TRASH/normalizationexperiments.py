from core.operations.slacxop import Operation

import numpy as np
from matplotlib import pyplot as plt

class SelectClosestTemperatureBackgroundFromTemperature(Operation):
    """Read temperature index file written by WriteTemperatureIndex."""

    def __init__(self):
        input_names = ['background_directory','this_temperature']
        output_names = ['background_q','background_I']
        super(SelectClosestTemperatureBackgroundFromTemperature, self).__init__(input_names, output_names)
        # docstrings
        self.input_doc['background_directory'] = "path to directory with background .csv's and .txt headers in it"
        self.input_doc['this_temperature'] = "temperature we want to find a background for"
        self.output_doc['background_q'] = 'appropriate background q'
        self.output_doc['background_I'] = 'appropriate background I'
        # source & type
        self.input_src['background_directory'] = optools.fs_input
        self.input_src['this_temperature'] = optools.wf_input
        self.input_type['background_directory'] = optools.str_type
        self.input_type['this_temperature'] = optools.float_type
        self.categories = ['1D DATA PROCESSING.BACKGROUND SUBTRACTION']

    def run(self):
        directory = self.inputs['background_directory']
        this_temperature = self.inputs['this_temperature']
        indexname = 'temperature_index.csv'
        indexloc = join(directory,indexname)
        temperatures = np.loadtxt(indexloc, dtype=float, delimiter=',', skiprows=1, usecols=(0,))
        filenames = np.loadtxt(indexloc, dtype=str, delimiter=',', skiprows=1, usecols=(1,))
        diff = np.fabs(temperatures - this_temperature)
        index_of_best_temp = np.where(diff == diff.min())[0][0]
        file_of_best_temp = filenames[index_of_best_temp]
        q, I = read_csv_q_I(file_of_best_temp)
        self.outputs['background_q'] = q
        self.outputs['background_I'] = I


class SelectClosestTemperatureBackgroundFromHeader(Operation):
    """Read temperature index file written by WriteTemperatureIndex."""

    def __init__(self):
        input_names = ['background_directory','this_header']
        output_names = ['background_q','background_I']
        super(SelectClosestTemperatureBackgroundFromHeader, self).__init__(input_names, output_names)
        # docstrings
        self.input_doc['background_directory'] = "path to directory with background .csv's and .txt headers in it"
        self.input_doc['this_header'] = "header of this data; will use entry *temp_celsius*"
        self.output_doc['background_q'] = 'appropriate background q'
        self.output_doc['background_I'] = 'appropriate background I'
        # source & type
        self.input_src['background_directory'] = optools.fs_input
        self.input_src['this_header'] = optools.wf_input
        self.input_type['background_directory'] = optools.str_type
        self.categories = ['1D DATA PROCESSING.BACKGROUND SUBTRACTION']

    def run(self):
        directory = self.inputs['background_directory']
        this_temperature = self.inputs['this_header']['temp_celsius']
        indexname = 'temperature_index.csv'
        indexloc = join(directory,indexname)
        temperatures = np.loadtxt(indexloc, dtype=float, delimiter=',', skiprows=1, usecols=(0,))
        filenames = np.loadtxt(indexloc, dtype=str, delimiter=',', skiprows=1, usecols=(1,))
        diff = np.fabs(temperatures - this_temperature)
        index_of_best_temp = np.where(diff == diff.min())[0][0]
        file_of_best_temp = filenames[index_of_best_temp]
        q, I = read_csv_q_I(file_of_best_temp)
        self.outputs['background_q'] = q
        self.outputs['background_I'] = I
'''
        this_temperature = self.inputs['header']['temp_celsius']
        temperatures = np.array(self.inputs['temperatures'])
        filenames = self.inputs['filenames']
        diff = np.fabs(temperatures - this_temperature)
        index_of_best_temp = np.where(diff == diff.min())[0][0]
        file_of_best_temp = filenames[index_of_best_temp]
        self.outputs['background_tiffile'] = file_of_best_temp
'''

def find_background_temperatures(directory):
    tifnames = find_by_extension(directory, '.tif')
    txtnames = find_by_extension(directory, '.txt')
    temperatures = []
    for ii in range(len(txtnames)):
        headerii = read_header(txtnames[ii])
        temp = headerii['temp_celsius']
        temperatures.append(temp)
    return tifnames, temperatures



def find_by_extension(directory, extension):
    '''
    Find all files in *directory* ending in *extension*.

    :param directory: string path to directory
    :param extension: string extension, e.g. ".txt"
    :return:

    Accepts extensions with or without an initial ".".
    Does not know that tif and tiff are the same thing.
    '''
    # os.splitext gives the extension with '.' in front.
    # Rather than require the user to know this, I take care of it here.
    if extension[0] != '.':
        extension = '.' + extension
    innames = listdir(directory)
    extnames = []
    for ii in range(len(innames)):
        innameii = splitext(innames[ii])
        if innameii[1] == extension:
            extnames.append(join(directory, innames[ii]))
    return extnames

