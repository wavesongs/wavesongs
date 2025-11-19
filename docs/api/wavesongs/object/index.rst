wavesongs.object
================

.. py:module:: wavesongs.object

.. autoapi-nested-parse::

   Store and compute acoustica features from base type.



Classes
-------

.. autoapisummary::

   wavesongs.object.Base
   wavesongs.object.Song
   wavesongs.object.Syllable
   wavesongs.object.Synthetic


Functions
---------

.. autoapisummary::

   wavesongs.object._is_notebook


Module Contents
---------------

.. py:class:: Base(file_id, proj_dirs = ProjDirs(), sr = 44100, tlim = (0, 1000), metadata = {'type': '', 'no_syllable': 0})

   .. py:method:: _envelope(s, sr, Nt)

      :param s: Audio amplitude array
      :type s: np.array
      :param sr: Sample rate
      :type sr: int
      :param Nt:
      :type Nt: int

      :returns: s_env_interpolated : np.array

      .. rubric:: Example

      >>>



   .. py:method:: _play()


   .. py:method:: acoustical_features(n_fft = 512, hop_length = None, win_length = None, umbral_FF = 1, ff_method = 'yin', flim = (0.01, 22000.0), Nt = 10, center = False, llambda = 1.5, n_mfcc = 4, n_mels = 4, stft_window = 'hann', pad_mode = 'constant')

      Coputing acoustical tempo-spectral variables

      :param n_fft: FFT window size.
      :type n_fft: int
      :param llambda:
      :type llambda: float
      :param hop_length: Number of audio samples between adjacent STFT columns.
      :type hop_length: int, optional
      :param win_length: Length of the windowed signal after padding with zeros
      :type win_length: int, optional
      :param center:
      :type center: bool = False
      :param umbral_FF:
      :type umbral_FF: int
      :param ff_method:
      :type ff_method: str
      :param Nt:
      :type Nt: int
      :param n_mfcc:
      :type n_mfcc: int
      :param n_mels:
      :type n_mels: int
      :param stft_window:
      :type stft_window: str

      :returns: None

      .. rubric:: Examples

      >>>



   .. py:method:: initialize()

      Initialize the object with audio file and metadata.



   .. py:method:: play()

      
      .. rubric:: Examples

      >>>



   .. py:method:: region_dict(region_mask, syllable_label, vocalization_label, id = 'fundamental')


   .. py:method:: segmentation(mode = 'amplitude', threshold_1 = 0.2, threshold_2 = 1, min_duration = 0.01, img_pro_params = {'scalar': 3, 'percentile': 80, 'no_harmonics': 6, 'min_area': 20, 'min_duration': 9, 'window_params': {'W': 64, 'h': 100}, 'stride': 2, 'margin_pixels': 3, 'times': 2, 'ff_computing': 'yin', 'closing': 3}, region_growing_params = {'threshold': 100, 'ff': 'yin'}, verbose = True)

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



   .. py:method:: write_audio(bit_depth = 16)

      
      .. rubric:: Examples

      >>>



   .. py:attribute:: SCI
      :type:  numpy.ndarray


   .. py:attribute:: ff_fun
      :type:  Any


   .. py:attribute:: ff_method
      :type:  Literal['yin', 'pyin', 'imgpro']


   .. py:attribute:: ff_time
      :type:  numpy.ndarray


   .. py:attribute:: file_id


   .. py:attribute:: id
      :type:  str
      :value: 'base'


      Object class to store, characterize, and compare syllables.
      See :func:`~wavesongs.object.Syllable.__init__`. :class:`~wavesongs.object.Song`

      :param proj_dirs: Object to manage project directories
      :type proj_dirs: ProjDirs | None
      :param song: Object
      :type song: Syllable | Song | None
      :param params: Diccionary with all or some constat of the physical
                     model motor gestures
      :type params: dict | None
      :param tlim: Time range
      :type tlim: tuple
      :param flim: Frequency range
      :type flim: tuple
      :param sr: Sample rate
      :type sr: int
      :param no_syllable: Sylalble number in song
      :type no_syllable: int
      :param id: Type of the object, "syllable" or "synth-syllable"
      :type id: str
      :param info: Audio metadata about the audio.
      :type info: dict
      :param type: A short description about the part, theme or trill, and the behaviour of the
                   fundamental frequency: plane, up, down, up-down, down-up, and complex.
                   Template: "{part}-{behaviour}". Example: theme-up
      :type type: str

      :raises adasdad:

      .. note:: asdasd

      .. warning:: adasdasd

      .. rubric:: Examples

      >>>


   .. py:attribute:: metadata


   .. py:attribute:: no_syllable


   .. py:attribute:: proj_dirs


   .. py:attribute:: region_mask
      :type:  numpy.ndarray


   .. py:attribute:: sr
      :type:  int


   .. py:attribute:: t0_bs
      :type:  float
      :value: 0.0



   .. py:attribute:: time
      :type:  numpy.ndarray


   .. py:attribute:: tlim
      :value: (0, 1000)



   .. py:attribute:: type


