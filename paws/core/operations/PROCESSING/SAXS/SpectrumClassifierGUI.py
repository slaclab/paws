from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider 
import saxskit
 
from ... import Operation as opmod
from ...Operation import Operation

inputs = OrderedDict(q_I=None)
outputs = OrderedDict(populations=None)

class SpectrumClassifierGUI(Operation):
    """Plots a SAXS spectrum and asks the user to flag its populations."""

    def __init__(self):
        super(SpectrumClassifierGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.output_doc['populations'] = 'Dict indicating the number of '\
            'each of a variety of potential scatterer populations.'

    def run(self):
        q_I = self.inputs['q_I']
        fig,ax = plt.subplots()

        pops = OrderedDict.fromkeys(saxskit.saxs_math.population_keys)
        n_pops = len(pops)
        plt.subplots_adjust(left=0.1,bottom=0.05*(n_pops+2))
        s = plt.semilogy(q_I[:,0],q_I[:,1],lw=2,color='black')
        slider_color = 'blue'
        sliders = []
        for ip, pop in enumerate(pops.keys()):
            ax_pop = plt.axes([0.25,0.05*(1+ip),0.6,0.03],facecolor = slider_color)
            sldr = Slider(ax_pop,pop,0.,5.,valinit=0.,valfmt="%i")
            sldr.on_changed(partial(self.set_slider,sldr))
            sliders.append(sldr)

        plt.show()

    @staticmethod
    def set_slider(s,val):
        s.val = round(val)
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
