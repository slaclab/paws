import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from ..PROCESSING.SAXS.NANOPARTICLES import SphericalNormalHeuristics

#r0_vals = np.arange(10,41,10,dtype=float)              #Angstrom
r0_vals = np.array([10])

sigma_over_r = []
width_metric = []
intensity_metric = []
qr0_focus = []

for ir,r0 in zip(range(len(r0_vals)),r0_vals):

    # q range on which the heuristics will be generated
    q = np.arange(0.001/r0,float(10)/r0,0.001/r0)       #1/Angstrom
    sigma_r_vals = np.arange(0*r0,0.21*r0,0.01*r0)      #Angstrom

    for isig,sigma_r in zip(range(len(sigma_r_vals)),sigma_r_vals):

        I = SphericalNormalHeuristics.SphericalNormalHeuristics.compute_saxs(q,r0,sigma_r) 
        d = SphericalNormalHeuristics.SphericalNormalHeuristics.saxs_heuristics(q,I)

        sigma_over_r.append(float(sigma_r)/r0)
        qr0_focus.append(d['q_at_Iqqqq_min1']*r0)
        width_metric.append(d['pI_qwidth']/d['q_at_Iqqqq_min1'])
        intensity_metric.append(d['I_at_Iqqqq_min1']/d['I_at_0'])

# TODO: standardize before fitting, then revert after
p_qr0_focus = np.polyfit(sigma_over_r,qr0_focus,2,None,False,None,False)
p_w = np.polyfit(sigma_over_r,width_metric,2,None,False,None,False)
p_I = np.polyfit(sigma_over_r,intensity_metric,3,None,False,None,False)

print 'polynomial for qr0 focus (wrt sigma_r/r0): {}x^2 + {}x + {}'.format(p_qr0_focus[0],p_qr0_focus[1],p_qr0_focus[2])
print 'polynomial for width metric (wrt sigma_r/r0): {}x^2 + {}x + {}'.format(p_w[0],p_w[1],p_w[2])
print 'polynomial for intensity metric (wrt sigma_r/r0): {}^3 + {}x^2 + {}x + {}'.format(p_I[0],p_I[1],p_I[2],p_I[3])

plot = True
if plot: 
    plt.figure(1)
    plt.scatter(sigma_over_r,width_metric)
    plt.plot(sigma_over_r,np.polyval(p_w,sigma_over_r))
    plt.figure(2)
    plt.scatter(sigma_over_r,intensity_metric)
    plt.plot(sigma_over_r,np.polyval(p_I,sigma_over_r))
    plt.figure(3)
    plt.scatter(sigma_over_r,qr0_focus)
    plt.plot(sigma_over_r,np.polyval(p_qr0_focus,sigma_over_r))
    plt.figure(4)
    plt.scatter(width_metric,intensity_metric) 
    plt.show()

