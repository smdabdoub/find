'''
Created on Jun 21, 2010

@author: dabdoubs
'''
import math
import matplotlib.ticker as mticker
import matplotlib.transforms as mtransforms
import numpy as np


def log(data, **kwargs):
    """
    Transforms the given data to a logarithmic scale.
    
    :@type data: ndarray
    :@param param: The data to be transformed
    
    kwargs
    ------
    :@type base: int or str
    :@param base: The logarithmic base to use when transforming the data. 
                  Acceptable values: 2, 10, and e. Any other value will 
                  default to 10.
    :@type min_clip: float
    :@param min_clip: The minimum value boundary. Values outside the boundary 
                      will be clipped to this value.
    
    """
    base = 10
    min_clip = 0.00001
    
    if 'base' in kwargs:
        try:
            base = int(kwargs['base'])
        except ValueError:
            base = kwargs['base']
    if 'min_clip' in kwargs:
        min_clip = float(kwargs['min_clip'])
    
    func = np.log10
    
    if base == 2:
        func = np.log2
    elif base == 'e':
        func = np.log1p
    
    return func(np.clip(data, a_min=min_clip, a_max=np.max(np.maximum.reduce(data))))


class LogLocator(mticker.Locator):
    """
    Determine the tick locations for previously log-transformed data.
    """
    
    def __init__(self, base=10.0, view_range=None):
        """
        
        """
        self.base(base)
        self.vrange = view_range
    
    def base(self,base):
        """
        Set the base of the log scaling (major tick every base**i, i interger)
        """
        self._base=base+0.0


    def __call__(self):
        """Return the locations of the ticks"""

        if self.vrange is not None:
            vmin, vmax = self.vrange
        else:
            vmin, vmax = self.axis.get_view_interval()
            vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander = 0.05)
            if vmax<vmin:
                vmin, vmax = vmax, vmin

        
        expmax = len(str(int(vmax)))
        expmin = len(str(int(vmin)))
        exprange = [10**i for i in range(expmin, expmax+1)]
        
        ticks = []
        for i in exprange:
            ticks.extend([log(j) for j in range(int(i*.1), i, int(i*.1))])
        

        return self.raise_if_exceeds(ticks)
    

    def view_limits(self, vmin, vmax):
        """Try to choose the view limits intelligently"""

        if vmax<vmin:
            vmin, vmax = vmax, vmin

        if vmin==vmax:
            vmin-=1
            vmax+=1

        exponent, remainder = divmod(math.log10(vmax - vmin), 1)

        if remainder < 0.5:
            exponent -= 1
        scale = 10**(-exponent)
        vmin = math.floor(scale*vmin)/scale
        vmax = math.ceil(scale*vmax)/scale

        return mtransforms.nonsingular(vmin, vmax)










