import numpy as np
#from matplotlib import pyplot as plt
#from os.path import join

from slacxop import Operation
import optools


class GenerateSphericalDiffractionQ(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Uses r0 in real units and gives q in real units."""

    def __init__(self):
        input_names = ['r0', 'sigma_r_over_r0', 'intensity_at_zero_q', 'qmin', 'qmax', 'qstep']
        output_names = ['q', 'I']
        super(GenerateSphericalDiffractionQ, self).__init__(input_names, output_names)
        self.input_doc['r0'] = 'mean particle radius'
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['qmin'] = 'lower bound of q range of interest'
        self.input_doc['qmax'] = 'upper bound of q range of interest'
        self.input_doc['qstep'] = 'step size in q range of interest'
        self.input_src['r0'] = optools.op_input
        self.input_src['sigma_r_over_r0'] = optools.op_input
        self.input_src['intensity_at_zero_q'] = optools.op_input
        self.input_src['qmin'] = optools.text_input
        self.input_src['qmax'] = optools.text_input
        self.input_src['qstep'] = optools.text_input
        self.input_type['qmin'] = optools.float_type
        self.input_type['qmax'] = optools.float_type
        self.input_type['qstep'] = optools.float_type
        self.output_doc['q'] = '1d ndarray; wave vector values'
        self.output_doc['I'] = '1d ndarray; intensity values'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['q'] = gen_q_vector(self.inputs['qmin'], self.inputs['qmax'], self.inputs['qstep'])
        self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_r_over_r0'],
                                           self.inputs['intensity_at_zero_q'], self.outputs['q'])

class GenerateSphericalDiffraction(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Uses r0 in real units and gives q in real units."""

    def __init__(self):
        input_names = ['r0', 'sigma_r_over_r0', 'intensity_at_zero_q', 'q_vector']
        output_names = ['I']
        super(GenerateSphericalDiffraction, self).__init__(input_names, output_names)
        self.input_doc['r0'] = 'mean particle radius'
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['q_vector'] = 'q values of interest'
        self.input_src['r0'] = optools.op_input
        self.input_src['sigma_r_over_r0'] = optools.op_input
        self.input_src['intensity_at_zero_q'] = optools.op_input
        self.input_src['q_vector'] = optools.op_input
        self.output_doc['I'] = '1d ndarray; intensity values'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_r_over_r0'],
                                           self.inputs['intensity_at_zero_q'], self.inputs['q_vector'])

'''
class GenerateSphericalDiffractionX(Operation):
    """Generate a SAXS diffraction pattern for spherical nanoparticles.

    Generates pattern in units x = r0 * q, with the assumption that x0 = r0 * q0 = 1."""

    def __init__(self):
        input_names = ['sigma_x_over_x0', 'intensity_at_zero_q', 'xmin', 'xmax', 'xstep']
        output_names = ['x', 'I']
        super(GenerateSphericalDiffractionX, self).__init__(input_names, output_names)
        self.input_doc['sigma_r_over_r0'] = 'width of distribution in r divided by r0'
        self.input_doc['intensity_at_zero_q'] = 'intensity at q = 0'
        self.input_doc['xmin'] = 'lower bound of x range of interest'
        self.input_doc['xmax'] = 'upper bound of x range of interest'
        self.input_doc['xstep'] = 'step size in x range of interest'
        self.input_src['sigma_x_over_x0'] = optools.text_input
        self.input_src['intensity_at_zero_q'] = optools.text_input
        self.input_src['xmin'] = optools.text_input
        self.input_src['xmax'] = optools.text_input
        self.input_src['xstep'] = optools.text_input
        self.input_type['sigma_x_over_x0'] = optools.float_type
        self.input_type['intensity_at_zero_q'] = optools.float_type
        self.input_type['xmin'] = optools.float_type
        self.input_type['xmax'] = optools.float_type
        self.input_type['xstep'] = optools.float_type
        self.output_doc['x'] = '1d ndarray; wave vector values'
        self.output_doc['I'] = '1d ndarray; intensity values'
        self.categories = ['1D DATA PROCESSING']

    def run(self):
        self.outputs['q'], self.outputs['I'] = \
            generate_spherical_diffraction(self.inputs['r0'], self.inputs['sigma_x_over_x0'],
                                           self.inputs['intensity_at_zero_q'], self.inputs['qmin'], self.inputs['qmax'],
                                           self.inputs['qstep'])
'''

def gen_q_vector(qmin, qmax, qstep):
    q = np.arange(qmin, qmax + qstep, qstep)
    return q


def generate_spherical_diffraction(r0, poly, i0, q):
    x = q * r0
    i = i0 * blur(x, poly)
    return i

def fullFunction(x):
    y = ((np.sin(x) - x * np.cos(x)) * x**-3)**2
    return y

def gauss(x, x0, sigma):
    y = ((sigma * (2 * np.pi)**0.5)**-1 )*np.exp(-0.5 * ((x - x0)/sigma)**2)
    return y

def generateRhoFactor(factor):
    '''

    :param factor: float
    :return:

    factor should be 0.1 for a sigma 10% of size
    '''
    factorCenter = 1
    factorMin = max(factorCenter-5*factor, 0.02)
    factorMax = factorCenter+5*factor
    factorVals = np.arange(factorMin, factorMax, factor*0.02)
    rhoVals = gauss(factorVals, factorCenter, factor)
    return factorVals, rhoVals

def factorStretched(x, factor):
    effective_x = x / factor
    y = fullFunction(effective_x)
    return y

def blur(x, factor):
    factorVals, rhoVals = generateRhoFactor(factor)
    deltaFactor = factorVals[1] - factorVals[0]
    ysum = np.zeros(x.shape)
    for ii in range(len(factorVals)):
        y = factorStretched(x, factorVals[ii])
        ysum += rhoVals[ii]*y*deltaFactor
    return ysum

