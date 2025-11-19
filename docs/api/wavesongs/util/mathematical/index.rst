wavesongs.util.mathematical
===========================

.. py:module:: wavesongs.util.mathematical


Functions
---------

.. autoapisummary::

   wavesongs.util.mathematical.rk4


Module Contents
---------------

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


