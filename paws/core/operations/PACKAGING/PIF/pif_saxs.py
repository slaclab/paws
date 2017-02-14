import numpy as np
import pypif.obj as pifobj

from ...operation import Operation
from ... import optools

class PifNPSynth(Operation):
    """
    Package results from nanoparticle solution synthesis into a pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['name','q','I','date_time','t_utc','T']
        output_names = ['pif']
        super(PifNPSynth,self).__init__(input_names,output_names)
        self.input_doc['name'] = 'user input string used as pif record uid'
        self.input_doc['q'] = 'array of q values for saxs spectrum'
        self.input_doc['I'] = 'array of I(q) for saxs spectrum'
        self.input_doc['date_time'] = 'string date/time from measurement header file for pif record tags'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['T'] = 'temperature in degrees celsius from measurement header file'
        self.output_doc['pif'] = 'pif object containing the relevant data for this experiment'
        self.input_src['name'] = optools.text_input
        self.input_src['q'] = optools.wf_input
        self.input_src['I'] = optools.wf_input
        self.input_src['date_time'] = optools.wf_input
        self.input_src['t_utc'] = optools.wf_input
        self.input_src['T'] = optools.wf_input
        self.input_type['name'] = optools.str_type
        self.input_type['q'] = optools.ref_type
        self.input_type['I'] = optools.ref_type
        self.input_type['date_time'] = optools.ref_type
        self.input_type['t_utc'] = optools.ref_type
        self.input_type['T'] = optools.ref_type

    def run(self):
        uid_pre = self.inputs['name']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = uid_pre+'_'+str(int(t_utc))
        T_C = self.inputs['T']
        q = self.inputs['q']
        I_q = self.inputs['I']
        # Subsystems for solution ingredients
        colloid_sys = pifobj.ChemicalSystem(uid_pre+'_pd_colloid',['colloidal Pd nanoparticles'],None,None,None,'Pd') 
        acid_sys = pifobj.ChemicalSystem(uid_pre+'_oleic_acid',['oleic acid'],None,None,None,'C18H34O2') 
        amine_sys = pifobj.ChemicalSystem(uid_pre+'_oleylamine',['oleylamine'],None,None,None,'C18H35NH2') 
        TOP_sys = pifobj.ChemicalSystem(uid_pre+'_trioctylphosphine',['trioctylphosphine'],None,None,None,'P(C8H17)3')
        subsys = [colloid_sys,acid_sys,amine_sys,TOP_sys]
        # TODO: Quantity information for subsystems
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid_full
        main_sys.sub_systems = subsys
        main_sys.properties = self.saxs_to_pif_properties(q,I_q,T_C)
        main_sys.tags = ['reaction id: '+uid_pre,'date: '+t_str,'utc: '+str(int(t_utc))]
        self.outputs['pif'] = main_sys

    def saxs_to_pif_properties(self,q,I_q,T_C):
        props = []
        for i in range(len(q)):
            p = pifobj.Property()
            p.name = 'SAXS intensity'
            p.scalars = [ pifobj.Scalar(I_q[i]) ]
            p.conditions = [] 
            p.conditions.append( pifobj.Value('scattering vector',[pifobj.Scalar(q[i])],None,None,'Angstrom^-1') )
            p.conditions.append( pifobj.Value('temperature',[pifobj.Scalar(T_C)],None,None,'degrees Celsius') )
            p.units = 'counts'
            props.append(p)
        return props
        
#    def make_piftemperature(self,t):
#        v = pifobj.Value()
#        v.name = 'temperature'
#        tscl = pifobj.Scalar()
#        tscl.value = str(t)
#        v.scalars = [tscl]
#        v.units = 'degrees Celsius'
#        return v
#
#    def make_pifvector(self,v):
#        pifv = []
#        for n in v:
#            s = pifobj.Scalar()
#            s.value = str(n)
#            pifv.append(s)
#        return pifv
#
#    def pifscalar(self,scl,errlo,errhi):
#        s = pifobj.Scalar()
#        s.value = str(scl) 
#        s.minimum = str(scl) 
#        s.maximum = str(scl) 
#        s.inclusiveMinimum = True
#        s.inclusiveMaximum = True
#        s.uncertainty = '+{},-{}'.format(errlo,errhi)
#        s.approximate = True
#        return s


