from os import linesep
from os.path import join, splitext
from os import listdir
import numpy as np

from slacxop import Operation
import optools
from SSRL_1_5_readers import read_header



np.savetxt(fname, X, fmt='%.18e', delimiter=' ', newline=linesep, header='# TEMPCELSIUS  FILENAME')[source]


class WriteTemperatureIndex(Operation):
    """Find .csv diffractograms; match with temperatures from headers; record."""

    def __init__(self):
        input_names = ['directory']
        output_names = ['temperatures', 'filenames']
        super(WriteTemperatureIndex, self).__init__(input_names, output_names)
        self.input_doc['directory'] = "path to directory with .csv's and .txt headers in it"
        self.output_doc['temperatures'] = 'temperatures from headers'
        self.output_doc['filenames'] = 'names of csvs'
        self.categories = ['MISC']

    def run(self):
        directory = self.inputs['directory']
        outname = 'temperature_index.csv'
        outloc = join(directory,outname)
        innames = listdir(directory)
        csvnames = []
        for ii in range(len(innames)):
            innameii = splitext(innames[ii])
            if innameii[1] == 'csv':
                csvnames.append(innames[ii])
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




        self.outputs['list_of_x_y_dy'] = []

def txtname_from_csvname(csvname):
    root = splitext(csvname)
    headername = join(root, '.txt')
    return headername