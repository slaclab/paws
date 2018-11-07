from collections import OrderedDict

from xrsdkit import visualization as xrsdvis
from matplotlib import pyplot as plt

from ..Operation import Operation

inputs = OrderedDict(
    q_I=None,
    source_wavelength=None,
    dI=None,
    show_plot=False,
    system={}) 

outputs = OrderedDict() 
    

class XRSDPlot(Operation):
    """Plot computed scattering intensity on top of some input data.

    Plots the individual contributions of each population in the input `system`,
    the total scattering intensity of the system,
    and whatever input `q_I` data are provided.
    """

    def __init__(self):
        super(XRSDPlot, self).__init__(inputs, outputs)
        self.input_doc['system'] = 'material system description, as a xrsdkit.system.System'
        self.input_doc['q_I'] = 'n-by-2 array of wave vectors (1/Angstrom) and intensities (counts)'
        self.input_doc['source_wavelength'] = 'wavelength of light source, in Angstroms'
        self.input_doc['dI'] = 'n-by-1 array of intensity error estimates corresponding to `q_I`'
        self.input_doc['show_plot'] = 'boolean for whether or not to show the plot'
        self.output_doc['figure'] = 'matplotlib figure containing the plot'

    def run(self):
        q_I = self.inputs['q_I']
        src_wl = self.inputs['source_wavelength']        
        dI = self.inputs['dI']        
        show_plot = self.inputs['show_plot']        
        sys = self.inputs['system']

        mplfig = xrsdvis.plot_xrsd_fit(sys,q_I[:,0],q_I[:,1],src_wl,dI,False)

        if show_plot:
            plt.show()

        self.outputs['figure'] = mplfig 
        return self.outputs

