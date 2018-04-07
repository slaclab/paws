from collections import OrderedDict
from functools import partial

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import xrsdkit
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
#from saxskit import saxs_math, saxs_fit
#from saxskit.saxs_classify import SaxsClassifier
#from saxskit.saxs_regression import SaxsRegressor 
from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    populations=None,
    fixed_params=None,
    param_bounds=None,
    param_constraints=None,
    source_wavelength=None)
outputs = OrderedDict(
    populations=None,
    report=None,
    q_I_opt=None,
    success_flag=False)
        
slider_color = 'blue'

class XRSDFitGUI(Operation):
    """Interactively fit a XRSD spectrum."""

    def __init__(self):
        super(XRSDFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['populations'] = 'dict defining populations, xrsdkit format'
        self.output_doc['populations'] = 'populations with parameters optimized'
        self.output_doc['success_flag'] = 'Boolean indicating whether '\
            'or not the user was satisfied with the fit.'

    def run(self):
        self.q_I = self.inputs['q_I']
        self.populations = self.inputs['populations']
        self.src_wl = self.inputs['source_wavelength']
        self.pf = self.inputs['fixed_params']
        self.pb = self.inputs['param_bounds']
        self.pc = self.inputs['param_constraints']
        self.xrsd_fitter = XRSDFitter(self.q_I,self.populations,self.src_wl)
        #self.feats = saxs_math.profile_spectrum(self.q_I)
        #self.saxs_cls = SaxsClassifier()
        #if self.populations is None:
        #    self.populations, certs = self.saxs_cls.classify(self.feats)
        #self.params = self.inputs['params']
        #self.saxs_reg = SaxsRegressor()
        #if self.params is None:
        #    self.params = self.predict_params()
        self.setup_plots()
        #self.pop_name_axes = OrderedDict()
        #self.pop_name_boxes = OrderedDict()
        #self.rm_pop_axes = OrderedDict()
        #self.rm_pop_buttons = OrderedDict()
        #self.pop_sliders = OrderedDict()
        #self.param_axes = OrderedDict()
        #self.param_sliders = OrderedDict()
        #self.ax_fit_btn = None
        #self.ax_success_btn = None
        #self.ax_finish_btn = None
        #self.fit_btn = None
        #self.finish_btn = None
        #self.success_btn = None
        self.setup_populations()
        #self.reset_params()
        plt.show()

    def finish(self,event):
        self.outputs['populations'] = self.populations
        self.outputs['params'] = self.params
        self.outputs['success_flag'] = self._success_flag
        plt.close()

    def setup_plots(self):
        n_pops = len(self.populations)
        self.fig = plt.figure(figsize=(15,8))
        self.ax_plot = plt.axes([0.08,0.05*(n_pops+2),0.45,0.9-0.05*(n_pops+2)])
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = xrsdkit.compute_intensity(self.q_I[:,0],self.populations,self.src_wl)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','estimated'])

    def setup_populations(self):
        vcoord = 0.9
        self.pop_name_axes = OrderedDict()
        self.pop_name_boxes = OrderedDict()
        self.rm_pop_axes = OrderedDict()
        self.rm_pop_buttons = OrderedDict()
        for i_pop, pop_name in enumerate(self.populations.keys()):
            popd = self.populations[pop_name]
            # widgets for editing population name
            nm_ax = plt.axes([0.65,vcoord,0.1,0.03],facecolor = 'white') 
            nm_box = TextBox(nm_ax, 'population {} name:'.format(i_pop), initial=pop_name)
            nm_box.on_submit(partial(self._rename_population,pop_name))
            # widgets for removing the population
            rm_pop_ax = plt.axes([0.77,vcoord,0.1,0.03],facecolor = 'white')   
            rm_pop_btn = Button(rm_pop_ax,'remove')   
            rm_pop_btn.on_clicked(partial(self._remove_population,pop_name))

            self.pop_name_axes[pop_name] = nm_ax 
            self.pop_name_boxes[pop_name] = nm_box
            self.rm_pop_axes[pop_name] = rm_pop_ax 
            self.rm_pop_buttons[pop_name] = rm_pop_btn 
            vcoord -= 0.04
        # additional widgets for adding a new population
        self.ax_pop_entry = plt.axes([0.65,vcoord,0.1,0.03],facecolor = 'white')
        self.pop_entry = TextBox(self.ax_pop_entry,'new population:')
        self.pop_entry.on_submit(self._new_population)
        self.ax_add_pop_btn = plt.axes([0.77,vcoord,0.1,0.03],facecolor = 'white')
        self.add_pop_btn = Button(self.ax_add_pop_btn,'add')
        #self.btns = RadioButtons(self.ax_btn, 
        #    ['identified','unidentified'], active=0, activecolor='red')
        #self.btns.on_clicked(self._set_unidentified)
        #if bool(self.populations['unidentified']):
        #    self.set_active(1)
        #    self._set_unidentified()
        #self.pop_sliders = OrderedDict() 
        #self.pop_axes = OrderedDict()
        #max_pop = 5
        #for ip, pop_name in enumerate(saxskit.population_keys):
        #    if not pop_name == 'unidentified':
        #        ax_pop = plt.axes([0.35,0.04*(1.5+ip),0.2,0.02],facecolor=slider_color)
        #        ax_pop.set_xticks(range(max_pop),True)
        #        sldr = Slider(ax_pop,pop_name,0.,max_pop,valinit=self.populations[pop_name],valfmt="%i")
        #        sldr.on_changed(partial(self._set_pop,pop_name))
        #        self.pop_axes[pop_name] = ax_pop
        #        self.pop_sliders[pop_name] = sldr

    def _remove_population(self,pop_name,label):
        self.populations.pop(pop_name)
        plt.clf()
        self.setup_plots()
        self.setup_populations()

    def _rename_population(self,old_name,new_name):
        popd = self.populations.pop(old_name)
        self.populations[new_name] = popd
        plt.clf()
        self.setup_plots()
        self.setup_populations()

    def _new_population(self,new_pop_name):
        self.populations[new_pop_name] = OrderedDict()
        self.populations[new_pop_name]['parameters'] = OrderedDict()
        self.populations[new_pop_name]['basis'] = OrderedDict()
        plt.clf()
        self.setup_plots()
        self.setup_populations()

    def reset_params(self):
        for param_name,axs in self.param_axes.items():
            for ax in axs:
                self.fig.delaxes(ax)
        if self.ax_fit_btn is not None:
            self.fig.delaxes(self.ax_fit_btn)
        if self.ax_finish_btn is not None:
            self.fig.delaxes(self.ax_finish_btn)
        if self.ax_success_btn is not None:
            self.fig.delaxes(self.ax_success_btn)
        n_params = len(self.params)
        self.param_sliders = OrderedDict()
        self.param_axes = OrderedDict()
        ipar = 0
        for param_name,vals in self.params.items():
            self.param_axes[param_name] = []
            self.param_sliders[param_name] = []
            for ival,val in enumerate(vals):
                ax_param = plt.axes([0.7,0.9-0.04*(1+ipar),0.2,0.02],facecolor=slider_color) 
                sldr_name = param_name+str(ival)
                llim = saxs_fit.param_limits[param_name][0]
                ulim = saxs_fit.param_limits[param_name][1]
                vinit = val
                vfmt = "%.3f" 
                param_change_func = partial(self._set_param,param_name,ival)
                log_slider = param_name in ['r0_sphere','rg_gp','I0_floor',\
                    'G_gp','I0_sphere','I_pkcenter']\
                    and not vinit < llim\
                    and not vinit < 1.E-6
                if log_slider:
                    sldr_name = sldr_name + ' (log)' 
                    if llim <= 0.:
                        llim = 1.E-6
                    if ulim is None:
                        ulim = 1.E7
                    llim = np.log10(llim)
                    ulim = np.log10(ulim)
                    vinit = np.log10(vinit)
                    vfmt = "%.2e"
                    param_change_func = partial(self._set_param_logarithmic,param_name,ival)
                sldr = Slider(ax_param,sldr_name,
                    llim,ulim,valinit=vinit,valfmt=vfmt)
                if log_slider: 
                    sldr.valtext.set_text(sldr.valfmt % 10.**vinit)
                sldr.on_changed(param_change_func)
                self.param_axes[param_name].append(ax_param)
                self.param_sliders[param_name].append(sldr)
                ipar += 1
        self.ax_fit_btn = plt.axes([0.7,0.88-0.04*(1+ipar),0.2,0.03],facecolor='white')
        self.fit_btn = Button(self.ax_fit_btn,'Fit')
        self.fit_btn.on_clicked(self.fit)
        self.ax_success_btn = plt.axes([0.7,0.7-0.04*(1+ipar),0.12,0.18],facecolor='white')
        self.ax_success_btn.axis('off')
        self.success_btn = RadioButtons(self.ax_success_btn, 
            ['good fit','bad fit'], active=0, activecolor='red')
        self._success_flag = True
        self.success_btn.on_clicked(self._set_success_flag)
        self.ax_finish_btn = plt.axes([0.8,0.74-0.04*(1+ipar),0.1,0.1],facecolor='white')
        self.finish_btn = Button(self.ax_finish_btn,'Finish')
        self.finish_btn.on_clicked(self.finish)

    def fit(self,event):
        self.message_callback('fitting...')
        self.params,rpt = self.saxs_fitter.fit(self.params)
        self.reset_params()
        self.update_plots()
        self.message_callback('fit complete (obj:{})'.format(rpt['final_objective']))
        #I_opt = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.opt_params)
        #self.ax_plot.semilogy(self.q_I[:,0],I_opt,lw=2,color='green')
        #self.ax_plot.legend(['measured',
        #    'estimated (obj: {:.2f})'.format(rpt['initial_objective']),
        #    'fit (obj: {:.2f})'.format(rpt['final_objective'])])
        #self.ax_plot.redraw_in_frame()
        #for param_name,axs in self.param_axes.items():
        #    pars = self.opt_params[param_name]
        #    for ax,par in zip(axs,pars):
        #        ax.plot(par,0.,'r*')
        #        ax.redraw_in_frame()

    def _set_unidentified(self,label):
        if label == 'unidentified':
            if not bool(self.populations['unidentified']):
                self.populations['unidentified'] = 1
                for pop,sldr in self.pop_sliders.items():
                    sldr.set_val(0.)
        elif label == 'identified':
            if bool(self.populations['unidentified']):
                self.populations['unidentified'] = 0

    def _set_success_flag(self,label):
        if label == 'yes':
            self._success_flag = True
        elif label == 'no':
            self._success_flag = False

    def _set_pop(self,pop_name,val):
        s = self.pop_sliders[pop_name]
        s.val = int(round(val))
        s.poly.xy[2] = s.val,1
        s.poly.xy[3] = s.val,0
        s.valtext.set_text(s.valfmt % s.val)
        self.set_population(pop_name,s.val)
        #dp = self.predict_params()
        #self.params = saxs_fit.update_params(dp,self.params)

    def set_population(self,pop_name,val):
        self.populations[pop_name] = int(val)
        self.saxs_fitter = saxs_fit.SaxsFitter(self.q_I,self.populations)
        self.params = self.predict_params()
        self.reset_params()
        self.update_plots()

    def _set_param(self,param_name,val_idx,val):
        self.params[param_name][val_idx] = val
        self.update_plots()

    def _set_param_logarithmic(self,param_name,val_idx,val):
        self.params[param_name][val_idx] = 10.**val
        self.update_plots()
        s = self.param_sliders[param_name][val_idx]
        s.valtext.set_text(s.valfmt % 10.**val)

    def predict_params(self):
        p = self.saxs_reg.predict_params(self.populations,self.feats,self.q_I)
        if bool(self.populations['diffraction_peaks']):
            p = self.saxs_fitter.estimate_peak_params(p)
        p,r = self.saxs_fitter.fit_intensity_params(p)
        return p

    def update_plots(self):
        self.ax_plot.clear()
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = saxs_math.compute_saxs(self.q_I[:,0],self.populations,self.params)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.legend(['measured','computed'])
        self.ax_plot.redraw_in_frame()


