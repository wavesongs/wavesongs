"""
Methods to implement the motor gesture model for birdsongs.
"""

import numpy as np
from math import isnan
from time import time
from multiprocessing import Pool

from IPython.display import display as Display


# https://docs.scipy.org/doc/scipy/reference/optimize.html
from scipy.optimize import (
    # minimization (local)
    minimize,
    # global_search,
    brute,
    basinhopping,
    differential_evolution,
    shgo,
    dual_annealing,
    direct,
    # root finding
    root,
)


from sympy import (
    symbols,
    lambdify,
    solveset
)

# from copy import deepcopy
from maad.sound import normalize
from numpy.polynomial import Polynomial


from numpy.typing import ArrayLike, DTypeLike
from typing import (
    Callable,
    Any,
    Union,
    Literal,
)


from .base import Model as BaseModel
from wavesongs.utils.math import rk4, gaussian
from wavesongs.object import Synthetic, Syllable


class Model(BaseModel):
    """Model for the motor gesture of birdsongs.
    Bogdanov–Takens bifurcation
    """
    _PARAMS = {
        "gm": 4e4,       # time scaling constant
        # -------------------------------- Trachea --------------------------------
        "C": 343,        # speed of sound in media [m/s]
        "L": 0.025,      # trachea length [m]
        "r": 0.65,       # reflection coeficient [adimensionelss]
        # ------------------------- Beak, Glottis and OEC -------------------------
        "Ch": 1.43E-10,  # OEC Compliance [m^3/Pa]
        "MG": 20,        # Beak Inertance [Pa s^2/m^3 = kg/m^4]
        "MB": 1E4,       # Glottis Inertance [Pa s^2/m^3 = kg/m^4]
        "RB": 5E6,       # Beak Resistance [Pa s/m^3 = kg/m^4 s]
        "Rh": 24E3       # OEC Resistence [Pa s/m^3 = kg/m^4 s]
    }
    r"""dict : Model parameters

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
    """
    # ---------------- physical model constants -----------------
    _Z = {
        "a0": 0.11,
        "b0": -0.1,
        "b1": 1,
        "b2": 0,
    }
    r"""dict : Motor gesture curves, air-sac pressure (:math:`\alpha`)
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
    """


    # bifurcation saddle nodes and array length
    _N = 1000
    _mu2_beta = -2.5 # compute automatically
    _mu1_alpha = 1/3
    _mu_parameters = (_mu1_alpha, _mu2_beta)
    # General nonlinear equation model of second order

    _V_MAX = -5e6 # model constraint
    """float : Maximum labia walls velocity.
    """
    
    _prct_noise = 0

    def __init__(
            self,
            f1: str = "ys",
            f2: str =  "(-alpha-beta*xs-xs**3+xs**2)*gamma**2 - (xs+1)*gamma*xs*ys",
            # \gamma^2(-\alpha-\beta x-x^3+x^2) - \gamma(x+1)x y,
            ovsr: int = 10
        ):
        
        f2_eq = f2.replace("xs", "x").replace("ys", "y").replace("alpha", '\\alpha').replace("beta", '\\beta').replace("gamma", '\\gamma').replace('**', '^')

        self.ovsr = ovsr
        """int : Oversample for the RK4
        """
        self._F1 = f1
        r"""str : First linear equation.
        Where :math:`x` is the labial position and :math:`y` the labial wall velocity.

        .. math::

            \frac{dx}{dt} = y
        """
        self._F2 = f2
        rf"""str: Second linear equation.
        Where :math:`x` is the labial position and :math:`y` the labial wall velocity.

        .. math::

            \\frac{"{dy}"}{"{dt}"} = {f2_eq}

        This equation is obtained using the Bogdanov–Takens bifurcation :cite:p:`a-Amador2013`.
        """

    #%%
    def bifurcation_ode(
            self,
            symbols_str: str = "xs, ys, alpha, beta, gamma"
        ) -> tuple[np.ndarray, np.ndarray, Callable, Callable]:
        """

        Parameters
        ----------
            f1 : str

            f2 : str

        Return
        ------
            beta_bif : np.array

            mu1_curves : np.array

            f1 : lambda functions

            f2 : lambda functions


        Example
        -------
            >>>
        """
        beta_bif = np.linspace(self._mu2_beta, self._mu1_alpha, self._N)
        xs, ys, alpha, beta, gamma = symbols(symbols_str)
        # ---------------- Labia EDO's Bifurcation -----------------------
        f1 = eval(self._F1)
        f2 = eval(self._F2)

        x01 = solveset(f1, ys).union(solveset(f1, xs))
        f2_x01 = f2.subs(ys, x01.args[0])

        f = solveset(f2_x01, alpha)
        g = alpha

        df = f.args[0].diff(xs) # type: ignore
        dg = g.diff(xs)

        roots_bif = solveset(df-dg, xs)

        mu1_curves = []
        for ff in roots_bif.args:
            # root evaluatings beta
            mu1 = np.zeros(self._N, dtype=float)
            x_root = np.zeros(self._N, dtype=float)
            for i in range(self._N):
                x_root[i] = ff.subs(beta, beta_bif[i])
                mu1[i] = f.subs([(beta,beta_bif[i]), (xs,x_root[i])]).args[0]
            mu1_curves.append(np.array(mu1, dtype=float))
        mu1_curves = np.array(mu1_curves)

        f1 = lambdify([xs, ys, alpha, beta, gamma], f1)
        f2 = lambdify([xs, ys, alpha, beta, gamma], f2)

        return beta_bif, mu1_curves, f1, f2
    #%%
    def beta(
            self,
            syllable: Synthetic | Syllable,
            z: dict = _Z,
            mode: Literal["poly", "ff", "custom"] = "ff", 
            poly_order: int = 3,
            func: Callable | None = None,
            **kwargs
        ) -> np.ndarray:
        
        t = np.linspace(0, syllable.T, len(syllable.s))
        b = np.array([float(z[f"b{i}"]) for i in range(poly_order)])
        
        if mode == "poly":
            t_parabole = np.array([t**i for i in range(poly_order)])
            beta = np.dot(b, t_parabole)
        elif mode == "ff":
            poly = Polynomial.fit(syllable.ff_time, syllable.ff, deg=10)
            _, y = poly.linspace(np.size(syllable.s))

            beta = np.dot(b, 
                          np.vstack([(y/np.max(y))**i
                                     for i in range(poly_order)]))
        elif mode == "custom" and func is not None:
            beta = func(t) # need improve
        else:
            raise Exception("The method for beta definition entered is not implemented. There are two possible options: poly, ff_aprox, and custom.")

        return beta
    #%%
    def alpha(
            self,
            syllable: Synthetic | Syllable,
            z: dict = _Z,
            mode: Literal["poly", "linear", "gaussian", "custom"] = "gaussian",
            poly_order: int = 3,
            func: Callable | None = None,
            **kwargs
        ) -> np.ndarray:
        n = kwargs.get("n", 2)
        sigma = kwargs.get("sigma", 1)

        a = np.array([z["a0"]])
        t = np.linspace(0, syllable.T, len(syllable.s))

        if mode == "poly":
            a = np.array([z[f"a{i}"] for i in range(poly_order)])
            t_parabole = np.array([t**i for i in range(poly_order)])
            alpha = np.dot(a, t_parabole)
        elif mode == "linear":
            alpha = np.ndarray([a[0] for _ in t])
        elif mode == "gaussian":
            alpha = gaussian(t, a[0], syllable.T/2, sigma, n) # gaussian curve
        elif mode == "lissajous":
            alpha = a[0] * np.cos(2 * np.pi * z["a1"] * t + z.get("a3", 0)) # lissajous curve
        elif mode == "custom" and func is not None:
            alpha = func(t)
        else:
            raise Exception("The method for alpha definition entered is not implemented. There are four possible options: parabola, linear, gaussian, and custom")
        return alpha
    #%%
    def control_parameters(
            self,
            syllable: Synthetic|Syllable,
            z: dict = _Z,
            alpha_mode: Literal["poly", "linear", "gaussian", "custom"] = "gaussian",
            beta_mode: Literal["poly", "ff", "custom"] = "ff", 
            poly_order: int = 3,
            func: Callable | None = None,
            **kwargs
        ) -> list[np.ndarray]:
        """
        """
        syllable.z = z

        alpha = self.alpha(syllable, z, alpha_mode, poly_order, func, **kwargs)
        beta = self.beta(syllable, z, beta_mode, poly_order, func, **kwargs)

        return [alpha, beta]
    #%%
    def motor_gesture(
            self,
            syllable: Syllable|Synthetic,
            curves: list[np.ndarray],
            params: dict = _PARAMS
        ) -> Synthetic:
        """


        Parameters
        ----------
            pramams : dict

        Return
        ------
            synth : Syllable
                Synthethic syllable with same parameters except
                for s and vs

        Example
        -------
            >>>

        """
        # rk4 constans
        t = 0                                    # initial time
        tmax = int(syllable.s.size * self.ovsr - 1)  # maximum time
        dt = 1 / (self.ovsr * syllable.sr)           # step
        out = np.zeros(syllable.s.size)          # output pressure, FINAL SIGNAL

        # trachea pressure pback and pin vectors initialization
        pi = np.zeros(tmax)              # input pressure
        pb = np.zeros(tmax)              # pressure back

        # initial vector ODEs (v0), it is not too relevant
        v = 1e-4 * np.array([1e2, 1e1, 1, 1, 1, 1])
        vs = [v] # np.zeros(tmax)
        # ------------- MG BIRD MODEL PARAMETERS -----------
        ## Syrinx
        gamma = params["gm"]
        ## Trachea
        r = params['r']
        L = params['L']
        c = params['C']
        ## OEC
        Ch = params['Ch']
        MG = params['MG']
        MB = params['MB']
        RB = params['RB']
        Rh = params['Rh']
        # ----------------------------------------------------
        alpha, beta = curves
        ## ------------- Bogdanov–Takens bifurcation ------------------
        beta_bif, mu1_curves, f1, f2 = self.bifurcation_ode()
        # ------------------------------ Physical Model -----------------------------
        def ODEs(v: np.ndarray) -> np.ndarray:
            dv = np.zeros(6)
            x, y, pout, i1, i2, i3 = v
            # ----------------- direct implementation of the EDOs -----------
            dv[0] = f1(x, y, alpha[t//self.ovsr], beta[t//self.ovsr], gamma)
            dv[1] = f2(x, y, alpha[t//self.ovsr], beta[t//self.ovsr], gamma)
            # ------------------------- trachea ------------------------
            pbold = pb[t] # pressure back before
            # Pin(t) = Ay(t) + pback(t-L/C) = Signal_env*v[1] + pb[t-L/C/dt]
            # pi[t] = (0.5*syllable.envelope[t//ovsr])*dv[1] + pb[t-int(L/c/dt)]
            # A = 1 #(0.5*syllable.envelope[t//ovsr])
            alpha_mean = alpha[:t//self.ovsr].mean()
            # A = 1 # alpha[:t//self.ovsr].mean()
            A = 0 if isnan(alpha_mean) else alpha_mean
            pi[t] = A*dv[1] + pb[t-int(L/c/dt)]
            pb[t] = -r*pi[t-int(L/c/dt)]    # pressure back: -rPin(t-L/C)
            pout = (1-r)*pi[t-int(L/c/dt)]  # pout
            # ---------------------------------------------------------------
            dv[2] = (pb[t]-pbold)/dt # dpout
            # ----------------------- OEC EDOs -----------------------
            dv[3] = i2
            dv[4] = -(1/Ch/MG)*i1 - Rh*(1/MB+1/MG)*i2 \
                    + (1/MG/Ch+Rh*RB/MG/MB)*i3 + (1/MG)*dv[2] \
                    + (Rh*RB/MG/MB)*pout
            dv[5] = -(MG/MB)*i2 - (Rh/MB)*i3 + (1/MB)*pout
            return dv
        # ----------------------- Update EDOs Variables ----------------------
        while t < tmax and np.abs(v[1]) > self._V_MAX:
            v = rk4(ODEs, v, dt)        # RK4 step
            vs.append(v)                # save step # vs[t] = v
            out[t//self.ovsr] = RB*v[-1]    # update output signal (synthetic)
            t += 1
        # ------------------------------------------------------------
        # synth = deepcopy(syllable)
        synth = Synthetic(
            duration = syllable.tlim[1] - syllable.tlim[0],
            sr = syllable.sr,
            file_id = f"{syllable.id}-synthetic",
            proj_dirs = syllable.proj_dirs,
            metadata = {
                "type": "",
                "no_syllable":  0,
            },
        )

        # Compute acoustical features to synthetic syllable
        # synth.acoustical_features(
        #     n_fft = syllable.n_fft,
        #     hop_length = syllable.hop_length,
        #     win_length = syllable.win_length,
        #     umbral_FF = syllable.umbral_FF,
        #     ff_method = syllable.ff_method,
        #     flim = syllable.flim,
        #     Nt = syllable.Nt,
        #     center = syllable.center,
        #     llambda = syllable.llambda,
        #     n_mfcc = syllable.n_mfcc,
        #     n_mels = syllable.n_mels,
        #     stft_window = syllable.stft_window,
        #     pad_mode = syllable.pad_mode,
        # )

        synth.initialize(normalize(out, max_amp=1.0))
        # Copying model parameters
        synth.params = params
        synth.alpha = alpha
        synth.beta = beta
        synth.z = syllable.z

        # saving bifurcation curvess and functions
        synth.beta_bif = beta_bif
        synth.mu1_curves = mu1_curves
        synth.f1 = f1
        synth.f2 = f2

        synth.times_vs = np.linspace(
            0,
            len(syllable.s)/syllable.sr,
            len(syllable.s)*self.ovsr
        )  # time vector for physical model variables
        synth.vs = np.array(vs) # PODE MUDAR

        # synth.s = normalize(out, max_amp=1.0)

        return synth
    #%%
    def dict_z(
        self,
        z: list[float] | dict[str, float] = _Z
    ) -> dict[str, float]:
        """


        Parameters
        ----------
            z : list[float] | dict
                [a0,a1,a2_,b,b1,b2,gamma]

        Return
        ------
            z : dict

        Exmaple
        -------
            >>>
        """
        if isinstance(z, (list, tuple)):
            keys = list(self._Z.keys())
            z0 = {keys[i]: z[i]
                   for i in range(min(len(z), len(keys)))}
        elif isinstance(z, dict):
            z0 = {k: z[k] for k in self.z.keys()}
        
        return z0
    #%%
    def dict_params(
        self,
        params: tuple[Any, ...] | dict[str, float] = _PARAMS
    ) -> dict[str, float]:
        """


        Parameters
        ----------
            params : list[float] | dict
                [a0,a1,a2_,b,b1,b2,gamma]

        Return
        ------
            params : dict

        Exmaple
        -------
            >>>
        """
        if isinstance(params, (list, tuple)):
            keys = list(self._PARAMS.keys())
            params0 = {keys[i]: params[i]
                       for i in range(min(len(params), len(keys)))}
        elif isinstance(params, dict):
            params0 = {k: params[k] for k in params.keys()}

        return params0

    #%%
    def synthetize(
            self,
            syllable: Syllable,
            z: dict[str, Any]  = _Z,
            params: dict[str, Any] = _PARAMS,
            beta_mode: Literal["poly", "ff", "custom"] = "ff", 
            alpha_mode: Literal["poly", "linear", "gaussian", "custom"] = "gaussian",
            **kwargs
        ) -> Synthetic:
        """
        Generate a synthetic syllable given some parameters and mehotd

        Parameters
        ----------
            z: list[float]

            params : dict

            order : int

        Return
        ------
            synth : Syllable


        Examples
        --------
            >>>
        """
        self.z = z
        self.params = params
        
        # define alpha and beta parameters
        curves = self.control_parameters(syllable, z, alpha_mode, beta_mode, **kwargs)
        synth = self.motor_gesture(syllable, curves, params) # generate the synthetic syllable

        return synth

#%%
class Solver:

    # trust regions ranges for minimization
    _ranges: dict[str, tuple[float, float]] = {
        "gm": (1e4, 1e5),
        "a0": (0, 0.3),
        "b0": (-1, 0.5),
        "b1": (0, 2),
        "b2": (0, 2),
        "alpha": (0, 0.3),
        "beta": (-1, 2),
    }
    r"""dict : Trust regions ranges for the model parameters.
    """
    
    def __init__(
            self,
            model: Model = Model(),
            order: int = 2
        ):
        """
        Optimizer class to solve the minimization problem for the motor gesture of birdsongs.

        Parameters
        ----------
            syllable : Syllable, optional
                The syllable syllableect to optimize. If None, a default syllable is used.
        """
        self.model = model
        self._PARAMS = self.model._PARAMS
        # self._Z = self.model._Z
        self.order = order

        self.z: list[float] = list(self.model._Z.values())
        """
        list array with the model parameters [a0, b0, b1, b2]
        """

    # ==========================================================================
    # --------------------------- Residual Functions ---------------------------
    # ==========================================================================
    

    # %%
    def residual(
        self, z: list[float],
        *params: tuple[Any, ...]
    ) -> np.ndarray:
        """


        Parameters
        ----------
            z : list [a0, b0, b1, b2]

            params : parameters for the model

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        self.z = z

        z_dict = self.model.dict_z(z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return synthetic.SCIFF  # + synth_syllable.scoreFF
        # scoreSCI +  syllable_synth.scoreFF
    # %%
    def residual_sci(
        self, z: list[float],
        *params: tuple[Any, ...]
    ) -> np.ndarray:
        """


        Parameters
        ----------
            z : list [a0,b0,b1,b2]

            paramvs : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        self.z

        z_dict = self.model.dict_z(z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return synthetic.SCIFF  # scoreSCI +  syllable_synth.scoreFF
    # %%
    def residual_sci_a0(self, z: list[float], *params: tuple[Any, ...]) -> np.ndarray:
        """


        Parameters
        ----------
            z : list

            params : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        # z_dict = {"a0": z[0]}
        self.z[0] = z[0]
        z_dict = self.model.dict_z(self.z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)


        return np.array([synthetic.scoreSCI]) # synthetic.scoreSCI  # syllable_synth.scoreFF
    # %%
    def residual_ff(self, z: list[float], *params: tuple[Any, ...]) -> np.ndarray:
        """


        Parameters
        ----------
            z : list

            params : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        self.z = z

        z_dict = self.model.dict_z(z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return np.array([synthetic.scoreFF]) # synthetic.scoreFF  # + syllable_synth.scoreCentroid
    # %%
    def residual_ff_b02(self, z: list[float], *params: tuple[Any, ...]) -> np.ndarray:
        """


        Parameters
        ----------
            z : list

            params : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """

        assert isinstance(params[-1], Syllable)
        syllable = params[-1]

        # z_dict = {"b0": float(z[0]), "b2": float(z[1])}
        # z_dict = self.model.dict_z([0, z[0], 0, z[1]])
        self.z[1] = z[0] # b0
        self.z[3] = z[1] # 
        z_dict = self.model.dict_z(self.z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return np.array([synthetic.scoreFF]) # synthetic.scoreFF  # + syllable_synth.scoreCentroid
    # %%
    def residual_ff_b1(self, z: dict, *params: tuple) -> np.ndarray:
        """


        Parameters
        ----------
            z : list

            params : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        # z_dict = {"b1": float(z[0])}
        # z_dict = self.model.dict_z([0, 0, z[0], 0])
        self.z[2] = z[0] # b1
        z_dict = self.model.dict_z(self.z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return np.array([synthetic.scoreFF])  # + syllable_synth.scoreCentroid
    # %%
    def residual_correlation(self, z: list[float], *params: tuple) -> np.ndarray:
        """


        Parameters
        ----------
            z : list

            params : tuple

        Return
        ------
            SCIFF: np.ndarray
                Fundamental Frequency and Spectral Content Index scores

        Examples
        --------
            >>>
        """
        assert isinstance(params[-1], Syllable)
        syllable = params[-1]
        self.z = z

        z_dict = self.model.dict_z(z)
        params_dict = self.model.dict_params(params)

        synthetic = self.model.synthetize(syllable, z_dict, params_dict, beta_method="ff_aprox")
        synthetic.evaluate(syllable, order=self.order)

        return synthetic.residualCorrelation
    # ==========================================================================
    # --------------------------- Optimizer Functions --------------------------
    # ==========================================================================
    # ----------------
    # %%
    def optimal(
        self,
        syllable: Syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            parameters: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        args = tuple(params.values()) + (syllable,)
        ranges = (self._ranges["a0"], self._ranges["b0"], self._ranges["b1"], self._ranges["b2"])
        start = time()
        if method == "brute":
            x0, fval, grid, Jout = brute(
                self.residual,
                ranges=ranges,
                args=args,
                Ns=Ns,
                full_output=full_output,
                disp=disp,
                workers=workers,
            )
        else:
            raise Exception(f"The method {method} does not exits.")
        end = time()
        tdiff = (end - start) / 60
        # a0, b0, b1, b2 = x0
        print(
            f"\t Optimal values: a_0={x0[0]:.4f}, b_0={x0[1]:.4f}, b_1={x0[2]:.4f},"
            + f" b_2={x0[3]:.4f}, t={tdiff:.2f} min"
        )
        z_dict = self.model.dict_z(list(x0))

        # syllable.z = z_dict

        return z_dict
    # %%
    def optimal_bs(
        self,
        syllable: Syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            params: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        args = tuple(params.values()) + (syllable,)
        # ---------------- b0 and b2 --------------------
        # ranges02 = (self._ranges["b0"], self._ranges["b2"])
        start02 = time()
        if method == "brute":
            x0, fval, grid, Jout = brute(
                self.residual_ff_b02,
                ranges=(self._ranges["b0"], self._ranges["b2"]),
                args=args,
                Ns=Ns,
                full_output=full_output,
                disp=disp,
                workers=workers,
            )
        end02 = time()
        b0, b2 = x0

        tdiff = (end02 - start02) / 60
        print(
            f"\t Optimal values: b_0={b0:.4f}, b_2={b2:.4f}, t={tdiff:.2f} min"
        )
        syllable.z["b0"] = round(float(b0), 5)
        syllable.z["b2"] = round(float(b2), 5)
        # print("Solved: ", x0)
        self.z = list(x0)

        # ---------------- b1-------------------- b3
        # ranges1 = (self._ranges["b1"],)
        start1 = time()
        if method == "brute":
            x0, fval, grid, Jout = brute(
                self.residual_ff_b1,
                ranges=(self._ranges["b1"],),
                args=args,
                Ns=Ns,
                full_output=full_output,
                disp=disp,
                workers=workers,
            )
        else:
            raise Exception(f"The method {method} does not exits.")
        end1 = time()
        b1 = round(float(x0[0]), 5)
        print(
            f"\t Optimal values: b_1={b1:.4f}, t={(end1-start1)/60:.2f} min"
        )
        syllable.z["b1"] = b1
        # self.z = list(x0)

        return syllable.z
    # %%
    def optimal_a(
        self,
        syllable: Syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            params: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        args = tuple(params.values()) + (syllable,)
        # ranges = (self._ranges["a0"],)

        start = time()
        if method == "brute":
            x0, fval, grid, Jout = brute(
                self.residual_sci_a0,
                ranges=(self._ranges["a0"],),
                args=args,
                Ns=Ns,
                full_output=full_output,
                disp=disp,
                workers=workers,
            )
        else:
            raise Exception(f"The method {method} does not exits.")
        end = time()
        a0 = round(float(x0[0]), 5)
        print(f"\t Optimal value: a_0={a0:.4f}, t={(end-start)/60:.2f} min")
        syllable.z["a0"] = a0
        self.z[0] = a0
        return syllable.z
    # %%
    def optimal_gamma(
        self,
        syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            parameters: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        args = tuple(params.values()) + (syllable,)
        # ranges = self._ranges["gm"]
        start = time()
        if method == "brute":
            x0, fval, grid, Jout = brute(
                self.residual_sci,
                ranges=(self._ranges["gm"], ),
                args=args,
                Ns=Ns,
                full_output=full_output,
                disp=disp,
                workers=workers,
            )
        else:
            raise Exception(f"The method {method} does not exits.")
        end = time()
        gamma = x0[0]
        print(f"\t\tOptimal values: γ* = {gamma:.0f}, t={(end-start)/60:.2f} min")
        syllable.Z["gm"] = gamma
        self.z[4] = gamma

        return syllable.z
    # %%
    def optimal_params(
        self,
        syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            parameters: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        start = time()
        print("\nComputing a0*...")
        z_opt_a0 = self.optimal_a(
            syllable,
            params=params,
            method=method,
            Ns=Ns,
            full_output=full_output,
            disp=disp,
            workers=workers,
        )
        syllable.z = z_opt_a0
        print(f"Finished computing a0*: {z_opt_a0}")
        # self.z = z_opt_a0

        print("\nComputing b0*, b1*, and b2*...")
        z_opt_b01 = self.optimal_bs(
            syllable,
            params=params,
            method=method,
            Ns=Ns,
            full_output=full_output,
            disp=disp,
            workers=workers,
        )

        syllable.z = z_opt_b01
        print(f"Finished computing b0*, b1*, and b2*: {z_opt_b01}")
        # self.z[1:4] = z_opt_b01[:]

        end = time()
        print(f"\nTime of execution: {(end-start)/60:.2f} min")

        if disp:
            print(f"\nOptimal model values (alpha and beta coefficients):\n\t{z_opt_b01}")

        return z_opt_b01
    # %%
    def optimal_params_general(
        self,
        syllable,
        params: dict|None = None,
        method: str = "brute",
        Ns: int = 20,
        full_output: bool = True,
        disp: bool = True,
        workers: int = -1,
    ) -> dict:
        """


        Parameters
        ----------
            syllable : Syllable

            params : dict

            method : str = "brute"

            Ns : int, optional = 20

            full_output : bool, optional = False

            disp : bool, optional = False

            workers : int, optional = 1


        Return
        ------
            parameters: dict


        Examples
        --------
            >>>
        """
        params = self._PARAMS if params is None else params

        # args = tuple(params.values())+(syllable,)
        start = time()
        print("Computing optimal variables: a0*, b0*, b1*, and b2*...")
        z_opt_b01 = self.optimal(
            syllable,
            params=params,
            method=method,
            Ns=Ns,
            full_output=full_output,
            disp=disp,
            workers=workers,
        )
        syllable.z = z_opt_b01
        print("Finished")
        end = time()
        print(f"Time of execution = {(end-start)/60:.4f} min")

        return syllable.z
    # %%
    def all_optimal_gammas(self, bird):
        start = time()

        gammas = np.zeros(bird.no_syllables)
        for i in range(1, bird.no_syllables + 1):
            print(f"Syllable {i}/{bird.no_syllables}")
            syllable = bird.Syllable(i)
            gammas[i - 1] = self.optimal_gamma(syllable)

        syllable.optimal_gamma = np.mean(gammas)
        syllable.Gammas = gammas
        # syllable = syllable0
        # syllable.p["gm"].set(value=syllable.optimal_gamma, vary=False)
        end = time()
        print(f"Time of execution = {(end-start)/60:.4f} min")
        return syllable.optimal_gamma
