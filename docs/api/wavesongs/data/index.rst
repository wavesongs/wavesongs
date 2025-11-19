wavesongs.data
==============

.. py:module:: wavesongs.data

.. autoapi-nested-parse::

   Query and download data from Xeno Canto



Attributes
----------

.. autoapisummary::

   wavesongs.data._AUDIO_FORMATS
   wavesongs.data._CATALOG_LABEL
   wavesongs.data.branch
   wavesongs.data.last
   wavesongs.data.space
   wavesongs.data.tee


Classes
-------

.. autoapisummary::

   wavesongs.data.ProjDirs


Functions
---------

.. autoapisummary::

   wavesongs.data.download_audios
   wavesongs.data.query_audios


Module Contents
---------------

.. py:class:: ProjDirs(audios = './assets/audios', results = './assets/results', metadata = 'spreadsheet.csv', catalog = False)

   .. py:method:: __str__()


   .. py:method:: audios_info()

      Get information about the audios folder: audios paths and
      number of audios.

      :param None:

      :returns: None

      .. rubric:: Example

      >>>



   .. py:method:: find_audio(id)

      Find an audio in the audios folder by the id or filename

      :param id: Whole filename of a part of it. Usually, the catalog number.
      :type id: str

      :returns:

                path : PosixPath
                    Aduio path location.

      .. rubric:: Example

      >>>



   .. py:method:: find_audios(pretty=False)

      Search for all audios, mp3 and wav types, in the audios folder.

      :param None:

      :returns:

                files_names : list
                    List with the audios files names

      .. rubric:: Notes

      If the audios folder contains a metadata file, spreadsheet.csv,
      the method will return a dataframe. However, the parameter
      `files_names` always is present.

      .. rubric:: Example

      >>>



   .. py:method:: tree(prefix = '')


   .. py:method:: tree_list(prefix = '')

      A recursive generator, given a directory Path object
      will yield a visual tree structure line by line
      with each line prefixed by the same characters



   .. py:attribute:: audios
      :type:  pathlib.PosixPath | pathlib.Path


   .. py:attribute:: catalog
      :type:  bool

      Creates a ProjDirs class,  which is used to store a project's
      file structure. This is required when constructing
      a :class:`~wavesongs.obj.Syllable` or a :class:`~wavesongs.obj.Song`
      objects and generally useful to keep paths tidy and in the same
      location.

      :param audios: Folder path where the audio records samples are stored.
      :type audios: str ='./assets/audio'
      :param results: Folder path to store the files and data generated.
      :type results: str = "./assets/results"
      :param metadata: Name of the csv file with the metadata of the audios.
                       Usually given by the data provider.
      :type metadata: str = "spreadsheet.csv"

      .. rubric:: Example

      >>> proj_dirs = ProjDirs(
      >>>     "./assets/audio", "./assets/results", "spreadsheet.csv"
      >>> )


   .. py:attribute:: examples
      :type:  pathlib.PosixPath | pathlib.Path


   .. py:attribute:: images
      :type:  pathlib.PosixPath | pathlib.Path


   .. py:attribute:: mg_param
      :type:  pathlib.PosixPath | pathlib.Path


   .. py:attribute:: results


   .. py:attribute:: spreadsheet
      :type:  pathlib.PosixPath | pathlib.Path


.. py:function:: download_audios(df_dataset, rootdir = './assets/audio', dataset_name = '', overwrite = True, save_csv = True, verbose = True)

   Download audios from `Xeno Canto <https://xeno-canto.org/>`_  with
   `maad.utils.xc_download <https://scikit-maad.github.io/util.html#xeno-canto>`_.

   :param df_dataset: Data Frame with the information to download.
   :type df_dataset: pd.DataFrame
   :param country: _description_. Defaults to "Colombia".
   :type country: str, optional
   :param rootdir: _description_. Defaults to "./assets/audio".
   :type rootdir: str, optional
   :param dataset_name: _description_. Defaults to ''.
   :type dataset_name: str, optional
   :param overwrite: _description_. Defaults to False.
   :type overwrite: bool, optional
   :param save_csv: _description_. Defaults to True.
   :type save_csv: bool, optional
   :param verbose: _description_. Defaults to True.
   :type verbose: bool, optional

   :returns: Data Frame
   :rtype: df_audios (pd.DataFrame)


.. py:function:: query_audios(specie_names, max_nb_files = None, random_seed = 2025, info = {}, format_time=True, format_date=True, verbose = True)

   Query me from `Xeno Canto <https://xeno-canto.org/>`_
   with `maad.utils.xc_multi_query <https://scikit-maad.github.io/util.html#xeno-canto>`_.

   :param specie_names: List with english and scientific specie names.
   :type specie_names: list[str], list[list[str]]
   :param max_nb_files: Maximum number of files to download. Defaults to None.
   :type max_nb_files: int, optional
   :param random_seed: Random seed. Defaults to 2025.
   :type random_seed: int, optional
   :param info: Dictionary with information to query. Defaults to {}.
   :type info: dict, optional
   :param format_time: Format time. Defaults to True.
   :type format_time: bool, optional
   :param format_date: Format date. Defaults to True.
   :type format_date: bool, optional
   :param verbose: Verbose. Defaults to True.
   :type verbose: bool, optional

   :returns: Data Frame
   :rtype: df_query (pd.DataFrame)


.. py:data:: _AUDIO_FORMATS
   :value: ('.mp3', '.wav')


.. py:data:: _CATALOG_LABEL
   :value: 'ML Catalog Number'


.. py:data:: branch
   :value: '│   '


.. py:data:: last
   :value: '└── '


.. py:data:: space
   :value: '    '


.. py:data:: tee
   :value: '├── '


