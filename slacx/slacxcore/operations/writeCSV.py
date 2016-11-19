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
        super(ReadTemperatureIndex, self).__init__(input_names, output_names)
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

class SelectClosestTemperatureBackground(Operation):
    """Read temperature index file written by WriteTemperatureIndex."""

    def __init__(self):
        input_names = ['directory','this_temperature']
        output_names = ['background_q','background_I']
        super(SelectClosestTemperatureBackground, self).__init__(input_names, output_names)
        self.input_doc['directory'] = "path to directory with background .csv's and .txt headers in it"
        self.input_doc['this_temperature'] = "temperature we want to find a background for"
        self.output_doc['background_q'] = 'appropriate background q'
        self.output_doc['background_I'] = 'appropriate background I'
        self.categories = ['MISC']

    def run(self):
        directory = self.inputs['directory']
        this_temperature = self.inputs['this_temperature']
        indexname = 'temperature_index.csv'
        indexloc = join(directory,indexname)
        temperatures = np.loadtxt(indexloc, dtype=float, delimiter=',', skiprows=1, usecols=(0))
        filenames = np.loadtxt(indexloc, dtype=str, delimiter=',', skiprows=1, usecols=(1))
        diff = np.fabs(temperatures - this_temperature)
        index_of_best_temp = np.where(diff == diff.min())[0][0]
        file_of_best_temp = filenames[index_of_best_temp]
        q, I = read_csv_q_I(file_of_best_temp)
        self.outputs['background_q'] = q
        self.outputs['background_I'] = I


class WriteCSV_q_I(Operation):
    """Write q and I to a csv-formatted file."""

    def __init__(self):
        input_names = ['q','I','image_location']
        output_names = ['csv_location']
        super(WriteCSV_q_I, self).__init__(input_names, output_names)
        self.categories = ['MISC']

    def run(self):
        csv_location = csvname_from_imagename(self.inputs['image_location'])
        write_csv_q_I(self.inputs['q'], self.inputs['I'], csv_location)
        self.outputs['csv_location'] = csv_location

class WriteCSV_q_I_dI(Operation):
    """Write q, I, and dI to a csv-formatted file."""

    def __init__(self):
        input_names = ['q','I','dI','image_location']
        output_names = ['csv_location']
        super(WriteCSV_q_I_dI, self).__init__(input_names, output_names)
        self.categories = ['MISC']

    def run(self):
        csv_location = csvname_from_imagename(self.inputs['image_location'])
        write_csv_q_I_dI(self.inputs['q'], self.inputs['I'], self.inputs['dI'], csv_location)
        self.outputs['csv_location'] = csv_location


def write_csv_q_I(q, I, nameloc):
    datablock = np.zeros((q.size,2),dtype=float)
    datablock[:,0] = q
    datablock[:,1] = I
    np.savetxt(nameloc, datablock, delimiter=',', newline=linesep, header='#q,I')

def write_csv_q_I_dI(q, I, dI, nameloc):
    datablock = np.zeros((q.size,3),dtype=float)
    datablock[:,0] = q
    datablock[:,1] = I
    datablock[:,2] = dI
    np.savetxt(nameloc, datablock, delimiter=',', newline=linesep, header='#q,I')


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

def csvname_from_imagename(imagename):
    root = splitext(imagename)
    csvname = join(root, '.csv')
    return csvname


def read_csv_q_I(nameloc):
    data = np.loadtxt(nameloc, dtype=float, delimiter=',', skiprows=1, usecols=(0,1))
    q = data[:,0]
    I = data[:,1]
    return q, I

def read_csv_q_I_dI(nameloc):
    data = np.loadtxt(nameloc, dtype=float, delimiter=',', skiprows=1, usecols=(0,1,2))
    q = data[:,0]
    I = data[:,1]
    dI = data[:,2]
    return q, I, dI
