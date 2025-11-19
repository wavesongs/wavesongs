from abc import ABC, abstractmethod

class Model(ABC):
    """
    Base model class for the motor gesture of birdsongs.
    """
    
    _PARAMS: dict
    r"""dict : Model parameters
    """
    _F1: str
    _F2: str

    _N: int = 1000 # number of time steps
    """int : Number of time steps for the model.
    """

    _V_MAX: float = -5e6 # model constraint
    """float : Maximum labia walls velocity.
    """

    _ovsr: int = 20 # oversampling rate for the model
    _prct_noise: int = 0 # percentage of noise in the model

    _mu_parameters: tuple[float, ...]
    _Z: dict

    @abstractmethod
    def bifurcation_ode(self):
        pass
    
    @abstractmethod
    def control_parameters(self): # alpha_beta
        pass
    
    @abstractmethod
    def motor_gesture(self):
        pass

    @abstractmethod
    def dict_z(self):
        pass
    
    @abstractmethod
    def dict_params(self):
        pass

    @abstractmethod
    def synthetize(self):
        pass
    
#%%
class Solver(ABC):
    """
    Base solver class for the motor gesture of birdsongs.
    """
    
    def __init__(self, model: Model):
        self.model = model
    
    # @abstractmethod
    # def optimize(self):
    #     pass
    
    # @abstractmethod
    # def solve(self):
    #     pass
    
    # @abstractmethod
    # def get_results(self):
    #     pass