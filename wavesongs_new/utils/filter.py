"""

"""
import numpy as np

#%%
def percentile(S, window_shape=(64, 100), stride=(32, 50), percentile=80):
    """
    Apply a percentile-based nonlinear filter mask to a spectrogram.

    Parameters:
        S (2D np.ndarray): Input spectrogram
        window_shape (tuple): Size of the window (rows, cols), e.g., (64, 100)
        stride (tuple): Stride for moving window (rows, cols), e.g., 50% overlap → (32, 50)
        percentile (float): Percentile value (e.g., 80 for P80)

    Returns:
        mask (2D np.ndarray): Binary mask after applying percentile threshold
    """
    rows, cols = S.shape
    wr, wc = window_shape
    sr, sc = stride

    mask = np.zeros_like(S, dtype=bool)
    counts = np.zeros_like(S, dtype=int)
    passes = np.zeros_like(S, dtype=int)

    # Slide the window
    for r in range(0, rows - wr + 1, sr):
        for c in range(0, cols - wc + 1, sc):
            patch = S[r:r+wr, c:c+wc]
            threshold = np.percentile(patch, percentile)
            local_mask = patch > threshold

            # Update mask only where pixels exceed threshold
            # Accumulate how many times each pixel passes the threshold
            counts[r:r+wr, c:c+wc] += 1
            passes[r:r+wr, c:c+wc] += local_mask.astype(int)

    # Strict condition: must pass all windows it belongs to
    mask = (passes == counts) & (counts > 0)
    return mask.astype(np.uint8)

#%%
def median_clipping(S, multiplier=3):
    """
    AppApply binary thresholding to the spectrogram S using the equation:
    S[r, c] > 3 * max(median(S[r, :]), median(S[:, c]))

    Parameters:
        S (ndarray): 2D spectrogram array.
        multiplier (float): Threshold multiplier (default 3).

    Returns:
        mask (ndarray): Binary mask (0 or 1).
    """
    # Compute row and column medians
    row_medians = np.median(S, axis=1)  # shape: (rows,)
    col_medians = np.median(S, axis=0)  # shape: (cols,)

    # Broadcast to build threshold matrix
    threshold = multiplier * np.maximum(row_medians[:, np.newaxis], col_medians[np.newaxis, :])

    # Apply threshold
    mask = (S > threshold).astype(np.uint8)

    return mask