.. py:class:: Song(file_id, proj_dirs = ProjDirs(), sr = 44100, tlim = (0, 60), metadata = {'type': '', 'no_syllable': 0})

   Bases: :py:obj:`Base`


   .. py:attribute:: id
      :value: 'song'


      Store a song and its properties in a class

      :param proj_dirs:
      :type proj_dirs: ProjDirs
      :param file_id: Name or id of the audio sample
      :type file_id: str
      :param tlim: Time range
      :type tlim: tuple
      :param flim: Frequency range
      :type flim: tuple
      :param sr: Sample rate
      :type sr: int
      :param info: Audio metadata.
      :type info: dict
      :param id:
      :type id: str = "song"

      .. rubric:: Example

      >>>


.. py:class:: Syllable(file_id, proj_dirs = ProjDirs(), sr = 44100, tlim = (0, 60), metadata = {'type': '', 'no_syllable': 0})

   Bases: :py:obj:`Base`


   .. py:attribute:: ff_method
      :type:  str


   .. py:attribute:: id
      :type:  str
      :value: 'syllable'


      Object class to store, characterize, and compare syllables.
      See :func:`~wavesongs.object.Syllable.__init__`. :class:`~wavesongs.object.Song`

      :param proj_dirs: Object to manage project directories
      :type proj_dirs: ProjDirs | None
      :param song: Object
      :type song: Syllable | Song | None
      :param params: Diccionary with all or some constat of the physical
                     model motor gestures
      :type params: dict | None
      :param tlim: Time range
      :type tlim: tuple
      :param flim: Frequency range
      :type flim: tuple
      :param sr: Sample rate
      :type sr: int
      :param no_syllable: Sylalble number in song
      :type no_syllable: int
      :param id: Type of the object, "syllable" or "synth-syllable"
      :type id: str
      :param info: Audio metadata about the audio.
      :type info: dict
      :param type: A short description about the part, theme or trill, and the behaviour of the
                   fundamental frequency: plane, up, down, up-down, down-up, and complex.
                   Template: "{part}-{behaviour}". Example: theme-up
      :type type: str

      :raises asdasd232:

      .. note:: adasds

      .. warning:: 12qsdad

      .. rubric:: Examples

      >>>


   .. py:attribute:: z
      :type:  dict[str, float]


