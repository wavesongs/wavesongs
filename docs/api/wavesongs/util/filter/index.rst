wavesongs.util.filter
=====================

.. py:module:: wavesongs.util.filter


Functions
---------

.. autoapisummary::

   wavesongs.util.filter.median_clipping
   wavesongs.util.filter.percentile


Module Contents
---------------

.. py:function:: median_clipping(S, multiplier=3)

   AppApply binary thresholding to the spectrogram S using the equation:
   S[r, c] > 3 * max(median(S[r, :]), median(S[:, c]))

   :param S: 2D spectrogram array.
   :type S: ndarray
   :param multiplier: Threshold multiplier (default 3).
   :type multiplier: float

   :returns: Binary mask (0 or 1).
   :rtype: mask (ndarray)


.. py:function:: percentile(S, window_shape=(64, 100), stride=(32, 50), percentile=80)

   Apply a percentile-based nonlinear filter mask to a spectrogram.

   :param S: Input spectrogram
   :type S: 2D np.ndarray
   :param window_shape: Size of the window (rows, cols), e.g., (64, 100)
   :type window_shape: tuple
   :param stride: Stride for moving window (rows, cols), e.g., 50% overlap → (32, 50)
   :type stride: tuple
   :param percentile: Percentile value (e.g., 80 for P80)
   :type percentile: float

   :returns: Binary mask after applying percentile threshold
   :rtype: mask (2D np.ndarray)


