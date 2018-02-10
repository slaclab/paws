from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import saxskit
 
from ... import Operation as opmod
from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    default_pops=OrderedDict())
outputs = OrderedDict(populations=None)

class SpectrumClassifierGUI(Operation):
    """Plots a SAXS spectrum and asks the user to flag its populations."""

    def __init__(self):
        super(SpectrumClassifierGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['default_pops'] = 'Dict of populations to set as initial values.' 
        self.output_doc['populations'] = 'Dict indicating the number of '\
            'each of a variety of potential scatterer populations.'

    def run(self):
        q_I = self.inputs['q_I']
        dpops = self.inputs['default_pops']
        self.pops = OrderedDict.fromkeys(saxskit.saxs_math.population_keys)
        n_pops = len(self.pops)

        if any([k not in self.pops.keys() for k in dpops.keys()]):
            msg = 'One of the default population keys is unfamiliar. '\
                + 'Default population keys: {} '.format(dpops.keys())\
                + 'Supported keys: {}'.format(self.pops.keys())
            raise KeyError(msg)
    
        self.pops.update(dpops)

        fig,ax = plt.subplots()
        plt.subplots_adjust(left=0.1,bottom=0.05*(n_pops+2))
        s = plt.semilogy(q_I[:,0],q_I[:,1],lw=2,color='black')

        self.sliders = OrderedDict() 
        for ip, popkey in enumerate(self.pops.keys()):
            if not popkey == 'unidentified':
                ax_pop = plt.axes([0.53,0.05*ip+0.03,0.35,0.03],facecolor = 'cyan')
                ax_pop.grid(True)
                p_init = int(0)
                if popkey in dpops.keys():
                    if bool(dpops[popkey]):
                        p_init = int(dpops[popkey])
                self.pops[popkey] = p_init
                sldr = Slider(ax_pop,popkey,0.,5.,valinit=p_init,valfmt="%i")
                sldr.on_changed(partial(self.set_slider,popkey))
                self.sliders[popkey] = sldr
        ax_btn = plt.axes([0.1,0.05,0.2,0.05*(n_pops)],facecolor = 'white')
        ax_btn.axis('off')
        self.btns = RadioButtons(ax_btn, ['identified','unidentified'], active=0, activecolor='red')
        self.btns.on_clicked(self.set_unidentified)
        if bool(self.pops['unidentified']):
            self.set_active(1)
        plt.show()

        # after the plot is closed,
        # expect the populations to be set
        print(self.pops)
        self.outputs['populations'] = self.pops

    def set_unidentified(self,label):
        if label == 'unidentified':
            if not bool(self.pops['unidentified']):
                self.pops['unidentified'] = 1
                for pop,sldr in self.sliders.items():
                    sldr.set_val(0.)
        elif label == 'identified':
            if bool(self.pops['unidentified']):
                self.pops['unidentified'] = 0

    def set_slider(self,pop,val):
        s = self.sliders[pop]
        s.val = round(val)
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
        self.pops[pop] = int(s.val)