.. py:class:: Synthetic(duration = 1, file_id = 'synth_0000', sr = 44100, proj_dirs = ProjDirs(), metadata = {'type': '', 'no_syllable': 0})

   Bases: :py:obj:`Base`


   


   .. py:method:: evaluate(obj, order = 2)

      :param synth:
      :type synth: Sylllable
      :param order:
      :type order: int

      .. rubric:: Example

      synth : Syllable



   .. py:method:: export_curves()

      _summary_

      :returns: _description_
      :rtype: _type_



   .. py:method:: export_mg(dataframe = False, export_curves = True)

      
      :returns: synth : Syllable

      .. rubric:: Examples

      >>>



   .. py:method:: import_curves()

      _summary_

      :returns: _description_
      :rtype: _type_



   .. py:method:: initialize(s=None)

      Initialize the object with audio file and metadata.



   .. py:attribute:: Df
      :type:  numpy.ndarray


   .. py:attribute:: SCIFF
      :type:  numpy.ndarray


   .. py:attribute:: SKL
      :type:  numpy.ndarray


   .. py:attribute:: T
      :value: 1



   .. py:attribute:: alpha
      :type:  numpy.ndarray


   .. py:attribute:: beta
      :type:  numpy.ndarray


   .. py:attribute:: beta_bif
      :type:  numpy.ndarray


   .. py:attribute:: correlation
      :type:  numpy.ndarray


   .. py:attribute:: deltaCentroid
      :type:  numpy.ndarray


   .. py:attribute:: deltaEnv
      :type:  numpy.ndarray


   .. py:attribute:: deltaEnv_mean
      :type:  float


   .. py:attribute:: deltaFF
      :type:  numpy.ndarray


   .. py:attribute:: deltaFF_mean
      :type:  float


   .. py:attribute:: deltaFmsf
      :type:  numpy.ndarray


   .. py:attribute:: deltaMel
      :type:  numpy.ndarray


   .. py:attribute:: deltaMfccs
      :type:  numpy.ndarray


   .. py:attribute:: deltaRMS
      :type:  numpy.ndarray


   .. py:attribute:: deltaSCI
      :type:  numpy.ndarray


   .. py:attribute:: deltaSCI_mean
      :type:  float


   .. py:attribute:: deltaSxx
      :type:  numpy.ndarray


   .. py:attribute:: f1
      :type:  Callable


   .. py:attribute:: f2
      :type:  Callable


   .. py:attribute:: file_name
      :value: 'synth_0000'



   .. py:attribute:: id
      :value: 'synthetic'


      Object class to store, characterize, and compare syllables.
      See :func:`~wavesongs.object.Syllable.__init__`. :class:`~wavesongs.object.Song`

      :param proj_dirs: Object to manage project directories
      :type proj_dirs: ProjDirs | None
      :param song: Object
      :type song: Syllable | Song | None
      :param params: Diccionary with all or some constat of the physical
                     model motor gestures
      :type params: dict | None
      :param tlim: Time range
      :type tlim: tuple
      :param flim: Frequency range
      :type flim: tuple
      :param sr: Sample rate
      :type sr: int
      :param no_syllable: Sylalble number in song
      :type no_syllable: int
      :param id: Type of the object, "syllable" or "synth-syllable"
      :type id: str
      :param info: Audio metadata about the audio.
      :type info: dict
      :param type: A short description about the part, theme or trill, and the behaviour of the
                   fundamental frequency: plane, up, down, up-down, down-up, and complex.
                   Template: "{part}-{behaviour}". Example: theme-up
      :type type: str

      :raises adasdad:

      .. note:: asdasd

      .. warning:: adasdasd

      .. rubric:: Examples

      >>>


   .. py:attribute:: mu1_curves
      :type:  numpy.ndarray


   .. py:attribute:: params
      :type:  dict


   .. py:attribute:: residualCorrelation
      :type:  numpy.ndarray


   .. py:attribute:: s


   .. py:attribute:: scoreCentroid


   .. py:attribute:: scoreCentroid_mean
      :type:  float


   .. py:attribute:: scoreCorrelation
      :type:  numpy.ndarray


   .. py:attribute:: scoreDF
      :type:  numpy.ndarray


   .. py:attribute:: scoreEnv


   .. py:attribute:: scoreFF


   .. py:attribute:: scoreFmsf


   .. py:attribute:: scoreFmsf_mean
      :type:  float


   .. py:attribute:: scoreMel


   .. py:attribute:: scoreMfccs


   .. py:attribute:: scoreRMS


   .. py:attribute:: scoreRMS_mean
      :type:  float


   .. py:attribute:: scoreSCI


   .. py:attribute:: scoreSKL
      :type:  numpy.ndarray


   .. py:attribute:: scoreSxx


   .. py:attribute:: time_vs
      :type:  numpy.ndarray


   .. py:attribute:: times_vs
      :type:  numpy.ndarray


   .. py:attribute:: vs
      :type:  numpy.ndarray


   .. py:attribute:: z
      :type:  dict


.. py:function:: _is_notebook()

