"""

"""
import numpy as np

#%%
def rk4(f, v: np.ndarray, dt: float):
    """
    Implentation of Runge-Kuta 4th order for a n-array
    
    Parameters
    ----------
        f : function
            differential equations functions y'=f(y)
        v : np.ndarray [x,y,i1,i2,i3]
            array with the differential variables 
        dt : float
            rk4 time step
    
    Return
    -------
        rk4 : np.ndarray [x,y,i1,i2,i3]
            reulst approximation 
    
    Example
    -------
        >>>
    """
    k1 = f(v)    
    k2 = f(v + dt/2.0*k1)
    k3 = f(v + dt/2.0*k2)
    k4 = f(v + dt*k3)

    return v + dt*(2.0*(k2+k3)+k1+k4)/6.0