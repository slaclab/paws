from core.operations.slacxop import Operation

import numpy as np
from matplotlib import pyplot as plt

#'/Users/Amanda/Desktop/Travails/Programming/ImageProcessing/SampleData/Liheng/SolventCorrection/R13.csv'
#'/Users/Amanda/Desktop/Travails/Programming/ImageProcessing/SampleData/Liheng/SolventCorrection/R4.csv'

class CompareKeyword(Operation):
    """foregroundDict[key] / backgroundDict[key] = factor."""

    def __init__(self):
        input_names = ['key', 'foregroundDict', 'backgroundDict']
        output_names = ['factor']
        super(CompareKeyword, self).__init__(input_names, output_names)
        self.input_doc['key'] = 'keyword identifying the relevant quantity'
        self.input_doc['foregroundDict'] = 'header dictionary such as produced by readtxt'
        self.input_doc['backgroundDict'] = 'header dictionary such as produced by readtxt'
        self.output_doc['factor'] = 'a float factor to multiply background by before subtraction from foreground'

    def run(self):
        val1 = self.inputs['dict1'][self.inputs['key']]
        val2 = self.inputs['dict2'][self.inputs['key']]
        self.outputs['factor'] = val1/val2

class HighestMultiplier(Operation):
    """(foreground/background).max() = factor."""

    def __init__(self):
        input_names = ['foreground', 'background']
        output_names = ['factor']
        super(HighestMultiplier, self).__init__(input_names, output_names)
        self.input_doc['foreground'] = 'ndarray of intensity values'
        self.input_doc['background'] = 'ndarray of intensity values with same location values as foreground'
        self.output_doc['factor'] = 'a float factor to multiply background by before subtraction from foreground'

    def run(self):
        self.outputs['factor'] = (self.inputs['foreground']/self.inputs['background']).max()

class CompositionAnalysis(Operation):
    """solvent volume / total volume = factor."""

    def __init__(self):
        input_names = ['solventvolume', 'solutevolume']
        output_names = ['factor']
        super(HighestMultiplier, self).__init__(input_names, output_names)
        self.input_doc['solventvolume'] = 'volume of solvent used'
        self.input_doc['solutevolume'] = 'combined volume of all non-solvent in solution'
        self.output_doc['factor'] = 'a float factor to multiply background by before subtraction from foreground'

    def run(self):
        totalvolume = self.inputs['solventvolume'] + self.inputs['solutevolume']
        self.outputs['factor'] = self.inputs['solventvolume']/totalvolume


class HighQMean(Operation):
    """A factor that makes high-q intensities match well."""

    def __init__(self):
        input_names = ['foreground', 'background', 'q', 'q_cutoff']
        output_names = ['factor']
        super(HighestMultiplier, self).__init__(input_names, output_names)
        self.input_doc['foreground'] = 'ndarray of intensity values at location values q'
        self.input_doc['background'] = 'ndarray of intensity values at location values q'
        self.input_doc['q'] = 'location values'
        self.input_doc['q_cutoff'] = 'foreground and background will be compared only for q values higher than this'
        self.output_doc['factor'] = 'a float factor to multiply background by before subtraction from foreground'

    def run(self):
        highq = np.where(self.inputs['q'] > self.inputs['q_cutoff'])
        highqratio = (self.inputs['foreground']/self.inputs['background'])[highq]
        self.outputs['factor'] = (highqratio).mean()


class QMax(Operation):
    """Final element of foreground divided by final element of background."""

    def __init__(self):
        input_names = ['foreground', 'background']
        output_names = ['factor']
        super(HighestMultiplier, self).__init__(input_names, output_names)
        self.input_doc['foreground'] = 'ndarray of intensity values'
        self.input_doc['background'] = 'ndarray of intensity values with same location values as foreground'
        self.output_doc['factor'] = 'a float factor to multiply background by before subtraction from foreground'

    def run(self):
        self.outputs['factor'] = self.inputs['foreground'][-1]/self.inputs['background'][-1]


class PlotBackgroundSubtraction(Operation):
    """Plot foreground, normalized background, and difference."""

    def __init__(self):
        input_names = ['foreground', 'foregrounderror', 'background', 'backgrounderror', 'q', 'factor', 'name']
        output_names = ['fig', 'ax']
        super(HighestMultiplier, self).__init__(input_names, output_names)
        self.input_doc['foreground'] = 'ndarray of intensity values at location values q'
        self.input_doc['foregrounderror'] = 'error estimate of foreground intensity'
        self.input_doc['background'] = 'ndarray of intensity values at location values q'
        self.input_doc['backgrounderror'] = 'error estimate of background intensity'
        self.input_doc['q'] = 'location values'
        self.input_doc['factor'] = 'a float factor by which to normalize background'
        self.input_doc['name'] = 'a name for the experiment/data plotted'
        self.output_doc['fig'] = 'a matplotlib.pyplot figure'
        self.output_doc['ax'] = 'a matplotlib.pyplot axis'

    def run(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # foreground
        ax.errorbar(self.inputs['q'], self.inputs['foreground'], yerr=self.inputs['foregrounderror'])
        # background
        background = self.inputs['background']*self.inputs['factor']
        backgrounderror = self.inputs['backgrounderror']*self.inputs['factor']
        ax.errorbar(self.inputs['q'], background, yerr=backgrounderror)
        # difference
        diff = self.inputs['foreground'] - background
        differror = (self.inputs['foregrounderror']**2 + backgrounderror**2)**0.5
        ax.errorbar(self.inputs['q'], diff, yerr=differror)
        # plot nice
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('q')
        ax.set_ylabel('I')
        fig.set_title('Background subtraction for %s with factor %f' % (self.inputs['name'], self.inputs['factor']))


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

