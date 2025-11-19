"""
Pure Synthetic Syllables
========================


"""

# %%
# Synthetic Objects
# -------------------
from wavesongs.utils.plot import plot
from wavesongs.object import Synthetic
from wavesongs.data import ProjDirs

# Define the plotter
plotter = plot.set_plotter(library="plotly")

proj_dirs = ProjDirs(audios="./assets/audios",
                     results="./assets/results_pure_synthetic")

synthetic = Synthetic(duration=1, proj_dirs=proj_dirs)
synthetic.initialize()
# %%
# The default function is a constant function of value 1, but you can give any
# array you want, do not forget to add the sampling rate
import numpy as np
sr = 44100
t = np.linspace(0, 1, sr)
x = np.sin(2 * np.pi * 2000 * t) + np.sin(2 * np.pi * 3500 * t)

synthetic.initialize(x)
# %%
# Compute acoustical features and plot the spectrogram synthetic sound
synthetic.acoustical_features(umbral_FF=1.4, n_fft=512, ff_method="yin")
fig = plotter.spectrogram(synthetic)
fig
# %%
# Model
# ------
from wavesongs.core.bird import Model

model = Model()

# Define control parameters and generate gesture
z = {"a0": 0.05, "b0": 0.1, "b1": -0.25, "b2": 0}
curves = model.control_parameters(synthetic, z, beta_mode="poly")
synthetized = model.motor_gesture(synthetic, curves)

# Plot motor gesture
plotter.alpha_beta(synthetized, save=False, show=False)
# %%
# Result
# ------

# Plot waveforme from synthetized sound
synthetized.acoustical_features(umbral_FF=1.4, n_fft=512, ff_method="yin")
plotter.spectrogram(synthetized, save=False)
# %%
fig = plotter.spectrogram(synthetized, type="3d")
fig