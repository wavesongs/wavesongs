import numpy as np
from maad.sound import normalize
from abc import ABC, abstractmethod
from wavesongs_new.utils.math import rk4


from math import isnan

from sympy import (
    symbols,
    lambdify,
    sympify,
    solveset
)

from numba import njit

# Module constants
_C = 343        # speed of sound in media [m/s]
    
ZF_PARAMS = {
    "gm": 24e3,       # time scaling constant
    # ------------------------ Trachea ----------------------
    "L": 0.025,      # trachea length [m]
    "r": 0.65,       # reflection coeficient [adimensionelss]
    # ------------------------- OEC -------------------------
    "Ch": 1.43E-10,  # OEC Compliance [m^3/Pa]
    "MG": 20,        # Beak Inertance [Pa s^2/m^3 = kg/m^4]
    "MB": 1E4,       # Glottis Inertance [Pa s^2/m^3 = kg/m^4]
    "RB": 5E6,       # Beak Resistance [Pa s/m^3 = kg/m^4 s]
    "Rh": 24E3       # OEC Resistence [Pa s/m^3 = kg/m^4 s]
}


# ---------------------------------------------------------------------
# --------------------------- Compiled ODEs ---------------------------
# ---------------------------------------------------------------------
@njit(cache=True)
def _syrinx_ode(x, y, alpha, beta, gamma):
    dx = y
    dy = (
        (-alpha - beta * x - x**3 + x**2) * gamma**2
        - (x + 1.0) * gamma * x * y
    )
    return dx, dy

@njit(cache=True)
def _oec_ode(
    i1: float,
    i2: float,
    i3: float,
    pout: float,
    dpout: float,
    ch: float,
    mg: float,
    mb: float,
    rb: float,
    rh: float,
) -> tuple[float, float, float]:
    di1 = i2

    di2 = (
        -(1.0 / ch / mg) * i1
        - rh * (1.0 / mb + 1.0 / mg) * i2
        + (1.0 / mg / ch + rh * rb / mg / mb) * i3
        + (1.0 / mg) * dpout
        + (rh * rb / mg / mb) * pout
    )

    di3 = (
        -(mg / mb) * i2
        - (rh / mb) * i3
        + (1.0 / mb) * pout
    )

    return di1, di2, di3

@njit(cache=True)
def _trachea_output(t, y, alpha_mean, dt, delay_steps, reflection, pi, pb):
    delayed_index = t - delay_steps
    # if delayed_index < 0:
    #     delayed_pi = 0.0
    #     delayed_pb = 0.0
    # else:
    delayed_pi = pi[delayed_index]
    delayed_pb = pb[delayed_index]

    pin = alpha_mean * y + delayed_pb
    pout = (1.0 - reflection) * delayed_pi
    current_pb = -reflection * delayed_pi
    previous_pb = pb[t - 1] if t > 0 else 0.0
    dpout = (current_pb - previous_pb) / dt

    return pin, current_pb, pout, dpout

# ---------------------------------------------------------------------
# ----------------------- Compiled Cupled ODEs ------------------------
# ---------------------------------------------------------------------
@njit
def _syrinx_oec_ode(
    state,
    alpha,
    beta,
    gamma,
    ch,
    mg,
    mb,
    rb,
    rh,
):
    x, y, i1, i2, i3 = state
    derivative = np.empty(5, dtype=np.float64)

    derivative[0], derivative[1] = _syrinx_ode(x, y, alpha, beta, gamma)

    derivative[2], derivative[3], derivative[4] = _oec_ode(
        i1,
        i2,
        i3,
        pout=0.0,
        dpout=0.0,
        ch=ch,
        mg=mg,
        mb=mb,
        rb=rb,
        rh=rh,
    )

    return derivative



@njit(cache=True)
def _syrinx_trachea_oec_ode(
    state,
    alpha,
    beta,
    gamma,
    pout,
    dpout,
    ch,
    mg,
    mb,
    rb,
    rh,
):
    x, y, _, i1, i2, i3 = state
    derivative = np.empty(6, dtype=np.float64)

    derivative[0], derivative[1] = _syrinx_ode(x, y, alpha, beta, gamma)

    derivative[2] = dpout
    derivative[3], derivative[4], derivative[5] = _oec_ode(
        i1, i2, i3, pout, dpout, ch, mg, mb, rb, rh
    )
    return derivative

