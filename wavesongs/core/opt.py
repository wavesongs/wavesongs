import numpy as np
import matplotlib.pyplot as plt



def create_grid(
        sr: int = 44100,
        gamma: float = 0.1,
        dalpha: int = 100, alpha_lim : tuple = (-0.05, 0.2),
        dbeta: int = 100, beta_lim : tuple = (-0.2, 1.5),
    ):
    # 1. Create 1D coordinate arrays
    alpha = np.linspace(alpha_lim[0], alpha_lim[1], dalpha)
    beta = np.linspace(beta_lim[0], beta_lim[1], dbeta)

    # 2. Generate the 2D coordinate mesh matrices
    ALPHA, BETA = np.meshgrid(alpha, beta)
