wavesongs.core.solver
=====================

.. py:module:: wavesongs.core.solver


Functions
---------

.. autoapisummary::

   wavesongs.core.solver.augmente_beta
   wavesongs.core.solver.augmente_data
   wavesongs.core.solver.optimal_beta_curve
   wavesongs.core.solver.transform_composition
   wavesongs.core.solver.transform_fitting


Module Contents
---------------

.. py:function:: augmente_beta(syllable, model, beta, alpha_0=0.5, N=10, random_per=1, mode='composition', poly_deg=5, no_params=4, umbral_FF=1.0, n_fft=512, ff_method='yin', verbose=True, plot=True, legend=True, save_audio=True, save_df=True, save_img=False)

.. py:function:: augmente_data(syllable, model, metadata, alpha_0=1e-05, mode='fitting', N=1, beta_N=10, poly_deg_beta=5, random_per=5, no_params=2, umbral_FF=1.4, n_fft=512, ff_method='yin', verbose=True, plot=True, save_audio=True, save_df=True)

.. py:function:: optimal_beta_curve(syllable, model, alpha_0=1e-05, beta_max=2, beta_N=50, duration=0.1, sr=44100, umbral_FF=1.4, n_fft=512, ff_method='yin', poly_deg=2, verbose=True, plot=True)

   Find the bifurcation curve for a given model and alpha_0 value.
   Returns the minimum beta value for oscillation. The grid is computed by creating
   lines of the control parameters and generating synthetic syllables.

   Parameters:
   model : Model
       The bird vocalization model.
   alpha_0 : float
       The alpha parameter value. Small values produce less harmonics.
   beta_max : float
       The maximum beta value to consider.
   beta_N : int
       The number of beta values to evaluate.
   duration : float
       Duration of the synthetic syllable in seconds.
   sr : int
       Sampling rate for the synthetic syllable.
   verbose : bool
       If True, prints computation time.


.. py:function:: transform_composition(params0, time, random_per=10, no_params=2)

.. py:function:: transform_fitting(params0, time, random_per=1, no_params=4)

