wavesongs.utils.math
====================

.. py:module:: wavesongs.utils.math

.. autoapi-nested-parse::

   Maht utils



Functions
---------

.. autoapisummary::

   wavesongs.utils.math.exponential
   wavesongs.utils.math.fitting
   wavesongs.utils.math.gaussian
   wavesongs.utils.math.rk4
   wavesongs.utils.math.sinusoidal


Module Contents
---------------

.. py:function:: exponential(t, A, B, C)

.. py:function:: fitting(time, ff, function = 'sinusoidal', poly_deg = 3, maxfev = 10000, verbose = True)

.. py:function:: gaussian(t, a0, t0, a1 = 0, sigma = 1, n = 1)

   Computes a generalized Gaussian function.
   :param t: Input array of time or independent variable values.
   :type t: np.ndarray
   :param a0: Amplitude of the Gaussian function.
   :type a0: float
   :param t0: Center (mean) of the Gaussian function.
   :type t0: float
   :param sigma: Standard deviation (spread or width) of the Gaussian function. Default is 1.
   :type sigma: float, optional
   :param n: Exponent controlling the shape of the Gaussian. Default is 1 (standard Gaussian).
   :type n: int, optional

   :returns: The computed Gaussian function values for each element in `t`.
   :rtype: np.ndarray

   .. rubric:: Notes

   For `n=1`, this reduces to the standard Gaussian function. Increasing `n` makes the function sharper.


.. py:function:: rk4(f, v, dt)

   Implentation of Runge-Kuta 4th order for a n-array

   :param f: differential equations functions y'=f(y)
   :type f: function
   :param v: array with the differential variables
   :type v: np.ndarray [x,y,i1,i2,i3]
   :param dt: rk4 time step
   :type dt: float

   :returns:

             rk4 : np.ndarray [x,y,i1,i2,i3]
                 reulst approximation

   .. rubric:: Example

   >>>


.. py:function:: sinusoidal(t, A, B, C, D)

   _summary_

   :param t: time
   :type t: _type_
   :param A: Amplitude offset
   :type A: _type_
   :param B: Amplitude
   :type B: _type_
   :param C: Frequency
   :type C: _type_
   :param D: Phase shift
   :type D: _type_

   :returns: _description_
   :rtype: _type_


