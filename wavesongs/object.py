"""
Store and compute acoustica features from base type.
"""

import numpy as np
import pandas as pd

from dataclasses import dataclass, field

from os.path import basename, normpath

# acoustical features
from librosa import (
    stft,
    reassigned_spectrogram,
    amplitude_to_db,
    fft_frequencies,
    times_like,
    yin,
    load,
    pyin
)

from librosa.feature import (
    spectral_centroid,
    mfcc,
    rms,
    melspectrogram
)

# sound playing
from IPython.display import Audio

# image processing 
from scipy.ndimage import (
    binary_dilation,
    binary_closing,
    gaussian_filter,
    generate_binary_structure,
    label
)

# filters
from wavesongs.utils.filter import median_clipping, percentile

# sound processing
from maad.sound import (
    normalize,
    write,
    normalize,
    envelope
)

# mathematical functions
from numpy.linalg import norm
from scipy.interpolate import interp1d

from .data.manager import ProjDirs
# typing
from typing import Callable, Any, Literal


# %%
def _is_notebook() -> bool:
  try:
    from IPython import get_ipython # type: ignore
    shell = get_ipython()
    if shell is None:
      return False
    if shell.__class__.__name__ == "ZMQInteractiveShell":
      return True  # Jupyter notebook or qtconsole
    else:
      return False  # Other type (Terminal, etc.)
  except ImportError:
    return False

