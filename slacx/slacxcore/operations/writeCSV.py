from os import linesep
from os.path import join, splitext
from os import listdir
import numpy as np

from slacxop import Operation
import optools
from SSRL_1_5_readers import read_header


class WriteTemperatureIndex(Operation):
    """Find .csv diffractograms; match with temperatures from headers; record."""

    def __init__(self):
        input_names = ['directory']
        output_names = ['temperatures', 'filenames', 'temperature_index_file']
        super(WriteTemperatureIndex, self).__init__(input_names, output_names)
        self.input_doc['directory'] = "path to directory with .csv's and .txt headers in it"
        self.output_doc['temperatures'] = 'temperatures from headers'
        self.output_doc['filenames'] = 'names of csvs'
        self.output_doc['temperature_index_file'] = 'csv-formatted file containing temperature indexed csv file names'
        self.categories = ['MISC']

    def run(self):
        directory = self.inputs['directory']
        outname = 'temperature_index.csv'
        outloc = join(directory,outname)
        csvnames = find_csvs(directory)
        temperatures = []
        for ii in range(len(csvnames)):
            headernameii = txtname_from_csvname(csvnames[ii])
            headerii = read_header(headernameii)
            temp = headerii['temp_celsius']
            temperatures.append(temp)
        outfile = open(outloc, 'w')
        outfile.write("#TEMPCELSIUS,FILENAME")
        for ii in range(len(csvnames)):
            csvmsg ='"%s"'% csvnames[ii]
            msg = str(temperatures[ii])+","+csvmsg+linesep
            outfile.write(msg)
        outfile.close()
        self.outputs['filenames'] = csvnames
        self.outputs['temperatures'] = temperatures
        self.outputs['temperature_index_file'] = outloc



class ReadTemperatureIndex(Operation):
    """Read temperature index file written by WriteTemperatureIndex."""

    def __init__(self):
        input_names = ['directory']
        output_names = ['temperatures', 'filenames', 'temperature_index_file']
        super(WriteTemperatureIndex, self).__init__(input_names, output_names)
        self.input_doc['directory'] = "path to directory with background .csv's and .txt headers in it"
        self.output_doc['temperatures'] = 'temperatures from headers'
        self.output_doc['filenames'] = 'names of csvs'
        self.output_doc['temperature_index_file'] = 'csv-formatted file containing temperature indexed csv file names'
        self.categories = ['MISC']

    def run(self):
        directory = self.inputs['directory']
        outname = 'temperature_index.csv'
        outloc = join(directory,outname)
        self.outputs['temperatures'] = np.loadtxt(outloc, dtype=float, delimiter=',', skiprows=1, usecols=(0))
        self.outputs['filenames'] = np.loadtxt(outloc, dtype=str, delimiter=',', skiprows=1, usecols=(1))
        self.outputs['temperature_index_file'] = outloc


def find_csvs(directory):
    innames = listdir(directory)
    csvnames = []
    for ii in range(len(innames)):
        innameii = splitext(innames[ii])
        if innameii[1] == 'csv':
            csvnames.append(innames[ii])
    return csvnames

def txtname_from_csvname(csvname):
    root = splitext(csvname)
    headername = join(root, '.txt')
    return headername

