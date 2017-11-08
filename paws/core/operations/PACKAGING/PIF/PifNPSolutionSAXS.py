from collections import OrderedDict

import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation
from saxskit import saxs_fit 

inputs=OrderedDict(
    uid_prefix=None,
    t_utc=None,
    temperature=None,
    q_I=None,
    flags=None,
    params=None,
    report=None)
outputs=OrderedDict(pif=None)

class PifNPSolutionSAXS(Operation):
    """
    Package SAXS results from a nanoparticle solution into a pypif.obj.ChemicalSystem record.
    """

    def __init__(self):
        super(PifNPSolutionSAXS,self).__init__(inputs,outputs)
        self.input_doc['uid_prefix'] = 'string for pif uid prefix '\
            '(pif uid = uid_prefix+t_utc), and also the '
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding saxs intensities'
        self.input_doc['flags'] = 'dict of boolean flags indicating scatterer populations'
        self.input_doc['params'] = 'dict of scattering equation parameters fit to q_I'
        self.input_doc['report'] = 'dict reporting key results '\
            'for the SAXS processing workflow, including fitting objectives, etc.'
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_type['t_utc'] = opmod.workflow_item
        self.input_type['temperature'] = opmod.workflow_item
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['flags'] = opmod.workflow_item
        self.input_type['params'] = opmod.workflow_item
        self.input_type['report'] = opmod.workflow_item

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if uid_pre is not None:
            uid_full = uid_pre
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']
        f = self.inputs['flags']
        p = self.inputs['params']
        r = self.inputs['report']

        # ChemicalSystem record construction begins here
        csys = pifobj.ChemicalSystem()
        csys.uid = uid_full
        csys.properties = []
        csys.tags = []
        csys.ids = []
        if uid_pre is not None:
            csys.ids.append(self.id_tag('EXPERIMENT_ID',uid_pre))
        #if uid_pre is not None:
        #    csys.tags.append('reaction id: '+uid_pre)
        if t_utc is not None:
            csys.tags.append('time (utc): '+str(int(t_utc)))

        if q_I is not None:
            # Process measured q_I into a property
            pI = self.q_I_property(q_I)
            if temp_C is not None:
                pI.conditions.append(pifobj.Value('temperature',[pifobj.Scalar(temp_C)],None,None,None,'degrees Celsius'))
            pI.name = 'SAXS intensity' 
            csys.properties.append(pI)
            # Store featurization of measured spectrum
            prof = saxs_fit.profile_spectrum(q_I)
            for fnm,fval in prof.items():
                csys.properties.append(self.param_property(
                fnm,fval,'','spectrum profiling heuristic quantity'))

        if q_I is not None and p is not None and f is not None:
            if not f['bad_data'] and not f['diffraction_peaks']:
                I_computed = saxs_fit.compute_saxs(q_I[:,0],f,p)
                pI_computed = self.q_I_property(np.array([q_I[:,0],I_computed]).T)
                pI_computed.name = 'computed SAXS intensity'
                csys.properties.append(pI_computed)


        # TODO: include the scattering equation in this record somehow
        if f is not None:
            if f['bad_data']:
                csys.properties.append(self.param_property(
                'bad_data',1.,'probability of bad data','EXPERIMENTAL'))
            if f['diffraction_peaks']:
                csys.properties.append(self.param_property(
                'diffraction_peaks',1.,'probability of diffraction peaks','EXPERIMENTAL'))
            if f['form_factor_scattering']:
                csys.properties.append(self.param_property(
                'form_factor_scattering',1.,'probability of form factor scattering','EXPERIMENTAL'))
            if f['precursor_scattering']:
                csys.properties.append(self.param_property(
                'precursor scattering',1.,'probability of precursor scattering','EXPERIMENTAL'))

        if p is not None:
            if 'I0_floor' in p:
                csys.properties.append(self.param_property(
                'I0_floor',p['I0_floor'],
                'arb','flat background intensity','FIT'))
            if 'G_precursor' in p:
                csys.properties.append(self.param_property(
                'G_precursor',p['G_precursor'],
                'arb','precursor Guinier factor','FIT'))
            if 'rg_precursor' in p:
                csys.properties.append(self.param_property(
                'rg_precursor',p['rg_precursor'],
                'Angstrom','precursor radius of gyration','FIT'))
            if 'I0_sphere' in p:
                csys.properties.append(self.param_property(
                'I0_sphere',p['I0_sphere'],
                'arb','spherical scatterer intensity','FIT'))
            if 'r0_sphere' in p:
                csys.properties.append(self.param_property(
                'r0_sphere',p['r0_sphere'],
                'Angstrom','spherical scatterer mean radius','FIT'))
            if 'sigma_sphere' in p:
                csys.properties.append(self.param_property(
                'sigma_sphere',p['sigma_sphere'],
                '','fractional standard deviation of spherical scatterer radii','FIT'))

        if r is not None:
            for rptnm,rptval in r.items():
                if isinstance(rptval,float):
                    csys.properties.append(self.param_property(
                    rptnm,rptval,'','spectrum fitting reported quantity','FIT'))

        self.outputs['pif'] = csys

    def id_tag(self,idname,idval,tags=None):
        return pifobj.Id(idname,idval,tags)

    def param_property(self,fname,fval,funits='',desc='',data_type=''):
        pf = pifobj.Property()
        pf.name = fname
        pf.scalars = [pifobj.Scalar(fval)]
        if funits:
            pf.units = funits
        if desc:
            pf.tags = [desc]
        if data_type:
            pf.dataType = data_type 
        return pf

    def q_I_property(self,q_I,Iunits='arb',qunits='1/Angstrom'):
        pI = pifobj.Property()
        n_qpoints = q_I.shape[0]
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = Iunits 
        pI.conditions = []
        pI.conditions.append( pifobj.Value('scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,None,qunits) )
        return pI 
        
