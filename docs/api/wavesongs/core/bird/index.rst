wavesongs.core.bird
===================

.. py:module:: wavesongs.core.bird

.. autoapi-nested-parse::

   Methods to implement the motor gesture model for birdsongs.



Classes
-------

.. autoapisummary::

   wavesongs.core.bird.Model
   wavesongs.core.bird.Solver


Module Contents
---------------

.. py:class:: Model(f1 = 'ys', f2 = '(-alpha-beta*xs-xs**3+xs**2)*gamma**2 - (xs+1)*gamma*xs*ys')

   Bases: :py:obj:`wavesongs.core.base.Model`


   Model for the motor gesture of birdsongs.
   Bogdanov–Takens bifurcation


   .. py:method:: _gaussian(t, a0, t0, sigma = 1, n = 1)

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



   .. py:method:: alpha(syllable, z = _Z, mode = 'gaussian', poly_order = 3, func = None, **kwargs)


   .. py:method:: beta(syllable, z = _Z, mode = 'ff', poly_order = 3, func = None, **kwargs)


   .. py:method:: bifurcation_ode(symbols_str = 'xs, ys, alpha, beta, gamma')

      :param f1:
      :type f1: str
      :param f2:
      :type f2: str

      :returns: beta_bif : np.array

                mu1_curves : np.array

                f1 : lambda functions

                f2 : lambda functions

      .. rubric:: Example

      >>>



   .. py:method:: control_parameters(syllable, z = _Z, alpha_mode = 'gaussian', beta_mode = 'ff', poly_order = 3, func = None, **kwargs)

      



   .. py:method:: dict_params(params = _PARAMS)

      :param params: [a0,a1,a2_,b,b1,b2,gamma]
      :type params: list[float] | dict

      :returns: * params : dict
                * *Exmaple*
                * *-------* -- >>>



   .. py:method:: dict_z(z = _Z)

      :param z: [a0,a1,a2_,b,b1,b2,gamma]
      :type z: list[float] | dict

      :returns: * z : dict
                * *Exmaple*
                * *-------* -- >>>



   .. py:method:: motor_gesture(syllable, curves, params = _PARAMS)

      :param pramams:
      :type pramams: dict

      :returns:

                synth : Syllable
                    Synthethic syllable with same parameters except
                    for s and vs

      .. rubric:: Example

      >>>



   .. py:method:: synthetize(syllable, z = _Z, params = _PARAMS, beta_mode = 'ff', alpha_mode = 'gaussian', **kwargs)

      Generate a synthetic syllable given some parameters and mehotd

      :param z:
      :type z: list[float]
      :param params:
      :type params: dict
      :param order:
      :type order: int

      :returns: synth : Syllable

      .. rubric:: Examples

      >>>



   .. py:attribute:: _F1
      :value: 'ys'


      First linear equation.
      Where :math:`x` is the labial position and :math:`y` the labial wall velocity.

      .. math::

          \frac{dx}{dt} = y

      :type: str


   .. py:attribute:: _F2
      :value: '(-alpha-beta*xs-xs**3+xs**2)*gamma**2 - (xs+1)*gamma*xs*ys'



   .. py:attribute:: _N
      :value: 1000


      Number of time steps for the model.

      :type: int


   .. py:attribute:: _PARAMS

      Model parameters

      .. table:: Birdsongs model parameters :cite:p:`a-Amador2013`.
          :width: 80%
          :widths: 2 6 3 3

          ==============  ========================  =======  ====================
          Constant        Description               Value     Unit
          ==============  ========================  =======  ====================
          :math:`\gamma`  Time scaling constant     40000    :math:`dms`
          :math:`C`       Speed of sound in media   343      :math:`m / s`
          :math:`L`       Trachea length            0.025    :math:`m`
          :math:`r`       Reflection coeficient     0.65     :math:`dms`
          :math:`Ch`      OEC Compliance            1.43     :math:`m^3 / Pa`
          :math:`MG`      Beak Inertance            20       :math:`kg / m^4`
          :math:`MB`      Glottis Inertance         10000    :math:`kg / m^4`
          :math:`RB`      Beak Resistance           5000000  :math:`s\; kg / m^4`
          :math:`Rh`      OEC Resistence            24000    :math:`s\;kg / m^4`
          ==============  ========================  =======  ====================

      Where :math:`dms` means dimensionless.

      :type: dict


   .. py:attribute:: _V_MAX
      :value: -5000000.0


      Maximum labia walls velocity.

      :type: float


   .. py:attribute:: _Z

      Motor gesture curves, air-sac pressure (:math:`\alpha`)
      and labial wall tension (:math:`\beta`). This function has two approaches:

      .. math::
          \begin{equation}
          \begin{aligned}[c]
              & \text{Performance}\\ \\
              & \alpha(t) = a_0  FIXING\\
              & \beta(t) = b_0 + b_1 \tilde{FF} + b_2 \tilde{FF}^2
          \end{aligned}
          \qquad\qquad\qquad
          \begin{aligned}[c]
              & \text{Interpretability}\\ \\
              & \alpha(t) = a_0 \\
              & \beta(t) = b_0 + b_1 t + b_2 t^2
          \end{aligned}
          \end{equation}

      The best performance, with the lowest relative errors, is obtained when the rescaled
      fundamental frequency is used as input through a quadratic composition, with :math:`\tilde{FF}=FF/10^4`.

      :type: dict


   .. py:attribute:: _mu1_alpha
      :value: 0.3333333333333333



   .. py:attribute:: _mu2_beta
      :value: -2.5



   .. py:attribute:: _mu_parameters


   .. py:attribute:: _ovsr
      :value: 20



   .. py:attribute:: _prct_noise
      :value: 0



