from collections import OrderedDict
from functools import partial
import copy

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkinter
from tkinter import Tk, Frame, Canvas, Button, Label, Entry, \
OptionMenu, Scrollbar, Checkbutton, \
StringVar, DoubleVar, BooleanVar, IntVar
import numpy as np
import xrsdkit
from xrsdkit.fitting.xrsd_fitter import XRSDFitter
from ...Operation import Operation

inputs = OrderedDict(
    q_I=None,
    source_wavelength=None,
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={},
    q_range=[0.,float('inf')],
    good_fit_prior=False)
outputs = OrderedDict(
    populations={},
    fixed_params={},
    param_bounds={},
    param_constraints={},
    report={},
    q_I_opt = None,
    q_range=[0.,float('inf')],
    good_fit_flag=False) 

# TODO: if structure in xrsdkit.crystalline_structure_names, block form factor selections
#   for all of the xrsdkit.noncrystalline_form_factor_names.

# TODO: display the lmfit parameter names for all params and site_params.
#   see xrsdkit.fitting.xrsdfitter.XRSDFitter.flatten_params() for how lmfit parameters are named.

# TODO: whenever any param or site_param value is updated,
#   check all of self.param_constraints and update params as necessary to satisfy the constraints.

# TODO: when a param is fixed or has a constraint set,
#   make the entry widget read-only

# TODO: make plot frame zoom-able

# TODO: add sub-curves for individual populations

# TODO: generally make the gui cleaner and more user-friendly.