# ---------------------------------------------------------------------
# ----------------------- Compiled RK4 solvers ------------------------
# ---------------------------------------------------------------------
@njit(cache=True)
def rk4_syrinx_trachea_oec(
    control_alpha,
    control_beta,
    tmax,
    ovsr,
    dt,
    gamma,
    delay_steps,
    reflection,
    ch,
    mg,
    mb,
    rb,
    rh,
):
    state = 1e-4 * np.array([1e2, 1e1, 1.0, 1.0, 1.0, 1.0])
    output = np.zeros(tmax // ovsr + 1, dtype=np.float64)
    pi = np.zeros(tmax, dtype=np.float64)
    pb = np.zeros(tmax, dtype=np.float64)
    alpha_cumsum = np.cumsum(control_alpha)

    for t in range(tmax):
        control_index = t // ovsr
        alpha = control_alpha[control_index]
        beta = control_beta[control_index]
        alpha_mean = alpha_cumsum[control_index - 1] / control_index if control_index > 0 else 0.0

        _, _, pout, dpout = _trachea_output(
            t,
            _syrinx_ode(state[0], state[1], alpha, beta, gamma)[1],
            alpha_mean,
            dt,
            delay_steps,
            reflection,
            pi,
            pb,
        )

        k1 = _syrinx_trachea_oec_ode(
            state, alpha, beta, gamma, pout, dpout, ch, mg, mb, rb, rh
        )
        k2 = _syrinx_trachea_oec_ode(
            state + 0.5 * dt * k1,
            alpha, beta, gamma, pout, dpout, ch, mg, mb, rb, rh,
        )
        k3 = _syrinx_trachea_oec_ode(
            state + 0.5 * dt * k2,
            alpha, beta, gamma, pout, dpout, ch, mg, mb, rb, rh,
        )
        k4 = _syrinx_trachea_oec_ode(
            state + dt * k3,
            alpha, beta, gamma, pout, dpout, ch, mg, mb, rb, rh,
        )
        state += dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        
        pi[t], pb[t], _, _ = _trachea_output(
            t,
            _syrinx_ode(state[0], state[1], alpha, beta, gamma)[1],
            alpha_mean,
            dt,
            delay_steps,
            reflection,
            pi,
            pb,
        )
        output[control_index] = rb * state[5]

    return output

@njit(cache=True)
def rk4_syrinx_oec(
    control_alpha,
    control_beta,
    tmax,
    ovsr,
    dt,
    gamma,
    ch,
    mg,
    mb,
    rb,
    rh,
):
    state = 1e-4 * np.array([1e2, 1e1, 1.0, 1.0, 1.0])
    output = np.zeros(tmax // ovsr + 1, dtype=np.float64)

    for t in range(tmax):
        control_index = t // ovsr
        alpha = control_alpha[control_index]
        beta = control_beta[control_index]

        k1 = _syrinx_oec_ode(
            state,
            alpha, beta, gamma
        )
        k2 = _syrinx_oec_ode(
            state + 0.5 * dt * k1,
            alpha, beta, gamma
        )
        k3 = _syrinx_oec_ode(
            state + 0.5 * dt * k2,
            alpha, beta, gamma,
        )
        k4 = _syrinx_oec_ode(
            state + dt * k3,
            alpha, beta, gamma,
        )
        state += dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        output[control_index] = rb * state[4]

    return output


#%%
class Organ(ABC):
    symbols_str: str
    symbols_array: list
    
    def __init__(
        self,
        fs: list[str],
        params: dict[str, float] = ZF_PARAMS
    ):
        self.params = params
        self.fs = fs

    @abstractmethod
    def update(self, args, **params):
        pass
#%%
class Syrinx(Organ):
    # bifurcation saddle nodes and array length
    # missing add the computation automatically
    _N = 1000
    _mu2_beta = -2.5 # compute automatically
    _mu1_alpha = 1/3
    _mu_parameters = (_mu1_alpha, _mu2_beta)
    _fs: list[str] = [
        "ys",
        "(-alpha-beta*xs-xs**3+xs**2)*gamma**2 - (xs+1)*gamma*xs*ys"
    ]
    
    def __init__(self, 
        fs: list[str] = _fs,
        params: dict[str, float] = ZF_PARAMS,
    ):
        symbols_str: str = "xs, ys, alpha, beta, gamma"
        """
        Syrinx model equations
        """
        self.gamma = params['gm']

        # equation string evaluation

        # Equations symbols
        self.symbols_list = symbols(symbols_str)
        self.xs = xs = self.symbols_list[0]
        self.ys = ys = self.symbols_list[1]
        self.alpha = alpha = self.symbols_list[2]
        self.beta = beta = self.symbols_list[3]
        self.gamma_symbol = gamma = self.symbols_list[4]

        equation_symbols = {
            "xs": self.xs,
            "ys": self.ys,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
        }
        self.f1_eq = sympify(fs[0], locals=equation_symbols)
        self.f2_eq = sympify(fs[1], locals=equation_symbols)
        # equations lambdified functions
        dynamic_symbols = [self.xs, self.ys, self.alpha, self.beta]
        self.f1 = lambdify(dynamic_symbols, self.f1_eq)
        self.f2 = lambdify(dynamic_symbols, self.f2_eq)

    def bifurcation_curves(self):
        beta_bif = np.linspace(self._mu2_beta, self._mu1_alpha, self._N)

        x01 = solveset(self.f1_eq, self.ys).union(solveset(self.f1_eq, self.xs))
        f2_x01 = self.f2_eq.subs(self.ys, x01.args[0])

        f = solveset(f2_x01, self.alpha)
        g = self.alpha

        df = f.args[0].diff(self.xs) # type: ignore
        dg = g.diff(self.xs)

        roots_bif = solveset(df-dg, self.xs)
        
        mu1_curves = []
        for ff in roots_bif.args:
            # root evaluatings beta
            mu1 = np.zeros(self._N, dtype=float)
            x_root = np.zeros(self._N, dtype=float)
            for i in range(self._N):
                x_root[i] = ff.subs(self.beta, beta_bif[i])
                mu1[i] = f.subs([(self.beta,beta_bif[i]), (self.xs,x_root[i])]).args[0]
            mu1_curves.append(np.array(mu1, dtype=float))
        mu1_curves = np.array(mu1_curves)

        return beta_bif, mu1_curves
        
    def update(self, t, control_var, v, dv, indexes=[0, 1]):
        alpha, beta = control_var
        x, y = v[indexes[0]], v[indexes[1]]
        
        dv[indexes[0]] = self.f1(x, y, alpha[t], beta[t])
        dv[indexes[1]] = self.f2(x, y, alpha[t], beta[t])

        return dv

    def correct_fstr(self, f: str) -> str:
        """
        Corrects the function string to ensure proper evaluation.
        """
        f = f.replace("xs", "x").replace("ys", "y").replace("alpha", '\\alpha').replace("beta", '\\beta').replace("gamma", '\\gamma').replace('**', '^')
        return f
#%%
class Trachea(Organ):
    def __init__(self, tmax, dt, params: dict[str, float] = ZF_PARAMS):
        """
        Trache model equations
        """
        self.dt = dt
        self.tmax = tmax

        self.r = params['r']
        self.L = params['L'] 
        # trachea pressure pback and pin vectors initialization
        self.pi = np.zeros(self.tmax) # input pressure
        self.pb = np.zeros(self.tmax) # pressure back
        # self.pout = np.zeros(self.tmax) # output pressure

    def update(self, t, control_var, dv, indexes=[1]): # t = t//ovsr
        alpha, _ = control_var
        y = dv[indexes[0]]
  
        self.pbold = self.pb[t]
        alpha_mean = alpha[:t].mean()
        A = 0 if isnan(alpha_mean) else alpha_mean
        # Pin(t) = Ay(t) + pback(t-L/C) = Signal_env*v[1] + pb[t-L/C/dt]
        self.pi[t] = A*y + self.pb[t-int(self.L/_C/self.dt)]
        # Pressure back: -rPin(t-L/C)
        self.pb[t] = -self.r*self.pi[t-int(self.L/_C/self.dt)]
        # Pout = (1-r)Pin(t-L/C)
        pout = (1-self.r)*self.pi[t-int(self.L/_C/self.dt)]
        # pout derivative using finite difference
        dpout = (self.pb[t]-self.pbold) / self.dt # dpout
        
        return pout, dpout
#%%
class OEC(Organ):
    _fs: list[str] = [
        "i2",
        "-(1/Ch/MG)*i1 - Rh*(1/MB+1/MG)*i2 " +
        "+ (1/MG/Ch+Rh*RB/MG/MB)*i3 + (1/MG)*dpout" +
        " + (Rh*RB/MG/MB)*pout", # dpout = dv[2]
        "-(MG/MB)*i2 - (Rh/MB)*i3 + (1/MB)*pout"
    ]
    __symbols_str: str = "i1, i2, i3, Ch, MG, MB, RB, Rh, pout, dpout"

    def __init__(
            self,
            fs: list[str] = _fs,
            params: dict[str, float] = ZF_PARAMS,
        ):
        """
        OEC model equations
        """

        # Phenomenological parameters
        self.Ch = params['Ch']
        self.MG = params['MG']
        self.MB = params['MB']
        self.RB = params['RB']
        self.Rh = params['Rh']

        # Equations symbols
        self.symbols_list = symbols(self.__symbols_str)
        self.i1= self.symbols_list[0]
        self.i2= self.symbols_list[1]
        self.i3= self.symbols_list[2]
        self.pout_symbol= self.symbols_list[8]
        self.dpout_symbol= self.symbols_list[9]

        # String to equation evaluation
        equation_symbols = {
            "i1": self.i1,
            "i2": self.i2,
            "i3": self.i3,
            "Ch": self.Ch,
            "MG": self.MG,
            "MB": self.MB,
            "RB": self.RB,
            "Rh": self.Rh,
            "pout": self.pout_symbol,
            "dpout": self.dpout_symbol,
        }
        self.f1_eq = sympify(fs[-3], locals=equation_symbols)
        self.f2_eq = sympify(fs[-2], locals=equation_symbols)
        self.f3_eq = sympify(fs[-1], locals=equation_symbols)
        # equations lambdified functions
        args = [
            self.i1, self.i2, self.i3,
            self.pout_symbol,
            self.dpout_symbol,
        ]
        self.f1 = lambdify(args, self.f1_eq)
        self.f2 = lambdify(args, self.f2_eq)
        self.f3 = lambdify(args, self.f3_eq)
        # self._params = (Ch, MG, MB, RB, Rh)

    def update(self, control_var, v, dv, indexes=[0, 1, 2]): # pout
        # i1, i2, i3 = v
        # pout, dpout = control_var

        # ----------------------- OEC EDOs -----------------------
        dv[indexes[0]] = self.f1(*v, *control_var) # i1
        dv[indexes[1]] = self.f2(*v, *control_var) # i2
        dv[indexes[2]] = self.f3(*v, *control_var) # i3

        return dv

#%%
class Model(ABC):
    """
    Base model class for the motor gesture of birdsongs.
    """
    
    _N: int = 1000 # number of time steps
    """int : Number of time steps for the model.
    """
    _mu_parameters: tuple[float, ...]

    def __init__(
            self,
            # syllable, # Syllable (sr and size)
            ovsr: int = 20, # oversample
            prct_noise: int = 0 # percentage of noise in the model
        ):
        self.organs = []
        self.ovsr = ovsr
        self.prct_noise = prct_noise 

    def ode(
            self,
            organs: list[type[Organ]] | list[str] = ["syrinx", "trachea", "oec"],
            size: int = 44100,
            sr: int = 44100, 
            fs: list[str] = Syrinx()._fs + OEC()._fs,
            params: dict[str, float] = ZF_PARAMS,
        ):

        ode_sys = ODESystem(organs, size=size, sr=sr, ovsr=self.ovsr, prct_noise=self.prct_noise, fs=fs, params=params)
        self.organs = ode_sys.organs # save organs in the model instance

        return ode_sys.ode()

    @abstractmethod
    def control_parameters(self): # alpha_beta
        pass
    
    @abstractmethod
    def motor_gesture(self):
        pass

    @abstractmethod
    def synthetize(self):
        pass

#%%
class ODESystem:
    __V_MAX: float = 5e6 # model constraint, max vel
    
    def __init__(
        self,
        organs: list[type[Organ]] | list[str] = [Syrinx],
        size: int = 44100,
        sr: int = 44100, 
        ovsr: int = 20, # oversample
        prct_noise: int = 0, # percentage of noise in the model
        fs: list[str] = Syrinx()._fs + OEC()._fs,
        params: dict[str, float] = ZF_PARAMS,
    ) -> None:
    
        self.sr = sr
        self.ovsr = ovsr
        self.prct_noise = prct_noise
        self.params = params
        self.organs = []

        # Array properties for the ouput
        self.N = self.ovsr * self.sr           # Total No of samples
        self.dt = 1 / self.N                   # time step in seconds by samples
        self.tmax = int(size * self.ovsr - 1)  # maximum time in samples
        self.out = np.zeros(size)              # output pressure, FINAL SIGNAL

        if not organs:
            raise ValueError("At least one Syrinx organ must be provided.")

        requested_organs = []
        for organ in organs:
            if organ is Syrinx or organ == "syrinx":
                organ_type = Syrinx
            elif organ is Trachea or organ == "trachea":
                organ_type = Trachea
            elif organ is OEC or organ == "oec":
                organ_type = OEC
            else:
                raise ValueError(f"Unsupported organ: {organ!r}")

            if organ_type not in requested_organs:
                requested_organs.append(organ_type)

        if Syrinx not in requested_organs:
            raise ValueError("At least one Syrinx organ must be provided.")

        for organ_type in (Syrinx, Trachea, OEC):
            if organ_type not in requested_organs:
                continue
            if organ_type is Syrinx:
                self.syrinx = Syrinx(fs, params)
                self.organs.append(self.syrinx)
            elif organ_type is Trachea:
                self.trachea = Trachea(self.tmax, self.dt, params=params)
                self.organs.append(self.trachea)
            else:
                self.oec = OEC(fs, params)
                self.organs.append(self.oec)

    def ode(self): # type[Callable]
        organ_types = tuple(type(organ) for organ in self.organs)

        if organ_types == (Syrinx,):
            return self.sound_source_ode
        if organ_types == (Syrinx, Trachea):
            return self.sound_source_trachea_ode
        if organ_types == (Syrinx, OEC):
            return self.sound_source_oec_ode
        if organ_types == (Syrinx, Trachea, OEC):
            return self._sound_source_trachea_oec_ode

        raise ValueError(
            "Invalid combination of organs. Must contain a Syrinx at least, "
            "and a Trachea, and/or OEC."
        )
        
    def _sound_source_trachea_oec_ode(
            self, 
            control_var: list[np.ndarray]
        ) -> np.ndarray:
        """
        System composed just by the sound source (syrinx) and the trachea
        """
        delay_steps = int(self.trachea.L / (_C * self.dt))
        raw_signal = rk4_syrinx_trachea_oec(
            control_var[0],
            control_var[1],
            self.tmax,
            self.ovsr,
            self.dt,
            self.syrinx.gamma,
            delay_steps,
            self.trachea.r,
            self.oec.Ch,
            self.oec.MG,
            self.oec.MB,
            self.oec.RB,
            self.oec.Rh,
        )
        self.out = raw_signal[:self.out.size]
        return normalize(self.out, max_amp=1.0)

    def sound_source_trachea_oec_ode(
                self, 
                control_var: list[float]
            ) -> np.ndarray:
            """
            System composed just by the sound source (syrinx) and the trachea
            """
            t = 0 # rk4 time step
    
            # system array initialization
            self.v = 1e-4 * np.array([1e2, 1e1, 1, 1, 1, 1]) # v0
            self.vs = [self.v] # np.zeros(tmax)
    
            # Ordinary Differential Equations (ODEs) system
            syrinx = self.syrinx
            trachea = self.trachea
            oec = self.oec
            ovsr = self.ovsr
    
            def ODEs(v: np.ndarray) -> np.ndarray:
                t_ovsr = t // ovsr
                dv = np.zeros(6)
    
                # ------------------------- SYRINX ------------------------
                dv[:2] = syrinx.update(
                    t_ovsr,
                    control_var,
                    v,
                    dv[:2],
                    indexes=(0, 1),
                )
                # ------------------------- TRACHEA ------------------------
                pout, dpout = trachea.update(t_ovsr, control_var, dv, indexes=(1,))
                dv[2] = dpout
                # ------------------------- OEC EDOs -----------------------
                dv[3:] = oec.update([pout, dpout], v[3:], dv[3:])
                
                return dv
    
            # ----------------------- Update EDOs Variables ----------------------
            while (t < self.tmax) and (np.abs(self.v[1]) < self.__V_MAX):
                self.v = rk4(ODEs, self.v, self.dt)              # RK4 step
                self.vs.append(self.v)                           # save step # vs[t] = v
                self.out[t // ovsr] = oec.RB * self.v[-1]  # update output signal (synthetic)
                t += 1
    
            return normalize(self.out, max_amp=1.0)
        
    
    def sound_source_ode(
            self, 
            control_var: list[float]
        ) -> np.ndarray:
        """
        System composed just by the sound source (syrinx)
        """
        t = 0 # rk4 time step
        
        # system array initialization
        self.v = 1e-4 * np.array([1e2, 1e1]) # v0
        self.vs = [self.v] # np.zeros(tmax)

        # Ordinary Differential Equations (ODEs) system
        def ODEs(v: np.ndarray) -> np.ndarray:
            t_ovsr = t // self.ovsr
            dv = np.zeros(2)

            # ------------------------- SYRINX ------------------------
            dv[[0, 1]] = self.syrinx.update(t_ovsr, control_var, v, dv, indexes=[0, 1]) # [x, y]
            
            return dv

        # ----------------------- Update EDOs Variables ----------------------
        while (t < self.tmax): # and (np.abs(self.v[1]) < self.__V_MAX):
            self.v = rk4(ODEs, self.v, self.dt)           # RK4 step
            self.vs.append(self.v)                        # save step # vs[t] = v
            self.out[t//self.ovsr] = self.v[-1]  # update output signal (synthetic)
            t += 1
            
            # print(t, self.v, self.dt)

        return normalize(self.out, max_amp=1.0)

    def sound_source_trachea_ode(
            self, 
            control_var: list[float]
        ) -> np.ndarray:
        """
        System composed just by the sound source (syrinx) and the trachea
        """
        t = 0 # rk4 time step
        
        # system array initialization
        self.v = 1e-4 * np.array([1e2, 1e1, 1]) # v0
        self.vs = [self.v] # np.zeros(tmax)

        # beta_bif, mu1_curves = syrinx.bifurcation_Curves()
        # Ordinary Differential Equations (ODEs) system
        indexes = [0, 1]
        def ODEs(v: np.ndarray) -> np.ndarray:
            t_ovsr = t // self.ovsr
            dv = np.zeros(3)

            # ------------------------- SYRINX ------------------------
            dv[indexes] = self.syrinx.update(t_ovsr, control_var, v, dv[indexes], indexes=indexes) # [x, y]
            # ------------------------- TRACHEA ------------------------
            pout, dpout = self.trachea.update(t_ovsr, control_var, dv, indexes=[1])
            dv[2] = dpout
            
            return dv

        # ----------------------- Update EDOs Variables ----------------------
        while (t < self.tmax) and (np.abs(self.v[1]) < self.__V_MAX):
            self.v = rk4(ODEs, self.v, self.dt)  # RK4 step
            self.vs.append(self.v)               # save step # vs[t] = v
            self.out[t//self.ovsr] = self.v[-1]  # update output signal (synthetic)
            t += 1

        return normalize(self.out, max_amp=1.0)

    def sound_source_oec_ode(
            self, 
            control_var: list[np.ndarray]
        ) -> np.ndarray:
        """
        System composed just by the sound source (syrinx) and the OEC
        """
        t = 0 # rk4 time step
        
        # system array initialization
        self.v = 1e-4 * np.array([1e2, 1e1, 1, 1, 1]) # v0
        self.vs = [self.v] # np.zeros(tmax)

        # beta_bif, mu1_curves = syrinx.bifurcation_Curves()
        # Ordinary Differential Equations (ODEs) system
        indexes = [0, 1]
        indexes_oec = [2, 3, 4]
        def ODEs(v: np.ndarray) -> np.ndarray:
            t_ovsr = t // self.ovsr
            dv = np.zeros(5)

            # ------------------------- SYRINX ------------------------
            dv[indexes] = self.syrinx.update(t_ovsr, control_var, v, dv[indexes], indexes=indexes) # [x, y]
            # ------------------------- OEC EDOs -----------------------
            alpha_mean = control_var[0][:t_ovsr].mean()
            A = 0 if isnan(alpha_mean) else alpha_mean
            pout = dv[1] # output pressure from syrinx
            dpout = (pout-v) / self.dt # dpout
            dv[indexes_oec] = self.oec.update([pout, dpout], v[indexes_oec], dv[indexes_oec]) # [i1, i2, i3]
            
            return dv

        # ----------------------- Update EDOs Variables ----------------------
        while (t < self.tmax) and (np.abs(self.v[1]) < self.__V_MAX):
            self.v = rk4(ODEs, self.v, self.dt)           # RK4 step
            self.vs.append(self.v)                        # save step # vs[t] = v
            self.out[t//self.ovsr] = self.oec.RB*self.v[-1]  # update output signal (synthetic)
            t += 1

        return normalize(self.out, max_amp=1.0)





