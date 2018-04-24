from collections import OrderedDict
from functools import partial

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter
from tkinter import Tk, \
Frame, Canvas, Button, Label, Entry, StringVar, OptionMenu, Scrollbar, Checkbutton
import numpy as np
#from matplotlib import pyplot as plt
#from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
import xrsdkit
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
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
        self.fit_report = None
        self.q_I_opt = None
        self.success_flag = False
        self.xrsd_fitter = XRSDFitter(self.q_I,self.populations,self.src_wl)

        self.fit_gui = Tk()
        self.fit_gui.title('xrsd profile fitter')
       
        # data structures for maintaining refs to widgets and variables 
        self.pop_frames = OrderedDict()
        self.structure_vars = OrderedDict()
        self.param_frames = OrderedDict()
        self.basis_frames = OrderedDict()
        self.basis_item_frames = OrderedDict()
        self.basis_param_frames = OrderedDict()
        self.fit_report = None
        self.q_I_opt = None

        # create the plots
        self.build_plot_widgets()
        
        # create the widgets for population control
        self.build_entry_widgets()

        # TODO: make these widgets resize when the main window is resized

        # start the tk loop
        self.fit_gui.mainloop()

        # after tk loop exits, finish Operation
        self.finish() 

    def build_plot_widgets(self):
        self.plot_frame = Frame(self.fit_gui,bd=4,relief=tkinter.SUNKEN, background="green")
        self.plot_frame.pack(side=tkinter.LEFT, expand=tkinter.YES,padx=2,pady=2)

        self.fig = Figure(figsize=(8,7))
        self.ax_plot = self.fig.add_subplot(111)
        self.plot_canvas = FigureCanvasTkAgg(self.fig,self.plot_frame)
        self.plot_canvas.get_tk_widget().pack()
        self.draw_plots()

    def build_entry_widgets(self):
        self.scroll_frame = Frame(self.fit_gui)
        self.scroll_frame.pack(side=tkinter.RIGHT,fill='y')
        self.pops_canvas = Canvas(self.scroll_frame, width=450)
        self.scroll_frame.bind_all("<MouseWheel>",  self.on_mousewheel)
        scr = Scrollbar(self.scroll_frame,orient='vertical',command=self.pops_canvas.yview)
        scr.pack(side=tkinter.RIGHT,fill='y')
        self.pops_frame = Frame(self.pops_canvas)
        scroll_canvas_config = lambda ev: self.pops_canvas.configure(scrollregion=self.pops_canvas.bbox("all"))
        self.pops_frame.bind("<Configure>",scroll_canvas_config)
        self.pops_frame.pack(side=tkinter.LEFT,fill='y')
        self.pops_canvas.create_window((0,0),window=self.pops_frame,anchor='nw')
        self.pops_canvas.configure(yscrollcommand=scr.set)
        # TODO: figure out how to get the scroll bar to not overlap the canvas
        # TODO: enable mouse wheel and track pad scrolling 
        #self.pops_canvas.configure(scrollregion=self.pops_canvas.bbox("all"),width=200,height=200)
        #self.pops_canvas.bind("<Button-4>",lambda event: print(event))
        #self.pops_canvas.bind("<Button-5>",lambda event: print(event))
        #self.pops_canvas.bind("<Button-4>", lambda event: event.widget.yview_scroll(-1, UNITS))
        #self.pops_canvas.bind("<Button-5>", lambda event: event.widget.yview_scroll(1, UNITS))
        self.pops_canvas.pack(side=tkinter.LEFT,fill='y')
        self.rebuild_entry_widgets()

    def on_mousewheel(self, event):
        if event.delta == 0:
            event.delta += 100
        self.pops_canvas.yview_scroll(-1 * event.delta, 'units')

    def finish(self):
        # TODO: check whether the user is satisfied with the result, 
        # and include this as an output or as a part of the report
        self.outputs['populations'] = self.populations
        self.outputs['report'] = self.fit_report
        self.outputs['q_I_opt'] = self.q_I_opt
        self.outputs['success_flag'] = self.success_flag

    def draw_plots(self):
        self.ax_plot.clear()
        #n_pops = len(self.populations)
        #if self.ax_plot is not None:
        #    self.fig.delaxes(self.ax_plot)
        #    #self.ax_plot.remove()
        #    self.ax_plot = None
        #self.ax_plot = plt.axes([0.08,0.05*(n_pops+2),0.45,0.9-0.05*(n_pops+2)])
        #self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        self.ax_plot.loglog(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = xrsdkit.scattering.compute_intensity(self.q_I[:,0],self.populations,self.src_wl)
        #self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.loglog(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','computed'])
        self.plot_canvas.show()

    def destroy_entry_widgets(self):
        pop_nm_list = list(self.pop_frames.keys())
        for pop_nm in pop_nm_list: 
            popfrm = self.pop_frames.pop(pop_nm)
            popfrm.pack_forget()
            popfrm.destroy()
            self.structure_vars.pop(pop_nm)
            param_nm_list = list(self.param_frames[pop_nm].keys())
            for param_nm in param_nm_list:
                param_frm = self.param_frames[pop_nm].pop(param_nm)
                param_frm.pack_forget()
                param_frm.destroy()
            site_nm_list = list(self.basis_frames[pop_nm].keys())
            for site_nm in site_nm_list: 
                site_frm = self.basis_frames[pop_nm].pop(site_nm)
                site_frm.pack_forget()
                site_frm.destroy()
                specie_nm_list = list(self.basis_item_frames[pop_nm][site_nm].keys())
                for specie_nm in specie_nm_list: 
                    specie_frms = self.basis_item_frames[pop_nm][site_nm][specie_nm]
                    for ispec in range(len(specie_frms))[::-1]:
                        specie_frm = self.basis_item_frames[pop_nm][site_nm][specie_nm].pop(ispec)
                        specie_frm.pack_forget()
                        specie_frm.destroy()
                        bparam_frms = self.basis_param_frames[pop_nm][site_nm][specie_nm][ispec]
                        bparam_nm_list = list(self.basis_param_frames[pop_nm][site_nm][specie_nm][ispec].keys())
                        for bparam_nm in bparam_nm_list:
                            bparam_frm = bparam_frms.pop(bparam_nm)
                            bparam_frm.pack_forget()
                            bparam_frm.destroy()

    def rebuild_entry_widgets(self):
        self.destroy_entry_widgets()
        # create a frame for every population
        for ipop,pop_name in enumerate(self.populations.keys()):
            popd = self.populations[pop_name]
            pf = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED) 
            self.pop_frames[pop_name] = pf
            self.param_frames[pop_name] = OrderedDict()
            self.basis_frames[pop_name] = OrderedDict()
            self.basis_item_frames[pop_name] = OrderedDict()
            self.basis_param_frames[pop_name] = OrderedDict()
            pf.pack(side=tkinter.TOP,pady=2,padx=2)

            popl = Label(pf,text='population name:',anchor='e')
            popl.grid(row=0,column=0,sticky=tkinter.E)
            popl2 = Label(pf,text=pop_name)
            popl2.grid(row=0,column=1,sticky=tkinter.W)
            #pope = Entry(pf,width=20)
            #pope.insert(0,pop_name)
            #pope.grid(row=0,column=1,sticky=tkinter.W)
            rmb = Button(pf,text='Remove',command=partial(self.remove_population,pop_name))
            rmb.grid(row=0,column=2)

            strl = Label(pf,text='structure:',width=12,anchor='e')
            strl.grid(row=1,column=0,sticky=tkinter.E)
            strvar = StringVar(pf)
            str_option_dict = OrderedDict.fromkeys(xrsdkit.structure_names)
            strcb = OptionMenu(pf,strvar,*str_option_dict)
            strvar.set(popd['structure'])
            strvar.trace('w',partial(self.update_structure,pop_name))
            strcb.grid(row=1,column=1,sticky=tkinter.W)
            self.structure_vars[pop_name] = strvar
            # TODO: connect stcb to structure selection    ????? is it done?

            paramsl = Label(pf,text='------ PARAMETERS ------')
            paramsl.grid(row=2,column=0,columnspan=3)
            npars = len(popd['parameters'])
            for ip,param_name in enumerate(xrsdkit.structure_params[popd['structure']]):
                paramf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE) 
                self.param_frames[pop_name][param_name] = paramf
                paramf.grid(row=3+ip,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)
                
                pl = Label(paramf,text='{}:'.format(param_name),width=12,anchor='e')
                pl.grid(row=0,column=0,sticky=tkinter.E)
                pe = Entry(paramf,width=20)

                param_val = xrsdkit.param_defaults[param_name]
                if param_name in popd['parameters']:
                    param_val = popd['parameters'][param_name]
                pe.insert(0,str(param_val))
                pe.grid(row=0,column=1,columnspan=2,sticky=tkinter.W)

                psw = Checkbutton(paramf,text="variable")
                varparam = not xrsdkit.fixed_param_defaults[param_name]
                # TODO: check for param in fixed_params 
                if varparam: psw.select()
                psw.grid(row=0,column=3,sticky=tkinter.W)
                pbndl = Label(paramf,text='bounds:',width=10,anchor='e')
                pbndl.grid(row=1,column=0,sticky=tkinter.E)
                pbnde1 = Entry(paramf,width=8) 
                pbnde2 = Entry(paramf,width=8)
                pbnde1.grid(row=1,column=1,sticky=tkinter.W) 
                pbnde2.grid(row=1,column=2,sticky=tkinter.W) 
                lbnd = xrsdkit.param_bound_defaults[param_name][0]
                ubnd = xrsdkit.param_bound_defaults[param_name][1] 
                # TODO: check for param in param_bounds 
                pbnde1.insert(0,str(lbnd))  
                pbnde2.insert(0,str(ubnd))
                pexpl = Label(paramf,text='expression:',width=10,anchor='e')
                pexpl.grid(row=2,column=0,sticky=tkinter.E)
                pexpe = Entry(paramf,width=16)
                # TODO: check for param in param_constraints 
                pexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W) 
                # TODO: connect pe to param entry
                # TODO: connect psw to changing fixed_params
                # TODO: connect pbnde to changing param_bounds
                # TODO: connect pexpe to setting param_constraints

            basisl = Label(pf,text='--------- BASIS ---------')
            basisl.grid(row=3+npars,column=0,columnspan=3)
            for ist,site_name in enumerate(popd['basis'].keys()):
                basisf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE) 
                self.basis_frames[pop_name][site_name] = basisf
                self.basis_item_frames[pop_name][site_name] = OrderedDict()
                self.basis_param_frames[pop_name][site_name] = OrderedDict()
                basisf.grid(row=4+npars+ist,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)
                site_def = popd['basis'][site_name]
                stl = Label(basisf,text='occupant name:',width=14,anchor='e')
                stl.grid(row=0,column=0,sticky=tkinter.E)
                ste = Entry(basisf,width=20)
                ste.insert(0,site_name)
                ste.grid(row=0,column=1,columnspan=3,sticky=tkinter.W)
                rmb = Button(basisf,text='Remove')
                rmb.grid(row=0,column=4)
                # TODO: connect the entry to renaming the occupant 
                # TODO: connect rmb to deleting the occupant 

                if popd['structure'] in xrsdkit.crystalline_structure_names:
                    coordl = Label(basisf,text='coordinates:',width=12,anchor='e')
                    coorde1 = Entry(basisf,width=6)
                    coorde2 = Entry(basisf,width=6)
                    coorde3 = Entry(basisf,width=6)
                    coordl.grid(row=1,column=0,sticky=tkinter.E)
                    coorde1.grid(row=1,column=1)
                    coorde2.grid(row=1,column=2)
                    coorde3.grid(row=1,column=3)
                    if 'coordinates' in popd['basis'][site_name]:
                        c = popd['basis'][site_name]['coordinates']
                    else:
                        c = [0,0,0]
                    coorde1.insert(0,str(c[0]))
                    coorde2.insert(0,str(c[1]))
                    coorde3.insert(0,str(c[2]))
                    # TODO: connect the entries to setting the coordinates
                    # TODO: controls for varying or constraining coords

                for ispec, specie_name in enumerate(popd['basis'][site_name].keys()):
                    if not specie_name == 'coordinates':
                        specie_def = popd['basis'][site_name][specie_name] 
                        if not isinstance(specie_def,list):
                            specie_def = [specie_def]
                        self.basis_item_frames[pop_name][site_name][specie_name] = []
                        self.basis_param_frames[pop_name][site_name][specie_name] = []
                        for specd in specie_def:
                            bitmf = Frame(basisf,bd=2,padx=10,pady=4,relief=tkinter.GROOVE) 
                            self.basis_item_frames[pop_name][site_name][specie_name].append(bitmf)
                            self.basis_param_frames[pop_name][site_name][specie_name].append(OrderedDict())
                            bitmf.grid(row=2+ispec,column=0,columnspan=5,pady=4,sticky=tkinter.E+tkinter.W)

                            specl = Label(bitmf,text='specie:'.format(ispec),width=12,anchor='e')
                            specl.grid(row=0,column=0,sticky=tkinter.E)

                            specvar = StringVar(basisf)
                            spec_option_dict = OrderedDict.fromkeys(xrsdkit.form_factor_names)
                            speccb = OptionMenu(bitmf,specvar,*spec_option_dict)
                            specvar.set(specie_name)
                            speccb.grid(row=0,column=1,sticky=tkinter.W+tkinter.E)

                            rmspecb = Button(bitmf,text='Remove')
                            rmspecb.grid(row=0,column=2)
                            # TODO: connect speccb to changing the specie
                            # TODO: connect rmspecb to removing the specie

                            for ibp,bparam_name in enumerate(xrsdkit.form_factor_params[specie_name]):
                                bparf = Frame(bitmf,bd=2,padx=4,pady=4,relief=tkinter.GROOVE) 
                                self.basis_param_frames[pop_name][site_name][specie_name][ispec][bparam_name] = bparf
                                bparf.grid(row=1+ibp,column=0,columnspan=3,sticky=tkinter.E+tkinter.W)
                                bparaml = Label(bparf,text='{}:'.format(bparam_name),width=10,anchor='e')
                                bparaml.grid(row=0,column=0,sticky=tkinter.E)
                                bparame = Entry(bparf,width=16)
                                bparam_val = xrsdkit.param_defaults[bparam_name] 
                                if bparam_name in specd: bparam_val = specd[bparam_name] 
                                bparame.insert(0,str(bparam_val))
                                bparame.grid(row=0,column=1,columnspan=2,sticky=tkinter.E+tkinter.W)
                                bparsw = Checkbutton(bparf,text="variable")
                                bparsw.grid(row=0,column=3,sticky=tkinter.W)
                                bparvar = not xrsdkit.fixed_param_defaults[bparam_name]
                                # TODO: check for bparam in fixed_params 
                                if bparvar: bparsw.select()
                                bparbndl = Label(bparf,text='bounds:',width=10,anchor='e')
                                bparbndl.grid(row=1,column=0,sticky=tkinter.E)
                                bparbnde1 = Entry(bparf,width=8) 
                                bparbnde2 = Entry(bparf,width=8)
                                lbnd = xrsdkit.param_bound_defaults[bparam_name][0]
                                ubnd = xrsdkit.param_bound_defaults[bparam_name][1] 
                                # TODO: check for bparam in param_bounds 
                                bparbnde1.insert(0,str(lbnd))  
                                bparbnde2.insert(0,str(ubnd))
                                bparbnde1.grid(row=1,column=1,sticky=tkinter.W) 
                                bparbnde2.grid(row=1,column=2,sticky=tkinter.W) 
                                bparexpl = Label(bparf,text='expression:',width=10,anchor='e')
                                bparexpl.grid(row=2,column=0,sticky=tkinter.E)
                                bparexpe = Entry(bparf,width=16) 
                                # TODO: check for bparam in param_constraints 
                                bparexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W) 
                                # TODO: connect bparame to setting the param
                                # TODO: connect bparsw to changing fixed_params
                                # TODO: connect bparbnde to changing param_bounds
                                # TODO: connect bparexpe to setting param_constraints

                # TODO: frame for adding a new specie

            # TODO: frame for adding a new site

        # TODO: frame for adding a new population
        new_pop = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        new_pop.pack(side=tkinter.TOP,pady=2,padx=2, fill="both", expand=True)
        add_pop = Label(new_pop,text='add population:',anchor='e')
        add_pop.grid(row=0,column=0,sticky=tkinter.E)
        name = Entry(new_pop,width=20)
        name.insert(0,'unique name')
        name.grid(row=0,column=1,sticky=tkinter.W)
        add_button = Button(new_pop, text='Add', width = 10, command=self.hi)
        add_button.grid(row=0,column=2, sticky=tkinter.E)

        # TODO: frame for fitting controls: 
        #   # fit button, objective readout
        #   # toggles for logI-weighted and error-weighted
        #   # toggle for user satisfaction, button for finishing

        fitting_control = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        fitting_control.pack(side=tkinter.TOP, pady=2,padx=2, fill="both", expand=True)
        error_weighted_box = Checkbutton(fitting_control,text="error weighted")
        error_weighted = True
        if error_weighted: error_weighted_box.select()
        error_weighted_box.grid(row=0,column=0)
        logI_weighted_box = Checkbutton(fitting_control, text="logI weighted")
        logI_weighted = True
        if logI_weighted: logI_weighted_box.select()
        logI_weighted_box.grid(row=0,column=1)
        #finish_button = Button(finish,text='Finish',command=partial(self.remove_population,pop_name))
        fit_button = Button(fitting_control,text='Fit',width = 10,  command=self.hi)
        fit_button.grid(row=0,column=2)
        obj = Label(fitting_control,text='obj:',anchor='e')
        obj.grid(row=1,column=0,sticky=tkinter.E)
        result = Entry(fitting_control,width=20)
        result.insert(0,'some number')
        result.grid(row=1,column=1,sticky=tkinter.W)

        finish = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        finish.pack(side=tkinter.TOP, pady=2,padx=2, fill="both", expand=True)
        fit = Checkbutton(finish,text="Good fit")
        if self.success_flag: fit.select()
        fit.grid(row=0,column=0)
        #finish_button = Button(finish,text='Finish',command=partial(self.remove_population,pop_name))
        finish_button = Button(finish,text='Finish',width = 10, command=self.hi)
        finish_button.grid(row=0,column=1)

    def hi(self):
        print('test-test')


    def remove_population(self,pop_name):
        self.populations.pop(pop_name)
        self.draw_plots()
        self.rebuild_entry_widgets()

    def update_structure(self,pop_name,var_name,dummy,mode):
        s = self.structure_vars[pop_name].get() 
        self.populations[pop_name]['structure'] = s
        new_params = OrderedDict.fromkeys(xrsdkit.structure_params[s])
        for pnm in new_params: new_params[pnm] = xrsdkit.param_defaults[pnm]
        self.populations[pop_name]['parameters'] = new_params
        new_settings = OrderedDict.fromkeys(xrsdkit.structure_settings[s])
        for snm in new_settings: new_settings[snm] = xrsdkit.setting_defaults[snm]
        self.populations[pop_name]['settings'] = new_settings
        # if the new structure is crystalline, ensure coordinates are set
        new_basis = self.populations[pop_name]['basis']
        if s in xrsdkit.crystalline_structure_names:
            for site_item_name, site_def in new_basis.items():
                site_def_keys = list(site_def.keys())
                for nm in site_def_keys:
                    if nm in xrsdkit.noncrystalline_ff_names:
                        site_def.pop(nm) 
                if not 'coordinates' in site_def:
                    site_def['coordinates'] = [0.,0.,0.]
        self.draw_plots()
        self.rebuild_entry_widgets()

    #def _rename_population(self,old_name,new_name):
    #    popd = self.populations.pop(old_name)
    #    self.populations[new_name] = popd
    #    self.setup_plots()
    #    self.setup_populations()

    #def _new_population(self,new_pop_name):
    #    self.populations[new_pop_name] = OrderedDict()
    #    self.populations[new_pop_name]['structure'] = 'diffuse' 
    #    self.populations[new_pop_name]['parameters'] = OrderedDict()
    #    self.populations[new_pop_name]['basis'] = OrderedDict()
    #    self.setup_plots()
    #    self.setup_populations()

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