.. py:class:: Solver(model = Model(), order = 2)

   .. py:method:: all_optimal_gammas(bird)


   .. py:method:: optimal(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: parameters: dict

      .. rubric:: Examples

      >>>



   .. py:method:: optimal_a(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: params: dict

      .. rubric:: Examples

      >>>



   .. py:method:: optimal_bs(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: params: dict

      .. rubric:: Examples

      >>>



   .. py:method:: optimal_gamma(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: parameters: dict

      .. rubric:: Examples

      >>>



   .. py:method:: optimal_params(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: parameters: dict

      .. rubric:: Examples

      >>>



   .. py:method:: optimal_params_general(syllable, params = None, method = 'brute', Ns = 20, full_output = True, disp = True, workers = -1)

      :param syllable:
      :type syllable: Syllable
      :param params:
      :type params: dict
      :param method:
      :type method: str = "brute"
      :param Ns:
      :type Ns: int, optional = 20
      :param full_output:
      :type full_output: bool, optional = False
      :param disp:
      :type disp: bool, optional = False
      :param workers:
      :type workers: int, optional = 1

      :returns: parameters: dict

      .. rubric:: Examples

      >>>



   .. py:method:: residual(z, *params)

      :param z:
      :type z: list [a0, b0, b1, b2]
      :param params:
      :type params: parameters for the model

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_correlation(z, *params)

      :param z:
      :type z: list
      :param params:
      :type params: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_ff(z, *params)

      :param z:
      :type z: list
      :param params:
      :type params: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_ff_b02(z, *params)

      :param z:
      :type z: list
      :param params:
      :type params: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_ff_b1(z, *params)

      :param z:
      :type z: list
      :param params:
      :type params: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_sci(z, *params)

      :param z:
      :type z: list [a0,b0,b1,b2]
      :param paramvs:
      :type paramvs: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:method:: residual_sci_a0(z, *params)

      :param z:
      :type z: list
      :param params:
      :type params: tuple

      :returns:

                SCIFF: np.ndarray
                    Fundamental Frequency and Spectral Content Index scores

      .. rubric:: Examples

      >>>



   .. py:attribute:: _PARAMS


   .. py:attribute:: _ranges
      :type:  dict[str, tuple[float, float]]

      Trust regions ranges for the model parameters.

      :type: dict


   .. py:attribute:: model


   .. py:attribute:: order
      :value: 2



   .. py:attribute:: z
      :type:  list[float]

      list array with the model parameters [a0, b0, b1, b2]