class XRSDFitGUI(Operation):
    """Interactively fit a XRSD spectrum."""

    def __init__(self):
        super(XRSDFitGUI, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of q(1/Angstrom) versus I(arb).'
        self.input_doc['source_wavelength'] = 'wavelength of light source, in Angstroms'
        self.input_doc['populations'] = 'dict defining populations, xrsdkit format'
        self.input_doc['fixed_params'] = 'dict defining fixed params, xrsdkit format'
        self.input_doc['param_bounds'] = 'dict defining param bounds, xrsdkit format'
        self.input_doc['param_constraints'] = 'dict defining param constraints, xrsdkit format'
        self.input_doc['good_fit_prior'] = 'flag indicating whether a good fit is expected'
        self.input_doc['q_range'] = 'lower and upper q-limits for the fit objective'
        self.output_doc['populations'] = 'populations with parameters optimized'
        self.output_doc['fixed_params'] = 'fixed_params after fitting complete'
        self.output_doc['param_bounds'] = 'param_bounds after fitting complete'
        self.output_doc['param_constraints'] = 'param_constraints after fitting complete'
        self.output_doc['report'] = 'dict reporting optimization results'
        self.output_doc['q_I_opt'] = 'computed intensity for the optimized populations'
        self.output_doc['good_fit_flag'] = 'flag indicating user satisfaction with the fit'
        self.input_datatype['populations'] = 'dict'
        self.input_datatype['fixed_params'] = 'dict'
        self.input_datatype['param_bounds'] = 'dict'
        self.input_datatype['param_constraints'] = 'dict'

    def run(self):
        self.q_I = self.inputs['q_I']
        self.src_wl = self.inputs['source_wavelength']
        self.populations = copy.deepcopy(self.inputs['populations'])
        self.fixed_params = copy.deepcopy(self.inputs['fixed_params'])
        self.param_bounds = copy.deepcopy(self.inputs['param_bounds'])
        self.param_constraints = copy.deepcopy(self.inputs['param_constraints'])
        self.q_range = self.inputs['q_range']
        self.good_fit_prior = self.inputs['good_fit_prior']
        self.fit_report = None
        self.q_I_opt = None
        self.finished = False

        self.fit_gui = Tk()
        self.fit_gui.title('xrsd profile fitter')

        scrollbar = Scrollbar(self.fit_gui, orient='horizontal')
        self.fit_gui_canvas = Canvas(self.fit_gui, width=1300, height=730) #background="green"
        scrollbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.fit_gui_canvas.pack(side=tkinter.RIGHT,fill=tkinter.BOTH, expand=tkinter.YES)
        scrollbar.config(command=self.fit_gui_canvas.xview)
        self.fit_gui_canvas.config(scrollregion=(0,0,1300,730), xscrollcommand=scrollbar.set)
        self.main_frame = Frame(self.fit_gui_canvas,bd=4,relief=tkinter.SUNKEN)#, background="green")
        self.window = self.fit_gui_canvas.create_window(0,0,window=self.main_frame, anchor='nw')
        self.fit_gui_canvas.bind("<Configure>", self.onCanvasConfigure)

        self.reset_all_widgets()

        # create the plots
        self.build_plot_widgets()

        # create the widgets for population control
        self.build_entry_widgets()

        # start the tk loop
        self.fit_gui.protocol('WM_DELETE_WINDOW',self.finish)
        self.fit_gui.mainloop()

        # if tk loop exits without calling finish(), call it now.
        #if not self.finished: 
        #    self.finish()

    def close_gui(self):
        self.finish()
        self.fit_gui_canvas = None 
        self.main_frame = None 
        self.window = None 
        self.reset_all_widgets()
        self.fit_gui.destroy()

    def reset_all_widgets(self):
        # data structures for maintaining refs to widgets
        self.pop_frames = OrderedDict()
        self.param_frames = OrderedDict()
        self.setting_frames = OrderedDict()
        self.site_frames = OrderedDict()
        self.coordinate_frames = OrderedDict()
        self.site_setting_frames = OrderedDict()
        self.site_param_frames = OrderedDict()
        self.new_site_frames = OrderedDict()
        self.new_pop_frame = None
        self.control_frame = None

        # tkinter vars for entry and display
        self.structure_vars = OrderedDict()
        self.param_vars = OrderedDict()
        self.param_fix_vars = OrderedDict()
        self.param_bound_vars = OrderedDict()
        self.param_constraint_vars = OrderedDict()
        self.setting_vars = OrderedDict()
        self.coordinate_vars = OrderedDict()
        self.coordinate_fix_vars = OrderedDict()
        self.ff_vars = OrderedDict()
        self.site_vars = OrderedDict()
        self.site_setting_vars = OrderedDict()
        self.site_param_vars = OrderedDict()
        self.site_param_fix_vars = OrderedDict()
        self.site_param_bound_vars = OrderedDict()
        self.site_param_constraint_vars = OrderedDict()
        self.new_site_vars = OrderedDict()
        self.new_pop_var = None
        self.logI_weighted_var = None
        self.error_weighted_var = None
        self.fit_obj_var = None
        self.q_range_vars = [None, None]
        self.good_fit_var = None

        

    def finish(self):
        self.outputs['populations'] = copy.deepcopy(self.populations)
        self.outputs['fixed_params'] = copy.deepcopy(self.fixed_params)
        self.outputs['param_bounds'] = copy.deepcopy(self.param_bounds)
        self.outputs['param_constraints'] = copy.deepcopy(self.param_constraints)
        self.outputs['report'] = copy.deepcopy(self.fit_report)
        self.outputs['q_I_opt'] = copy.deepcopy(self.q_I_opt)
        self.outputs['q_range'] = copy.deepcopy([self.q_range_vars[0].get(),self.q_range_vars[1].get()])
        self.outputs['good_fit_flag'] = copy.copy(self.good_fit_var.get())
        #self.finished = True
        #self.fit_gui.destroy()

    def onCanvasConfigure(self, event):
        #Resize the inner frame to match the canvas
        minWidth = self.main_frame.winfo_reqwidth()
        minHeight = self.main_frame.winfo_reqheight()

        if self.fit_gui.winfo_width() >= minWidth:
            newWidth = self.fit_gui.winfo_width()
        else:
            newWidth = minWidth
        if self.fit_gui.winfo_height() >= minHeight:
            newHeight = self.fit_gui.winfo_height()
        else:
            newHeight = minHeight
        self.fit_gui_canvas.itemconfigure(self.window, width=newWidth, height=newHeight)

    def onCanvasConfigure2(self, event):
        #Resize the inner frame to match the canvas
        minWidth = self.mplCanvas.winfo_reqwidth()
        minHeight = self.mplCanvas.winfo_reqheight()
        if self.plot_frame.winfo_width() >= minWidth:
            newWidth = self.plot_frame.winfo_width()
        else:
            newWidth = minWidth
        if self.plot_frame.winfo_height() >= minHeight:
            newHeight = self.plot_frame.winfo_height()
        else:
            newHeight = minHeight
        self.canvas.itemconfigure(self.cwid, width=newWidth, height=newHeight)

    def on_mousewheel(self, event):
        self.pops_canvas.yview_scroll(-1 * event.delta, 'units')

    #def on_mousewheel2(self, event):
        #self.canvas.yview_scroll(-1 * event.delta, 'units')

    def on_trackpad(self, event):
        if event.num == 4:
            d = -2
        elif event.num == 5:
            d = 2
        self.pops_canvas.yview_scroll(d, 'units')

    #def on_trackpad2(self, event):
    #    if event.num == 4:
    #        d = -2
    #    elif event.num == 5:
    #        d = 2
    #    self.canvas.yview_scroll(d, 'units')

    def connected_entry(self,parent,tkvar,cbfun=None,entry_width=20):
        if cbfun:
            # piggyback on entry validation to update internal data
            # NOTE: validatecommand must return a boolean, or else it will disconnect quietly
            e = Entry(parent,width=entry_width,textvariable=tkvar,validate="focusout",validatecommand=cbfun)
            # also respond to the return key
            e.bind('<Return>',cbfun)
        else:
            e = Entry(parent,width=20,textvariable=tkvar)
        return e

    def connected_checkbutton(self,parent,boolvar,cbfun,label=''):
        if cbfun:
            e = Checkbutton(parent,text=label,variable=boolvar,command=cbfun)
        else:
            e = Checkbutton(parent,text=label,variable=boolvar)
        return e

    def build_plot_widgets(self):
        self.plot_frame = Frame(self.main_frame,bd=4,relief=tkinter.SUNKEN)#, background="green")
        self.plot_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.YES,padx=2,pady=2)

        self.fig = Figure()
        self.fig.set_size_inches(8,7, forward=True)
        self.ax_plot = self.fig.add_subplot(111)

        self.canvas = Canvas(self.plot_frame, width=790)
        #self.plot_frame.bind_all("<MouseWheel>", self.on_mousewheel2)
        #self.plot_frame.bind_all("<Button-4>", self.on_trackpad2)
        #self.plot_frame.bind_all("<Button-5>", self.on_trackpad2)
        yScrollbar = Scrollbar(self.plot_frame)
        yScrollbar.pack(side=tkinter.RIGHT,fill='y')
        self.canvas.pack(fill='both',expand=True)

        self.canvas.config(yscrollcommand=yScrollbar.set)
        yScrollbar.config(command=self.canvas.yview)
        self.plot_canvas = FigureCanvasTkAgg(self.fig,self.canvas)
        self.mplCanvas = self.plot_canvas.get_tk_widget()
        self.cwid = self.canvas.create_window(0, 0, window=self.mplCanvas, anchor='nw')
        #self.canvas.config(scrollregion=self.canvas.bbox('all'))
        self.canvas.config(scrollregion=(0,0,730,730))
        self.canvas.bind("<Configure>", self.onCanvasConfigure2)
        self.draw_plots()

    def build_entry_widgets(self):
        self.scroll_frame = Frame(self.main_frame)
        self.scroll_frame.pack(side=tkinter.RIGHT,fill='y')
        #self.fit_gui_canvas.create_window(820,0,window=self.scroll_frame, anchor='nw')
        self.pops_canvas = Canvas(self.scroll_frame, width=450)# height=730
        self.scroll_frame.bind_all("<MouseWheel>", self.on_mousewheel)
        self.scroll_frame.bind_all("<Button-4>", self.on_trackpad)
        self.scroll_frame.bind_all("<Button-5>", self.on_trackpad)
        scr = Scrollbar(self.scroll_frame,orient='vertical',command=self.pops_canvas.yview)
        scr.pack(side=tkinter.RIGHT,fill='y')
        self.pops_frame = Frame(self.pops_canvas)
        scroll_canvas_config = lambda ev: self.pops_canvas.configure(scrollregion=self.pops_canvas.bbox("all"))
        self.pops_frame.bind("<Configure>",scroll_canvas_config)
        self.pops_frame.pack(side=tkinter.LEFT,fill='y')
        self.pops_canvas.create_window((0,0),window=self.pops_frame,anchor='nw')
        self.pops_canvas.configure(yscrollcommand=scr.set)
        self.pops_canvas.pack(side=tkinter.LEFT,fill='y')
        self.create_entry_widgets()
        self.create_new_pop_frame()
        self.create_control_frame()

    def draw_plots(self):
        self.ax_plot.clear()
        self.ax_plot.semilogy(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        #self.ax_plot.loglog(self.q_I[:,0],self.q_I[:,1],lw=2,color='black')
        I_est = xrsdkit.scattering.compute_intensity(self.q_I[:,0],self.populations,self.src_wl)
        self.ax_plot.semilogy(self.q_I[:,0],I_est,lw=2,color='red')
        colors='gbcmyk'
        for ip,nm in enumerate(self.pop_frames.keys()):
            pd = self.populations[nm]
            I_p = xrsdkit.scattering.compute_intensity(self.q_I[:,0],{nm:pd},self.src_wl)
            self.ax_plot.semilogy(self.q_I[:,0],I_p,lw=1,color=colors[ip])
        #self.ax_plot.loglog(self.q_I[:,0],I_est,lw=2,color='red')
        self.ax_plot.set_xlabel('q (1/Angstrom)')
        self.ax_plot.set_ylabel('Intensity (counts)')
        self.ax_plot.legend(['measured','computed']+list(self.pop_frames.keys()))
        self.plot_canvas.draw()

    def create_entry_widgets(self):
        self.pop_frames = OrderedDict()
        # create a frame for every population
        for pop_nm in self.populations.keys():
            self.create_pop_frame(pop_nm)

    def create_pop_frame(self,pop_nm):
        popd = self.populations[pop_nm]
        pf = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        self.pop_frames[pop_nm] = pf

        popl = Label(pf,text='population name:',anchor='e')
        popl.grid(row=0,column=0,sticky=tkinter.E)
        popnml = Label(pf,text=pop_nm,anchor='w')
        popnml.grid(row=0,column=1,sticky=tkinter.W)
        rmb = Button(pf,text='Remove',command=partial(self.remove_population,pop_nm))
        rmb.grid(row=0,column=2,sticky=tkinter.E+tkinter.W)

        strl = Label(pf,text='structure:',width=12,anchor='e')
        strl.grid(row=1,column=0,sticky=tkinter.E)
        strvar = StringVar(pf)
        str_option_dict = OrderedDict.fromkeys(xrsdkit.structure_names)
        strcb = OptionMenu(pf,strvar,*str_option_dict)
        strvar.set(popd['structure'])
        strvar.trace('w',partial(self.update_structure,pop_nm))
        strcb.grid(row=1,column=1,columnspan=2,sticky=tkinter.E+tkinter.W)
        self.structure_vars[pop_nm] = strvar

        self.create_setting_frames(pop_nm)
        self.create_param_frames(pop_nm)
        self.create_site_frames(pop_nm)
        pf.pack(side=tkinter.TOP,pady=2,padx=2)
        if self.new_pop_frame is not None:
            self.repack_new_pop_frame()
        if self.control_frame is not None:
            self.repack_control_frame()

    def create_setting_frames(self,pop_nm):
        self.setting_frames[pop_nm] = OrderedDict()
        self.setting_vars[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        settingsl = Label(pf,text='------- SETTINGS -------')
        settingsl.grid(row=2,column=0,columnspan=3)
        for istg,stg_nm in enumerate(xrsdkit.structure_settings[popd['structure']]):
            stgf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE)

            if xrsdkit.setting_datatypes[stg_nm] is str:
                stgv = StringVar(pf)
            elif xrsdkit.setting_datatypes[stg_nm] is int:
                stgv = IntVar(pf)
            elif xrsdkit.setting_datatypes[stg_nm] is float:
                stgv = DoubleVar(pf)
            self.setting_frames[pop_nm][stg_nm] = stgf
            self.setting_vars[pop_nm][stg_nm] = stgv

            stgl = Label(stgf,text='{}:'.format(stg_nm),width=12,anchor='e')
            stgl.grid(row=0,column=0,sticky=tkinter.E)
            s = xrsdkit.setting_defaults[stg_nm]
            if stg_nm in popd['settings']:
                s = popd['settings'][stg_nm]
            stgv.set(str(s))
            stge = self.connected_entry(stgf,stgv,partial(self.update_setting,pop_nm,stg_nm,True))
            stge.grid(row=0,column=1,columnspan=2,sticky=tkinter.W)
            stgf.grid(row=3+istg,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    def create_param_frames(self,pop_nm):
        self.param_frames[pop_nm] = OrderedDict()
        self.param_vars[pop_nm] = OrderedDict()
        self.param_fix_vars[pop_nm] = OrderedDict()
        self.param_bound_vars[pop_nm] = OrderedDict()
        self.param_constraint_vars[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        paramsl = Label(pf,text='------ PARAMETERS ------')
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        paramsl.grid(row=3+nstgs,column=0,columnspan=3)
        for ip,param_nm in enumerate(xrsdkit.structure_params[popd['structure']]):
            paramf = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE)
            paramv = DoubleVar(pf)
            p = xrsdkit.param_defaults[param_nm]
            if param_nm in popd['parameters']:
                p = popd['parameters'][param_nm]
            paramv.set(p)
            self.param_frames[pop_nm][param_nm] = paramf
            self.param_vars[pop_nm][param_nm] = paramv

            pl = Label(paramf,text='{}:'.format(param_nm),width=12,anchor='e')
            pl.grid(row=0,column=0,sticky=tkinter.E)
            pe = self.connected_entry(paramf,paramv,partial(self.update_param,pop_nm,param_nm,True))
            pe.grid(row=0,column=1,columnspan=2,sticky=tkinter.W)

            pfixvar = BooleanVar(pf)
            pfx = xrsdkit.fixed_param_defaults[param_nm]
            if xrsdkit.contains_param(self.fixed_params,pop_nm,param_nm):
                pfx = self.fixed_params[pop_nm]['parameters'][param_nm]
            pfixvar.set(pfx)
            self.param_fix_vars[pop_nm][param_nm] = pfixvar
            psw = self.connected_checkbutton(paramf,pfixvar,
                partial(self.update_fixed_param,pop_nm,param_nm),'fixed')

            psw.grid(row=0,column=3,sticky=tkinter.W)
            pbndl = Label(paramf,text='bounds:',width=10,anchor='e')
            pbndl.grid(row=1,column=0,sticky=tkinter.E)
            lbndv = DoubleVar(pf)
            ubndv = DoubleVar(pf)
            lbnd = xrsdkit.param_bound_defaults[param_nm][0]
            ubnd = xrsdkit.param_bound_defaults[param_nm][1]
            if xrsdkit.contains_param(self.param_bounds,pop_nm,param_nm):
                lbnd = self.param_bounds[pop_nm]['parameters'][param_nm][0]
                ubnd = self.param_bounds[pop_nm]['parameters'][param_nm][1]
            if lbnd is None: lbnd = float('inf')
            if ubnd is None: ubnd = float('inf')
            lbndv.set(lbnd)
            ubndv.set(ubnd)
            self.param_bound_vars[pop_nm][param_nm]=[lbndv,ubndv]
            pbnde1 = self.connected_entry(paramf,lbndv,partial(self.update_param_bound,pop_nm,param_nm,0),8)
            pbnde2 = self.connected_entry(paramf,ubndv,partial(self.update_param_bound,pop_nm,param_nm,1),8)
            pbnde1.grid(row=1,column=1,sticky=tkinter.W)
            pbnde2.grid(row=1,column=2,sticky=tkinter.W)

            pexpl = Label(paramf,text='expression:',width=10,anchor='e')
            pexpl.grid(row=2,column=0,sticky=tkinter.E)
            expr = StringVar(pf)
            expr.set("")
            if xrsdkit.contains_param(self.param_constraints,pop_nm,param_nm):
                expr.set(self.param_constraints[pop_nm]['parameters'][param_nm])
            self.param_constraint_vars[pop_nm][param_nm] = expr
            pexpe = self.connected_entry(paramf,expr,partial(self.update_param_constraints,pop_nm,param_nm))
            pexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W)
            paramf.grid(row=4+nstgs+ip,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    def create_site_frames(self,pop_nm):
        self.site_frames[pop_nm] = OrderedDict()
        self.coordinate_frames[pop_nm] = OrderedDict()
        self.coordinate_vars[pop_nm] = OrderedDict()
        self.coordinate_fix_vars[pop_nm] = OrderedDict()
        self.ff_vars[pop_nm] = OrderedDict()
        self.site_param_frames[pop_nm] = OrderedDict()
        self.site_param_vars[pop_nm] = OrderedDict()
        self.site_param_fix_vars[pop_nm] = OrderedDict()
        self.site_param_bound_vars[pop_nm] = OrderedDict()
        self.site_param_constraint_vars[pop_nm] = OrderedDict()
        self.site_setting_frames[pop_nm] = OrderedDict()
        self.site_setting_vars[pop_nm] = OrderedDict()
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        basisl = Label(pf,text='--------- BASIS ---------')
        basisl.grid(row=4+nstgs+npars,column=0,columnspan=3)
        for site_nm in popd['basis'].keys():
            self.create_site_frame(pop_nm,site_nm)
        self.create_new_site_frame(pop_nm)

    def create_site_frame(self,pop_nm,site_nm):
        popd = self.populations[pop_nm]
        pf = self.pop_frames[pop_nm]
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        site_row = len(self.site_frames[pop_nm])
        sitef = Frame(pf,bd=2,pady=4,padx=10,relief=tkinter.GROOVE)
        self.site_frames[pop_nm][site_nm] = sitef
        self.site_setting_frames[pop_nm][site_nm] = OrderedDict() 
        self.site_setting_vars[pop_nm][site_nm] = OrderedDict()
        self.site_param_frames[pop_nm][site_nm] = OrderedDict() 
        self.site_param_vars[pop_nm][site_nm] = OrderedDict()
        self.site_param_fix_vars[pop_nm][site_nm] = OrderedDict()
        self.site_param_bound_vars[pop_nm][site_nm] = OrderedDict()
        self.site_param_constraint_vars[pop_nm][site_nm] = OrderedDict()

        stl = Label(sitef,text='site name:',anchor='e')
        stl.grid(row=0,column=0,sticky=tkinter.E)
        stnml = Label(sitef,text=site_nm,anchor='w')
        stnml.grid(row=0,column=1,sticky=tkinter.W+tkinter.E)
        rmb = Button(sitef,text='Remove',command=partial(self.remove_site,pop_nm,site_nm))
        rmb.grid(row=0,column=2,sticky=tkinter.E+tkinter.W)

        ffl = Label(sitef,text='form:',width=12,anchor='e')
        ffl.grid(row=1,column=0,sticky=tkinter.E)
        ffvar = StringVar(sitef)
        ff_option_dict = OrderedDict.fromkeys(xrsdkit.form_factor_names)
        ffcb = OptionMenu(sitef,ffvar,*ff_option_dict)
        ffvar.set(popd['basis'][site_nm]['form'])
        ffvar.trace('w',partial(self.update_form_factor,pop_nm,site_nm))
        ffcb.grid(row=1,column=1,columnspan=2,sticky=tkinter.E+tkinter.W)
        self.ff_vars[pop_nm][site_nm] = ffvar

        self.create_coordinate_widgets(pop_nm,site_nm)
        self.create_site_setting_widgets(pop_nm,site_nm)
        self.create_site_param_widgets(pop_nm,site_nm)
        sitef.grid(row=5+npars+nstgs+site_row,column=0,columnspan=3,sticky=tkinter.E+tkinter.W)
        if pop_nm in self.new_site_frames:
            if self.new_site_frames[pop_nm] is not None:
                self.repack_new_site_frame(pop_nm)

    def create_coordinate_widgets(self,pop_nm,site_nm):
        popd = self.populations[pop_nm]
        sitef = self.site_frames[pop_nm][site_nm]   
        if popd['structure'] in xrsdkit.crystalline_structure_names:
            coordf = Frame(sitef,bd=0,pady=0,padx=0)
            cvarx = DoubleVar(coordf)
            cvary = DoubleVar(coordf)
            cvarz = DoubleVar(coordf)
            cfixvarx = BooleanVar(coordf)
            cfixvary = BooleanVar(coordf)
            cfixvarz = BooleanVar(coordf)
            self.coordinate_frames[pop_nm][site_nm] = coordf 
            self.coordinate_vars[pop_nm][site_nm] = [cvarx,cvary,cvarz]
            self.coordinate_fix_vars[pop_nm][site_nm] = [cfixvarx,cfixvary,cfixvarz]
            coordl = Label(coordf,text='coordinates:',width=12,anchor='e')
            coordfixl = Label(coordf,text='fixed:',width=12,anchor='e')
            coorde1 = self.connected_entry(coordf,cvarx,partial(self.update_coord,pop_nm,site_nm,0,True),6)
            coorde2 = self.connected_entry(coordf,cvary,partial(self.update_coord,pop_nm,site_nm,1,True),6)
            coorde3 = self.connected_entry(coordf,cvarz,partial(self.update_coord,pop_nm,site_nm,2,True),6)
            coordcb1 = self.connected_checkbutton(coordf,cfixvarx,
                partial(self.update_fixed_coord,pop_nm,site_nm,0),'x')
            coordcb2 = self.connected_checkbutton(coordf,cfixvary,
                partial(self.update_fixed_coord,pop_nm,site_nm,1),'y')
            coordcb3 = self.connected_checkbutton(coordf,cfixvarz,
                partial(self.update_fixed_coord,pop_nm,site_nm,2),'z')
            coordf.grid(row=2,column=0,columnspan=3)
            coordl.grid(row=0,column=0,sticky=tkinter.E)
            coorde1.grid(row=0,column=1)
            coorde2.grid(row=0,column=2)
            coorde3.grid(row=0,column=3)
            coordfixl.grid(row=1,column=0,sticky=tkinter.E)
            coordcb1.grid(row=1,column=1)
            coordcb2.grid(row=1,column=2)
            coordcb3.grid(row=1,column=3)
            cdef = xrsdkit.param_defaults['coordinates']
            c = [float(cdef),float(cdef),float(cdef)]
            if 'coordinates' in popd['basis'][site_nm]:
                c = popd['basis'][site_nm]['coordinates']
            cfxdef = xrsdkit.fixed_param_defaults['coordinates']
            cfx = [bool(cfxdef),bool(cfxdef),bool(cfxdef)]
            if xrsdkit.contains_coordinates(self.fixed_params,pop_nm,site_nm):
                cfx = self.fixed_params[pop_nm]['basis'][site_nm]['coordinates'] 
            cvarx.set(c[0])
            cvary.set(c[1])
            cvarz.set(c[2])
            cfixvarx.set(cfx[0])
            cfixvary.set(cfx[1])
            cfixvarz.set(cfx[2])
            # (low priority) TODO: controls for bounding,constraining coords
        else:
            self.coordinate_frames[pop_nm][site_nm] = None 
            self.coordinate_vars[pop_nm][site_nm] = [None,None,None]
            self.coordinate_fix_vars[pop_nm][site_nm] = [None,None,None]

    def create_new_site_frame(self,pop_nm):
        pf = self.pop_frames[pop_nm]
        popd = self.populations[pop_nm]
        nsts = len(popd['basis'])
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        nsf = Frame(pf,bd=2,pady=10,padx=10,relief=tkinter.GROOVE)
        nsv = StringVar(pf)
        self.new_site_frames[pop_nm] = nsf
        self.new_site_vars[pop_nm] = nsv
        addl = Label(nsf,text='add site:',anchor='e')
        addl.grid(row=0,column=0,sticky=tkinter.E)
        nsv.set(self.default_new_site_name(pop_nm))
        stnme = self.connected_entry(nsf,nsv,None)
        stnme.grid(row=0,column=1,sticky=tkinter.W)
        stnme.bind('<Return>',partial(self.new_site,pop_nm))
        addb = Button(nsf,text='Add',width=10,command=partial(self.new_site,pop_nm))
        addb.grid(row=0,column=2)
        nsf.grid(row=5+npars+nstgs+nsts,column=0,columnspan=4)

    def repack_new_site_frame(self,pop_nm):
        popd = self.populations[pop_nm]
        nsts = len(popd['basis'])
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        self.new_site_frames[pop_nm].pack_forget()
        self.new_site_frames[pop_nm].grid(row=5+npars+nstgs+nsts,column=0,columnspan=4)

    def create_site_setting_widgets(self,pop_nm,site_nm):
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        sitef = self.site_frames[pop_nm][site_nm]
        icrd = 0
        if popd['structure'] in xrsdkit.crystalline_structure_names:
            icrd = 1
        for istg,stg_nm in enumerate(xrsdkit.form_factor_settings[site_def['form']]):
            stgf = Frame(sitef,bd=2,padx=4,pady=4,relief=tkinter.GROOVE)

            if xrsdkit.setting_datatypes[stg_nm] is str:
                stgv = StringVar(stgf)
            elif xrsdkit.setting_datatypes[stg_nm] is int:
                stgv = IntVar(stgf)
            elif xrsdkit.setting_datatypes[stg_nm] is float:
                stgv = DoubleVar(stgf)

            self.site_setting_frames[pop_nm][site_nm][stg_nm] = stgf
            self.site_setting_vars[pop_nm][site_nm][stg_nm] = stgv
            stgf.grid(row=1+icrd+istg,column=0,columnspan=3,sticky=tkinter.E+tkinter.W)
            stgl = Label(stgf,text='{}:'.format(stg_nm),width=10,anchor='e')
            stgl.grid(row=0,column=0,sticky=tkinter.E)
            stg_val = xrsdkit.setting_defaults[stg_nm]
            if stg_nm in site_def['settings']: stg_val = site_def['settings'][stg_nm]
            stgv.set(stg_val)
            stge = self.connected_entry(stgf,stgv,partial(self.update_site_setting,pop_nm,site_nm,stg_nm,True))
            stge.grid(row=0,column=1,sticky=tkinter.E+tkinter.W)

    def create_site_param_widgets(self,pop_nm,site_nm):
        popd = self.populations[pop_nm]
        site_def = popd['basis'][site_nm]
        sitef = self.site_frames[pop_nm][site_nm]
        nstgs = len(xrsdkit.form_factor_settings[site_def['form']])
        icrd = 0
        if popd['structure'] in xrsdkit.crystalline_structure_names:
            icrd = 1
        for isp,param_nm in enumerate(xrsdkit.form_factor_params[site_def['form']]):
            sparf = Frame(sitef,bd=2,padx=4,pady=4,relief=tkinter.GROOVE)
            spvar = DoubleVar(sparf)
            self.site_param_frames[pop_nm][site_nm][param_nm] = sparf
            self.site_param_vars[pop_nm][site_nm][param_nm] = spvar
            sparf.grid(row=2+nstgs+icrd+isp,column=0,columnspan=3,sticky=tkinter.E+tkinter.W)
            sparl = Label(sparf,text='{}:'.format(param_nm),width=10,anchor='e')
            sparl.grid(row=0,column=0,sticky=tkinter.E)
            param_val = xrsdkit.param_defaults[param_nm]
            if param_nm in site_def['parameters']: param_val = site_def['parameters'][param_nm]
            spvar.set(param_val)
            spare = self.connected_entry(sparf,spvar,partial(self.update_site_param,pop_nm,site_nm,param_nm,True))
            spare.grid(row=0,column=1,columnspan=2,sticky=tkinter.E+tkinter.W)
            sparsw = Checkbutton(sparf,text="fixed")
            sparsw.grid(row=0,column=3,sticky=tkinter.W)

            sparfxvar = BooleanVar(sitef)
            sparfx = xrsdkit.fixed_param_defaults[param_nm]
            if xrsdkit.contains_site_param(self.fixed_params,pop_nm,site_nm,param_nm):
                sparfx = self.fixed_params[pop_nm]['basis'][site_nm]['parameters'][param_nm]
            sparfxvar.set(sparfx)
            self.site_param_fix_vars[pop_nm][site_nm][param_nm] = sparfxvar
            sparsw = self.connected_checkbutton(sparf,sparfxvar,
                partial(self.update_fixed_site_param,pop_nm,site_nm,param_nm),'fixed')
            sparsw.grid(row=0,column=3,sticky=tkinter.W)

            lbv = DoubleVar(sitef)
            ubv = DoubleVar(sitef)
            bndl = Label(sparf,text='bounds:',width=10,anchor='e')
            bndl.grid(row=1,column=0,sticky=tkinter.E)
            lbnd = xrsdkit.param_bound_defaults[param_nm][0]
            ubnd = xrsdkit.param_bound_defaults[param_nm][1]
            if xrsdkit.contains_site_param(self.param_bounds,pop_nm,site_nm,param_nm):
                lbnd = self.param_bounds[pop_nm]['basis'][site_nm]['parameters'][param_nm][0]
                ubnd = self.param_bounds[pop_nm]['basis'][site_nm]['parameters'][param_nm][1]
            if lbnd is None: lbnd = float('inf')
            if ubnd is None: ubnd = float('inf')
            lbv.set(lbnd)
            ubv.set(ubnd)
            self.site_param_bound_vars[pop_nm][site_nm][param_nm] = [lbv,ubv]
            sparbnde1 = self.connected_entry(sparf,lbv,partial(self.update_site_param_bound,pop_nm,site_nm,param_nm,0),8)
            sparbnde2 = self.connected_entry(sparf,ubv,partial(self.update_site_param_bound,pop_nm,site_nm,param_nm,1),8)
            sparbnde1.grid(row=1,column=1,sticky=tkinter.W)
            sparbnde2.grid(row=1,column=2,sticky=tkinter.W)
            
            spexpl = Label(sparf,text='expression:',width=10,anchor='e')
            spexpl.grid(row=2,column=0,sticky=tkinter.E)
            expr = StringVar(sparf)
            expr.set("")
            if xrsdkit.contains_site_param(self.param_constraints,pop_nm,site_nm,param_nm):
                expr.set(self.param_constraints[pop_nm]['basis'][site_nm]['parameters'][param_nm])
            self.site_param_constraint_vars[pop_nm][site_nm][param_nm] = expr
            
            sparexpe = self.connected_entry(sparf,expr,partial(self.update_site_param_constraints,pop_nm,site_nm,param_nm))
            sparexpe.grid(row=2,column=1,columnspan=3,sticky=tkinter.E+tkinter.W)

    def new_population(self,event=None):
        new_nm = self.new_pop_var.get()
        if not new_nm in self.populations:
            self.populations[new_nm] = xrsdkit.unidentified_population()
            self.create_pop_frame(new_nm)
            self.repack_entry_widgets()
        self.new_pop_var.set(self.default_new_pop_name())

    def new_site(self,pop_nm,event=None):
        site_nm = self.new_site_vars[pop_nm].get()
        if site_nm in self.populations[pop_nm]['basis']:
            self.new_site_vars[pop_nm].set(self.default_new_site_name(pop_nm))
        else:
            self.make_new_site(pop_nm,site_nm,'flat')
            self.create_site_frame(pop_nm,site_nm)
            self.new_site_vars[pop_nm].set(self.default_new_site_name(pop_nm))
            self.draw_plots()
            self.repack_new_site_frame(pop_nm) 

    def make_new_site(self,pop_nm,site_name,ff_name):
        pd,fp,pb,pc = xrsdkit.new_site(self.populations,pop_nm,site_name,ff_name)
        xrsdkit.update_populations(self.populations,pd)
        if any(fp):
            xrsdkit.update_populations(self.fixed_params,fp)
        if any(pb):
            xrsdkit.update_populations(self.param_bounds,pb)
        if any(pc):
            xrsdkit.update_populations(self.param_constraints,pc)

    def remove_population(self,pop_nm):
        self.destroy_pop_frame(pop_nm)
        self.populations.pop(pop_nm)
        if pop_nm in self.fixed_params:
            self.fixed_params.pop(pop_nm)
        if pop_nm in self.param_bounds:
            self.param_bounds.pop(pop_nm)
        if pop_nm in self.param_constraints:
            self.param_constraints.pop(pop_nm)
        self.draw_plots()
        self.repack_entry_widgets()

    def remove_site(self,pop_nm,site_nm):
        self.destroy_site_frame(pop_nm,site_nm)
        self.populations[pop_nm]['basis'].pop(site_nm)
        self.draw_plots()
        self.repack_basis_widgets(pop_nm)

    def update_all_population_values(self,new_pops):
        # assume the structure and settings of new_pops
        # will be the same as self.populations.
        for pop_nm,popd in new_pops.items():
            self.update_population_values(pop_nm,popd)
        #self.populations = new_pops
        
    def update_population_values(self,pop_nm,pop_dict):
        for param_nm, param_val in pop_dict['parameters'].items():
            self.update_param_value(pop_nm,param_nm,param_val)
        for site_nm, site_def in pop_dict['basis'].items():
            self.update_site_values(pop_nm,site_nm,site_def)

    def update_param_value(self,pop_nm,param_nm,param_val):
        self.populations[pop_nm]['parameters'][param_nm] = param_val
        self.param_vars[pop_nm][param_nm].set(param_val)

    def update_site_values(self,pop_nm,site_nm,site_def):
        if 'coordinates' in site_def:
            self.update_coordinate_values(pop_nm,site_nm,site_def['coordinates'])
        if 'parameters' in site_def:
            self.update_site_param_values(pop_nm,site_nm,site_def['parameters'])

    def update_coordinate_values(self,pop_nm,site_nm,coords):
        c = self.populations[pop_nm]['basis'][site_nm]['coordinates']
        cvars = self.coordinate_vars[pop_nm][site_nm]
        for ic,cval in enumerate(coords):
            c[ic] = cval
            cvars[ic].set(cval)

    def update_site_param_values(self,pop_nm,site_nm,site_params):
        sp = self.populations[pop_nm]['basis'][site_nm]['parameters']
        param_vars = self.site_param_vars[pop_nm][site_nm]
        for param_nm,param_val in site_params.items():
            sp[param_nm] = param_val
            param_vars[param_nm].set(param_val)

    def update_structure(self,pop_nm,var_nm,dummy,mode):
        # updates self.populations to the structure in self.structure_vars
        s = self.structure_vars[pop_nm].get()
        if not s == self.populations[pop_nm]['structure']:
            self.populations[pop_nm]['structure'] = s
            # get default params for the new structure
            new_params = OrderedDict.fromkeys(xrsdkit.structure_params[s])
            for pnm in new_params: new_params[pnm] = xrsdkit.param_defaults[pnm]
            self.populations[pop_nm]['parameters'] = new_params
            # get default settings for the new structure
            new_settings = OrderedDict.fromkeys(xrsdkit.structure_settings[s])
            for snm in new_settings: new_settings[snm] = xrsdkit.setting_defaults[snm]
            self.populations[pop_nm]['settings'] = new_settings

            new_basis = self.populations[pop_nm]['basis']
            site_nms = list(new_basis.keys())
            for site_nm in site_nms:
                if s in xrsdkit.crystalline_structure_names:
                    if new_basis[site_nm]['form'] in xrsdkit.noncrystalline_ff_names:
                        new_basis.pop(site_nm)
                    elif not 'coordinates' in new_basis[site_nm]:
                        new_basis[site_nm]['coordinates'] = [0.,0.,0.]
                else:
                    if 'coordinates' in new_basis[site_nm]:
                        new_basis[site_nm].pop('coordinates')

            self.destroy_setting_frames(pop_nm)
            self.destroy_param_frames(pop_nm)
            self.destroy_site_frames(pop_nm)
            self.create_setting_frames(pop_nm)
            self.create_param_frames(pop_nm)
            self.create_site_frames(pop_nm)
            #self.destroy_pop_frame(pop_nm)
            #self.create_pop_frame(pop_nm)
            self.draw_plots()

    def update_form_factor(self,pop_nm,site_nm,var_nm,dummy,mode):
        ff = self.ff_vars[pop_nm][site_nm].get()
        if not ff == self.populations[pop_nm]['basis'][site_nm]['form']:
            self.make_new_site(pop_nm,site_nm,ff)
            self.destroy_coordinate_widgets(pop_nm,site_nm)
            self.destroy_site_setting_widgets(pop_nm,site_nm)
            self.destroy_site_param_widgets(pop_nm,site_nm)
            self.create_coordinate_widgets(pop_nm,site_nm)
            self.create_site_setting_widgets(pop_nm,site_nm)
            self.create_site_param_widgets(pop_nm,site_nm)
            self.draw_plots()

    def validate_and_update(self,parent,item_key,old_val,tkvar,draw_plots=False):
        """Validate a Var entry and set its value in a parent data structure

        If the entry is valid, the value is set in `parent` at `item_key`.
        If the entry is not valid, the `tkvar` is reset to `old_val`.
        
        Parameters
        ----------
        parent : object
            A data structure
        item_key : object
            A key for addressing an item in the `parent`
        old_val : object
            A value to fall back on if the Var fails to get()
        tkvar : tk.Variable
            The tkinter Variable to get() the new value from

        Returns
        -------
        is_valid : boolean
            Flag for whether or not the entry was found to be valid
        """
        is_valid = True
        try:
            new_val = tkvar.get()
        except:
            is_valid = False
        if is_valid:
            if not new_val == old_val: 
                parent[item_key] = new_val 
                if draw_plots:
                    self.draw_plots()
        else:
            tkvar.set(old_val)
        return is_valid

    def update_setting(self,pop_nm,stg_nm,draw_plots=False,event=None):
        stgs = self.populations[pop_nm]['settings']
        s_old = stgs[stg_nm]
        s_var = self.setting_vars[pop_nm][stg_nm]
        return self.validate_and_update(stgs,stg_nm,s_old,s_var,draw_plots)

    def update_param(self,pop_nm,param_nm,draw_plots=False,event=None):
        params = self.populations[pop_nm]['parameters']
        p_old = params[param_nm]
        p_var = self.param_vars[pop_nm][param_nm]
        return self.validate_and_update(params,param_nm,p_old,p_var,draw_plots)

    def update_param_bound(self,pop_nm,param_nm,bound_idx,draw_plots=False,event=None):
        bounds = copy.deepcopy(xrsdkit.param_bound_defaults[param_nm])
        if xrsdkit.contains_param(self.param_bounds,pop_nm,param_nm):
            bounds = self.param_bounds[pop_nm]['parameters'][param_nm]
        b_old = bounds[bound_idx]
        b_var = self.param_bound_vars[pop_nm][param_nm][bound_idx]
        is_valid = self.validate_and_update(bounds,bound_idx,b_old,b_var,False)
        if is_valid:
            xrsdkit.update_param(self.param_bounds,pop_nm,param_nm,bounds)
            # TODO: check the value of the param- if it is outside the bounds, update it and draw_plots.
        return is_valid

    def update_fixed_site_param(self,pop_nm,site_nm,param_nm,event=None):
        fp = {} 
        fx_old = bool(xrsdkit.fixed_param_defaults[param_nm])
        if xrsdkit.contains_site_param(self.fixed_params,pop_nm,site_nm,param_nm):
            fp = self.fixed_params[pop_nm]['basis'][site_nm]['parameters']
            fx_old = fp[param_nm]
        fx_var = self.site_param_fix_vars[pop_nm][site_nm][param_nm]
        is_valid = self.validate_and_update(fp,param_nm,fx_old,fx_var,False)
        if is_valid:
            xrsdkit.update_site_param(self.fixed_params,pop_nm,site_nm,param_nm,fp[param_nm])
        return is_valid

    def update_fixed_param(self,pop_nm,param_nm,event=None):
        fp = {} 
        fx_old = bool(xrsdkit.fixed_param_defaults[param_nm])
        if xrsdkit.contains_param(self.fixed_params,pop_nm,param_nm):
            fp = self.fixed_params[pop_nm]['parameters']
            fx_old = fp[param_nm]
        fx_var = self.param_fix_vars[pop_nm][param_nm]
        is_valid = self.validate_and_update(fp,param_nm,fx_old,fx_var,False)
        if is_valid:
            xrsdkit.update_param(self.fixed_params,pop_nm,param_nm,fp[param_nm])
        return is_valid

    def update_param_constraints(self,pop_nm,param_nm,draw_plots=False,event=None):
        pc = {}
        pc_old = None
        if xrsdkit.contains_param(self.param_constraints,pop_nm,param_nm):
            pc = self.param_constraints[pop_nm]['parameters']
            pc_old = pc[param_nm]
        pc_var = self.param_constraint_vars[pop_nm][param_nm]
        is_valid = self.validate_and_update(pc,param_nm,pc_old,pc_var,False)
        # TODO (low priority): any additional validation of the constraint expression?
        if is_valid:
            xrsdkit.update_param(self.param_constraints,pop_nm,param_nm,pc[param_nm])
            # TODO: check the value of the param- if violates the constraint, update it and draw_plots.
        return is_valid

    def update_coord(self,pop_nm,site_nm,coord_idx,draw_plots=False,event=None):
        coords = self.populations[pop_nm]['basis'][site_nm]['coordinates']
        c_old = coords[coord_idx]
        c_var = self.coordinate_vars[pop_nm][site_nm][coord_idx]
        return self.validate_and_update(coords,coord_idx,c_old,c_var,draw_plots)

    def update_fixed_coord(self,pop_nm,site_nm,coord_idx,event=None):
        fcdef = bool(xrsdkit.fixed_param_defaults['coordinates'])
        fc = [bool(fcdef),bool(fcdef),bool(fcdef)] 
        if xrsdkit.contains_coordinates(self.fixed_params,pop_nm,site_nm):
            fc = self.fixed_params[pop_nm]['basis'][site_nm]['coordinates']
        fc_old = fc[coord_idx]
        fc_var = self.coordinate_fix_vars[pop_nm][site_nm][coord_idx]
        is_valid = self.validate_and_update(fc,coord_idx,fc_old,fc_var,False)
        if is_valid:
            xrsdkit.update_coordinates(self.fixed_params,pop_nm,site_nm,fc)
        return is_valid

    def update_site_param(self,pop_nm,site_nm,param_nm,draw_plots=False,event=None):
        site_def = self.populations[pop_nm]['basis'][site_nm]
        sp_old = site_def['parameters'][param_nm]
        sp_var = self.site_param_vars[pop_nm][site_nm][param_nm]
        return self.validate_and_update(site_def['parameters'],param_nm,sp_old,sp_var,draw_plots)

    def update_site_setting(self,pop_nm,site_nm,setting_nm,draw_plots=False,event=None):
        site_def = self.populations[pop_nm]['basis'][site_nm]
        s_old = site_def['settings'][setting_nm]
        s_var = self.site_setting_vars[pop_nm][site_nm][setting_nm]
        return self.validate_and_update(site_def['settings'],setting_nm,s_old,s_var,draw_plots)

    def update_site_param_bound(self,pop_nm,site_nm,param_nm,bound_idx,draw_plots=False,event=None):
        bounds = copy.deepcopy(xrsdkit.param_bound_defaults[param_nm])
        if xrsdkit.contains_site_param(self.param_bounds,pop_nm,site_nm,param_nm):
            bounds = self.param_bounds[pop_nm]['basis'][site_nm]['parameters'][param_nm]
        b_old = bounds[bound_idx]
        b_var = self.site_param_bound_vars[pop_nm][site_nm][param_nm][bound_idx]
        is_valid = self.validate_and_update(bounds,bound_idx,b_old,b_var,False)
        if is_valid:
            xrsdkit.update_site_param(self.param_bounds,pop_nm,site_nm,param_nm,bounds)
            # TODO: check the value of the param- if it is outside the bounds, update it and draw_plots.
        return is_valid

    def update_site_param_constraints(self,pop_nm,site_nm,param_nm,draw_plots=False,event=None):
        pc = {}
        pc_old = None
        if xrsdkit.contains_site_param(self.param_constraints,pop_nm,site_nm,param_nm):
            pc = self.param_constraints[pop_nm]['basis'][site_nm]['parameters']
            pc_old = pc[param_nm]
        pc_var = self.site_param_constraint_vars[pop_nm][site_nm][param_nm]
        is_valid = self.validate_and_update(pc,param_nm,pc_old,pc_var,False)
        # TODO: any additional validation of the constraint expression?
        if is_valid:
            xrsdkit.update_site_param(self.param_constraints,pop_nm,site_nm,param_nm,pc[param_nm])
            # TODO: check the value of the param- if violates constraints, update it and draw_plots.
        return is_valid

    def fit(self):
        ftr = xrsdkit.fitting.xrsd_fitter.XRSDFitter(self.q_I,self.populations,self.src_wl)
        logIwtd = bool(self.logI_weighted_var.get())
        erwtd = bool(self.error_weighted_var.get())
        q_lo = self.q_range_vars[0].get()
        q_hi = self.q_range_vars[1].get()
        lmf_params = ftr.pack_lmfit_params(self.populations,self.fixed_params,self.param_bounds,self.param_constraints)
        #if self.message_callback:
        #    self.message_callback(lmf_params.pretty_print())
        if self.message_callback:
            print('fitting...')
        p_opt,rpt = ftr.fit(self.fixed_params,self.param_bounds,self.param_constraints,erwtd,logIwtd,[q_lo,q_hi])
        self.q_I_opt = xrsdkit.scattering.compute_intensity(self.q_I[:,0],self.populations,self.src_wl)
        self.fit_report = rpt
        if self.message_callback:
            self.message_callback(ftr.print_report(self.populations,p_opt,rpt))
        self.fit_obj_var.set(rpt['final_objective'])
        self.update_all_population_values(p_opt)
        self.draw_plots()

    def compute_objective(self):
        ftr = xrsdkit.fitting.xrsd_fitter.XRSDFitter(self.q_I,self.populations,self.src_wl)
        erwtd = bool(self.error_weighted_var.get())
        logIwtd = bool(self.logI_weighted_var.get())
        return ftr.evaluate_residual(self.populations,erwtd,logIwtd,self.q_range)

    def repack_new_pop_frame(self):
        self.new_pop_frame.pack_forget()
        self.new_pop_frame.pack(side=tkinter.TOP,pady=2,padx=2, fill="both", expand=True)

    def repack_control_frame(self):
        self.control_frame.pack_forget()
        self.control_frame.pack(side=tkinter.TOP, pady=2,padx=2, fill="both", expand=True)

    def create_new_pop_frame(self):
        npf = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        self.new_pop_frame = npf
        npf.pack(side=tkinter.TOP,pady=2,padx=2, fill="both", expand=True)
        addl = Label(npf,text='add population:',anchor='e')
        addl.grid(row=0,column=0,sticky=tkinter.E)
        self.new_pop_var = StringVar(self.pops_frame)
        nme = self.connected_entry(npf,self.new_pop_var,None)
        nme.grid(row=0,column=1,sticky=tkinter.W)
        nme.bind('<Return>',self.new_population)
        addb = Button(npf,text='Add',width=10,command=self.new_population)
        addb.grid(row=0,column=2)

    def default_new_pop_name(self):
        ipop = 0
        nm = 'pop_'+str(ipop)
        while nm in self.populations:
            ipop += 1
            nm = 'pop_'+str(ipop)
        return nm

    def default_new_site_name(self,pop_nm):
        ist = 0
        nm = 'site_'+str(ist)
        while nm in self.populations[pop_nm]['basis']:
            ist += 1
            nm = 'site_'+str(ist)
        return nm

    def create_control_frame(self):
        cf = Frame(self.pops_frame,bd=4,pady=10,padx=10,relief=tkinter.RAISED)
        self.control_frame = cf
        self.fit_obj_var = StringVar(cf)
        self.error_weighted_var = BooleanVar(cf)
        self.logI_weighted_var = BooleanVar(cf)
        objl = Label(cf,text='objective:',anchor='e')
        objl.grid(row=0,column=0,rowspan=2,sticky=tkinter.E)
        rese = Entry(cf,width=20,state='readonly',textvariable=self.fit_obj_var)
        rese.grid(row=0,column=1,rowspan=2,columnspan=2,sticky=tkinter.W)
        self.update_fit_objective()
        self.error_weighted_var = BooleanVar(cf)
        ewtcb = Checkbutton(cf,text="error weighted",variable=self.error_weighted_var)
        ewtcb.select()
        ewtcb.grid(row=0,column=3,sticky=tkinter.W)
        self.logI_weighted_var = BooleanVar(cf)
        logwtbox = Checkbutton(cf,text="log(I) weighted",variable=self.logI_weighted_var)
        logwtbox.select()
        logwtbox.grid(row=1,column=3,sticky=tkinter.W)
        q_range_lbl = Label(cf,text='q-range:',anchor='e')
        q_range_lbl.grid(row=2,column=0)
        self.q_range_vars = [DoubleVar(cf),DoubleVar(cf)]
        q_lo_ent = Entry(cf,width=8,textvariable=self.q_range_vars[0])
        q_hi_ent = Entry(cf,width=8,textvariable=self.q_range_vars[1])
        q_lo_ent.grid(row=2,column=1)
        q_hi_ent.grid(row=2,column=2)
        self.q_range_vars[0].set(self.q_range[0])
        self.q_range_vars[1].set(self.q_range[1])
        fitbtn = Button(cf,text='Fit',width=10,command=self.fit)
        fitbtn.grid(row=3,column=0)
        finbtn = Button(cf,text='Finish',width=10,command=self.close_gui)
        finbtn.grid(row=3,column=1,columnspan=2)
        self.good_fit_var = tkinter.BooleanVar(cf)
        fitcb = Checkbutton(cf,text="Good fit", variable=self.good_fit_var)
        fitcb.grid(row=3,column=3,sticky=tkinter.W)
        self.good_fit_var.set(self.good_fit_prior)
        cf.pack(side=tkinter.TOP,pady=2,padx=2,fill="both",expand=True)

    def update_fit_objective(self):
        self.fit_obj_var.set(str(self.compute_objective()))

    def repack_entry_widgets(self):
        for pop_nm,pf in self.pop_frames.items():
            pf = self.pop_frames[pop_nm]
            pf.pack_forget()
            pf.pack(side=tkinter.TOP,pady=2,padx=2)
            self.repack_basis_widgets(pop_nm)
        self.repack_new_pop_frame()
        self.repack_control_frame()

    def repack_basis_widgets(self,pop_nm):
        popd = self.populations[pop_nm]
        npars = len(xrsdkit.structure_params[popd['structure']])
        nstgs = len(xrsdkit.structure_settings[popd['structure']])
        for ist,site_nm in enumerate(popd['basis'].keys()):
            sitef = self.site_frames[pop_nm][site_nm]
            sitef.pack_forget()
            sitef.grid(row=5+npars+nstgs+ist,column=0,columnspan=4,sticky=tkinter.E+tkinter.W)

    #def destroy_entry_widgets(self):
    #    pop_nm_list = list(self.pop_frames.keys())
    #    for pop_nm in pop_nm_list:
    #        self.destroy_pop_frame(pop_nm)
    #        self.structure_vars.pop(pop_nm)
    #    self.repack_new_pop_frame()
    #    self.repack_control_frame()

    def destroy_pop_frame(self,pop_nm):
        self.destroy_setting_frames(pop_nm)
        self.destroy_param_frames(pop_nm)
        self.destroy_site_frames(pop_nm)
        popfrm = self.pop_frames.pop(pop_nm)
        popfrm.pack_forget()
        popfrm.destroy()

    def destroy_setting_frames(self,pop_nm):
        for setting_nm in list(self.setting_frames[pop_nm].keys()):
            self.setting_vars[pop_nm].pop(setting_nm)
            setting_frm = self.setting_frames[pop_nm].pop(setting_nm)
            setting_frm.pack_forget()
            setting_frm.destroy()

    def destroy_param_frames(self,pop_nm):
        param_nm_list = list(self.param_frames[pop_nm].keys())
        for param_nm in param_nm_list:
            self.param_vars[pop_nm].pop(param_nm)
            self.param_fix_vars[pop_nm].pop(param_nm) 
            self.param_bound_vars[pop_nm].pop(param_nm)  
            self.param_constraint_vars[pop_nm].pop(param_nm)  
            param_frm = self.param_frames[pop_nm].pop(param_nm)
            param_frm.pack_forget()
            param_frm.destroy()

    def destroy_site_frames(self,pop_nm):
        site_nm_list = list(self.site_frames[pop_nm].keys())
        for site_nm in site_nm_list:
            self.destroy_coordinate_widgets(pop_nm,site_nm)
            self.destroy_site_setting_widgets(pop_nm,site_nm)
            self.destroy_site_param_widgets(pop_nm,site_nm)
            self.destroy_site_frame(pop_nm,site_nm)
        self.destroy_new_site_frame(pop_nm)

    def destroy_coordinate_widgets(self,pop_nm,site_nm):
        if self.coordinate_frames[pop_nm][site_nm] is not None:
            self.coordinate_vars[pop_nm].pop(site_nm)
            self.coordinate_fix_vars[pop_nm].pop(site_nm)
            coord_frm = self.coordinate_frames[pop_nm].pop(site_nm)
            coord_frm.pack_forget()
            coord_frm.destroy()

    def destroy_site_setting_widgets(self,pop_nm,site_nm):
        for setting_nm in list(self.site_setting_frames[pop_nm][site_nm].keys()):
            self.site_setting_vars[pop_nm][site_nm].pop(setting_nm)
            setting_frm = self.site_setting_frames[pop_nm][site_nm].pop(setting_nm)
            setting_frm.pack_forget()
            setting_frm.destroy()

    def destroy_site_param_widgets(self,pop_nm,site_nm):
        for param_nm in list(self.site_param_frames[pop_nm][site_nm].keys()):
            self.site_param_vars[pop_nm][site_nm].pop(param_nm)
            self.site_param_fix_vars[pop_nm][site_nm].pop(param_nm)
            self.site_param_bound_vars[pop_nm][site_nm].pop(param_nm)
            self.site_param_constraint_vars[pop_nm][site_nm].pop(param_nm)
            param_frm = self.site_param_frames[pop_nm][site_nm].pop(param_nm)
            param_frm.pack_forget()
            param_frm.destroy()

    def destroy_site_frame(self,pop_nm,site_nm):
        site_frm = self.site_frames[pop_nm].pop(site_nm)
        site_frm.pack_forget()
        site_frm.destroy()

    def destroy_new_site_frame(self,pop_nm):
        site_frm = self.new_site_frames.pop(pop_nm)
        site_frm.pack_forget()
        site_frm.destroy()


