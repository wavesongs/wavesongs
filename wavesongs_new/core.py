from abc import ABC, abstractmethod
import numpy as np
# sound playing
from IPython.display import Audio

from dataclasses import dataclass, field

from os.path import basename, normpath


from numpy.linalg import norm

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
    melspectrogram,
    zero_crossing_rate
)

from maad.sound import (
    normalize,
    write,
    normalize,
    envelope
)

from typing import (
    Callable,
    Any,
    Literal
)

from scipy.interpolate import interp1d

from wavesongs.data.manager import ProjDirs

# go to tools
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
class Song(ABC):
    """
    Abstract base class for a song.
    """
    s: np.ndarray
    sr: int
    tlim: tuple[float, float]

    @classmethod
    def create(
            cls,
            s,
            sr: int = 44100,
            tlim: tuple[float, float] = (0, 600),
            file_name: str  = "",
            proj_dirs: ProjDirs | None = None,
            metadata: dict | None = None,
        ):
        """
        Creates the song object by reading the audio file and computing its acoustic properties.
        """

        song = cls(
            file_name=file_name,
            proj_dirs=proj_dirs,
            sr=sr,
            tlim=tlim,
            metadata=metadata,
        )

        song.s = np.asarray(s)
        song.time_s = np.linspace(0, len(song.s) / song.sr, len(song.s))
        song.t0 = tlim[0]
        song.t0_bs = 0

        return song

        # return cls

        # return song
        
    def __init__(
            self,
            file_name: str  = "",
            proj_dirs: ProjDirs | None = None,
            sr: int = 44100,
            tlim: tuple[float, float] = (0, 600),
            metadata: dict | None = None,
        ) -> None:

        self.sr = sr
        self.tlim = tlim
        self.file_name = file_name
        self.metadata = {} if metadata is None else metadata
        self.proj_dirs = ProjDirs() if proj_dirs is None else proj_dirs

    
    def read_audio(self):
        """
        Reads the audio file and returns the audio data and sample rate.
        """
        # Implement audio reading logic here
        self.file_path = self.proj_dirs.find_audio(self.file_name)
        self.file_name = basename(normpath(self.file_path))

        s, _ = load(self.file_path, sr=self.sr, mono=True)
        s = s[int(self.tlim[0]*self.sr) : int(self.tlim[1]*self.sr)]

        self.t0_bs = 0
        self.t0 = self.tlim[0]
        
        self.s = normalize(s, max_amp=1.0)
        self.time_s = np.linspace(0, len(self.s)/self.sr, len(self.s))

    def write_audio(
            self,
            bit_depth: int = 16,
            path = "",
            verbose=True
        ) -> None:
        """
        NEED TO BE MODIFIED IF PROJDIRECT IS MODIFIED
        
        Parameters
        ----------

        Return
        ------

        Examples
        --------
            >>>
        """
        audio_name = f'{self.file_name[:-4]}-{self.file_name}.wav' # -{self.no_syllable}
        path_name = self.proj_dirs.examples / audio_name.replace(" ", "") if path == "" else path
        write(filename=path_name, fs=self.sr, data=self.s, bit_depth=bit_depth)
        if verbose:
            print(f"Audio saved at {path_name}.")

    
    def _play(self) -> Audio | None: 
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
                return Audio(data=self.s, rate=self.sr)
    #%%
    def _envelope(
        self,
        s: np.ndarray,
        sr: int = 44100,
        Nt: int = 10
    ) -> np.ndarray:
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
        self.Nt = Nt

        time = np.linspace(0, len(s)/sr, len(s))
        s_env = envelope(s, Nt=self.Nt)
        t_env = np.arange(0, len(s_env), 1) * np.float16(len(s) / sr / len(s_env))
        t_env[-1] = time[-1] 
        fun_s = interp1d(t_env, s_env)
        s_env_interpolated = np.array(fun_s(time))

        return s_env_interpolated

    def rstft(
        self,
        n_fft: int = 512,
        hop_length: int | None = None,
        frame_length: int | None = None,
        center: bool = False,
        n_mfcc: int = 4,
        n_mels: int = 4,
        stft_window: str = "hann",
        pad_mode: Literal['constant', 'edge', 'linear_ramp', 'reflect', 'symmetric', 'empty'] = "constant",
        flim: tuple[float, float] = (1e-2, 22e3),
        # ff_method: Literal["yin", "pyin", "imgpro", None] = "yin",
    ):
        """
        Computes and returns the acoustic properties of the song.
        """
        # Fourier transform parameters
        self.flim = flim if flim is not None else (0.1, self.sr/2)

        # def spectrogram parameters
        self.n_fft = n_fft
        self.center = center
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.pad_mode = pad_mode
        self.stft_window = stft_window

        self.time0 = np.linspace(0, len(self.s)/self.sr, len(self.s))
        # self.time_s = np.linspace(0, len(self.s)/self.sr, len(self.s))
        self.T = self.s.size / self.sr
        
        self.t_interval = np.array([self.time_s[0], self.time_s[-1]])
        self.t_interval += self.t0_bs

        self.frame_length = self.n_fft if frame_length is None else frame_length
        self.hop_length = self.frame_length // 4 if hop_length is None else hop_length
        self.overlap = self.hop_length / self.n_fft

        # resolution
        self.f_resolution = self.sr / self.n_fft
        self.time_resolution = self.hop_length / self.sr
        # ------------------------------- STFT -------------------------------
        self.stft = stft(
            y=self.s,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.frame_length,
            window=self.stft_window,
            center=self.center,
            dtype=float,
            pad_mode=self.pad_mode,
        )
        freqs, times, mags = reassigned_spectrogram(
            self.s,
            sr=self.sr,
            S=self.stft,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.frame_length,
            window=self.stft_window,
            center=self.center,
            reassign_frequencies=True,
            reassign_times=True,
            ref_power=1e-6,
            fill_nan=True,
            clip=True,
            dtype=float,
            pad_mode=self.pad_mode,
        )
        self.Sxx_dB = amplitude_to_db(mags, ref=np.max)
        self.freqs = freqs
        self.times = times
        self.Sxx = mags

        self.ff_coef = np.abs(self.stft)
        self.freq = fft_frequencies(sr=self.sr, n_fft=self.n_fft) 
        self.time = times_like(X=self.stft,
                                sr=self.sr,
                                hop_length=self.hop_length,
                                n_fft=self.n_fft) #, axis=-1
        self.time -= self.time[0] # to reset the plot
        

    def ad(
        self,
        type: Literal["temporal", "spectral", "both"] | None  = "both",
    ):
        """
        Computes and returns the acoustic descriptors of the song.
        """
        if type is "temporal":
            self.temporal_ad()
        elif type is "spectral":
            self.spectral_ad()
        elif type is "both":
            self.spectral_ad()
            self.temporal_ad()

    def zcr(
        self,
        frame_length: int | None = None,
        hop_length: int | None = None,
        center: bool = True,
        threshold: float = 1e-10,
        ref_magnitude: float | Callable | None = None,
        pad: bool = True,
        zero_pos: bool = True,
    ):
        kwargs = {
            "threshold": threshold,
            "pad": pad,
            "zero_pos": zero_pos,
            "ref_magnitude": ref_magnitude,
        }
        zcr = zero_crossing_rate(
            self.s,
            frame_length=frame_length,
            hop_length=hop_length,
            center=center, 
            **kwargs
        )

        return zcr

    def temporal_ad(
        self,
        threshold: float = 1e-10,
        ref_magnitude: float | Callable | None = None,
        pad: bool = True,
        zero_pos: bool = True,
        Nt: int = 10,
    ):
        # Zero crossing rate
        self.zcr(
            self.frame_length, self.hop_length, self.center,
            threshold, ref_magnitude, pad, zero_pos
        )
        # Envelope
        self.envelope = self._envelope(self.s, Nt=self.Nt, sr=self.sr)
        
    def spectral_centroid(self):
        self.centroid = spectral_centroid(
                    y=self.s,
                    sr=self.sr,
                    S=self.ff_coef,
                    n_fft=self.n_fft,
                    hop_length=self.hop_length,
                    freq=self.freqs,
                    frame_length=self.frame_length, 
                    window=self.stft_window,
                    center=self.center,
                    pad_mode=self.pad_mode
                )[0]

    def fmsf(self):
        self.f_msf = np.array([
            norm(self.ff_coef[:, i] * self.freq, 1) / norm(self.ff_coef[:, i], 1)
            for i in range(self.ff_coef.shape[1])
        ])
        
    def sci(self, f0: np.ndarray):
        self.f0_time = np.linspace(0,self.time[-1], f0.size)
        self.f0_fun = interp1d(self.f0_time, f0)
        self.fmsf()
        self.SCI = self.f_msf / self.f0_fun(self.time)

        return self.SCI

    def mfcc(self):
        self.mfccs = mfcc(
                    y=self.s,
                    sr=self.sr,
                    S=self.stft,
                    n_mfcc=self.n_mfcc,
                    dct_type=2,
                    norm='ortho',
                    lifter=0
                )

    def melspectrogram(self, power:float = 2.0):
        self.s_mel = melspectrogram(
                    y=self.s,
                    sr=self.sr,
                    S=self.stft,
                    n_fft=self.n_fft,
                    hop_length=self.hop_length,
                    frame_length=self.frame_length,
                    window=self.stft_window,
                    center=self.center,
                    pad_mode=self.pad_mode,
                    power=power,
                    n_mels=self.n_mels,
                    fmin=self.flim[0],
                    fmax=self.flim[1]
                )
    def rms(self):
        self.rms = rms(
                    y=self.s,
                    S=self.stft,
                    frame_length=self.n_fft,
                    hop_length=self.hop_length,
                    center=self.center,
                    pad_mode=self.pad_mode
                )[0]
        
    def spectral_ad(
            self,
            f0_alg: Literal["yin", "pyin"] = "yin"
        ):
        """
        Spectral acoustic descriptors (features) of the song. Computes
        and returns the spectral acoustic features of the song.
        """
        # f0
        if f0_alg == "yin":
            self.f0 = self.f0_yin(self.s)
        elif f0_alg == "pyin":
            self.f0 = self.f0_pyin(self.s)
        # SCI
        self.sci(self.f0)
        # Spectral Centroid
        self.spectral_centroid()
        # MFCCs
        self.mfcc()
        # RMS
        self.rms()
        # S Mel
        self.melspectrogram()
        
    def f0_pyin(
        self,
        s: np.ndarray,
        fmin: float = 1.1,
        fmax: float = 22000,
        sr: int = 44100,
        frame_length: int = 512,
        hop_length: int = 128,
        center: bool = True,
        pad_mode: str = "constant",
        # tunning paramters
        n_thresholds = 100,
        beta_parameters = (2, 18),
        boltzmann_parameter = 2,
        resolution = 0.1,
        max_transition_rate = 35.92,
        switch_prob = 0.01,
        no_trough_prob = 0.01,
        fill_na = 0,
    ) -> np.ndarray:
        """
        Computes and returns the fundamental frequency (f0) of the song.
        """
        ff, _, _ = pyin(
            s,
            fmin=fmin,
            fmax=fmax,
            sr=sr,
            frame_length=frame_length,
            hop_length=hop_length,
            n_thresholds=n_thresholds,
            beta_parameters=beta_parameters,
            boltzmann_parameter=boltzmann_parameter,
            resolution=resolution,
            max_transition_rate=max_transition_rate,
            switch_prob=switch_prob,
            no_trough_prob=no_trough_prob,
            fill_na=fill_na,
            center=center,
            pad_mode=pad_mode
        )

        return ff

    def f0_yin(
        self,
        s: np.ndarray,
        sr: int = 44100,
        n_fft: int = 512,
        frame_length: int | None = None,
        hop_length: int | None = None,
        fmin: float = 100,
        fmax: float = 22000,
        center: bool = True,
        trough_threshold: float = 1.0,
        pad_mode: str = "constant",
        # tunning parameter
        umbral_FF: float = 1,
    ):
        
        self.umbral_FF = umbral_FF
        ff = yin(
            s,
            fmin=fmin,
            fmax=fmax,
            sr=sr,
            frame_length=n_fft, 
            hop_length=hop_length,
            center=center,
            trough_threshold=umbral_FF,
            pad_mode=pad_mode
        )
        return ff
