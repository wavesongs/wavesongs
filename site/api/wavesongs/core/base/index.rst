wavesongs.core.base
===================

.. py:module:: wavesongs.core.base


Classes
-------

.. autoapisummary::

   wavesongs.core.base.Model
   wavesongs.core.base.Solver


Module Contents
---------------

.. py:class:: Model

   Bases: :py:obj:`abc.ABC`


   Base model class for the motor gesture of birdsongs.


   .. py:method:: bifurcation_ode()
      :abstractmethod:



   .. py:method:: control_parameters()
      :abstractmethod:



   .. py:method:: dict_params()
      :abstractmethod:



   .. py:method:: dict_z()
      :abstractmethod:



   .. py:method:: motor_gesture()
      :abstractmethod:



   .. py:method:: synthetize()
      :abstractmethod:



   .. py:attribute:: _F1
      :type:  str


   .. py:attribute:: _F2
      :type:  str


   .. py:attribute:: _N
      :type:  int
      :value: 1000


      Number of time steps for the model.

      :type: int


   .. py:attribute:: _PARAMS
      :type:  dict

      Model parameters

      :type: dict


   .. py:attribute:: _V_MAX
      :type:  float
      :value: -5000000.0


      Maximum labia walls velocity.

      :type: float


   .. py:attribute:: _Z
      :type:  dict


   .. py:attribute:: _mu_parameters
      :type:  tuple[float, Ellipsis]


   .. py:attribute:: _ovsr
      :type:  int
      :value: 20



   .. py:attribute:: _prct_noise
      :type:  int
      :value: 0



.. py:class:: Solver(model)

   Bases: :py:obj:`abc.ABC`


   Base solver class for the motor gesture of birdsongs.


   .. py:attribute:: model


