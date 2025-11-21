"""
Syllable Example
================

This example shows how to segment bird song syllables using plotly for plotting.
"""


# %%
# Project directories
# -------------------
# The `ProjDirs` class is used to manage directories for audio files and results.
# It can be customized to point to your specific directories.

from wavesongs.data import ProjDirs

proj_dirs = ProjDirs(audios="../assets/audios",
                     results="../assets/results")
proj_dirs.find_audios(pretty=True) # Check files in the audio directory

# %%
# Syllable definition
# -------------------
# The `Syllable` class is used to define a syllable from an audio file.
# It requires the file ID and the time limits for the syllable.
# The `proj_dirs` argument is used to specify the directories for audio files and results.
from wavesongs.object import Syllable

copeton_1 = Syllable(file_id="574179401", tlim=(0.6, 3), proj_dirs=proj_dirs)
# %%
# The `Syllable` object can be used to access various properties of the syllable,
# such as the audio file, time limits, and other attributes.
copeton_1.acoustical_features(umbral_FF=1.4, n_fft=512)

# %%
# Visualization
# -------------
# The `set_plotter` function is used to set the plotting backend.
# In this case, we are using Plotly for visualization.
# The `spectrogram` method of the `Syllable` class is used to plot the spectrogram of the syllable.
# The `type` parameter can be set to "2d" or "3d" for different visualizations.
from wavesongs.utils.plot import set_plotter

plotter = set_plotter("plotly")
fig = plotter.spectrogram(copeton_1, type="3d")
fig
# %%
# Spectrogram
# -----------
plotter.spectrogram(copeton_1, type="2d", auxiliar="both",
                        mode="max", waveforme=True, grid=True, ff=True)