#%%
class BirdSong(Song):
    """
    Concrete implementation of a bird song.
    """
    def __init__(
        self,
        file_name: str,
        proj_dirs: ProjDirs | None = None,
        sr: int = 44100,
        tlim: tuple[float, float] = (0, 600),
        metadata: dict | None = None,
    ) -> None:
        super().__init__(file_name, proj_dirs, sr, tlim, metadata)

    def extract_syllables(self):
        """
        Extract the syllables from the bird song. Done using segmentation.
        """
        print("Extracting syllables from bird song...")

#%% 
class Syllable(Song):
    def __init__(
        self,
        file_name: str,
        proj_dirs: ProjDirs | None = None,
        sr: int = 44100,
        tlim: tuple[float, float] = (0, 600),
        metadata: dict | None = None,
    ) -> None:
        super().__init__(file_name, proj_dirs, sr, tlim, metadata)

#%% 
class Synthetic(Song):
    def __init__(
        self,
        duration: float  = 1,
        s: np.ndarray | None = None,
        file_name: str = "Synthetic",
        proj_dirs: ProjDirs | None = None,
        sr: int = 44100,
        tlim: tuple[float, float] = (0, 600),
        metadata: dict | None = None,
    ) -> None:
        self.sr = sr
        self.tlim = tlim
        self.file_name = file_name
        self.metadata = {} if metadata is None else metadata
        self.proj_dirs = ProjDirs() if proj_dirs is None else proj_dirs

        # Initialize the synthetic signal time
        self.t0 = 0
        self.t0_bs = 0
        self.T = duration
        self.s = np.ones(int(self.T * self.sr)) if s is None else s
#%% 
class Chunck(Song):
    def __init__(
        self,
        file_name: str,
        proj_dirs: ProjDirs | None = None,
        duration: float = 20.0, # in ms
        sr: int = 44100,
        tlim: tuple[float, float] = (0, 600),
        metadata: dict | None = None,
    ) -> None:
        super().__init__(file_name, proj_dirs, sr, tlim, metadata)
        self.duration = duration
