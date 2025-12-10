"""
Maht utils
"""
import numpy as np
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial
from sklearn.metrics import r2_score, mean_squared_error

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
    k2 = f(v + dt/2*k1)
    k3 = f(v + dt/2*k2)
    k4 = f(v + dt*k3)

    return v + dt*(2*(k2+k3)+k1+k4)/6

#%%
def gaussian(
            t: np.ndarray,
            a0: float,
            t0: float,
            a1: float = 0,
            sigma: float = 1,
            n: int = 1
        ) -> np.ndarray:
        """
        Computes a generalized Gaussian function.
        Parameters
        ----------
        t : np.ndarray
            Input array of time or independent variable values.
        a0 : float
            Amplitude of the Gaussian function.
        t0 : float
            Center (mean) of the Gaussian function.
        sigma : float, optional
            Standard deviation (spread or width) of the Gaussian function. Default is 1.
        n : int, optional
            Exponent controlling the shape of the Gaussian. Default is 1 (standard Gaussian).
        Returns
        -------
        np.ndarray
            The computed Gaussian function values for each element in `t`.
        Notes
        -----
        For `n=1`, this reduces to the standard Gaussian function. Increasing `n` makes the function sharper.
        """

        return np.array(a1 + a0 * np.exp(-((t - t0)**(2*n) / (2*sigma**(2*n)))))
#%%
# Nonlinear fit of btv_0.ff using A+B*sin(C*t+D)
def sinusoidal(t: np.ndarray, A: float, B: float, C: float, D: float) -> np.ndarray:
    """_summary_

    Args:
        t (_type_): time
        A (_type_): Amplitude offset
        B (_type_): Amplitude
        C (_type_): Frequency
        D (_type_): Phase shift

    Returns:
        _type_: _description_
    """
    return A + B * np.sin(2*np.pi*(C * t + D))
#%%
# Exponential fit: ff = A + B * exp(C * t)
def exponential(t: np.ndarray, A: float, B: float, C: float) -> np.ndarray:
    return A + B * np.exp(C * t)
#%%
def fitting(
        # object,
        time, ff,
        function:str = "sinusoidal",
        poly_deg: int = 3,
        maxfev: int = 10000,
        verbose: bool = True
    ) -> tuple[np.ndarray, np.ndarray, list]:
    
    if function == "sinusoidal":
        # Initial guess for parameters: A, B, C, D
        Av = np.mean(ff)
        A = (np.max(ff) - np.min(ff)) / 2
        W = 1 / (time[-1] - time[0])
        P = 0
        p0 = [Av, A, W, P]

        # Fit the data
        params, cov = curve_fit(sinusoidal, time, ff, p0=p0, maxfev=maxfev)
        # A_fit, B_fit, C_fit, D_fit = params

        # Calculate fitted values and metrics
        ff_fit = sinusoidal(time, *params)
        r2 = r2_score(ff_fit, ff)
        rmse = np.sqrt(mean_squared_error(ff_fit, ff))
        metrics = [r2, rmse, cov]

    elif function == "exponential":
        p0 = [np.max(ff), -1.0, np.min(ff)]
        params, _ = curve_fit(exponential, time, ff, p0=p0, maxfev=maxfev)
        ff_fit = exponential(time, *params)
        r2 = r2_score(ff_fit, ff)
        rmse = np.sqrt(mean_squared_error(ff_fit, ff))
        metrics = [r2, rmse]

    elif function == "polynomial":
        fit = Polynomial.fit(time, ff, deg=poly_deg)
        params = fit.coef[::-1]  # Reverse to standard order
        ff_fit = fit(time)
        r2 = r2_score(ff_fit, ff)
        rmse = np.sqrt(mean_squared_error(ff_fit, ff))
        metrics = [r2, rmse]
    elif function == "custom":
        pass

    else:
        print(f"Method {function} is not an option.")

    if verbose:
        print(f'{function} fit metrics: R^2={r2:.4f}, RMSE={rmse:.4f}\n',
              f'{function}: {params}')
    
    return ff_fit, params, metrics