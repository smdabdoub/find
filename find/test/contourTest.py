import numpy as np
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy.ma as ma
from numpy.random import uniform
import facs


labDat = facs.loadFacsCSV('Mx_080122_mix.csv')
x = labDat[1][:,7]
y = labDat[1][:,5]
z = x*np.exp(-x**10-y**10)

npts = len(x)

# define grid.
xi = np.linspace(1e-1, 3e5)
yi = np.linspace(1e-1, 3e5)

# grid the data.
zi = griddata(x,y,z,xi,yi)

# contour the gridded data, plotting dots at the randomly spaced data points.
CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k',yscale='log',xscale='log')
CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet,yscale='log',xscale='log')
plt.colorbar() # draw colorbar

# plot data points.
#plt.plot(x,y,'.',c='b',ms=1)
plt.xlim(1e-1, 3e5)
plt.ylim(1e-1, 3e5)
plt.title('griddata test (%d points)' % npts)
plt.show()