#%%
@dataclass
class Base:
    sr: int

    ff_method: Literal["yin", "pyin", "imgpro"]
    region_mask: np.ndarray
    
    ff_time: np.ndarray
    ff_fun: Any
    SCI: np.ndarray

    time: np.ndarray

    t0_bs: float = 0.0
    id: str = "base"
    #%%
    """
    Object class to store, characterize, and compare syllables. 
    See :func:`~wavesongs.object.Syllable.__init__`. :class:`~wavesongs.object.Song`
    
    Parameters
    ----------
        proj_dirs : ProjDirs | None 
            Object to manage project directories
        song : Syllable | Song | None
            Object
        params : dict | None
            Diccionary with all or some constat of the physical
            model motor gestures
        tlim : tuple
            Time range
        flim : tuple
            Frequency range
        sr : int
            Sample rate
        no_syllable : int 
            Sylalble number in song
        id : str
            Type of the object, "syllable" or "synth-syllable"
        info : dict
            Audio metadata about the audio.
        type : str
            A short description about the part, theme or trill, and the behaviour of the
            fundamental frequency: plane, up, down, up-down, down-up, and complex. 
            Template: "{part}-{behaviour}". Example: theme-up 
            
    
    Raise
    -----
        adasdad

    Note
    ----
        asdasd    
    
    Warning
    -------
        adasdasd

    Examples
    --------
        >>> 
    """ 
    #%%
    def __init__(
            self,
            file_id: str,
            proj_dirs: ProjDirs = ProjDirs(),
            sr: int = 44100,
            tlim: tuple[float, float] = (0, 1000),
            metadata: dict = {
                "type": "",
                "no_syllable":  0,
            },
        ):
        """_summary_

        Args:
            

        Raises:
            Exception: _description_
        """
        self.metadata = metadata
        self.no_syllable = metadata.get("no_syllable", 0)
        self.type = metadata.get("type", "")
        
        # self.region_mask = np.ndarray([0,0])

        self.sr = sr
        self.tlim = tlim
        self.file_id = file_id
        self.proj_dirs = proj_dirs

    #%%
    def _envelope(self, s: np.ndarray, sr: int, Nt: int) -> np.ndarray:
        """
        
        Parameters
        ----------
            s : np.array
                Audio amplitude array
            sr : int
                Sample rate
            Nt : int
        
        Return
        ------
            s_env_interpolated : np.array 
        
        Example
        -------
            >>>
        """
        time = np.linspace(0, len(s)/sr, len(s))
        s_env = envelope(s, Nt=Nt) 
        t_env = np.arange(0, len(s_env), 1) * np.float16(len(s) / sr / len(s_env))
        t_env[-1] = time[-1] 
        fun_s = interp1d(t_env, s_env)
        s_env_interpolated = np.array(fun_s(time))
        return s_env_interpolated

    #%%
    def initialize(self):
        """
        Initialize the object with audio file and metadata.
        """
        
        self.file_path = self.proj_dirs.find_audio(self.file_id)
        self.file_name = basename(normpath(self.file_path))

        s, _ = load(self.file_path, sr=self.sr, mono=True)
        s = s[int(self.tlim[0]*self.sr) : int(self.tlim[1]*self.sr)]

        self.t0_bs = 0
        self.t0 = self.tlim[0]
        
        self.s = normalize(s, max_amp=1.0)
        self.time_s = np.linspace(0, len(self.s)/self.sr, len(self.s))
        
    #%%
    def acoustical_features(
        self,
        n_fft: int = 512,
        hop_length: int | None = None,
        win_length: int | None = None,
        umbral_FF: float = 1,
        ff_method: Literal["yin", "pyin", "imgpro"] = "yin",
        flim: tuple[float, float] = (1e-2, 22e3),
        Nt: int = 10,
        center: bool = False,
        llambda: float = 1.5,
        n_mfcc: int = 4,
        n_mels: int = 4,
        stft_window: str = "hann",
        pad_mode: Literal['constant', 'edge', 'linear_ramp', 'reflect', 'symmetric', 'empty'] = "constant",
    ) -> None:
        """
        Coputing acoustical tempo-spectral variables
        
        Parameters
        ----------
            n_fft : int
                FFT window size.
            llambda : float

            hop_length: int, optional
                Number of audio samples between adjacent STFT columns.

            win_length : int, optional
                Length of the windowed signal after padding with zeros

            center : bool = False

            umbral_FF : int

            ff_method : str

            Nt : int

            n_mfcc : int

            n_mels : int

            stft_window : str

        Return
        ------
            None

        Examples
        --------
            >>>
        """
        self.stft_window = stft_window
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.flim = flim if flim is not None else (0.1, self.sr/2)
        self.n_fft = n_fft
        self.Nt = Nt
        
        self.ff_method = ff_method
        self.umbral_FF = umbral_FF
        self.llambda = llambda
        self.center = center
        self.envelope = self._envelope(self.s, int(self.sr), self.Nt)

        self.time0 = np.linspace(0, len(self.s)/self.sr, len(self.s))
        # self.time_s = np.linspace(0, len(self.s)/self.sr, len(self.s))
        self.T = self.s.size / self.sr
        
        self.t_interval = np.array([self.time_s[0], self.time_s[-1]])
        self.t_interval += self.t0_bs

        self.win_length = self.n_fft if win_length is None else win_length
        self.hop_length = self.win_length // 4 if hop_length is None else hop_length
        self.overlap = self.hop_length / self.n_fft

        # resolution
        self.f_resolution = self.sr / self.n_fft
        self.time_resolution = self.hop_length / self.sr
        # ------------- ACOUSTIC FEATURES -------------------------------
        self.stft = stft(y=self.s,
                         n_fft=self.n_fft,
                         hop_length=self.hop_length,
                         win_length=self.n_fft,
                         window=self.stft_window,
                         center=self.center,
                         dtype=float,
                         pad_mode=pad_mode)
        freqs, times, mags = reassigned_spectrogram(
                                self.s,
                                sr=self.sr,
                                S=self.stft,
                                n_fft=self.n_fft,
                                hop_length=self.hop_length,
                                win_length=self.win_length,
                                window=self.stft_window, 
                                center=self.center,
                                reassign_frequencies=True,
                                reassign_times=True,
                                ref_power=1e-06,
                                fill_nan=True,
                                clip=True,
                                dtype=float,
                                pad_mode=pad_mode
                             )
        self.Sxx_dB  = amplitude_to_db(mags, ref=np.max)
        self.freqs = freqs  
        self.times = times 
        self.Sxx = mags 
        
        # Means over time and frequency
        self.Sxx_ff_mean = np.mean(self.Sxx_dB, axis=1)
        self.Sxx_ff_max = np.max(self.Sxx_dB, axis=1)
        self.Sxx_time_mean = np.mean(self.Sxx_dB, axis=0)
        self.Sxx_time_max = np.max(self.Sxx_dB, axis=0)

        self.ff_coef = np.abs(self.stft)
        self.freq = fft_frequencies(sr=self.sr, n_fft=self.n_fft) 
        self.time = times_like(X=self.stft,
                               sr=self.sr,
                               hop_length=self.hop_length,
                               n_fft=self.n_fft) #, axis=-1
        self.time -= self.time[0]
        
        self.f_msf = np.array([
            norm(self.ff_coef[:, i] * self.freq, 1) / norm(self.ff_coef[:, i], 1)
            for i in range(self.ff_coef.shape[1])
        ])
        # [norm(self.ff_coef[:,i]*self.freq, 1)
        #               / norm(self.ff_coef[:,i], 1)
        #               for i in range(self.ff_coef.shape[1])]
        # self.f_msf = np.array(self.f_msf)
        
        # Other acoustical features
        self.centroid = spectral_centroid(
            y=self.s,
            sr=self.sr,
            S=self.ff_coef,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            freq=self.freqs,
            win_length=self.win_length, 
            window=self.stft_window,
            center=self.center,
            pad_mode=pad_mode
        )[0]
        self.mfccs = mfcc(
            y=self.s,
            sr=self.sr,
            S=self.stft,
            n_mfcc=self.n_mfcc,
            dct_type=2,
            norm='ortho',
            lifter=0
        )
        self.rms = rms(
            y=self.s,
            S=self.stft,
            frame_length=self.n_fft,
            hop_length=self.hop_length,
            center=self.center,
            pad_mode=pad_mode
        )[0]
        self.s_mel = melspectrogram(
            y=self.s,
            sr=self.sr,
            S=self.stft,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            window=self.stft_window,
            center=self.center,
            pad_mode=pad_mode,
            power=2.0,
            n_mels=self.n_mels,
            fmin=self.flim[0],
            fmax=self.flim[1]
        )
        # # ------------- Fundamental Frequency computing --------------
        if self.ff_method=="pyin":
            self.ff, _, _ = pyin(
                self.s,
                fmin=1.1*self.f_resolution,
                fmax=self.flim[1],
                sr=self.sr,
                frame_length=self.n_fft, 
                hop_length=self.hop_length,
                n_thresholds=100,
                beta_parameters=(2, 18), 
                boltzmann_parameter=2,
                resolution=0.1,
                max_transition_rate=35.92,
                switch_prob=0.01, 
                no_trough_prob=0.01,
                fill_na=0,
                center=self.center,
                pad_mode=pad_mode
            )
        elif self.ff_method=="yin":
            self.ff = yin(
                self.s,
                fmin=1.1*self.f_resolution,# flim[0],
                fmax=self.flim[1],
                sr=self.sr,
                frame_length=self.n_fft, 
                hop_length=self.hop_length,
                center=self.center,
                trough_threshold=self.umbral_FF,
                pad_mode=pad_mode
            )
        elif self.ff_method=="both":
            self.ff2, _, _ = pyin(
                self.s,
                fmin=1.1*self.f_resolution,
                fmax=self.flim[1],
                sr=self.sr,
                frame_length=self.n_fft, 
                hop_length=self.hop_length,
                n_thresholds=100,
                beta_parameters=(2, 18), 
                boltzmann_parameter=2,
                resolution=0.1,
                max_transition_rate=35.92,
                switch_prob=0.01, 
                no_trough_prob=0.01,
                fill_na=0,
                center=self.center,
                pad_mode=pad_mode
            )
            self.ff = yin(
                self.s,
                fmin=1.1*self.f_resolution,
                fmax=self.flim[1],
                sr=self.sr,
                frame_length=self.n_fft, 
                hop_length=self.hop_length,
                center=self.center,
                trough_threshold=self.umbral_FF,
                pad_mode=pad_mode
            )
        elif self.ff_method=="img_pro":
            raise Exception("Not implemented yet!")
        elif self.ff_method=="manual":
            raise Exception("Not implemented yet!")
        
        self.ff_time = np.linspace(0,self.time[-1], self.ff.size)
        self.ff_fun = interp1d(self.ff_time, self.ff)
        self.SCI = self.f_msf / self.ff_fun(self.time)
    #%%
    def region_dict(
        self,
        region_mask: np.ndarray,
        syllable_label: int,
        vocalization_label: int,
        id: Literal["fundamental", "harmonic"]= "fundamental"
    ) -> dict:
        region_dict = {
            "syllable_label": syllable_label, # syllable label
            "vocalization_label": vocalization_label, # vocalization label

            "mask": region_mask, # fundamental frequency mask
            "area": np.sum(region_mask), # area of the region
            "id": id,

            "t_ini": np.min(self.time[np.any(region_mask, axis=0)]) + self.t0, 
            "t_end": np.max(self.time[np.any(region_mask, axis=0)]) + self.t0,

            "f_ini": np.max(self.freq[np.any(region_mask, axis=1)]), 
            "f_end": np.min(self.freq[np.any(region_mask, axis=1)]),

            "mean_intensity": np.mean(self.Sxx[region_mask]), # mean intensity
            "mean_intensity_dB": np.mean(self.Sxx_dB[region_mask]), # mean intensity dB
        }

        region_dict["duration"] = region_dict["t_end"] - region_dict["t_ini"]
        region_dict["bw"] = np.abs(region_dict["f_end"] - region_dict["f_ini"])
        
        return region_dict
        # self.regions[syllable_label]["harmonic"] = self.harmonics if id == "fundamental" else []
        # self.regions[syllable_label]["fundamental"] = vocalization_label if id == "harmonic" else 0
        # self.regions[current_label]["type"] = 

    # More classes to deal with syllables
    def segmentation(
        self,
        mode: Literal["amplitude", "freq", "signal_pro", "ff", "region_growing"] = "amplitude",
        threshold_1: float = 0.2,
        threshold_2: float = 1, min_duration: float = 0.01,
        img_pro_params: dict = {
            "scalar": 3, # for the filter
            # "threshold": 1e-6, # PSD units
            # "pref": 34, # dB units
            "percentile": 80,
            "no_harmonics": 6,
            "min_area": 20, # pixels
            "min_duration": 9, # pixels
            "window_params": {"W": 64, "h":100},
            "stride": 2,
            "margin_pixels": 3,
            "times": 2, # for the model noisy
            "ff_computing": "yin",  # "yin", "pyin", "img_pro"
            "closing": 3,
        },
        region_growing_params: dict = {
            "threshold": 100,
            "ff": "yin",
        },
        verbose: bool = True,
    ):
        """
        1) Segmentation of acoustic signals from the noise back-
        ground: In the second segmentation step, to remove impulse
        noise and weak harmonics while leaving strong harmonics
        intact, we calculate the average intensity of the remaining
        blobs and discard those that have low intensity using a
        threshold of 10−6 . This value can be tuned to ﬁt different noise
        conditions, but we recommend it should not be less than 10−8
        or larger than 10−3 , corresponding to the sound level of 14dB
        (barely audible) to 64dB (vacuum cleaner noise), respectively.
        2) Identifying harmonics: We compare the mean intensity
        of the projected harmonic with the surrounding area. If the
        difference is 4 times or more we consider harmonic found.
        Because acoustic energy is in logarithmic scale, even faint
        harmonic should have much higher energy than the surround-
        ing area, so the threshold that we use is considered “safe” to
        be used in various noise condition.
        """
        self.threshold_1 = threshold_1
        self.threshold_2 = threshold_2
        if mode == "amplitude":
            # Identify regions where the envelope exceeds the threshold
            self.above_thresh = self.envelope >= threshold_1

            # Find contiguous regions above threshold
            self.segments = []
            start_idx = None
            for idx, val in enumerate(self.above_thresh):
                if val and start_idx is None:
                    start_idx = idx
                elif not val and start_idx is not None:
                    self.segments.append((start_idx, idx))
                    start_idx = None

            # Handle case where the last segment reaches the end
            if start_idx is not None:
                self.segments.append((start_idx, len(self.envelope)))            
            
            # Convert index segments to time intervals using self.time_s
            self.segments_time = [
                (self.time_s[start], self.time_s[end])
                for start, end in self.segments
                if (end > start) and (np.abs(self.time_s[end]-self.time_s[start]) >= min_duration)
            ]
            
            # Find the closest frame index for start and end
            self.segments_spectrogram = []
            for start_time, end_time in self.segments_time:
                start_idx = np.argmin(np.abs(self.time - start_time))
                end_idx = np.argmin(np.abs(self.time - end_time))
                self.segments_spectrogram.append((start_idx, end_idx))

            # Create segments for time and spectrogram
            indexs = self.segments_spectrogram
            # self.segments_time = [self.time[i:j] for [i, j] in indexs]
            self.segments_Sxx = [self.Sxx[:, i:j] for [i, j] in indexs]
            self.segments_Sxx_dB = [self.Sxx_dB[:, i:j] for [i, j] in indexs]

            if verbose:
                print("There are {} segments found.".format(len(self.segments_time)))

        elif mode == "freq":
            self.img = self.ff_fun(self.time)
        elif mode == "ff":
            self.img = self.ff
        elif mode == "signal_pro":
            # parameters extraction
            sigma = img_pro_params.get("sigma", 1)
            W, h = img_pro_params["window_params"].values()
            min_area = img_pro_params.get("min_area", 20)
            min_duration = img_pro_params.get("min_duration", 9)
            threshold = img_pro_params.get("threshold", 1e-6)  # PSD units
            margin_pixels = img_pro_params.get("margin_pixels", 3)
            times = img_pro_params.get("times", 4)
            no_harmonics = img_pro_params.get("no_harmonics", 6)
            scalar = img_pro_params.get("scalar", 3)
            closing = img_pro_params.get("closing", 3)
            stride = img_pro_params.get("stride", 2)

            # Step 2: Identifying fundamental frequency
            # Applying filters to the spectrogram
            self.img_smoothed = gaussian_filter(self.Sxx, sigma=sigma) if sigma > 0 else self.Sxx
            self.mask_1 = median_clipping(self.img_smoothed, multiplier=scalar)
            self.mask_2 = percentile(
                self.img_smoothed,
                window_shape=(W, h),
                stride=(W//stride, h//stride), # 50 % stride if stride = 2
                percentile=img_pro_params["percentile"]
            )
            self.mask = self.mask_1 * self.mask_2
            # ------------------------------- post-processing ------------------------------- 
            self.Sxx_masked_post = self.mask.copy()
            self.Sxx_masked = self.mask * self.Sxx
            self.ff_sp = np.zeros(self.Sxx_masked.shape[1])  # fundamental frequency for each blob
            self.ff_sp_index = np.zeros(self.Sxx_masked.shape[1])  # fundamental frequency index for each blob

            # Fundamental frequency calculation
            if img_pro_params["ff_computing"] == "yin":
                self.ff_sp[:] = self.ff
                self.ff_sp_index[:] = np.abs(self.freq[:, None] - self.ff_sp).argmin(axis=0)
            elif img_pro_params["ff_computing"] == "img_pro":
                self.ff_sp_index[:] = np.argmax(self.Sxx_masked, axis=0)
                self.ff_sp[:] = self.freq[self.ff_sp_index.astype(int)]

            # Create a mask for fundamental frequency points
            self.ff_mask = np.zeros_like(self.Sxx, dtype=bool)
            f_indices = np.abs(self.freq[:, None] - self.ff_sp).argmin(axis=0)
            self.ff_mask[f_indices, np.arange(self.Sxx.shape[1])] = True

            # Remove small blobs based on area and duration
            self.mask_pre_proc = self.mask
            s_8 = generate_binary_structure(2, 2)
            labeled_mask, num_features = label(self.mask, structure=s_8) # type: ignore

            filtered_mask = np.zeros_like(self.mask, dtype=bool)
            for region_label in range(1, num_features + 1):
                region = (labeled_mask == region_label)
                area = np.sum(region)
                duration = np.sum(np.any(region, axis=0))
                region_mean = np.mean(self.Sxx[region])
                ff_in_region = np.any(self.ff_mask & region)
                if area >= min_area and duration >= min_duration and region_mean > threshold and ff_in_region:
                    filtered_mask |= region

            self.mask = filtered_mask
            self.mask_filtered = filtered_mask.copy()

            # Step 3: Identifying harmonics
            Sxx_masked = self.mask * self.Sxx
            self.ff_sp_index[:] = np.argmax(Sxx_masked, axis=0)
            self.ff_sp[:] = self.freq[self.ff_sp_index.astype(int)]

            self.harmonics = []
            self.harmonics_filtered = []
            self.harmonic_masks = []
            self.harmonic_mask_final = np.zeros_like(self.Sxx, dtype=bool)
            self.harmonics_rois = np.zeros_like(self.Sxx, dtype=bool)

            # Labeling the regions in the mask by time index (j)
            label_img, num_features = label(self.mask.astype(np.uint8), structure=s_8) # type: ignore
            # Find the initial time index (j) for each labeled region and create a mapping
            region_start_times = {}
            for region_label in range(1, num_features + 1):
                coords = np.argwhere(label_img == region_label)
                if coords.size > 0:
                    min_j = coords[:, 1].min()
                    region_start_times[region_label] = min_j

            # Sort regions by their initial time index
            sorted_labels = sorted(region_start_times, key=lambda k: region_start_times[k])

            # Create a new label_img with regions relabeled by their order of appearance in time
            label_img_renamed = np.zeros_like(label_img)
            for new_label, old_label in enumerate(sorted_labels, start=1):
                label_img_renamed[label_img == old_label] = new_label

            label_img = label_img_renamed
            self.sorted_labels = label_img

            # Saving regions as dictionary
            self.regions = {}

            syllable_label = 1
            vocalization_label = 1

            self.vocalizations = np.zeros_like(self.Sxx, dtype=int)
            self.syllables = np.zeros_like(self.Sxx, dtype=int)

            # iterating over the fundamental frequency regions
            for l in range(num_features):
                region_mask = (label_img == l + 1)

                regions_dict = [
                    self.region_dict(region_mask, syllable_label ,vocalization_label, "fundamental")
                ]
                
                self.vocalizations[region_mask] = vocalization_label
                self.syllables[region_mask] = syllable_label

                vocalization_label += 1
                
                # Harmonics calculation
                for no_harmonic in range(2, no_harmonics + 1):
                    harmonic_mask = np.zeros_like(self.Sxx, dtype=bool)

                    harmonic = no_harmonic * self.ff_sp
                    harmonic_indices = np.abs(self.freq[:, None] - harmonic).argmin(axis=0)
                    # Set indices to -100 if the corresponding harmonic is outside the frequency range
                    harmonic_indices[(harmonic < self.freq[0]) | (harmonic > self.freq[-1])] = -100

                    # Check the distance from the fundamental frequency  curve to any point of the mask
                    region_coords = np.argwhere(region_mask)
                    for i, j in region_coords:
                        distance_pixels = int(self.ff_sp_index[j] - i)
                        idx = harmonic_indices[j] + distance_pixels
                        if 0 <= idx < self.mask.shape[0]:
                            harmonic_mask[idx, j] = True
                        

                    # Create surrounding mask for the harmonic
                    expanded_harmonic_mask = binary_dilation(
                        harmonic_mask,
                        structure=np.ones((2 * margin_pixels + 1, 2 * margin_pixels + 1))
                    )
                    harmonic_margin_mask = expanded_harmonic_mask & (~harmonic_mask)

                    # Apply morphological closing to the harmonic mask
                    if closing != 0:
                        struct_elem = np.ones((2 * closing + 1, 2 * closing + 1), dtype=bool)
                        harmonic_mask_closed = binary_closing(harmonic_mask, structure=struct_elem)
                    else:
                        harmonic_mask_closed = harmonic_mask

                    # Intensity calculations
                    harmonic_mean_intensity = np.mean(self.Sxx[harmonic_mask])
                    margin_mean_intensity = np.mean(self.Sxx[harmonic_margin_mask])

                    
                    self.harmonic_masks.append(harmonic_mask)
                    self.harmonics.append(harmonic)

                    self.harmonics_rois |= harmonic_mask_closed

                    # Verify if the harmonic mean intensity is significantly higher than the margin mean intensity
                    if harmonic_mean_intensity > times * margin_mean_intensity:
                        self.harmonic_mask_final |= harmonic_mask
                        
                        self.harmonics_filtered.append(harmonic_mask)
                        
                        self.syllables[harmonic_mask] = syllable_label
                        self.vocalizations[harmonic_mask] = vocalization_label

                        regions_dict.append(
                            self.region_dict(harmonic_mask, syllable_label, vocalization_label, "harmonic")
                        )
                        vocalization_label += 1
                        
                self.regions[syllable_label] = regions_dict
                syllable_label += 1

            self.final_mask = self.harmonic_mask_final | self.mask

            self.num_syllables = syllable_label
            self.num_vocalizations = vocalization_label

            self.all_mask = 2 * self.harmonics_rois.astype(int) + self.mask.astype(int)


        elif mode == "region_growing":
            """
            Performs region growing on a grayscale image using 8-connectivity.

            Parameters:
            - image: 2D numpy array (grayscale image).
            - seeds: 2D numpy array (same shape as image), 1s at seed points, 0s elsewhere.
            - predicate: function f(x, y, value) -> bool, returns True if pixel (x,y) satisfies condition.

            Returns:
            - labeled_image: 2D numpy array with labeled regions.
            """
            image = self.Sxx_dB.copy()  # Use the dB-scaled spectrogram
            Sxx_dB_grayscale = self.Sxx_dB - self.Sxx_dB.min()
            Sxx_dB_grayscale = Sxx_dB_grayscale / Sxx_dB_grayscale.max()  # Normalize to [0, 1]

            # Fundamental frequency mask
            # if region_growing_params["ff"] == "yin":
            self.ff_mask = np.zeros_like(self.Sxx, dtype=bool)
            for t_idx, freq in enumerate(self.ff):
                f_idx = np.argmin(np.abs(self.freq - freq))
                self.ff_mask[f_idx, t_idx] = True
            seeds = self.ff_mask.astype(int)

            struct = generate_binary_structure(2, 2)  # 8-connectivity

            # Step 1: Reduce each connected component in S to one pixel
            labeled_seeds, num_seeds = label(seeds, structure=struct) # type: ignore
            reduced_seeds = np.zeros_like(seeds, dtype=np.uint8)
            seed_coords = []
            for i in range(1, num_seeds + 1):
                coords = np.argwhere(labeled_seeds == i)
                if coords.size > 0:
                    reduced_seeds[tuple(coords[0])] = 1
                    seed_coords.append(tuple(coords[0]))

            # Step 2: Form image fQ using predicate and distance restriction
            # mean_ff_dB = np.mean(image[seeds])
            percentile_80 = np.percentile(image[seeds.astype(bool)], 20)

            seed_coords = np.array(seed_coords)
            # print("Seed coordinates: ", np.array(seed_coords).shape)
            fQ = np.zeros_like(image, dtype=np.uint8)
            for x in range(image.shape[0]):
                for y in range(image.shape[1]):
                    # Check if (x, y) is within 20 pixels of any seed
                    Sxx_dB_xy = image[x, y]
                    if Sxx_dB_xy > percentile_80 :#  and np.min((x - seed_coords[:, 0]) ** 2) <= 20: # (np.min(np.sqrt((x - seed_coords[:, 0]) ** 2 + (y - seed_coords[:, 1]) ** 2)) <= 20):
                        fQ[x, y] = 1

            # Step 3: Grow region by connecting seed points with 8-connected neighbors in fQ
            prev = np.zeros_like(reduced_seeds)
            current = reduced_seeds.copy()
            while not np.array_equal(current, prev):
                prev = current.copy()
                dilated = binary_dilation(current, structure=struct)
                current = np.logical_and(dilated, fQ).astype(np.uint8)

            # Step 4: Label the connected components in the grown region
            labeled_image, _ = label(current, structure=struct) # type: ignore
            return labeled_image

        else:
            raise Exception("Mode not implemented yet. Please, use one of the "
                            + "following: 'amplitude', 'freq', 'signal_pro', or 'ff'.")
    #%%
    def _play(self) -> Audio | None: Audio(data=self.s, rate=self.sr)
    def play(self) -> Audio | None:
        """


        Parameters
        ----------

        Return
        ------

        Examples
        --------
            >>>
        """
        if _is_notebook():
            return Audio(data=self.s, rate=self.sr)
        else:
            raise Exception("This method is only available in normal terminal.")
        # sound.stop()
            
    #%%    
    def write_audio(self, bit_depth: int = 16) -> None:
        """
        
        
        Parameters
        ----------

        Return
        ------

        Examples
        --------
            >>>
        """
        audio_name = f'{self.file_name[:-4]}-{self.id}-{self.no_syllable}.wav'
        path_name = self.proj_dirs.examples / audio_name.replace(" ", "")
        write(filename=path_name, fs=self.sr, data=self.s, bit_depth=bit_depth)
        print(f"Audio saved at {path_name}.")

#%%
@dataclass
class Syllable(Base):
    
    ff_method: str
    z: dict[str, float] = field(default_factory=dict)
    id: str = field(default="syllable")
    
    #%%
    """
    Object class to store, characterize, and compare syllables. 
    See :func:`~wavesongs.object.Syllable.__init__`. :class:`~wavesongs.object.Song`

    Parameters
    ----------
        proj_dirs : ProjDirs | None 
            Object to manage project directories
        song : Syllable | Song | None
            Object
        params : dict | None
            Diccionary with all or some constat of the physical
            model motor gestures
        tlim : tuple
            Time range
        flim : tuple
            Frequency range
        sr : int
            Sample rate
        no_syllable : int 
            Sylalble number in song
        id : str
            Type of the object, "syllable" or "synth-syllable"
        info : dict
            Audio metadata about the audio.
        type : str
            A short description about the part, theme or trill, and the behaviour of the
            fundamental frequency: plane, up, down, up-down, down-up, and complex. 
            Template: "{part}-{behaviour}". Example: theme-up 
            
    
    Raise
    -----
        asdasd232

    Note
    ----
        adasds
    
    Warning
    -------
        12qsdad

    Examples
    --------
        >>> 
    """ 
    #%%
    def __init__(
        self,
        file_id: str,
        proj_dirs: ProjDirs = ProjDirs(),
        sr: int = 44100,
        tlim: tuple[float, float] = (0, 60),
        metadata: dict = {
            "type": "",
            "no_syllable":  0,
        }
    ):
        """_summary_

        Args:
            

        Raises:
            Exception: _description_
        """
        super().__init__(file_id, proj_dirs, sr, tlim, metadata)
        self.initialize()


#%% 
class Synthetic(Base):
    """
    """
    z: dict
    beta: np.ndarray
    alpha: np.ndarray

    # bifurcation points
    beta_bif: np.ndarray
    mu1_curves: np.ndarray
    f1: Callable
    f2: Callable

    # physical variables
    times_vs: np.ndarray
    vs: np.ndarray

    # delta values
    deltaCentroid: np.ndarray
    deltaMfccs: np.ndarray
    deltaFmsf: np.ndarray
    deltaEnv: np.ndarray
    deltaSCI: np.ndarray
    deltaRMS: np.ndarray
    deltaSxx: np.ndarray
    deltaMel: np.ndarray
    deltaFF: np.ndarray

    # score values
    scoreCentroid = np.ndarray
    scoreFmsf = np.ndarray
    scoreMfccs = np.ndarray
    scoreSCI = np.ndarray
    scoreEnv = np.ndarray
    scoreRMS = np.ndarray
    scoreSxx = np.ndarray
    scoreMel = np.ndarray
    scoreFF = np.ndarray

    # mean values
    scoreCentroid_mean: float
    scoreFmsf_mean: float
    deltaSCI_mean: float
    scoreRMS_mean: float
    deltaEnv_mean: float
    deltaFF_mean: float

    # similarity values
    correlation: np.ndarray
    SKL: np.ndarray
    Df: np.ndarray

    scoreCorrelation: np.ndarray
    scoreSKL: np.ndarray
    scoreDF: np.ndarray

    residualCorrelation: np.ndarray
    SCIFF: np.ndarray

    params: dict
    z: dict
    time_vs: np.ndarray

    id = "synthetic"

    def __init__(
            self, 
            # duration: float|np.ndarray|list = 1,
            duration: float = 1,
            file_id: str = "synth_0000",
            sr: int = 44100,
            proj_dirs: ProjDirs = ProjDirs(),
            metadata: dict = {
                "type": "",
                "no_syllable":  0,
            },
        ):
        """
        """
        super().__init__(file_id, proj_dirs, sr, (0, duration), metadata)
        self.T = duration
        self.s = np.ones(int(self.T * self.sr))
            
        self.file_name = file_id
        self.t0 = self.t0_bs = 0
    
    #%%
    def initialize(self, s=None):
        """
        Initialize the object with audio file and metadata.
        """
        
        if s is None:
            s = self.s

        self.t0_bs = 0
        self.t0 = self.tlim[0]
        
        self.s = normalize(s, max_amp=1.0)
        self.time_s = np.linspace(0, len(self.s)/self.sr, len(self.s))
    #%%
    def evaluate(
            self,
            obj: Syllable,
            order: int = 2
        ) -> None:
        """
        
        
        Parameters
        ----------
            synth : Sylllable

            order : int
        
        Return
        ------

                
        Example
        -------
            synth : Syllable

        """
        self.envelope = obj._envelope(self.s, int(self.sr), obj.Nt)
        self.ff_method = obj.ff_method

        self.acoustical_features(
            stft_window = obj.stft_window,
            umbral_FF = obj.umbral_FF,
            ff_method = obj.ff_method, # type: ignore
            hop_length = obj.hop_length,
            win_length = obj.win_length,
            llambda = obj.llambda,
            center = obj.center,
            n_mfcc = obj.n_mfcc,
            n_mels = obj.n_mels,
            n_fft = obj.n_fft,
            Nt = obj.Nt
        )

        # residual difference between real and synthetic samples
        self.deltaCentroid = np.abs(self.centroid - obj.centroid)
        self.deltaMfccs = np.abs(self.mfccs - obj.mfccs)
        self.deltaFmsf = np.abs(self.f_msf - obj.f_msf)
        self.deltaEnv = np.abs(self.envelope - obj.envelope)
        self.deltaSCI = np.abs(self.SCI - obj.SCI)
        self.deltaRMS = np.abs(self.rms - obj.rms)
        self.deltaSxx = np.abs(self.Sxx_dB - obj.Sxx_dB)
        self.deltaMel = np.abs(self.ff_coef - obj.ff_coef)
        self.deltaFF = np.abs(self.ff - obj.ff)
        ## --------- normalizing ----------------------
        self.deltaCentroid /= np.max(self.deltaCentroid)
        self.deltaMfccs /= np.max(self.deltaMfccs)
        self.deltaFmsf /= self.f_msf
        self.deltaSCI /= self.SCI
        self.deltaEnv /= self.envelope
        self.deltaRMS /= self.rms
        self.deltaSxx /= np.max(self.deltaSxx)
        self.deltaMel /= np.max(self.deltaMel)
        self.deltaFF /= self.ff
        # --------------- scoring variables --------------------
        self.scoreCentroid = norm(self.deltaCentroid, ord=order)
        self.scoreFmsf = norm(self.deltaFmsf, ord=order)
        self.scoreMfccs = norm(self.deltaMfccs, ord=np.inf)
        self.scoreSCI = norm(self.deltaSCI, ord=order)
        self.scoreEnv = norm(self.deltaEnv, ord=order)
        self.scoreRMS = norm(self.deltaRMS, ord=order)
        self.scoreSxx = norm(self.deltaSxx, ord=np.inf)
        self.scoreMel = norm(self.deltaMel, ord=np.inf)
        self.scoreFF = norm(self.deltaFF, ord=order)
        # ------------------- removing size dependency -------------------
        self.scoreCentroid /= self.deltaCentroid.size
        self.scoreMfccs /= self.deltaMfccs.size
        self.scoreFmsf /= self.deltaFmsf.size
        self.scoreSCI /= self.deltaSCI.size
        self.scoreEnv /= self.deltaEnv.size
        self.scoreRMS /= self.deltaRMS.size
        self.scoreSxx /= self.deltaSxx.size
        self.scoreMel /= self.deltaMel.size
        self.scoreFF /= self.deltaFF.size
        # -------------------- variables mean -------------------------
        # synth.scoreNoHarm = deltaNOP*10**(deltaNOP-2)
        self.scoreCentroid_mean = self.scoreCentroid.mean()
        self.scoreFmsf_mean = self.deltaFmsf.mean()
        self.deltaSCI_mean = self.deltaSCI.mean()
        self.scoreRMS_mean = self.scoreRMS.mean()
        self.deltaEnv_mean = self.deltaEnv.mean()
        self.deltaFF_mean = self.deltaFF.mean()
        # ------------- acoustic dissimilarity indexes (adi) ---------------
        self.correlation = np.zeros_like(self.time)
        self.SKL = np.zeros_like(self.time)
        self.Df = np.zeros_like(self.time)
        for i in range(self.mfccs.shape[1]):
            x = self.mfccs[:,i]
            y = self.mfccs[:,i]
            r = norm(x*y,ord=1) / (norm(x,ord=2)*norm(y,ord=2))
            
            Df = x*np.log2(np.abs(x/y)) + y*np.log2(np.abs(y/x))
            self.correlation[i] = np.sqrt(1-r)
            self.SKL[i] = 0.5*norm(np.abs(x-y), ord=1)
            self.Df[i] = 0.5*norm(Df, ord=1)
            #synth.Df[np.argwhere(np.isnan(synth.Df))]=-10
        # ------------- normalizing adi -----------------
        # synth.correlation /= synth.correlation.max()
        self.SKL /= self.SKL.max()
        self.Df /= self.Df.max()
        # computing adi scores
        self.scoreCorrelation = np.array(norm(self.correlation, ord=order))
        self.scoreSKL = norm(self.SKL, ord=order) # type: ignore
        self.scoreDF = np.array(norm(self.Df, ord=order))
        # normalizing
        self.scoreCorrelation /= self.correlation.size
        self.scoreSKL /= self.SKL.size
        self.scoreDF /= self.Df.size
        # mean scores
        score = self.scoreCorrelation + self.scoreDF + self.scoreSKL
        mean_scores = np.mean(score)
        self.residualCorrelation = np.array(self.scoreFF - mean_scores)
        self.SCIFF = np.array(self.scoreSCI + self.scoreFF)


    #%%
    def export_mg(
            self,
            dataframe: bool = False,
            export_curves: bool = True
        ) -> pd.DataFrame | None:
        """
        
        
        Parameters
        ----------
            

        Return
        ------
            synth : Syllable


        Examples
        --------
            >>>
        """
        if "synth" not in self.id:
            raise Exception("You only can export motor gestures"
                            + " parameters from synthetic objects")
        # ------------ export p values and alpha-beta arrays ------------
        file_name = self.file_name.replace("synth-","")
        type = self.type if self.type!="" else ""
        info = {
            "t_ini": round(self.t_interval[0], 4),
            "t_end": round(self.t_interval[1], 4),
            "f_ini": self.flim[0],
            "f_end": self.flim[1],
            "id": self.id,
            "no_syllable": self.no_syllable,
            "sr": self.sr,
            "n_fft": self.n_fft,
            "umbral_FF": self.umbral_FF,
            "ff_method": self.ff_method,
            "type": type,
            "metadata": str(self.metadata),
            "file_name": file_name,
            "audios_folder": self.proj_dirs.audios,
            "z": str(self.z),
            "duration": self.T,
            "params": str(self.params),
            "Nt": self.Nt,
            "center": self.center,
            "overlap": self.overlap,
            "llambda": self.llambda,
            "n_mfcc": self.n_mfcc,
            "n_mels": self.n_mels,
            "stft_window": self.stft_window
        }
        if export_curves:
            path = self.export_curves()
            info = info | {"curves_csv": path} 

        name = f"{file_name[:-4]}-{self.no_syllable}-mg.csv"\
                if type!="" \
                else f"{file_name[:-4]}-{self.no_syllable}-{self.type}-mg.csv"
        path = self.proj_dirs.mg_param / name.replace(" ", "")
        df_mg = pd.DataFrame.from_dict(info, orient="index", columns=["value"])
        df_mg.to_csv(path, index=True)
        print(f"Motor gesture parameters saved at {path}.")

        if dataframe:
            return df_mg
    
    # %%
    def export_curves(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        curves_array = np.array([self.time_s, self.alpha, self.beta]).T
        curves_df = pd.DataFrame(curves_array, columns=["time","alpha","beta"])
        name = f"{self.file_name[:-4]}-{self.no_syllable}-curves.csv"\
                if type!="" \
                else f"{self.file_name[:-4]}-{self.no_syllable}-{self.type}-curves.csv"
        
        path = self.proj_dirs.mg_param / name.replace(" ", "")
        curves_df.to_csv(path, index=True)
        print(f"Curves arrays saved at {path}")
        return path

    # %%
    def import_curves(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        curves_array = np.array([self.time_s, self.alpha, self.beta])
        curves_df = pd.DataFrame(curves_array)
        name = f"{self.file_name[:-4]}-{self.no_syllable}-curves.csv"\
                if type!="" \
                else f"{self.file_name[:-4]}-{self.no_syllable}-{self.type}-curves.csv"
        path = self.proj_dirs.mg_param / name
        return pd.read_csv(path)
#%%
class Song(Base):
    id = "song"

    """
    Store a song and its properties in a class
    
    Parameters
    ----------
        proj_dirs : ProjDirs

        file_id : str
            Name or id of the audio sample
        tlim : tuple
            Time range
        flim : tuple
            Frequency range
        sr : int
            Sample rate
        info : dict
            Audio metadata.
        id : str = "song"

    
    Attributes
    ----------

    Example
    -------
        >>>
    """
    def __init__(
            self,
            file_id: str,
            proj_dirs: ProjDirs = ProjDirs(),
            sr: int = 44100,
            tlim: tuple[float, float] = (0, 60),
            metadata: dict = {
                "type": "",
                "no_syllable":  0,
            },
        ):  
        super().__init__(file_id, proj_dirs, sr, tlim, metadata)
        self.initialize()